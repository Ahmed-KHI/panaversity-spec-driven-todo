"""
Tag model for task organization.
[Task]: T-A-005
[From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §2.4
        specs/005-phase-v-cloud/phase5-cloud.plan.md §3.1
"""

from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.task import Task
    from src.models.user import User


class Tag(SQLModel, table=True):
    """
    Tag model for organizing tasks into categories.
    
    [Task]: T-A-005
    [From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §2.4
    
    Tags are user-created labels that can be applied to multiple tasks.
    Each tag has a name and color for visual organization.
    """
    __tablename__ = "tags"
    
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        nullable=False
    )
    
    name: str = Field(
        nullable=False,
        unique=True,
        index=True,
        min_length=1,
        max_length=50,
        description="Tag name (unique across all users)"
    )
    
    color: str = Field(
        default="#3B82F6",
        nullable=False,
        max_length=7,
        regex=r"^#[0-9A-Fa-f]{6}$",
        description="Hex color code for tag display"
    )
    
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )
    
    created_by: UUID = Field(
        foreign_key="users.id",
        nullable=False,
        description="User who created this tag"
    )
    
    # Relationships
    tasks: List["Task"] = Relationship(
        back_populates="tags",
        sa_relationship_kwargs={"secondary": "task_tags"}
    )
    
    creator: "User" = Relationship()


class TaskTag(SQLModel, table=True):
    """
    Junction table linking tasks and tags (many-to-many).
    
    [Task]: T-A-005
    [From]: specs/005-phase-v-cloud/phase5-cloud.plan.md §2.2
    
    Allows tasks to have multiple tags and tags to apply to multiple tasks.
    """
    __tablename__ = "task_tags"
    
    task_id: int = Field(
        foreign_key="tasks.id",
        primary_key=True,
        nullable=False,
        ondelete="CASCADE"
    )
    
    tag_id: int = Field(
        foreign_key="tags.id",
        primary_key=True,
        nullable=False,
        ondelete="CASCADE"
    )
