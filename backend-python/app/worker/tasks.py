import asyncio
import logging
import os
import traceback
from pathlib import Path
from datetime import datetime
import time

# --- Framework Taskiq ---
from app.broker import broker

# --- Config & Infra V3.1 ---
from app.core.config import settings
from app.core.database import get_worker_db
from app.core.models_db import Meeting
from app.services.storage import storage

# --- Services IA ---
from app.services.audio import convert_to_wav, cleanup_files
from app.services.diarization import run_diarization
from app.services.transcription import run_transcription
from app.services.fusion import merge_transcription_diarization
from app.services.identification import get_voice_bank_embeddings, identify_speaker
from app.core.models import release_models, load_embedding_model

# Import spécifique Pyannote
from pyannote.audio.core.io import Audio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@broker.task(task_name="process_transcription_full")
async def process_transcription_full(file_path: str, meeting_id: str):
    """
    Pipeline V3.1 : 
    1. Mise à jour DB (PROCESSING)
    2. Pipeline IA (Diarisation -> Identification -> Transcription)
    3. Sauvegarde via Storage (JSONs)
    4. Mise à jour DB (COMPLETED)
    
    Args:
        file_path: Chemin relatif du fichier (ex: "uploads/uuid.wav")
        meeting_id: UUID de la réunion
    """
    start_time = time.time()
    audio_wav = None
    
    # On ouvre une session DB dédiée à ce job
    async with get_worker_db() as db:
        try:
            # 1. RÉCUPÉRATION DU JOB & PASSAGE EN "PROCESSING"
            logger.info(f"🚀 [JOB {meeting_id}] Démarrage du pipeline V3.1...")
            
            # On récupère l'objet Meeting dans la base
            meeting = await db.get(Meeting, meeting_id)
            if not meeting:
                logger.error(f"❌ [JOB {meeting_id}] Meeting introuvable en base !")
                return
            
            meeting.status = "PROCESSING"
            await db.commit()

            # 2. PRÉPARATION FICHIER (Construction du chemin absolu pour FFmpeg)
            # FFmpeg a besoin d'un vrai chemin fichier sur le disque
            # Dans la V3.1 (Local), on reconstruit le chemin complet : /data/uploads/xxx.wav
            input_abs_path = os.path.join(settings.STORAGE_PATH, file_path)
            
            # ÉTAPE 0 : CONVERSION AUDIO (CPU)
            # Convertit en WAV 16kHz Mono
            audio_wav = convert_to_wav(input_abs_path)
            
            # 3. ÉTAPE 1 : DIARISATION (GPU - Pyannote)
            logger.info(f"👥 [JOB {meeting_id}] Étape 1 : Diarisation (Pyannote)...")
            diarization_annotation = run_diarization(audio_wav)
            
            # 4. ÉTAPE 1.5 : IDENTIFICATION DES VOIX (WeSpeaker)
            logger.info(f"🔍 [JOB {meeting_id}] Étape 1.5 : Identification (WeSpeaker)...")
            
            bank_signatures = get_voice_bank_embeddings()
            speaker_mapping = {}
            
            if bank_signatures:
                audio_loader = Audio(sample_rate=16000, mono="downmix")
                inference_model = load_embedding_model() 
                
                for speaker in diarization_annotation.labels():
                    try:
                        # On prend le segment le plus long pour ce speaker
                        speaker_timeline = diarization_annotation.label_timeline(speaker)
                        longest_segment = max(speaker_timeline, key=lambda x: x.duration)
                        waveform, sr = audio_loader.crop(audio_wav, longest_segment)
                        
                        # Embedding & Comparaison
                        speaker_emb = inference_model({"waveform": waveform, "sample_rate": sr})
                        name, score = identify_speaker(speaker_emb, bank_signatures, threshold=0.5)
                        
                        if name:
                            logger.info(f"   👤 {speaker} reconnu : {name} ({score:.2f})")
                            speaker_mapping[speaker] = name
                    except Exception as e:
                        logger.warning(f"   ⚠️ Erreur identif. {speaker}: {e}")

            # Nettoyage VRAM avant Whisper
            release_models() 

            # 5. ÉTAPE 2 : TRANSCRIPTION (GPU - Whisper)
            logger.info(f"✍️ [JOB {meeting_id}] Étape 2 : Transcription (Whisper)...")
            whisper_segments = run_transcription(audio_wav)
            release_models() 

            # 6. ÉTAPE 3 : FUSION & MAPPING
            logger.info(f"🔗 [JOB {meeting_id}] Étape 3 : Fusion...")
            final_data = merge_transcription_diarization(whisper_segments, diarization_annotation)
            
            # Application des noms identifiés
            for segment in final_data:
                if segment["speaker"] in speaker_mapping:
                    segment["speaker"] = speaker_mapping[segment["speaker"]]

            # 7. SAUVEGARDE VIA STORAGE ABSTRAIT
            # On prépare les données pour diarisation.json et transcription.json
            diarization_list = [
                {"start": turn.start, "end": turn.end, "speaker": speaker}
                for turn, _, speaker in diarization_annotation.itertracks(yield_label=True)
            ]
            transcription_list = [
                {"start": s.start, "end": s.end, "text": s.text.strip()} 
                for s in whisper_segments
            ]
            
            # Le service storage s'occupe de créer les dossiers et fichiers
            saved_paths = storage.save_results(
                meeting_id=meeting_id,
                clean_name=Path(file_path).name,
                data_dict={
                    "fusion": final_data,
                    "diarization": diarization_list,
                    "transcription": transcription_list
                }
            )

            # 8. CLÔTURE DU JOB EN BASE
            duration = time.time() - start_time
            
            meeting.status = "COMPLETED"
            meeting.processing_duration = round(duration, 2)
            # On enregistre les chemins relatifs renvoyés par storage
            meeting.fusion_path = saved_paths.get("fusion")
            meeting.diarization_path = saved_paths.get("diarization")
            meeting.transcription_path = saved_paths.get("transcription")
            
            await db.commit()
            logger.info(f"✅ [JOB {meeting_id}] Terminés en {duration:.1f}s.")

        except Exception as e:
            # GESTION DES ERREURS
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            logger.error(f"💥 [JOB {meeting_id}] CRASH : {error_msg}")
            
            # On tente de noter l'erreur en base
            try:
                # On recharge l'objet au cas où la session soit sale
                if 'meeting' in locals() and meeting:
                    meeting.status = "ERROR"
                    meeting.error_message = str(e)
                    await db.commit()
            except:
                logger.error("Impossible de sauvegarder l'erreur en DB.")
                
        finally:
            # Nettoyage fichier WAV temporaire
            if audio_wav and os.path.exists(audio_wav):
                cleanup_files(audio_wav)