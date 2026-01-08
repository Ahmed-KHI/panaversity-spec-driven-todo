"""
Message model for storing conversation messages.
[Task]: T-002
[From]: specs/003-phase-iii-chatbot/spec.md §4.2, plan.md §2.1.1
"""

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .conversation import Conversation


class Message(SQLModel, table=True):
    """
    Represents a single message in a conversation.
    Role can be 'user' or 'assistant'.
    """
    __tablename__ = "messages"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True, ondelete="CASCADE")
    user_id: UUID = Field(foreign_key="users.id", index=True, ondelete="CASCADE")
    role: str = Field(max_length=20)  # 'user' or 'assistant'
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    # Relationships
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")
