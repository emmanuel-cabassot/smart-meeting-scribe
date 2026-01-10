"""
Endpoint de transcription audio.
Orchestration du pipeline : Audio → Diarisation → Identification → Transcription → Fusion
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import time
import traceback
import os

# ══════════════════════════════════════════════════════════════════════════════
# IMPORTS
# ══════════════════════════════════════════════════════════════════════════════
from app.core.models import release_models, load_embedding_model
from app.services.audio import convert_to_wav, cleanup_files
from app.services.diarization import run_diarization
from app.services.transcription import run_transcription
from app.services.identification import get_voice_bank_embeddings, identify_speaker
from app.services.fusion import merge_transcription_diarization
from app.services.storage import save_results

router = APIRouter()

# ══════════════════════════════════════════════════════════════════════════════
# UTILITAIRE DE LOGGING
# ══════════════════════════════════════════════════════════════════════════════
def log_step(message, start_time=None):
    """Affiche un log visuel avec la durée si start_time est fourni."""
    if start_time:
        duration = time.time() - start_time
        print(f"   ✅ Terminé en {duration:.2f} secondes.")
        print(f"---------------------------------------------------")
    else:
        print(f"\n🚀 [ÉTAPE] {message}")
        print(f"---------------------------------------------------")
    return time.time()

# ══════════════════════════════════════════════════════════════════════════════
# ROUTE PRINCIPALE
# ══════════════════════════════════════════════════════════════════════════════
@router.post("/")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Orchestre tout le processus IA de A à Z.
    """
    # Timer Global
    global_start = time.time()
    
    clean_name = "".join(x for x in file.filename if x.isalnum() or x in "._-")
    temp_filename = f"temp_{clean_name}"
    wav_filename = None 
    
    print(f"\n\n===================================================")
    print(f"📥 RÉCEPTION : {clean_name}")
    print(f"===================================================")

    try:
        # --- ÉTAPE 0 : Sauvegarde ---
        t0 = log_step("0. Sauvegarde Fichier Temporaire")
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        log_step("Fichier sauvegardé", t0)
        
        # --- ÉTAPE 1 : Conversion ---
        t1 = log_step("1. Conversion Audio (WAV 16kHz Mono)")
        wav_filename = convert_to_wav(temp_filename)
        log_step("Conversion terminée", t1)
        
        # --- ÉTAPE 2 : Diarisation ---
        t2 = log_step("2. Diarisation (Qui parle quand ?)")
        annotation = run_diarization(wav_filename)
        
        # Petit log stat
        nb_segments = len(list(annotation.itertracks(yield_label=True)))
        print(f"   📊 Segments détectés : {nb_segments}")
        
        release_models() # Important : On vide pour laisser la place à la suite
        log_step("Diarisation terminée", t2)
        
        # --- ÉTAPE 3 : Identification ---
        t3 = log_step("3. Identification Vocale (WeSpeaker)")
        bank_embeddings = get_voice_bank_embeddings()
        speaker_mapping = {}
        
        if bank_embeddings:
            print(f"   📂 Banque de voix chargée ({len(bank_embeddings)} profils)")
            emb_model = load_embedding_model()
            
            # On récupère les labels (SPEAKER_00, SPEAKER_01...)
            detected_labels = annotation.labels()
            
            for label in detected_labels:
                # On cherche le segment le plus long pour ce speaker pour avoir une bonne identification
                track_segment = next((s for s, _, l in annotation.itertracks(yield_label=True) if l == label and s.duration > 2.0), None)
                
                if track_segment:
                    # On découpe l'audio sur ce segment précis
                    unknown_emb = emb_model.crop(wav_filename, track_segment)
                    # On compare
                    name, score = identify_speaker(unknown_emb, bank_embeddings)
                    
                    if name:
                        print(f"   🔍 {label} identifié comme 👤 {name} (Score: {score:.2f})")
                        speaker_mapping[label] = name
                    else:
                        print(f"   ❓ {label} inconnu")
                        speaker_mapping[label] = label
                else:
                    speaker_mapping[label] = label
        else:
            print("   ⚠️ Pas de banque de voix trouvée, identification sautée.")
            
        release_models()
        log_step("Identification terminée", t3)
        
        # --- ÉTAPE 4 : Transcription ---
        t4 = log_step("4. Transcription (Whisper Large-v3)")
        segments = run_transcription(wav_filename)
        print(f"   📝 Phrases transcrites : {len(segments)}")
        release_models()
        log_step("Transcription terminée", t4)
        
        # --- ÉTAPE 5 : Fusion & Sauvegarde ---
        t5 = log_step("5. Fusion & Résultat Final")
        
        # On applique le mapping des noms (SPEAKER_00 -> Emmanuel)
        final_result = merge_transcription_diarization(segments, annotation)
        for item in final_result:
            if item["speaker"] in speaker_mapping:
                item["speaker"] = speaker_mapping[item["speaker"]]
        
        save_path = save_results(clean_name, annotation, segments, final_result)
        
        log_step(f"Sauvegarde effectuée dans : {save_path}", t5)
        
        # Bilan
        total_duration = time.time() - global_start
        print(f"\n✨ SUCCÈS - Durée totale : {total_duration:.2f}s ✨")
        print(f"===================================================\n")

        return {
            "metadata": {
                "filename": clean_name,
                "duration_process": round(total_duration, 2),
                "saved_at": save_path
            }, 
            "segments": final_result
        }

    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE : {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        if wav_filename:
            cleanup_files(temp_filename, wav_filename)
        else:
            cleanup_files(temp_filename)
        
        release_models()
