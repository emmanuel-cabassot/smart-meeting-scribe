import uuid
import boto3
from botocore.exceptions import ClientError
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.broker import broker, kicker
from app.core.config import settings

router = APIRouter()

# Extensions supportées
ALLOWED_EXTENSIONS = ('.mp4', '.mov', '.mp3', '.m4a', '.wav', '.webm', '.ogg')

# --- CONFIGURATION BOTO3 (MinIO) ---
s3_client = boto3.client(
    "s3",
    endpoint_url=f"http://{settings.MINIO_ENDPOINT}",
    aws_access_key_id=settings.MINIO_ACCESS_KEY,
    aws_secret_access_key=settings.MINIO_SECRET_KEY
)

# Création du bucket au démarrage si inexistant
try:
    s3_client.create_bucket(Bucket=settings.MINIO_BUCKET_AUDIO)
except ClientError:
    pass  # Bucket existe déjà


@router.post("/")
async def start_transcription(file: UploadFile = File(...)):
    """
    1. Reçoit le fichier (Stream)
    2. L'écrit sur S3 (MinIO) via Boto3
    3. Envoie la tâche au Worker via Redis
    """
    # Validation du format
    if not file.filename.lower().endswith(ALLOWED_EXTENSIONS):
        raise HTTPException(
            status_code=400, 
            detail=f"Format non supporté. Extensions acceptées: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    meeting_id = str(uuid.uuid4())
    safe_filename = file.filename.replace(" ", "_")
    object_name = f"{meeting_id}_{safe_filename}"
    
    print(f"📥 [API] Réception fichier : {file.filename}")

    # === UPLOAD BOTO3 (Stream vers MinIO) ===
    try:
        # Rembobiner le fichier au début
        await file.seek(0)
        
        # upload_fileobj est optimisé pour le streaming (pas tout en RAM)
        s3_client.upload_fileobj(
            file.file,
            settings.MINIO_BUCKET_AUDIO,
            object_name,
            ExtraArgs={"ContentType": file.content_type or "application/octet-stream"}
        )
        
        s3_path = f"s3://{settings.MINIO_BUCKET_AUDIO}/{object_name}"
        print(f"✅ [API] Upload S3 terminé: {s3_path}")

    except Exception as e:
        print(f"❌ [API] Erreur S3 : {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur S3: {str(e)}")

    # === DISPATCH VERS REDIS ===
    try:
        task = await kicker.kiq(file_path=s3_path, meeting_id=meeting_id)
        print(f"🚀 [API] Tâche envoyée (ID: {task.task_id})")
    except Exception as e:
        print(f"❌ [API] Erreur Broker : {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur Broker: {str(e)}")

    return {
        "status": "queued",
        "meeting_id": meeting_id,
        "task_id": task.task_id,
        "s3_path": s3_path,
        "message": "Fichier reçu. L'IA va démarrer dès que possible."
    }


@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """
    Permet au Frontend de demander : 'C'est fini ?'
    Interroge Redis pour voir l'état de la tâche.
    """
    try:
        result = broker.result_backend.get_result(task_id)
        is_ready = await result.is_ready()
        
        if is_ready:
            task_result = await result.get_result()
            return {
                "status": "completed",
                "task_id": task_id,
                "result": task_result
            }
        
        return {
            "status": "processing",
            "task_id": task_id,
            "message": "La transcription est en cours..."
        }
        
    except Exception as e:
        print(f"❌ [API] Erreur status : {str(e)}")
        return {
            "status": "unknown",
            "task_id": task_id,
            "error": str(e)
        }