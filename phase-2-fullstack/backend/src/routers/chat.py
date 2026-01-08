"""
Chat API endpoint for AI agent interaction.
[Task]: T-007
[From]: specs/003-phase-iii-chatbot/spec.md §5.1, plan.md §2.1.4
"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select, col
from pydantic import BaseModel
from uuid import UUID
from typing import Optional, List, Dict, Any
from datetime import datetime
from src.database import get_session
from src.models.user import User
from src.models.conversation import Conversation
from src.models.message import Message
from src.utils.deps import get_current_user
from src.agent.runner import run_agent

router = APIRouter(prefix="/api", tags=["chat"])


# Request/Response schemas
class ChatRequest(BaseModel):
    conversation_id: Optional[int] = None
    message: str


class ChatResponse(BaseModel):
    conversation_id: int
    response: str
    tool_calls: List[Dict[str, Any]]


@router.post("/{user_id}/chat", response_model=ChatResponse)
def chat(
    user_id: UUID,
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Send message to AI agent and receive response.
    
    Stateless request cycle:
    1. Validate auth (JWT)
    2. Verify user_id matches token
    3. Fetch/create conversation
    4. Load message history
    5. Store user message
    6. Run agent
    7. Store assistant message
    8. Return response
    
    Args:
        user_id: User UUID from path parameter
        request: Chat request with optional conversation_id and message
        current_user: Authenticated user from JWT token
        session: Database session
        
    Returns:
        ChatResponse with conversation_id, response text, and tool call metadata
    """
    
    # CRITICAL: Verify path user_id matches authenticated user (Layer 2 security)
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found"
        )
    
    # Validate message
    if not request.message or len(request.message.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Message cannot be empty"
        )
    
    if len(request.message) > 2000:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Message must be under 2000 characters"
        )
    
    # Get or create conversation
    if request.conversation_id:
        conversation = session.exec(
            select(Conversation).where(
                Conversation.id == request.conversation_id,
                Conversation.user_id == current_user.id  # Layer 3: Database filtering
            )
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
    else:
        # Create new conversation
        conversation = Conversation(user_id=current_user.id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
    
    # Load conversation history (last 50 messages for token efficiency)
    messages_query = select(Message).where(
        Message.conversation_id == conversation.id
    ).order_by(col(Message.created_at)).limit(50)
    
    message_history = session.exec(messages_query).all()
    
    # Build messages array for agent
    messages_array = [
        {"role": msg.role, "content": msg.content}
        for msg in message_history
    ]
    
    # Add current user message
    messages_array.append({"role": "user", "content": request.message})
    
    # Store user message
    user_message = Message(
        conversation_id=conversation.id,
        user_id=current_user.id,
        role="user",
        content=request.message
    )
    session.add(user_message)
    session.commit()
    
    # Run agent
    try:
        agent_result = run_agent(
            session=session,
            user_id=current_user.id,
            messages=messages_array
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )
    
    # Store assistant message
    assistant_message = Message(
        conversation_id=conversation.id if conversation.id else 0,
        user_id=current_user.id,
        role="assistant",
        content=agent_result["response"]
    )
    session.add(assistant_message)
    session.commit()
    
    # Update conversation timestamp
    conversation.updated_at = datetime.utcnow()
    session.add(conversation)
    session.commit()
    
    # Return response
    return ChatResponse(
        conversation_id=conversation.id if conversation.id else 0,
        response=agent_result["response"],
        tool_calls=agent_result["tool_calls"]
    )
