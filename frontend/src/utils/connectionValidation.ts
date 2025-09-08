import { WorkflowNode, WorkflowEdge } from '../types/workflow';

export const validateWorkflowConnections = (
  nodes: WorkflowNode[], 
  edges: WorkflowEdge[]
): { isValid: boolean; errors: string[] } => {
  const errors: string[] = [];

  // Check if workflow has nodes
  if (nodes.length === 0) {
    errors.push('Workflow must contain at least one node');
    return { isValid: false, errors };
  }

  // Check for isolated nodes (except single node workflows)
  if (nodes.length > 1) {
    const connectedNodes = new Set<string>();
    edges.forEach(edge => {
      connectedNodes.add(edge.source);
      connectedNodes.add(edge.target);
    });

    const isolatedNodes = nodes.filter(node => !connectedNodes.has(node.id));
    if (isolatedNodes.length > 0) {
      errors.push(`Isolated nodes detected: ${isolatedNodes.map(n => n.data.label).join(', ')}`);
    }
  }

  // Check for cycles
  if (hasCycle(nodes, edges)) {
    errors.push('Workflow contains circular dependencies');
  }

  // Check for valid node connections
  edges.forEach(edge => {
    const sourceNode = nodes.find(n => n.id === edge.source);
    const targetNode = nodes.find(n => n.id === edge.target);

    if (!sourceNode || !targetNode) {
      errors.push(`Invalid edge connection: ${edge.id}`);
      return;
    }

    if (!isValidConnection(sourceNode.type, targetNode.type)) {
      errors.push(
        `Invalid connection: ${sourceNode.data.label} cannot connect to ${targetNode.data.label}`
      );
    }
  });

  return {
    isValid: errors.length === 0,
    errors,
  };
};

const hasCycle = (nodes: WorkflowNode[], edges: WorkflowEdge[]): boolean => {
  const visited = new Set<string>();
  const recursionStack = new Set<string>();

  const adjacencyList: Record<string, string[]> = {};
  nodes.forEach(node => {
    adjacencyList[node.id] = [];
  });

  edges.forEach(edge => {
    adjacencyList[edge.source].push(edge.target);
  });

  const dfs = (nodeId: string): boolean => {
    visited.add(nodeId);
    recursionStack.add(nodeId);

    for (const neighbor of adjacencyList[nodeId] || []) {
      if (!visited.has(neighbor)) {
        if (dfs(neighbor)) return true;
      } else if (recursionStack.has(neighbor)) {
        return true; // Cycle detected
      }
    }

    recursionStack.delete(nodeId);
    return false;
  };

  for (const node of nodes) {
    if (!visited.has(node.id)) {
      if (dfs(node.id)) return true;
    }
  }

  return false;
};

const isValidConnection = (sourceType: string, targetType: string): boolean => {
  const validConnections: Record<string, string[]> = {
    userQuery: ['llm', 'knowledgeBase', 'output'],
    knowledgeBase: ['llm', 'output'],
    llm: ['output'],
    output: [],
  };

  return validConnections[sourceType]?.includes(targetType) ?? false;
};
