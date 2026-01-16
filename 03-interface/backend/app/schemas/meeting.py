"""
Pydantic schemas for Meeting model with organization support.
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.schemas.organization import ServiceMinimal, ProjectMinimal


# ============================================================
# Base schemas
# ============================================================

class MeetingBase(BaseModel):
    title: Optional[str] = None
    is_confidential: bool = False


class MeetingCreate(MeetingBase):
    """Schema for creating a meeting (upload)."""
    original_filename: str
    s3_path: str
    project_ids: Optional[List[int]] = None  # Optional project tagging


class MeetingUpdate(BaseModel):
    """Schema for updating a meeting."""
    title: Optional[str] = None
    is_confidential: Optional[bool] = None
    project_ids: Optional[List[int]] = None  # Update project tags


# ============================================================
# Response schemas
# ============================================================

class MeetingOut(MeetingBase):
    """Basic meeting response."""
    id: int
    original_filename: str
    status: str
    created_at: datetime
    owner_id: Optional[int] = None
    
    class Config:
        from_attributes = True


class MeetingWithContext(MeetingOut):
    """Meeting with full organization context."""
    service: Optional[ServiceMinimal] = None
    projects: List[ProjectMinimal] = []
    transcription_text: Optional[str] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MeetingList(BaseModel):
    """Paginated list of meetings."""
    items: List[MeetingOut]
    total: int
    page: int
    size: int
