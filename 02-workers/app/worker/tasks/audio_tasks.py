"""
Audio Tasks - Tâches liées au traitement audio.

Contient:
- process_transcription_full: Pipeline complet de transcription
- (Future) process_audio_conversion: Conversion de formats audio
- (Future) process_diarization_only: Diarisation seule sans transcription
"""

import logging
import os
from pathlib import Path
import httpx

from app.broker import broker
from app.worker.tasks.base import smart_download, cleanup_files

# --- Imports des services IA ---
from app.services.audio import convert_to_wav
from app.services.diarization import run_diarization
from app.services.transcription import run_transcription
from app.services.fusion import merge_transcription_diarization
from app.services.storage import save_results
from app.services.identification import get_voice_bank_embeddings, identify_speaker
from app.core.models import release_models, load_embedding_model

logger = logging.getLogger(__name__)

# URL de l'API pour le callback (réseau Docker)
API_WEBHOOK_URL = os.getenv("API_WEBHOOK_URL", "http://sms_api:8000/api/v1/internal/webhook/transcription-complete")
INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY", "sms-internal-worker-key-2026")


# =============================================================================
# PIPELINE TRANSCRIPTION COMPLET
# =============================================================================

@broker.task(task_name="process_transcription_full")
async def process_transcription_full(file_path: str, meeting_id: str):
    """
    Pipeline V5 (Cloud Native) : 
    S3 (MinIO) -> Download Temp -> IA (Diarization/Whisper) -> Upload S3 -> Clean.
    
    Args:
        file_path (str): Chemin S3 du fichier source (ex: s3://uploads/meeting.mp3)
        meeting_id (str): ID unique de la réunion
        
    Returns:
        dict: Résultat avec status, meeting_id, et result_path
    """
    local_input_path = None
    audio_wav = None
    
    try:
        logger.info(f"🚀 [JOB {meeting_id}] Démarrage Worker V5 (Boto3 Native)")
        logger.info(f"   📥 Source : {file_path}")

        # ==================================================================
        # ÉTAPE 0 : TÉLÉCHARGEMENT DEPUIS MINIO (S3 -> LOCAL)
        # ==================================================================
        filename = Path(file_path).name
        local_input_path = f"/tmp/{meeting_id}_{filename}"
        
        smart_download(file_path, local_input_path)

        # ==================================================================
        # ÉTAPE 1 : CONVERSION AUDIO (CPU)
        # ==================================================================
        audio_wav = convert_to_wav(local_input_path)
        
        # ==================================================================
        # ÉTAPE 2 : DIARISATION (GPU - Pyannote)
        # ==================================================================
        logger.info(f"👥 [JOB {meeting_id}] Étape 2 : Diarisation...")
        diarization_annotation = run_diarization(audio_wav)
        
        # ==================================================================
        # ÉTAPE 2.5 : IDENTIFICATION DES LOCUTEURS (GPU - WeSpeaker)
        # ==================================================================
        speaker_mapping = _identify_speakers(
            audio_wav, 
            diarization_annotation, 
            meeting_id
        )
        
        # Nettoyage VRAM intermédiaire
        release_models() 

        # ==================================================================
        # ÉTAPE 3 : TRANSCRIPTION (GPU - Whisper)
        # ==================================================================
        logger.info(f"✍️ [JOB {meeting_id}] Étape 3 : Transcription...")
        whisper_segments = run_transcription(audio_wav)
        release_models() 

        # ==================================================================
        # ÉTAPE 4 : FUSION & SAUVEGARDE (S3)
        # ==================================================================
        logger.info(f"🔗 [JOB {meeting_id}] Étape 4 : Fusion et Upload S3...")
        final_data = merge_transcription_diarization(
            whisper_segments, 
            diarization_annotation, 
            speaker_mapping
        )

        # Sauvegarde via storage.py (écrit sur MinIO)
        s3_result_path = save_results(
            clean_name=filename,
            annotation=diarization_annotation,
            raw_segments=whisper_segments,
            fusion_segments=final_data
        )

        logger.info(f"✅ [JOB {meeting_id}] Succès ! Résultats : {s3_result_path}")
        
        # Notify API that transcription is complete
        await _notify_api_completion(meeting_id, "completed", s3_result_path)
        
        return {
            "status": "success", 
            "meeting_id": meeting_id, 
            "result_path": s3_result_path
        }

    except Exception as e:
        logger.error(f"💥 [JOB {meeting_id}] ÉCHEC : {str(e)}", exc_info=True)
        
        # Notify API about the error
        await _notify_api_completion(meeting_id, "error", error_message=str(e))
        
        return {"status": "error", "message": str(e), "meeting_id": meeting_id}

    finally:
        # ==================================================================
        # NETTOYAGE (GARBAGE COLLECTION)
        # ==================================================================
        cleanup_files([local_input_path, audio_wav], meeting_id)


