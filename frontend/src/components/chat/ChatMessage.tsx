import React from 'react';
import { Bot, User } from 'lucide-react';
import { ChatMessage as ChatMessageType } from '../../types/nodes';

interface ChatMessageProps {
  message: ChatMessageType;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.type === 'user';
  
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[70%] rounded-lg px-4 py-2 ${
          isUser
            ? 'bg-blue-600 text-white'
            : 'bg-gray-100 text-gray-900'
        }`}
      >
        {!isUser && (
          <div className="flex items-center mb-2">
            <div className="w-6 h-6 bg-green-600 rounded-full flex items-center justify-center mr-2">
              <Bot className="w-3 h-3 text-white" />
            </div>
            <span className="text-xs text-gray-500">GenAI Assistant</span>
          </div>
        )}
        
        <div className="text-sm whitespace-pre-wrap">{message.content}</div>
        
        {message.metadata && (
          <div className="mt-2 text-xs opacity-70">
            {message.metadata.executionTime && (
              <span>⚡ {message.metadata.executionTime}ms</span>
            )}
            {message.metadata.tokensUsed && (
              <span className="ml-2">🎯 {message.metadata.tokensUsed} tokens</span>
            )}
          </div>
        )}
        
        <div className="text-xs opacity-60 mt-1">
          {message.timestamp.toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
};
