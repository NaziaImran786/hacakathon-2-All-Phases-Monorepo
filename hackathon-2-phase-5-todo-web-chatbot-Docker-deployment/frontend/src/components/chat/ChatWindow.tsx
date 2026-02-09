// Chat Window Component for Phase III Chatbot
// Task ID: T027
// Reference: specs/features/chatbot/plan.md (UI Requirements)

'use client';

import React, { useRef, useEffect } from 'react';
import { useChatKit } from './ChatKitProvider';
import { MessageBubble } from './MessageBubble';
import { ChatInput } from './ChatInput';
import { TypingIndicator } from './typing/TypingIndicator';

interface ChatWindowProps {
  className?: string;
  showTasks?: boolean;
}

export function ChatWindow({ className = '', showTasks = true }: ChatWindowProps) {
  const { messages, isLoading, sendMessage, clearConversation } = useChatKit();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messagesEndRef.current && scrollContainerRef.current) {
      const container = scrollContainerRef.current;
      container.scrollTop = container.scrollHeight;
    }
  }, [messages, isLoading]);

  const handleSend = async (content: string) => {
    await sendMessage(content);
  };

  const handleClear = () => {
    if (confirm('Clear conversation history?')) {
      clearConversation();
    }
  };

  return (
    <div className={`flex flex-col h-full max-w-4xl mx-auto ${className}`}>
      {/* Header - Dark theme matching Phase II */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-700 bg-gray-900">
        <h1 className="text-lg font-semibold text-slate-100">AI Chatbot</h1>
        <button
          onClick={handleClear}
          className="text-sm text-gray-400 hover:text-slate-100 transition-colors"
        >
          Clear Chat
        </button>
      </div>

      {/* Messages Container - Dark theme */}
      <div
        ref={scrollContainerRef}
        className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-900"
      >
        {/* Welcome message if empty */}
        {messages.length === 0 && (
          <div className="text-center text-gray-400 py-8">
            <p className="text-lg mb-2 text-slate-100">Welcome to AI Chatbot!</p>
            <p className="text-sm text-gray-400">
              Try saying things like:
            </p>
            <ul className="text-sm mt-2 space-y-1 text-gray-300">
              <li>"Add a task to buy groceries"</li>
              <li>"What's pending?"</li>
              <li>"Complete task 1"</li>
            </ul>
          </div>
        )}

        {/* Messages */}
        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            message={message}
            showTasks={showTasks}
          />
        ))}

        {/* Typing Indicator */}
        {isLoading && <TypingIndicator />}

        {/* Scroll anchor */}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area - Dark theme */}
      <div className="border-t border-gray-700 bg-gray-900 p-4">
        <ChatInput onSend={handleSend} disabled={isLoading} />
      </div>
    </div>
  );
}
