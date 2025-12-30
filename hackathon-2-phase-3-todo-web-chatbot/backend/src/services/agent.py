# Agent Service for Phase III Chatbot
# Task ID: T020
# Reference: specs/features/chatbot/plan.md (OpenAI Agents SDK Integration)
# Reference: specs/api/mcp-tools.md (Tool specifications)
# Uses OpenAI Agents SDK for agent orchestration

import os
import json
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

from agents import Agent, Runner, function_tool
from openai import AsyncOpenAI
from ..db import Database

# Initialize OpenAI client with API key from environment
# This is required for the OpenAI Agents SDK to work
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required for Phase III chatbot")

# Set OpenAI API key for the agents SDK
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


@dataclass
class AgentResult:
    """Result from agent execution."""
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_results: Optional[List[Dict[str, Any]]] = None
    tasks: Optional[List[Dict[str, Any]]] = None


# Tool implementation functions (not decorated - called by AgentService)
# These functions are wrapped by the agent to inject user_id automatically


async def _add_task_impl(
    user_id: str,
    title: str,
    description: Optional[str] = None,
    due_date: Optional[str] = None,
) -> dict:
    """Add a new task implementation."""
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


async def _list_tasks_impl(
    user_id: str,
    status: str = "all",
    limit: int = 50,
    offset: int = 0,
) -> dict:
    """List tasks implementation."""
    if not user_id:
        return {"success": False, "error": "User ID is required to list tasks"}

    valid_statuses = ["pending", "completed", "cancelled", "all"]
    if status not in valid_statuses:
        return {"success": False, "error": f"Invalid status: {status}. Must be one of: {valid_statuses}"}

    if limit < 1 or limit > 100:
        return {"success": False, "error": "Limit must be between 1 and 100"}

    if offset < 0:
        return {"success": False, "error": "Offset must be non-negative"}

    db = Database()
    tasks = await db.get_tasks(user_id, status=status if status != "all" else None)

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


async def _complete_task_impl(user_id: str, task_id: int) -> dict:
    """Complete task implementation."""
    if not user_id:
        return {"success": False, "error": "User ID is required"}

    if not isinstance(task_id, int) or task_id <= 0:
        return {"success": False, "error": "Invalid task ID"}

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


async def _update_task_impl(
    user_id: str,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    due_date: Optional[str] = None,
) -> dict:
    """Update task implementation."""
    if not user_id:
        return {"success": False, "error": "User ID is required"}

    if not isinstance(task_id, int) or task_id <= 0:
        return {"success": False, "error": "Invalid task ID"}

    if title is None and description is None and due_date is None:
        return {"success": False, "error": "At least one of title, description, or due_date must be provided"}

    parsed_due_date: Optional[datetime] = None
    if due_date is not None:
        if due_date == "" or due_date.lower() == "null":
            parsed_due_date = None
        else:
            try:
                parsed_due_date = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
            except ValueError:
                return {"success": False, "error": f"Invalid due_date format: {due_date}. Use ISO 8601 format."}

    updates = {}
    if title is not None:
        if not title.strip():
            return {"success": False, "error": "Title cannot be empty"}
        updates["title"] = title.strip()
    if description is not None:
        updates["description"] = description.strip() if description.strip() else None
    if parsed_due_date is not None or due_date == "":
        updates["due_date"] = parsed_due_date

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


async def _delete_task_impl(user_id: str, task_id: int) -> dict:
    """Delete task implementation."""
    if not user_id:
        return {"success": False, "error": "User ID is required"}

    if not isinstance(task_id, int) or task_id <= 0:
        return {"success": False, "error": "Invalid task ID"}

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


def create_user_tools(user_id: str):
    """
    Create function tools with user_id pre-bound.

    The OpenAI Agents SDK calls tools as standalone functions.
    This factory creates tools that have the user_id already bound,
    so the LLM doesn't need to (and can't) specify it.

    Args:
        user_id: The authenticated user's username/ID to bind to tools

    Returns:
        List of function tools with user_id pre-bound
    """

    @function_tool
    async def add_task(
        title: str,
        description: Optional[str] = None,
        due_date: Optional[str] = None,
    ) -> dict:
        """
        Add a new task.

        Args:
            title: The task title/description
            description: Optional detailed description
            due_date: Optional due date in ISO 8601 format

        Returns:
            dict with success status and task data
        """
        return await _add_task_impl(user_id, title, description, due_date)

    @function_tool
    async def list_tasks(
        status: str = "all",
        limit: int = 50,
        offset: int = 0,
    ) -> dict:
        """
        List your tasks with optional filtering.

        Args:
            status: Filter by task status - "pending", "completed", "cancelled", or "all"
            limit: Maximum number of tasks to return (default: 50)
            offset: Number of tasks to skip for pagination (default: 0)

        Returns:
            dict with success status and list of tasks
        """
        return await _list_tasks_impl(user_id, status, limit, offset)

    @function_tool
    async def complete_task(task_id: int) -> dict:
        """
        Mark a task as completed.

        Args:
            task_id: The ID of the task to complete

        Returns:
            dict with success status and updated task data
        """
        return await _complete_task_impl(user_id, task_id)

    @function_tool
    async def update_task(
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        due_date: Optional[str] = None,
    ) -> dict:
        """
        Update task details.

        Args:
            task_id: The ID of the task to update
            title: New title (optional)
            description: New description (optional)
            due_date: New due date in ISO 8601 format (optional, use null to clear)

        Returns:
            dict with success status and updated task data
        """
        return await _update_task_impl(user_id, task_id, title, description, due_date)

    @function_tool
    async def delete_task(task_id: int) -> dict:
        """
        Delete a task permanently.

        Args:
            task_id: The ID of the task to delete

        Returns:
            dict with success status
        """
        return await _delete_task_impl(user_id, task_id)

    return [add_task, list_tasks, complete_task, update_task, delete_task]


