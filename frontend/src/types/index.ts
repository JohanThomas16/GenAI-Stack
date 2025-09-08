export interface NodeData {
  [key: string]: any;
  label?: string;
  type?: string;
  configuration?: any;
}

export interface WorkflowNode {
  id: string;
  type: string;
  position: { x: number; y: number };
  data: NodeData;
}

export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  type?: string;
}
