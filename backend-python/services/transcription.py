from core.models import load_whisper


def run_transcription(wav_path: str) -> list:
    """
    Charge le modèle Whisper, transcrit le fichier audio et retourne les segments.
    
    Args:
        wav_path: Chemin vers le fichier audio WAV à transcrire
        
    Returns:
        Liste des segments transcrits
    """
    model = load_whisper()
    segments, info = model.transcribe(wav_path, beam_size=5)
    return list(segments)
