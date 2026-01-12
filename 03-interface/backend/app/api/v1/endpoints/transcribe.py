import uuid
import fsspec
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.broker import kicker
from app.core.config import settings

router = APIRouter()

@router.post("/")
async def start_transcription(file: UploadFile = File(...)):
    meeting_id = str(uuid.uuid4())
    safe_filename = file.filename.replace(" ", "_")
    object_name = f"{meeting_id}_{safe_filename}"
    s3_path = f"{settings.STORAGE_PROTOCOL}://{settings.MINIO_BUCKET_AUDIO}/{object_name}"
    
    print(f"📥 [API] Réception fichier : {file.filename}")

    try:
        storage_options = {
            "endpoint_url": f"http://{settings.MINIO_ENDPOINT}",
            "key": settings.MINIO_ACCESS_KEY,
            "secret": settings.MINIO_SECRET_KEY
        }

        with fsspec.open(s3_path, "wb", **storage_options) as s3_file:
            while content := await file.read(1024 * 1024):
                s3_file.write(content)
                
        print(f"✅ [API] Upload S3 terminé.")

    except Exception as e:
        print(f"❌ [API] Erreur S3 : {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur S3: {str(e)}")

    try:
        task = await kicker.kiq(file_path=s3_path, meeting_id=meeting_id)
        print(f"🚀 [API] Tâche envoyée (ID: {task.task_id})")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur Broker: {str(e)}")

    return {
        "status": "queued",
        "meeting_id": meeting_id,
        "task_id": task.task_id,
        "s3_path": s3_path
    }