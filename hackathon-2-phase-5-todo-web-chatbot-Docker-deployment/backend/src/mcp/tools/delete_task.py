# MCP Tool: delete_task for Phase III Chatbot
# Task ID: T043 (from user stories, implemented early for foundation)
# Reference: specs/api/mcp-tools.md (delete_task tool specification)
# Uses Official MCP SDK (FastMCP) for tool integration

from mcp.server.fastmcp import FastMCP

from ...db import Database

# Create FastMCP instance
mcp = FastMCP("chatbot-task-server")


@mcp.tool()
async def delete_task_handler(
    user_id: str,
    task_id: int,
) -> dict:
    """
    Delete a task permanently.

    This handler is called by the MCP server when the agent invokes delete_task.
    User isolation is enforced - only tasks belonging to the user can be deleted.

    Args:
        user_id: The authenticated user's UUID (extracted from JWT)
        task_id: The ID of the task to delete

    Returns:
        dict with success status
    """
    # Validate inputs
    if not user_id:
        return {"success": False, "error": "User ID is required"}

    if not isinstance(task_id, int) or task_id <= 0:
        return {"success": False, "error": "Invalid task ID"}

    # Delete task via Database utility (enforces user isolation)
    db = Database()
    deleted = await db.delete_task(user_id, task_id)

    if not deleted:
        return {
            "success": False,
            "error": f"Task {task_id} not found or does not belong to you"
        }

    return {
        "success": True,
        "message": f"Task {task_id} deleted successfully"
    }
