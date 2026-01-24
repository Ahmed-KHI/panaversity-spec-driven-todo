"""
Job trigger endpoints for scheduled tasks and reminders.
[Task]: T-C-007 (Job Trigger Endpoint)
[From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §3.2, §6.2,
        specs/005-phase-v-cloud/phase5-cloud.plan.md §5.3
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List, Dict, Any
from src.database import get_session
from src.services.reminder_scheduler import get_reminder_scheduler
from src.services.event_publisher import get_event_publisher

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("/check-reminders")
def check_reminders(
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Check for due reminders and publish events.
    
    This endpoint is designed to be called by:
    - Dapr Jobs API (scheduled cron job)
    - Kubernetes CronJob
    - External scheduler
    
    [Task]: T-C-007
    [From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §3.2.1, §6.2.1
    """
    try:
        scheduler = get_reminder_scheduler()
        reminders = scheduler.get_due_reminders(session, lookahead_minutes=60)
        
        # Publish reminder events
        event_publisher = get_event_publisher()
        published_count = 0
        
        for reminder in reminders:
            try:
                event_publisher.publish(
                    event_type="reminder.due",
                    topic="reminders",
                    payload=reminder,
                    task_id=reminder["task_id"],
                    user_id=reminder["user_id"],
                    session=session
                )
                published_count += 1
            except Exception as e:
                print(f"⚠️  Failed to publish reminder for task {reminder['task_id']}: {e}")
        
        return {
            "status": "success",
            "reminders_found": len(reminders),
            "events_published": published_count,
            "reminders": reminders
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check reminders: {str(e)}"
        )


@router.post("/check-overdue")
def check_overdue(
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Check for overdue tasks and publish notifications.
    
    [Task]: T-C-007
    [From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §3.2.2, §6.2.2
    """
    try:
        scheduler = get_reminder_scheduler()
        overdue_tasks = scheduler.get_overdue_tasks(session)
        
        # Publish overdue events
        event_publisher = get_event_publisher()
        published_count = 0
        
        for task in overdue_tasks:
            try:
                event_publisher.publish(
                    event_type="task.overdue",
                    topic="task-events",
                    payload=task,
                    task_id=task["task_id"],
                    user_id=task["user_id"],
                    session=session
                )
                published_count += 1
            except Exception as e:
                print(f"⚠️  Failed to publish overdue for task {task['task_id']}: {e}")
        
        return {
            "status": "success",
            "overdue_found": len(overdue_tasks),
            "events_published": published_count,
            "overdue_tasks": overdue_tasks
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check overdue tasks: {str(e)}"
        )


@router.get("/health")
def jobs_health_check() -> Dict[str, str]:
    """Health check for job endpoints."""
    return {
        "status": "healthy",
        "service": "jobs"
    }
