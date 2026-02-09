import json
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import ChatRequest, ChatResponse, ErrorResponse
from .deps import get_current_user_id
from ..services.agent import AgentService, AgentResult
from ..services.chat import ChatService
from ..db.database import get_session 

# Configure logging
logger = logging.getLogger(__name__)

# Create router with /api prefix and "chat" tag
router = APIRouter(prefix="/api", tags=["chat"])

@router.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Process Chat Message"
)
async def chat_endpoint(
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session) # Session inject ho rahi hai
) -> ChatResponse:
    # Validate request
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        
        from sqlmodel import select
        from models import User
        
        statement = select(User).where(User.username == user_id)
        result = await session.execute(statement)
        user_obj = result.scalar_one_or_none()
        
        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Dono services ko session pass karna lazmi hai
        # AgentService ab session use karega Database class ki bajaye
        agent = AgentService(user_id, session) 
        chat = ChatService(user_obj.id, session) 

        # Step 1: Fetch or create conversation (Stateless - from DB)
        conversation = await chat.get_or_create_conversation(
            conversation_id=request.conversation_id,
            title=f"Chat {request.message[:50]}..." if not request.conversation_id else None
        )

        # Step 2: Get message history from Neon DB
        messages = await chat.get_messages(conversation.id)

        # Step 3: Store new user message in DB
        user_msg = await chat.add_user_message(
            conversation_id=conversation.id,
            content=request.message.strip()
        )

        # Step 4: Format history and run agent
        message_history = chat.format_messages_for_agent(messages)
        message_history.append({"role": "user", "content": request.message.strip()})

        logger.info(f"Running agent for user {user_id}")
        result: AgentResult = await agent.run(message_history)

        # Step 5: Store assistant response back to DB
        tool_calls_json = json.dumps(result.tool_calls) if result.tool_calls else None
        tool_results_json = json.dumps(result.tool_results) if result.tool_results else None

        assistant_msg = await chat.add_assistant_message(
            conversation_id=conversation.id,
            content=result.content,
            tool_calls=tool_calls_json,
            tool_results=tool_results_json
        )

        # Step 6: Return structured response
        return ChatResponse(
            success=True,
            response={
                "content": result.content,
                "tasks": result.tasks or []
            },
            conversation_id=conversation.id,
            message_id=assistant_msg.id
        )

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        # Detailed error message for debugging CrashLoopBackOff
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Chat error: {str(e)}"
        )

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "chat-api"}

__all__ = ["router"]