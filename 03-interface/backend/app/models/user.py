"""
User model with organization relationships.
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.organization import user_project_link


class User(Base):
    """
    User model with matrix organization support.
    
    Organization Rules:
    - A User belongs to exactly ONE Service (service_id)
    - A User can participate in MULTIPLE Projects (projects)
    """
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    # Organization: Service (1:N) - Required
    service_id = Column(Integer, ForeignKey("service.id"), nullable=True)  # nullable for migration
    service = relationship("Service", back_populates="users")

    # Organization: Projects (N:N) - Optional
    projects = relationship(
        "Project",
        secondary=user_project_link,
        back_populates="members"
    )

    # Meetings created by this user
    meetings = relationship("Meeting", back_populates="owner")

    def __repr__(self) -> str:
        return f"<User {self.email}>"
    
    @property
    def project_ids(self) -> set[int]:
        """Return set of project IDs for quick lookup."""
        return {p.id for p in self.projects}
