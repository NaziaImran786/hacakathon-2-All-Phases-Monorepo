// Task Card Component for FlowTask Dashboard
// Dark card style with status indicators

'use client';

import { MoreHorizontal, Calendar, Clock, Edit2, Trash2, CheckCircle } from 'lucide-react';
import { useState } from 'react';

interface Task {
  id: number;
  title: string;
  description?: string;
  completed: boolean;
  created_at?: string;
  due_date?: string;
  priority?: 'high' | 'medium' | 'low';
}

interface TaskCardProps {
  task: Task;
  onEdit: (task: Task) => void;
  onDelete: (taskId: number) => void;
  onToggleComplete: (task: Task) => void;
}

export function TaskCard({ task, onEdit, onDelete, onToggleComplete }: TaskCardProps) {
  const [showMenu, setShowMenu] = useState(false);

  const priorityColors = {
    high: 'bg-red-500/20 text-red-400 border-red-500/30',
    medium: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    low: 'bg-green-500/20 text-green-400 border-green-500/30',
  };

  const priority = task.priority || 'medium';

  return (
    <div className={`group relative bg-[#1e293b] border border-slate-700 rounded-2xl p-5 hover:border-slate-600 transition-all ${task.completed ? 'opacity-60' : ''}`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <button
            onClick={() => onToggleComplete(task)}
            className={`w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all ${
              task.completed
                ? 'bg-emerald-500 border-emerald-500'
                : 'border-slate-500 hover:border-violet-500'
            }`}
          >
            {task.completed && <CheckCircle className="w-4 h-4 text-white" />}
          </button>
          <span className={`px-2.5 py-1 text-xs font-medium rounded-lg border ${priorityColors[priority]}`}>
            {priority.charAt(0).toUpperCase() + priority.slice(1)}
          </span>
        </div>

        {/* Menu */}
        <div className="relative">
          <button
            onClick={() => setShowMenu(!showMenu)}
            className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-700 rounded-lg opacity-0 group-hover:opacity-100 transition-all"
          >
            <MoreHorizontal className="w-5 h-5" />
          </button>

          {showMenu && (
            <div className="absolute right-0 top-full mt-1 w-36 bg-[#0f172a] border border-slate-700 rounded-xl shadow-xl z-10 overflow-hidden">
              <button
                onClick={() => { onEdit(task); setShowMenu(false); }}
                className="w-full flex items-center gap-2 px-4 py-2.5 text-sm text-slate-300 hover:text-white hover:bg-slate-800 transition-all"
              >
                <Edit2 className="w-4 h-4" />
                Edit
              </button>
              <button
                onClick={() => { onDelete(task.id); setShowMenu(false); }}
                className="w-full flex items-center gap-2 px-4 py-2.5 text-sm text-red-400 hover:text-red-300 hover:bg-red-500/10 transition-all"
              >
                <Trash2 className="w-4 h-4" />
                Delete
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Content */}
      <h3 className={`text-lg font-semibold text-white mb-2 ${task.completed ? 'line-through' : ''}`}>
        {task.title}
      </h3>
      {task.description && (
        <p className="text-slate-400 text-sm mb-4 line-clamp-2">
          {task.description}
        </p>
      )}

      {/* Footer */}
      <div className="flex items-center gap-4 text-xs text-slate-500">
        {task.due_date && (
          <div className="flex items-center gap-1.5">
            <Calendar className="w-3.5 h-3.5" />
            <span>{new Date(task.due_date).toLocaleDateString()}</span>
          </div>
        )}
        {task.created_at && (
          <div className="flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5" />
            <span>Created {new Date(task.created_at).toLocaleDateString()}</span>
          </div>
        )}
      </div>
    </div>
  );
}
