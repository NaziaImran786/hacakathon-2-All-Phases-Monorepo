from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from models import Conversation, Message

class ChatService:
    def __init__(self, user_id: str, session: AsyncSession):
        self.user_id = user_id
        self.session = session # Ab ye seedha async session use karega

    async def get_or_create_conversation(
        self, conversation_id: Optional[int] = None, title: Optional[str] = None
    ) -> Conversation:
        if conversation_id:
            # Async execution
            stmt = select(Conversation).where(
                Conversation.id == conversation_id, 
                Conversation.user_id == self.user_id
            )
            result = await self.session.execute(stmt)
            conversation = result.scalars().first()
            if conversation:
                return conversation

        # Create new
        new_conv = Conversation(user_id=self.user_id, title=title or "New Chat")
        self.session.add(new_conv)
        await self.session.commit()
        await self.session.refresh(new_conv)
        return new_conv

    async def get_messages(self, conversation_id: int) -> List[Message]:
        stmt = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def add_message(
        self, conversation_id: int, role: str, content: str, **kwargs
    ) -> Message:
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            **kwargs
        )
        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)
        return message

    # Convenience methods
    async def add_user_message(self, conversation_id: int, content: str):
        return await self.add_message(conversation_id, "user", content)

    async def add_assistant_message(self, conversation_id: int, content: str, **kwargs):
        return await self.add_message(conversation_id, "assistant", content, **kwargs)

    def format_messages_for_agent(self, messages: List[Message]) -> List[dict]:
        return [{"role": m.role, "content": m.content} for m in messages]