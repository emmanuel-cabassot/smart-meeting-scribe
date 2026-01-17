"""
Modèle User avec relations de groupes.
"""
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.group import user_group_link


class User(Base):
    """
    Modèle utilisateur avec support de groupes.
    
    Règles :
    - Un utilisateur peut appartenir à PLUSIEURS Groupes (N:N)
    - La visibilité des meetings dépend des groupes partagés
    """
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    # Groupes (N:N) - Remplace service_id et projects
    groups = relationship(
        "Group",
        secondary=user_group_link,
        back_populates="members"
    )

    # Meetings créés par cet utilisateur
    meetings = relationship("Meeting", back_populates="owner")

    def __repr__(self) -> str:
        return f"<User {self.email}>"
    
    @property
    def group_ids(self) -> set[int]:
        """Retourne l'ensemble des IDs de groupes pour une recherche rapide."""
        return {g.id for g in self.groups}
