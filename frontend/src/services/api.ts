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

export const workflowAPI = {
  // Workflow operations
  getWorkflows: () => api.get<Workflow[]>('/api/v1/workflows'),
  getWorkflow: (id: string) => api.get<Workflow>(`/api/v1/workflows/${id}`),
  createWorkflow: (workflow: Omit<Workflow, 'id'>) => 
    api.post<Workflow>('/api/v1/workflows', workflow),
  updateWorkflow: (id: string, workflow: Partial<Workflow>) => 
    api.put<Workflow>(`/api/v1/workflows/${id}`, workflow),
  deleteWorkflow: (id: string) => api.delete(`/api/v1/workflows/${id}`),
  
  // Workflow execution
  executeWorkflow: (workflowId: string, inputData: any) =>
    api.post<WorkflowExecution>(`/api/v1/workflows/${workflowId}/execute`, { inputData }),
  
  // Validation
  validateWorkflow: (workflow: { nodes: any[], edges: any[] }) =>
    api.post('/api/v1/workflows/validate', { configuration: workflow }),
};

export const chatAPI = {
  // Chat operations
  getSessions: () => api.get<ChatSession[]>('/api/v1/chat/sessions'),
  createSession: (workflowId?: string) => 
    api.post<ChatSession>('/api/v1/chat/sessions', { workflowId }),
  getMessages: (sessionId: string) => 
    api.get<ChatMessage[]>(`/api/v1/chat/sessions/${sessionId}/messages`),
  sendMessage: (message: string, workflowId?: string, sessionId?: string) =>
    api.post('/api/v1/chat/execute', { message, workflowId, sessionId }),
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
