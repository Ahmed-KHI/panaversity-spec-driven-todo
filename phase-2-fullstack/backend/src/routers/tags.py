"""
Tag CRUD endpoints for task organization.
[Task]: T-B-005 (Tag Management)
[From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §2.4, §5.2,
        specs/005-phase-v-cloud/phase5-cloud.plan.md §3.1.2, §4.2
"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select
from uuid import UUID
from datetime import datetime
from src.database import get_session
from src.models.tag import Tag, TaskTag
from src.models.user import User
from src.schemas.tag import TagCreate, TagUpdate, TagResponse, TagListResponse
from src.utils.deps import get_current_user

router = APIRouter(prefix="/api/{user_id}/tags", tags=["tags"])


@router.get("", response_model=TagListResponse)
def list_tags(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    List all tags for authenticated user.
    
    [Task]: T-B-005
    [From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §5.2.1
    """
    # CRITICAL: Verify path user_id matches authenticated user
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found"
        )
    
    # Get tags created by user or used by user's tasks
    tags = session.exec(
        select(Tag).where(Tag.created_by == current_user.id)
    ).all()
    
    return TagListResponse(
        tags=[TagResponse.model_validate(tag) for tag in tags],
        count=len(tags)
    )


@router.post("", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(
    user_id: UUID,
    request: TagCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Create new tag.
    
    [Task]: T-B-005
    [From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §5.2.2
    """
    # CRITICAL: Verify path user_id matches authenticated user
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found"
        )
    
    # Check if tag name already exists
    existing_tag = session.exec(
        select(Tag).where(Tag.name == request.name)
    ).first()
    
    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tag '{request.name}' already exists"
        )
    
    # Create tag
    tag = Tag(
        name=request.name,
        color=request.color if request.color else "#3B82F6",
        created_by=current_user.id
    )
    session.add(tag)
    session.commit()
    session.refresh(tag)
    
    return TagResponse.model_validate(tag)


@router.get("/{tag_id}", response_model=TagResponse)
def get_tag(
    user_id: UUID,
    tag_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get tag by ID.
    
    [Task]: T-B-005
    [From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §5.2.1
    """
    # CRITICAL: Verify path user_id matches authenticated user
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found"
        )
    
    tag = session.exec(
        select(Tag).where(
            Tag.id == tag_id,
            Tag.created_by == current_user.id
        )
    ).first()
    
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    
    return TagResponse.model_validate(tag)


@router.put("/{tag_id}", response_model=TagResponse)
def update_tag(
    user_id: UUID,
    tag_id: int,
    request: TagUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update tag.
    
    [Task]: T-B-005
    [From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §5.2.3
    """
    # CRITICAL: Verify path user_id matches authenticated user
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found"
        )
    
    tag = session.exec(
        select(Tag).where(
            Tag.id == tag_id,
            Tag.created_by == current_user.id
        )
    ).first()
    
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    
    # Update fields
    if request.name is not None:
        # Check if new name conflicts
        existing = session.exec(
            select(Tag).where(
                Tag.name == request.name,
                Tag.id != tag_id
            )
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tag '{request.name}' already exists"
            )
        tag.name = request.name
    
    if request.color is not None:
        tag.color = request.color
    
    session.add(tag)
    session.commit()
    session.refresh(tag)
    
    return TagResponse.model_validate(tag)


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(
    user_id: UUID,
    tag_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete tag and remove all task associations.
    
    [Task]: T-B-005
    [From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §5.2.4
    """
    # CRITICAL: Verify path user_id matches authenticated user
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found"
        )
    
    tag = session.exec(
        select(Tag).where(
            Tag.id == tag_id,
            Tag.created_by == current_user.id
        )
    ).first()
    
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    
    # Delete all task-tag associations first
    task_tags = session.exec(
        select(TaskTag).where(TaskTag.tag_id == tag_id)
    ).all()
    for tt in task_tags:
        session.delete(tt)
    
    # Delete tag
    session.delete(tag)
    session.commit()
    
    return None
