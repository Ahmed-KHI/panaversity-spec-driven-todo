"""
Task statistics and analytics endpoints.
[Task]: T-B-010 (Task Statistics)
[From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §5.3,
        specs/005-phase-v-cloud/phase5-cloud.plan.md §4.3
"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select, func
from uuid import UUID
from datetime import datetime, timedelta
from typing import Dict, Any
from src.database import get_session
from src.models.task import Task, Priority
from src.models.user import User
from src.utils.deps import get_current_user

router = APIRouter(prefix="/api/{user_id}/stats", tags=["statistics"])


@router.get("/tasks", response_model=Dict[str, Any])
def get_task_statistics(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get task statistics for authenticated user.
    
    [Task]: T-B-010
    [From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §5.3
    
    Returns:
        - total: Total number of tasks
        - completed: Number of completed tasks
        - pending: Number of pending tasks
        - by_priority: Count by priority level
        - overdue: Number of overdue tasks
        - due_today: Tasks due today
        - due_this_week: Tasks due this week
        - recurring: Number of recurring tasks
        - completion_rate: Percentage of completed tasks
    """
    # CRITICAL: Verify path user_id matches authenticated user
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found"
        )
    
    # Get all tasks for user
    all_tasks = session.exec(
        select(Task).where(Task.user_id == current_user.id)
    ).all()
    
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)
    today_end = today_start + timedelta(days=1)
    week_end = today_start + timedelta(days=7)
    
    # Calculate statistics
    total = len(all_tasks)
    completed = sum(1 for t in all_tasks if t.completed)
    pending = total - completed
    
    # Count by priority
    by_priority = {
        "low": sum(1 for t in all_tasks if t.priority == Priority.LOW),
        "medium": sum(1 for t in all_tasks if t.priority == Priority.MEDIUM),
        "high": sum(1 for t in all_tasks if t.priority == Priority.HIGH),
        "urgent": sum(1 for t in all_tasks if t.priority == Priority.URGENT),
    }
    
    # Overdue tasks (not completed and due date passed)
    overdue = sum(
        1 for t in all_tasks 
        if not t.completed and t.due_date and t.due_date < now
    )
    
    # Due today
    due_today = sum(
        1 for t in all_tasks
        if not t.completed and t.due_date and today_start <= t.due_date < today_end
    )
    
    # Due this week
    due_this_week = sum(
        1 for t in all_tasks
        if not t.completed and t.due_date and today_start <= t.due_date < week_end
    )
    
    # Recurring tasks
    recurring = sum(1 for t in all_tasks if t.is_recurring)
    
    # Completion rate
    completion_rate = round((completed / total * 100), 2) if total > 0 else 0.0
    
    return {
        "total": total,
        "completed": completed,
        "pending": pending,
        "by_priority": by_priority,
        "overdue": overdue,
        "due_today": due_today,
        "due_this_week": due_this_week,
        "recurring": recurring,
        "completion_rate": completion_rate,
        "generated_at": now.isoformat()
    }
