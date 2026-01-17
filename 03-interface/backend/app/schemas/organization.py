"""
Schémas Pydantic pour les modèles organisationnels (Service, Projet).
"""
from pydantic import BaseModel
from typing import Optional


# ============================================================
# Schémas Service
# ============================================================

class ServiceBase(BaseModel):
    name: str
    description: Optional[str] = None


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class ServiceRead(ServiceBase):
    id: int

    class Config:
        from_attributes = True


class ServiceWithCount(ServiceRead):
    """Service avec compteur de membres pour les vues admin."""
    member_count: int = 0


# ============================================================
# Schémas Projet
# ============================================================

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ProjectRead(ProjectBase):
    id: int

    class Config:
        from_attributes = True


class ProjectWithCount(ProjectRead):
    """Projet avec compteur de membres pour les vues admin."""
    member_count: int = 0


# ============================================================
# Schémas légers pour l'intégration dans d'autres réponses
# ============================================================

class ServiceMinimal(BaseModel):
    """Info service minimale pour le contexte utilisateur."""
    id: int
    name: str

    class Config:
        from_attributes = True


class ProjectMinimal(BaseModel):
    """Info projet minimale pour le contexte utilisateur."""
    id: int
    name: str

    class Config:
        from_attributes = True
