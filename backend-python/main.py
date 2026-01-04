"""
📜 SMART MEETING SCRIBE - BACKEND API (V3 Final + Sauvegarde)
=============================================================

Ce serveur FastAPI orchestre un pipeline d'IA hybride pour la transcription de réunions.

FONCTIONNEMENT :
1. Réception du fichier audio/vidéo via API REST.
2. Conversion FFmpeg en WAV 16kHz Mono (Standardisation).
3. DIARISATION (Pyannote) : Identification des plages de temps par locuteur.
4. TRANSCRIPTION (Whisper) : Conversion de la parole en texte.
5. FUSION : Algorithme d'alignement temporel pour attribuer chaque phrase au bon locuteur.
6. SAUVEGARDE : Enregistrement des résultats (Diarisation, Transcription, Fusion) sur le disque.

AUTEUR : Généré via assistance IA pour architecture Docker/CUDA.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from faster_whisper import WhisperModel
from pyannote.audio import Pipeline
import torch
import shutil
import os
import time
import subprocess
import traceback
import json
from datetime import datetime

app = FastAPI(title="Smart Meeting Scribe (Final V3 + Save)")

# ==========================================
# ⚙️ CONFIGURATION & CHARGEMENT
# ==========================================
print("⏳ Initialisation du système...")

# 🚀 BOOST PERFORMANCE RTX 4000 (TF32)
import torch
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True

# 1. Config GPU
if torch.cuda.is_available():
    DEVICE = "cuda"
    COMPUTE_TYPE = "int8_float16"
    print(f"🚀 GPU Détecté : {torch.cuda.get_device_name(0)}")
else:
    DEVICE = "cpu"
    COMPUTE_TYPE = "int8"
    print("⚠️ GPU non détecté.")

# 2. Whisper
print("⏳ Chargement de Whisper (large-v3)...")
whisper_model = WhisperModel("large-v3", device=DEVICE, compute_type=COMPUTE_TYPE)
print("✅ Whisper chargé !")

# 3. Pyannote
print("⏳ Chargement de Pyannote...")
try:
    # --- PATCH SECURITE PYTORCH 2.6 ---
    original_torch_load = torch.load
    def patched_torch_load(*args, **kwargs):
        kwargs["weights_only"] = False 
        return original_torch_load(*args, **kwargs)
    torch.load = patched_torch_load
    
    # Chargement du Pipeline
    diarization_pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1")
    diarization_pipeline.to(torch.device(DEVICE))
    
    # Restauration
    torch.load = original_torch_load
    print("✅ Pyannote chargé !")

except Exception as e:
    if 'original_torch_load' in locals():
        torch.load = original_torch_load
    print(f"❌ Erreur Pyannote : {e}")
    pass

# ==========================================
# 🛠️ FONCTIONS UTILITAIRES
# ==========================================
def convert_to_wav(input_path: str) -> str:
    """Convertit l'entrée en WAV 16kHz Mono via FFmpeg."""
    output_path = f"{input_path}_converted.wav"
    command = ["ffmpeg", "-i", input_path, "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", "-y", output_path]
    try:
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return output_path
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Erreur Conversion Audio (FFmpeg)")

def get_diarization_object(diarization_result):
    """Extrait l'objet annotation propre depuis le wrapper Pyannote."""
    if hasattr(diarization_result, 'speaker_diarization'):
        return diarization_result.speaker_diarization
    elif hasattr(diarization_result, 'annotation'):
        return diarization_result.annotation
    return diarization_result

def assign_speaker(start, end, diarization_result):
    """
    Algorithme de Fusion : Trouve le locuteur majoritaire sur un segment.
    """
    diarization_result = get_diarization_object(diarization_result)
    
    max_overlap = 0
    assigned_speaker = "Unknown"
    
    # Sécurité anti-crash
    if not hasattr(diarization_result, 'itertracks'):
        return "Speaker_Error"

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
    # Nettoyage nom de fichier
    clean_name = "".join(x for x in file.filename if x.isalnum() or x in "._-")
    temp_filename = f"temp_{clean_name}"
    wav_filename = None 
    
    start_time = time.time()
    
    try:
        # 1. Sauvegarde Fichier Brut (Temporaire)
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"🎙️  Reçu : {clean_name}")
        
        # 2. Conversion
        print("   -> Conversion en WAV 16kHz...")
        wav_filename = convert_to_wav(temp_filename)
        
        # 3. Diarisation
        print("   -> Analyse des locuteurs (Pyannote)...")
        diarization_raw = diarization_pipeline(wav_filename)
        
        # 4. Transcription
        print("   -> Transcription du texte (Whisper)...")
        segments, info = whisper_model.transcribe(wav_filename, beam_size=5)
        # Note : 'segments' est un générateur, on doit le convertir en liste pour le réutiliser
        segments = list(segments) 
        
        # 5. Fusion
        formatted_segments = []
        for segment in segments:
            speaker = assign_speaker(segment.start, segment.end, diarization_raw)
            formatted_segments.append({
                "start": round(segment.start, 2),
                "end": round(segment.end, 2),
                "text": segment.text.strip(),
                "speaker": speaker
            })
            
        duration = time.time() - start_time
        print(f"✅ Terminé en {duration:.2f}s.")

        # ==========================================
        # 💾 SAUVEGARDE SUR DISQUE (ARCHIVAGE)
        # ==========================================
        print("   -> Sauvegarde des archives...")
        
        # A. Création du dossier unique
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_name = f"{timestamp}_{clean_name.split('.')[0]}"
        save_dir = os.path.join("recordings", folder_name)
        os.makedirs(save_dir, exist_ok=True)
        
        # B. Préparation des données Diarisation (Brut)
        diarization_data = []
        annotation = get_diarization_object(diarization_raw)
        if hasattr(annotation, 'itertracks'):
            for turn, _, speaker in annotation.itertracks(yield_label=True):
                diarization_data.append({
                    "start": round(turn.start, 2),
                    "end": round(turn.end, 2),
                    "speaker": speaker
                })
                
        # C. Préparation des données Transcription (Brut)
        transcription_data = []
        for seg in segments:
            transcription_data.append({
                "start": round(seg.start, 2),
                "end": round(seg.end, 2),
                "text": seg.text.strip()
            })

        # D. Écriture des 3 fichiers JSON
        
        # 1. diarization.json
        with open(os.path.join(save_dir, "diarization.json"), "w", encoding="utf-8") as f:
            json.dump(diarization_data, f, indent=2, ensure_ascii=False)
            
        # 2. transcription.json
        with open(os.path.join(save_dir, "transcription.json"), "w", encoding="utf-8") as f:
            json.dump(transcription_data, f, indent=2, ensure_ascii=False)
            
        # 3. fusion.json (Le résultat final)
        with open(os.path.join(save_dir, "fusion.json"), "w", encoding="utf-8") as f:
            json.dump(formatted_segments, f, indent=2, ensure_ascii=False)

        print(f"📂 Archives sauvegardées dans : /app/{save_dir}")
        # ==========================================
        
        return {
            "metadata": {
                "filename": file.filename, 
                "duration": duration,
                "saved_at": save_dir
            },
            "segments": formatted_segments
        }

    except Exception as e:
        print(f"❌ Erreur : {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        # Nettoyage des fichiers temporaires (mais on garde le dossier recordings !)
        if os.path.exists(temp_filename): os.remove(temp_filename)
        if wav_filename and os.path.exists(wav_filename): os.remove(wav_filename)