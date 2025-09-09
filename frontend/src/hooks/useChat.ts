import { useState } from 'react';
import { useMutation, UseMutationResult } from 'react-query';
import toast from 'react-hot-toast';
import { chatAPI } from '../services/api';
import { ChatSession, ChatMessage } from '../types/nodes';

export const useChat = (workflowId?: string) => {
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isTyping, setIsTyping] = useState(false);


  const createSessionMutation: UseMutationResult<

    ChatSession,
 
    unknown,
 
    void
  > = useMutation(
    () => chatAPI.createSession(workflowId).then(res => res.data),
    {
      onSuccess: session => {
        setCurrentSession(session);
        setMessages([]);
      },
      onError: () => {
        toast.error('Failed to create chat session');
      },
    }
  );

  const sendMessageMutation: UseMutationResult<
    ChatMessage,
    unknown,
    { message: string; sessionId?: string }
  > = useMutation(
    ({ message, sessionId }) =>
      chatAPI
        .sendMessage(message, workflowId, sessionId || currentSession?.id)
        .then(res => res.data),
    {
      onMutate: () => {
        setIsTyping(true);
      },
      onSuccess: msg => {
        setIsTyping(false);
        setMessages(prev => [...prev, msg]);
      },
      onError: () => {
        setIsTyping(false);
        toast.error('Failed to send message');
      },
    }
  );

  const sendMessage = (message: string) => {
    if (!message.trim()) return;

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      content: message,
      role: 'user',
      timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMsg]);
    sendMessageMutation.mutate({ message, sessionId: currentSession?.id });
  };

  return {
    currentSession,
    messages,
    isTyping,
    isLoading: createSessionMutation.isLoading || sendMessageMutation.isLoading,
    createSession: () => createSessionMutation.mutate(),
    sendMessage,
  };
};