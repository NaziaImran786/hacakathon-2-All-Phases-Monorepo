# MCP Tools Specification: Task Management API

**Created**: 2025-12-29
**Status**: Draft
**Version**: 1.0.0
**Related Feature**: `specs/features/chatbot.md`

## Overview

This document defines the Model Context Protocol (MCP) tools exposed by the backend MCP server for task management operations. All tools require `user_id` to enforce user data isolation per the project's Stateless Architecture principle.

## Database Schema

### Task Table

```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'cancelled')),
    due_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT unique_user_task UNIQUE (user_id, title)
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_status ON tasks(status);
```

### Conversation Table

```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_user_conversation FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
```

### Message Table

```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    tool_calls JSONB,
    tool_results JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_conversation FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
```

## Tool Definitions

---

### Tool: add_task

Add a new task for the authenticated user.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "format": "uuid",
      "description": "The user's unique identifier (UUID)"
    },
    "title": {
      "type": "string",
      "minLength": 1,
      "maxLength": 500,
      "description": "The task title/description"
    },
    "description": {
      "type": "string",
      "maxLength": 5000,
      "description": "Optional detailed description"
    },
    "due_date": {
      "type": "string",
      "format": "date-time",
      "description": "Optional due date in ISO 8601 format"
    }
  },
  "required": ["user_id", "title"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "success": { "type": "boolean" },
    "task": {
      "type": "object",
      "properties": {
        "id": { "type": "integer" },
        "user_id": { "type": "string" },
        "title": { "type": "string" },
        "description": { "type": "string", "nullable": true },
        "status": { "type": "string" },
        "due_date": { "type": "string", "format": "date-time", "nullable": true },
        "created_at": { "type": "string", "format": "date-time" }
      }
    }
  }
}
```

**Errors**:
| Code | Condition |
|------|-----------|
| 400 | Missing required fields or invalid data |
| 401 | Invalid or missing user_id |
| 409 | Duplicate task title for this user |
| 500 | Database error |

**Examples**:
```json
// Request
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "due_date": "2025-12-30T18:00:00Z"
}

// Response
{
  "success": true,
  "task": {
    "id": 42,
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "status": "pending",
    "due_date": "2025-12-30T18:00:00Z",
    "created_at": "2025-12-29T10:00:00Z"
  }
}
```

---

### Tool: list_tasks

List tasks for the authenticated user with optional filtering.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "format": "uuid",
      "description": "The user's unique identifier (UUID)"
    },
    "status": {
      "type": "string",
      "enum": ["pending", "completed", "cancelled", "all"],
      "description": "Filter by task status (default: all)"
    },
    "limit": {
      "type": "integer",
      "minimum": 1,
      "maximum": 100,
      "default": 50,
      "description": "Maximum number of tasks to return"
    },
    "offset": {
      "type": "integer",
      "minimum": 0,
      "default": 0,
      "description": "Number of tasks to skip for pagination"
    }
  },
  "required": ["user_id"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "success": { "type": "boolean" },
    "tasks": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "integer" },
          "user_id": { "type": "string" },
          "title": { "type": "string" },
          "description": { "type": "string", "nullable": true },
          "status": { "type": "string" },
          "due_date": { "type": "string", "format": "date-time", "nullable": true },
          "created_at": { "type": "string", "format": "date-time" },
          "updated_at": { "type": "string", "format": "date-time" }
        }
      }
    },
    "total": { "type": "integer" },
    "limit": { "type": "integer" },
    "offset": { "type": "integer" }
  }
}
```

**Errors**:
| Code | Condition |
|------|-----------|
| 400 | Invalid status value |
| 401 | Invalid or missing user_id |
| 500 | Database error |

**Examples**:
```json
// Request - List pending tasks
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "limit": 10
}

// Response
{
  "success": true,
  "tasks": [
    {
      "id": 42,
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "status": "pending",
      "due_date": "2025-12-30T18:00:00Z",
      "created_at": "2025-12-29T10:00:00Z",
      "updated_at": "2025-12-29T10:00:00Z"
    }
  ],
  "total": 1,
  "limit": 10,
  "offset": 0
}
```

---

### Tool: complete_task

