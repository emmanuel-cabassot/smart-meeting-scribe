"""
Pydantic schemas for User model with organization context.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List

from app.schemas.organization import ServiceMinimal, ProjectMinimal


# ============================================================
# Base schemas
# ============================================================

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    """Schema for user registration."""
    password: str


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


# ============================================================
# Response schemas
# ============================================================

class UserOut(UserBase):
    """Basic user response (no organization info)."""
    id: int
    is_superuser: bool = False

    class Config:
        from_attributes = True


class UserWithContext(UserOut):
    """
    User response with full organization context.
    Used for /users/me endpoint to populate frontend state.
    """
    service: Optional[ServiceMinimal] = None
    projects: List[ProjectMinimal] = []

    class Config:
        from_attributes = True


# ============================================================
# Admin schemas
# ============================================================

class UserAdminUpdate(BaseModel):
    """Admin-only user update (can change service/projects)."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    service_id: Optional[int] = None
    project_ids: Optional[List[int]] = None
