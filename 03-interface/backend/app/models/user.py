"""
Modèle User avec relations organisationnelles.
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.organization import user_project_link


class User(Base):
    """
    Modèle utilisateur avec support d'organisation matricielle.
    
    Règles organisationnelles :
    - Un utilisateur appartient à exactement UN Service (service_id)
    - Un utilisateur peut participer à PLUSIEURS Projets (projects)
    """
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    # Organisation : Service (1:N) - Requis
    service_id = Column(Integer, ForeignKey("service.id"), nullable=True)  # nullable pour la migration
    service = relationship("Service", back_populates="users")

    # Organisation : Projets (N:N) - Optionnel
    projects = relationship(
        "Project",
        secondary=user_project_link,
        back_populates="members"
    )

    # Meetings créés par cet utilisateur
    meetings = relationship("Meeting", back_populates="owner")

    def __repr__(self) -> str:
        return f"<User {self.email}>"
    
    @property
    def project_ids(self) -> set[int]:
        """Retourne l'ensemble des IDs de projets pour une recherche rapide."""
        return {p.id for p in self.projects}
