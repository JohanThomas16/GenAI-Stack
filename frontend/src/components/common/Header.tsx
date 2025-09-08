import React from 'react';

interface HeaderProps {
  onSave: () => void;
  onChat: () => void;
  saved: boolean;
  loading?: boolean;
}

export const Header: React.FC<HeaderProps> = ({ onSave, onChat, saved, loading }) => {
  return (
    <div className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
      <div className="flex items-center space-x-3">
        <div className="w-8 h-8 bg-green-600 rounded-full flex items-center justify-center">
          <span className="text-white text-sm font-bold">G</span>
        </div>
        <h1 className="text-xl font-semibold text-gray-900">GenAI Stack</h1>
      </div>
      
      <div className="flex items-center space-x-3">
        <button
          onClick={onSave}
          disabled={loading}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            saved 
              ? 'bg-green-100 text-green-700 border border-green-200' 
              : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
          } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          {loading && <div className="spinner mr-2"></div>}
          {saved ? '✓ Saved' : 'Save'}
        </button>
        
        <div className="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center cursor-pointer">
          <span className="text-white text-sm font-bold">U</span>
        </div>
      </div>
    </div>
  );
};
