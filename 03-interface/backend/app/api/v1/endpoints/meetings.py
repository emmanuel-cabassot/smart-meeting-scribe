"""
Meetings CRUD endpoints with matrix visibility.
"""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.meeting import Meeting, can_user_access_meeting
from app.schemas.meeting import MeetingOut, MeetingWithContext, MeetingUpdate
from app.services.meeting import (
    get_meeting, 
    get_meetings_for_user, 
    update_meeting, 
    delete_meeting
)

router = APIRouter()


@router.get("/", response_model=List[MeetingWithContext])
async def list_meetings(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    service_id: Optional[int] = Query(None, description="Filter by service ID"),
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    status: Optional[str] = Query(None, description="Filter by status (pending, processing, completed, error)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all meetings visible to the current user.
    
    Visibility rules (matrix logic):
    - Meetings from user's service (solidarity)
    - Meetings tagged with user's projects (if not confidential)
    
    Optional filters:
    - service_id: Filter by specific service
    - project_id: Filter by specific project
    - status: Filter by transcription status
    """
    # Load user with relationships for visibility check
    user_query = await db.execute(
        select(User)
        .options(selectinload(User.projects))
        .where(User.id == current_user.id)
    )
    user = user_query.scalar_one()
    
    meetings = await get_meetings_for_user(
        db, user, 
        skip=skip, 
        limit=limit,
        service_id=service_id,
        project_id=project_id,
        status=status
    )
    return meetings


@router.get("/mine", response_model=List[MeetingWithContext])
async def list_my_meetings(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List only meetings owned by the current user.
    """
    query = (
        select(Meeting)
        .options(
            selectinload(Meeting.service),
            selectinload(Meeting.projects),
            selectinload(Meeting.owner)
        )
        .where(Meeting.owner_id == current_user.id)
        .order_by(Meeting.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    
    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/{meeting_id}", response_model=MeetingWithContext)
async def get_meeting_detail(
    meeting_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific meeting by ID.
    
    Checks visibility before returning.
    """
    meeting = await get_meeting(db, meeting_id)
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    # Load user with projects for visibility check
    user_query = await db.execute(
        select(User)
        .options(selectinload(User.projects))
        .where(User.id == current_user.id)
    )
    user = user_query.scalar_one()
    
    # Check visibility
    if not can_user_access_meeting(user, meeting) and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="You don't have access to this meeting")
    
    return meeting


@router.patch("/{meeting_id}", response_model=MeetingWithContext)
async def update_meeting_endpoint(
    meeting_id: int,
    meeting_in: MeetingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a meeting.
    
    Only the owner or a superuser can update.
    """
    meeting = await get_meeting(db, meeting_id)
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    # Load user with projects for update validation
    user_query = await db.execute(
        select(User)
        .options(selectinload(User.projects))
        .where(User.id == current_user.id)
    )
    user = user_query.scalar_one()
    
    updated_meeting = await update_meeting(db, meeting, meeting_in, user)
    return updated_meeting


@router.delete("/{meeting_id}", status_code=204)
async def delete_meeting_endpoint(
    meeting_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a meeting.
    
    Only the owner or a superuser can delete.
    """
    meeting = await get_meeting(db, meeting_id)
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    # Load user for permission check
    user_query = await db.execute(
        select(User)
        .options(selectinload(User.projects))
        .where(User.id == current_user.id)
    )
    user = user_query.scalar_one()
    
    await delete_meeting(db, meeting, user)
    return None


@router.get("/stats/count")
async def get_meetings_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get count of meetings visible to the current user.
    """
    # Load user with projects
    user_query = await db.execute(
        select(User)
        .options(selectinload(User.projects))
        .where(User.id == current_user.id)
    )
    user = user_query.scalar_one()
    
    # Use the same visibility logic
    meetings = await get_meetings_for_user(db, user, skip=0, limit=10000)
    
    return {
        "total": len(meetings),
        "owned": len([m for m in meetings if m.owner_id == current_user.id])
    }
