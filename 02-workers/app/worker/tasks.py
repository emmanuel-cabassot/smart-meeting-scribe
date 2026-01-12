import asyncio
import logging
import json
import os
import shutil
import fsspec
from pathlib import Path
from app.broker import broker
from app.core.config import settings

# --- Imports des services IA ---
from app.services.audio import convert_to_wav
from app.services.diarization import run_diarization
from app.services.transcription import run_transcription
from app.services.fusion import merge_transcription_diarization
from app.services.storage import save_results
from app.core.models import release_models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@broker.task(task_name="process_transcription_full")
async def process_transcription_full(file_path: str, meeting_id: str):
    """
    Pipeline V5 (Cloud Native) : 
    S3 (MinIO) -> Download Temp -> IA (Diarization/Whisper) -> Upload S3 -> Clean.
    
    Args:
        file_path (str): Chemin S3 du fichier source (ex: s3://uploads/meeting.mp3)
        meeting_id (str): ID unique de la réunion
    """
    local_input_path = None
    audio_wav = None
    
    try:
        logger.info(f"🚀 [JOB {meeting_id}] Démarrage Worker V5 (MinIO Native)")
        logger.info(f"   📥 Source : {file_path}")

        # ======================================================================
        # ÉTAPE 0 : TÉLÉCHARGEMENT DEPUIS MINIO (S3 -> LOCAL)
        # ======================================================================
        # On définit les options de connexion S3
        storage_options = {
            "endpoint_url": f"http://{settings.MINIO_ENDPOINT}",
            "key": settings.MINIO_ACCESS_KEY,
            "secret": settings.MINIO_SECRET_KEY
        }
        
        # On crée un chemin temporaire local pour travailler
        filename = Path(file_path).name
        local_input_path = f"/tmp/{meeting_id}_{filename}"
        
        logger.info(f"   ⬇️ Téléchargement vers {local_input_path}...")
        
        # Téléchargement via fsspec
        # On force le protocole "s3://" si absent
        s3_path = file_path if file_path.startswith("s3://") else f"s3://{file_path}"
        
        with fsspec.open(s3_path, "rb", **storage_options) as source_f:
            with open(local_input_path, "wb") as dest_f:
                shutil.copyfileobj(source_f, dest_f)

        # ======================================================================
        # ÉTAPE 1 : CONVERSION AUDIO (CPU)
        # ======================================================================
        # FFmpeg travaille maintenant sur le fichier local téléchargé
        audio_wav = convert_to_wav(local_input_path)
        
        # ======================================================================
        # ÉTAPE 2 : DIARISATION (GPU - Pyannote)
        # ======================================================================
        logger.info(f"👥 [JOB {meeting_id}] Étape 2 : Diarisation...")
        diarization_annotation = run_diarization(audio_wav)
        
        # Nettoyage VRAM intermédiaire
        release_models() 

        # ======================================================================
        # ÉTAPE 3 : TRANSCRIPTION (GPU - Whisper)
        # ======================================================================
        logger.info(f"✍️ [JOB {meeting_id}] Étape 3 : Transcription...")
        whisper_segments = run_transcription(audio_wav)
        release_models() 

        # ======================================================================
        # ÉTAPE 4 : FUSION & SAUVEGARDE (S3)
        # ======================================================================
        logger.info(f"🔗 [JOB {meeting_id}] Étape 4 : Fusion et Upload S3...")
        final_data = merge_transcription_diarization(whisper_segments, diarization_annotation)

        # Sauvegarde via le nouveau storage.py (qui écrit directement sur MinIO)
        s3_result_path = save_results(
            clean_name=filename,
            annotation=diarization_annotation,
            raw_segments=whisper_segments,
            fusion_segments=final_data
        )

        logger.info(f"✅ [JOB {meeting_id}] Succès ! Résultats dispos sur : {s3_result_path}")
        return {
            "status": "success", 
            "meeting_id": meeting_id, 
            "result_path": s3_result_path
        }

    except Exception as e:
        logger.error(f"💥 [JOB {meeting_id}] ÉCHEC : {str(e)}", exc_info=True)
        return {"status": "error", "message": str(e), "meeting_id": meeting_id}

    finally:
        # ======================================================================
        # NETTOYAGE (GARBAGE COLLECTION)
        # ======================================================================
        files_to_clean = [local_input_path, audio_wav]
        for f in files_to_clean:
            if f and os.path.exists(f):
                try:
                    os.remove(f)
                    logger.info(f"   🧹 Supprimé : {f}")
                except Exception as clean_err:
                    logger.warning(f"   ⚠️ Impossible de supprimer {f}: {clean_err}")