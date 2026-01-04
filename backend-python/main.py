from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil
import time
import traceback

# On importe les fonctions de gestion mémoire
from core.models import release_models
from services.audio import convert_to_wav, cleanup_files
from services.diarization import run_diarization
from services.transcription import run_transcription
from services.fusion import merge_transcription_diarization
from services.storage import save_results

app = FastAPI(title="Smart Meeting Scribe (Modular + VRAM Saver)")

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    clean_name = "".join(x for x in file.filename if x.isalnum() or x in "._-")
    temp_filename = f"temp_{clean_name}"
    wav_filename = None 
    start_time = time.time()
    
    try:
        # 0. SETUP
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"🎙️  Traitement de : {clean_name}")
        
        # 1. Conversion Audio
        print("   -> Conversion WAV...")
        wav_filename = convert_to_wav(temp_filename)
        
        # ═══════════════════════════════════════════════════════════
        # 2. DIARISATION (Charge -> Traite -> Vide)
        # ═══════════════════════════════════════════════════════════
        print("📥 [1/3] Diarisation...")
        # Note: run_diarization appelle load_pyannote() en interne
        annotation = run_diarization(wav_filename)
        
        # 🛑 NETTOYAGE VRAM (On vire Pyannote)
        release_models()
        
        # ═══════════════════════════════════════════════════════════
        # 3. TRANSCRIPTION (Charge -> Traite -> Vide)
        # ═══════════════════════════════════════════════════════════
        print("✍️ [2/3] Transcription...")
        segments = run_transcription(wav_filename)
        
        # 🛑 NETTOYAGE VRAM (On vire Whisper)
        release_models()
        
        # ═══════════════════════════════════════════════════════════
        # 4. FUSION & SAUVEGARDE (CPU uniquement)
        # ═══════════════════════════════════════════════════════════
        print("🧩 [3/3] Fusion & Archivage...")
        final_result = merge_transcription_diarization(segments, annotation)
        save_path = save_results(clean_name, annotation, segments, final_result)
        
        duration = time.time() - start_time
        print(f"✅ Terminé en {duration:.2f}s. (Saved in {save_path})")
        
        return {
            "metadata": {
                "filename": file.filename, 
                "duration": duration,
                "saved_at": save_path
            },
            "segments": final_result
        }

    except Exception as e:
        print(f"❌ Erreur : {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        cleanup_files(temp_filename, wav_filename)
        # 🛡️ Sécurité ultime : on nettoie tout en sortant
        release_models()