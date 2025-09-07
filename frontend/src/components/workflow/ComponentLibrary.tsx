import React from 'react';

const components = [
  {
    type: 'userQuery',
    name: 'User Query',
    icon: '💬',
    description: 'Input'
  },
  {
    type: 'llm',
    name: 'LLM (OpenAI)',
    icon: '🤖',
    description: 'LLM (OpenAI)'
  },
  {
    type: 'knowledgeBase',
    name: 'Knowledge Base',
    icon: '📚',
    description: 'Knowledge Base'
  },
  {
    type: 'output',
    name: 'Output',
    icon: '📤',
    description: 'Output'
  }
];

export const ComponentLibrary: React.FC = () => {
  const onDragStart = (event: React.DragEvent, nodeType: string) => {
    event.dataTransfer.setData('application/reactflow', nodeType);
    event.dataTransfer.effectAllowed = 'move';
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
            className="flex items-center space-x-3 p-2 rounded-lg border border-gray-200 cursor-grab hover:border-gray-300 hover:bg-gray-50 transition-colors"
            draggable
            onDragStart={(event) => onDragStart(event, component.type)}
          >
            <span className="text-lg">{component.icon}</span>
            <span className="text-sm font-medium text-gray-900">{component.description}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
