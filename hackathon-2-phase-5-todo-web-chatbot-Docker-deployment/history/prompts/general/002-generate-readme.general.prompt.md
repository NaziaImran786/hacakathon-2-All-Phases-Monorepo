---
id: 002
title: generate-readme
stage: general
date: 2025-12-30
surface: agent
model: claude-sonnet-4.5
feature: none
branch: main
user: Nazia Imran
command: generate comprehensive README
labels: ["documentation", "readme", "architecture"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - README.md
tests:
 - N/A (documentation task)
---

## Prompt

Please analyze the entire codebase of this Phase III Todo Web Chatbot and generate a professional, comprehensive README.md file in the root directory. The documentation must include:

1. Project Overview:

Name: FlowTask - AI-Powered Productivity Dashboard.

Description: A modern, stateless Todo application featuring an integrated AI Assistant powered by OpenAI and MCP (Model Context Protocol).

2. Tech Stack:

Frontend: Next.js, Tailwind CSS (Glassmorphism theme), Framer Motion, Better Auth (JWT).

Backend: FastAPI, SQLModel (Asynchronous), Neon PostgreSQL.

AI: OpenAI Agents SDK, MCP Tools for Task CRUD operations.

3. Key Features & Architecture:

Stateless AI Chat: Explain how the assistant fetches history from the DB on every request to maintain a stateless backend.

Unified Data Sync: Detail how AI-added tasks and manual tasks are synced in real-time via the same Neon DB tasks table.

Modern UI: Mention the floating AI widget, side-drawer chat, and dark-themed dashboard.

Secure Auth: Explain the Signup-to-Login redirect flow and JWT-based user

## Response snapshot

Created a comprehensive README.md file in the root directory with the following sections:

**Project Overview:**
- Name: FlowTask - AI-Powered Productivity Dashboard
- Description with key features: stateless AI chat, unified data sync, modern UI, secure auth

**Tech Stack:**
- Frontend: Next.js 14.1.0, Tailwind CSS, Framer Motion, Lucide React, TypeScript
- Backend: FastAPI, Neon PostgreSQL with SQLModel, JWT (python-jose) with Bcrypt
- AI & MCP: OpenAI Agents SDK, GPT-4o model, Official MCP SDK (FastMCP v1.25.0)

**Key Features & Architecture:**
- Stateless AI Chat: Detailed request cycle diagram explaining how conversation history is fetched from database on every request, with benefits (no memory leaks, easy scaling, all data persisted)
- Unified Data Sync: Explained how both manual and AI-created tasks go to same Neon PostgreSQL tasks table, with real-time sync mechanism (fetchTasks() + custom events)
- Modern UI: Glassmorphism theme, centered task list, FAB button, side-drawer chat (450px width, full height)
- Secure Auth: Detailed signup flow (no token returned, redirect to /login) and login flow (JWT returned, stored in localStorage)

**Additional Sections:**
- Project Structure: Complete directory tree with file descriptions
- Installation: Prerequisites, backend setup, frontend setup with environment variables
- Usage: Manual task creation, AI-assisted task creation, task management, natural language commands
- API Endpoints: Full list of authentication, task CRUD, and chat endpoints
- MCP Tools: Table of all available tools with parameters
- Database Schema: Legacy tables (Phase I/II) and Phase III tables
- Development: Testing and production build instructions
- Contributing: Standard Git workflow
- License and Support information

## Outcome

- ✅ Impact: Professional documentation created covering entire codebase architecture
- 🧪 Tests: N/A (documentation task)
- 📁 Files: 1 file created (README.md in root)
- 🔁 Next prompts: Consider adding inline code comments or API documentation
- 🧠 Reflection: README provides complete architectural overview for new developers, including stateless architecture details, MCP tool integration, and database schema. The signup-to-login flow is clearly documented to match the recent implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A (documentation task)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A - documentation complete
