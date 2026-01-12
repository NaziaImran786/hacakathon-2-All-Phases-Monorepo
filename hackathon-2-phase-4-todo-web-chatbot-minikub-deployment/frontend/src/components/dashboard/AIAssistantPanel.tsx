// AI Task Assistant Panel for FlowTask Dashboard
// Sleek dark container with bubble-style messages

'use client';

import { useState, useRef, useEffect } from 'react';
import { Bot, Send, Sparkles, User } from 'lucide-react';
import { apiClient, ChatResponse, TaskResponse } from '../../lib/api';

interface Message {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  tasks?: TaskResponse[];
  timestamp: Date;
}

interface AIAssistantPanelProps {
  onTaskCreated?: () => void;
}

export function AIAssistantPanel({ onTaskCreated }: AIAssistantPanelProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 0,
      role: 'assistant',
      content: "Hi! I'm your AI Task Assistant. I can help you manage your tasks. Try saying things like:\n\n• \"Add a task to review project proposal\"\n• \"Show me my pending tasks\"\n• \"Mark task 1 as complete\"",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await apiClient.sendMessage({
        message: input.trim(),
        conversation_id: conversationId || undefined,
      });

      if (!conversationId) {
        setConversationId(response.conversation_id);
      }

      const assistantMessage: Message = {
        id: response.message_id,
        role: 'assistant',
        content: response.response.content,
        tasks: response.response.tasks,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // Notify parent if tasks were created and dispatch global event
      if (response.response.tasks?.length > 0) {
        if (onTaskCreated) {
          onTaskCreated();
        }
        // Dispatch custom event for cross-component synchronization
        window.dispatchEvent(new CustomEvent('taskUpdated'));
      }
    } catch (error) {
      const errorMessage: Message = {
        id: Date.now(),
        role: 'assistant',
        content: error instanceof Error ? error.message : 'Something went wrong. Please try again.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="w-96 bg-[#0f172a] border-l border-slate-800 flex flex-col h-full">
      {/* Header */}
      <div className="p-5 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-gradient-to-br from-violet-500/20 to-purple-500/20">
            <Sparkles className="w-5 h-5 text-violet-400" />
          </div>
          <div>
            <h2 className="text-lg font-semibold bg-gradient-to-r from-violet-400 to-purple-400 bg-clip-text text-transparent">
              AI Task Assistant
            </h2>
            <p className="text-xs text-slate-500">Powered by GPT-4</p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-3 ${
                message.role === 'user'
                  ? 'bg-gradient-to-r from-violet-600 to-purple-600 text-white rounded-br-md'
                  : 'bg-[#1e293b] text-slate-200 rounded-bl-md'
              }`}
            >
              {/* Role Icon */}
              <div className="flex items-start gap-2">
                {message.role === 'assistant' && (
                  <Bot className="w-4 h-4 text-violet-400 mt-0.5 flex-shrink-0" />
                )}
                <div className="flex-1 min-w-0">
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>

                  {/* Task Update Notification - Simple indicator, actual tasks shown in dashboard */}
                  {message.tasks && message.tasks.length > 0 && (
                    <div className="mt-2 flex items-center gap-1.5 text-xs text-emerald-400">
                      <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                      <span>{message.tasks.length} task{message.tasks.length > 1 ? 's' : ''} updated in dashboard</span>
                    </div>
                  )}
                </div>
                {message.role === 'user' && (
                  <User className="w-4 h-4 text-violet-200 mt-0.5 flex-shrink-0" />
                )}
              </div>

              {/* Timestamp */}
              <p className={`text-xs mt-2 ${message.role === 'user' ? 'text-violet-200' : 'text-slate-500'}`}>
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </p>
            </div>
          </div>
        ))}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-[#1e293b] rounded-2xl rounded-bl-md px-4 py-3">
              <div className="flex items-center gap-2">
                <Bot className="w-4 h-4 text-violet-400" />
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-slate-800">
        <div className="flex items-end gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask me anything about your tasks..."
            rows={1}
            className="flex-1 px-4 py-3 bg-[#1e293b] border border-slate-700 rounded-xl text-white placeholder-slate-400 resize-none focus:outline-none focus:ring-2 focus:ring-violet-500/50 focus:border-violet-500 transition-all min-h-[48px] max-h-[120px]"
            style={{ height: 'auto' }}
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || isLoading}
            className="p-3 bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-700 hover:to-purple-700 disabled:from-slate-600 disabled:to-slate-600 text-white rounded-xl transition-all disabled:cursor-not-allowed"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        <p className="text-xs text-slate-500 mt-2 text-center">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}
