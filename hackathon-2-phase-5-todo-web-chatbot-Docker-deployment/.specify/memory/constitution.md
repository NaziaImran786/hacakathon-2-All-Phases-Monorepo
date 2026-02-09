<!-- Sync Impact Report:
Version change: 0.0.0 -> 1.0.0
Modified principles: All principles are new.
Added sections: Core Principles, Constraints & Requirements, Development Workflow.
Removed sections: None.
Templates requiring updates:
- .specify/templates/plan-template.md: ✅ updated (will be checked in later steps)
- .specify/templates/spec-template.md: ✅ updated (will be checked in later steps)
- .specify/templates/tasks-template.md: ✅ updated (will be checked in later steps)
- .specify/templates/commands/*.md: ✅ updated (will be checked in later steps)
Follow-up TODOs: None.
-->
# Spec-Driven Development Todo Web Constitution

## Core Principles

### I. Spec-Driven Development (SDD)
All code must be generated from specifications; manual code writing is strictly prohibited.

### II. Standardized Tech Stack
Frontend: Next.js 16+ (App Router), Backend: Python FastAPI, ORM: SQLModel, Database: Neon Serverless PostgreSQL.

### III. Monorepo Architecture
The project utilizes a monorepo structure to manage both frontend and backend within a unified codebase.

### IV. Secure Authentication (JWT)
Authentication must use Better Auth with JWT tokens. All frontend API requests must include the JWT token in the 'Authorization: Bearer <token>' header.

### V. User Isolation & JWT Verification
The backend must verify all JWT tokens and enforce strict user isolation by filtering database queries, ensuring users only access their own tasks.

### VI. AI Agents Development (Phase III)
All AI agent logic must use the **OpenAI Agents SDK** for agent orchestration and decision-making. All tool integrations must use the **Official MCP SDK** (Model Context Protocol). Agents SDK handles agent handoffs, guardrails, and structured outputs; MCP SDK handles external tool connections.

### VII. Stateless Architecture (Phase III)
The server must hold **no internal state**. All conversation history and task states must be persisted to the **Neon PostgreSQL database**. This includes:
- Chat/message histories
- Agent conversation context
- Task completion states
- Any temporal data requiring persistence

Statelessness ensures horizontal scalability, fault tolerance, and consistent behavior across server restarts.

## Constraints & Requirements

No manual code writing.
Strict adherence to the defined tech stack (Next.js 16+, FastAPI, SQLModel, Neon Serverless PostgreSQL).
Monorepo structure is mandatory.
Authentication via Better Auth with JWT tokens, with token inclusion in API request headers.
Backend JWT verification and user-specific data filtering.
AI agent logic must use OpenAI Agents SDK; tool integrations must use Official MCP SDK.
Server must be stateless; all state persisted to Neon PostgreSQL database.

## Development Workflow

All development must strictly follow the Spec-Driven Development (SDD) workflow.
Code generation is the primary method of implementation; manual coding is prohibited.
Specifications (specs), plans, and tasks will drive all development cycles.

## Governance

This Constitution is the supreme governing document for all project development.
Amendments require a formal proposal, review, and consensus from key stakeholders, documented via an ADR.
Compliance with these principles must be verified during code reviews and continuous integration processes.
New features, architectural decisions, and major refactors must align with these core principles.

**Version**: 2.0.0 | **Ratified**: 2025-12-23 | **Last Amended**: 2025-12-29
