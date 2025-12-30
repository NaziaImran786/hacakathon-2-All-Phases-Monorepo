# FlowTask - AI-Powered Productivity Dashboard

A modern, stateless Todo application featuring an integrated AI Assistant powered by OpenAI and MCP (Model Context Protocol). FlowTask combines intuitive task management with intelligent AI assistance, allowing users to create, organize, and complete tasks using natural language commands.

![Version](https://img.shields.io/badge/version-3.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Overview

FlowTask is a Phase III Todo Web Chatbot that provides:
- **Stateless AI Chat**: AI assistant with full conversational memory, no session state required
- **Unified Data Sync**: AI-created tasks and manual tasks are stored in the same database for seamless synchronization
- **Modern UI**: Floating AI widget, side-drawer chat interface, and dark-themed glassmorphism dashboard
- **Secure Auth**: JWT-based authentication with signup-to-login redirect flow

## Tech Stack

### Frontend
- **Framework**: Next.js 14.1.0 (App Router)
- **Styling**: Tailwind CSS with custom glassmorphism theme
- **Animations**: Framer Motion for smooth UI transitions
- **Icons**: Lucide React
- **TypeScript**: Full type safety

### Backend
- **Framework**: FastAPI (Python)
- **Database**: Neon PostgreSQL with SQLModel ORM
- **Authentication**: JWT (python-jose) with Bcrypt password hashing
- **CORS**: Configured for frontend-backend communication

### AI & MCP
- **OpenAI Agents SDK**: Agent orchestration and structured outputs
- **Model**: GPT-4o
- **MCP (Model Context Protocol)**: Official MCP SDK (FastMCP v1.25.0) for tool integrations
- **MCP Tools**: Task CRUD operations (add, list, complete, update, delete)

## Key Features & Architecture

### Stateless AI Chat

FlowTask implements a **stateless request cycle** where the AI assistant fetches entire conversation history from the database on every request:

```
Request Flow:
1. User sends message → Frontend
2. Frontend includes JWT in Authorization header
3. Backend validates JWT and extracts user_id
4. ChatService fetches all messages from Neon DB for this conversation
5. Agent processes message history + new user message
6. Agent response is saved to database
7. Response returned to frontend
```

**Why Stateless?**
- No memory leaks or session state issues
- Easy horizontal scaling (any server can handle any request)
- All conversation history persisted to Neon PostgreSQL
- User can refresh page and continue seamlessly

**Database Schema for Chat:**
- `conversations` table: Stores chat sessions with user isolation
- `messages` table: Stores all user/assistant messages with tool context

### Unified Data Sync

All tasks are stored in a single Neon PostgreSQL database table, whether created:
- Manually via UI (frontend → REST API)
- Via AI assistant (user → AI → MCP tools → same database)

**Task Table Schema:**
```python
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: Optional[str] = None
    status: str = "pending"  # pending, completed, cancelled
    user_id: str = Field(foreign_key="user.id")
    due_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
```

**Real-time Sync:**
- Frontend uses `fetchTasks()` after AI interactions to update UI
- Custom event `taskUpdated` dispatched for cross-component synchronization
- Both manual and AI-created tasks appear in the same dashboard

### Modern UI

**Dashboard Features:**
- Dark theme with glassmorphism (semi-transparent cards, backdrop blur)
- Centered task list with responsive layout
- Floating Action Button (FAB) for AI chat access
- Side-drawer chat window (450px width, full height)
- Smooth animations via Framer Motion

**Chat Interface:**
- Full-height drawer from right side
- Quick action buttons (Add Task, List Tasks, Complete, etc.)
- Message bubbles with timestamps
- Typing indicators during AI processing

### Secure Authentication

**Signup Flow:**
1. User registers with username/password
2. Backend creates user account in database
3. Returns success message only: `{"message": "User created successfully"}`
4. Frontend redirects to `/login` with toast message
5. User must explicitly log in with credentials

**Login Flow:**
1. User submits credentials to `/token` endpoint
2. Backend validates and returns JWT (30-minute expiry)
3. Frontend stores JWT in `localStorage`
4. All subsequent requests include `Authorization: Bearer {token}` header

**Security Features:**
- Passwords hashed with Bcrypt before storage
- JWT tokens signed with secret key (HS256)
- User isolation enforced via `user_id` in all database queries
- CORS configured for frontend origin only

## Project Structure

```
flowtask/
├── backend/                  # FastAPI backend
│   ├── main.py              # Main API app, auth endpoints, task CRUD
│   ├── auth.py              # JWT token generation/validation
│   ├── models.py            # Legacy SQLModel definitions (Task, User)
│   ├── src/
│   │   ├── api/
│   │   │   ├── chat.py     # POST /api/chat endpoint
│   │   │   ├── schemas.py  # Pydantic models for API
│   │   │   └── deps.py    # Dependency injection (JWT extraction)
│   │   ├── services/
│   │   │   ├── agent.py     # OpenAI Agents SDK orchestration
│   │   │   ├── chat.py     # Conversation history management
│   │   │   └── db.py      # Database connection and queries
│   │   ├── mcp/
│   │   │   ├── server.py    # MCP server wrapper (FastMCP)
│   │   │   └── tools/
│   │   │       ├── add_task.py
│   │   │       ├── list_tasks.py
│   │   │       ├── complete_task.py
│   │   │       ├── update_task.py
│   │   │       └── delete_task.py
│   │   └── models/
│   │       ├── conversation.py
│   │       ├── message.py
│   │       └── task.py
│   └── requirements.txt
│
├── frontend/                 # Next.js 14 frontend
│   ├── app/
│   │   ├── layout.tsx       # Root layout with metadata
│   │   ├── page.tsx         # Landing page
│   │   ├── login/
│   │   │   └── page.tsx     # Login form with JWT storage
│   │   ├── signup/
│   │   │   └── page.tsx     # Signup form (no token returned)
│   │   └── tasks/
│   │       └── page.tsx     # Main dashboard + AI chat
│   ├── src/
│   │   └── lib/
│   │       └── api.ts         # API client with JWT auth
│   ├── package.json
│   ├── tailwind.config.js
│   └── tsconfig.json
│
├── .env                     # Environment variables (create from example)
├── CLAUDE.md               # Project guidelines
└── README.md               # This file
```

## Installation

### Prerequisites
- Python 3.9+
- Node.js 18+
- Neon PostgreSQL account (free tier available)
- OpenAI API key

### Backend Setup

1. **Create virtual environment:**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
Create `.env` file in `backend/`:
```env
DATABASE_URL=postgresql://user:password@ep-cool.us-east-2.aws.neon.tech/neondb?sslmode=require
OPENAI_API_KEY=sk-proj-...
BETTER_AUTH_SECRET=your-secret-key-here
```

4. **Run backend:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. **Install dependencies:**
```bash
cd frontend
npm install
```

2. **Configure environment:**
Create `.env.local` file in `frontend/`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. **Run frontend:**
```bash
npm run dev
```

4. **Open browser:**
Navigate to `http://localhost:3000`

## Usage

### Creating a Task

**Manual:**
1. Login to your account
2. Click "Add Task" button
3. Enter task details
4. Click "Create Task"

**Via AI Assistant:**
1. Click floating chat button (bottom-right)
2. Type: "Add a task called 'Buy groceries'"
3. AI will confirm and create task
4. Task appears in dashboard automatically

### Managing Tasks

- **Complete**: Click "Complete" button on any task
- **Edit**: Click edit icon to modify title/description
- **Delete**: Click "Delete" button to remove task

### AI Chat Commands

The AI assistant understands natural language:
- "Show me all my tasks"
- "Add a task to call mom tomorrow"
- "Mark task #3 as complete"
- "Delete the task about groceries"
- "Update task #2 to say 'Buy milk instead of groceries'"

## API Endpoints

### Authentication
- `POST /signup` - Create user account (returns success message, no token)
- `POST /token` - Login and receive JWT token
- `GET /api/me` - Get current user info (JWT required)

### Tasks
- `POST /api/{user_id}/tasks/` - Create task (JWT required)
- `GET /api/{user_id}/tasks/` - List user's tasks (JWT required)
- `PUT /api/{user_id}/tasks/{task_id}` - Update task (JWT required)
- `DELETE /api/{user_id}/tasks/{task_id}` - Delete task (JWT required)
- `PATCH /api/{user_id}/tasks/{task_id}/complete` - Toggle completion (JWT required)

### AI Chat
- `POST /api/chat` - Send message to AI assistant (JWT required)
  - Request: `{ "message": "string", "conversation_id": number }`
  - Response: `{ "success": true, "response": { "content": "...", "tasks": [...] }, "conversation_id": 123, "message_id": 456 }`
- `GET /api/health` - Health check

## MCP Tools

The AI assistant has access to these MCP tools:

| Tool | Description | Parameters |
|------|-------------|-------------|
| `add_task` | Create a new task | `title`, `description?`, `due_date?` |
| `list_tasks` | List user's tasks | `status?` (all/pending/completed), `limit?`, `offset?` |
| `complete_task` | Mark task as completed | `task_id` |
| `update_task` | Update task details | `task_id`, `title?`, `description?`, `due_date?` |
| `delete_task` | Remove a task | `task_id` |

All tools are scoped to the authenticated user via `user_id`.

## Database Schema

### Legacy Tables (Phase I/II)
- `users`: username, hashed_password
- `tasks`: id, title, description, completed, owner_id

### Phase III Tables
- `conversations`: id, user_id, title, created_at, updated_at
- `messages`: id, conversation_id, role, content, tool_calls, tool_results, created_at
- `tasks` (extended): status, due_date, created_at, updated_at

## Development

### Running Tests
```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

### Building for Production
```bash
# Frontend
cd frontend
npm run build
npm start

# Backend (with gunicorn)
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: [repository-url]/issues
- Documentation: [docs-url]

---

**Built with ❤️ using Next.js, FastAPI, and OpenAI Agents SDK**
