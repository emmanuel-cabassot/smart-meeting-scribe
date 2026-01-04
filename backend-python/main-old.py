from fastapi import FastAPI, UploadFile, File, HTTPException
from faster_whisper import WhisperModel
from pyannote.audio import Pipeline
import torch
import shutil
import os
import time
import subprocess
import traceback

app = FastAPI(title="Smart Meeting Scribe (Final Edition)")

# ==========================================
# ⚙️ CONFIGURATION & CHARGEMENT
# ==========================================
print("⏳ Initialisation du système...")

# 1. Config GPU
if torch.cuda.is_available():
    DEVICE = "cuda"
    COMPUTE_TYPE = "int8_float16"
    print(f"🚀 GPU Détecté : {torch.cuda.get_device_name(0)}")
else:
    DEVICE = "cpu"
    COMPUTE_TYPE = "int8"
    print("⚠️ GPU non détecté. Le CPU sera utilisé (lent).")

# 2. Chargement WHISPER
print("⏳ Chargement de Whisper (large-v3)...")
whisper_model = WhisperModel("large-v3", device=DEVICE, compute_type=COMPUTE_TYPE)
print("✅ Whisper chargé !")

# 3. Chargement PYANNOTE (Avec Patch de Compatibilité)
print("⏳ Chargement de Pyannote...")
try:
    # --- 🩹 PATCH PYTORCH 2.6 ---
    # Permet de charger le modèle même si PyTorch est trop strict sur la sécurité
    original_torch_load = torch.load
    def patched_torch_load(*args, **kwargs):
        kwargs["weights_only"] = False 
        return original_torch_load(*args, **kwargs)
    torch.load = patched_torch_load
    # ---------------------------

    # Chargement via HF_TOKEN (variable d'environnement)
    diarization_pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1")
    
    # --- FIN DU PATCH ---
    torch.load = original_torch_load
    
    # Envoi sur le GPU
    diarization_pipeline.to(torch.device(DEVICE))
    print("✅ Pyannote chargé !")

except Exception as e:
    # On restaure torch.load si ça plante
    if 'original_torch_load' in locals():
        torch.load = original_torch_load
    print(f"❌ Erreur critique Pyannote : {e}")
    # On laisse tourner pour debug, mais la diarisation plantera
    pass


# ==========================================
# 🛠️ FONCTIONS UTILITAIRES
# ==========================================
def convert_to_wav(input_path: str) -> str:
    """
    Convertit tout fichier audio/vidéo en WAV 16kHz Mono.
    Indispensable pour éviter les erreurs de sample rate de Pyannote.
    """
    output_path = f"{input_path}_converted.wav"
    command = [
        "ffmpeg", "-i", input_path,
        "-vn",                # Pas de vidéo
        "-acodec", "pcm_s16le", # Codec WAV standard
        "-ar", "16000",       # 16000 Hz (Standard IA)
        "-ac", "1",           # Mono
        "-y",                 # Forcer l'écrasement
        output_path
    ]
    try:
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return output_path
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Erreur FFmpeg : Impossible de convertir le fichier.")

def assign_speaker(start, end, diarization_result):
    """
    Trouve qui parle entre start et end.
    """
    max_overlap = 0
    assigned_speaker = "Unknown"
    
    # diarization_result est maintenant un objet Annotation (grâce au fix plus bas)
    for turn, _, speaker in diarization_result.itertracks(yield_label=True):
        intersection_start = max(start, turn.start)
        intersection_end = min(end, turn.end)
        overlap = intersection_end - intersection_start
        
        if overlap > 0 and overlap > max_overlap:
            max_overlap = overlap
            assigned_speaker = speaker
            
    return assigned_speaker


# ==========================================
# 🔌 ROUTE PRINCIPALE
# ==========================================
@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    clean_name = "".join(x for x in file.filename if x.isalnum() or x in "._-")
    temp_filename = f"temp_{clean_name}"
    wav_filename = None 
    
    start_time = time.time()
    
    try:
        # 1. Sauvegarde brut
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        print(f"🎙️  Reçu : {clean_name}")
        
        # 2. Conversion
        print("   -> Conversion en WAV 16kHz...")
        wav_filename = convert_to_wav(temp_filename)
        
        # 3. Diarisation
        print("   -> Analyse des locuteurs...")
        diarization_output = diarization_pipeline(wav_filename)

        # --- 🩹 FIX PYANNOTE UPDATES ---
        # On extrait l'annotation réelle de l'objet wrapper si nécessaire
        if hasattr(diarization_output, 'annotation'):
            diarization_result = diarization_output.annotation
        else:
            diarization_result = diarization_output
        # -------------------------------
        
        # 4. Transcription Whisper
        print("   -> Transcription du texte...")
        segments, info = whisper_model.transcribe(wav_filename, beam_size=5)
        
        # 5. Fusion des résultats
        formatted_segments = []
        
        for segment in segments:
            speaker = assign_speaker(segment.start, segment.end, diarization_result)
            
            segment_data = {
                "start": round(segment.start, 2),
                "end": round(segment.end, 2),
                "text": segment.text.strip(),
                "speaker": speaker
            }
            formatted_segments.append(segment_data)
            
        duration = time.time() - start_time
        print(f"✅ Terminé en {duration:.2f}s.")
        
        return {
            "metadata": {
                "filename": file.filename,
                "language": info.language,
                "duration": duration
            },
            "segments": formatted_segments
        }

    except Exception as e:
        print(f"❌ Erreur : {e}")
        traceback.print_exc() # Affiche les détails dans les logs Docker
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        # Nettoyage
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        if wav_filename and os.path.exists(wav_filename):
            os.remove(wav_filename)