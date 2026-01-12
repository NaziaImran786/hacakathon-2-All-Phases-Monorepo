Specify Phase: Full-Stack Web Application

Goal: Develop a secure, multi-user web application for task management with persistent database storage.

1. Functional Requirements:


Authentication: Implement a complete user registration and login system.


Task Management: Provide a Web UI for users to create, read, update, and delete tasks.
+1


Task Completion: Allow users to toggle the completion status of any task.


User Isolation: Ensure strict data privacy where users can only access and manage their own tasks. The backend MUST extract user_id from the JWT token (not URL parameters) and filter all queries accordingly.

2. Technical Requirements:


Frontend: Build a responsive interface using Next.js 16+ with App Router.
+1


Backend: Develop a FastAPI service to handle logic and database communication.
+1


Database: Use Neon Serverless PostgreSQL with SQLModel as the ORM.
+1

Security: Use Better Auth to issue JWT tokens. The backend must verify these tokens in every request header.
+2

3. API Specification (REST):

All endpoints extract user_id from the JWT Authorization header. The backend validates the JWT and extracts the user_id claim.

GET /api/tasks: Retrieve all tasks for the authenticated user.

POST /api/tasks: Create a new task entry.

PUT /api/tasks/{id}: Update specific task details.

DELETE /api/tasks/{id}: Remove a task.

PATCH /api/tasks/{id}/complete: Toggle task completion.

4. MCP Tools (Phase III):

All MCP tools require user_id parameter for data isolation. See specs/api/mcp-tools.md for detailed tool specifications.