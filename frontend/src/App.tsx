import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from 'react-query';
import Dashboard from './components/Dashboard';
import WorkflowCanvasWrapper from './components/workflow/WorkflowCanvas'; // adjust import if needed

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, refetchOnWindowFocus: false }
  }
});

function App() {
  const [currentWorkflowId, setCurrentWorkflowId] = useState<string | null>(null);

  // When user chooses to edit stack on dashboard
  const handleEditStack = (id: string) => {
    setCurrentWorkflowId(id);
  };

  // To return to dashboard from canvas (add a Back button for this)
  const handleBackToDashboard = () => {
    setCurrentWorkflowId(null);
  };

  return (
    <QueryClientProvider client={queryClient}>
      {currentWorkflowId ? (
        <WorkflowCanvasWrapper 
          workflowId={currentWorkflowId} 
          onBack={handleBackToDashboard} 
        />
      ) : (
        <Dashboard onEditStack={handleEditStack} />
      )}
    </QueryClientProvider>
  );
}

export default App;
