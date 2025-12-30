# Message SQLModel for Phase III Chatbot
# Task ID: T010
# Reference: specs/api/mcp-tools.md (Message Table schema)
# Reference: specs/features/chatbot/plan.md (SQLModel Definitions)

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class Message(SQLModel, table=True):
    """
    Message entity representing a single message in a conversation.
    Supports stateless request cycle by persisting all chat history to database.
    Stores role (user/assistant/system), content, and tool call/results for audit.
    """
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(
        foreign_key="conversations.id",
        index=True,
        description="Reference to parent conversation"
    )
    role: str = Field(
        max_length=20,
        description="Message role: user, assistant, or system"
    )
    content: str = Field(
        description="Message content text"
    )
    tool_calls: Optional[str] = Field(
        default=None,
        description="JSON-encoded tool calls made during message processing"
    )
    tool_results: Optional[str] = Field(
        default=None,
        description="JSON-encoded results from tool invocations"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when message was created"
    )

    # Relationship to conversation - uses string reference to avoid circular import
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")


class MessageCreate(SQLModel):
    """Schema for creating a new message."""
    conversation_id: int
    role: str
    content: str
    tool_calls: Optional[str] = None
    tool_results: Optional[str] = None


class MessageResponse(SQLModel):
    """Schema for message response."""
    id: int
    conversation_id: int
    role: str
    content: str
    tool_calls: Optional[str]
    tool_results: Optional[str]
    created_at: datetime
