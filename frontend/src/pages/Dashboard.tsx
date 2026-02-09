import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  CircularProgress,
} from '@mui/material';
import { getDashboardSummary } from '../services/api';

interface DashboardData {
  total_projects: number;
  active_projects: number;
  total_sprints: number;
  active_sprint: string | null;
  total_teams: number;
  total_team_members: number;
  total_user_stories: number;
  total_story_points: number;
  insights_count: { [key: string]: number };
}

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const [error, setError] = useState<string | null>(null);

  const loadDashboard = async () => {
    try {
      setError(null);
      const summary = await getDashboardSummary();
      setData(summary);
    } catch (err: any) {
      console.error('Error loading dashboard:', err);
      const msg = err.response?.data?.detail ?? err.message ?? 'Backend unreachable (check CORS or URL)';
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg));
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (!data) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom>
          Dashboard
        </Typography>
        <Typography color="error">Failed to load dashboard data</Typography>
        {error && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            {error}
          </Typography>
        )}
      </Box>
    );
  }

  const statCards = [
    { title: 'Total Projects', value: data.total_projects, subtitle: `${data.active_projects} active` },
    { title: 'Total Teams', value: data.total_teams, subtitle: `${data.total_team_members} members` },
    { title: 'User Stories', value: data.total_user_stories, subtitle: `${data.total_story_points.toFixed(1)} story points` },
    { title: 'Active Sprint', value: data.active_sprint || 'None', subtitle: `${data.total_sprints} total sprints` },
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {statCards.map((card) => (
          <Grid item xs={12} sm={6} md={3} key={card.title}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  {card.title}
                </Typography>
                <Typography variant="h4" component="div">
                  {card.value}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  {card.subtitle}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>
        Active Insights
      </Typography>
      
      <Grid container spacing={3}>
        {Object.entries(data.insights_count).map(([type, count]) => (
          <Grid item xs={12} sm={6} md={4} key={type}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </Typography>
                <Typography variant="h3" color="primary">
                  {count}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Active insights
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
        
        {Object.keys(data.insights_count).length === 0 && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="body1" color="textSecondary">
                  No active insights. Everything looks good!
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Box>
  );
}
