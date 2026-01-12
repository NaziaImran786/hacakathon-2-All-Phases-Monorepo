// Empty State Component for FlowTask Dashboard
// 'No tasks found' illustration with create button

'use client';

import { FileQuestion, Plus } from 'lucide-react';

interface EmptyStateProps {
  onCreateTask: () => void;
}

export function EmptyState({ onCreateTask }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-8">
      {/* Illustration */}
      <div className="relative mb-6">
        <div className="w-32 h-32 rounded-full bg-gradient-to-br from-violet-500/20 to-purple-500/20 flex items-center justify-center">
          <FileQuestion className="w-16 h-16 text-violet-400" />
        </div>
        {/* Decorative rings */}
        <div className="absolute inset-0 rounded-full border-2 border-dashed border-slate-700 animate-spin-slow" style={{ animationDuration: '20s' }} />
      </div>

      {/* Text */}
      <h3 className="text-xl font-semibold text-white mb-2">No tasks found</h3>
      <p className="text-slate-400 text-center mb-6 max-w-sm">
        You don't have any tasks yet. Create your first task to get started with FlowTask.
      </p>

      {/* Create Button */}
      <button
        onClick={onCreateTask}
        className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-700 hover:to-purple-700 text-white rounded-xl font-medium transition-all shadow-lg shadow-violet-500/25"
      >
        <Plus className="w-5 h-5" />
        Create New Task
      </button>
    </div>
  );
}
