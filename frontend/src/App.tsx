import React from 'react';
import { QueryClient, QueryClientProvider } from 'react-query';
import WorkflowBuilder from './WorkflowBuilder';  // Your main builder component
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
        <WorkflowBuilder />
      </QueryClientProvider>
    </div>
  );
}

export default App;
