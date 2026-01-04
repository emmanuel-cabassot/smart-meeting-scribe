from core.models import load_pyannote  # On importe la fonction, pas le modèle

def get_diarization_object(diarization_result):
    """Extrait l'objet annotation propre depuis le wrapper Pyannote."""
    if hasattr(diarization_result, 'speaker_diarization'):
        return diarization_result.speaker_diarization
    elif hasattr(diarization_result, 'annotation'):
        return diarization_result.annotation
    return diarization_result

def run_diarization(wav_path):
    """Lance le pipeline sur un fichier audio (charge Pyannote à la demande)."""
    # CHARGEMENT À LA DEMANDE
    pipeline = load_pyannote()
    
    raw_result = pipeline(wav_path)
    return get_diarization_object(raw_result)
