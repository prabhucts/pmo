import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Chip,
  Button,
  Grid,
  Alert,
} from '@mui/material';
import { getInsights, generateInsights, resolveInsight } from '../services/api';

interface Insight {
  id: number;
  insight_type: string;
  title: string;
  description?: string;
  severity: string;
  is_resolved: boolean;
  created_at: string;
}

export default function Insights() {
  const [insights, setInsights] = useState<Insight[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    loadInsights();
  }, []);

  const loadInsights = async () => {
    try {
      const data = await getInsights();
      setInsights(data);
    } catch (error) {
      console.error('Error loading insights:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      await generateInsights();
      await loadInsights();
    } catch (error) {
      console.error('Error generating insights:', error);
    } finally {
      setGenerating(false);
    }
  };

  const handleResolve = async (insightId: number) => {
    try {
      await resolveInsight(insightId);
      await loadInsights();
    } catch (error) {
      console.error('Error resolving insight:', error);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'error';
      case 'warning':
        return 'warning';
      case 'info':
        return 'info';
      default:
        return 'default';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">
          Insights
        </Typography>
        <Button
          variant="contained"
          onClick={handleGenerate}
          disabled={generating}
        >
          {generating ? 'Generating...' : 'Generate New Insights'}
        </Button>
      </Box>

      {insights.length === 0 ? (
        <Alert severity="success">
          No active insights. All systems operating normally!
        </Alert>
      ) : (
        <Grid container spacing={3}>
          {insights.map((insight) => (
            <Grid item xs={12} key={insight.id}>
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                    <Box flex={1}>
                      <Box display="flex" alignItems="center" gap={1} mb={1}>
                        <Chip
                          label={insight.severity.toUpperCase()}
                          color={getSeverityColor(insight.severity) as any}
                          size="small"
                        />
                        <Chip
                          label={insight.insight_type.replace(/_/g, ' ').toUpperCase()}
                          size="small"
                          variant="outlined"
                        />
                      </Box>
                      
                      <Typography variant="h6" gutterBottom>
                        {insight.title}
                      </Typography>
                      
                      {insight.description && (
                        <Typography variant="body2" color="textSecondary" gutterBottom>
                          {insight.description}
                        </Typography>
                      )}
                      
                      <Typography variant="caption" color="textSecondary">
                        {new Date(insight.created_at).toLocaleString()}
                      </Typography>
                    </Box>
                    
                    <Button
                      variant="outlined"
                      size="small"
                      onClick={() => handleResolve(insight.id)}
                    >
                      Resolve
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
}
