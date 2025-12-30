# Conversation SQLModel for Phase III Chatbot
# Task ID: T009
# Reference: specs/api/mcp-tools.md (Conversation Table schema)
# Reference: specs/features/chatbot/plan.md (SQLModel Definitions)

from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class Conversation(SQLModel, table=True):
    """
    Conversation entity representing a chat session between user and agent.
    Supports stateless request cycle by storing all conversation history in database.
    User isolation enforced via user_id field - conversations are user-scoped.
    """
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(
        index=True,
        description="User UUID for data isolation - all operations require user_id filter"
    )
    title: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Optional conversation title for identification"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when conversation was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when conversation was last updated"
    )

    # Relationship to messages - uses string reference to avoid circular import
    # Note: Relationship is optional for stateless architecture - we use explicit queries
    messages: List["Message"] = Relationship(back_populates="conversation")


class ConversationResponse(SQLModel):
    """Schema for conversation response."""
    id: int
    user_id: str
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
