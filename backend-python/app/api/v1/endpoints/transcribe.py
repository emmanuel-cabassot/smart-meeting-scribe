"""
Endpoint de transcription audio.

Ce fichier définit la route POST /api/v1/process/ qui orchestre tout le pipeline :
Audio → Diarisation → Identification → Transcription → Fusion → Sauvegarde

L'objet `router` créé ici est importé par api/v1/router.py qui le branche
sur le préfixe "/process". C'est le pattern FastAPI pour modulariser les routes.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import time
import traceback

# ══════════════════════════════════════════════════════════════════════════════
# IMPORTS INTERNES - On importe nos services métier
# ══════════════════════════════════════════════════════════════════════════════
from app.core.models import release_models           # Libération mémoire GPU
from app.services.audio import convert_to_wav, cleanup_files  # Conversion audio
from app.services.diarization import run_diarization          # "Qui parle quand?"
from app.services.transcription import run_transcription      # "Qu'est-ce qui est dit?"
from app.services.identification import get_voice_bank_embeddings, identify_speaker  # "C'est qui?"
from app.services.fusion import merge_transcription_diarization  # Combine le tout
from app.services.storage import save_results                    # Sauvegarde JSON

# ══════════════════════════════════════════════════════════════════════════════
# CRÉATION DU ROUTER
# ══════════════════════════════════════════════════════════════════════════════
# Ce router sera importé par api/v1/router.py avec la ligne :
#   from app.api.v1.endpoints import transcribe
#   api_router.include_router(transcribe.router, prefix="/process")
#
# Résultat : la route @router.post("/") ci-dessous devient POST /api/v1/process/
# ══════════════════════════════════════════════════════════════════════════════
router = APIRouter()


@router.post("/")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Endpoint principal de transcription.
    
    Reçoit un fichier audio et retourne la transcription avec identification des locuteurs.
    
    Args:
        file: Fichier audio uploadé (mp3, m4a, wav, etc.)
    
    Returns:
        JSON avec metadata et segments de transcription
    """
    clean_name = "".join(x for x in file.filename if x.isalnum() or x in "._-")
    temp_filename = f"temp_{clean_name}"
    wav_filename = None 
    start_time = time.time()
    
    try:
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        wav_filename = convert_to_wav(temp_filename)
        
        # 1. Diarisation
        annotation = run_diarization(wav_filename)
        release_models()
        
        # 2. Identification
        bank_embeddings = get_voice_bank_embeddings()
        speaker_mapping = {}
        if bank_embeddings:
            # (Le code d'identification que nous avons validé...)
            detected_labels = annotation.labels()
            from pyannote.audio import Inference
            from app.core.models import load_embedding_model
            emb_model = load_embedding_model()
            
            for label in detected_labels:
                track_segment = next((s for s, _, l in annotation.itertracks(yield_label=True) if l == label and s.duration > 2.0), None)
                if track_segment:
                    unknown_emb = emb_model.crop(wav_filename, track_segment)
                    name, score = identify_speaker(unknown_emb, bank_embeddings)
                    # Si identification réussie, on utilise le nom, sinon on garde le label par défaut
                    speaker_mapping[label] = name if name else label
                else:
                    # Pas de segment assez long → on garde le label par défaut (SPEAKER_XX)
                    speaker_mapping[label] = label
        release_models()
        
        # 3. Transcription
        segments = run_transcription(wav_filename)
        release_models()
        
        # 4. Fusion
        final_result = merge_transcription_diarization(segments, annotation)
        for item in final_result:
            if item["speaker"] in speaker_mapping:
                item["speaker"] = speaker_mapping[item["speaker"]]
        
        save_path = save_results(clean_name, annotation, segments, final_result)
        
        return {"metadata": {"saved_at": save_path}, "segments": final_result}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cleanup_files(temp_filename, wav_filename)
        release_models()
