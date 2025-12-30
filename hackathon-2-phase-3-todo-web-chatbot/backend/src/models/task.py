# Task SQLModel for Phase III Chatbot
# Task ID: T008
# Reference: specs/api/mcp-tools.md (Task Table schema)
# Reference: specs/features/chatbot/plan.md (SQLModel Definitions)

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Index


class ChatTask(SQLModel, table=True):
    """
    Task entity for Phase III Chatbot (renamed to avoid collision with Phase I/II Task).
    Supports stateless request cycle by persisting all task state to database.
    User isolation enforced via user_id field - all queries MUST filter by user_id.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(
        index=True,
        description="User UUID for data isolation - all operations require user_id filter"
    )
    title: str = Field(
        max_length=500,
        description="Task title/description"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Optional detailed task description"
    )
    status: str = Field(
        default="pending",
        max_length=20,
        description="Task status: pending, completed, or cancelled"
    )
    due_date: Optional[datetime] = Field(
        default=None,
        description="Optional due date in ISO 8601 format"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when task was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when task was last updated"
    )

    # Indexes for query performance
    __tablename__ = "tasks"

    class Config:
        indexes = [
            Index("idx_tasks_user_id", "user_id"),
            Index("idx_tasks_status", "status"),
        ]


# Pydantic schemas for task operations (used by MCP tools)
class TaskCreate(SQLModel):
    """Schema for creating a new task."""
    user_id: str
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None


class TaskUpdate(SQLModel):
    """Schema for updating an existing task."""
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    status: Optional[str] = None


class TaskResponse(SQLModel):
    """Schema for task response."""
    id: int
    user_id: str
    title: str
    description: Optional[str]
    status: str
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
