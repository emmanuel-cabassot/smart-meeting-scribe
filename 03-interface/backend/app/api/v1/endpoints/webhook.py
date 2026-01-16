"""
Internal webhook endpoints.
These are called by the Worker, not by users.
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

# Internal API key for worker authentication
# In production, move this to environment variable
INTERNAL_API_KEY = "sms-internal-worker-key-2026"


class TranscriptionCompletePayload(BaseModel):
    """Payload sent by Worker when transcription is complete."""
    meeting_id: int
    status: str  # "completed" or "error"
    result_path: Optional[str] = None  # s3://processed/...
    error_message: Optional[str] = None


@router.post("/transcription-complete")
async def transcription_complete(
    payload: TranscriptionCompletePayload,
    x_internal_key: str = Header(..., alias="X-Internal-Key"),
    db: AsyncSession = Depends(get_db),
):
    """
    Called by the Worker when transcription is complete.
    
    Updates the Meeting in the database with the new status and result path.
    
    Security: Requires X-Internal-Key header matching INTERNAL_API_KEY.
    """
    # Verify internal API key
    if x_internal_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid internal API key")
    
    # Find the meeting
    result = await db.execute(
        select(Meeting).where(Meeting.id == payload.meeting_id)
    )
    meeting = result.scalar_one_or_none()
    
    if not meeting:
        raise HTTPException(status_code=404, detail=f"Meeting {payload.meeting_id} not found")
    
    # Update the meeting
    meeting.status = payload.status
    
    if payload.result_path:
        # Store the result path in a field (we could add result_path to Meeting model)
        # For now, we'll store it in transcription_text as a reference
        meeting.transcription_text = f"Result: {payload.result_path}"
    
    if payload.error_message:
        meeting.transcription_text = f"Error: {payload.error_message}"
    
    await db.commit()
    
    print(f"✅ [Webhook] Meeting {payload.meeting_id} updated to status: {payload.status}")
    
    return {
        "success": True,
        "meeting_id": payload.meeting_id,
        "status": payload.status
    }
