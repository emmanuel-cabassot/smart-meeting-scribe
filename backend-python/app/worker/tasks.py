import asyncio
import logging
import json
import os
from pathlib import Path
from app.broker import broker
from app.core.config import settings

# --- Imports des services IA ---
from app.services.audio import convert_to_wav
from app.services.diarization import run_diarization
from app.services.transcription import run_transcription
from app.services.fusion import merge_transcription_diarization
from app.core.models import release_models, load_embedding_model

# Services d'identification (WeSpeaker)
from app.services.identification import get_voice_bank_embeddings, identify_speaker

# Import spécifique pour le découpage audio propre
from pyannote.audio.core.io import Audio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@broker.task(task_name="process_transcription_full")
async def process_transcription_full(file_path: str, meeting_id: str):
    """
    Pipeline complet : 
    Conversion -> Diarisation -> Identification (WeSpeaker) -> Transcription -> Fusion.
    """
    audio_wav = None
    try:
        logger.info(f"🚀 [JOB {meeting_id}] Démarrage du pipeline complet...")
        results_dir = Path(settings.STORAGE_PATH) / "results"
        results_dir.mkdir(parents=True, exist_ok=True)

        # 1. ÉTAPE 0 : CONVERSION AUDIO (CPU)
        audio_wav = convert_to_wav(file_path)
        
        # 2. ÉTAPE 1 : DIARISATION (GPU - Pyannote)
        logger.info(f"👥 [JOB {meeting_id}] Étape 1 : Diarisation (Pyannote)...")
        diarization_annotation = run_diarization(audio_wav)
        
        # 🌟 ÉTAPE 1.5 : IDENTIFICATION DES VOIX (WeSpeaker)
        logger.info(f"🔍 [JOB {meeting_id}] Étape 1.5 : Reconnaissance vocale (WeSpeaker)...")
        
        # A. On génère les signatures de la banque de voix (Homme.wav, Femme.wav)
        bank_signatures = get_voice_bank_embeddings()
        
        # B. On initialise l'outil de découpage et le modèle WeSpeaker
        speaker_mapping = {}
        audio_loader = Audio(sample_rate=16000, mono="downmix")
        inference_model = load_embedding_model() 
        
        for speaker in diarization_annotation.labels():
            try:
                # Récupérer les segments du locuteur et choisir le plus long (plus de données = meilleure signature)
                speaker_timeline = diarization_annotation.label_timeline(speaker)
                longest_segment = max(speaker_timeline, key=lambda x: x.duration)
                
                # Découpage physique du signal audio pour ce locuteur
                waveform, sr = audio_loader.crop(audio_wav, longest_segment)
                
                # Calcul de l'embedding (signature) via WeSpeaker
                # On passe le dictionnaire waveform/sample_rate attendu par WeSpeaker
                speaker_emb = inference_model({"waveform": waveform, "sample_rate": sr})
                
                # Comparaison avec la banque (Homme/Femme) via Similarité Cosinus
                name, score = identify_speaker(speaker_emb, bank_signatures, threshold=0.5)
                
                if name:
                    logger.info(f"   👤 {speaker} identifié comme : {name} (score: {score:.2f})")
                    speaker_mapping[speaker] = name
                else:
                    logger.info(f"   ❓ {speaker} non reconnu dans la banque (score: {score:.2f})")
                    
            except Exception as e:
                logger.warning(f"   ⚠️ Échec identification pour {speaker}: {str(e)}")

        # Nettoyage VRAM pour laisser la place à Whisper
        release_models() 

        # 3. ÉTAPE 2 : TRANSCRIPTION (GPU - Whisper)
        logger.info(f"✍️ [JOB {meeting_id}] Étape 2 : Transcription (Whisper)...")
        whisper_segments = run_transcription(audio_wav)
        release_models() 

        # 4. ÉTAPE 3 : FUSION DES RÉSULTATS (CPU)
        logger.info(f"🔗 [JOB {meeting_id}] Étape 3 : Fusion et renommage...")
        final_data = merge_transcription_diarization(whisper_segments, diarization_annotation)
        
        # On remplace SPEAKER_XX par "Homme" ou "Femme"
        for segment in final_data:
            label = segment["speaker"]
            if label in speaker_mapping:
                segment["speaker"] = speaker_mapping[label]

        # 5. SAUVEGARDE FINALE
        result_file = results_dir / f"{meeting_id}.json"
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(final_data, f, ensure_ascii=False, indent=4)

        logger.info(f"✅ [JOB {meeting_id}] Succès ! Résultat : {result_file}")
        return {"status": "success", "meeting_id": meeting_id, "result_path": str(result_file)}

    except Exception as e:
        logger.error(f"💥 [JOB {meeting_id}] ÉCHEC : {str(e)}", exc_info=True)
        return {"status": "error", "message": str(e), "meeting_id": meeting_id}

    finally:
        # Nettoyage
        if audio_wav and os.path.exists(audio_wav) and audio_wav != file_path:
            try:
                os.remove(audio_wav)
                logger.info(f"🧹 [JOB {meeting_id}] Nettoyage WAV temporaire.")
            except:
                pass