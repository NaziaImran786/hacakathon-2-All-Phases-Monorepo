'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function Tasks() {
    const [tasks, setTasks] = useState<any[]>([]);
    const [user, setUser] = useState<any>(null);
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [editingTask, setEditingTask] = useState<any>(null);
    const [isLoading, setIsLoading] = useState(true);
    const router = useRouter();

    useEffect(() => {
        const fetchUserAndTasks = async () => {
            const token = localStorage.getItem('token');
            if (!token) {
                router.push('/login');
                return;
            }

            try {
                // Fetch user
                const userResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'}/api/me`, {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });

                if (!userResponse.ok) {
                    throw new Error('Failed to fetch user');
                }

                const userData = await userResponse.json();
                setUser(userData);

                // Fetch tasks
                const tasksResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'}/api/${userData.id}/tasks/`, {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });

                if (!tasksResponse.ok) {
                    throw new Error('Failed to fetch tasks');
                }

                const tasksData = await tasksResponse.json();
                setTasks(tasksData);
            } catch (error) {
                console.error(error);
                localStorage.removeItem('token');
                router.push('/login');
            } finally {
                setIsLoading(false);
            }
        };

        fetchUserAndTasks();
    }, [router]);

    const handleCreateTask = async (e: React.FormEvent) => {
        e.preventDefault();
        const token = localStorage.getItem('token');
        if (!token || !user) return;

        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'}/api/${user.id}/tasks/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({ title, description }),
        });

        if (response.ok) {
            const newTask = await response.json();
            setTasks([...tasks, newTask]);
            setTitle('');
            setDescription('');
        }
    };

    const handleUpdateTask = async (task: any) => {
        const token = localStorage.getItem('token');
        if (!token || !user) return;

        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'}/api/${user.id}/tasks/${task.id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify(task),
        });

        if (response.ok) {
            const updatedTask = await response.json();
            setTasks(tasks.map((t) => (t.id === updatedTask.id ? updatedTask : t)));
            setEditingTask(null);
        }
    };

    const handleDeleteTask = async (taskId: number) => {
        const token = localStorage.getItem('token');
        if (!token || !user) return;

        await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'}/api/${user.id}/tasks/${taskId}`, {
            method: 'DELETE',
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });

        setTasks(tasks.filter((t) => t.id !== taskId));
    };

    const handleLogout = () => {
        localStorage.removeItem('token');
        router.push('/');
    };

    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-black">
                <div className="text-white">Loading...</div>
            </div>
        );
    }

    if (!user) {
        return null; // or a redirect, though useEffect should handle it
    }

    return (
        <div className="min-h-screen p-8 bg-black text-white">
            <div className="flex justify-between py-4 px-4 rounded-lg bg-gray-800 border-b border-gray-700 items-center mb-8">
                <h1 className="text-2xl font-bold ">Tasks for {user.username}</h1>
                <button onClick={handleLogout} className="bg-red-500 text-white p-2 rounded">
                    Logout
                </button>
            </div>

            <form onSubmit={handleCreateTask} className="mb-8 p-4 bg-gray-900 rounded-lg">
                <h2 className="text-xl font-bold mb-4">Create Task</h2>
                <div className="mb-4">
                    <label className="block mb-1">Title</label>
                    <input
                        type="text"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        className="w-full p-2 border rounded bg-gray-800 border-gray-600"
                        required
                    />
                </div>
                <div className="mb-4">
                    <label className="block mb-1">Description</label>
                    <input
                        type="text"
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        className="w-full p-2 border rounded bg-gray-800 border-gray-600"
                        required
                    />
                </div>
                <button type="submit" className="bg-blue-500 text-white p-2 rounded">
                    Create Task
                </button>
            </form>

            <div>
                <h2 className="text-xl font-bold mb-4">Your Tasks</h2>
                <ul>
                    {tasks.map((task: any) => (
                        <li key={task.id} className="border p-4 rounded mb-4 bg-gray-900 border-gray-700">
                            {editingTask?.id === task.id ? (
                                <div>
                                    <input
                                        type="text"
                                        value={editingTask.title}
                                        onChange={(e) => setEditingTask({ ...editingTask, title: e.target.value })}
                                        className="w-full p-2 border rounded mb-2 bg-gray-800 border-gray-600"
                                    />
                                    <input
                                        type="text"
                                        value={editingTask.description}
                                        onChange={(e) => setEditingTask({ ...editingTask, description: e.target.value })}
                                        className="w-full p-2 border rounded mb-2 bg-gray-800 border-gray-600"
                                    />
                                    <button onClick={() => handleUpdateTask(editingTask)} className="bg-green-500 text-white p-2 rounded mr-2">
                                        Save
                                    </button>
                                    <button onClick={() => setEditingTask(null)} className="bg-gray-500 text-white p-2 rounded">
                                        Cancel
                                    </button>
                                </div>
                            ) : (
                                <div>
                                    <h3 className="text-lg font-bold">{task.title}</h3>
                                    <p>{task.description}</p>
                                    <div className="mt-4">
                                        <button onClick={() => setEditingTask(task)} className="bg-yellow-500 text-white p-2 rounded mr-2">
                                            Edit
                                        </button>
                                        <button onClick={() => handleDeleteTask(task.id)} className="bg-red-500 text-white p-2 rounded">
                                            Delete
                                        </button>
                                    </div>
                                </div>
                            )}
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
}


