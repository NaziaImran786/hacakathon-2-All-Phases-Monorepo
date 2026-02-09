// FlowTask Landing Page
// Deep Navy theme with gradient accents

'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { CheckCircle2, ArrowRight, Sparkles, Zap, Shield } from 'lucide-react';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      router.push('/tasks');
    }
  }, [router]);

  return (
    <div className="min-h-screen bg-[#0f172a] overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-0 left-1/4 w-[600px] h-[600px] bg-violet-600/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-[600px] h-[600px] bg-purple-600/10 rounded-full blur-3xl" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-blue-600/5 rounded-full blur-3xl" />
      </div>

      {/* Header */}
      <header className="relative z-10 flex items-center justify-between px-8 py-6 max-w-7xl mx-auto">
        <div className="flex items-center gap-2">
          <CheckCircle2 className="w-8 h-8 text-emerald-500" strokeWidth={2.5} />
          <span className="text-xl font-bold text-white tracking-tight">
            Flow<span className="text-emerald-500">Task</span>
          </span>
        </div>
        <div className="flex items-center gap-4">
          <Link
            href="/login"
            className="px-5 py-2.5 text-slate-300 hover:text-white font-medium transition-colors"
          >
            Sign In
          </Link>
          <Link
            href="/signup"
            className="px-5 py-2.5 bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-700 hover:to-purple-700 text-white rounded-xl font-medium transition-all shadow-lg shadow-violet-500/25"
          >
            Get Started
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <main className="relative z-10 max-w-7xl mx-auto px-8 pt-12 pb-32">
        <div className="text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-violet-500/10 border border-violet-500/20 rounded-full mb-8">
            <Sparkles className="w-4 h-4 text-violet-400" />
            <span className="text-sm text-violet-300 font-medium">AI-Powered Task Management</span>
          </div>

          {/* Headline */}
          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
            Manage Tasks with
            <br />
            <span className="bg-gradient-to-r from-violet-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              AI Intelligence
            </span>
          </h1>

          {/* Subheadline */}
          <p className="text-xl text-slate-400 max-w-2xl mx-auto mb-10">
            Create, organize, and complete tasks using natural language. Let AI handle the complexity while you focus on what matters.
          </p>

          {/* CTA Buttons */}
          <div className="flex items-center justify-center gap-4 mb-20">
            <Link
              href="/signup"
              className="flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-700 hover:to-purple-700 text-white rounded-xl font-semibold text-lg transition-all shadow-xl shadow-violet-500/25"
            >
              Start Free
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link
              href="/login"
              className="px-8 py-4 bg-white/5 hover:bg-white/10 border border-white/10 text-white rounded-xl font-semibold text-lg transition-all"
            >
              Sign In
            </Link>
          </div>

          {/* Feature Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto pt-8">
            {[
              {
                icon: Sparkles,
                title: 'AI-Powered',
                description: 'Create tasks using natural language. Just tell the AI what you need.',
                gradient: 'from-violet-500/20 to-purple-500/20',
                border: 'border-violet-500/30',
                iconColor: 'text-violet-400',
              },
              {
                icon: Zap,
                title: 'Lightning Fast',
                description: 'Instant task creation and updates. No forms, no clicks, just talk.',
                gradient: 'from-yellow-500/20 to-orange-500/20',
                border: 'border-yellow-500/30',
                iconColor: 'text-yellow-400',
              },
              {
                icon: Shield,
                title: 'Secure',
                description: 'Your data is encrypted and protected. We take privacy seriously.',
                gradient: 'from-emerald-500/20 to-green-500/20',
                border: 'border-emerald-500/30',
                iconColor: 'text-emerald-400',
              },
            ].map((feature, i) => {
              const Icon = feature.icon;
              return (
                <div
                  key={i}
                  className={`relative overflow-hidden rounded-2xl border ${feature.border} bg-gradient-to-br ${feature.gradient} backdrop-blur-sm p-6 text-left`}
                >
                  <div className={`p-3 rounded-xl bg-slate-800/50 ${feature.iconColor} w-fit mb-4`}>
                    <Icon className="w-6 h-6" />
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">{feature.title}</h3>
                  <p className="text-slate-400 text-sm">{feature.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-slate-800 py-8">
        <div className="max-w-7xl mx-auto px-8 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-emerald-500" />
            <span className="text-sm text-slate-400">
              Flow<span className="text-emerald-500">Task</span> &copy; 2025
            </span>
          </div>
          <p className="text-sm text-slate-500">
            Built with AI for the modern workflow
          </p>
        </div>
      </footer>
    </div>
  );
}
