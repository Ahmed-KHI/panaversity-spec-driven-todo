"""
Task request/response schemas.
[Task]: T-006 (Task Schemas), T-A-007 (Phase V Extensions)
[From]: specs/phase1-console-app.specify.md §6.2, plan.md §5,
        specs/005-phase-v-cloud/phase5-cloud.specify.md §2.1-2.5,
        specs/005-phase-v-cloud/phase5-cloud.plan.md §3.1
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from uuid import UUID
from datetime import datetime, date
from typing import Optional, List
from src.models.task import Priority, RecurrenceFrequency


from src.models.task import Priority, RecurrenceFrequency


# ===== Recurrence Pattern Schemas =====

class RecurrencePatternCreate(BaseModel):
    """Recurrence pattern for recurring tasks."""
    frequency: RecurrenceFrequency = Field(..., description="Recurrence frequency (daily, weekly, monthly, yearly)")
    interval: int = Field(1, ge=1, le=365, description="Interval between recurrences (e.g., every 2 weeks)")
    days_of_week: Optional[List[int]] = Field(None, description="Days of week (0=Monday, 6=Sunday) for weekly recurrence")
    day_of_month: Optional[int] = Field(None, ge=1, le=31, description="Day of month for monthly recurrence")
    month: Optional[int] = Field(None, ge=1, le=12, description="Month for yearly recurrence")
    end_date: Optional[date] = Field(None, description="End date for recurrence")
    occurrences: Optional[int] = Field(None, ge=1, description="Number of occurrences (alternative to end_date)")
    
    @field_validator('days_of_week')
    @classmethod
    def validate_days_of_week(cls, v):
        if v is not None:
            if not all(0 <= day <= 6 for day in v):
                raise ValueError("Days of week must be between 0 (Monday) and 6 (Sunday)")
        return v


class RecurrencePatternResponse(BaseModel):
    """Recurrence pattern response."""
    frequency: RecurrenceFrequency
    interval: int = 1
    days_of_week: Optional[List[int]] = None
    day_of_month: Optional[int] = None
    month: Optional[int] = None
    end_date: Optional[date] = None
    occurrences: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


# ===== Tag Schemas =====

class TagCreate(BaseModel):
    """Create tag request."""
    name: str = Field(..., min_length=1, max_length=50, description="Tag name")
    color: Optional[str] = Field("#3B82F6", pattern="^#[0-9A-Fa-f]{6}$", description="Hex color code")


class TagResponse(BaseModel):
    """Tag response."""
    id: int
    name: str
    color: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ===== Task Schemas =====

class TaskCreateRequest(BaseModel):
    """Create new task request with Phase V advanced features."""
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    priority: Priority = Field(Priority.MEDIUM, description="Task priority (low, medium, high, urgent)")
    due_date: Optional[datetime] = Field(None, description="Due date and time for task")
    reminder_time: Optional[datetime] = Field(None, description="Reminder notification time")
    is_recurring: bool = Field(False, description="Whether task recurs")
    recurrence_pattern: Optional[RecurrencePatternCreate] = Field(None, description="Recurrence configuration")
    tags: Optional[List[str]] = Field(None, description="List of tag names to associate with task")


class TaskUpdateRequest(BaseModel):
    """Update task (PUT) request with Phase V fields."""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    priority: Optional[Priority] = Field(None, description="Task priority")
    due_date: Optional[datetime] = Field(None, description="Due date and time")
    reminder_time: Optional[datetime] = Field(None, description="Reminder time")
    is_recurring: Optional[bool] = Field(None, description="Recurring flag")
    recurrence_pattern: Optional[RecurrencePatternCreate] = Field(None, description="Recurrence configuration")
    tags: Optional[List[str]] = Field(None, description="Tag names")


class TaskPatchRequest(BaseModel):
    """Patch task (toggle completion) request."""
    completed: bool = Field(..., description="Task completion status")


class TaskResponse(BaseModel):
    """Task response model with Phase V fields."""
    id: int
    user_id: UUID
    title: str
    description: Optional[str]
    completed: bool
    priority: Priority
    due_date: Optional[datetime]
    reminder_time: Optional[datetime]
    is_recurring: bool
    recurrence_pattern: Optional[RecurrencePatternResponse]
    tags: List[TagResponse]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class TaskListResponse(BaseModel):
    """List of tasks response."""
    tasks: List[TaskResponse]
    count: int


# ===== Search and Filter Schemas =====

class TaskSearchFilters(BaseModel):
    """Search and filter parameters for tasks."""
    search: Optional[str] = Field(None, description="Search in title and description")
    priority: Optional[List[Priority]] = Field(None, description="Filter by priorities")
    completed: Optional[bool] = Field(None, description="Filter by completion status")
    tags: Optional[List[str]] = Field(None, description="Filter by tag names (AND logic)")
    due_before: Optional[datetime] = Field(None, description="Filter tasks due before this date")
    due_after: Optional[datetime] = Field(None, description="Filter tasks due after this date")
    is_recurring: Optional[bool] = Field(None, description="Filter recurring tasks")
    sort_by: str = Field("created_at", description="Sort field (created_at, updated_at, due_date, priority, title)")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Sort order (asc, desc)")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")

