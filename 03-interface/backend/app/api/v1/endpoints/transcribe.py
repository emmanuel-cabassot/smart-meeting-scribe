"""
Upload and transcription endpoints.
Handles file upload to S3 and dispatches processing tasks.
"""
import uuid
import json
import boto3
from typing import Optional, List
from botocore.exceptions import ClientError
from urllib.parse import urlparse
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.worker.broker import broker, kicker
from app.core.config import settings
from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.meeting import Meeting
from app.models.organization import Project
from app.schemas.meeting import MeetingOut
from sqlalchemy import select

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


@router.post("/", response_model=MeetingOut)
async def start_transcription(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    is_confidential: bool = Form(False),
    project_ids: Optional[str] = Form(None),  # JSON string: "[1, 2]"
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload audio/video file and start transcription.
    
    1. Validates file format
    2. Uploads to S3 (MinIO)
    3. Creates Meeting in database (with service auto-set)
    4. Dispatches task to Worker via Redis
    
    Args:
        file: Audio/video file
        title: Optional meeting title
        is_confidential: If true, only service members can see (default: false)
        project_ids: JSON array of project IDs to tag, e.g. "[1, 2]"
    
    Returns:
        Created Meeting object with task_id
    """
    # Validation du format
    if not file.filename.lower().endswith(ALLOWED_EXTENSIONS):
        raise HTTPException(
            status_code=400, 
            detail=f"Format non supporté. Extensions acceptées: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Parse project_ids if provided
    parsed_project_ids: List[int] = []
    if project_ids:
        try:
            parsed_project_ids = json.loads(project_ids)
            if not isinstance(parsed_project_ids, list):
                parsed_project_ids = []
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="project_ids doit être un JSON array valide")
    
    # Validate project membership (SECURITY)
    valid_projects = []
    if parsed_project_ids:
        user_project_ids = {p.id for p in current_user.projects}
        
        for pid in parsed_project_ids:
            if pid not in user_project_ids:
                raise HTTPException(
                    status_code=403,
                    detail=f"Vous ne pouvez pas taguer le projet {pid}: vous n'en êtes pas membre"
                )
        
        # Fetch project objects
        result = await db.execute(
            select(Project).where(Project.id.in_(parsed_project_ids))
        )
        valid_projects = list(result.scalars().all())

    # Generate unique meeting ID
    safe_filename = file.filename.replace(" ", "_")
    object_name = f"{uuid.uuid4()}_{safe_filename}"
    
    print(f"📥 [API] Réception fichier : {file.filename} (user: {current_user.email})")

    # === UPLOAD BOTO3 (Stream vers MinIO) ===
    try:
        await file.seek(0)
        
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

    # === CREATE MEETING IN DATABASE ===
    meeting = Meeting(
        title=title or file.filename,
        original_filename=file.filename,
        s3_path=s3_path,
        status="pending",
        is_confidential=is_confidential,
        owner_id=current_user.id,
        service_id=current_user.service_id,  # Auto-set from user
    )
    
    # Add validated projects
    if valid_projects:
        meeting.projects = valid_projects
    
    db.add(meeting)
    await db.commit()
    await db.refresh(meeting)
    
    print(f"💾 [API] Meeting créé en DB: ID={meeting.id}, service={current_user.service_id}")

    # === DISPATCH VERS REDIS ===
    try:
        # Pass meeting.id to worker so it can update the DB
        task = await kicker.kiq(file_path=s3_path, meeting_id=str(meeting.id))
        
        # Store task_id in some way if needed (could add to meeting model later)
        print(f"🚀 [API] Tâche envoyée (task_id: {task.task_id}, meeting_id: {meeting.id})")
        
    except Exception as e:
        # Rollback: delete meeting if dispatch fails
        await db.delete(meeting)
        await db.commit()
        print(f"❌ [API] Erreur Broker : {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur Broker: {str(e)}")

    return meeting


@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """
    Permet au Frontend de demander : 'C'est fini ?'
    Interroge Redis pour voir l'état de la tâche.
    Si terminée, va chercher le JSON fusion.json dans S3 et le renvoie.
    """
    try:
        # Taskiq RedisAsyncResultBackend : get_result retourne un TaskiqResult
        taskiq_result = await broker.result_backend.get_result(task_id)
        
        # Si pas de résultat, la tâche est encore en cours
        if taskiq_result is None:
            return {
                "status": "processing",
                "task_id": task_id,
                "message": "La transcription est en cours..."
            }
        
        # Essaye d'accéder au résultat (peut lever une exception si pas prêt)
        try:
            task_result = taskiq_result.return_value
        except (AttributeError, Exception):
            # Pas encore prêt
            return {
                "status": "processing",
                "task_id": task_id,
                "message": "La transcription est en cours..."
            }
        
        # Si le résultat est None, encore en cours
        if task_result is None:
            return {
                "status": "processing",
                "task_id": task_id,
                "message": "La transcription est en cours..."
            }
        # task_result = {"status": "success", "meeting_id": "...", "result_path": "s3://processed/..."}
        
        # Vérifie si c'est une erreur du worker
        if task_result.get("status") == "error":
            return {
                "status": "error",
                "task_id": task_id,
                "message": task_result.get("message", "Erreur inconnue")
            }
        
        # Essaye de récupérer le JSON depuis S3
        try:
            s3_folder_url = task_result.get("result_path")
            
            if not s3_folder_url:
                return {"status": "completed", "task_id": task_id, "result": []}
            
            # Parse l'URL s3://bucket/dossier
            parsed = urlparse(s3_folder_url)
            bucket_name = parsed.netloc
            folder_path = parsed.path.lstrip('/')
            
            # Construit le chemin vers fusion.json
            file_key = f"{folder_path}/fusion.json"
            
            print(f"📂 [API] Lecture S3: {bucket_name}/{file_key}")
            
            # Télécharge le contenu JSON
            s3_response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
            json_content = json.loads(s3_response['Body'].read().decode('utf-8'))
            
            return {
                "status": "completed",
                "task_id": task_id,
                "result": json_content  # Array direct [{speaker, start, end, text}, ...]
            }
            
        except Exception as e:
            print(f"⚠️ [API] Erreur récupération S3 ({task_id}): {e}")
            return {
                "status": "error",
                "task_id": task_id,
                "message": "Fichier résultat introuvable dans S3"
            }
        
    except Exception as e:
        error_message = str(e)
        
        # "Cannot get result" signifie que la tâche est en queue mais pas encore traitée
        if "Cannot get result" in error_message or "not found" in error_message.lower():
            print(f"⏳ [API] Tâche en attente : {task_id}")
            return {
                "status": "pending",
                "task_id": task_id,
                "message": "La tâche est en attente de traitement..."
            }
        
        # Vraie erreur
        print(f"❌ [API] Erreur status : {error_message}")
        return {
            "status": "unknown",
            "task_id": task_id,
            "error": error_message
        }