import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  CircularProgress,
  Chip,
  LinearProgress,
} from '@mui/material';
import { getProjects, getProjectSummary } from '../services/api';

interface Project {
  id: number;
  itpr_code: string;
  name: string;
  status: string;
  owner?: string;
}

interface ProjectSummary {
  project: Project;
  epics_count: number;
  features_count: number;
  user_stories_count: number;
  total_story_points: number;
  completed_story_points: number;
  completion_percentage: number;
}

export default function Projects() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [summaries, setSummaries] = useState<{ [key: number]: ProjectSummary }>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      const projectsData = await getProjects();
      setProjects(projectsData);
      
      // Load summaries for each project
      for (const project of projectsData.slice(0, 10)) {
        try {
          const summary = await getProjectSummary(project.id);
          setSummaries(prev => ({ ...prev, [project.id]: summary }));
        } catch (error) {
          console.error(`Error loading summary for project ${project.id}:`, error);
        }
      }
    } catch (error) {
      console.error('Error loading projects:', error);
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

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Projects
      </Typography>
      <Typography variant="body2" color="textSecondary" gutterBottom sx={{ mb: 3 }}>
        Total: {projects.length} projects
      </Typography>

      <Grid container spacing={3}>
        {projects.map((project) => {
          const summary = summaries[project.id];
          
          return (
            <Grid item xs={12} md={6} key={project.id}>
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Typography variant="h6">
                      {project.itpr_code}
                    </Typography>
                    <Chip 
                      label={project.status}
                      color={project.status === 'Active' ? 'success' : 'default'}
                      size="small"
                    />
                  </Box>
                  
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    {project.name}
                  </Typography>
                  
                  {project.owner && (
                    <Typography variant="caption" color="textSecondary" display="block" sx={{ mb: 2 }}>
                      Owner: {project.owner}
                    </Typography>
                  )}

                  {summary ? (
                    <>
                      <Box sx={{ mt: 2 }}>
                        <Typography variant="body2" gutterBottom>
                          Progress: {summary.completion_percentage.toFixed(1)}%
                        </Typography>
                        <LinearProgress 
                          variant="determinate" 
                          value={summary.completion_percentage}
                          sx={{ mb: 2 }}
                        />
                      </Box>

                      <Grid container spacing={2}>
                        <Grid item xs={6}>
                          <Typography variant="caption" color="textSecondary">
                            Epics: {summary.epics_count}
                          </Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="caption" color="textSecondary">
                            Features: {summary.features_count}
                          </Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="caption" color="textSecondary">
                            Stories: {summary.user_stories_count}
                          </Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="caption" color="textSecondary">
                            Points: {summary.total_story_points.toFixed(1)}
                          </Typography>
                        </Grid>
                      </Grid>
                    </>
                  ) : (
                    <Typography variant="caption" color="textSecondary">
                      Loading details...
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>
    </Box>
  );
}
