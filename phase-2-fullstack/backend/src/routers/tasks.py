"""
Task CRUD endpoints with user isolation.
[Task]: T-010 (Task Endpoints)
[From]: spec.md §6.2, plan.md §7
"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select
from uuid import UUID
from datetime import datetime
from typing import Optional
from src.database import get_session
from src.models.task import Task
from src.models.user import User
from src.schemas.task import (
    TaskCreateRequest,
    TaskUpdateRequest,
    TaskPatchRequest,
    TaskResponse,
    TaskListResponse
)
from src.utils.deps import get_current_user

router = APIRouter(prefix="/api/{user_id}/tasks", tags=["tasks"])


@router.get("", response_model=TaskListResponse)
def list_tasks(
    user_id: UUID,
    completed: Optional[str] = "all",  # all, pending, completed
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    List all tasks for authenticated user.
    
    Query params:
    - completed: Filter by status (all, pending, completed)
    """
    # CRITICAL: Verify path user_id matches authenticated user
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found"
        )
    
    # Build query with user_id filter
    query = select(Task).where(Task.user_id == current_user.id)
    
    # Apply completion filter
    if completed == "pending":
        query = query.where(Task.completed == False)
    elif completed == "completed":
        query = query.where(Task.completed == True)
    # "all" - no additional filter
    
    # Execute query
    tasks = session.exec(query.order_by(Task.created_at.desc())).all()
    
    return TaskListResponse(
        tasks=[TaskResponse.model_validate(task) for task in tasks],
        count=len(tasks)
    )


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    user_id: UUID,
    request: TaskCreateRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create new task for authenticated user."""
    # CRITICAL: Verify path user_id matches authenticated user
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found"
        )
    
    # Create task
    task = Task(
        user_id=current_user.id,
        title=request.title,
        description=request.description,
        completed=False
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    
    return TaskResponse.model_validate(task)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    user_id: UUID,
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get single task by ID."""
    # CRITICAL: Verify path user_id matches authenticated user
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found"
        )
    
    # Get task with user_id filter
    task = session.exec(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == current_user.id
        )
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return TaskResponse.model_validate(task)


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    user_id: UUID,
    task_id: int,
    request: TaskUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update task (full update)."""
    # CRITICAL: Verify path user_id matches authenticated user
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found"
        )
    
    # Get task with user_id filter
    task = session.exec(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == current_user.id
        )
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Update fields
    if request.title is not None:
        task.title = request.title
    if request.description is not None:
        task.description = request.description
    
    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)
    
    return TaskResponse.model_validate(task)


@router.patch("/{task_id}", response_model=TaskResponse)
def patch_task(
    user_id: UUID,
    task_id: int,
    request: TaskPatchRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Toggle task completion status."""
    # CRITICAL: Verify path user_id matches authenticated user
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found"
        )
    
    # Get task with user_id filter
    task = session.exec(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == current_user.id
        )
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Update completion status
    task.completed = request.completed
    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)
    
    return TaskResponse.model_validate(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    user_id: UUID,
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete task."""
    # CRITICAL: Verify path user_id matches authenticated user
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found"
        )
    
    # Get task with user_id filter
    task = session.exec(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == current_user.id
        )
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Delete task
    session.delete(task)
    session.commit()
    
    return None
