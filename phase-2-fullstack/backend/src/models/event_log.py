"""
Event Log model for audit trail and event tracking.
[Task]: T-A-006
[From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §3.1
        specs/005-phase-v-cloud/phase5-cloud.plan.md §2.4, §3.1
"""

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.dialects.postgresql import JSONB
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, TYPE_CHECKING, Dict, Any
import json

if TYPE_CHECKING:
    from src.models.task import Task
    from src.models.user import User


class EventLog(SQLModel, table=True):
    """
    Event log model for tracking all system events.
    
    [Task]: T-A-006
    [From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §3.1
    
    Stores audit trail of all events published to Kafka topics.
    Used for debugging, analytics, and activity timelines.
    
    Events include:
    - task.created, task.updated, task.completed, task.deleted
    - reminder.scheduled, reminder.due, reminder.cancelled
    - task.sync (real-time updates)
    """
    __tablename__ = "event_log"
    
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        nullable=False
    )
    
    event_id: UUID = Field(
        default_factory=uuid4,
        nullable=False,
        unique=True,
        index=True,
        description="Unique event identifier (UUID)"
    )
    
    event_type: str = Field(
        nullable=False,
        max_length=50,
        index=True,
        description="Type of event (e.g., 'task.created', 'reminder.due')"
    )
    
    topic: str = Field(
        nullable=False,
        max_length=50,
        description="Kafka topic where event was published"
    )
    
    task_id: Optional[int] = Field(
        default=None,
        foreign_key="tasks.id",
        nullable=True,
        index=True,
        ondelete="SET NULL",
        description="Related task ID (if applicable)"
    )
    
    user_id: Optional[UUID] = Field(
        default=None,
        foreign_key="users.id",
        nullable=True,
        index=True,
        ondelete="SET NULL",
        description="User who triggered the event"
    )
    
    payload: str = Field(
        nullable=False,
        sa_type=JSONB,
        description="Full event data (JSONB)"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
        description="When the event occurred"
    )
    
    processed: bool = Field(
        default=False,
        nullable=False,
        description="Whether this event has been processed by consumers"
    )
    
    # Relationships (optional, for querying)
    task: Optional["Task"] = Relationship()
    user: Optional["User"] = Relationship()
    
    # Helper methods for payload handling
    @property
    def payload_dict(self) -> Dict[str, Any]:
        """
        Get payload as dictionary.
        [Task]: T-A-006
        """
        if isinstance(self.payload, str):
            try:
                return json.loads(self.payload)
            except (json.JSONDecodeError, TypeError):
                return {}
        return self.payload if isinstance(self.payload, dict) else {}
    
    @payload_dict.setter
    def payload_dict(self, data: Dict[str, Any]):
        """
        Set payload from dictionary.
        [Task]: T-A-006
        """
        self.payload = json.dumps(data)
