import React, { useState, useEffect } from 'react';
import { X, Upload, Trash2 } from 'lucide-react';
import { WorkflowNode } from '../../types/workflow';
import { LLMNodeData, KnowledgeBaseNodeData, OutputNodeData, UserQueryNodeData } from '../../types/nodes';

interface ConfigurationPanelProps {
  node: WorkflowNode | null;
  onClose: () => void;
  onUpdate: (nodeId: string, updates: Partial<WorkflowNode>) => void;
}

export const ConfigurationPanel: React.FC<ConfigurationPanelProps> = ({
  node,
  onClose,
  onUpdate,
}) => {
  const [nodeData, setNodeData] = useState<any>(node?.data || {});

  useEffect(() => {
    if (node) {
      setNodeData(node.data);
    }
  }, [node]);

  if (!node) return null;

  const handleUpdate = (key: string, value: any) => {
    const updatedData = {
      ...nodeData,
      [key]: value,
    };
    setNodeData(updatedData);
    
    onUpdate(node.id, {
      data: updatedData,
    });
  };

  const renderConfiguration = () => {
    switch (node.type) {
      case 'userQuery':
        return (
          <UserQueryConfig
            data={nodeData as UserQueryNodeData}
            onUpdate={handleUpdate}
          />
        );
      case 'llm':
        return (
          <LLMConfig
            data={nodeData as LLMNodeData}
            onUpdate={handleUpdate}
          />
        );
      case 'knowledgeBase':
        return (
          <KnowledgeBaseConfig
            data={nodeData as KnowledgeBaseNodeData}
            onUpdate={handleUpdate}
          />
        );
      case 'output':
        return (
          <OutputConfig
            data={nodeData as OutputNodeData}
            onUpdate={handleUpdate}
          />
        );
      default:
        return (
          <div className="text-sm text-gray-500">
            Configuration not available for this node type.
          </div>
        );
    }
  };

  return (
    <div className="w-80 bg-white border-l border-gray-200 flex flex-col">
      <div className="p-4 border-b border-gray-200 flex items-center justify-between">
        <h3 className="font-semibold text-gray-900">{node.data.label}</h3>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>
      
      <div className="flex-1 p-4 overflow-y-auto">
        {renderConfiguration()}
      </div>
    </div>
  );
};

// Individual configuration components
const UserQueryConfig: React.FC<{
  data: UserQueryNodeData;
  onUpdate: (key: string, value: any) => void;
}> = ({ data, onUpdate }) => {
  return (
    <div className="space-y-4">
      <div>
        <label className="form-label">Label</label>
        <input
          type="text"
          value={data.label}
          onChange={(e) => onUpdate('label', e.target.value)}
          className="form-input"
        />
      </div>
      
      <div>
        <label className="form-label">Placeholder</label>
        <input
          type="text"
          value={data.placeholder}
          onChange={(e) => onUpdate('placeholder', e.target.value)}
          className="form-input"
        />
      </div>
      
      <div>
        <label className="form-label">Description</label>
        <textarea
          value={data.description || ''}
          onChange={(e) => onUpdate('description', e.target.value)}
          rows={3}
          className="form-textarea"
          placeholder="Optional description..."
        />
      </div>
    </div>
  );
};

const LLMConfig: React.FC<{
  data: LLMNodeData;
  onUpdate: (key: string, value: any) => void;
}> = ({ data, onUpdate }) => {
  return (
    <div className="space-y-4">
      <div>
        <label className="form-label">Model</label>
        <select
          value={data.model}
          onChange={(e) => onUpdate('model', e.target.value)}
          className="form-select"
        >
          <option value="gpt-3.5-turbo">GPT 3.5 Turbo</option>
          <option value="gpt-4">GPT 4</option>
          <option value="gpt-4-turbo">GPT 4 Turbo</option>
          <option value="gpt-4o-mini">GPT 4o - Mini</option>
        </select>
      </div>
      
      <div>
        <label className="form-label">API Key</label>
        <input
          type="password"
          value={data.apiKey || ''}
          onChange={(e) => onUpdate('apiKey', e.target.value)}
          placeholder="sk-..."
          className="form-input"
        />
      </div>
      
      <div>
        <label className="form-label">System Prompt</label>
        <textarea
          value={data.prompt}
          onChange={(e) => onUpdate('prompt', e.target.value)}
          rows={4}
          className="form-textarea"
          placeholder="You are a helpful assistant..."
        />
      </div>
      
      <div>
        <label className="form-label">Temperature: {data.temperature}</label>
        <input
          type="range"
          min="0"
          max="2"
          step="0.1"
          value={data.temperature}
          onChange={(e) => onUpdate('temperature', parseFloat(e.target.value))}
          className="w-full"
        />
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>Focused</span>
          <span>Balanced</span>
          <span>Creative</span>
        </div>
      </div>
      
      <div>
        <label className="form-label">Max Tokens</label>
        <input
          type="number"
          value={data.maxTokens || ''}
          onChange={(e) => onUpdate('maxTokens', e.target.value ? parseInt(e.target.value) : null)}
          placeholder="Leave empty for default"
          className="form-input"
        />
      </div>
    </div>
  );
};

