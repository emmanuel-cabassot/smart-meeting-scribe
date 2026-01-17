"""
Schémas Pydantic pour le modèle User avec contexte organisationnel.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List

from app.schemas.organization import ServiceMinimal, ProjectMinimal


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
    """Réponse utilisateur basique (sans info organisationnelle)."""
    id: int
    is_superuser: bool = False

    class Config:
        from_attributes = True


class UserWithContext(UserOut):
    """
    Réponse utilisateur avec contexte organisationnel complet.
    Utilisé pour l'endpoint /users/me pour peupler l'état du frontend.
    """
    service: Optional[ServiceMinimal] = None
    projects: List[ProjectMinimal] = []

    class Config:
        from_attributes = True


# ============================================================
# Schémas admin
# ============================================================

class UserAdminUpdate(BaseModel):
    """Mise à jour utilisateur réservée aux admins (peut changer service/projets)."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    service_id: Optional[int] = None
    project_ids: Optional[List[int]] = None
