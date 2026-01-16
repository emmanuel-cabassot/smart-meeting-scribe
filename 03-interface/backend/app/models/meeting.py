"""
Meeting model with organization relationships and visibility logic.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base
from app.models.organization import meeting_project_link


class Meeting(Base):
    """
    Meeting model with matrix visibility support.
    
    Visibility Rules:
    1. Service members can see all meetings of their service (unless confidential)
    2. Project members can see meetings tagged to their projects (unless confidential)
    3. Confidential meetings are ONLY visible to service members
    
    Ownership Rules:
    - service_id is automatically set to the owner's service
    - owner_id uses SET NULL on delete (meeting persists if user is deleted)
    """
    __tablename__ = "meeting"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True, nullable=True)
    
    # File info
    original_filename = Column(String(500), nullable=False)
    s3_path = Column(String(1000), nullable=False)
    
    # Workflow status
    status = Column(String(50), default="pending", index=True)
    
    # Results
    transcription_text = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # =====================================================
    # Organization Fields (Matrix Logic)
    # =====================================================
    
    # Confidentiality flag
    is_confidential = Column(Boolean, default=False, nullable=False)
    
    # Owner (SET NULL on delete - meeting persists)
    owner_id = Column(
        Integer, 
        ForeignKey("user.id", ondelete="SET NULL"), 
        nullable=True  # Nullable for orphan meetings
    )
    owner = relationship("User", back_populates="meetings")
    
    # Service ownership (required, auto-set from owner's service)
    service_id = Column(
        Integer, 
        ForeignKey("service.id"), 
        nullable=True  # nullable for migration, should be required
    )
    service = relationship("Service", back_populates="meetings")
    
    # Project tagging (N:N, optional)
    projects = relationship(
        "Project",
        secondary=meeting_project_link,
        back_populates="meetings"
    )

    def __repr__(self) -> str:
        return f"<Meeting {self.id}: {self.title or self.original_filename}>"


# ============================================================
# Visibility Logic (used in services/meeting.py)
# ============================================================

def can_user_access_meeting(user, meeting: Meeting) -> bool:
    """
    Check if a user can access a meeting based on matrix rules.
    
    Args:
        user: User object with service_id and projects
        meeting: Meeting object to check access for
    
    Returns:
        True if user can access, False otherwise
    """
    # Rule 1: Service solidarity (same service = access)
    if meeting.service_id == user.service_id:
        return True
    
    # Rule 2: Project bridge (shared project = access, unless confidential)
    if not meeting.is_confidential:
        user_project_ids = {p.id for p in user.projects}
        meeting_project_ids = {p.id for p in meeting.projects}
        
        # Check intersection
        if user_project_ids & meeting_project_ids:
            return True
    
    # No access
    return False
