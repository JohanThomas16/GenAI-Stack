import React, { useState, useCallback } from 'react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import { Header } from './components/common/Header';
import { ComponentLibrary } from './components/workflow/ComponentLibrary';
import { WorkflowCanvasWrapper } from './components/workflow/WorkflowCanvas';
import { ConfigurationPanel } from './components/workflow/ConfigurationPanel';
import { ChatInterface } from './components/chat/ChatInterface';
import { useWorkflow } from './hooks/useWorkflow';
import { validateWorkflowConnections } from './utils/connectionValidation';
import './styles/globals.css';
import './styles/reactflow.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function WorkflowBuilder() {
  const [chatOpen, setChatOpen] = useState(false);
  const [workflowId] = useState<string>('demo-workflow');

  const {
    nodes,
    edges,
    selectedNode,
    setNodes,
    setEdges,
    setSelectedNode,
    saveWorkflow,
    isSaving,
  } = useWorkflow(workflowId);

  const handleDragStart = useCallback((event: React.DragEvent, component: any) => {
    // Drag start is handled in ComponentLibrary
  }, []);

  const handleSave = useCallback(() => {
    const validation = validateWorkflowConnections(nodes, edges);
    
    if (!validation.isValid) {
      console.warn('Workflow validation failed:', validation.errors);
    }
    
    saveWorkflow({
      id: workflowId,
      name: 'Chat With AI',
      description: 'GenAI Stack workflow for intelligent conversations',
    });
  }, [nodes, edges, saveWorkflow, workflowId]);

  const handleNodeUpdate = useCallback((nodeId: string, updates: any) => {
    const updatedNodes = nodes.map((node: any) =>
      node.id === nodeId ? { ...node, ...updates } : node
    );
    setNodes(updatedNodes);
  }, [nodes, setNodes]);

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      <Header 
        onSave={handleSave}
        onChat={() => setChatOpen(true)}
        saved={false}
        loading={isSaving}
      />
      
      <div className="flex-1 flex overflow-hidden">
        <ComponentLibrary onDragStart={handleDragStart} />
        
        <WorkflowCanvasWrapper
          nodes={nodes}
          edges={edges}
          onNodesChange={setNodes}
          onEdgesChange={setEdges}
          onNodeSelect={setSelectedNode}
          selectedNode={selectedNode}
          onSave={handleSave}
          onOpenChat={() => setChatOpen(true)}
        />
        
        {selectedNode && (
          <ConfigurationPanel 
            node={selectedNode}
            onClose={() => setSelectedNode(null)}
            onUpdate={handleNodeUpdate}
          />
        )}
      </div>
      
      <ChatInterface 
        isOpen={chatOpen}
        onClose={() => setChatOpen(false)}
        workflowId={workflowId}
      />
      
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          className: 'toast',
        }}
      />
    </div>
  );
}

function App() {
  return (
   <div className="flex flex-col h-full">
      <QueryClientProvider client={queryClient}>
        <WorkflowBuilder />
      </QueryClientProvider>
    </div>
  );
}

export default App;
