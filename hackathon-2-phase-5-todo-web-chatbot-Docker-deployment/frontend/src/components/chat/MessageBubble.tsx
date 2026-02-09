// Message Bubble Component for Phase III Chatbot
// Task ID: T029
// Reference: specs/features/chatbot/plan.md (UI Requirements)
// Reference: specs/features/chatbot/plan.md (Markdown rendering for task responses)

'use client';

import React from 'react';
import { Message } from '../../hooks/useChat';
import { TaskResponse } from '../../lib/api';

interface MessageBubbleProps {
  message: Message;
  showTasks?: boolean;
}

function formatDate(date: Date): string {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function TaskNotification({ tasks }: { tasks: TaskResponse[] }) {
  if (!tasks || tasks.length === 0) return null;

  // Simple notification - actual tasks are displayed in the dashboard
  return (
    <div className="mt-2 flex items-center gap-1.5 text-xs text-emerald-400">
      <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
      <span>{tasks.length} task{tasks.length > 1 ? 's' : ''} updated in dashboard</span>
    </div>
  );
}

function ErrorMessage({ message }: { message: string }) {
  return (
    <div className="p-3 bg-red-900/30 border border-red-700 rounded-lg">
      <p className="text-sm text-red-400 font-medium">Error</p>
      <p className="text-sm text-red-300 mt-1">{message}</p>
      <button className="text-sm text-red-400 hover:text-red-300 mt-2 underline">
        Try again
      </button>
    </div>
  );
}

export function MessageBubble({ message, showTasks = true }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  const isAssistant = message.role === 'assistant';
  const isSystem = message.role === 'system';

  return (
    <div
      className={`flex ${
        isUser ? 'justify-end' : 'justify-start'
      } animate-fade-in`}
    >
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-blue-600 text-white rounded-br-sm'
            : isAssistant
            ? 'bg-gray-800 border border-gray-700 text-slate-100 rounded-bl-sm'
            : 'bg-gray-700 text-gray-300 text-sm italic rounded-bl-sm'
        }`}
      >
        {/* Message content */}
        {message.error ? (
          <ErrorMessage message={message.error} />
        ) : (
          <>
            <p className={`whitespace-pre-wrap ${isSystem ? 'text-sm' : ''} ${isAssistant ? 'text-slate-100' : ''}`}>
              {message.content}
            </p>

            {/* Task notification for assistant messages - actual tasks shown in dashboard */}
            {isAssistant && showTasks && message.tasks && message.tasks.length > 0 && (
              <TaskNotification tasks={message.tasks} />
            )}
          </>
        )}

        {/* Timestamp */}
        <p
          className={`text-xs mt-1 ${
            isUser ? 'text-blue-200' : 'text-gray-400'
          }`}
        >
          {formatDate(message.timestamp)}
        </p>
      </div>
    </div>
  );
}
