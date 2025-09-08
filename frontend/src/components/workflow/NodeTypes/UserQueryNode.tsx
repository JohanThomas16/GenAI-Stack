import React from 'react';
import { Handle, Position } from '@xyflow/react';
import { UserQueryNodeData } from '../../../types/nodes';

interface UserQueryNodeProps {
  data: UserQueryNodeData;
  selected?: boolean;
}

export const UserQueryNode: React.FC<UserQueryNodeProps> = ({ data, selected }) => {
  return (
    <div className={`px-4 py-3 shadow-lg rounded-lg bg-white border-2 min-w-[180px] ${
      selected ? 'border-blue-500' : 'border-gray-200'
    }`}>
      <div className="flex items-center space-x-2">
        <span className="text-xl">💬</span>
        <div className="flex-1">
          <div className="font-medium text-gray-900 text-sm">{data.label}</div>
          <div className="text-xs text-gray-500 mt-1">Entry point for queries</div>
        </div>
      </div>
      
      <div className="mt-2 text-xs text-gray-600">
        {data.placeholder}
      </div>

      <Handle
        type="source"
        position={Position.Right}
        className="w-3 h-3 !bg-blue-500 border-2 border-white"
      />
    </div>
  );
};