const KnowledgeBaseConfig: React.FC<{
  data: KnowledgeBaseNodeData;
  onUpdate: (key: string, value: any) => void;
}> = ({ data, onUpdate }) => {
  return (
    <div className="space-y-4">
      <div>
        <label className="form-label">File for Knowledge Base</label>
        {data.fileName ? (
          <div className="flex items-center justify-between p-3 bg-gray-50 border border-gray-200 rounded-lg">
            <span className="text-sm text-gray-700">{data.fileName}</span>
            <button
              onClick={() => {
                onUpdate('fileName', '');
                onUpdate('fileId', '');
              }}
              className="text-red-500 hover:text-red-700"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
            <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
            <p className="text-sm text-gray-600">Click to upload or drag and drop</p>
            <p className="text-xs text-gray-500">PDF, TXT, DOCX files supported</p>
          </div>
        )}
      </div>
      
      <div>
        <label className="form-label">Embedding Model</label>
        <select
          value={data.embeddingModel}
          onChange={(e) => onUpdate('embeddingModel', e.target.value)}
          className="form-select"
        >
          <option value="text-embedding-3-large">text-embedding-3-large</option>
          <option value="text-embedding-3-small">text-embedding-3-small</option>
          <option value="text-embedding-ada-002">text-embedding-ada-002</option>
        </select>
      </div>
      
      <div>
        <label className="form-label">Chunk Size</label>
        <input
          type="number"
          value={data.chunkSize}
          onChange={(e) => onUpdate('chunkSize', parseInt(e.target.value))}
          className="form-input"
        />
      </div>
      
      <div>
        <label className="form-label">Similarity Threshold</label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.1"
          value={data.similarityThreshold}
          onChange={(e) => onUpdate('similarityThreshold', parseFloat(e.target.value))}
          className="w-full"
        />
        <div className="text-center text-sm text-gray-500 mt-1">
          {data.similarityThreshold}
        </div>
      </div>
      
      <div>
        <label className="form-label">Max Results</label>
        <input
          type="number"
          value={data.maxResults}
          onChange={(e) => onUpdate('maxResults', parseInt(e.target.value))}
          min="1"
          max="20"
          className="form-input"
        />
      </div>
    </div>
  );
};

const OutputConfig: React.FC<{
  data: OutputNodeData;
  onUpdate: (key: string, value: any) => void;
}> = ({ data, onUpdate }) => {
  return (
    <div className="space-y-4">
      <div>
        <label className="form-label">Output Format</label>
        <select
          value={data.format}
          onChange={(e) => onUpdate('format', e.target.value)}
          className="form-select"
        >
          <option value="text">Text</option>
          <option value="json">JSON</option>
          <option value="markdown">Markdown</option>
        </select>
      </div>
      
      <div>
        <label className="form-label">Output Template</label>
        <textarea
          value={data.template || ''}
          onChange={(e) => onUpdate('template', e.target.value)}
          rows={3}
          className="form-textarea"
          placeholder="Optional template for formatting output..."
        />
      </div>
      
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <label className="text-sm font-medium text-gray-700">Include Sources</label>
          <div className="relative inline-block w-10 mr-2 align-middle select-none">
            <input
              type="checkbox"
              checked={data.includeSources}
              onChange={(e) => onUpdate('includeSources', e.target.checked)}
              className="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer"
            />
            <label className="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 cursor-pointer"></label>
          </div>
        </div>
        
        <div className="flex items-center justify-between">
          <label className="text-sm font-medium text-gray-700">Include Metadata</label>
          <div className="relative inline-block w-10 mr-2 align-middle select-none">
            <input
              type="checkbox"
              checked={data.includeMetadata}
              onChange={(e) => onUpdate('includeMetadata', e.target.checked)}
              className="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer"
            />
            <label className="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 cursor-pointer"></label>
          </div>
        </div>
      </div>
    </div>
  );
};
