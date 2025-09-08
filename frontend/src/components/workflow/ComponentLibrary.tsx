import React from 'react';
import { NodeType } from '../../types/workflow';
import { getNodeDefaults, getNodeDisplayName } from '../../utils/nodeDefaults';

interface ComponentItem {
  type: NodeType;
  name: string;
  description: string;
  icon: string;
}

interface ComponentLibraryProps {
  onDragStart: (event: React.DragEvent, component: ComponentItem) => void;
}

const components: ComponentItem[] = [
  {
    type: 'userQuery',
    name: 'User Query',
    description: 'Input',
    icon: '💬'
  },
  {
    type: 'llm',
    name: 'LLM (OpenAI)',
    description: 'LLM (OpenAI)',
    icon: '🤖'
  },
  {
    type: 'knowledgeBase',
    name: 'Knowledge Base',
    description: 'Knowledge Base',
    icon: '📚'
  },
  {
    type: 'output',
    name: 'Output',
    description: 'Output',
    icon: '📤'
  }
];

export const ComponentLibrary: React.FC<ComponentLibraryProps> = ({ onDragStart }) => {
  const handleDragStart = (event: React.DragEvent, component: ComponentItem) => {
    event.dataTransfer.setData('application/json', JSON.stringify({
      type: component.type,
      name: component.name,
      icon: component.icon,
      data: getNodeDefaults(component.type)
    }));
    event.dataTransfer.effectAllowed = 'copy';
    onDragStart(event, component);
  };

  return (
    <div className="w-48 bg-white border-r border-gray-200 flex flex-col">
      <div className="p-3 border-b border-gray-200">
        <h3 className="font-medium text-gray-900 text-sm">Components</h3>
      </div>
      
      <div className="flex-1 p-3 space-y-1">
        {components.map((component) => (
          <div
            key={component.type}
            className="drag-item flex items-center space-x-3 p-2 rounded-lg border border-gray-200 cursor-grab hover:border-gray-300 hover:bg-gray-50 transition-all active:cursor-grabbing"
            draggable
            onDragStart={(event) => handleDragStart(event, component)}
          >
            <span className="text-lg">{component.icon}</span>
            <span className="text-sm font-medium text-gray-900">{component.description}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
