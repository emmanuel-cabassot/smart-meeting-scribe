"""
Logique métier pour les meetings avec visibilité par groupes.
"""
from typing import List, Optional
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.meeting import Meeting, can_user_access_meeting
from app.models.group import Group
from app.models.user import User
from app.schemas.meeting import MeetingCreate, MeetingUpdate


async def get_meeting(db: AsyncSession, meeting_id: int) -> Optional[Meeting]:
    """Récupère un meeting par son ID avec les relations chargées."""
    result = await db.execute(
        select(Meeting)
        .options(
            selectinload(Meeting.groups),
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
    group_id: Optional[int] = None,
    status_filter: Optional[str] = None,
) -> List[Meeting]:
    """
    Récupère les meetings visibles pour un utilisateur.
    
    Règle : Un utilisateur voit un meeting s'il partage au moins un groupe avec lui.
    
    Filtres optionnels :
    - group_id : Filtrer par groupe spécifique
    - status_filter : Filtrer par statut de transcription
    """
    # Récupère les IDs de groupes de l'utilisateur
    user_group_ids = [g.id for g in user.groups] if user.groups else []
    
    # Si pas de groupes, l'utilisateur ne voit rien
    if not user_group_ids:
        return []
    
    # Condition de visibilité : le meeting a au moins un groupe de l'utilisateur
    query = (
        select(Meeting)
        .options(
            selectinload(Meeting.groups),
            selectinload(Meeting.owner)
        )
        .where(Meeting.groups.any(Group.id.in_(user_group_ids)))
    )
    
    # Applique les filtres optionnels
    if group_id is not None:
        query = query.where(Meeting.groups.any(Group.id == group_id))
    
    if status_filter is not None:
        query = query.where(Meeting.status == status_filter)
    
    # Applique l'ordre et la pagination
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
    Crée un meeting avec validation de sécurité.
    
    Règle : L'utilisateur doit être membre des groupes qu'il assigne au meeting.
    """
    # Valide les groupes (SÉCURITÉ : l'utilisateur doit être membre)
    user_group_ids = {g.id for g in current_user.groups}
    
    for gid in meeting_in.group_ids:
        if gid not in user_group_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Impossible d'assigner le groupe {gid} : vous n'êtes pas membre"
            )
    
    # Récupère les objets groupe
    result = await db.execute(
        select(Group).where(Group.id.in_(meeting_in.group_ids))
    )
    groups = list(result.scalars().all())
    
    if not groups:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Au moins un groupe valide est requis"
        )
    
    # Crée le meeting
    meeting = Meeting(
        title=meeting_in.title,
        original_filename=meeting_in.original_filename,
        s3_path=meeting_in.s3_path,
        owner_id=current_user.id,
    )
    meeting.groups = groups
    
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
    Met à jour un meeting.
    Seul le propriétaire ou un superuser peut modifier.
    """
    # Vérifie les permissions
    if meeting.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non autorisé à modifier ce meeting"
        )
    
    # Met à jour le titre
    if meeting_in.title is not None:
        meeting.title = meeting_in.title
    
    # Met à jour les groupes (avec validation de sécurité)
    if meeting_in.group_ids is not None:
        user_group_ids = {g.id for g in current_user.groups}
        
        for gid in meeting_in.group_ids:
            if gid not in user_group_ids and not current_user.is_superuser:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Impossible d'assigner le groupe {gid} : vous n'êtes pas membre"
                )
        
        result = await db.execute(
            select(Group).where(Group.id.in_(meeting_in.group_ids))
        )
        meeting.groups = list(result.scalars().all())
    
    await db.commit()
    await db.refresh(meeting)
    
    return meeting


async def delete_meeting(
    db: AsyncSession,
    meeting: Meeting,
    current_user: User
) -> None:
    """
    Supprime un meeting.
    Seul le propriétaire ou un superuser peut supprimer.
    """
    if meeting.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non autorisé à supprimer ce meeting"
        )
    
    await db.delete(meeting)
    await db.commit()
