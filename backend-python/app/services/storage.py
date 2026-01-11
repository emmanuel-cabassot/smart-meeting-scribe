"""
Service de Stockage Abstrait (V3.1).
Utilise fsspec pour gérer les fichiers de manière agnostique (Local, S3, MinIO).
"""
import fsspec
import json
import os
from datetime import datetime
from app.core.config import settings

class StorageService:
    def __init__(self):
        # On initialise le système de fichiers
        # auto_mkdir=True : Crée les dossiers parents automatiquement (indispensable en local)
        self.fs = fsspec.filesystem("file", auto_mkdir=True)
        
        # Point de montage racine (défini dans docker-compose: /data)
        self.base_path = settings.STORAGE_PATH

    def _get_full_path(self, relative_path: str) -> str:
        """Transforme 'uploads/file.wav' en '/data/uploads/file.wav'."""
        return os.path.join(self.base_path, relative_path)

    def save_upload(self, file_obj, filename: str) -> str:
        """
        Sauvegarde un fichier uploadé par l'API.
        Retourne : Le chemin relatif (ex: 'uploads/uuid-meeting.wav')
        """
        relative_path = f"uploads/{filename}"
        full_path = self._get_full_path(relative_path)
        
        # Écriture en mode binaire (wb) via fsspec
        with self.fs.open(full_path, "wb") as f:
            f.write(file_obj.file.read())
            
        print(f"   💾 [Storage] Fichier sauvegardé : {full_path}")
        return relative_path

    def save_results(self, meeting_id: str, clean_name: str, data_dict: dict):
        """
        Sauvegarde les résultats JSON finaux (Transcription, Diarisation, Fusion).
        Crée une structure : /data/results/YYYYMMDD/meeting_id/
        """
        # 1. Structure du dossier : results/20260111/uuid-meeting/
        date_str = datetime.now().strftime("%Y%m%d")
        folder_rel = f"results/{date_str}/{meeting_id}"
        
        # 2. Sauvegarde des 3 fichiers clés
        paths = {}
        for key, content in data_dict.items():
            # key vaut 'transcription', 'diarization' ou 'fusion'
            filename = f"{key}.json"
            rel_path = f"{folder_rel}/{filename}"
            full_path = self._get_full_path(rel_path)
            
            with self.fs.open(full_path, "w", encoding="utf-8") as f:
                json.dump(content, f, ensure_ascii=False, indent=2)
            
            paths[key] = rel_path

        print(f"   💾 [Storage] Résultats sauvegardés pour {meeting_id}")
        return paths

    def read_file(self, relative_path: str) -> bytes:
        """Lit un fichier binaire depuis le stockage (pour le Worker)."""
        full_path = self._get_full_path(relative_path)
        with self.fs.open(full_path, "rb") as f:
            return f.read()

# Singleton : On instancie le service une seule fois pour l'utiliser partout
storage = StorageService()