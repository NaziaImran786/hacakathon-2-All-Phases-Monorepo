// API Client for Phase III Chatbot
// Task ID: T021 (Frontend foundation)
// Reference: specs/features/chatbot/plan.md (JWT Authentication Integration)

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ChatResponse {
  success: boolean;
  response: {
    content: string;
    tasks: TaskResponse[];
  };
  conversation_id: number;
  message_id: number;
}

export interface TaskResponse {
  id: number;
  user_id: string;
  title: string;
  description: string | null;
  status: string;
  due_date: string | null;
  created_at: string;
  updated_at: string;
}

export interface SendMessageRequest {
  message: string;
  conversation_id?: number;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Get the JWT token from storage.
   * Checks multiple locations for compatibility with existing auth.
   */
  private getToken(): string {
    if (typeof window === 'undefined') {
      return '';
    }
    // Primary: check localStorage 'token' (Phase I/II auth)
    const token = localStorage.getItem('token');
    if (token) {
      return token;
    }
    // Fallback: try Better Auth session
    const session = localStorage.getItem('better-auth-session');
    if (session) {
      try {
        const parsed = JSON.parse(session);
        return parsed.token || '';
      } catch {
        return '';
      }
    }
    // Fallback: try session storage
    return sessionStorage.getItem('auth-token') || '';
  }

  /**
   * Send a chat message to the backend.
   * Includes JWT authentication via Authorization header.
   */
  async sendMessage(request: SendMessageRequest): Promise<ChatResponse> {
    const token = this.getToken();

    if (!token) {
      throw new Error('No authentication token available');
    }

    const response = await fetch(`${this.baseUrl}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }));

      if (response.status === 401) {
        throw new Error('Unauthorized: Please log in again');
      }
      if (response.status === 400) {
        throw new Error(error.detail || 'Invalid request');
      }
      if (response.status === 500) {
        throw new Error('Server error: Please try again later');
      }

      throw new Error(error.detail || 'Request failed');
    }

    return response.json();
  }

  /**
   * Health check for the API.
   */
  async healthCheck(): Promise<{ status: string; service: string }> {
    const response = await fetch(`${this.baseUrl}/api/health`);
    return response.json();
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

// Export class for custom configurations
export { ApiClient };
