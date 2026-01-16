"""
Business logic for meetings with matrix visibility.
"""
from typing import List, Optional
from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.meeting import Meeting, can_user_access_meeting
from app.models.organization import Project
from app.models.user import User
from app.schemas.meeting import MeetingCreate, MeetingUpdate


async def get_meeting(db: AsyncSession, meeting_id: int) -> Optional[Meeting]:
    """Get a meeting by ID with relationships loaded."""
    result = await db.execute(
        select(Meeting)
        .options(
            selectinload(Meeting.service),
            selectinload(Meeting.projects),
            selectinload(Meeting.owner)
        )
        .where(Meeting.id == meeting_id)
    )
    return result.scalar_one_or_none()


async def get_meetings_for_user(
    db: AsyncSession, 
    user: User,
    skip: int = 0,
    limit: int = 50,
    service_id: Optional[int] = None,
    project_id: Optional[int] = None,
    status: Optional[str] = None,
) -> List[Meeting]:
    """
    Get meetings visible to a user based on matrix rules:
    1. Meetings from user's service (if user has a service)
    2. Meetings tagged with user's projects (if not confidential)
    
    Optional filters (applied on top of visibility):
    - service_id: Filter by specific service
    - project_id: Filter by specific project
    - status: Filter by transcription status
    
    Edge case: If user has no service_id, only project-based visibility applies.
    """
    # Get user's project IDs
    user_project_ids = [p.id for p in user.projects] if user.projects else []
    
    # Build visibility conditions
    visibility_conditions = []
    
    # Condition A: Same service (only if user has a service)
    if user.service_id is not None:
        visibility_conditions.append(Meeting.service_id == user.service_id)
    
    # Condition B: Shared project (non-confidential)
    if user_project_ids:
        visibility_conditions.append(
            and_(
                Meeting.is_confidential == False,
                Meeting.projects.any(Project.id.in_(user_project_ids))
            )
        )
    
    # If no visibility conditions, user sees nothing
    if not visibility_conditions:
        return []
    
    # Build the base query with visibility
    query = (
        select(Meeting)
        .options(
            selectinload(Meeting.service),
            selectinload(Meeting.projects),
            selectinload(Meeting.owner)
        )
        .where(or_(*visibility_conditions))
    )
    
    # Apply optional filters
    if service_id is not None:
        query = query.where(Meeting.service_id == service_id)
    
    if project_id is not None:
        query = query.where(Meeting.projects.any(Project.id == project_id))
    
    if status is not None:
        query = query.where(Meeting.status == status)
    
    # Apply ordering and pagination
    query = (
        query
        .order_by(Meeting.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_meeting(
    db: AsyncSession,
    meeting_in: MeetingCreate,
    current_user: User
) -> Meeting:
    """
    Create a meeting with security validation.
    
    Security rules:
    - service_id is automatically set to user's service
    - project_ids must be projects the user belongs to
    """
    # Validate project tagging (SECURITY: user must be member)
    valid_projects = []
    if meeting_in.project_ids:
        user_project_ids = {p.id for p in current_user.projects}
        
        for pid in meeting_in.project_ids:
            if pid not in user_project_ids:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Cannot tag project {pid}: you are not a member"
                )
        
        # Fetch project objects
        result = await db.execute(
            select(Project).where(Project.id.in_(meeting_in.project_ids))
        )
        valid_projects = list(result.scalars().all())
    
    # Create meeting
    meeting = Meeting(
        title=meeting_in.title,
        original_filename=meeting_in.original_filename,
        s3_path=meeting_in.s3_path,
        is_confidential=meeting_in.is_confidential,
        owner_id=current_user.id,
        service_id=current_user.service_id,  # Auto-set from user
    )
    
    # Add validated projects
    if valid_projects:
        meeting.projects = valid_projects
    
    db.add(meeting)
    await db.commit()
    await db.refresh(meeting)
    
    return meeting


async def update_meeting(
    db: AsyncSession,
    meeting: Meeting,
    meeting_in: MeetingUpdate,
    current_user: User
) -> Meeting:
    """
    Update a meeting.
    Only owner or superuser can update.
    """
    # Check permission
    if meeting.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to update this meeting"
        )
    
    # Update basic fields
    if meeting_in.title is not None:
        meeting.title = meeting_in.title
    if meeting_in.is_confidential is not None:
        meeting.is_confidential = meeting_in.is_confidential
    
    # Update project tags (with security validation)
    if meeting_in.project_ids is not None:
        user_project_ids = {p.id for p in current_user.projects}
        
        for pid in meeting_in.project_ids:
            if pid not in user_project_ids and not current_user.is_superuser:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Cannot tag project {pid}: you are not a member"
                )
        
        result = await db.execute(
            select(Project).where(Project.id.in_(meeting_in.project_ids))
        )
        meeting.projects = list(result.scalars().all())
    
    await db.commit()
    await db.refresh(meeting)
    
    return meeting


async def delete_meeting(
    db: AsyncSession,
    meeting: Meeting,
    current_user: User
) -> None:
    """
    Delete a meeting.
    Only owner or superuser can delete.
    """
    if meeting.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to delete this meeting"
        )
    
    await db.delete(meeting)
    await db.commit()
