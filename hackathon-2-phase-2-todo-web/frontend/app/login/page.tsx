'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function Login() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [status, setStatus] = useState('');
    const router = useRouter();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setStatus('Processing...');
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

        try {
            const response = await fetch(`${apiUrl}/token`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({
                    username,
                    password,
                }),
            });

            if (response.ok) {
                setStatus('Success! Redirecting to tasks...');
                const data = await response.json();
                localStorage.setItem('token', data.access_token);
                setTimeout(() => router.push('/tasks'), 1500);
            } else {
                const errorData = await response.json();
                setStatus(`Error: ${errorData.detail || 'Login failed'}`);
            }
        } catch (err) {
            console.error(err);
            setStatus('Connection Failed. Is backend running?');
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-black">
            <form onSubmit={handleSubmit} className="p-8 border border-gray-700 rounded-lg shadow-xl bg-gray-900 w-full max-w-md">
                <h1 className="text-2xl font-bold mb-6 text-white text-center">Login</h1>

                {status && (
                    <div className={`mb-4 p-2 text-sm text-center rounded ${status.includes('Success') ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                        {status}
                    </div>
                )}

                <div className="mb-4">
                    <label className="block mb-2 text-gray-300">Username</label>
                    <input
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        className="w-full p-2 rounded bg-gray-800 border border-gray-600 text-white focus:outline-none focus:border-blue-500"
                        required
                    />
                </div>
                <div className="mb-6">
                    <label className="block mb-2 text-gray-300">Password</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="w-full p-2 rounded bg-gray-800 border border-gray-600 text-white focus:outline-none focus:border-blue-500"
                        required
                    />
                </div>
                <button type="submit" className="w-full bg-blue-600 text-white p-2 rounded font-bold hover:bg-blue-700 transition">
                    Login
                </button>
                <p className="text-center mt-4 text-gray-400">
                    Don't have an account?{' '}
                    <Link href="/signup" className="text-blue-500 hover:underline">
                        Sign up
                    </Link>
                </p>
            </form>
        </div>
    );
}

