import json
import fsspec
from datetime import datetime
from app.core.config import settings

def save_results(clean_name, annotation, raw_segments, fusion_segments):
    """
    Sauvegarde les résultats (JSON) sur MinIO (S3) via fsspec.
    Plus de disque dur local !
    
    Structure S3 : s3://processed/YYYYMMDD_HHMMSS_nomdufichier/
    """
    
    # 1. Construction du chemin S3 unique (Timestamp)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = clean_name.split('.')[0] # On enlève l'extension .wav/.mp3
    folder_name = f"{timestamp}_{safe_filename}"
    
    # Chemin de base : s3://processed/20260112_...
    base_path = f"{settings.STORAGE_PROTOCOL}://{settings.MINIO_BUCKET_RESULTS}/{folder_name}"

    # 2. Configuration de la connexion S3 (MinIO)
    # On passe les credentials définis dans config.py
    storage_options = {
        "endpoint_url": f"http://{settings.MINIO_ENDPOINT}",
        "key": settings.MINIO_ACCESS_KEY,
        "secret": settings.MINIO_SECRET_KEY
    }

    # 3. Préparation des données (Logique Métier inchangée V3)
    diarization_data = []
    if hasattr(annotation, 'itertracks'):
        for turn, _, speaker in annotation.itertracks(yield_label=True):
            diarization_data.append({
                "start": round(turn.start, 2),
                "end": round(turn.end, 2),
                "speaker": speaker
            })

    transcription_data = [
        {"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()} 
        for s in raw_segments
    ]

    # 4. Fonction utilitaire d'écriture S3
    def write_json_to_s3(filename, data):
        full_path = f"{base_path}/{filename}"
        print(f"   💾 Upload S3 vers : {full_path}")
        
        # La magie fsspec : on ouvre une connexion réseau comme un fichier local
        try:
            with fsspec.open(full_path, "w", encoding="utf-8", **storage_options) as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"   ❌ Erreur écriture S3 ({filename}): {str(e)}")
            raise e

    # 5. Exécution des sauvegardes
    write_json_to_s3("diarization.json", diarization_data)
    write_json_to_s3("transcription.json", transcription_data)
    write_json_to_s3("fusion.json", fusion_segments)
    
    # On retourne le chemin S3 pour que le Worker puisse le confirmer
    return base_path