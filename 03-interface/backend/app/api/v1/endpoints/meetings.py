"""
Endpoints CRUD pour les Meetings avec visibilité matricielle.
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
    service_id: Optional[int] = Query(None, description="Filtrer par ID de service"),
    project_id: Optional[int] = Query(None, description="Filtrer par ID de projet"),
    status: Optional[str] = Query(None, description="Filtrer par statut (pending, processing, completed, error)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Liste tous les meetings visibles pour l'utilisateur courant.
    
    Règles de visibilité (logique matricielle) :
    - Meetings du service de l'utilisateur (solidarité)
    - Meetings taggés avec les projets de l'utilisateur (si non confidentiel)
    
    Filtres optionnels :
    - service_id : Filtrer par service spécifique
    - project_id : Filtrer par projet spécifique
    - status : Filtrer par statut de transcription
    """
    # Charge l'utilisateur avec ses relations pour la vérification de visibilité
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
    Liste uniquement les meetings créés par l'utilisateur courant.
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
    Récupère un meeting spécifique par son ID.
    
    Vérifie la visibilité avant de retourner le résultat.
    """
    meeting = await get_meeting(db, meeting_id)
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting introuvable")
    
    # Charge l'utilisateur avec ses projets pour la vérification de visibilité
    user_query = await db.execute(
        select(User)
        .options(selectinload(User.projects))
        .where(User.id == current_user.id)
    )
    user = user_query.scalar_one()
    
    # Vérifie la visibilité
    if not can_user_access_meeting(user, meeting) and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Vous n'avez pas accès à ce meeting")
    
    return meeting


@router.patch("/{meeting_id}", response_model=MeetingWithContext)
async def update_meeting_endpoint(
    meeting_id: int,
    meeting_in: MeetingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Met à jour un meeting.
    
    Seul le propriétaire ou un superuser peut modifier.
    """
    meeting = await get_meeting(db, meeting_id)
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting introuvable")
    
    # Charge l'utilisateur avec ses projets pour la validation de mise à jour
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
    Supprime un meeting.
    
    Seul le propriétaire ou un superuser peut supprimer.
    """
    meeting = await get_meeting(db, meeting_id)
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting introuvable")
    
    # Charge l'utilisateur pour la vérification des permissions
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
    Récupère le nombre de meetings visibles pour l'utilisateur courant.
    """
    # Charge l'utilisateur avec ses projets
    user_query = await db.execute(
        select(User)
        .options(selectinload(User.projects))
        .where(User.id == current_user.id)
    )
    user = user_query.scalar_one()
    
    # Utilise la même logique de visibilité
    meetings = await get_meetings_for_user(db, user, skip=0, limit=10000)
    
    return {
        "total": len(meetings),
        "owned": len([m for m in meetings if m.owner_id == current_user.id])
    }
