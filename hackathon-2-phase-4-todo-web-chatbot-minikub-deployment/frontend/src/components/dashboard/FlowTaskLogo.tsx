// FlowTask Logo Component
// Deep Navy theme with green checkmark

'use client';

import { CheckCircle2 } from 'lucide-react';

export function FlowTaskLogo() {
  return (
    <div className="flex items-center gap-2">
      <div className="relative">
        <CheckCircle2 className="w-8 h-8 text-emerald-500" strokeWidth={2.5} />
      </div>
      <span className="text-xl font-bold text-white tracking-tight">
        Flow<span className="text-emerald-500">Task</span>
      </span>
    </div>
  );
}
