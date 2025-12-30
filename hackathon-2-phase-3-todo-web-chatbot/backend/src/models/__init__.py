# Models package
# Export all SQLModel entities for Phase III Chatbot
# NOTE: Task is renamed to ChatTask to avoid collision with Phase I/II Task model
#
# Import order matters for SQLModel relationship resolution:
# 1. First import Conversation (has forward reference to Message)
# 2. Then import Message (has back_populates to Conversation)
# This allows SQLModel to resolve the bidirectional relationship correctly.

from .task import ChatTask, TaskCreate, TaskUpdate, TaskResponse
from .conversation import Conversation, ConversationResponse
from .message import Message, MessageCreate, MessageResponse

# Update forward references for relationship resolution
# This ensures SQLModel can properly resolve string annotations
Conversation.model_rebuild()
Message.model_rebuild()

__all__ = [
    # Task models (ChatTask renamed to avoid collision with Phase I/II Task)
    "ChatTask",
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    # Conversation models
    "Conversation",
    "ConversationResponse",
    # Message models
    "Message",
    "MessageCreate",
    "MessageResponse",
]
