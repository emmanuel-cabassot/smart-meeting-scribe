import asyncio
import logging
import json
import os
from pathlib import Path
from app.broker import broker
from app.core.config import settings

# --- Imports des services IA (Noms synchronisés) ---
from app.services.audio import convert_to_wav
from app.services.diarization import run_diarization
from app.services.transcription import run_transcription
from app.services.fusion import merge_transcription_diarization
from app.core.models import release_models

# Configuration du logging pour le suivi dans la console Docker
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@broker.task(task_name="process_transcription_full")
async def process_transcription_full(file_path: str, meeting_id: str):
    """
    Pipeline orchestré : 
    1. Conversion (CPU)
    2. Diarisation (GPU - Pyannote)
    3. Transcription (GPU - Whisper)
    4. Fusion (CPU)
    """
    audio_wav = None
    try:
        logger.info(f"🚀 [JOB {meeting_id}] Initialisation du traitement...")

        # 0. S'assurer que le dossier de résultats existe
        results_dir = Path(settings.STORAGE_PATH) / "results"
        results_dir.mkdir(parents=True, exist_ok=True)

        # 1. ÉTAPE 0 : CONVERSION AUDIO (CPU)
        # Prépare le terrain pour les modèles IA (16kHz Mono)
        logger.info(f"⏳ [JOB {meeting_id}] Étape 0 : Conversion vers WAV...")
        audio_wav = convert_to_wav(file_path)
        
        # 2. ÉTAPE 1 : DIARISATION (GPU)
        # Qui parle et quand ?
        logger.info(f"👥 [JOB {meeting_id}] Étape 1 : Diarisation (Pyannote)...")
        diarization_annotation = run_diarization(audio_wav)
        
        # Sécurité VRAM : Libère Pyannote avant de charger Whisper
        release_models() 

        # 3. ÉTAPE 2 : TRANSCRIPTION (GPU)
        # Quel est le texte dit ?
        logger.info(f"✍️ [JOB {meeting_id}] Étape 2 : Transcription (Whisper)...")
        # ✅ CORRIGÉ : On ne passe plus 'diarization_annotation' ici
        whisper_segments = run_transcription(audio_wav)
        
        # Sécurité VRAM : Libère Whisper
        release_models() 

        # 4. ÉTAPE 3 : FUSION DES RÉSULTATS (CPU)
        # Attribue chaque phrase de Whisper au bon locuteur de Pyannote
        logger.info(f"🔗 [JOB {meeting_id}] Étape 3 : Fusion des segments...")
        final_data = merge_transcription_diarization(whisper_segments, diarization_annotation)

        # 5. ÉTAPE 4 : SAUVEGARDE FINALE
        result_file = results_dir / f"{meeting_id}.json"
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(final_data, f, ensure_ascii=False, indent=4)

        logger.info(f"✅ [JOB {meeting_id}] Traitement terminé avec succès !")
        logger.info(f"📂 Résultat disponible : {result_file}")
        
        return {
            "status": "success", 
            "meeting_id": meeting_id, 
            "result_path": str(result_file)
        }

    except Exception as e:
        logger.error(f"💥 [JOB {meeting_id}] ERREUR CRITIQUE : {str(e)}", exc_info=True)
        return {"status": "error", "message": str(e), "meeting_id": meeting_id}

    finally:
        # Nettoyage systématique du fichier WAV de travail
        if audio_wav and os.path.exists(audio_wav) and audio_wav != file_path:
            try:
                os.remove(audio_wav)
                logger.info(f"🧹 [JOB {meeting_id}] Nettoyage du fichier WAV de travail effectué.")
            except Exception as clean_err:
                logger.warning(f"⚠️ Erreur lors du nettoyage : {clean_err}")