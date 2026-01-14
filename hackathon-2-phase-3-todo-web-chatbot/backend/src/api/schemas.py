# API Request/Response Schemas for Phase III Chatbot
# Task ID: T015
# Reference: specs/features/chatbot/plan.md (Backend API: POST /api/chat)
# Reference: specs/api/mcp-tools.md (Tool input/output schemas)

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class ChatRequest(BaseModel):
    """
    Request schema for POST /api/chat endpoint.

    Used by the frontend Chatkit client to send messages to the agent.
    The user_id is extracted from the JWT token, not included in the request body.
    """
    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="User's natural language message"
    )
    conversation_id: Optional[int] = Field(
        default=None,
        description="Optional conversation ID for multi-turn chats"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Add a task to buy groceries",
                "conversation_id": 1
            }
        }
    )


class TaskResponse(BaseModel):
    """Task data returned in chat responses."""
    id: int
    title: str
    status: str
    user_id: Optional[str] = None      # <-- Made Optional
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    created_at: Optional[datetime] = None # <-- Made Optional
    updated_at: Optional[datetime] = None # <-- Made Optional

    model_config = ConfigDict(from_attributes=True)


class ChatResponse(BaseModel):
    """
    Response schema for POST /api/chat endpoint.

    Contains the agent's response and any task data affected by the interaction.
    """
    success: bool = Field(..., description="Whether the request was successful")
    response: "ChatResponseContent" = Field(..., description="Agent response data")
    conversation_id: int = Field(..., description="Conversation ID for follow-up messages")
    message_id: int = Field(..., description="Assistant message ID for reference")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "response": {
                    "content": "I've added a task 'Buy groceries' to your list.",
                    "tasks": [
                        {
                            "id": 42,
                            "user_id": "550e8400-e29b-41d4-a716-446655440000",
                            "title": "Buy groceries",
                            "status": "pending",
                            "created_at": "2025-12-29T10:00:00Z"
                        }
                    ]
                },
                "conversation_id": 1,
                "message_id": 10
            }
        }
    )


class ChatResponseContent(BaseModel):
    """Content of the agent's response."""
    content: str = Field(..., description="Agent's textual response")
    tasks: List[TaskResponse] = Field(
        default_factory=list,
        description="Tasks affected by this interaction"
    )


class ErrorResponse(BaseModel):
    """Error response schema for API errors."""
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Machine-readable error code")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detail": "Invalid token: missing user_id",
                "error_code": "UNAUTHORIZED"
            }
        }
    )


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    database: str = Field(..., description="Database connection status")


# Forward references for nested models
ChatResponse.model_rebuild()
ChatResponseContent.model_rebuild()
