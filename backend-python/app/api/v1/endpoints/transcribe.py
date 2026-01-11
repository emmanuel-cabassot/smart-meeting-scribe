import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

# --- Imports V3.1 ---
from app.worker.tasks import process_transcription_full
from app.services.storage import storage
from app.core.database import get_db
from app.core.models_db import Meeting

router = APIRouter()

@router.post("/")
async def start_transcription(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint V3.1 :
    1. Sauvegarde le fichier via l'abstraction Storage.
    2. Crée une entrée de suivi dans la DB (Postgres).
    3. Délègue le traitement lourd au Worker (Redis).
    """
    # 1. Génération de l'ID unique de la réunion
    meeting_id = str(uuid.uuid4())
    
    try:
        # 2. Sauvegarde Physique (Via fsspec)
        # On nettoie le nom de fichier pour éviter les soucis
        file_ext = file.filename.split('.')[-1]
        clean_filename = f"{meeting_id}.{file_ext}"
        
        # storage.save_upload retourne le chemin relatif (ex: "uploads/uuid.wav")
        # C'est ce chemin "neutre" qu'on stocke en base.
        storage_path = storage.save_upload(file, clean_filename)

        # 3. Création de la fiche de suivi (Base de Données)
        new_meeting = Meeting(
            id=meeting_id,
            filename=file.filename,      # Nom original (pour l'affichage user)
            storage_path=storage_path,   # Chemin physique
            status="PENDING"             # Statut initial
        )
        db.add(new_meeting)
        await db.commit()
        # On refresh pour récupérer l'objet à jour (avec dates etc.)
        await db.refresh(new_meeting)
        
        # 4. Envoi de la tâche au Worker (Taskiq)
        # On passe le meeting_id et le chemin relatif.
        # Le worker utilisera storage.read_file() ou get_full_path()
        task = await process_transcription_full.kiq(
            file_path=storage_path,
            meeting_id=meeting_id
        )

        return {
            "status": "pending",
            "meeting_id": meeting_id,
            "task_id": task.task_id,
            "message": "Fichier reçu et sécurisé. Traitement IA démarré."
        }

    except Exception as e:
        # En cas d'erreur, on loggue et on renvoie une 500
        raise HTTPException(status_code=500, detail=f"Erreur Upload V3.1 : {str(e)}")