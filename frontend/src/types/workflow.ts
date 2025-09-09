// Import types from @xyflow/react to extend and ensure compatibility
import { Node, Edge, XYPosition } from '@xyflow/react';

// Allow NodeData to have arbitrary keys to satisfy React Flow's expectation
export interface NodeData {
  label: string;
  description?: string;
  config?: Record<string, any>;
  [key: string]: any; // <-- add index signature for compatibility
}

// NodeType string literal union
export type NodeType = 'userQuery' | 'llm' | 'knowledgeBase' | 'output';

// WorkflowNode extends React Flow's Node with parameters for NodeData and NodeType
export interface WorkflowNode extends Node<NodeData, string> {
  type: NodeType;
  // position and id are inherited from Node
}

// WorkflowEdge extends React Flow's Edge


export interface WorkflowEdge extends Edge<Record<string, unknown>, string> {
  sourceHandle?: string;
  targetHandle?: string;
  type?: string;
  animated?: boolean;
  data?: Record<string, unknown>;  // <-- ensure data field is defined
}

// Workflow with nodes and edges arrays
export interface Workflow {
  id: string;
  name: string;
  description?: string;
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  isActive?: boolean;
  createdAt?: string;
  updatedAt?: string;
}

export interface WorkflowExecution {
  id: string;
  workflowId: string;
  status: 'running' | 'completed' | 'failed';
  result?: any;
  error?: string;
  startedAt: string;
  completedAt?: string;
}
