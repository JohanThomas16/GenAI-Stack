import { useCallback } from 'react';
import { useQuery } from 'react-query';
import { nodeAPI } from '../services/api';
import { NodeType } from '../types/workflow';
import { getNodeDefaults } from '../utils/nodeDefaults';
import toast from 'react-hot-toast';

export const useNodes = () => {
  // Fetch available node types
  const { data: nodeTypes } = useQuery(
    'node-types',
    () => nodeAPI.getNodeTypes().then(res => res.data),
    {
      onError: () => toast.error('Failed to load node types'),
    }
  );

  const createNode = useCallback((
    type: NodeType,
    position: { x: number; y: number },
    customData?: any
  ) => {
    const defaults = getNodeDefaults(type);
    
    return {
      id: `${type}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      type,
      position,
      data: {
        ...defaults,
        ...customData,
      },
    };
  }, []);

  const validateNodeConnection = useCallback((
    sourceType: NodeType,
    targetType: NodeType
  ): boolean => {
    // Define valid connections based on workflow logic
    const validConnections: Record<NodeType, NodeType[]> = {
      userQuery: ['llm', 'knowledgeBase', 'output'],
      knowledgeBase: ['llm', 'output'],
      llm: ['output'],
      output: [], // Output nodes don't connect to anything
    };

    return validConnections[sourceType]?.includes(targetType) ?? false;
  }, []);

  const getNodeColor = useCallback((type: NodeType): string => {
    const colors: Record<NodeType, string> = {
      userQuery: 'bg-blue-500',
      llm: 'bg-purple-500',
      knowledgeBase: 'bg-green-500',
      output: 'bg-orange-500',
    };
    return colors[type] || 'bg-gray-500';
  }, []);

  const getNodeIcon = useCallback((type: NodeType): string => {
    const icons: Record<NodeType, string> = {
      userQuery: '💬',
      llm: '🤖',
      knowledgeBase: '📚',
      output: '📤',
    };
    return icons[type] || '⚙️';
  }, []);

  return {
    nodeTypes,
    createNode,
    validateNodeConnection,
    getNodeColor,
    getNodeIcon,
  };
};
