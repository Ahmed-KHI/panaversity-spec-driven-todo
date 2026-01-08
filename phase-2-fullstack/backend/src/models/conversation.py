"""
Conversation model for storing chat sessions.
[Task]: T-001
[From]: specs/003-phase-iii-chatbot/spec.md §4.1, plan.md §2.1.1
"""

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .message import Message


class Conversation(SQLModel, table=True):
    """
    Represents a chat conversation between user and AI assistant.
    Each conversation contains multiple messages.
    """
    __tablename__ = "conversations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True, ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation")
