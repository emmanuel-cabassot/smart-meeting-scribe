"""
Modèle Group pour la gestion des accès et de la visibilité.
Remplace le système Service + Projet par un modèle unifié style Active Directory.
"""
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Boolean, Table, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.db.base_class import Base


# ============================================================
# Enum pour le type de groupe
# ============================================================

class GroupType(str, PyEnum):
    """
    Types de groupes pour l'organisation et l'affichage.
    
    - department : Départements/Services (R&D, Marketing, RH)
    - project : Projets transversaux (Lancement V5, Audit)
    - recurring : Réunions récurrentes (COMOP, Café AGAM)
    """
    DEPARTMENT = "department"
    PROJECT = "project"
    RECURRING = "recurring"


# ============================================================
# Tables d'association (Many-to-Many)
# ============================================================

# User <-> Group (N:N) : Quels utilisateurs sont dans quels groupes ?
user_group_link = Table(
    "user_group_link",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("user.id", ondelete="CASCADE"), primary_key=True),
    Column("group_id", Integer, ForeignKey("group.id", ondelete="CASCADE"), primary_key=True),
)

# Meeting <-> Group (N:N) : Quels meetings sont visibles par quels groupes ?
meeting_group_link = Table(
    "meeting_group_link",
    Base.metadata,
    Column("meeting_id", Integer, ForeignKey("meeting.id", ondelete="CASCADE"), primary_key=True),
    Column("group_id", Integer, ForeignKey("group.id", ondelete="CASCADE"), primary_key=True),
)


# ============================================================
# Modèle Group
# ============================================================

class Group(Base):
    """
    Groupe d'accès (style Active Directory).
    
    Règles :
    - Un utilisateur peut appartenir à PLUSIEURS Groupes (N:N)
    - Un Meeting est visible par un ou plusieurs Groupes (N:N)
    - Un utilisateur voit un meeting s'il partage au moins un groupe avec lui
    
    Exemples de groupes :
    - Départements : R&D, Marketing, Commercial, RH
    - Projets : COMOP, Projet V5, Café AGAM
    - Spéciaux : Tous, Direction
    """
    __tablename__ = "group"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(String(500), nullable=True)
    type = Column(
        Enum(
            'department', 'project', 'recurring',
            name='grouptype',
            create_type=False  # Already created by migration
        ), 
        default='department', 
        nullable=False,
        index=True
    )
    is_active = Column(Boolean, default=True, nullable=False)

    # Relations (Many-to-Many)
    members = relationship(
        "User",
        secondary=user_group_link,
        back_populates="groups"
    )
    meetings = relationship(
        "Meeting",
        secondary=meeting_group_link,
        back_populates="groups"
    )

    def __repr__(self) -> str:
        return f"<Group {self.name}>"
