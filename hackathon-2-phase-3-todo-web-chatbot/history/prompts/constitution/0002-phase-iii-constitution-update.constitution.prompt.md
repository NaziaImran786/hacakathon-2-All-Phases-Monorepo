---
id: "0002"
title: "Phase III Constitution Update"
stage: "constitution"
date: "2025-12-29"
surface: "agent"
model: "sonnet-4-5-20250929"
feature: "none"
branch: "main"
user: "Nazia Imran"
command: "update sp.constitution for Phase III"
labels: ["constitution","phase-3","ai-agents","stateless"]
links:
  spec: "null"
  ticket: "null"
  adr: "null"
  pr: "null"
files:
  - ".specify/memory/constitution.md"
  - "CLAUDE.md"
tests: []
---

## Prompt

Update sp.constitution for Phase III. 1.Add rules for AI agents development: use OpenAI Agents SDK for logic and Official MCP SDK for tools. 2.Define the Stateless Architecture:The server must hold no state; all conversation history and task states must be presisted to the Neon PostgeySQL database. 3.Update CLAUDE.md to iclude instruction for the new /backend MCP server and /frontend OpenAI Chatkit integration.

## Response snapshot

Updated constitution.md (v1.0.0 → v2.0.0):
- Added Principle VI: AI Agents Development (OpenAI Agents SDK for logic, Official MCP SDK for tools)
- Added Principle VII: Stateless Architecture (no server state, all persistence to Neon PostgreSQL)
- Updated Constraints & Requirements section
- Updated version and amendment date

Updated CLAUDE.md:
- Added "MCP Server Configuration (Phase III)" section with guidelines and run command
- Added "OpenAI Chatkit Integration (Phase III)" section with guidelines and dev command

## Outcome

- ✅ Impact: Updated project constitution and CLAUDE.md for Phase III requirements
- 🧪 Tests: None (constitution update)
- 📁 Files: 2 files modified (.specify/memory/constitution.md, CLAUDE.md)
- 🔁 Next prompts: None
- 🧠 Reflection: Added AI Agents SDK and Stateless Architecture principles for Phase III; MCP server and Chatkit integration instructions for Claude Code agent

## Evaluation notes (flywheel)

- Failure modes observed: "null"
- Graders run and results (PASS/FAIL): "null"
- Prompt variant (if applicable): "null"
- Next experiment (smallest change to try): "null"
