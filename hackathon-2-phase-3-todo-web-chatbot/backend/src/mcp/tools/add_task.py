# MCP Tool: add_task for Phase III Chatbot
# Task ID: T021 (from user stories, implemented early for foundation)
# Reference: specs/api/mcp-tools.md (add_task tool specification)
# Uses Official MCP SDK (FastMCP) for tool integration

from datetime import datetime
from typing import Optional, Any
from mcp.server.fastmcp import FastMCP

from ...db import Database

# Create FastMCP instance
mcp = FastMCP("chatbot-task-server")


@mcp.tool()
async def add_task_handler(
    user_id: str,
    title: str,
    description: Optional[str] = None,
    due_date: Optional[str] = None,
) -> dict:
    """
    Add a new task for the authenticated user.

    This handler is called by the MCP server when the agent invokes add_task.
    User isolation is enforced - the user_id parameter is mandatory.

    Args:
        user_id: The authenticated user's UUID (extracted from JWT)
        title: The task title/description
        description: Optional detailed description
        due_date: Optional due date in ISO 8601 format

    Returns:
        dict with success status and task data
    """
    # Validate inputs
    if not title or not title.strip():
        return {"success": False, "error": "Task title cannot be empty"}

    if not user_id:
        return {"success": False, "error": "User ID is required for task creation"}

    # Parse due_date if provided
    parsed_due_date: Optional[datetime] = None
    if due_date:
        try:
            parsed_due_date = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
        except ValueError:
            return {"success": False, "error": f"Invalid due_date format: {due_date}. Use ISO 8601 format."}

    # Create task via Database utility (enforces user isolation)
    db = Database()
    task = await db.create_task({
        "user_id": user_id,
        "title": title.strip(),
        "description": description.strip() if description else None,
        "due_date": parsed_due_date,
    })

    return {
        "success": True,
        "task": {
            "id": task.id,
            "user_id": task.user_id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "created_at": task.created_at.isoformat(),
        },
        "message": f"Task '{task.title}' created successfully"
    }
