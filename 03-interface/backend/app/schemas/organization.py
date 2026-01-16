"""
Pydantic schemas for organization models (Service, Project).
"""
from pydantic import BaseModel
from typing import Optional


# ============================================================
# Service Schemas
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
    """Service with member count for admin views."""
    member_count: int = 0


# ============================================================
# Project Schemas
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
    """Project with member count for admin views."""
    member_count: int = 0


# ============================================================
# Lightweight schemas for embedding in other responses
# ============================================================

class ServiceMinimal(BaseModel):
    """Minimal service info for user context."""
    id: int
    name: str

    class Config:
        from_attributes = True


class ProjectMinimal(BaseModel):
    """Minimal project info for user context."""
    id: int
    name: str

    class Config:
        from_attributes = True
