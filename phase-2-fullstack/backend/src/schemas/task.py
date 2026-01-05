"""
Task request/response schemas.
[Task]: T-006 (Task Schemas)
[From]: spec.md §6.2, plan.md §5
"""

from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List


class TaskCreateRequest(BaseModel):
    """Create new task request."""
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")


class TaskUpdateRequest(BaseModel):
    """Update task (PUT) request."""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")


class TaskPatchRequest(BaseModel):
    """Patch task (toggle completion) request."""
    completed: bool = Field(..., description="Task completion status")


class TaskResponse(BaseModel):
    """Task response model."""
    id: int
    user_id: UUID
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class TaskListResponse(BaseModel):
    """List of tasks response."""
    tasks: List[TaskResponse]
    count: int
