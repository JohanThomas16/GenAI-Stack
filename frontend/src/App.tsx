import React from 'react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { WorkflowCanvasWrapper } from './components/workflow/WorkflowCanvas';
import { WorkflowNode, WorkflowEdge } from './types/workflow';
import { workflowAPI } from './services/api';
import type { Workflow } from './types/workflow'; 

import './styles/globals.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, refetchOnWindowFocus: false }
  }
});

function App() {
  const [nodes, setNodes] = React.useState<WorkflowNode[]>([]);
  const [edges, setEdges] = React.useState<WorkflowEdge[]>([]);
  const [selectedNode, setSelectedNode] = React.useState<WorkflowNode | null>(null);

  const handleNodesChange = (newNodes: WorkflowNode[]) => {
    setNodes(newNodes);
  };

  const handleEdgesChange = (newEdges: WorkflowEdge[]) => {
    setEdges(newEdges);
  };

  const handleNodeSelect = (node: WorkflowNode | null) => {
    setSelectedNode(node);
  };

  const handleSave = async () => {
    // Save handler code here...
  };

  const handleOpenChat = () => {
    // Open chat logic here...
  };

  return (
    <div className="flex flex-col h-full min-h-screen">
      <QueryClientProvider client={queryClient}>
        <WorkflowCanvasWrapper
          nodes={nodes}
          edges={edges}
          onNodesChange={handleNodesChange}
          onEdgesChange={handleEdgesChange}
          onNodeSelect={handleNodeSelect}
          selectedNode={selectedNode}
          onSave={handleSave}
          onOpenChat={handleOpenChat}
        />
      </QueryClientProvider>
    </div>
  );
}
