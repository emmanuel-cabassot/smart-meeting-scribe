"""
Modèles organisationnels : Service (vertical) et Projet (transversal).
Implémente la logique matricielle pour la visibilité des utilisateurs et des meetings.
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship

from app.db.base_class import Base


# ============================================================
# Tables d'association (Many-to-Many)
# ============================================================

# User <-> Projet (N:N) : Quels utilisateurs sont dans quels projets ?
user_project_link = Table(
    "user_project_link",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("user.id", ondelete="CASCADE"), primary_key=True),
    Column("project_id", Integer, ForeignKey("project.id", ondelete="CASCADE"), primary_key=True),
)

# Meeting <-> Projet (N:N) : Quels meetings sont taggés sur quels projets ?
meeting_project_link = Table(
    "meeting_project_link",
    Base.metadata,
    Column("meeting_id", Integer, ForeignKey("meeting.id", ondelete="CASCADE"), primary_key=True),
    Column("project_id", Integer, ForeignKey("project.id", ondelete="CASCADE"), primary_key=True),
)


# ============================================================
# Modèle Service (Vertical / Département)
# ============================================================

class Service(Base):
    """
    Département vertical (R&D, Ventes, Marketing, RH, etc.)
    
    Règles :
    - Un utilisateur appartient à exactement UN Service (1:N)
    - Un Meeting appartient à exactement UN Service (celui du propriétaire)
    - Les membres d'un Service peuvent voir tous les meetings non-confidentiels de ce Service
    """
    __tablename__ = "service"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(String(500), nullable=True)

    # Relations
    users = relationship("User", back_populates="service")
    meetings = relationship("Meeting", back_populates="service")

    def __repr__(self) -> str:
        return f"<Service {self.name}>"


# ============================================================
# Modèle Projet (Transversal / Inter-fonctionnel)
# ============================================================

class Project(Base):
    """
    Projet transversal qui couvre plusieurs services.
    
    Règles :
    - Un utilisateur peut appartenir à PLUSIEURS Projets (N:N)
    - Un Meeting peut être taggé sur PLUSIEURS Projets (N:N)
    - L'appartenance à un projet permet la visibilité inter-services
    """
    __tablename__ = "project"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relations (Many-to-Many)
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
