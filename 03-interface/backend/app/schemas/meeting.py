"""
Schémas Pydantic pour le modèle Meeting avec support organisationnel.
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.schemas.organization import ServiceMinimal, ProjectMinimal


# ============================================================
# Schémas de base
# ============================================================

class MeetingBase(BaseModel):
    title: Optional[str] = None
    is_confidential: bool = False


class MeetingCreate(MeetingBase):
    """Schéma pour la création d'un meeting (upload)."""
    original_filename: str
    s3_path: str
    project_ids: Optional[List[int]] = None  # Tags de projet optionnels


class MeetingUpdate(BaseModel):
    """Schéma pour la mise à jour d'un meeting."""
    title: Optional[str] = None
    is_confidential: Optional[bool] = None
    project_ids: Optional[List[int]] = None  # Mise à jour des tags de projet


# ============================================================
# Schémas de réponse
# ============================================================

class MeetingOut(MeetingBase):
    """Réponse meeting basique."""
    id: int
    original_filename: str
    status: str
    created_at: datetime
    owner_id: Optional[int] = None
    
    class Config:
        from_attributes = True


class MeetingWithContext(MeetingOut):
    """Meeting avec contexte organisationnel complet."""
    service: Optional[ServiceMinimal] = None
    projects: List[ProjectMinimal] = []
    transcription_text: Optional[str] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MeetingList(BaseModel):
    """Liste paginée de meetings."""
    items: List[MeetingOut]
    total: int
    page: int
    size: int
