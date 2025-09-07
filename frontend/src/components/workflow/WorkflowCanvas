import React, { useCallback, useRef, useState } from 'react';
import {
  ReactFlow,
  ReactFlowProvider,
  addEdge,
  useNodesState,
  useEdgesState,
  Controls,
  Background,
  useReactFlow,
  Connection,
  Edge,
  Node,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import { UserQueryNode } from './NodeTypes/UserQueryNode';
import { KnowledgeBaseNode } from './NodeTypes/KnowledgeBaseNode';
import { LLMNode } from './NodeTypes/LLMNode';
import { OutputNode } from './NodeTypes/OutputNode';

const nodeTypes = {
  userQuery: UserQueryNode,
  knowledgeBase: KnowledgeBaseNode,
  llm: LLMNode,
  output: OutputNode,
};

interface WorkflowCanvasProps {
  onNodeSelect: (node: Node | null) => void;
  selectedNode: Node | null;
}

export const WorkflowCanvas: React.FC<WorkflowCanvasProps> = ({ 
  onNodeSelect, 
  selectedNode 
}) => {
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const { screenToFlowPosition } = useReactFlow();

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    []
  );

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();

      const type = event.dataTransfer.getData('application/reactflow');
      if (typeof type === 'undefined' || !type) {
        return;
      }

      const position = screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });

      const newNode: Node = {
        id: `${type}-${Date.now()}`,
        type,
        position,
        data: getDefaultNodeData(type),
      };

      setNodes((nds) => nds.concat(newNode));
    },
    [screenToFlowPosition]
  );

  const getDefaultNodeData = (type: string) => {
    switch (type) {
      case 'userQuery':
        return { 
          label: 'User Query',
          placeholder: 'Enter point for queries'
        };
      case 'knowledgeBase':
        return { 
          label: 'Knowledge Base',
          file: null,
          embeddingModel: 'text-embedding-3-large'
        };
      case 'llm':
        return { 
          label: 'LLM (OpenAI)',
          model: 'GPT 4o - Mini',
          apiKey: '',
          prompt: 'You are a helpful PDF assistant. Use web search if the PDF lacks context.',
          temperature: 0.75
        };
      case 'output':
        return { 
          label: 'Output',
          format: 'text'
        };
      default:
        return { label: type };
    }
  };

  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    onNodeSelect(node);
  }, [onNodeSelect]);

  return (
    <div className="flex-1 relative">
      <div className="absolute top-4 left-4 bg-blue-50 border border-blue-200 rounded-lg px-3 py-2 z-10">
        <h3 className="font-medium text-blue-900 text-sm">Chat With AI</h3>
      </div>
      
      <div className="reactflow-wrapper h-full" ref={reactFlowWrapper}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onDrop={onDrop}
          onDragOver={onDragOver}
          onNodeClick={onNodeClick}
          nodeTypes={nodeTypes}
          fitView
          className="bg-gray-50"
        >
          <Controls 
            className="bg-white border border-gray-200 rounded-lg shadow-sm"
            showFitView={false}
            showInteractive={false}
          />
          <Background color="#e5e7eb" gap={16} />
          
          {nodes.length === 0 && (
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              <div className="text-center">
                <div className="w-16 h-16 mx-auto mb-4 bg-green-100 rounded-full flex items-center justify-center">
                  <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                </div>
                <p className="text-gray-500 font-medium">Drag & drop to get started</p>
              </div>
            </div>
          )}
        </ReactFlow>
      </div>
      
      {/* Bottom Controls */}
      <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex items-center space-x-2 bg-white border border-gray-200 rounded-lg px-3 py-2 shadow-sm">
        <button className="p-1 hover:bg-gray-100 rounded">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
        </button>
        <button className="p-1 hover:bg-gray-100 rounded">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
          </svg>
        </button>
        <button className="p-1 hover:bg-gray-100 rounded">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
          </svg>
        </button>
        <span className="text-sm text-gray-600 px-2">100%</span>
      </div>
      
      {/* Build Stack Button */}
      {nodes.length > 0 && (
        <div className="absolute bottom-4 right-4 flex items-center space-x-2">
          <button className="bg-green-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-green-700 transition-colors">
            Build Stack
          </button>
          <button className="w-10 h-10 bg-green-600 text-white rounded-full flex items-center justify-center hover:bg-green-700 transition-colors">
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
            </svg>
          </button>
        </div>
      )}
    </div>
  );
};
