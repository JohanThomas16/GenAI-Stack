import React, { useState, useRef, useEffect } from 'react';
import { X, Send, Bot } from 'lucide-react';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { useChat } from '../../hooks/useChat';
import { ChatMessage as ChatMessageType } from '../../types/nodes';

interface ChatInterfaceProps {
  isOpen: boolean;
  onClose: () => void;
  workflowId?: string;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  isOpen,
  onClose,
  workflowId,
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { messages, isTyping, sendMessage, isLoading } = useChat(workflowId);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isTyping]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl w-[800px] h-[600px] flex flex-col shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-green-600 rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-bold">G</span>
            </div>
            <h3 className="font-semibold text-gray-900">GenAI Stack Chat</h3>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 p-6 overflow-y-auto">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-12 h-12 bg-green-600 rounded-full flex items-center justify-center mb-4">
                <span className="text-white text-lg font-bold">G</span>
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">GenAI Stack Chat</h4>
              <p className="text-gray-500">Start a conversation to test your stack</p>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
              
              {isTyping && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 rounded-lg px-4 py-2 max-w-[70%]">
                    <div className="flex items-center space-x-2">
                      <div className="w-6 h-6 bg-green-600 rounded-full flex items-center justify-center">
                        <Bot className="w-3 h-3 text-white" />
                      </div>
                      <span className="text-sm text-gray-600">Thinking...</span>
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input */}
        <ChatInput 
          onSendMessage={sendMessage}
          disabled={isLoading}
          placeholder="Send a message"
        />
      </div>
    </div>
  );
};
