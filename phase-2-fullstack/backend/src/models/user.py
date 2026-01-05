"""
User model for authentication.
[Task]: T-005 (User Model)
[From]: spec.md §7.1, plan.md §5
"""

from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.task import Task


class User(SQLModel, table=True):
    """
    User account model.
    
    Primary entity for authentication and task ownership.
    """
    __tablename__ = "users"
    
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False
    )
    
    email: str = Field(
        unique=True,
        index=True,
        nullable=False,
        max_length=255
    )
    
    password_hash: str = Field(
        nullable=False,
        max_length=255
    )
    
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )
    
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    tasks: List["Task"] = Relationship(back_populates="user", cascade_delete=True)
