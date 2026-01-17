"""
Modèle Meeting avec relations organisationnelles et logique de visibilité.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base
from app.models.organization import meeting_project_link


class Meeting(Base):
    """
    Modèle Meeting avec support de visibilité matricielle.
    
    Règles de visibilité :
    1. Les membres d'un service peuvent voir tous les meetings de leur service (sauf confidentiel)
    2. Les membres d'un projet peuvent voir les meetings taggés sur leurs projets (sauf confidentiel)
    3. Les meetings confidentiels ne sont visibles QUE par les membres du service
    
    Règles de propriété :
    - service_id est automatiquement défini sur le service du propriétaire
    - owner_id utilise SET NULL à la suppression (le meeting persiste si l'utilisateur est supprimé)
    """
    __tablename__ = "meeting"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True, nullable=True)
    
    # Informations du fichier
    original_filename = Column(String(500), nullable=False)
    s3_path = Column(String(1000), nullable=False)
    
    # Statut du workflow
    status = Column(String(50), default="pending", index=True)
    
    # Résultats
    transcription_text = Column(Text, nullable=True)
    
    # Horodatages
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # =====================================================
    # Champs organisationnels (Logique matricielle)
    # =====================================================
    
    # Indicateur de confidentialité
    is_confidential = Column(Boolean, default=False, nullable=False)
    
    # Propriétaire (SET NULL à la suppression - le meeting persiste)
    owner_id = Column(
        Integer, 
        ForeignKey("user.id", ondelete="SET NULL"), 
        nullable=True  # Nullable pour les meetings orphelins
    )
    owner = relationship("User", back_populates="meetings")
    
    # Propriété du service (requis, auto-défini depuis le service du propriétaire)
    service_id = Column(
        Integer, 
        ForeignKey("service.id"), 
        nullable=True  # nullable pour la migration, devrait être requis
    )
    service = relationship("Service", back_populates="meetings")
    
    # Tags de projet (N:N, optionnel)
    projects = relationship(
        "Project",
        secondary=meeting_project_link,
        back_populates="meetings"
    )

    def __repr__(self) -> str:
        return f"<Meeting {self.id}: {self.title or self.original_filename}>"


# ============================================================
# Logique de visibilité (utilisée dans services/meeting.py)
# ============================================================

def can_user_access_meeting(user, meeting: Meeting) -> bool:
    """
    Vérifie si un utilisateur peut accéder à un meeting selon les règles matricielles.
    
    Args:
        user: Objet User avec service_id et projects
        meeting: Objet Meeting dont on vérifie l'accès
    
    Returns:
        True si l'utilisateur peut accéder, False sinon
    """
    # Règle 1 : Solidarité de service (même service = accès)
    if meeting.service_id == user.service_id:
        return True
    
    # Règle 2 : Passerelle projet (projet partagé = accès, sauf si confidentiel)
    if not meeting.is_confidential:
        user_project_ids = {p.id for p in user.projects}
        meeting_project_ids = {p.id for p in meeting.projects}
        
        # Vérifie l'intersection
        if user_project_ids & meeting_project_ids:
            return True
    
    # Pas d'accès
    return False
