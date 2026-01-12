# MCP Tool: update_task for Phase III Chatbot
# Task ID: T039 (from user stories, implemented early for foundation)
# Reference: specs/api/mcp-tools.md (update_task tool specification)
# Uses Official MCP SDK (FastMCP) for tool integration

from datetime import datetime
from typing import Optional
from mcp.server.fastmcp import FastMCP

from ...db import Database

# Create FastMCP instance
mcp = FastMCP("chatbot-task-server")


@mcp.tool()
async def update_task_handler(
    user_id: str,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    due_date: Optional[str] = None,
) -> dict:
    """
    Update task details.

    This handler is called by the MCP server when the agent invokes update_task.
    User isolation is enforced - only tasks belonging to the user can be updated.

    Args:
        user_id: The authenticated user's UUID (extracted from JWT)
        task_id: The ID of the task to update
        title: New title (optional)
        description: New description (optional)
        due_date: New due date in ISO 8601 format (optional, use null to clear)

    Returns:
        dict with success status and updated task data
    """
    # Validate inputs
    if not user_id:
        return {"success": False, "error": "User ID is required"}

    if not isinstance(task_id, int) or task_id <= 0:
        return {"success": False, "error": "Invalid task ID"}

    # Check at least one update field is provided
    if title is None and description is None and due_date is None:
        return {"success": False, "error": "At least one of title, description, or due_date must be provided"}

    # Parse due_date if provided
    parsed_due_date: Optional[datetime] = None
    if due_date is not None:
        if due_date == "" or due_date.lower() == "null":
            # Clear the due date
            parsed_due_date = None
        else:
            try:
                parsed_due_date = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
            except ValueError:
                return {"success": False, "error": f"Invalid due_date format: {due_date}. Use ISO 8601 format."}

    # Build update dict with non-None values
    updates = {}
    if title is not None:
        if not title.strip():
            return {"success": False, "error": "Title cannot be empty"}
        updates["title"] = title.strip()
    if description is not None:
        updates["description"] = description.strip() if description.strip() else None
    if parsed_due_date is not None or due_date == "":
        updates["due_date"] = parsed_due_date

    # Update task via Database utility (enforces user isolation)
    db = Database()
    task = await db.update_task(user_id, task_id, **updates)

    if task is None:
        return {
            "success": False,
            "error": f"Task {task_id} not found or does not belong to you"
        }

    return {
        "success": True,
        "task": {
            "id": task.id,
            "user_id": task.user_id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "updated_at": task.updated_at.isoformat(),
        },
        "message": f"Task '{task.title}' updated successfully"
    }
