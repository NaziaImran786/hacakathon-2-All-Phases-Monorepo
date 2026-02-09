# Tasks: AI Chatbot Agent

**Input**: Design documents from `/specs/features/chatbot/`
**Prerequisites**: plan.md (complete), spec.md (complete), mcp-tools.md (complete)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for backend and frontend

- [ ] T001 Create backend directory structure per plan: backend/src/{models,mcp/tools,services,api}
- [ ] T002 Create frontend directory structure per plan: frontend/src/{components/chat,lib,app/chat,hooks}
- [ ] T003 Initialize backend/requirements.txt with FastAPI, SQLModel, OpenAI, MCP SDK, PyJWT
- [ ] T004 Initialize frontend/package.json with Next.js 16+, React, OpenAI Chatkit SDK
- [ ] T005 [P] Create backend/.env.example with DATABASE_URL, BETTER_AUTH_SECRET, OPENAI_API_KEY
- [ ] T006 [P] Create frontend/.env.example with NEXT_PUBLIC_API_URL

**Checkpoint**: Project structure ready for foundational work

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

### Database Models

- [ ] T007 Create backend/src/models/__init__.py with SQLModel imports
- [x] T008 Create backend/src/models/task.py with Task SQLModel (id, user_id, title, description, status, due_date, created_at, updated_at)
- [x] T009 Create backend/src/models/conversation.py with Conversation SQLModel (id, user_id, title, created_at, updated_at)
- [x] T010 Create backend/src/models/message.py with Message SQLModel (id, conversation_id, role, content, tool_calls, tool_results, created_at)
- [x] T011 Create backend/src/db/__init__.py with Database session management
- [x] T012 Create backend/src/db/session.py with async SQLModel session factory

### JWT Authentication

- [x] T013 Create backend/src/api/__init__.py
- [x] T014 Create backend/src/api/deps.py with get_current_user_id dependency (extract user_id from JWT "sub" claim)
- [x] T015 [P] Create backend/src/api/schemas.py with ChatRequest and ChatResponse Pydantic models

### MCP Server Foundation

- [x] T016 Create backend/src/mcp/__init__.py
- [x] T017 Create backend/src/mcp/server.py with MCP server class and tool registration
- [x] T018 Create backend/src/mcp/tools/__init__.py with tool exports
- [x] T019 [P] Create backend/src/services/__init__.py
- [x] T020 [P] Create backend/src/services/agent.py with AgentService base class (OpenAI Agents SDK integration)

### Frontend Foundation

- [x] T021 Create frontend/src/lib/api.ts with authenticated fetch helper (includes JWT)
- [x] T022 Create frontend/src/hooks/useChat.ts hook for chat state management

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add Tasks via Natural Language (Priority: P1) MVP

**Goal**: Users can add tasks using natural language like "Add a task to buy groceries"

**Independent Test**: Send "Add a task to buy groceries" to POST /api/chat, verify task is created in database with correct title and user_id

### MCP Tool: add_task

- [x] T021 [P] [US1] Implement add_task tool handler in backend/src/mcp/tools/add_task.py (user_id, title, description, due_date params)
- [x] T022 [US1] Register add_task tool in backend/src/mcp/server.py tool registry

### Backend Endpoint

- [x] T023 [US1] Create backend/src/api/chat.py with POST /api/chat endpoint
- [x] T024 [US1] Implement chat endpoint to: verify JWT, create conversation, store user message, call agent, store assistant response
- [x] T025 [US1] Add error handling for 401 (unauthorized), 400 (invalid request), 500 (internal error)

### Frontend Components

- [x] T026 [P] [US1] Create frontend/src/components/chat/ChatKitProvider.tsx with Chatkit client class
- [x] T027 [P] [US1] Create frontend/src/components/chat/ChatWindow.tsx main chat container
- [x] T028 [P] [US1] Create frontend/src/components/chat/ChatInput.tsx text input with submit button
- [x] T029 [P] [US1] Create frontend/src/components/chat/MessageBubble.tsx for displaying messages
- [x] T030 [US1] Create frontend/src/app/chat/page.tsx chat route page

**Checkpoint**: User can send "Add a task to buy groceries" and see task created

---

## Phase 4: User Story 2 - List Tasks via Natural Language (Priority: P1)

**Goal**: Users can query their tasks using natural language like "What's pending?"

**Independent Test**: Ask "What's pending?" via chat, verify all incomplete tasks are returned

### MCP Tool: list_tasks

- [x] T031 [P] [US2] Implement list_tasks tool handler in backend/src/mcp/tools/list_tasks.py (user_id, status, limit, offset params)
- [x] T032 [US2] Register list_tasks tool in backend/src/mcp/server.py tool registry

### Backend Integration

- [ ] T033 [US2] Update backend/src/api/chat.py agent prompt to include list_tasks capability
- [ ] T034 [US2] Update ChatService to support querying tasks for agent response

**Checkpoint**: User can ask "What's pending?" and see their incomplete tasks

---

## Phase 5: User Story 3 - Complete Tasks via Natural Language (Priority: P1)

**Goal**: Users can mark tasks complete using natural language like "Mark task 1 as done"

**Independent Test**: Ask "Complete task 1", verify task status changes to "completed"

### MCP Tool: complete_task

- [x] T035 [P] [US3] Implement complete_task tool handler in backend/src/mcp/tools/complete_task.py (user_id, task_id params)
- [x] T036 [US3] Register complete_task tool in backend/src/mcp/server.py tool registry

### Backend Integration

- [ ] T037 [US3] Update backend/src/api/chat.py agent prompt to include complete_task capability
- [ ] T038 [US3] Add task not found and already completed error responses

