export interface BaseNodeData {
  label: string;
  description?: string;
}

export interface UserQueryNodeData extends BaseNodeData {
  placeholder: string;
  validationRules?: Record<string, any>;
}

export interface LLMNodeData extends BaseNodeData {
  model: string;
  apiKey?: string;
  prompt: string;
  temperature: number;
  maxTokens?: number;
  topP?: number;
  frequencyPenalty?: number;
  presencePenalty?: number;
}

export interface KnowledgeBaseNodeData extends BaseNodeData {
  fileId?: string;
  fileName?: string;
  embeddingModel: string;
  chunkSize: number;
  chunkOverlap: number;
  similarityThreshold: number;
  maxResults: number;
}

export interface OutputNodeData extends BaseNodeData {
  format: 'text' | 'json' | 'markdown';
  template?: string;
  includeSources: boolean;
  includeMetadata: boolean;
}

// export interface ChatMessage {
//   id: string;
//   type: 'user' | 'assistant' | 'system';
//   content: string;
//   timestamp: Date;
//   metadata?: Record<string, any>;
// }

// export interface ChatSession {
//   id: string;
//   workflowId?: string;
//   messages: ChatMessage[];
//   isActive: boolean;
//   startedAt: Date;
//   lastActivity: Date;
// }
export interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: string;
}

export interface ChatSession {
  id: string;
  workflowId?: string;
  createdAt: string;
  updatedAt: string;
}
