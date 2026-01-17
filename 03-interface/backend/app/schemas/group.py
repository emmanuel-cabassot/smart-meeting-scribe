"""
Schémas Pydantic pour le modèle Group.
"""
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class GroupType(str, Enum):
    """Types de groupes."""
    DEPARTMENT = "department"
    PROJECT = "project"
    RECURRING = "recurring"


# ============================================================
# Schémas de base
# ============================================================

class GroupBase(BaseModel):
    name: str
    description: Optional[str] = None
    type: GroupType = GroupType.DEPARTMENT


class GroupCreate(GroupBase):
    """Schéma pour la création d'un groupe."""
    pass


class GroupUpdate(BaseModel):
    """Schéma pour la mise à jour d'un groupe."""
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[GroupType] = None
    is_active: Optional[bool] = None


# ============================================================
# Schémas de réponse
# ============================================================

class GroupRead(GroupBase):
    """Réponse complète d'un groupe."""
    id: int
    is_active: bool

    class Config:
        from_attributes = True


class GroupWithCount(GroupRead):
    """Groupe avec compteur de membres pour les vues admin."""
    member_count: int = 0


class GroupMinimal(BaseModel):
    """Info groupe minimale pour le contexte utilisateur/meeting."""
    id: int
    name: str
    type: GroupType

    class Config:
        from_attributes = True
