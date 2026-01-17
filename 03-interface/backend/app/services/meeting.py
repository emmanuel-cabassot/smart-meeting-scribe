"""
Logique métier pour les meetings avec visibilité matricielle.
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
    """Récupère un meeting par son ID avec les relations chargées."""
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
    Récupère les meetings visibles pour un utilisateur selon les règles matricielles :
    1. Meetings du service de l'utilisateur (si l'utilisateur a un service)
    2. Meetings taggés sur les projets de l'utilisateur (si non confidentiels)
    
    Filtres optionnels (appliqués en plus de la visibilité) :
    - service_id : Filtrer par service spécifique
    - project_id : Filtrer par projet spécifique
    - status : Filtrer par statut de transcription
    
    Cas limite : Si l'utilisateur n'a pas de service_id, seule la visibilité par projet s'applique.
    """
    # Récupère les IDs de projets de l'utilisateur
    user_project_ids = [p.id for p in user.projects] if user.projects else []
    
    # Construit les conditions de visibilité
    visibility_conditions = []
    
    # Condition A : Même service (seulement si l'utilisateur a un service)
    if user.service_id is not None:
        visibility_conditions.append(Meeting.service_id == user.service_id)
    
    # Condition B : Projet partagé (non confidentiel)
    if user_project_ids:
        visibility_conditions.append(
            and_(
                Meeting.is_confidential == False,
                Meeting.projects.any(Project.id.in_(user_project_ids))
            )
        )
    
    # Si pas de conditions de visibilité, l'utilisateur ne voit rien
    if not visibility_conditions:
        return []
    
    # Construit la requête de base avec la visibilité
    query = (
        select(Meeting)
        .options(
            selectinload(Meeting.service),
            selectinload(Meeting.projects),
            selectinload(Meeting.owner)
        )
        .where(or_(*visibility_conditions))
    )
    
    # Applique les filtres optionnels
    if service_id is not None:
        query = query.where(Meeting.service_id == service_id)
    
    if project_id is not None:
        query = query.where(Meeting.projects.any(Project.id == project_id))
    
    if status is not None:
        query = query.where(Meeting.status == status)
    
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
    
    Règles de sécurité :
    - service_id est automatiquement défini sur le service de l'utilisateur
    - project_ids doivent être des projets dont l'utilisateur est membre
    """
    # Valide les tags de projet (SÉCURITÉ : l'utilisateur doit être membre)
    valid_projects = []
    if meeting_in.project_ids:
        user_project_ids = {p.id for p in current_user.projects}
        
        for pid in meeting_in.project_ids:
            if pid not in user_project_ids:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Impossible de taguer le projet {pid} : vous n'êtes pas membre"
                )
        
        # Récupère les objets projet
        result = await db.execute(
            select(Project).where(Project.id.in_(meeting_in.project_ids))
        )
        valid_projects = list(result.scalars().all())
    
    # Crée le meeting
    meeting = Meeting(
        title=meeting_in.title,
        original_filename=meeting_in.original_filename,
        s3_path=meeting_in.s3_path,
        is_confidential=meeting_in.is_confidential,
        owner_id=current_user.id,
        service_id=current_user.service_id,  # Auto-défini depuis l'utilisateur
    )
    
    # Ajoute les projets validés
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
    Met à jour un meeting.
    Seul le propriétaire ou un superuser peut modifier.
    """
    # Vérifie les permissions
    if meeting.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non autorisé à modifier ce meeting"
        )
    
    # Met à jour les champs de base
    if meeting_in.title is not None:
        meeting.title = meeting_in.title
    if meeting_in.is_confidential is not None:
        meeting.is_confidential = meeting_in.is_confidential
    
    # Met à jour les tags de projet (avec validation de sécurité)
    if meeting_in.project_ids is not None:
        user_project_ids = {p.id for p in current_user.projects}
        
        for pid in meeting_in.project_ids:
            if pid not in user_project_ids and not current_user.is_superuser:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Impossible de taguer le projet {pid} : vous n'êtes pas membre"
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
