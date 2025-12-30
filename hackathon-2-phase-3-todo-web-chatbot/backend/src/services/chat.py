# Chat Service for Phase III Chatbot
# Task ID: T047 (from user stories, implemented early for foundation)
# Reference: specs/features/chatbot/plan.md (Conversational Context)
# Reference: specs/api/mcp-tools.md (Message table schema)

from typing import List, Optional
from datetime import datetime

from ..models import Conversation, Message, MessageCreate
from ..db import Database


class ChatService:
    """
    Chat service for managing conversation history.

    Provides methods for creating conversations, adding messages,
    and retrieving message history. Supports stateless request cycle
    by persisting all chat data to the database.

    Reference: specs/features/chatbot/plan.md - "Stateless Request Cycle"
    """

    def __init__(self, user_id: str):
        """
        Initialize chat service with user context.

        Args:
            user_id: The authenticated user's UUID for data isolation
        """
        self.user_id = user_id
        self.db = Database()

    async def get_or_create_conversation(
        self,
        conversation_id: Optional[int] = None,
        title: Optional[str] = None
    ) -> Conversation:
        """
        Get an existing conversation or create a new one.

        Args:
            conversation_id: Optional existing conversation ID
            title: Optional title for new conversations

        Returns:
            Conversation: The conversation object
        """
        if conversation_id:
            # Try to get existing conversation
            conversation = await self.db.get_conversation(self.user_id, conversation_id)
            if conversation:
                return conversation
            # If not found, create new one with this ID
            conversation = await self.db.create_conversation(self.user_id, title)
            return conversation

        # Create new conversation
        conversation = await self.db.create_conversation(self.user_id, title)
        return conversation

    async def get_messages(self, conversation_id: int) -> List[Message]:
        """
        Get all messages for a conversation, ordered by creation time.

        Args:
            conversation_id: The conversation ID

        Returns:
            List[Message]: List of messages in chronological order
        """
        messages = await self.db.get_messages(conversation_id)
        return messages

    async def add_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        tool_calls: Optional[str] = None,
        tool_results: Optional[str] = None,
    ) -> Message:
        """
        Add a message to a conversation.

        Args:
            conversation_id: The conversation ID
            role: Message role ('user', 'assistant', 'system')
            content: Message content
            tool_calls: JSON-encoded tool calls (optional)
            tool_results: JSON-encoded tool results (optional)

        Returns:
            Message: The created message
        """
        message = await self.db.add_message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tool_calls=tool_calls,
            tool_results=tool_results,
        )
        return message

    async def add_user_message(
        self,
        conversation_id: int,
        content: str,
    ) -> Message:
        """
        Add a user message to a conversation.

        Convenience method for adding user messages.

        Args:
            conversation_id: The conversation ID
            content: User's message content

        Returns:
            Message: The created message
        """
        return await self.add_message(
            conversation_id=conversation_id,
            role="user",
            content=content,
        )

    async def add_assistant_message(
        self,
        conversation_id: int,
        content: str,
        tool_calls: Optional[str] = None,
        tool_results: Optional[str] = None,
    ) -> Message:
        """
        Add an assistant message to a conversation.

        Convenience method for adding assistant messages with tool context.

        Args:
            conversation_id: The conversation ID
            content: Assistant's response content
            tool_calls: JSON-encoded tool calls (optional)
            tool_results: JSON-encoded tool results (optional)

        Returns:
            Message: The created message
        """
        return await self.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=content,
            tool_calls=tool_calls,
            tool_results=tool_results,
        )

    def format_messages_for_agent(self, messages: List[Message]) -> List[dict]:
        """
        Format messages for the agent's message array.

        Converts Message SQLModel objects to dict format expected
        by the OpenAI Agents SDK.

        Args:
            messages: List of Message objects

        Returns:
            List of dicts with 'role' and 'content' keys
        """
        formatted = []
        for msg in messages:
            formatted.append({
                "role": msg.role,
                "content": msg.content,
            })
        return formatted
