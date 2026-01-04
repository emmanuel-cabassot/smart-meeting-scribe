from fastapi import FastAPI, UploadFile, File, HTTPException
from faster_whisper import WhisperModel
import torch
import shutil
import os
import time

app = FastAPI(title="Smart Meeting Scribe (Faster Engine)")

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================
MODEL_SIZE = "large-v3"
print("⏳ Initialisation du système...")

if torch.cuda.is_available():
    DEVICE = "cuda"
    COMPUTE_TYPE = "int8_float16"
    GPU_NAME = torch.cuda.get_device_name(0)
    print(f"🚀 GPU Détecté : {GPU_NAME} (Mode Optimisé {COMPUTE_TYPE})")
else:
    DEVICE = "cpu"
    COMPUTE_TYPE = "int8"
    print("⚠️ GPU non détecté, passage en mode CPU.")

try:
    print(f"⏳ Chargement du modèle {MODEL_SIZE}...")
    model = WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)
    print(f"✅ Modèle chargé !")
except Exception as e:
    print(f"❌ Erreur critique : {e}")
    raise e

# ==========================================
# 🔌 ROUTES API
# ==========================================

@app.get("/")
def read_root():
    return {"status": "Online", "engine": "faster-whisper", "model": MODEL_SIZE}

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Renvoie le texte DÉCOUPÉ par segments temporels.
    Prépare le terrain pour la diarisation.
    """
    clean_name = "".join(x for x in file.filename if x.isalnum() or x in "._-")
    temp_filename = f"temp_{clean_name}"
    start_time = time.time()
    
    try:
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"🎙️  Transcription de {clean_name} avec Timestamps...")
        
        # On lance la transcription
        segments, info = model.transcribe(temp_filename, beam_size=5)
        
        # --- NOUVEAU : On structure les données ---
        formatted_segments = []
        full_text = ""
        
        for segment in segments:
            # On construit un objet propre pour chaque phrase
            segment_data = {
                "start": round(segment.start, 2),  # Arrondi à 2 décimales (ex: 12.54s)
                "end": round(segment.end, 2),
                "text": segment.text.strip(),
                "speaker": "Unknown" # Placeholder pour la future étape 2
            }
            formatted_segments.append(segment_data)
            full_text += segment.text + " "
            
        duration = time.time() - start_time
        print(f"✅ Terminé en {duration:.2f}s.")
        
        return {
            "metadata": {
                "filename": file.filename,
                "language": info.language,
                "duration_processing": round(duration, 2),
            },
            # C'est ici que ça change : on renvoie la liste détaillée
            "segments": formatted_segments,
            # On garde le texte complet pour un affichage rapide si besoin
            "full_text": full_text.strip()
        }

    except Exception as e:
        print(f"❌ Erreur : {e}")
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)