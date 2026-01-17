"""
Modèle Meeting avec visibilité basée sur les groupes.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base
from app.models.group import meeting_group_link


class Meeting(Base):
    """
    Modèle Meeting avec visibilité par groupes.
    
    Règles de visibilité :
    - Un meeting est visible par les membres des groupes auxquels il est assigné
    - Un utilisateur voit le meeting s'il partage AU MOINS UN groupe avec lui
    
    Règle de propriété :
    - owner_id référence le créateur du meeting
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
    # Relations
    # =====================================================
    
    # Propriétaire (SET NULL à la suppression - le meeting persiste)
    owner_id = Column(
        Integer, 
        ForeignKey("user.id", ondelete="SET NULL"), 
        nullable=True
    )
    owner = relationship("User", back_populates="meetings")
    
    # Groupes (N:N) - Définit la visibilité
    groups = relationship(
        "Group",
        secondary=meeting_group_link,
        back_populates="meetings"
    )

    def __repr__(self) -> str:
        return f"<Meeting {self.id}: {self.title or self.original_filename}>"


# ============================================================
# Logique de visibilité
# ============================================================

def can_user_access_meeting(user, meeting: Meeting) -> bool:
    """
    Vérifie si un utilisateur peut accéder à un meeting.
    
    Règle simple : L'utilisateur doit partager au moins un groupe avec le meeting.
    
    Args:
        user: Objet User avec ses groupes
        meeting: Objet Meeting dont on vérifie l'accès
    
    Returns:
        True si l'utilisateur peut accéder, False sinon
    """
    user_group_ids = {g.id for g in user.groups}
    meeting_group_ids = {g.id for g in meeting.groups}
    
    # Intersection : au moins un groupe en commun ?
    return bool(user_group_ids & meeting_group_ids)
