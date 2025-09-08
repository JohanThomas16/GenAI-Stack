import React from 'react';

interface TabHeaderProps {
  title: string;
  isActive?: boolean;
  onClick?: () => void;
}

export const TabHeader: React.FC<TabHeaderProps> = ({ title, isActive = true, onClick }) => {
  return (
    <div 
      className={`inline-flex items-center px-3 py-2 rounded-lg border cursor-pointer transition-colors ${
        isActive 
          ? 'bg-blue-50 border-blue-200 text-blue-900' 
          : 'bg-gray-50 border-gray-200 text-gray-700 hover:bg-gray-100'
      }`}
      onClick={onClick}
    >
      <h3 className="font-medium text-sm">{title}</h3>
    </div>
  );
};
