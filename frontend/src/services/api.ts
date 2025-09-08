import axios from 'axios';
import { Workflow, WorkflowExecution } from '../types/workflow';
import { ChatMessage, ChatSession } from '../types/nodes';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

export const workflowAPI = {
  // List workflows
  getWorkflows: () => apiClient.get('/api/v1/workflows'),

  // Get single workflow
  getWorkflow: (id: string) => apiClient.get(`/api/v1/workflows/${id}`),

  // Create workflow (automatically sends JSON)
  createWorkflow: (workflow: Omit<Workflow, 'id'>) =>
    apiClient.post('/api/v1/workflows', workflow),

  // Update workflow
  updateWorkflow: (id: string, workflow: Partial<Workflow>) =>
    apiClient.put(`/api/v1/workflows/${id}`, workflow),

  // Delete workflow
  deleteWorkflow: (id: string) => apiClient.delete(`/api/v1/workflows/${id}`),

  // Validate workflow
  validateWorkflow: (workflow: { nodes: WorkflowNode[]; edges: WorkflowEdge[] }) =>
    apiClient.post('/api/v1/workflows/validate', workflow),  // adjust endpoint if needed

  // Chat session endpoints
  listChatSessions: () => apiClient.get('/api/v1/chat/sessions'),
  createChatSession: (data: { workflow_id: string }) =>
    apiClient.post('/api/v1/chat/sessions', data),
  getChatSession: (id: string) =>
    apiClient.get(`/api/v1/chat/sessions/${id}`),
   sendMessage: (message: string, workflowId?: string, sessionId?: string) =>
  api.post('/api/v1/chat/sessions/${sessionId}/messages', { message, workflow_id: workflowId }),
};


export const chatAPI = {
  // Chat operations
  getSessions: () => api.get<ChatSession[]>('/api/v1/chat/sessions'),
  createSession: (workflowId?: string) => 
    api.post<ChatSession>('/api/v1/chat/sessions', { workflowId }),
  getMessages: (sessionId: string) => 
    api.get<ChatMessage[]>(`/api/v1/chat/sessions/${sessionId}/messages`),
 sendMessage: (message: string, workflowId?: string, sessionId?: string) =>
    api.post(
      `/api/v1/chat/sessions/${sessionId}/messages`,
      { message, workflow_id: workflowId }
    ),
};

export const nodeAPI = {
  getNodeTypes: () => api.get('/api/v1/nodes/types'),
  getNodeDefaults: (nodeType: string) => api.get(`/api/v1/nodes/defaults/${nodeType}`),
  validateNodeConfig: (nodeType: string, config: any) =>
    api.post(`/api/v1/nodes/validate?node_type=${nodeType}`, config),
};

export const documentAPI = {
  uploadDocument: (file: File, workflowId?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    if (workflowId) {
      formData.append('workflow_id', workflowId);
    }
    return api.post('/api/v1/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  getDocuments: () => api.get('/api/v1/documents'),
  deleteDocument: (id: string) => api.delete(`/api/v1/documents/${id}`),
};

export default api;
