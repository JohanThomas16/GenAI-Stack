// src/App.tsx

import React from 'react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { WorkflowCanvasWrapper } from './components/workflow/WorkflowCanvas';
// Import your styles (adjust the path if needed)
import './styles/globals.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, refetchOnWindowFocus: false }
  }
});

function App() {
  // Provide default required props to WorkflowCanvasWrapper.
  // Replace these with your actual app's state management if necessary.
  // For example, use hooks or context to share state.

  // Example props (replace with your managed state if needed):
  const nodes: any[] = [];
  const edges: any[] = [];
  const [selectedNode, setSelectedNode] = React.useState(null);

  const handleNodesChange = (newNodes: any[]) => {};
  const handleEdgesChange = (newEdges: any[]) => {};
  const handleNodeSelect = (node: any) => setSelectedNode(node);
  const handleSave = () => {};
  const handleOpenChat = () => {};

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
