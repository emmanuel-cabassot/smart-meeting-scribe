import asyncio
import logging
import json
import os
import boto3
from urllib.parse import urlparse
from pathlib import Path
from app.broker import broker
from app.core.config import settings

# --- Imports des services IA ---
from app.services.audio import convert_to_wav
from app.services.diarization import run_diarization
from app.services.transcription import run_transcription
from app.services.fusion import merge_transcription_diarization
from app.services.storage import save_results
from app.services.identification import get_voice_bank_embeddings, identify_speaker
from app.core.models import release_models, load_embedding_model

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- CONFIGURATION BOTO3 (Worker) ---
def get_s3_client():
    """Crée un client S3 boto3 configuré pour MinIO."""
    return boto3.client(
        "s3",
        endpoint_url=f"http://{settings.MINIO_ENDPOINT}",
        aws_access_key_id=settings.MINIO_ACCESS_KEY,
        aws_secret_access_key=settings.MINIO_SECRET_KEY
    )


def smart_download(remote_path: str, local_dest: str):
    """
    Télécharge un fichier depuis S3 via Boto3.
    Gère les URL s3://bucket/key
    """
    if remote_path.startswith("s3://"):
        logger.info(f"⬇️ [Boto3] Téléchargement de {remote_path}...")
        
        parsed = urlparse(remote_path)
        bucket_name = parsed.netloc
        object_key = parsed.path.lstrip('/')
        
        s3 = get_s3_client()
        s3.download_file(bucket_name, object_key, local_dest)
        
        logger.info(f"   ✅ Téléchargé vers {local_dest}")
    else:
        # Fallback pour tests locaux
        import shutil
        shutil.copy(remote_path, local_dest)


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
        logger.info(f"🚀 [JOB {meeting_id}] Démarrage Worker V5 (Boto3 Native)")
        logger.info(f"   📥 Source : {file_path}")

        # ======================================================================
        # ÉTAPE 0 : TÉLÉCHARGEMENT DEPUIS MINIO (S3 -> LOCAL)
        # ======================================================================
        filename = Path(file_path).name
        local_input_path = f"/tmp/{meeting_id}_{filename}"
        
        smart_download(file_path, local_input_path)

        # ======================================================================
        # ÉTAPE 1 : CONVERSION AUDIO (CPU)
        # ======================================================================
        audio_wav = convert_to_wav(local_input_path)
        
        # ======================================================================
        # ÉTAPE 2 : DIARISATION (GPU - Pyannote)
        # ======================================================================
        logger.info(f"👥 [JOB {meeting_id}] Étape 2 : Diarisation...")
        diarization_annotation = run_diarization(audio_wav)
        
        # ======================================================================
        # ÉTAPE 2.5 : IDENTIFICATION DES LOCUTEURS (GPU - WeSpeaker)
        # ======================================================================
        logger.info(f"🎯 [JOB {meeting_id}] Étape 2.5 : Identification des locuteurs...")
        
        # Charger la banque de voix
        bank_embeddings = get_voice_bank_embeddings()
        
        if bank_embeddings:
            # Mapper les speakers détectés vers des noms connus
            embedding_model = load_embedding_model()
            speaker_mapping = {}  # Ex: {"SPEAKER_00": "Emmanuel", "SPEAKER_01": "Marie"}
            
            for segment, _, speaker in diarization_annotation.itertracks(yield_label=True):
                if speaker not in speaker_mapping:
                    # Extraire un segment audio pour ce speaker
                    # On prend le premier segment de chaque speaker pour l'identification
                    # TODO: Améliorer en utilisant plusieurs segments
                    try:
                        import librosa
                        audio_segment, sr = librosa.load(
                            audio_wav, 
                            sr=16000, 
                            offset=segment.start, 
                            duration=min(segment.duration, 5.0)  # Max 5 secondes
                        )
                        # Sauvegarder temporairement le segment
                        import soundfile as sf
                        temp_segment_path = f"/tmp/{meeting_id}_speaker_{speaker}.wav"
                        sf.write(temp_segment_path, audio_segment, sr)
                        
                        # Calculer l'embedding et identifier
                        unknown_emb = embedding_model(temp_segment_path)
                        identified_name, score = identify_speaker(unknown_emb, bank_embeddings)
                        
                        if identified_name:
                            speaker_mapping[speaker] = identified_name
                            logger.info(f"   ✅ {speaker} -> {identified_name} (score: {score:.2f})")
                        else:
                            speaker_mapping[speaker] = speaker  # Garder le label original
                            logger.info(f"   ❓ {speaker} non reconnu (score: {score:.2f})")
                        
                        # Nettoyer le fichier temporaire
                        os.remove(temp_segment_path)
                    except Exception as e:
                        logger.warning(f"   ⚠️ Erreur identification {speaker}: {e}")
                        speaker_mapping[speaker] = speaker
            
            logger.info(f"   📋 Mapping final: {speaker_mapping}")
        else:
            logger.info("   ℹ️ Pas de voice bank, utilisation des labels par défaut")
            speaker_mapping = None
        
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
        final_data = merge_transcription_diarization(whisper_segments, diarization_annotation, speaker_mapping)

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