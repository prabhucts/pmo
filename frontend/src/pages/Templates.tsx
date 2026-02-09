import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  Button,
  Card,
  CardContent,
  CardActions,
  Alert,
  CircularProgress,
  Chip
} from '@mui/material';
import {
  Download as DownloadIcon,
  Description as DescriptionIcon,
  CloudDownload as CloudDownloadIcon
} from '@mui/icons-material';
import api from '../services/api';

interface Template {
  id: string;
  filename: string;
  size: number;
  description: string;
}

const Templates: React.FC = () => {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [downloading, setDownloading] = useState<string | null>(null);

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get('/templates/list');
      setTemplates(response.data?.templates ?? []);
    } catch (err: any) {
      const msg = err.response?.data?.detail ?? err.message ?? 'Backend unreachable (check CORS or API URL)';
      setError(typeof msg === 'string' ? msg : 'Failed to load templates');
    } finally {
      setLoading(false);
    }
  };

  const downloadTemplate = async (templateId: string, filename: string) => {
    try {
      setDownloading(templateId);
      const response = await api.get(`/templates/download/${templateId}`, {
        responseType: 'blob',
      });
      
      // Create a download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to download template');
    } finally {
      setDownloading(null);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const getTemplateIcon = (filename: string) => {
    if (filename.includes('epic')) return '📋';
    if (filename.includes('feature')) return '⭐';
    if (filename.includes('story')) return '📝';
    if (filename.includes('clarity') || filename.includes('timesheet')) return '⏰';
    return '📄';
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
          Template Downloads
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Download CSV templates to understand the data format. Use these as examples when preparing your own data for upload.
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
          <CloudDownloadIcon sx={{ mr: 1 }} />
          Quick Start Guide
        </Typography>
        <Typography variant="body2" paragraph>
          1. Download the template files below to see the expected data format
        </Typography>
        <Typography variant="body2" paragraph>
          2. Prepare your data according to the template structure
        </Typography>
        <Typography variant="body2" paragraph>
          3. Upload your data files using the Data Upload page
        </Typography>
        <Typography variant="body2" color="primary">
          💡 Tip: The application comes pre-loaded with sample data. You can start exploring immediately!
        </Typography>
      </Paper>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      ) : (
        <Grid container spacing={3}>
          {templates.map((template) => (
            <Grid item xs={12} sm={6} md={6} key={template.id}>
              <Card 
                sx={{ 
                  height: '100%', 
                  display: 'flex', 
                  flexDirection: 'column',
                  transition: 'transform 0.2s, box-shadow 0.2s',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: 4
                  }
                }}
              >
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
                    <Typography variant="h3" sx={{ mr: 2 }}>
                      {getTemplateIcon(template.filename)}
                    </Typography>
                    <Box sx={{ flexGrow: 1 }}>
                      <Typography variant="h6" gutterBottom>
                        {template.filename}
                      </Typography>
                      <Chip 
                        label={formatFileSize(template.size)} 
                        size="small" 
                        sx={{ mb: 1 }}
                      />
                    </Box>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    {template.description}
                  </Typography>
                </CardContent>
                <CardActions sx={{ p: 2, pt: 0 }}>
                  <Button
                    variant="contained"
                    startIcon={downloading === template.id ? <CircularProgress size={20} /> : <DownloadIcon />}
                    onClick={() => downloadTemplate(template.id, template.filename)}
                    disabled={downloading === template.id}
                    fullWidth
                  >
                    {downloading === template.id ? 'Downloading...' : 'Download Template'}
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {templates.length === 0 && !loading && (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <DescriptionIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary">
            No templates available
          </Typography>
        </Paper>
      )}
    </Container>
  );
};

export default Templates;
