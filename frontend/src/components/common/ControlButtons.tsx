import React from 'react';
import { ZoomIn, ZoomOut, Maximize2, RotateCcw } from 'lucide-react';

interface ControlButtonsProps {
  onZoomIn: () => void;
  onZoomOut: () => void;
  onFitView: () => void;
  onReset?: () => void;
  zoomLevel: number;
}

export const ControlButtons: React.FC<ControlButtonsProps> = ({
  onZoomIn,
  onZoomOut,
  onFitView,
  onReset,
  zoomLevel
}) => {
  return (
    <div className="flex items-center space-x-2 bg-white border border-gray-200 rounded-lg px-3 py-2 shadow-sm">
      <button
        onClick={onZoomIn}
        className="p-1 hover:bg-gray-100 rounded transition-colors"
        title="Zoom In"
      >
        <ZoomIn className="w-4 h-4 text-gray-600" />
      </button>
      
      <button
        onClick={onZoomOut}
        className="p-1 hover:bg-gray-100 rounded transition-colors"
        title="Zoom Out"
      >
        <ZoomOut className="w-4 h-4 text-gray-600" />
      </button>
      
      <button
        onClick={onFitView}
        className="p-1 hover:bg-gray-100 rounded transition-colors"
        title="Fit View"
      >
        <Maximize2 className="w-4 h-4 text-gray-600" />
      </button>
      
      {onReset && (
        <button
          onClick={onReset}
          className="p-1 hover:bg-gray-100 rounded transition-colors"
          title="Reset"
        >
          <RotateCcw className="w-4 h-4 text-gray-600" />
        </button>
      )}
      
      <span className="text-sm text-gray-600 px-2 border-l border-gray-200">
        {Math.round(zoomLevel * 100)}%
      </span>
    </div>
  );
};
