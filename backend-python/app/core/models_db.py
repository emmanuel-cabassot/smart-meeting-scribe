"""
Modèles SQLAlchemy (Tables de la Base de Données).
Définit la structure des données persistantes.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float, Text
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

class Meeting(Base):
    """
    Table 'meetings' : Centralise tout le cycle de vie d'une réunion.
    """
    __tablename__ = "meetings"

    # Identifiant unique (UUID) généré automatiquement
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Date de création (Upload)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # --- MÉTADONNÉES FICHIER ---
    filename = Column(String, nullable=False)       # Nom original (ex: "CODIR_Janvier.mp3")
    storage_path = Column(String, nullable=False)   # Chemin abstrait (ex: "uploads/uuid.wav")
    
    # --- SUIVI DU JOB (Workflow) ---
    # États : PENDING, PROCESSING, COMPLETED, ERROR
    status = Column(String, default="PENDING", index=True)
    error_message = Column(Text, nullable=True)     # Pour debugger si ça plante
    
    # --- RÉSULTATS (Chemins vers les fichiers JSON générés) ---
    # On stocke juste le chemin fsspec, pas le gros contenu JSON (trop lourd pour SQL)
    transcription_path = Column(String, nullable=True)
    diarization_path = Column(String, nullable=True)
    fusion_path = Column(String, nullable=True)
    
    # --- PERFORMANCES ---
    processing_duration = Column(Float, nullable=True) # Temps de calcul en secondes