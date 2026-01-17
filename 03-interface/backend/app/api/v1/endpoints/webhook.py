"""
Endpoints webhook internes.
Ces endpoints sont appelés par le Worker, pas par les utilisateurs.
"""
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends

from app.core.config import settings
from app.core.deps import get_db
from app.models.meeting import Meeting

router = APIRouter()

# Clé API interne pour l'authentification du worker
# En production, à déplacer vers une variable d'environnement
INTERNAL_API_KEY = "sms-internal-worker-key-2026"


class TranscriptionCompletePayload(BaseModel):
    """Payload envoyé par le Worker quand la transcription est terminée."""
    meeting_id: int
    status: str  # "completed" ou "error"
    result_path: Optional[str] = None  # s3://processed/...
    error_message: Optional[str] = None


@router.post("/transcription-complete")
async def transcription_complete(
    payload: TranscriptionCompletePayload,
    x_internal_key: str = Header(..., alias="X-Internal-Key"),
    db: AsyncSession = Depends(get_db),
):
    """
    Appelé par le Worker quand la transcription est terminée.
    
    Met à jour le Meeting dans la base avec le nouveau statut et le chemin du résultat.
    
    Sécurité : Requiert le header X-Internal-Key correspondant à INTERNAL_API_KEY.
    """
    # Vérifie la clé API interne
    if x_internal_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=401, detail="Clé API interne invalide")
    
    # Trouve le meeting
    result = await db.execute(
        select(Meeting).where(Meeting.id == payload.meeting_id)
    )
    meeting = result.scalar_one_or_none()
    
    if not meeting:
        raise HTTPException(status_code=404, detail=f"Meeting {payload.meeting_id} introuvable")
    
    # Met à jour le meeting
    meeting.status = payload.status
    
    if payload.result_path:
        # Stocke le chemin du résultat dans un champ (on pourrait ajouter result_path au modèle Meeting plus tard)
        # Pour l'instant, on le stocke dans transcription_text comme référence
        meeting.transcription_text = f"Résultat : {payload.result_path}"
    
    if payload.error_message:
        meeting.transcription_text = f"Erreur : {payload.error_message}"
    
    await db.commit()
    
    print(f"✅ [Webhook] Meeting {payload.meeting_id} mis à jour avec le statut : {payload.status}")
    
    return {
        "success": True,
        "meeting_id": payload.meeting_id,
        "status": payload.status
    }
