"""
Task model for todo management.
[Task]: T-006 (Task Model), T-A-004 (Phase V: Advanced Fields)
[From]: spec.md §7.2, plan.md §5
        specs/005-phase-v-cloud/phase5-cloud.specify.md §2.1-2.5
        specs/005-phase-v-cloud/phase5-cloud.plan.md §3.1
"""

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.dialects.postgresql import JSONB
from uuid import UUID
from datetime import datetime
from typing import Optional, TYPE_CHECKING, List
from enum import Enum
import json

if TYPE_CHECKING:
    from src.models.user import User
    from src.models.tag import Tag, TaskTag


class Priority(str, Enum):
    """
    Task priority levels.
    [Task]: T-A-004
    [From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §2.3
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class RecurrenceFrequency(str, Enum):
    """
    Recurrence frequency options.
    [Task]: T-A-004
    [From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §2.1
    """
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class RecurrencePattern(SQLModel):
    """
    Recurrence pattern configuration (stored as JSONB).
    [Task]: T-A-004
    [From]: specs/005-phase-v-cloud/phase5-cloud.plan.md §2.3
    """
    frequency: RecurrenceFrequency
    interval: int = 1
    days_of_week: Optional[List[int]] = None  # 0=Sunday, 6=Saturday
    day_of_month: Optional[int] = None  # 1-31
    month: Optional[int] = None  # 1-12
    end_date: Optional[datetime] = None
    occurrences: Optional[int] = None


class Task(SQLModel, table=True):
    """
    Task/Todo item model with Phase V advanced features.
    
    [Task]: T-006 (Base), T-A-004 (Phase V Extensions)
    [From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §2.1-2.5
    
    Each task belongs to one user (user_id foreign key).
    Phase V additions:
    - Priority levels (low, medium, high, urgent)
    - Due dates and reminder times
    - Recurring task support with flexible patterns
    - Tag relationships for organization
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
    
    # Phase V: Advanced Features
    priority: Priority = Field(
        default=Priority.MEDIUM,
        nullable=False,
        index=True,
        description="Task priority: low, medium, high, urgent"
    )
    
    due_date: Optional[datetime] = Field(
        default=None,
        nullable=True,
        index=True,
        description="When the task is due"
    )
    
    reminder_time: Optional[datetime] = Field(
        default=None,
        nullable=True,
        description="When to send reminder notification"
    )
    
    is_recurring: bool = Field(
        default=False,
        nullable=False,
        index=True,
        description="Whether this task repeats on a schedule"
    )
    
    recurrence_pattern: Optional[str] = Field(
        default=None,
        nullable=True,
        sa_type=JSONB,
        description="JSONB: RecurrencePattern configuration"
    )
    
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True
    )
    
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    user: "User" = Relationship(back_populates="tasks")
    tags: List["Tag"] = Relationship(
        back_populates="tasks",
        sa_relationship_kwargs={"secondary": "task_tags"}
    )
    
    # Property methods for recurrence pattern handling
    @property
    def recurrence(self) -> Optional[RecurrencePattern]:
        """
        Get recurrence pattern as RecurrencePattern object.
        [Task]: T-A-004
        """
        if self.recurrence_pattern:
            try:
                data = json.loads(self.recurrence_pattern)
                return RecurrencePattern(**data)
            except (json.JSONDecodeError, TypeError, ValueError):
                return None
        return None
    
    @recurrence.setter
    def recurrence(self, pattern: Optional[RecurrencePattern]):
        """
        Set recurrence pattern from RecurrencePattern object.
        [Task]: T-A-004
        """
        if pattern:
            self.recurrence_pattern = pattern.model_dump_json()
        else:
            self.recurrence_pattern = None
