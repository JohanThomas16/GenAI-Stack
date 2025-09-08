import { useState, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { workflowAPI } from '../services/api';
import { Workflow, WorkflowNode, WorkflowEdge } from '../types/workflow';
import toast from 'react-hot-toast';

export const useWorkflow = (workflowId?: string) => {
  const queryClient = useQueryClient();
  const [nodes, setNodes] = useState<WorkflowNode[]>([]);
  const [edges, setEdges] = useState<WorkflowEdge[]>([]);
  const [selectedNode, setSelectedNode] = useState<WorkflowNode | null>(null);

  // Fetch workflows
  const { data: workflows, isLoading: workflowsLoading } = useQuery(
    'workflows',
    () => workflowAPI.getWorkflows().then(res => res.data),
    {
      onError: () => toast.error('Failed to load workflows'),
    }
  );

  // Fetch specific workflow
  const { data: currentWorkflow, isLoading: workflowLoading } = useQuery(
    ['workflow', workflowId],
    () => workflowAPI.getWorkflow(workflowId!).then(res => res.data),
    {
      enabled: !!workflowId,
      onSuccess: (workflow) => {
        setNodes(workflow.nodes);
        setEdges(workflow.edges);
      },
      onError: () => toast.error('Failed to load workflow'),
    }
  );

  // Create workflow mutation
  const createWorkflowMutation = useMutation(
    (workflow: Omit<Workflow, 'id'>) => workflowAPI.createWorkflow(workflow),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('workflows');
        toast.success('Workflow created successfully');
      },
      onError: () => toast.error('Failed to create workflow'),
    }
  );

  // Update workflow mutation
  const updateWorkflowMutation = useMutation(
    ({ id, workflow }: { id: string; workflow: Partial<Workflow> }) =>
      workflowAPI.updateWorkflow(id, workflow),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('workflows');
        queryClient.invalidateQueries(['workflow', workflowId]);
        toast.success('Workflow saved successfully');
      },
      onError: () => toast.error('Failed to save workflow'),
    }
  );

  // Delete workflow mutation
  const deleteWorkflowMutation = useMutation(
    (id: string) => workflowAPI.deleteWorkflow(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('workflows');
        toast.success('Workflow deleted successfully');
      },
      onError: () => toast.error('Failed to delete workflow'),
    }
  );

  // Validate workflow mutation
  const validateWorkflowMutation = useMutation(
    (workflow: { nodes: WorkflowNode[]; edges: WorkflowEdge[] }) =>
      workflowAPI.validateWorkflow(workflow),
    {
      onError: () => toast.error('Workflow validation failed'),
    }
  );

  const addNode = useCallback((node: WorkflowNode) => {
    setNodes(prev => [...prev, node]);
  }, []);

  const updateNode = useCallback((nodeId: string, updates: Partial<WorkflowNode>) => {
    setNodes(prev => prev.map(node => 
      node.id === nodeId ? { ...node, ...updates } : node
    ));
  }, []);

  const removeNode = useCallback((nodeId: string) => {
    setNodes(prev => prev.filter(node => node.id !== nodeId));
    setEdges(prev => prev.filter(edge => 
      edge.source !== nodeId && edge.target !== nodeId
    ));
    if (selectedNode?.id === nodeId) {
      setSelectedNode(null);
    }
  }, [selectedNode]);

  const addEdge = useCallback((edge: WorkflowEdge) => {
    setEdges(prev => [...prev, edge]);
  }, []);

  const removeEdge = useCallback((edgeId: string) => {
    setEdges(prev => prev.filter(edge => edge.id !== edgeId));
  }, []);

  const saveWorkflow = useCallback((workflowData: Partial<Workflow>) => {
    const workflow = {
      ...workflowData,
      nodes,
      edges,
    };

    if (workflowId) {
      updateWorkflowMutation.mutate({ id: workflowId, workflow });
    } else {
      createWorkflowMutation.mutate(workflow as Omit<Workflow, 'id'>);
    }
  }, [nodes, edges, workflowId]);

  return {
    // Data
    workflows,
    currentWorkflow,
    nodes,
    edges,
    selectedNode,
    
    // Loading states
    workflowsLoading,
    workflowLoading,
    isSaving: createWorkflowMutation.isLoading || updateWorkflowMutation.isLoading,
    
    // Actions
    setNodes,
    setEdges,
    setSelectedNode,
    addNode,
    updateNode,
    removeNode,
    addEdge,
    removeEdge,
    saveWorkflow,
    deleteWorkflow: deleteWorkflowMutation.mutate,
    validateWorkflow: validateWorkflowMutation.mutate,
    
    // Mutations
    createWorkflow: createWorkflowMutation.mutate,
    updateWorkflow: updateWorkflowMutation.mutate,
  };
};
