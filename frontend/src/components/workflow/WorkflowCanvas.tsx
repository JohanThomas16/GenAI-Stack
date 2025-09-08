import React, { useCallback, useRef, useState } from 'react';
import {
  ReactFlow,
  addEdge,
  useNodesState,
  useEdgesState,
  useReactFlow,
  Controls,
  Background,
  Connection,
  Edge,
  Node,
  ReactFlowProvider,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import { WorkflowNode, WorkflowEdge } from '../../types/workflow';
import { UserQueryNode } from './NodeTypes/UserQueryNode';
import { LLMNode } from './NodeTypes/LLMNode';
import { KnowledgeBaseNode } from './NodeTypes/KnowledgeBaseNode';
import { OutputNode } from './NodeTypes/OutputNode';
import { TabHeader } from '../common/TabHeader';
import { ControlButtons } from '../common/ControlButtons';
import { Plus } from 'lucide-react';

const nodeTypes = {
  userQuery: UserQueryNode,
  llm: LLMNode,
  knowledgeBase: KnowledgeBaseNode,
  output: OutputNode,
};

interface WorkflowCanvasProps {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  onNodesChange: (nodes: WorkflowNode[]) => void;
  onEdgesChange: (edges: WorkflowEdge[]) => void;
  onNodeSelect: (node: WorkflowNode | null) => void;
  selectedNode: WorkflowNode | null;
  onSave: () => void;
  onOpenChat: () => void;
}

export const WorkflowCanvas: React.FC<WorkflowCanvasProps> = ({
  nodes,
  edges,
  onNodesChange,
  onEdgesChange,
  onNodeSelect,
  selectedNode,
  onSave,
  onOpenChat,
}) => {
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const { screenToFlowPosition, zoomIn, zoomOut, fitView, getZoom } = useReactFlow();
  const [reactFlowInstance, setReactFlowInstance] = useState<any>(null);

  const [reactNodes, setReactNodes, onReactNodesChange] = useNodesState(nodes);
  const [reactEdges, setReactEdges, onReactEdgesChange] = useEdgesState(edges);

  React.useEffect(() => {
    setReactNodes(nodes);
  }, [nodes, setReactNodes]);

  React.useEffect(() => {
    setReactEdges(edges);
  }, [edges, setReactEdges]);

  const onConnect = useCallback(
    (params: Connection) => {
      const newEdge: WorkflowEdge = {
        id: `edge-${params.source}-${params.target}`,
        source: params.source!,
        target: params.target!,
        sourceHandle: params.sourceHandle,
        targetHandle: params.targetHandle,
        type: 'default',
        animated: false,
      };
      
      const updatedEdges = addEdge(newEdge, reactEdges);
      setReactEdges(updatedEdges);
      onEdgesChange(updatedEdges);
    },
    [reactEdges, setReactEdges, onEdgesChange]
  );

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();

      const reactFlowBounds = reactFlowWrapper.current?.getBoundingClientRect();
      if (!reactFlowBounds) return;

      const data = event.dataTransfer.getData('application/json');
      if (!data) return;

      const nodeData = JSON.parse(data);
      const position = screenToFlowPosition({
        x: event.clientX - reactFlowBounds.left,
        y: event.clientY - reactFlowBounds.top,
      });

      const newNode: WorkflowNode = {
        id: `${nodeData.type}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        type: nodeData.type,
        position,
        data: {
          ...nodeData.data,
          label: nodeData.name,
        },
      };

      const updatedNodes = [...reactNodes, newNode];
      setReactNodes(updatedNodes);
      onNodesChange(updatedNodes);
    },
    [screenToFlowPosition, reactNodes, setReactNodes, onNodesChange]
  );

  const onNodeClick = useCallback(
    (event: React.MouseEvent, node: Node) => {
      event.stopPropagation();
      const workflowNode = reactNodes.find(n => n.id === node.id) as WorkflowNode;
      onNodeSelect(workflowNode || null);
    },
    [reactNodes, onNodeSelect]
  );

  const onPaneClick = useCallback(() => {
    onNodeSelect(null);
  }, [onNodeSelect]);

  const handleNodesChange = useCallback(
    (changes: any) => {
      onReactNodesChange(changes);
      // Convert back to WorkflowNode[] format
      const updatedNodes = reactNodes.map(node => ({
        ...node,
        type: node.type as any,
      })) as WorkflowNode[];
      onNodesChange(updatedNodes);
    },
    [onReactNodesChange, reactNodes, onNodesChange]
  );

  const handleEdgesChange = useCallback(
    (changes: any) => {
      onReactEdgesChange(changes);
      onEdgesChange(reactEdges);
    },
    [onReactEdgesChange, reactEdges, onEdgesChange]
  );

  return (
    <div className="flex-1 relative">
      {/* Tab Header */}
      <div className="absolute top-4 left-4 z-10">
        <TabHeader title="Chat With AI" />
      </div>
      
      <div 
        ref={reactFlowWrapper}
        className="h-full workflow-canvas"
      >
        <ReactFlow
          nodes={reactNodes.map(node => ({
            ...node,
            selected: selectedNode?.id === node.id,
          }))}
          edges={reactEdges}
          onNodesChange={handleNodesChange}
          onEdgesChange={handleEdgesChange}
          onConnect={onConnect}
          onDrop={onDrop}
          onDragOver={onDragOver}
          onNodeClick={onNodeClick}
          onPaneClick={onPaneClick}
          nodeTypes={nodeTypes}
          fitView
          className="bg-gray-50"
          onInit={setReactFlowInstance}
        >
          <Controls showFitView={false} showInteractive={false} />
          <Background color="#e5e7eb" gap={16} />
          
          {/* Empty State */}
          {reactNodes.length === 0 && (
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              <div className="text-center">
                <div className="w-16 h-16 mx-auto mb-4 bg-green-100 rounded-full flex items-center justify-center">
                  <Plus className="w-8 h-8 text-green-600" />
                </div>
                <p className="text-gray-500 font-medium">Drag & drop to get started</p>
              </div>
            </div>
          )}
        </ReactFlow>
      </div>
      
      {/* Bottom Controls */}
      <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 z-10">
        <ControlButtons
          onZoomIn={() => zoomIn()}
          onZoomOut={() => zoomOut()}
          onFitView={() => fitView()}
          zoomLevel={getZoom()}
        />
      </div>
      
      {/* Action Buttons */}
      {reactNodes.length > 0 && (
        <div className="absolute bottom-4 right-4 flex items-center space-x-2 z-10">
          <button
            onClick={onSave}
            className="bg-green-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-green-700 transition-colors"
          >
            Build Stack
          </button>
          <button
            onClick={onOpenChat}
            className="w-10 h-10 bg-green-600 text-white rounded-full flex items-center justify-center hover:bg-green-700 transition-colors"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
            </svg>
          </button>
        </div>
      )}
    </div>
  );
};

// Wrapper component with ReactFlowProvider
export const WorkflowCanvasWrapper: React.FC<WorkflowCanvasProps> = (props) => {
  return (
    <ReactFlowProvider>
      <WorkflowCanvas {...props} />
    </ReactFlowProvider>
  );
};