# =============================================================================
# FONCTIONS HELPER PRIVÉES
# =============================================================================

async def _notify_api_completion(
    meeting_id: str, 
    status: str, 
    result_path: str = None, 
    error_message: str = None
):
    """
    Notifie l'API que la transcription est terminée via webhook.
    
    Args:
        meeting_id: ID du meeting (doit être un int pour la DB)
        status: "completed" ou "error"
        result_path: Chemin S3 des résultats (si succès)
        error_message: Message d'erreur (si erreur)
    """
    try:
        # meeting_id peut être un UUID ou un int, on essaie de parser
        try:
            meeting_id_int = int(meeting_id)
        except ValueError:
            logger.warning(f"⚠️ [Webhook] meeting_id '{meeting_id}' n'est pas un int, skip notification")
            return
        
        payload = {
            "meeting_id": meeting_id_int,
            "status": status,
            "result_path": result_path,
            "error_message": error_message
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                API_WEBHOOK_URL,
                json=payload,
                headers={"X-Internal-Key": INTERNAL_API_KEY}
            )
            
            if response.status_code == 200:
                logger.info(f"✅ [Webhook] API notifiée: meeting {meeting_id} -> {status}")
            else:
                logger.warning(f"⚠️ [Webhook] API réponse {response.status_code}: {response.text}")
                
    except Exception as e:
        # Ne pas faire échouer la tâche si le webhook échoue
        logger.warning(f"⚠️ [Webhook] Erreur notification API: {e}")


def _identify_speakers(audio_wav: str, diarization_annotation, meeting_id: str) -> dict:
    """
    Identifie les locuteurs en comparant avec la banque de voix.
    
    Args:
        audio_wav: Chemin du fichier WAV
        diarization_annotation: Annotation de diarisation Pyannote
        meeting_id: ID du meeting pour les logs
        
    Returns:
        dict: Mapping {speaker_label: nom_identifié} ou None si pas de voice bank
    """
    logger.info(f"🎯 [JOB {meeting_id}] Étape 2.5 : Identification des locuteurs...")
    
    bank_embeddings = get_voice_bank_embeddings()
    
    if not bank_embeddings:
        logger.info("   ℹ️ Pas de voice bank, utilisation des labels par défaut")
        return None
    
    # Mapper les speakers détectés vers des noms connus
    embedding_model = load_embedding_model()
    speaker_mapping = {}
    
    for segment, _, speaker in diarization_annotation.itertracks(yield_label=True):
        if speaker not in speaker_mapping:
            speaker_mapping[speaker] = _identify_single_speaker(
                audio_wav=audio_wav,
                segment=segment,
                speaker=speaker,
                embedding_model=embedding_model,
                bank_embeddings=bank_embeddings,
                meeting_id=meeting_id
            )
    
    logger.info(f"   📋 Mapping final: {speaker_mapping}")
    return speaker_mapping


def _identify_single_speaker(
    audio_wav: str,
    segment,
    speaker: str,
    embedding_model,
    bank_embeddings: dict,
    meeting_id: str
) -> str:
    """
    Identifie un seul locuteur à partir d'un segment audio.
    
    Returns:
        str: Nom identifié ou label original si non reconnu
    """
    try:
        import librosa
        import soundfile as sf
        
        # Extraire le segment audio
        audio_segment, sr = librosa.load(
            audio_wav, 
            sr=16000, 
            offset=segment.start, 
            duration=min(segment.duration, 5.0)  # Max 5 secondes
        )
        
        # Sauvegarder temporairement
        temp_segment_path = f"/tmp/{meeting_id}_speaker_{speaker}.wav"
        sf.write(temp_segment_path, audio_segment, sr)
        
        # Calculer l'embedding et identifier
        unknown_emb = embedding_model(temp_segment_path)
        identified_name, score = identify_speaker(unknown_emb, bank_embeddings)
        
        # Nettoyer le fichier temporaire
        os.remove(temp_segment_path)
        
        if identified_name:
            logger.info(f"   ✅ {speaker} -> {identified_name} (score: {score:.2f})")
            return identified_name
        else:
            logger.info(f"   ❓ {speaker} non reconnu (score: {score:.2f})")
            return speaker
            
    except Exception as e:
        logger.warning(f"   ⚠️ Erreur identification {speaker}: {e}")
        return speaker


# =============================================================================
# FUTURES TÂCHES AUDIO
# =============================================================================

# @broker.task(task_name="process_audio_conversion")
# async def process_audio_conversion(file_path: str, target_format: str = "wav"):
#     """
#     Convertit un fichier audio vers un autre format.
#     """
#     pass


# @broker.task(task_name="process_diarization_only")
# async def process_diarization_only(file_path: str, meeting_id: str):
#     """
#     Exécute uniquement la diarisation (sans transcription).
#     """
#     pass
