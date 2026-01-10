import uuid
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.worker.tasks import process_transcription_full # On importe la vraie tâche
from app.core.config import settings

router = APIRouter()

@router.post("/")
async def start_transcription(file: UploadFile = File(...)):
    """Reçoit un fichier et délègue le travail au Worker GPU."""
    meeting_id = str(uuid.uuid4())
    
    # Création du chemin sur le volume partagé /data
    upload_dir = Path(settings.STORAGE_PATH) / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_dir / f"{meeting_id}{Path(file.filename).suffix}"

    try:
        # 1. On sauvegarde physiquement le fichier
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 2. On lance la tâche sur le Worker
        # .kiq() envoie la tâche dans Redis et rend la main immédiatement
        task = await process_transcription_full.kiq(
            file_path=str(file_path),
            meeting_id=meeting_id
        )

        return {
            "status": "processing",
            "meeting_id": meeting_id,
            "task_id": task.task_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))