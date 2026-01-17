"""
MCP tool implementations for task operations.
[Task]: T-004
[From]: specs/003-phase-iii-chatbot/spec.md §6, plan.md §2.1.2

These tools provide stateless, database-backed operations for task management.
All tools enforce user isolation through user_id filtering.
"""

from sqlmodel import Session, select, col
from src.models.task import Task
from uuid import UUID
from typing import Dict, Any, Optional


def add_task(
    session: Session,
    user_id: UUID,
    title: str,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new task for the user.
    
    Args:
        session: Database session
        user_id: User UUID from JWT token
        title: Task title (1-200 characters)
        description: Optional task description
        
    Returns:
        {"task_id": int, "status": "created", "title": str, "description": str}
    """
    try:
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            completed=False
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        
        return {
            "task_id": task.id,
            "status": "created",
            "title": task.title,
            "description": task.description
        }
    except Exception as e:
        session.rollback()
        return {"error": f"Failed to create task: {str(e)}"}


def list_tasks(
    session: Session,
    user_id: UUID,
    status: str = "all"
) -> Dict[str, Any]:
    """
    List all tasks for the user, optionally filtered by completion status.
    
    Args:
        session: Database session
        user_id: User UUID from JWT token
        status: Filter by status ('all', 'pending', 'completed')
        
    Returns:
        {"tasks": [...], "count": int}
    """
    try:
        query = select(Task).where(Task.user_id == user_id)
        
        if status == "pending":
            query = query.where(Task.completed == False)
        elif status == "completed":
            query = query.where(Task.completed == True)
        
        tasks = session.exec(query.order_by(col(Task.created_at).desc())).all()
        
        return {
            "tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat() if task.created_at else None
                }
                for task in tasks
            ],
            "count": len(tasks)
        }
    except Exception as e:
        return {"error": f"Failed to list tasks: {str(e)}"}


def complete_task(
    session: Session,
    user_id: UUID,
    task_id: int
) -> Dict[str, Any]:
    """
    Mark a task as completed.
    
    Args:
        session: Database session
        user_id: User UUID from JWT token
        task_id: ID of the task to complete
        
    Returns:
        {"task_id": int, "status": "completed", "title": str}
    """
    try:
        # Ensure user_id is UUID type
        if isinstance(user_id, str):
            user_id = UUID(user_id)
            
        task = session.exec(
            select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id
            )
        ).first()
        
        if not task:
            return {"error": "Task not found or access denied"}
        
        task.completed = True
        session.add(task)
        session.commit()
        session.refresh(task)
        
        return {
            "task_id": task.id,
            "status": "completed",
            "title": task.title
        }
    except Exception as e:
        session.rollback()
        return {"error": f"Failed to complete task: {str(e)}"}


def update_task(
    session: Session,
    user_id: UUID,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update task title and/or description.
    
    Args:
        session: Database session
        user_id: User UUID from JWT token
        task_id: ID of the task to update
        title: New task title (optional)
        description: New task description (optional)
        
    Returns:
        {"task_id": int, "status": "updated", "title": str}
    """
    try:
        # Ensure user_id is UUID type
        if isinstance(user_id, str):
            user_id = UUID(user_id)
            
        task = session.exec(
            select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id
            )
        ).first()
        
        if not task:
            return {"error": "Task not found or access denied"}
        
        if title:
            task.title = title
        if description is not None:
            task.description = description
        
        session.add(task)
        session.commit()
        session.refresh(task)
        
        return {
            "task_id": task.id,
            "status": "updated",
            "title": task.title
        }
    except Exception as e:
        session.rollback()
        return {"error": f"Failed to update task: {str(e)}"}


def delete_task(
    session: Session,
    user_id: UUID,
    task_id: int
) -> Dict[str, Any]:
    """
    Permanently delete a task.
    
    Args:
        session: Database session
        user_id: User UUID from JWT token
        task_id: ID of the task to delete
        
    Returns:
        {"task_id": int, "status": "deleted", "title": str}
    """
    try:
        # Ensure user_id is UUID type
        if isinstance(user_id, str):
            user_id = UUID(user_id)
            
        task = session.exec(
            select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id
            )
        ).first()
        
        if not task:
            return {"error": "Task not found or access denied"}
        
        title = task.title
        session.delete(task)
        session.commit()
        
        return {
            "task_id": task_id,
            "status": "deleted",
            "title": title
        }
    except Exception as e:
        session.rollback()
        return {"error": f"Failed to delete task: {str(e)}"}
