# Database session management for Phase III Chatbot
# Task ID: T012
# Reference: specs/features/chatbot/plan.md (Stateless Architecture)
# Reference: specs/api/mcp-tools.md (Database Schema)

from __future__ import annotations

import os
from typing import AsyncGenerator, TYPE_CHECKING, Any
from sqlmodel import SQLModel, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import NullPool
from sqlalchemy import asc
from datetime import datetime

# Import models for type hints and usage
if TYPE_CHECKING:
    from ..models import ChatTask, Conversation, Message


# Database URL from environment - Neon Serverless PostgreSQL
# Use DATABASE_URL_ASYNC for async operations (Phase III)
# Must use postgresql+psycopg:// prefix for psycopg v3 async driver
DATABASE_URL = os.getenv(
    "DATABASE_URL_ASYNC",
    os.getenv("DATABASE_URL", "postgresql+psycopg://user:password@localhost/tododb")
)

# Create async SQLModel engine for stateless architecture
# All state is persisted to database - no in-memory session storage
#
# Connection pooling settings for Neon Serverless PostgreSQL:
# - pool_pre_ping=True: Test connections before use to handle SSL closures
# - poolclass=NullPool: Disable connection pooling for serverless (each request = new connection)
#   This prevents "SSL connection has been closed unexpectedly" errors with Neon
# - connect_args: Pass SSL mode to psycopg driver
# - echo=False: Disable SQL logging in production
async_engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    poolclass=NullPool,  # Essential for Neon serverless - no persistent connections
    connect_args={
        "sslmode": "require",  # Ensure SSL for Neon connections
    },
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides an async database session.
    Follows stateless architecture - each request gets its own session.
    Session is closed after request completes.
    """
    async with AsyncSession(async_engine) as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_db_and_tables():
    """
    Create all database tables based on SQLModel metadata.
    Should be called on application startup.
    """
    from ..models import ChatTask, Conversation, Message

    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


class Database:
    """
    Database utility class for MCP tool handlers.
    Provides simple CRUD operations with user isolation.

    IMPORTANT: Uses Phase I/II Task model (from models.py) to ensure
    AI-created tasks appear in the manual dashboard. The Phase I/II
    model uses owner_id (int) as foreign key to User table, while
    Phase III originally used user_id (string). This class now bridges
    the gap by looking up user ID from username.
    """

    def __init__(self):
        self.engine = async_engine

    async def _get_user_id_from_username(self, username: str) -> int | None:
        """
        Look up the numeric user ID from username.
        Phase I/II auth stores username in JWT sub claim.
        """
        from sqlmodel import Session as SyncSession
        from models import User, engine as sync_engine

        with SyncSession(sync_engine) as session:
            query = select(User).where(User.username == username)
            result = session.exec(query)
            user = result.first()
            return user.id if user else None

    async def create_task(self, task_data: dict) -> Any:
        """
        Create a new task using Phase I/II Task model.
        Converts username to owner_id for proper user isolation.
        """
        from sqlmodel import Session as SyncSession
        from models import Task, engine as sync_engine

        # Extract username and convert to owner_id
        username = task_data.pop("user_id", None)
        owner_id = await self._get_user_id_from_username(username) if username else None

        if not owner_id:
            raise ValueError(f"User not found: {username}")

        # Create task with Phase I/II model
        task = Task(
            title=task_data.get("title", ""),
            description=task_data.get("description"),
            completed=False,
            owner_id=owner_id,
        )

        with SyncSession(sync_engine) as session:
            session.add(task)
            session.commit()
            session.refresh(task)

            # Return a compatible object with expected attributes
            return TaskResult(
                id=task.id,
                user_id=username,  # Return original username for API response
                title=task.title,
                description=task.description,
                status="pending" if not task.completed else "completed",
                due_date=None,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

    async def get_tasks(self, user_id: str, status: str = None) -> list[Any]:
        """
        Get tasks for user using Phase I/II Task model.
        Filters by owner_id (looked up from username).
        """
        from sqlmodel import Session as SyncSession
        from models import Task, engine as sync_engine

        # Convert username to owner_id
        owner_id = await self._get_user_id_from_username(user_id)
        if not owner_id:
            return []

        with SyncSession(sync_engine) as session:
            query = select(Task).where(Task.owner_id == owner_id)

            # Map status filter to completed boolean
            if status == "completed":
                query = query.where(Task.completed == True)
            elif status == "pending":
                query = query.where(Task.completed == False)
            # "all" or None = no filter

            result = session.exec(query)
            tasks = result.all()

            # Convert to expected format
            return [
                TaskResult(
                    id=task.id,
                    user_id=user_id,
                    title=task.title,
                    description=task.description,
                    status="completed" if task.completed else "pending",
                    due_date=None,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                for task in tasks
            ]

    async def get_task_by_id(self, user_id: str, task_id: int) -> Any | None:
        """Get a single task by ID with user isolation."""
        from sqlmodel import Session as SyncSession
        from models import Task, engine as sync_engine

        owner_id = await self._get_user_id_from_username(user_id)
        if not owner_id:
            return None

        with SyncSession(sync_engine) as session:
            task = session.get(Task, task_id)
            if not task or task.owner_id != owner_id:
                return None

            return TaskResult(
                id=task.id,
                user_id=user_id,
                title=task.title,
                description=task.description,
                status="completed" if task.completed else "pending",
                due_date=None,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

    async def update_task(self, user_id: str, task_id: int, **updates) -> Any | None:
        """Update a task with user isolation using Phase I/II model."""
        from sqlmodel import Session as SyncSession
        from models import Task, engine as sync_engine

        owner_id = await self._get_user_id_from_username(user_id)
        if not owner_id:
            return None

        with SyncSession(sync_engine) as session:
            task = session.get(Task, task_id)
            if not task or task.owner_id != owner_id:
                return None

            # Apply updates - map status to completed boolean
            if "status" in updates:
                task.completed = updates["status"] == "completed"
            if "title" in updates:
                task.title = updates["title"]
            if "description" in updates:
                task.description = updates["description"]

            session.add(task)
            session.commit()
            session.refresh(task)

            return TaskResult(
                id=task.id,
                user_id=user_id,
                title=task.title,
                description=task.description,
                status="completed" if task.completed else "pending",
                due_date=None,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

    async def delete_task(self, user_id: str, task_id: int) -> bool:
        """Delete a task with user isolation using Phase I/II model."""
        from sqlmodel import Session as SyncSession
        from models import Task, engine as sync_engine

        owner_id = await self._get_user_id_from_username(user_id)
        if not owner_id:
            return False

        with SyncSession(sync_engine) as session:
            task = session.get(Task, task_id)
            if not task or task.owner_id != owner_id:
                return False

            session.delete(task)
            session.commit()
            return True

    async def create_conversation(self, user_id: str, title: str = None) -> Conversation:
        """Create a new conversation with user isolation."""
        from ..models import Conversation as ConversationModel
        conversation = ConversationModel(user_id=user_id, title=title)
        async with AsyncSession(self.engine) as session:
            session.add(conversation)
            await session.commit()
            await session.refresh(conversation)
            return conversation

    async def get_conversation(self, user_id: str, conversation_id: int) -> Conversation | None:
        """Get a conversation with user isolation."""
        from ..models import Conversation as ConversationModel
        async with AsyncSession(self.engine) as session:
            query = select(ConversationModel).where(
                ConversationModel.id == conversation_id,
                ConversationModel.user_id == user_id
            )
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def add_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        tool_calls: str = None,
        tool_results: str = None
    ) -> Message:
        """Add a message to a conversation."""
        from ..models import Message as MessageModel
        message = MessageModel(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tool_calls=tool_calls,
            tool_results=tool_results
        )
        async with AsyncSession(self.engine) as session:
            session.add(message)
            await session.commit()
            await session.refresh(message)
            return message

    async def get_messages(self, conversation_id: int) -> list[Message]:
        """Get all messages for a conversation ordered by creation time."""
        from ..models import Message as MessageModel
        async with AsyncSession(self.engine) as session:
            query = (
                select(MessageModel)
                .where(MessageModel.conversation_id == conversation_id)
                .order_by(asc(MessageModel.created_at))
            )
            result = await session.execute(query)
            return result.scalars().all()


class TaskResult:
    """
    Simple class to hold task data in a format compatible with agent tools.
    Bridges Phase I/II Task model with Phase III API expectations.
    """
    def __init__(self, id: int, user_id: str, title: str, description: str | None,
                 status: str, due_date: datetime | None, created_at: datetime,
                 updated_at: datetime):
        self.id = id
        self.user_id = user_id
        self.title = title
        self.description = description
        self.status = status
        self.due_date = due_date
        self.created_at = created_at
        self.updated_at = updated_at