Mark a task as completed.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "format": "uuid",
      "description": "The user's unique identifier (UUID)"
    },
    "task_id": {
      "type": "integer",
      "description": "The task ID to complete"
    }
  },
  "required": ["user_id", "task_id"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "success": { "type": "boolean" },
    "task": {
      "type": "object",
      "properties": {
        "id": { "type": "integer" },
        "user_id": { "type": "string" },
        "title": { "type": "string" },
        "status": { "type": "string" },
        "updated_at": { "type": "string", "format": "date-time" }
      }
    },
    "message": { "type": "string" }
  }
}
```

**Errors**:
| Code | Condition |
|------|-----------|
| 400 | Missing required fields |
| 401 | Invalid or missing user_id |
| 404 | Task not found or doesn't belong to user |
| 409 | Task already completed |
| 500 | Database error |

**Examples**:
```json
// Request
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_id": 42
}

// Response
{
  "success": true,
  "task": {
    "id": 42,
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Buy groceries",
    "status": "completed",
    "updated_at": "2025-12-29T11:00:00Z"
  },
  "message": "Task 'Buy groceries' marked as completed"
}
```

---

### Tool: update_task

Update task details.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "format": "uuid",
      "description": "The user's unique identifier (UUID)"
    },
    "task_id": {
      "type": "integer",
      "description": "The task ID to update"
    },
    "title": {
      "type": "string",
      "minLength": 1,
      "maxLength": 500,
      "description": "New task title (optional)"
    },
    "description": {
      "type": "string",
      "maxLength": 5000,
      "description": "New description (optional)"
    },
    "due_date": {
      "type": "string",
      "format": "date-time",
      "description": "New due date (optional, use null to clear)"
    }
  },
  "required": ["user_id", "task_id"],
  "additionalProperties": false
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "success": { "type": "boolean" },
    "task": {
      "type": "object",
      "properties": {
        "id": { "type": "integer" },
        "user_id": { "type": "string" },
        "title": { "type": "string" },
        "description": { "type": "string", "nullable": true },
        "status": { "type": "string" },
        "due_date": { "type": "string", "format": "date-time", "nullable": true },
        "updated_at": { "type": "string", "format": "date-time" }
      }
    },
    "message": { "type": "string" }
  }
}
```

**Errors**:
| Code | Condition |
|------|-----------|
| 400 | No valid update fields provided |
| 401 | Invalid or missing user_id |
| 404 | Task not found or doesn't belong to user |
| 409 | Duplicate task title for this user |
| 500 | Database error |

**Examples**:
```json
// Request - Update title
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_id": 42,
  "title": "Buy groceries and household items"
}

// Response
{
  "success": true,
  "task": {
    "id": 42,
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Buy groceries and household items",
    "description": "Milk, eggs, bread",
    "status": "pending",
    "due_date": "2025-12-30T18:00:00Z",
    "updated_at": "2025-12-29T12:00:00Z"
  },
  "message": "Task updated successfully"
}
```

---

### Tool: delete_task

Delete a task permanently.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "format": "uuid",
      "description": "The user's unique identifier (UUID)"
    },
    "task_id": {
      "type": "integer",
      "description": "The task ID to delete"
    }
  },
  "required": ["user_id", "task_id"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "success": { "type": "boolean" },
    "message": { "type": "string" }
  }
}
```

**Errors**:
| Code | Condition |
|------|-----------|
| 400 | Missing required fields |
| 401 | Invalid or missing user_id |
| 404 | Task not found or doesn't belong to user |
| 500 | Database error |

**Examples**:
```json
// Request
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_id": 42
}

// Response
{
  "success": true,
  "message": "Task deleted successfully"
}
```

---

## User Isolation Rules

All tools enforce strict user data isolation:

1. **Every tool requires `user_id` parameter** - No exceptions
2. **Database queries MUST include WHERE user_id = ?** - Prevents cross-user access
3. **Responses only include tasks belonging to the requesting user**
4. **Error messages never reveal existence of other users' data**

### Isolation Verification Queries

```python
# Example: Safe query pattern
async def get_task_by_id(user_id: str, task_id: int) -> Task | None:
    query = "SELECT * FROM tasks WHERE id = ? AND user_id = ?"
    return await db.fetchone(query, (task_id, user_id))
```

## Rate Limiting

| Operation | Limit |
|-----------|-------|
| Any tool call | 60 requests/minute/user |
| add_task | 30 requests/minute/user |
| list_tasks | 30 requests/minute/user |

## Audit Logging

All tool invocations are logged with:
- Timestamp
- user_id
- tool_name
- input parameters (sanitized)
- success/failure status
- execution time
