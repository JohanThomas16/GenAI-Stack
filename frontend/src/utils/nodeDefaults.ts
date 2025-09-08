import { NodeType } from '../types/workflow';
import { 
  UserQueryNodeData, 
  LLMNodeData, 
  KnowledgeBaseNodeData, 
  OutputNodeData 
} from '../types/nodes';

export const getNodeDefaults = (type: NodeType) => {
  switch (type) {
    case 'userQuery':
      return {
        label: 'User Query',
        description: 'Entry point for queries',
        placeholder: 'Enter your question here...',
        validationRules: {},
      } as UserQueryNodeData;

    case 'llm':
      return {
        label: 'LLM (OpenAI)',
        description: 'Language model processing',
        model: 'gpt-3.5-turbo',
        prompt: 'You are a helpful assistant.',
        temperature: 0.7,
        maxTokens: 150,
        topP: 1.0,
        frequencyPenalty: 0.0,
        presencePenalty: 0.0,
      } as LLMNodeData;

    case 'knowledgeBase':
      return {
        label: 'Knowledge Base',
        description: 'Document knowledge source',
        embeddingModel: 'text-embedding-3-large',
        chunkSize: 1000,
        chunkOverlap: 200,
        similarityThreshold: 0.7,
        maxResults: 5,
      } as KnowledgeBaseNodeData;

    case 'output':
      return {
        label: 'Output',
        description: 'Final response output',
        format: 'text',
        includeSources: true,
        includeMetadata: false,
      } as OutputNodeData;

    default:
      return {
        label: 'Unknown Node',
        description: 'Unknown node type',
      };
  }
};

export const getNodeDisplayName = (type: NodeType): string => {
  const names: Record<NodeType, string> = {
    userQuery: 'User Query',
    llm: 'LLM (OpenAI)',
    knowledgeBase: 'Knowledge Base',
    output: 'Output',
  };
  return names[type] || type;
};
