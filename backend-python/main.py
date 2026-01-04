from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil
import time
import traceback

# Import des fonctions de gestion mémoire
from core.models import release_models
from services.audio import convert_to_wav, cleanup_files
from services.diarization import run_diarization
from services.transcription import run_transcription
from services.identification import get_voice_bank_embeddings, identify_speaker # <--- NOUVEAU
from services.fusion import merge_transcription_diarization
from services.storage import save_results

app = FastAPI(title="Smart Meeting Scribe (Full Stack IA - Identification)")

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
        # 2. DIARISATION
        # ═══════════════════════════════════════════════════════════
        print("📥 [1/4] Diarisation...")
        annotation = run_diarization(wav_filename)
        release_models() # On libère la VRAM après Pyannote
        
        # ═══════════════════════════════════════════════════════════
        # 3. IDENTIFICATION VOCALE (Le nouveau "cerveau")
        # ═══════════════════════════════════════════════════════════
        print("🔍 [2/4] Identification des locuteurs...")
        
        # A. Charger la banque de voix (crée les embeddings Homme/Femme)
        bank_embeddings = get_voice_bank_embeddings()
        
        # B. Mapper chaque SPEAKER trouvé à un nom de la banque
        speaker_mapping = {}
        if bank_embeddings:
            # On récupère la liste des labels uniques (SPEAKER_00, etc.)
            detected_labels = annotation.labels()
            for label in detected_labels:
                # Pour l'instant on simplifie : on récupère l'embedding du premier segment du speaker
                # (Une version plus poussée extrairait le segment le plus long)
                # On utilise le modèle d'identification ici
                from pyannote.audio import Inference
                from core.models import load_embedding_model
                from pyannote.core import Segment
                
                emb_model = load_embedding_model()
                
                # On prend le premier segment assez long (> 2s) pour identifier
                track_segment = None
                for segment, _, l in annotation.itertracks(yield_label=True):
                    if l == label and segment.duration > 2.0:
                        track_segment = segment
                        break
                
                if track_segment:
                    unknown_emb = emb_model.crop(wav_filename, track_segment)
                    name, score = identify_speaker(unknown_emb, bank_embeddings)
                    speaker_mapping[label] = name
                    print(f"      ✨ {label} identifié comme : {name} (Score: {score:.2f})")
                else:
                    speaker_mapping[label] = label
        
        release_models() # On libère la VRAM après WeSpeaker
        
        # ═══════════════════════════════════════════════════════════
        # 4. TRANSCRIPTION
        # ═══════════════════════════════════════════════════════════
        print("✍️ [3/4] Transcription Whisper...")
        segments = run_transcription(wav_filename)
        release_models() # On libère la VRAM après Whisper
        
        # ═══════════════════════════════════════════════════════════
        # 5. FUSION & SAUVEGARDE
        # ═══════════════════════════════════════════════════════════
        print("🧩 [4/4] Fusion & Archivage...")
        
        # On fusionne texte et speakers
        final_result = merge_transcription_diarization(segments, annotation)
        
        # On remplace les SPEAKER_XX par les vrais noms trouvés
        for item in final_result:
            if item["speaker"] in speaker_mapping:
                item["speaker"] = speaker_mapping[item["speaker"]]
        
        save_path = save_results(clean_name, annotation, segments, final_result)
        
        duration = time.time() - start_time
        print(f"✅ Terminé en {duration:.2f}s.")
        
        return {
            "metadata": {"filename": file.filename, "duration": duration, "saved_at": save_path},
            "segments": final_result
        }

    except Exception as e:
        print(f"❌ Erreur : {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        cleanup_files(temp_filename, wav_filename)
        release_models()