import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Dashboard API
export const getDashboardSummary = async () => {
  const response = await api.get('/dashboard/summary');
  return response.data;
};

// Chat API
export const sendChatMessage = async (message: string, sessionId?: string) => {
  const response = await api.post('/chat/message', { message, session_id: sessionId });
  return response.data;
};

export const getChatHistory = async (sessionId: string) => {
  const response = await api.get(`/chat/history/${sessionId}`);
  return response.data;
};

// Projects API
export const getProjects = async () => {
  const response = await api.get('/projects/');
  return response.data;
};

export const getProject = async (projectId: number) => {
  const response = await api.get(`/projects/${projectId}`);
  return response.data;
};

export const getProjectSummary = async (projectId: number) => {
  const response = await api.get(`/projects/${projectId}/summary`);
  return response.data;
};

// Insights API
export const getInsights = async (type?: string, resolved?: boolean) => {
  const params = new URLSearchParams();
  if (type) params.append('insight_type', type);
  if (resolved !== undefined) params.append('resolved', resolved.toString());
  
  const response = await api.get(`/insights/?${params.toString()}`);
  return response.data;
};

export const generateInsights = async () => {
  const response = await api.get('/insights/generate');
  return response.data;
};

export const resolveInsight = async (insightId: number) => {
  const response = await api.patch(`/insights/${insightId}/resolve`);
  return response.data;
};

// Rules API
export const getRules = async (ruleType?: string, activeOnly: boolean = true) => {
  const params = new URLSearchParams();
  if (ruleType) params.append('rule_type', ruleType);
  params.append('active_only', activeOnly.toString());
  
  const response = await api.get(`/rules/?${params.toString()}`);
  return response.data;
};

export const createRule = async (rule: any) => {
  const response = await api.post('/rules/', rule);
  return response.data;
};

export const updateRule = async (ruleId: number, rule: any) => {
  const response = await api.put(`/rules/${ruleId}`, rule);
  return response.data;
};

export const deleteRule = async (ruleId: number) => {
  const response = await api.delete(`/rules/${ruleId}`);
  return response.data;
};

// Upload API
export const uploadFile = async (file: File, fileType: string) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post(`/uploads/${fileType}`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export default api;
