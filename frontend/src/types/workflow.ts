export interface WorkflowNode {
  id: string;
  type: NodeType;
  position: { x: number; y: number };
  data: NodeData;
}

export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  sourceHandle?: string;
  targetHandle?: string;
  type?: string;
  animated?: boolean;
}

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

export type NodeType = 'userQuery' | 'llm' | 'knowledgeBase' | 'output';

export interface NodeData {
  label: string;
  description?: string;
  config?: Record<string, any>;
}
