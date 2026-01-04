import subprocess
import os
from fastapi import HTTPException

def convert_to_wav(input_path: str) -> str:
    """Convertit l'entrée en WAV 16kHz Mono via FFmpeg."""
    output_path = f"{input_path}_converted.wav"
    command = [
        "ffmpeg", "-i", input_path, 
        "-vn",               # Pas de vidéo
        "-acodec", "pcm_s16le", 
        "-ar", "16000",      # 16kHz
        "-ac", "1",          # Mono
        "-y",                # Force overwrite
        output_path
    ]
    try:
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return output_path
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Erreur Conversion Audio (FFmpeg)")

def cleanup_files(*files):
    """Supprime les fichiers temporaires."""
    for f in files:
        if f and os.path.exists(f):
            os.remove(f)
