"""
Endpoints d'upload et de transcription.
Gère l'upload de fichiers vers S3 et le dispatch des tâches de traitement.
"""
import uuid
import json
import boto3
from typing import Optional, List
from botocore.exceptions import ClientError
from urllib.parse import urlparse
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.worker.broker import broker, kicker
from app.core.config import settings
from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.meeting import Meeting
from app.models.group import Group
from app.schemas.meeting import MeetingOut

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
    file: UploadFile = File(..., description="Fichier audio/vidéo à transcrire"),
    title: Optional[str] = Form(None, description="Titre du meeting (optionnel)"),
    group_ids: Optional[str] = Form(
        None, 
        description="JSON array des IDs de groupes. Exemple: [1, 2]",
        examples=["[1]", "[1, 2, 3]"]
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload un fichier audio/vidéo et lance la transcription.
    
    1. Valide le format du fichier
    2. Upload vers S3 (MinIO)
    3. Crée le Meeting en base avec les groupes assignés
    4. Dispatch la tâche au Worker via Redis
    
    Args:
        file: Fichier audio/vidéo
        title: Titre optionnel du meeting
        group_ids: JSON array des IDs de groupes, ex: "[1, 2]"
    
    Returns:
        Objet Meeting créé
    """
    # Validation du format
    if not file.filename.lower().endswith(ALLOWED_EXTENSIONS):
        raise HTTPException(
            status_code=400, 
            detail=f"Format non supporté. Extensions acceptées: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Charge l'utilisateur avec ses groupes
    user_query = await db.execute(
        select(User)
        .options(selectinload(User.groups))
        .where(User.id == current_user.id)
    )
    user = user_query.scalar_one()

    # Parse group_ids si fourni
    parsed_group_ids: List[int] = []
    print(f"🔍 [DEBUG] group_ids reçu: '{group_ids}' (type: {type(group_ids)})")
    
    if group_ids:
        try:
            parsed_group_ids = json.loads(group_ids)
            if not isinstance(parsed_group_ids, list):
                raise HTTPException(
                    status_code=400, 
                    detail=f"group_ids doit être un JSON array (ex: [1, 2]), reçu: {group_ids}"
                )
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400, 
                detail=f"group_ids doit être un JSON array valide (ex: [1, 2]), reçu: {group_ids}"
            )
    
    print(f"🔍 [DEBUG] parsed_group_ids: {parsed_group_ids}")
    
    # Si pas de group_ids fourni, utiliser tous les groupes de l'utilisateur
    if not parsed_group_ids:
        parsed_group_ids = [g.id for g in user.groups]
        print(f"🔍 [DEBUG] Fallback - groupes utilisateur: {parsed_group_ids}")
    
    # Valide les groupes (SÉCURITÉ : l'utilisateur doit être membre)
    user_group_ids = {g.id for g in user.groups}
    valid_groups = []
    
    for gid in parsed_group_ids:
        if gid not in user_group_ids:
            raise HTTPException(
                status_code=403,
                detail=f"Vous ne pouvez pas assigner le groupe {gid}: vous n'en êtes pas membre"
            )
    
    # Récupère les objets groupe
    if parsed_group_ids:
        result = await db.execute(
            select(Group).where(Group.id.in_(parsed_group_ids))
        )
        valid_groups = list(result.scalars().all())
    
    if not valid_groups:
        raise HTTPException(
            status_code=400,
            detail="Au moins un groupe valide est requis"
        )

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
        owner_id=current_user.id,
    )
    meeting.groups = valid_groups
    
    db.add(meeting)
    await db.commit()
    await db.refresh(meeting)
    
    group_names = [g.name for g in valid_groups]
    print(f"💾 [API] Meeting créé en DB: ID={meeting.id}, groupes={group_names}")

    # === DISPATCH VERS REDIS ===
    try:
        task = await kicker.kiq(file_path=s3_path, meeting_id=str(meeting.id))
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