"""
Validators for Phase V task fields.
[Task]: T-B-007 (Due Date Validation), T-B-008 (Recurrence Pattern Validation)
[From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §2.2, §2.3,
        specs/005-phase-v-cloud/phase5-cloud.plan.md §3.3
"""

from datetime import datetime, date
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from src.models.task import RecurrenceFrequency


def validate_due_date(due_date: Optional[datetime], reminder_time: Optional[datetime]) -> None:
    """
    Validate due date and reminder time constraints.
    
    [Task]: T-B-007
    [From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §2.2
    
    Rules:
    1. Due date cannot be in the past (with 1-minute grace period)
    2. Reminder time must be before due date
    3. Reminder time cannot be in the past
    
    Raises:
        HTTPException: If validation fails
    """
    now = datetime.utcnow()
    
    # Allow 1-minute grace period for clock skew
    grace_period_seconds = 60
    
    if due_date:
        # Check if due date is not too far in the past
        if (now - due_date).total_seconds() > grace_period_seconds:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Due date cannot be in the past"
            )
    
    if reminder_time:
        # Reminder must not be in the past
        if (now - reminder_time).total_seconds() > grace_period_seconds:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reminder time cannot be in the past"
            )
        
        # Reminder must be before due date
        if due_date and reminder_time >= due_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reminder time must be before due date"
            )


def validate_recurrence_pattern(
    is_recurring: bool,
    recurrence_pattern: Optional[Dict[str, Any]]
) -> None:
    """
    Validate recurrence pattern configuration.
    
    [Task]: T-B-008
    [From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §2.3
    
    Rules:
    1. If is_recurring=True, recurrence_pattern is required
    2. Frequency-specific validations:
       - WEEKLY: Must have days_of_week (1-7 days)
       - MONTHLY: Must have day_of_month (1-31)
       - YEARLY: Must have month (1-12) and day_of_month
    3. Interval must be >= 1
    4. Cannot have both end_date and occurrences
    5. days_of_week must be valid (0-6)
    6. End date must be in the future
    
    Raises:
        HTTPException: If validation fails
    """
    # Rule 1: Recurring tasks must have pattern
    if is_recurring and not recurrence_pattern:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recurrence pattern is required for recurring tasks"
        )
    
    if not is_recurring:
        return  # No validation needed for non-recurring tasks
    
    if not recurrence_pattern:
        return
    
    frequency = recurrence_pattern.get("frequency")
    interval = recurrence_pattern.get("interval", 1)
    days_of_week = recurrence_pattern.get("days_of_week")
    day_of_month = recurrence_pattern.get("day_of_month")
    month = recurrence_pattern.get("month")
    end_date = recurrence_pattern.get("end_date")
    occurrences = recurrence_pattern.get("occurrences")
    
    # Validate interval
    if interval < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recurrence interval must be at least 1"
        )
    
    # Validate frequency-specific rules
    if frequency == RecurrenceFrequency.WEEKLY:
        if not days_of_week or len(days_of_week) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Weekly recurrence requires at least one day of week"
            )
        if len(days_of_week) > 7:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot specify more than 7 days of week"
            )
        # Validate day values (0=Monday, 6=Sunday)
        for day in days_of_week:
            if not isinstance(day, int) or day < 0 or day > 6:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Days of week must be integers between 0 (Monday) and 6 (Sunday)"
                )
    
    elif frequency == RecurrenceFrequency.MONTHLY:
        if not day_of_month:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Monthly recurrence requires day_of_month (1-31)"
            )
        if day_of_month < 1 or day_of_month > 31:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="day_of_month must be between 1 and 31"
            )
    
    elif frequency == RecurrenceFrequency.YEARLY:
        if not month:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Yearly recurrence requires month (1-12)"
            )
        if month < 1 or month > 12:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="month must be between 1 and 12"
            )
        if not day_of_month:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Yearly recurrence requires day_of_month (1-31)"
            )
        if day_of_month < 1 or day_of_month > 31:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="day_of_month must be between 1 and 31"
            )
    
    # Validate end condition
    if end_date and occurrences:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot specify both end_date and occurrences. Choose one."
        )
    
    # Validate end_date is in the future
    if end_date:
        if isinstance(end_date, str):
            end_date = date.fromisoformat(end_date)
        if end_date < date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Recurrence end_date must be in the future"
            )
    
    # Validate occurrences
    if occurrences is not None:
        if occurrences < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="occurrences must be at least 1"
            )


def validate_task_data(
    title: Optional[str] = None,
    due_date: Optional[datetime] = None,
    reminder_time: Optional[datetime] = None,
    is_recurring: bool = False,
    recurrence_pattern: Optional[Dict[str, Any]] = None
) -> None:
    """
    Validate complete task data.
    
    Combines all validation rules for task creation/update.
    
    Raises:
        HTTPException: If any validation fails
    """
    # Validate title
    if title is not None and len(title.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title cannot be empty"
        )
    
    # Validate dates
    validate_due_date(due_date, reminder_time)
    
    # Validate recurrence
    validate_recurrence_pattern(is_recurring, recurrence_pattern)
