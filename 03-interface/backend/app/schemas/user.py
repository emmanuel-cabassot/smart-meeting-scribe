"""
Schémas Pydantic pour le modèle User avec contexte de groupes.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List

from app.schemas.group import GroupMinimal


# ============================================================
# Schémas de base
# ============================================================

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    """Schéma pour l'inscription utilisateur."""
    password: str


class UserUpdate(BaseModel):
    """Schéma pour la mise à jour du profil utilisateur."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


# ============================================================
# Schémas de réponse
# ============================================================

class UserOut(UserBase):
    """Réponse utilisateur basique (sans groupes)."""
    id: int
    is_superuser: bool = False

    class Config:
        from_attributes = True


class UserWithContext(UserOut):
    """
    Réponse utilisateur avec ses groupes.
    Utilisé pour l'endpoint /users/me pour peupler l'état du frontend.
    """
    groups: List[GroupMinimal] = []

    class Config:
        from_attributes = True


# ============================================================
# Schémas admin
# ============================================================

class UserAdminUpdate(BaseModel):
    """Mise à jour utilisateur réservée aux admins (peut changer les groupes)."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    group_ids: Optional[List[int]] = None
