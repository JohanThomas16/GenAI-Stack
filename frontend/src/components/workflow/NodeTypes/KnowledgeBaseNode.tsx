import React from 'react';
import { Handle, Position } from '@xyflow/react';
import { KnowledgeBaseNodeData } from '../../../types/nodes';

interface KnowledgeBaseNodeProps {
  data: KnowledgeBaseNodeData;
  selected?: boolean;
}

export const KnowledgeBaseNode: React.FC<KnowledgeBaseNodeProps> = ({ data, selected }) => {
  return (
    <div className={`px-4 py-3 shadow-lg rounded-lg bg-white border-2 min-w-[180px] ${
      selected ? 'border-blue-500' : 'border-gray-200'
    }`}>
      <div className="flex items-center space-x-2">
        <span className="text-xl">📚</span>
        <div className="flex-1">
          <div className="font-medium text-gray-900 text-sm">{data.label}</div>
          <div className="text-xs text-gray-500 mt-1">
            {data.fileName || 'No file uploaded'}
          </div>
        </div>
      </div>
      
      <div className="mt-2 text-xs text-gray-600">
        Model: {data.embeddingModel}
      </div>

      <Handle
        type="target"
        position={Position.Left}
        className="w-3 h-3 !bg-green-500 border-2 border-white"
      />
      
      <Handle
        type="source"
        position={Position.Right}
        className="w-3 h-3 !bg-green-500 border-2 border-white"
      />
    </div>
  );
};