class AgentService:
    """
    Agent service using OpenAI Agents SDK.

    Orchestrates the AI agent that processes natural language commands
    and invokes function tools for task management. All operations are
    scoped to the authenticated user via user_id.

    STATELESS ARCHITECTURE:
    - Fetches conversation history from Neon DB at the start of every request
    - Saves agent response back to messages table after processing
    - No in-memory state is retained between requests

    Reference: specs/features/chatbot/plan.md - "Tool Registration with Agent"
    """

    def __init__(self, user_id: str):
        """
        Initialize agent service with user context.

        Args:
            user_id: The authenticated user's UUID for data isolation
        """
        self.user_id = user_id
        self.model = "gpt-4o"
        self.db = Database()

    def get_system_prompt(self) -> str:
        """
        Get the system prompt that defines the agent's behavior.

        Returns:
            str: System prompt with agent instructions
        """
        return f"""You are a helpful task management assistant for a todo list application.

Your capabilities:
- Add tasks: Use add_task when user wants to create a new task
- List tasks: Use list_tasks when user asks about their tasks
- Complete tasks: Use complete_task when user indicates a task is done
- Update tasks: Use update_task when user wants to modify a task
- Delete tasks: Use delete_task when user wants to remove a task

Guidelines:
1. Always confirm actions with the user before executing them
2. If a command is unclear, ask for clarification
3. Present task lists in a clear, organized format
4. Use natural language in your responses
5. When listing tasks, show the task ID and title

User context:
- Your user ID is: {self.user_id}
- All task operations are automatically scoped to this user
- You don't need to ask for user_id - it's provided automatically

Remember: You have access to tools for managing tasks. Use them appropriately based on the user's intent."""

    async def run_with_history(
        self,
        conversation_id: int,
        user_message: str
    ) -> AgentResult:
        """
        Run the agent with conversation history from database.

        STATELESS: Fetches history from DB, processes, saves response back.

        Args:
            conversation_id: The conversation ID to load history from
            user_message: The new user message to process

        Returns:
            AgentResult: Agent's response and any tool calls/results
        """
        # 1. Fetch conversation history from Neon DB (stateless)
        db_messages = await self.db.get_messages(conversation_id)

        # 2. Convert DB messages to agent format
        messages = []
        for msg in db_messages:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })

        # 3. Add the new user message
        messages.append({"role": "user", "content": user_message})

        # 4. Save user message to DB immediately
        await self.db.add_message(
            conversation_id=conversation_id,
            role="user",
            content=user_message
        )

        # 5. Run agent
        result = await self.run(messages)

        # 6. Save agent response to DB (stateless - persist everything)
        await self.db.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=result.content,
            tool_calls=json.dumps(result.tool_calls) if result.tool_calls else None,
            tool_results=json.dumps(result.tool_results) if result.tool_results else None
        )

        return result

    async def run(self, messages: List[Dict[str, str]]) -> AgentResult:
        """
        Run the agent with the given message history.

        Args:
            messages: List of message dicts with 'role' and 'content' keys

        Returns:
            AgentResult: Agent's response and any tool calls/results
        """
        # Create user-scoped tools with user_id pre-bound
        # This ensures all task operations are tied to the authenticated user
        user_tools = create_user_tools(self.user_id)

        # Create agent with function tools (MCP tools for task management)
        agent = Agent(
            name="TaskManager",
            instructions=self.get_system_prompt(),
            model=self.model,
            tools=user_tools,
        )

        # Combine messages into a single input string
        input_text = self._format_messages(messages)

        # Run agent with message history
        result = await Runner.run(agent, input_text)

        # Extract tool information if any tools were called
        tool_calls = None
        tool_results = None
        tasks = None

        if hasattr(result, 'tool_calls') and result.tool_calls:
            tool_calls = [
                {
                    "name": tc.name,
                    "arguments": tc.arguments
                }
                for tc in result.tool_calls
            ]

        if hasattr(result, 'tool_results') and result.tool_results:
            tool_results = [
                {
                    "tool": tr.tool,
                    "result": tr.result
                }
                for tr in result.tool_results
            ]

            # Extract task data from tool results
            tasks = []
            for tr in result.tool_results:
                if tr.tool in ["add_task", "complete_task", "update_task", "delete_task"]:
                    if hasattr(tr, 'result') and tr.result:
                        result_data = tr.result
                        if isinstance(result_data, dict) and result_data.get("success"):
                            if "task" in result_data:
                                tasks.append(result_data["task"])

        return AgentResult(
            content=result.final_output if hasattr(result, 'final_output') else str(result),
            tool_calls=tool_calls,
            tool_results=tool_results,
            tasks=tasks if tasks else None,
        )

    def _format_messages(self, messages: List[Dict[str, str]]) -> str:
        """Format messages for the agent input."""
        formatted = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            formatted.append(f"[{role}]: {content}")
        return "\n".join(formatted)

    async def run_single(self, user_message: str) -> AgentResult:
        """
        Run the agent with a single user message (no history).

        Convenience method for simple interactions.

        Args:
            user_message: The user's message

        Returns:
            AgentResult: Agent's response
        """
        messages = [{"role": "user", "content": user_message}]
        return await self.run(messages)