**Checkpoint**: User can say "Complete task 1" and see task marked done

---

## Phase 6: User Story 4 - Update Tasks via Natural Language (Priority: P2)

**Goal**: Users can modify tasks using natural language like "Change task 1 to buy vegetables"

**Independent Test**: Send "Change task 1 to buy vegetables", verify task title updates

### MCP Tool: update_task

- [x] T039 [P] [US4] Implement update_task tool handler in backend/src/mcp/tools/update_task.py (user_id, task_id, title, description, due_date params)
- [x] T040 [US4] Register update_task tool in backend/src/mcp/server.py tool registry

### Backend Integration

- [ ] T041 [US4] Update backend/src/api/chat.py agent prompt to include update_task capability
- [ ] T042 [US4] Add validation for at least one update field provided

**Checkpoint**: User can update task details via natural language

---

## Phase 7: User Story 5 - Delete Tasks via Natural Language (Priority: P2)

**Goal**: Users can remove tasks using natural language like "Delete task 5"

**Independent Test**: Send "Delete task 5", verify task is removed from database

### MCP Tool: delete_task

- [x] T043 [P] [US5] Implement delete_task tool handler in backend/src/mcp/tools/delete_task.py (user_id, task_id params)
- [x] T044 [US5] Register delete_task tool in backend/src/mcp/server.py tool registry

### Backend Integration

- [ ] T045 [US5] Update backend/src/api/chat.py agent prompt to include delete_task capability
- [ ] T046 [US5] Add soft-delete or hard-delete with confirmation pattern

**Checkpoint**: User can delete tasks via natural language

---

## Phase 8: User Story 6 - Conversational Context (Priority: P2)

**Goal**: Agent remembers conversation context for multi-turn chats like "Complete the first one"

**Independent Test**: Ask "What tasks?" then "Complete the first one", verify correct task is completed

### Conversation History Service

- [x] T047 [P] [US6] Create backend/src/services/chat.py with ChatService class
- [x] T048 [US6] Implement get_or_create_conversation() method in ChatService
- [x] T049 [US6] Implement get_messages() and add_message() methods in ChatService

### Agent Context Integration

- [ ] T050 [US6] Update backend/src/services/agent.py to pass conversation history to agent
- [ ] T051 [US6] Store user and assistant messages with tool_calls/tool_results for audit

### Frontend Context

- [ ] T052 [P] [US6] Update ChatKitProvider to track conversation_id across messages
- [ ] T053 [US6] Add conversation_id to chat API requests for multi-turn continuity

**Checkpoint**: Agent maintains conversation context across messages

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T054 [P] Add rate limiting middleware in backend/src/api/chat.py (60 req/min per user)
- [ ] T055 [P] Add audit logging for all tool invocations in backend/src/services/audit.py
- [ ] T056 Add loading state UI in frontend/src/components/chat/TypingIndicator.tsx
- [ ] T057 Add error retry UI in ChatWindow for failed messages
- [ ] T058 Add markdown rendering for agent responses in MessageBubble.tsx
- [ ] T059 Update frontend/README.md with chat integration instructions
- [ ] T060 [P] Add integration test: full chat flow with add->list->complete in backend/tests/test_chat_flow.py
- [ ] T061 [P] Add frontend test: ChatWindow renders messages in frontend/tests/chat/ChatWindow.test.tsx

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational - Uses same conversation infrastructure as US1
- **User Story 3 (P1)**: Can start after Foundational - Depends on US1 for task existence
- **User Story 4 (P2)**: Can start after Foundational - Depends on US1
- **User Story 5 (P2)**: Can start after Foundational - Depends on US1
- **User Story 6 (P2)**: Can start after Foundational - Cross-cuts all stories

### Within Each User Story

- MCP tools before backend endpoints
- Backend endpoints before frontend components
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel
- MCP tools within a user story marked [P] can run in parallel
- Frontend components within a user story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all MCP tool implementations for US1 together:
Task: T021 "Implement add_task tool handler in backend/src/mcp/tools/add_task.py"

# Launch all frontend components for US1 together:
Task: T026 "Create ChatKitProvider.tsx"
Task: T027 "Create ChatWindow.tsx"
Task: T028 "Create ChatInput.tsx"
Task: T029 "Create MessageBubble.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test "Add a task to buy groceries" works
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add P2 stories as needed → Test → Deploy
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (add tasks)
   - Developer B: User Story 2 + 3 (list + complete tasks)
   - Developer C: User Story 4 + 5 + 6 (update, delete, context)
3. Stories complete and integrate independently

---

## Task Summary

| Phase | Tasks | Description |
|-------|-------|-------------|
| Phase 1 | T001-T006 | Setup (6 tasks) |
| Phase 2 | T007-T020 | Foundational (14 tasks) |
| Phase 3 (US1) | T021-T030 | Add Tasks (10 tasks) - MVP |
| Phase 4 (US2) | T031-T034 | List Tasks (4 tasks) |
| Phase 5 (US3) | T035-T038 | Complete Tasks (4 tasks) |
| Phase 6 (US4) | T039-T042 | Update Tasks (4 tasks) |
| Phase 7 (US5) | T043-T046 | Delete Tasks (4 tasks) |
| Phase 8 (US6) | T047-T053 | Conversational Context (7 tasks) |
| Phase 9 | T054-T061 | Polish (8 tasks) |

**Total Tasks**: 61

**MVP Scope**: Phases 1-3 (20 tasks) - Add tasks via natural language

**Parallel Opportunities**: 30+ tasks marked [P] can run concurrently
