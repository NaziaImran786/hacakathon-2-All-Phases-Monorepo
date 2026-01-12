import ssl
import certifi
import os
import json
from datetime import datetime
from typing import AsyncGenerator, Any, Optional
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, asc
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession as SQLAsyncSession

# Models import
from models import User, Task
from models import Conversation, Message

load_dotenv()

# Database URL adjustment for asyncpg
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    # 1. Driver change karein
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    
    # 2. Saare extra parameters (? ke baad wala sab kuch) saaf karein
    # Is se 'neondb&channel_binding=require' jese masle khatam ho jayengy
    if "?" in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.split("?")[0]

# SSL for Neon
# ssl_context = ssl.create_default_context(cafile=certifi.where())
# ssl_context.check_hostname = False
# ssl_context.verify_mode = ssl.CERT_NONE

# Engine Setup
async_engine = create_async_engine(
    DATABASE_URL, 
    echo=False, 
    connect_args={
        "ssl": True,        
        "server_settings": {
            "jit": "off",}
    },
    
    # In settings ka izafa karein taake connection drops handle ho saken
    pool_pre_ping=True,       # Har request se pehle connection check karega
    pool_recycle=300,         # 5 minutes ke baad connections recycle karega
    pool_size=5,              # Connections ki tadaad
    max_overflow=10           # Zarurat par extra connections
)

async_session_maker = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

# Database Initialization
async def init_models():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

# FastAPI Dependency
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# TaskResult Helper
class TaskResult:
    def __init__(self, id: int, user_id: str, title: str, description: str | None = None,
                 status: str = "pending", due_date: datetime | None = None, 
                 created_at: datetime | None = None,
                 updated_at: datetime | None = None):
        self.id = id
        self.user_id = user_id
        self.title = title
        self.description = description
        self.status = status
        self.due_date = due_date
        # Agar timestamps nahi hain, toh current time de dein
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

# The Missing Utility Class for Chatbot & Services
class Database:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _get_user_id_from_username(self, username: str) -> Optional[int]:
        """Look up numeric ID from username string ('zoni' -> 18)"""
        query = select(User).where(User.username == username)
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()
        return user.id if user else None

    async def create_task(self, task_data: dict) -> Any:
        username = task_data.pop("user_id", None)
        owner_id = await self._get_user_id_from_username(username)
        
        if not owner_id:
            raise ValueError(f"User not found: {username}")

        task = Task(
            title=task_data.get("title", ""),
            description=task_data.get("description"),
            completed=False,
            owner_id=owner_id,
        )
        self.session.add(task)
        await self.session.flush() # Get ID without full commit
        
        return TaskResult(
            id=task.id, user_id=username, title=task.title,
            description=task.description, status="pending",
            due_date=None, created_at=datetime.utcnow(), updated_at=datetime.utcnow()
        )

    async def get_tasks(self, user_id: str, status: str = None) -> list[Any]:
        owner_id = await self._get_user_id_from_username(user_id)
        if not owner_id: return []

        query = select(Task).where(Task.owner_id == owner_id)
        if status == "completed": query = query.where(Task.completed == True)
        elif status == "pending": query = query.where(Task.completed == False)

        result = await self.session.execute(query)
        tasks = result.scalars().all()

        return [TaskResult(
            id=t.id, user_id=user_id, title=t.title, description=t.description,
            status="completed" if t.completed else "pending",
            due_date=None, created_at=datetime.utcnow(), updated_at=datetime.utcnow()
        ) for t in tasks]

    async def update_task(self, user_id: str, task_id: int, **updates) -> Any | None:
        owner_id = await self._get_user_id_from_username(user_id)
        if not owner_id: return None

        task = await self.session.get(Task, task_id)
        if not task or task.owner_id != owner_id: return None

        if "status" in updates: task.completed = (updates["status"] == "completed")
        if "title" in updates: task.title = updates["title"]
        if "description" in updates: task.description = updates["description"]

        self.session.add(task)
        return TaskResult(
            id=task.id, user_id=user_id, title=task.title, description=task.description,
            status="completed" if task.completed else "pending",
            due_date=None, created_at=datetime.utcnow(), updated_at=datetime.utcnow()
        )

    async def delete_task(self, user_id: str, task_id: int) -> bool:
        owner_id = await self._get_user_id_from_username(user_id)
        if not owner_id: return False
        task = await self.session.get(Task, task_id)
        if not task or task.owner_id != owner_id: return False
        await self.session.delete(task)
        return True


























# import ssl
# import certifi
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
# from sqlmodel import SQLModel
# import os
# from dotenv import load_dotenv
# from typing import AsyncGenerator

# load_dotenv()

# DATABASE_URL = os.getenv("DATABASE_URL")
# if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
#     DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    
# ssl_context = ssl.create_default_context(cafile=certifi.where())
# ssl_context.check_hostname = False
# ssl_context.verify_mode = ssl.CERT_NONE

# # Export names exactly as src/db/__init__.py expects
# async_engine = create_async_engine(
#     DATABASE_URL, 
#     echo=True, 
#     connect_args={"ssl": ssl_context}
# )

# async_session_maker = async_sessionmaker(
#     async_engine, class_=AsyncSession, expire_on_commit=False
# )

# async def init_models():
#     async with async_engine.begin() as conn:
#         await conn.run_sync(SQLModel.metadata.create_all)

# async def get_session() -> AsyncGenerator[AsyncSession, None]:
#     # async_session_maker ko use karte hue session create karein
#     async with async_session_maker() as session:
#         try:
#             yield session
#             # Request ke aakhir mein commit karne ki koshish karein
#             await session.commit()
#         except Exception:
#             await session.rollback()
#             raise
#         finally:
#             await session.close()


# # async def get_session() -> AsyncGenerator[AsyncSession, None]:
# #     async with async_session_maker() as session:
# #         yield session