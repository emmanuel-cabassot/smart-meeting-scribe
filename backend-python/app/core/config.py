import os
import torch

class Settings:
    PROJECT_NAME: str = "Smart Meeting Scribe V3"
    VERSION: str = "3.1.0"
    
    # --- Infrastructure ---
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379")
    STORAGE_PATH: str = os.getenv("STORAGE_PATH", "/data")
    HF_TOKEN: str = os.getenv("HF_TOKEN", "")

    # --- IA & GPU (Les variables manquantes) ---
    # Détection automatique : 'cuda' si GPU disponible, sinon 'cpu'
    DEVICE: str = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Type de calcul : float16 est idéal pour les RTX (gain de vitesse/VRAM)
    # On utilise int8_float16 si on veut encore plus d'économie
    COMPUTE_TYPE: str = "float16" if torch.cuda.is_available() else "int8"

settings = Settings()

# Export des variables pour la compatibilité avec tes anciens services
DEVICE = settings.DEVICE
COMPUTE_TYPE = settings.COMPUTE_TYPE
HF_TOKEN = settings.HF_TOKEN