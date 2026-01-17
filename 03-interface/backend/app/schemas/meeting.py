"""
Schémas Pydantic pour le modèle Meeting avec groupes.
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.schemas.group import GroupMinimal


# ============================================================
# Schémas de base
# ============================================================

class MeetingBase(BaseModel):
    title: Optional[str] = None


class MeetingCreate(MeetingBase):
    """Schéma pour la création d'un meeting (upload)."""
    original_filename: str
    s3_path: str
    group_ids: List[int]  # Requis : au moins un groupe


class MeetingUpdate(BaseModel):
    """Schéma pour la mise à jour d'un meeting."""
    title: Optional[str] = None
    group_ids: Optional[List[int]] = None  # Mise à jour des groupes


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
    """Meeting avec ses groupes."""
    groups: List[GroupMinimal] = []
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
