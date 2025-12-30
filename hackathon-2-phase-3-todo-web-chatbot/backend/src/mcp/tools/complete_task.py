# MCP Tool: complete_task for Phase III Chatbot
# Task ID: T035 (from user stories, implemented early for foundation)
# Reference: specs/api/mcp-tools.md (complete_task tool specification)
# Uses Official MCP SDK (FastMCP) for tool integration

from mcp.server.fastmcp import FastMCP

from ...db import Database

# Create FastMCP instance
mcp = FastMCP("chatbot-task-server")


@mcp.tool()
async def complete_task_handler(
    user_id: str,
    task_id: int,
) -> dict:
    """
    Mark a task as completed.

    This handler is called by the MCP server when the agent invokes complete_task.
    User isolation is enforced - only tasks belonging to the user can be completed.

    Args:
        user_id: The authenticated user's UUID (extracted from JWT)
        task_id: The ID of the task to complete

    Returns:
        dict with success status and updated task data
    """
    # Validate inputs
    if not user_id:
        return {"success": False, "error": "User ID is required"}

    if not isinstance(task_id, int) or task_id <= 0:
        return {"success": False, "error": "Invalid task ID"}

    # Complete task via Database utility (enforces user isolation)
    db = Database()
    task = await db.update_task(user_id, task_id, status="completed")

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
            "status": task.status,
            "updated_at": task.updated_at.isoformat(),
        },
        "message": f"Task '{task.title}' marked as completed"
    }
