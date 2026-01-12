# MCP Server for Phase III Chatbot
# Task ID: T017
# Reference: specs/features/chatbot/plan.md (MCP Tools Integration)
# Reference: specs/api/mcp-tools.md (Tool specifications)
# Uses Official MCP SDK (FastMCP) for tool integrations

from typing import Optional
from mcp.server.fastmcp import FastMCP

from .tools import (
    add_task_handler,
    list_tasks_handler,
    complete_task_handler,
    update_task_handler,
    delete_task_handler,
)


class MCPServer:
    """
    MCP (Model Context Protocol) Server for task management.

    Exposes task CRUD operations as MCP tools that can be invoked by
    the OpenAI Agent. All tools enforce user isolation by requiring
    user_id parameter.

    Reference: specs/features/chatbot/plan.md - "MCP Tools Integration"
    """

    def __init__(self, user_id: str):
        """
        Initialize MCP server with user context.

        Args:
            user_id: The authenticated user's UUID for data isolation
        """
        self.user_id = user_id
        self._mcp = FastMCP("chatbot-task-server")
        self._register_tools()

    def _register_tools(self):
        """Register all task management tools with the MCP server."""
        # Add all tools to the FastMCP instance
        self._mcp.add_tool(add_task_handler)
        self._mcp.add_tool(list_tasks_handler)
        self._mcp.add_tool(complete_task_handler)
        self._mcp.add_tool(update_task_handler)
        self._mcp.add_tool(delete_task_handler)

    def get_tools(self):
        """
        Get all registered MCP tools.

        Returns:
            List of tool callables for agent integration
        """
        return [
            add_task_handler,
            list_tasks_handler,
            complete_task_handler,
            update_task_handler,
            delete_task_handler,
        ]

    @property
    def mcp(self) -> FastMCP:
        """Get the underlying FastMCP instance."""
        return self._mcp

    async def run(self):
        """Run the MCP server (for standalone mode)."""
        await self._mcp.run_stdio()
