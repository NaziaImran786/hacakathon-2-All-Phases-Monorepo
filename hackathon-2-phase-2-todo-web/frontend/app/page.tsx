'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function Home() {
    const router = useRouter();

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (token) {
            router.push('/tasks');
        }
    }, [router]);

    return (
        <div className="flex flex-col min-h-screen bg-gray-900 text-white">
            {/* --- Header --- */}
            <header className="flex items-center justify-between px-8 py-6 bg-gray-800 border-b border-gray-700 shadow-md">
                <div className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
                    TaskMaster Pro
                </div>
                <nav className="flex gap-6">
                    <Link href="/login" className="hover:text-blue-400 py-2 font-bold transition">Login</Link>
                    <Link href="/signup" className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-md transition font-medium">
                        Get Started
                    </Link>
                </nav>
            </header>

            {/* --- Hero Section --- */}
            <main className="flex-grow flex flex-col items-center justify-center px-4 py-20 text-center">
                <h1 className="text-5xl md:text-7xl font-extrabold mb-6 tracking-tight">
                    Organize your work <br />
                    <span className="text-blue-500 text-shadow-glow">anywhere, anytime.</span>
                </h1>
                <p className="text-gray-400 text-xl mb-10 max-w-2xl">
                    The simplest way to manage your personal and professional tasks. 
                    Stay focused, organized, and calm with TaskMaster Pro.
                </p>
                
                <div className="flex flex-col sm:flex-row gap-4 mb-16">
                    <Link href="/signup" className="bg-blue-600 hover:bg-blue-700 text-white px-10 py-4 rounded-full text-lg font-bold transition shadow-lg">
                        Create Free Account
                    </Link>
                    <Link href="/login" className="border border-gray-600 hover:bg-gray-800 text-white px-10 py-4 rounded-full text-lg font-bold transition">
                        Sign In
                    </Link>
                </div>

                {/* --- Feature Cards --- */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl w-full px-4">
                    <div className="p-8 bg-gray-800 rounded-2xl border border-gray-700 hover:border-blue-500 transition shadow-sm">
                        <div className="text-3xl mb-4">🚀</div>
                        <h3 className="text-xl font-bold mb-2">Fast Performance</h3>
                        <p className="text-gray-400 text-sm leading-relaxed">Lightning fast task creation and real-time updates across all your devices.</p>
                    </div>
                    <div className="p-8 bg-gray-800 rounded-2xl border border-gray-700 hover:border-blue-500 transition shadow-sm">
                        <div className="text-3xl mb-4">🔒</div>
                        <h3 className="text-xl font-bold mb-2">Secure Storage</h3>
                        <p className="text-gray-400 text-sm leading-relaxed">Your data is encrypted and stored safely in our cloud-based database.</p>
                    </div>
                    <div className="p-8 bg-gray-800 rounded-2xl border border-gray-700 hover:border-blue-500 transition shadow-sm">
                        <div className="text-3xl mb-4">🎯</div>
                        <h3 className="text-xl font-bold mb-2">Stay Focused</h3>
                        <p className="text-gray-400 text-sm leading-relaxed">Minimalist design helps you focus on what really matters - your productivity.</p>
                    </div>
                </div>
            </main>

            {/* --- Footer --- */}
            <footer className="bg-gray-800 border-t border-gray-700 py-10 text-center">
                <p className="text-gray-500 text-sm mb-4">© 2025 TaskMaster Pro. All rights reserved.</p>
                <div className="flex justify-center gap-6 text-gray-400 text-sm">
                    <Link href="#" className="hover:text-white transition">Privacy Policy</Link>
                    <Link href="#" className="hover:text-white transition">Terms of Service</Link>
                    <Link href="#" className="hover:text-white transition">Contact Us</Link>
                </div>
            </footer>
        </div>
    );
}