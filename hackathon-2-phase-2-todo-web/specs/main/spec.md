Specify Phase: Full-Stack Web Application

Goal: Develop a secure, multi-user web application for task management with persistent database storage.

1. Functional Requirements:


Authentication: Implement a complete user registration and login system.


Task Management: Provide a Web UI for users to create, read, update, and delete tasks.
+1


Task Completion: Allow users to toggle the completion status of any task.


User Isolation: Ensure strict data privacy where users can only access and manage their own tasks based on their user_id.
+1

2. Technical Requirements:


Frontend: Build a responsive interface using Next.js 16+ with App Router.
+1


Backend: Develop a FastAPI service to handle logic and database communication.
+1


Database: Use Neon Serverless PostgreSQL with SQLModel as the ORM.
+1

Security: Use Better Auth to issue JWT tokens. The backend must verify these tokens in every request header.
+2

3. API Specification:


GET /api/{user_id}/tasks: Retrieve all tasks for the logged-in user.


POST /api/{user_id}/tasks: Create a new task entry.


PUT /api/{user_id}/tasks/{id}: Update specific task details.


DELETE /api/{user_id}/tasks/{id}: Remove a task.


PATCH /api/{user_id}/tasks/{id}/complete: Toggle task completion.