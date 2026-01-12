---
id: "0002"
title: "Phase III Chatbot Implementation Plan"
stage: "plan"
date: "2025-12-29"
surface: "agent"
model: "sonnet-4-5-20250929"
feature: "chatbot-agent"
branch: "feat/chatbot-agent"
user: "Nazia Imran"
command: "Generate speckit.plan for Phase III"
labels: ["plan","phase-3","stateless","chatbot","mcp"]
links:
  spec: "specs/features/chatbot.md"
  ticket: "null"
  adr: "null"
  pr: "null"
files:
  - "specs/features/chatbot/plan.md"
tests: []
---

## Prompt

Generate speckit.plan for Phase III. 1. Plan the Stateless Request Cycle: Receive message -> Fetch history from DB -> Build message array -> Run agent with MCP tools -> Store response -> Return to client. 2. Plan the OpenAI ChatKit integration on the frontend and the POST /api/{user_id}/chat endpoint on the backend. 3. Ensure the Better Auth JWT is still used to identify the user for all AI actions.

## Response snapshot

Created comprehensive implementation plan in specs/features/chatbot/plan.md:

1. Stateless Request Cycle (9 steps):
   - Receive message with JWT
   - Verify JWT and extract user_id
   - Fetch conversation history from DB
   - Build message array (history + new)
   - Run OpenAI Agent with MCP tools
   - Store user message
   - Store assistant message with tool calls/results
   - Return response to client

2. OpenAI ChatKit Integration:
   - ChatKitProvider component for client management
   - ChatWindow, ChatInput, MessageBubble components
   - JWT passed via Authorization header
   - API endpoint: POST /api/chat

3. Backend API Design:
   - POST /api/chat endpoint with request/response schemas
   - JWT verification dependency extracting user_id from token
   - Integration with AgentService and ChatService

4. MCP Tools Integration:
   - Tool registration with OpenAI Agents SDK
   - add_task, list_tasks, complete_task, update_task, delete_task
   - User isolation enforced in each tool handler

5. JWT Authentication:
   - user_id extracted from JWT "sub" claim
   - Consistent across REST and MCP interfaces
   - HTTPBearer dependency for verification

## Outcome

- ✅ Impact: Created complete implementation plan for Phase III chatbot
- 🧪 Tests: None (planning phase)
- 📁 Files: 1 file created (specs/features/chatbot/plan.md)
- 🔁 Next prompts: Run /sp.tasks to generate implementation tasks
- 🧠 Reflection: Designed stateless architecture ensuring scalability; defined clear request cycle; integrated JWT auth for user isolation; specified MCP tool patterns

## Evaluation notes (flywheel)

- Failure modes observed: "null"
- Graders run and results (PASS/FAIL): "null"
- Prompt variant (if applicable): "null"
- Next experiment (smallest change to try): "null"
