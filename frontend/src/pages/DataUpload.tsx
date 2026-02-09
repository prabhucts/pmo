import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  LinearProgress,
  Alert,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import { uploadFile } from '../services/api';

interface UploadResult {
  filename: string;
  file_type: string;
  rows_processed: number;
  status: string;
  message: string;
}

const fileTypes = [
  { id: 'user-stories', label: 'User Stories', description: 'Rally User Stories export (CSV)' },
  { id: 'features', label: 'Features', description: 'Rally Features export (CSV)' },
  { id: 'epics', label: 'Epics', description: 'Rally Epics export (CSV)' },
  { id: 'clarity-timesheet', label: 'Clarity Timesheet', description: 'Clarity team allocations (CSV)' },
];

export default function DataUpload() {
  const [uploading, setUploading] = useState<{ [key: string]: boolean }>({});
  const [results, setResults] = useState<{ [key: string]: UploadResult }>({});

  const handleFileUpload = async (fileType: string, file: File) => {
    setUploading({ ...uploading, [fileType]: true });
    
    try {
      const result = await uploadFile(file, fileType);
      setResults({ ...results, [fileType]: result });
    } catch (error: any) {
      setResults({
        ...results,
        [fileType]: {
          filename: file.name,
          file_type: fileType,
          rows_processed: 0,
          status: 'error',
          message: error.response?.data?.detail || 'Upload failed',
        },
      });
    } finally {
      setUploading({ ...uploading, [fileType]: false });
    }
  };

  const handleFileChange = (fileType: string, event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      handleFileUpload(fileType, file);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Data Upload
      </Typography>
      <Typography variant="body2" color="textSecondary" gutterBottom sx={{ mb: 3 }}>
        Upload your Rally extracts and Clarity timesheet data
      </Typography>

      <Grid container spacing={3}>
        {fileTypes.map((type) => (
          <Grid item xs={12} md={6} key={type.id}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {type.label}
                </Typography>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  {type.description}
                </Typography>

                <Box sx={{ mt: 2 }}>
                  <input
                    accept=".csv,.xlsx,.xls"
                    style={{ display: 'none' }}
                    id={`upload-${type.id}`}
                    type="file"
                    onChange={(e) => handleFileChange(type.id, e)}
                    disabled={uploading[type.id]}
                  />
                  <label htmlFor={`upload-${type.id}`}>
                    <Button
                      variant="contained"
                      component="span"
                      startIcon={<CloudUploadIcon />}
                      disabled={uploading[type.id]}
                      fullWidth
                    >
                      {uploading[type.id] ? 'Uploading...' : 'Choose File'}
                    </Button>
                  </label>
                </Box>

                {uploading[type.id] && (
                  <Box sx={{ mt: 2 }}>
                    <LinearProgress />
                  </Box>
                )}

                {results[type.id] && (
                  <Box sx={{ mt: 2 }}>
                    <Alert
                      severity={results[type.id].status === 'success' ? 'success' : 'error'}
                    >
                      <Typography variant="body2">
                        <strong>{results[type.id].filename}</strong>
                      </Typography>
                      <Typography variant="body2">
                        {results[type.id].message}
                      </Typography>
                      {results[type.id].status === 'success' && (
                        <Typography variant="caption">
                          Processed {results[type.id].rows_processed} rows
                        </Typography>
                      )}
                    </Alert>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Box sx={{ mt: 4 }}>
        <Alert severity="info">
          <Typography variant="body2" gutterBottom>
            <strong>File Format Requirements:</strong>
          </Typography>
          <ul style={{ margin: 0, paddingLeft: 20 }}>
            <li>User Stories: Must include columns - Formatted ID, Name, Project, Plan Estimate</li>
            <li>Features: Must include columns - Formatted ID, Name, Parent</li>
            <li>Epics: Must include columns - Formatted ID, Name, Parent</li>
            <li>Clarity Timesheet: Must include Team, Resource Name, and weekly date columns</li>
          </ul>
        </Alert>
      </Box>
    </Box>
  );
}
