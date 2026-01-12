// ChatKit Provider for Phase III Chatbot
// Task ID: T026
// Reference: specs/features/chatbot/plan.md (Chatkit Provider Pattern)

'use client';

import React, { createContext, useContext, useCallback, useState, useEffect, ReactNode } from 'react';
import { apiClient, ChatResponse, TaskResponse } from '../../lib/api';
import { useChat, Message } from '../../hooks/useChat';

interface ChatKitConfig {
  apiUrl?: string;
  onError?: (error: string) => void;
  onMessage?: (message: Message) => void;
}

interface ChatKitContextValue {
  isConnected: boolean;
  sendMessage: (content: string) => Promise<void>;
  messages: Message[];
  isLoading: boolean;
  conversationId: number | null;
  clearConversation: () => void;
}

const ChatKitContext = createContext<ChatKitContextValue | null>(null);

export function useChatKit() {
  const context = useContext(ChatKitContext);
  if (!context) {
    throw new Error('useChatKit must be used within a ChatKitProvider');
  }
  return context;
}

interface ChatKitProviderProps {
  children: ReactNode;
  config?: ChatKitConfig;
  initialConversationId?: number;
}

export function ChatKitProvider({
  children,
  config,
  initialConversationId,
}: ChatKitProviderProps) {
  const [isConnected, setIsConnected] = useState(false);

  const {
    messages,
    isLoading,
    sendMessage,
    clearMessages,
    conversationId,
  } = useChat({
    initialConversationId,
    onError: config?.onError,
  });

  // Check connection on mount
  useEffect(() => {
    const checkConnection = async () => {
      try {
        await apiClient.healthCheck();
        setIsConnected(true);
      } catch {
        setIsConnected(false);
      }
    };

    checkConnection();
  }, []);

  // Callback for new messages
  const handleMessage = useCallback((message: Message) => {
    if (config?.onMessage) {
      config.onMessage(message);
    }
  }, [config]);

  const clearConversation = useCallback(() => {
    clearMessages();
  }, [clearMessages]);

  const value: ChatKitContextValue = {
    isConnected,
    sendMessage: async (content: string) => {
      await sendMessage(content);
    },
    messages,
    isLoading,
    conversationId,
    clearConversation,
  };

  return (
    <ChatKitContext.Provider value={value}>
      {children}
    </ChatKitContext.Provider>
  );
}

// Export types for consumers
export type { ChatKitConfig, ChatKitContextValue };
