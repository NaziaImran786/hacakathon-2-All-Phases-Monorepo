# MCP Tool: list_tasks for Phase III Chatbot
# Task ID: T031 (from user stories, implemented early for foundation)
# Reference: specs/api/mcp-tools.md (list_tasks tool specification)
# Uses Official MCP SDK (FastMCP) for tool integration

from typing import Optional
from mcp.server.fastmcp import FastMCP

from ...db import Database

# Create FastMCP instance
mcp = FastMCP("chatbot-task-server")


@mcp.tool()
async def list_tasks_handler(
    user_id: str,
    status: str = "all",
    limit: int = 50,
    offset: int = 0,
) -> dict:
    """
    List tasks for the authenticated user with optional filtering.

    This handler is called by the MCP server when the agent invokes list_tasks.
    User isolation is enforced - queries are filtered by user_id.

    Args:
        user_id: The authenticated user's UUID (extracted from JWT)
        status: Filter by task status - "pending", "completed", "cancelled", or "all"
        limit: Maximum number of tasks to return (default: 50)
        offset: Number of tasks to skip for pagination (default: 0)

    Returns:
        dict with success status and list of tasks
    """
    # Validate inputs
    if not user_id:
        return {"success": False, "error": "User ID is required to list tasks"}

    valid_statuses = ["pending", "completed", "cancelled", "all"]
    if status not in valid_statuses:
        return {"success": False, "error": f"Invalid status: {status}. Must be one of: {valid_statuses}"}

    if limit < 1 or limit > 100:
        return {"success": False, "error": "Limit must be between 1 and 100"}

    if offset < 0:
        return {"success": False, "error": "Offset must be non-negative"}

    # Fetch tasks via Database utility (enforces user isolation)
    db = Database()
    tasks = await db.get_tasks(user_id, status=status if status != "all" else None)

    # Apply pagination
    paginated_tasks = tasks[offset:offset + limit]

    return {
        "success": True,
        "tasks": [
            {
                "id": task.id,
                "user_id": task.user_id,
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
            }
            for task in paginated_tasks
        ],
        "total": len(tasks),
        "limit": limit,
        "offset": offset,
        "message": f"Found {len(tasks)} task(s)" + (f" ({status})" if status != "all" else "")
    }
