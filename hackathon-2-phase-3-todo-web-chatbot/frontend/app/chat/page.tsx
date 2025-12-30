// Chat Page for Phase III Chatbot
// Task ID: T030
// Reference: specs/features/chatbot/plan.md (Frontend Development)

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ChatKitProvider } from '../../src/components/chat/ChatKitProvider';
import { ChatWindow } from '../../src/components/chat/ChatWindow';

export default function ChatPage() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // Check for authentication token
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }
    setIsAuthenticated(true);
    setIsLoading(false);
  }, [router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black">
        <div className="text-slate-100">Loading chat...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-black">
      <ChatKitProvider>
        <main className="h-screen">
          <ChatWindow showTasks />
        </main>
      </ChatKitProvider>
    </div>
  );
}
