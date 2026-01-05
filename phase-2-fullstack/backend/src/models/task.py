"""
Task model for todo management.
[Task]: T-006 (Task Model)
[From]: spec.md §7.2, plan.md §5
"""

from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.user import User


class Task(SQLModel, table=True):
    """
    Task/Todo item model.
    
    Each task belongs to one user (user_id foreign key).
    """
    __tablename__ = "tasks"
    
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        nullable=False
    )
    
    user_id: UUID = Field(
        foreign_key="users.id",
        nullable=False,
        index=True
    )
    
    title: str = Field(
        nullable=False,
        min_length=1,
        max_length=200
    )
    
    description: Optional[str] = Field(
        default=None,
        max_length=1000
    )
    
    completed: bool = Field(
        default=False,
        nullable=False
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
    user: "User" = Relationship(back_populates="tasks")
