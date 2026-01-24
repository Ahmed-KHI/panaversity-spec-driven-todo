"""
Task CRUD endpoints with user isolation.
[Task]: T-010 (Task Endpoints), T-B-001 through T-B-009 (Phase V Enhancements),
        T-C-002, T-C-003, T-C-004 (Event Publishing)
[From]: specs/phase1-console-app.specify.md §6.2, plan.md §7,
        specs/005-phase-v-cloud/phase5-cloud.specify.md §2.1-2.5, §3.1, §5.1,
        specs/005-phase-v-cloud/phase5-cloud.plan.md §3.1, §4.1, §5.1-5.2
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlmodel import Session, select, or_, and_, col
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from src.database import get_session
from src.models.task import Task
from src.models.tag import Tag, TaskTag
from src.models.user import User
from src.schemas.task import (
    TaskCreateRequest,
    TaskUpdateRequest,
    TaskPatchRequest,
    TaskResponse,
    TaskListResponse,
    TaskSearchFilters,
    TagResponse
)
from src.utils.deps import get_current_user
from src.utils.validators import validate_task_data
from src.services.event_publisher import get_event_publisher

router = APIRouter(prefix="/api/{user_id}/tasks", tags=["tasks"])


# ===== Helper Functions =====

def _load_task_with_tags(task_id: int, session: Session) -> TaskResponse:
    """
    Load task with associated tags.
    
    [Task]: T-B-001, T-B-009
    [From]: specs/005-phase-v-cloud/phase5-cloud.plan.md §4.1
    """
    task = session.exec(
        select(Task).where(Task.id == task_id)
    ).first()
    
    if not task:
        return None
    
    # Load tags
    task_tags = session.exec(
        select(TaskTag).where(TaskTag.task_id == task_id)
    ).all()
    
    tags = []
    for tt in task_tags:
        tag = session.exec(
            select(Tag).where(Tag.id == tt.tag_id)
        ).first()
        if tag:
            tags.append(TagResponse.model_validate(tag))
    
    # Build response
    task_dict = task.model_dump()
    task_dict['tags'] = tags
    
    return TaskResponse.model_validate(task_dict)


# ===== Endpoints =====


@router.get("", response_model=TaskListResponse)
def list_tasks(
    user_id: UUID,
    completed: Optional[str] = Query("all", description="Filter: all, pending, completed"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    priority: Optional[List[str]] = Query(None, description="Filter by priorities"),
    tags: Optional[List[str]] = Query(None, description="Filter by tag names"),
    due_before: Optional[datetime] = Query(None, description="Tasks due before this date"),
    due_after: Optional[datetime] = Query(None, description="Tasks due after this date"),
    is_recurring: Optional[bool] = Query(None, description="Filter recurring tasks"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    List all tasks for authenticated user with advanced search, filter, and sort.
    
    [Task]: T-B-002 (Search), T-B-003 (Filter), T-B-004 (Sort), T-B-009 (Enhanced List)
    [From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §2.5, §5.1.2-5.1.4
    
    Query params:
    - completed: Filter by status (all, pending, completed)
    - search: Search in title and description (case-insensitive)
    - priority: Filter by priority levels (can be multiple)
    - tags: Filter by tag names (AND logic - task must have all tags)
    - due_before, due_after: Date range filter
    - is_recurring: Filter recurring/non-recurring tasks
    - sort_by: Field to sort by (created_at, updated_at, due_date, priority, title)
    - sort_order: asc or desc
    - page, page_size: Pagination
    """
    # CRITICAL: Verify path user_id matches authenticated user
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found"
        )
    
    # Build base query with user_id filter
    query = select(Task).where(Task.user_id == current_user.id)
    
    # Apply completion filter
    if completed == "pending":
        query = query.where(Task.completed == False)
    elif completed == "completed":
        query = query.where(Task.completed == True)
    
    # Apply search filter
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                Task.title.ilike(search_pattern),
                Task.description.ilike(search_pattern)
            )
        )
    
    # Apply priority filter
    if priority:
        from src.models.task import Priority
        priority_values = [Priority(p) for p in priority]
        query = query.where(Task.priority.in_(priority_values))
    
    # Apply date range filters
    if due_before:
        query = query.where(Task.due_date <= due_before)
    if due_after:
        query = query.where(Task.due_date >= due_after)
    
    # Apply recurring filter
    if is_recurring is not None:
        query = query.where(Task.is_recurring == is_recurring)
    
    # Apply tag filter (AND logic)
    if tags:
        for tag_name in tags:
            tag = session.exec(
                select(Tag).where(Tag.name == tag_name)
            ).first()
            if tag:
                # Subquery to check task has this tag
                query = query.where(
                    Task.id.in_(
                        select(TaskTag.task_id).where(TaskTag.tag_id == tag.id)
                    )
                )
    
    # Apply sorting
    sort_field = Task.created_at  # Default
    if sort_by == "updated_at":
        sort_field = Task.updated_at
    elif sort_by == "due_date":
        sort_field = Task.due_date
    elif sort_by == "priority":
        sort_field = Task.priority
    elif sort_by == "title":
        sort_field = Task.title
    
    if sort_order == "asc":
        query = query.order_by(sort_field.asc())
    else:
        query = query.order_by(sort_field.desc())
    
    # Execute query and get total count
    all_tasks = session.exec(query).all()
    total_count = len(all_tasks)
    
    # Apply pagination
    offset = (page - 1) * page_size
    tasks = all_tasks[offset:offset + page_size]
    
    # Load tasks with tags
    tasks_with_tags = [_load_task_with_tags(task.id, session) for task in tasks]
    
    return TaskListResponse(
        tasks=tasks_with_tags,
        count=total_count
    )


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    user_id: UUID,
    request: TaskCreateRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Create new task for authenticated user with Phase V advanced features.
    
    [Task]: T-B-001, T-B-007, T-B-008
    [From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §2.1-2.5, §5.1.1
    """
    # CRITICAL: Verify path user_id matches authenticated user
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found"
        )
    
    # Validate task data (T-B-007, T-B-008)
    validate_task_data(
        title=request.title,
        due_date=request.due_date,
        reminder_time=request.reminder_time,
        is_recurring=request.is_recurring,
        recurrence_pattern=request.recurrence_pattern.model_dump() if request.recurrence_pattern else None
    )
    
    # Create task with Phase V fields
    task = Task(
        user_id=current_user.id,
        title=request.title,
        description=request.description,
        completed=False,
        priority=request.priority,
        due_date=request.due_date,
        reminder_time=request.reminder_time,
        is_recurring=request.is_recurring
    )
    
    # Handle recurrence pattern
    if request.recurrence_pattern:
        task.recurrence_pattern = request.recurrence_pattern.model_dump()
    
    session.add(task)
    session.flush()  # Get task ID before adding tags
    
    # Handle tags
    if request.tags:
        for tag_name in request.tags:
            # Find or create tag
            tag = session.exec(
                select(Tag).where(Tag.name == tag_name)
            ).first()
            
            if not tag:
                tag = Tag(
                    name=tag_name,
                    color="#3B82F6",  # Default blue
                    created_by=current_user.id
                )
                session.add(tag)
                session.flush()
            
            # Associate tag with task
            task_tag = TaskTag(task_id=task.id, tag_id=tag.id)
            session.add(task_tag)
    
    session.commit()
    session.refresh(task)
    
    # Publish task.created event (T-C-002)
    try:
        event_publisher = get_event_publisher()
        event_publisher.publish_task_created(
            task_id=task.id,
            user_id=str(current_user.id),
            task_data={
                "title": task.title,
                "description": task.description,
                "priority": task.priority.value,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "reminder_time": task.reminder_time.isoformat() if task.reminder_time else None,
                "is_recurring": task.is_recurring,
                "recurrence_pattern": task.recurrence_pattern,
                "tags": request.tags if request.tags else []
            },
            session=session
        )
    except Exception as e:
        print(f"⚠️  Event publishing failed: {e}")
        # Continue execution even if event publishing fails
    
    # Publish reminder.scheduled event if reminder is set (T-C-009)
    if task.reminder_time:
        try:
            event_publisher.publish_reminder_scheduled(
                task_id=task.id,
                user_id=str(current_user.id),
                reminder_time=task.reminder_time.isoformat(),
                session=session
            )
        except Exception as e:
            print(f"⚠️  Reminder scheduling failed: {e}")
    
    # Load task with tags for response
    task_with_tags = _load_task_with_tags(task.id, session)
    return task_with_tags


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    user_id: UUID,
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get single task by ID with tags.
    
    [Task]: T-B-009
    [From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §5.1.2
    """
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
    
    return _load_task_with_tags(task.id, session)


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    user_id: UUID,
    task_id: int,
    request: TaskUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update task (full update) with Phase V fields.
    
    [Task]: T-B-001, T-B-007, T-B-008
    [From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §5.1.1
    """
    # CRITICAL: Verify path user_id matches authenticated user
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found"
        )
    
    # Validate task data (T-B-007, T-B-008)
    validate_task_data(
        title=request.title,
        due_date=request.due_date,
        reminder_time=request.reminder_time,
        is_recurring=request.is_recurring if request.is_recurring is not None else False,
        recurrence_pattern=request.recurrence_pattern.model_dump() if request.recurrence_pattern else None
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
    
    # Update basic fields
    if request.title is not None:
        task.title = request.title
    if request.description is not None:
        task.description = request.description
    
    # Update Phase V fields
    if request.priority is not None:
        task.priority = request.priority
    if request.due_date is not None:
        task.due_date = request.due_date
    if request.reminder_time is not None:
        task.reminder_time = request.reminder_time
    if request.is_recurring is not None:
        task.is_recurring = request.is_recurring
    if request.recurrence_pattern is not None:
        task.recurrence_pattern = request.recurrence_pattern.model_dump()
    
    # Update tags if provided
    if request.tags is not None:
        # Remove existing tags
        session.exec(
            select(TaskTag).where(TaskTag.task_id == task_id)
        ).all()
        for tt in session.exec(select(TaskTag).where(TaskTag.task_id == task_id)).all():
            session.delete(tt)
        
        # Add new tags
        for tag_name in request.tags:
            tag = session.exec(
                select(Tag).where(Tag.name == tag_name)
            ).first()
            
            if not tag:
                tag = Tag(
                    name=tag_name,
                    color="#3B82F6",
                    created_by=current_user.id
                )
                session.add(tag)
                session.flush()
            
            task_tag = TaskTag(task_id=task.id, tag_id=tag.id)
            session.add(task_tag)
    
    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)
    
    # Publish task.updated event (T-C-003)
    try:
        event_publisher = get_event_publisher()
        changes = {}
        if request.title is not None:
            changes["title"] = request.title
        if request.description is not None:
            changes["description"] = request.description
        if request.priority is not None:
            changes["priority"] = request.priority.value
        if request.due_date is not None:
            changes["due_date"] = request.due_date.isoformat()
        if request.reminder_time is not None:
            changes["reminder_time"] = request.reminder_time.isoformat()
        if request.is_recurring is not None:
            changes["is_recurring"] = request.is_recurring
        if request.recurrence_pattern is not None:
            changes["recurrence_pattern"] = request.recurrence_pattern.model_dump()
        if request.tags is not None:
            changes["tags"] = request.tags
        
        event_publisher.publish_task_updated(
            task_id=task.id,
            user_id=str(current_user.id),
            changes=changes,
            session=session
        )
    except Exception as e:
        print(f"⚠️  Event publishing failed: {e}")
    
    return _load_task_with_tags(task.id, session)


@router.patch("/{task_id}", response_model=TaskResponse)
def patch_task(
    user_id: UUID,
    task_id: int,
    request: TaskPatchRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Toggle task completion status.
    
    [Task]: T-B-006, T-C-004
    [From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §3.1.3
    """
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
    
    # Publish task.completed event (T-C-004)
    try:
        event_publisher = get_event_publisher()
        event_publisher.publish_task_completed(
            task_id=task.id,
            user_id=str(current_user.id),
            completed=request.completed,
            session=session
        )
    except Exception as e:
        print(f"⚠️  Event publishing failed: {e}")
    
    return _load_task_with_tags(task.id, session)


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
    
    # Publish task.deleted event
    try:
        event_publisher = get_event_publisher()
        event_publisher.publish_task_deleted(
            task_id=task.id,
            user_id=str(current_user.id),
            session=session
        )
    except Exception as e:
        print(f"⚠️  Event publishing failed: {e}")
    
    # Delete task
    session.delete(task)
    session.commit()
    
    return None
