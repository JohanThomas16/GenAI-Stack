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

export default App;
