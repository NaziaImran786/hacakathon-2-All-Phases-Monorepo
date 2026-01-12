import os
import json
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession

from agents import Agent, Runner, function_tool
from openai import AsyncOpenAI

# Import the Database utility class
from ..db.database import Database

@dataclass
class AgentResult:
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_results: Optional[List[Dict[str, Any]]] = None
    tasks: Optional[List[Dict[str, Any]]] = None

class AgentService:
    def __init__(self, user_id: str, session: AsyncSession):
        # user_id is now the username string
        self.user_id = user_id 
        self.db = Database(session)
        self.model = "gpt-4o"

    # --- Tool Implementations (now using self.db) ---

    async def _add_task_impl(self, title: str, description: Optional[str] = None, due_date: Optional[str] = None) -> dict:
        try:
            task_data = {
                "title": title.strip(),
                "description": description,
                "user_id": self.user_id # Pass username
            }
            # The Database class expects a dictionary and returns a TaskResult object
            task_result = await self.db.create_task(task_data)
            return {"success": True, "task": {"id": task_result.id, "title": task_result.title}}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _list_tasks_impl(self) -> dict:
        try:
            # The Database class returns a list of TaskResult objects
            tasks = await self.db.get_tasks(self.user_id)
            return {"success": True, "tasks": [{"id": t.id, "title": t.title, "status": t.status} for t in tasks]}
        except Exception as e:
            return {"success": False, "error": str(e)}
        
        
    # --- NAYA TOOL IMPLEMENTATION ---
    async def _update_task_status_impl(self, task_id: int, status: str) -> dict:
        """Helper to call database update_task"""
        try:
            # Database class has update_task(user_id, task_id, **updates)
            # 'completed' status logically maps to status='completed'
            result = await self.db.update_task(self.user_id, task_id, status=status)
            if result:
                return {"success": True, "message": f"Task {task_id} updated to {status}"}
            return {"success": False, "message": "Task not found or access denied"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # --- Agent Execution ---

    async def run(self, messages: List[Dict[str, str]]) -> AgentResult:
        @function_tool
        async def add_task(title: str, description: Optional[str] = None) -> dict:
            """Add a new task to the user's task list."""
            return await self._add_task_impl(title, description)

        @function_tool
        async def list_tasks() -> dict:
            """List all of the user's tasks."""
            return await self._list_tasks_impl()
        
        # --- YE NAYA TOOL HAI JO AI USE KAREGA ---
        @function_tool
        async def mark_task_complete(task_id: int) -> dict:
            """Mark a specific task as completed using its ID."""
            return await self._update_task_status_impl(task_id, "completed")

        agent = Agent(
            name="TaskManager",
            instructions=f"You are a helpful task management assistant for user '{self.user_id}'.",
            model=self.model,
            tools=[add_task, list_tasks, mark_task_complete],
        )

        input_text = "\n".join([f"[{m['role']}]: {m['content']}" for m in messages])
        result = await Runner.run(agent, input_text)

        # This part depends on the 'agents' library structure, assuming it's similar
        # Fetch tasks again to reflect any changes made by the agent
        task_list_result = await self._list_tasks_impl()
        final_tasks = task_list_result.get("tasks") if task_list_result.get("success") else []

        return AgentResult(
            content=getattr(result, 'final_output', str(result)),
            tool_calls=getattr(result, 'tool_calls', []),
            tool_results=getattr(result, 'tool_results', []),
            tasks=final_tasks
        )
