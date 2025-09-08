import { useState, useCallback, useEffect } from 'react';
import { useMutation, useQuery } from 'react-query';
import { chatAPI } from '../services/api';
import { ChatMessage, ChatSession } from '../types/nodes';
import { wsService } from '../services/websocket';
import toast from 'react-hot-toast';

export const useChat = (workflowId?: string) => {
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isTyping, setIsTyping] = useState(false);

  // Fetch chat sessions
  const { data: sessions } = useQuery(
    'chat-sessions',
    () => chatAPI.getSessions().then(res => res.data),
    {
      onError: () => toast.error('Failed to load chat sessions'),
    }
  );

  // Create session mutation
  const createSessionMutation = useMutation(
    (workflowId?: string) => chatAPI.createSession(workflowId),
    {
      onSuccess: (response) => {
        setCurrentSession(response.data);
        setMessages([]);
      },
      onError: () => toast.error('Failed to create chat session'),
    }
  );

  // Send message mutation
  const sendMessageMutation = useMutation(
    ({ message, workflowId, sessionId }: { 
      message: string; 
      workflowId?: string; 
      sessionId?: string;
    }) => chatAPI.sendMessage(message, workflowId, sessionId),
    {
      onSuccess: (response) => {
        const assistantMessage: ChatMessage = {
          id: Date.now().toString(),
          type: 'assistant',
          content: response.data.response,
          timestamp: new Date(),
          metadata: {
            executionTime: response.data.execution_time,
            tokensUsed: response.data.tokens_used,
            model: response.data.model_used,
          },
        };
        setMessages(prev => [...prev, assistantMessage]);
        setIsTyping(false);
      },
      onError: (error) => {
        setIsTyping(false);
        toast.error('Failed to send message');
        console.error('Chat error:', error);
      },
    }
  );

  const sendMessage = useCallback((content: string) => {
    if (!content.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: content.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);

    sendMessageMutation.mutate({
      message: content,
      workflowId,
      sessionId: currentSession?.id,
    });
  }, [workflowId, currentSession?.id, sendMessageMutation]);

  const startNewSession = useCallback(() => {
    createSessionMutation.mutate(workflowId);
  }, [workflowId, createSessionMutation]);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  // Initialize session on mount
  useEffect(() => {
    if (workflowId && !currentSession) {
      startNewSession();
    }
  }, [workflowId, currentSession, startNewSession]);

  // WebSocket connection for real-time updates
  useEffect(() => {
    if (currentSession?.id) {
      wsService.connect(currentSession.id).then(() => {
        wsService.onMessage((data) => {
          if (data.type === 'message') {
            const message: ChatMessage = {
              id: data.id || Date.now().toString(),
              type: data.sender === 'assistant' ? 'assistant' : 'user',
              content: data.content,
              timestamp: new Date(data.timestamp),
              metadata: data.metadata,
            };
            setMessages(prev => [...prev, message]);
          }
        });
      }).catch(console.error);

      return () => {
        wsService.disconnect();
      };
    }
  }, [currentSession?.id]);

  return {
    // Data
    sessions,
    currentSession,
    messages,
    isTyping,
    
    // Loading states
    isLoading: sendMessageMutation.isLoading,
    isCreatingSession: createSessionMutation.isLoading,
    
    // Actions
    sendMessage,
    startNewSession,
    clearMessages,
    setCurrentSession,
  };
};
