import os
import json
from datetime import datetime

def save_results(clean_name, annotation, raw_segments, fusion_segments):
    """Sauvegarde les 3 fichiers JSON dans un dossier daté."""
    
    # 1. Création dossier
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"{timestamp}_{clean_name.split('.')[0]}"
    
    # --- 🛠️ FIX DOCKER : CHEMIN ABSOLU ---
    # On force le chemin vers le volume monté dans /code/recordings
    # Cela évite les erreurs si le script est exécuté depuis /code/app
    save_dir = os.path.join("/code/recordings", folder_name)
    # -------------------------------------
    
    os.makedirs(save_dir, exist_ok=True)
    
    # 2. Préparation Diarisation
    diarization_data = []
    if hasattr(annotation, 'itertracks'):
        for turn, _, speaker in annotation.itertracks(yield_label=True):
            diarization_data.append({
                "start": round(turn.start, 2),
                "end": round(turn.end, 2),
                "speaker": speaker
            })

    # 3. Préparation Transcription
    transcription_data = [{"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()} for s in raw_segments]

    # 4. Écriture
    def write_json(name, data):
        with open(os.path.join(save_dir, name), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    write_json("diarization.json", diarization_data)
    write_json("transcription.json", transcription_data)
    write_json("fusion.json", fusion_segments)
    
    return save_dir