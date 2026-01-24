"""
Reminder scheduler service for task reminders.
[Task]: T-C-006 (Reminder Scheduler)
[From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §3.2,
        specs/005-phase-v-cloud/phase5-cloud.plan.md §5.3
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlmodel import Session, select
from src.models.task import Task
from src.models.user import User


class ReminderScheduler:
    """
    Service for identifying and scheduling task reminders.
    
    [Task]: T-C-006
    [From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §3.2.1
    """
    
    def get_due_reminders(self, session: Session, lookahead_minutes: int = 60) -> List[Dict[str, Any]]:
        """
        Get tasks with reminders due within the specified lookahead window.
        
        Args:
            session: Database session
            lookahead_minutes: How many minutes ahead to check (default 60)
        
        Returns:
            List of reminder dictionaries with task and user info
        
        [Task]: T-C-006
        [From]: specs/005-phase-v-cloud/phase5-cloud.plan.md §5.3.1
        """
        now = datetime.utcnow()
        lookahead_time = now + timedelta(minutes=lookahead_minutes)
        
        # Query tasks with reminders in the lookahead window
        tasks = session.exec(
            select(Task).where(
                Task.reminder_time.isnot(None),
                Task.reminder_time <= lookahead_time,
                Task.reminder_time > now,
                Task.completed == False
            )
        ).all()
        
        reminders = []
        for task in tasks:
            user = session.exec(
                select(User).where(User.id == task.user_id)
            ).first()
            
            if user:
                reminders.append({
                    "task_id": task.id,
                    "user_id": str(task.user_id),
                    "user_email": user.email,
                    "user_name": user.full_name,
                    "title": task.title,
                    "description": task.description,
                    "reminder_time": task.reminder_time.isoformat(),
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "priority": task.priority.value,
                    "minutes_until_reminder": int((task.reminder_time - now).total_seconds() / 60)
                })
        
        return reminders
    
    def get_overdue_tasks(self, session: Session) -> List[Dict[str, Any]]:
        """
        Get tasks that are overdue (past due date and not completed).
        
        [Task]: T-C-006
        [From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §3.2.2
        """
        now = datetime.utcnow()
        
        tasks = session.exec(
            select(Task).where(
                Task.due_date.isnot(None),
                Task.due_date < now,
                Task.completed == False
            )
        ).all()
        
        overdue = []
        for task in tasks:
            user = session.exec(
                select(User).where(User.id == task.user_id)
            ).first()
            
            if user:
                overdue.append({
                    "task_id": task.id,
                    "user_id": str(task.user_id),
                    "user_email": user.email,
                    "user_name": user.full_name,
                    "title": task.title,
                    "due_date": task.due_date.isoformat(),
                    "priority": task.priority.value,
                    "hours_overdue": int((now - task.due_date).total_seconds() / 3600)
                })
        
        return overdue


def get_reminder_scheduler() -> ReminderScheduler:
    """Get singleton reminder scheduler instance."""
    return ReminderScheduler()
