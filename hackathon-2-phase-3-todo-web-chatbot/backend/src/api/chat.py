# Chat API Endpoint for Phase III Chatbot
# Tasks: T023, T024, T025
# Reference: specs/features/chatbot/plan.md (Backend API: POST /api/chat)
# Reference: specs/features/chatbot/plan.md (Stateless Request Cycle)

import json
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional

from .schemas import ChatRequest, ChatResponse, ErrorResponse
from .deps import get_current_user_id
from ..services.agent import AgentService, AgentResult
from ..services.chat import ChatService

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
    summary="Process Chat Message",
    description="Process a natural language chat message with the AI agent"
)
async def chat_endpoint(
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id),
) -> ChatResponse:
    """
    Process a natural language chat message with the AI agent.

    This endpoint implements the stateless request cycle:
    1. Verify JWT and extract user_id
    2. Fetch or create conversation
    3. Load message history from database
    4. Store new user message
    5. Run agent with history and tools
    6. Store assistant response
    7. Return response to client

    All state is persisted to Neon PostgreSQL - no in-memory session storage.
    """
    # Validate request
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty"
        )

    if len(request.message) > 10000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message too long (max 10000 characters)"
        )

    try:
        # Initialize services with user_id for isolation
        agent = AgentService(user_id)
        chat = ChatService(user_id)

        # Step 1: Fetch or create conversation
        conversation = await chat.get_or_create_conversation(
            conversation_id=request.conversation_id,
            title=f"Chat {request.message[:50]}..." if not request.conversation_id else None
        )

        # Step 2: Get message history for context
        messages = await chat.get_messages(conversation.id)

        # Step 3: Store new user message
        user_msg = await chat.add_user_message(
            conversation_id=conversation.id,
            content=request.message.strip()
        )

        # Step 4: Format messages for agent
        message_history = chat.format_messages_for_agent(messages)
        message_history.append({
            "role": "user",
            "content": request.message.strip()
        })

        # Step 5: Run agent with history and MCP tools
        logger.info(f"Running agent for user {user_id}, conversation {conversation.id}")
        result: AgentResult = await agent.run(message_history)

        # Step 6: Store assistant response with tool context
        tool_calls_json = json.dumps(result.tool_calls) if result.tool_calls else None
        tool_results_json = json.dumps(result.tool_results) if result.tool_results else None

        assistant_msg = await chat.add_assistant_message(
            conversation_id=conversation.id,
            content=result.content,
            tool_calls=tool_calls_json,
            tool_results=tool_results_json
        )

        # Log successful interaction
        logger.info(
            f"Chat interaction complete: user={user_id}, "
            f"conversation={conversation.id}, message={assistant_msg.id}, "
            f"tools_called={len(result.tool_calls) if result.tool_calls else 0}"
        )

        # Step 7: Return response
        return ChatResponse(
            success=True,
            response={
                "content": result.content,
                "tasks": result.tasks if result.tasks else []
            },
            conversation_id=conversation.id,
            message_id=assistant_msg.id
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except ValueError as e:
        # Handle validation errors
        logger.warning(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Chat endpoint error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your message"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for the chat service."""
    return {"status": "healthy", "service": "chat-api"}


# Export router for FastAPI app
__all__ = ["router"]
