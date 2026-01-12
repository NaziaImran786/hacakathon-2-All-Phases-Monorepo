from typing import List, Optional
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    tasks: List["Task"] = Relationship(back_populates="owner")
    conversations: List["Conversation"] = Relationship(back_populates="user")

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: Optional[str] = None
    completed: bool = False
    owner_id: int = Field(foreign_key="user.id")
    owner: User = Relationship(back_populates="tasks")

class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True) # <-- Ye missing tha
    user_id: int = Field(foreign_key="user.id") # <-- Isay ab sirf 'int' rehne diya
    title: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user: User = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation")

class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id")
    role: str  # 'user' or 'assistant'
    content: str
    tool_calls: Optional[str] = None
    tool_results: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    conversation: Conversation = Relationship(back_populates="messages")