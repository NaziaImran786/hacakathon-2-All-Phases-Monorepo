// Stats Cards Component for FlowTask Dashboard
// Purple-tinted borders with large white numbers

'use client';

import { ListTodo, Clock, CheckCircle } from 'lucide-react';

interface StatsCardsProps {
  total: number;
  active: number;
  completed: number;
}

export function StatsCards({ total, active, completed }: StatsCardsProps) {
  const cards = [
    {
      label: 'Total Tasks',
      value: total,
      icon: ListTodo,
      gradient: 'from-violet-500/20 to-purple-500/20',
      border: 'border-violet-500/30',
      iconColor: 'text-violet-400',
    },
    {
      label: 'Active',
      value: active,
      icon: Clock,
      gradient: 'from-blue-500/20 to-cyan-500/20',
      border: 'border-blue-500/30',
      iconColor: 'text-blue-400',
    },
    {
      label: 'Completed',
      value: completed,
      icon: CheckCircle,
      gradient: 'from-emerald-500/20 to-green-500/20',
      border: 'border-emerald-500/30',
      iconColor: 'text-emerald-400',
    },
  ];

  return (
    <div className="grid grid-cols-3 gap-4">
      {cards.map((card) => {
        const Icon = card.icon;
        return (
          <div
            key={card.label}
            className={`relative overflow-hidden rounded-2xl border ${card.border} bg-gradient-to-br ${card.gradient} backdrop-blur-sm p-6`}
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-slate-400 text-sm font-medium mb-1">{card.label}</p>
                <p className="text-4xl font-bold text-white">{card.value}</p>
              </div>
              <div className={`p-3 rounded-xl bg-slate-800/50 ${card.iconColor}`}>
                <Icon className="w-6 h-6" />
              </div>
            </div>
            {/* Decorative gradient blur */}
            <div className={`absolute -bottom-4 -right-4 w-24 h-24 rounded-full bg-gradient-to-br ${card.gradient} blur-2xl opacity-50`} />
          </div>
        );
      })}
    </div>
  );
}
