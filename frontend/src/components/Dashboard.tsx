import React, { useEffect, useState } from 'react';
import { workflowAPI } from '../services/api';
import CreateStackModal from './CreateStackModal';

interface Workflow {
  id: string;
  name: string;
  description: string;
}

const Dashboard: React.FC<{ onEditStack: (id: string) => void }> = ({ onEditStack }) => {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const fetchWorkflows = async () => {
    setLoading(true);
    try {
      const resp = await workflowAPI.getWorkflows();
      setWorkflows(resp.data);
    } catch (error) {
      console.error('Failed to fetch workflows', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWorkflows();
  }, []);

  const handleCreated = () => {
    setModalOpen(false);
    fetchWorkflows();
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-semibold">My Stacks</h1>
        <button
          className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition"
          onClick={() => setModalOpen(true)}
        >
          + New Stack
        </button>
      </div>

      {loading ? (
        <p>Loading stacks...</p>
      ) : workflows.length === 0 ? (
        <p>No stacks found. Create some!</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
          {workflows.map((wf) => (
            <div
              key={wf.id}
              className="border border-gray-300 rounded p-4 flex flex-col justify-between"
            >
              <div>
                <h2 className="text-xl font-semibold">{wf.name}</h2>
                <p className="text-gray-600">{wf.description}</p>
              </div>
              <button
                onClick={() => onEditStack(wf.id)}
                className="mt-4 text-green-700 hover:underline"
              >
                Edit Stack
              </button>
            </div>
          ))}
        </div>
      )}

      {modalOpen && <CreateStackModal onClose={() => setModalOpen(false)} onCreated={handleCreated} />}
    </div>
  );
};

export default Dashboard;
