import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Grid,
  Chip,
} from '@mui/material';
import { getRules, createRule, updateRule, deleteRule } from '../services/api';

interface Rule {
  id: number;
  name: string;
  description?: string;
  rule_type: string;
  parameters: any;
  is_active: boolean;
  priority: number;
}

export default function Rules() {
  const [rules, setRules] = useState<Rule[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingRule, setEditingRule] = useState<Rule | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    rule_type: 'conversion',
    parameters: '{}',
    is_active: true,
    priority: 0,
  });

  useEffect(() => {
    loadRules();
  }, []);

  const loadRules = async () => {
    try {
      const data = await getRules();
      setRules(data);
    } catch (error) {
      console.error('Error loading rules:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (rule?: Rule) => {
    if (rule) {
      setEditingRule(rule);
      setFormData({
        name: rule.name,
        description: rule.description || '',
        rule_type: rule.rule_type,
        parameters: JSON.stringify(rule.parameters, null, 2),
        is_active: rule.is_active,
        priority: rule.priority,
      });
    } else {
      setEditingRule(null);
      setFormData({
        name: '',
        description: '',
        rule_type: 'conversion',
        parameters: '{}',
        is_active: true,
        priority: 0,
      });
    }
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditingRule(null);
  };

  const handleSave = async () => {
    try {
      const ruleData = {
        ...formData,
        parameters: JSON.parse(formData.parameters),
      };

      if (editingRule) {
        await updateRule(editingRule.id, ruleData);
      } else {
        await createRule(ruleData);
      }

      await loadRules();
      handleCloseDialog();
    } catch (error) {
      console.error('Error saving rule:', error);
      alert('Error saving rule. Please check your JSON parameters.');
    }
  };

  const handleDelete = async (ruleId: number) => {
    if (window.confirm('Are you sure you want to delete this rule?')) {
      try {
        await deleteRule(ruleId);
        await loadRules();
      } catch (error) {
        console.error('Error deleting rule:', error);
      }
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
          Business Rules
        </Typography>
        <Button
          variant="contained"
          onClick={() => handleOpenDialog()}
        >
          Add New Rule
        </Button>
      </Box>

      <Grid container spacing={3}>
        {rules.map((rule) => (
          <Grid item xs={12} key={rule.id}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                  <Box flex={1}>
                    <Box display="flex" alignItems="center" gap={1} mb={1}>
                      <Chip
                        label={rule.rule_type}
                        size="small"
                        color="primary"
                      />
                      {rule.is_active ? (
                        <Chip label="Active" size="small" color="success" />
                      ) : (
                        <Chip label="Inactive" size="small" />
                      )}
                      <Chip label={`Priority: ${rule.priority}`} size="small" variant="outlined" />
                    </Box>
                    
                    <Typography variant="h6" gutterBottom>
                      {rule.name}
                    </Typography>
                    
                    {rule.description && (
                      <Typography variant="body2" color="textSecondary" gutterBottom>
                        {rule.description}
                      </Typography>
                    )}
                    
                    <Typography variant="caption" color="textSecondary" component="div" sx={{ mt: 1 }}>
                      Parameters: {JSON.stringify(rule.parameters)}
                    </Typography>
                  </Box>
                  
                  <Box display="flex" gap={1}>
                    <Button
                      variant="outlined"
                      size="small"
                      onClick={() => handleOpenDialog(rule)}
                    >
                      Edit
                    </Button>
                    <Button
                      variant="outlined"
                      size="small"
                      color="error"
                      onClick={() => handleDelete(rule.id)}
                    >
                      Delete
                    </Button>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingRule ? 'Edit Rule' : 'Add New Rule'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <TextField
              fullWidth
              label="Rule Name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              margin="normal"
            />
            
            <TextField
              fullWidth
              label="Description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              margin="normal"
              multiline
              rows={2}
            />
            
            <FormControl fullWidth margin="normal">
              <InputLabel>Rule Type</InputLabel>
              <Select
                value={formData.rule_type}
                onChange={(e) => setFormData({ ...formData, rule_type: e.target.value })}
                label="Rule Type"
              >
                <MenuItem value="conversion">Conversion</MenuItem>
                <MenuItem value="validation">Validation</MenuItem>
                <MenuItem value="alert">Alert</MenuItem>
                <MenuItem value="calculation">Calculation</MenuItem>
              </Select>
            </FormControl>
            
            <TextField
              fullWidth
              label="Parameters (JSON)"
              value={formData.parameters}
              onChange={(e) => setFormData({ ...formData, parameters: e.target.value })}
              margin="normal"
              multiline
              rows={4}
              helperText='Example: {"value": 13, "unit": "hours"}'
            />
            
            <TextField
              fullWidth
              label="Priority"
              type="number"
              value={formData.priority}
              onChange={(e) => setFormData({ ...formData, priority: parseInt(e.target.value) })}
              margin="normal"
            />
            
            <FormControlLabel
              control={
                <Switch
                  checked={formData.is_active}
                  onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                />
              }
              label="Active"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSave} variant="contained">
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
