// Chat Hook for Phase III Chatbot
// Task ID: T022 (Frontend foundation)
// Reference: specs/features/chatbot/plan.md (UI Requirements)

import { useState, useCallback, useRef, useEffect } from 'react';
import { apiClient, ChatResponse, TaskResponse } from '../lib/api';

export interface Message {
  id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  tasks?: TaskResponse[];
  timestamp: Date;
  error?: string;
}

interface UseChatOptions {
  initialConversationId?: number;
  onError?: (error: string) => void;
}

interface UseChatReturn {
  messages: Message[];
  isLoading: boolean;
  sendMessage: (content: string) => Promise<void>;
  clearMessages: () => void;
  conversationId: number | null;
}

export function useChat(options: UseChatOptions = {}): UseChatReturn {
  const { initialConversationId, onError } = options;
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<number | null>(
    initialConversationId || null
  );
  const messagesRef = useRef<Message[]>([]);

  // Keep ref in sync with state
  useEffect(() => {
    messagesRef.current = messages;
  }, [messages]);

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim() || isLoading) return;

    // Add user message immediately
    const userMessage: Message = {
      id: Date.now(),
      role: 'user',
      content: content.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Send to backend
      const response = await apiClient.sendMessage({
        message: content.trim(),
        conversation_id: conversationId || undefined,
      });

      // Update conversation ID if this is the first message
      if (conversationId === null) {
        setConversationId(response.conversation_id);
      }

      // Add assistant response
      const assistantMessage: Message = {
        id: response.message_id,
        role: 'assistant',
        content: response.response.content,
        tasks: response.response.tasks,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // Dispatch taskUpdated event if tasks were created/modified
      // This triggers refresh in the dashboard task list
      if (response.response.tasks && response.response.tasks.length > 0) {
        window.dispatchEvent(new CustomEvent('taskUpdated'));
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to send message';

      // Add error message
      const errorMsg: Message = {
        id: Date.now(),
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        error: errorMessage,
      };

      setMessages((prev) => [...prev, errorMsg]);

      // Call error callback if provided
      if (onError) {
        onError(errorMessage);
      }
    } finally {
      setIsLoading(false);
    }
  }, [conversationId, isLoading, onError]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setConversationId(null);
  }, []);

  return {
    messages,
    isLoading,
    sendMessage,
    clearMessages,
    conversationId,
  };
}
