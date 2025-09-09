import React, { useState } from 'react';
import { workflowAPI } from '../services/api';

interface CreateStackModalProps {
  onClose: () => void;
  onCreated: () => void;
}

const CreateStackModal: React.FC<CreateStackModalProps> = ({ onClose, onCreated }) => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [saving, setSaving] = useState(false);

  const handleCreate = async () => {
    if (!name.trim()) return alert('Name is required');
    setSaving(true);
    try {
      await workflowAPI.createWorkflow({ name, description, nodes: [], edges: [] });
      onCreated();
    } catch (error) {
      alert('Failed to create stack. Check console.');
      console.error(error);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-lg p-6 w-full max-w-md">
        <h2 className="text-xl font-semibold mb-4">Create New Stack</h2>
        <label className="block mb-2">
          <span className="text-gray-700">Name</span>
          <input
            type="text"
            className="mt-1 block w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
            value={name}
            onChange={(e) => setName(e.target.value)}
            disabled={saving}
          />
        </label>
        <label className="block mb-4">
          <span className="text-gray-700">Description</span>
          <textarea
            className="mt-1 block w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            disabled={saving}
            rows={4}
          />
        </label>
        <div className="flex justify-end space-x-2">
          <button
            className="text-gray-600 px-4 py-2 rounded hover:bg-gray-100"
            onClick={onClose}
            disabled={saving}
          >
            Cancel
          </button>
          <button
            className={`bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition disabled:opacity-50`}
            onClick={handleCreate}
            disabled={saving || !name.trim()}
          >
            {saving ? 'Creating...' : 'Create'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default CreateStackModal;
