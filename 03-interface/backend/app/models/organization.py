"""
Organization models: Service (vertical) and Project (transversal).
Implements the matrix logic for user and meeting visibility.
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship

from app.db.base_class import Base


# ============================================================
# Association Tables (Many-to-Many)
# ============================================================

# User <-> Project (N:N): Which users are in which projects?
user_project_link = Table(
    "user_project_link",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("user.id", ondelete="CASCADE"), primary_key=True),
    Column("project_id", Integer, ForeignKey("project.id", ondelete="CASCADE"), primary_key=True),
)

# Meeting <-> Project (N:N): Which meetings are tagged to which projects?
meeting_project_link = Table(
    "meeting_project_link",
    Base.metadata,
    Column("meeting_id", Integer, ForeignKey("meeting.id", ondelete="CASCADE"), primary_key=True),
    Column("project_id", Integer, ForeignKey("project.id", ondelete="CASCADE"), primary_key=True),
)


# ============================================================
# Service Model (Vertical / Department)
# ============================================================

class Service(Base):
    """
    Vertical department (R&D, Sales, Marketing, HR, etc.)
    
    Rules:
    - A User belongs to exactly ONE Service (1:N)
    - A Meeting belongs to exactly ONE Service (the owner's)
    - Members of a Service can see all non-confidential meetings of that Service
    """
    __tablename__ = "service"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(String(500), nullable=True)

    # Relationships
    users = relationship("User", back_populates="service")
    meetings = relationship("Meeting", back_populates="service")

    def __repr__(self) -> str:
        return f"<Service {self.name}>"


# ============================================================
# Project Model (Transversal / Cross-functional)
# ============================================================

class Project(Base):
    """
    Transversal project that spans multiple services.
    
    Rules:
    - A User can belong to MULTIPLE Projects (N:N)
    - A Meeting can be tagged to MULTIPLE Projects (N:N)
    - Project membership enables cross-service visibility
    """
    __tablename__ = "project"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships (Many-to-Many)
    members = relationship(
        "User",
        secondary=user_project_link,
        back_populates="projects"
    )
    meetings = relationship(
        "Meeting",
        secondary=meeting_project_link,
        back_populates="projects"
    )

    def __repr__(self) -> str:
        return f"<Project {self.name}>"
