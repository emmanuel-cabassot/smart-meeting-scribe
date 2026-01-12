import subprocess
import os

def convert_to_wav(input_path: str) -> str:
    """
    Convertit l'entrée en WAV 16kHz Mono via FFmpeg.
    Nécessaire pour la précision de Whisper et Pyannote.
    """
    output_path = f"{input_path}_converted.wav"
    command = [
        "ffmpeg", "-i", input_path, 
        "-vn",               # Pas de flux vidéo
        "-acodec", "pcm_s16le", 
        "-ar", "16000",      # Fréquence d'échantillonnage 16kHz
        "-ac", "1",          # Mono
        "-y",                # Écrase si existe déjà
        output_path
    ]
    try:
        # On capture stderr pour avoir le détail en cas d'erreur FFmpeg
        subprocess.run(command, check=True, capture_output=True)
        return output_path
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode() if e.stderr else "Erreur FFmpeg inconnue"
        raise RuntimeError(f"Erreur Conversion Audio : {error_msg}")

def cleanup_files(*files):
    """Supprime les fichiers temporaires après usage."""
    for f in files:
        if f and os.path.exists(f):
            try:
                os.remove(f)
            except OSError:
                pass