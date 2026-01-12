import os
import torch

class Settings:
    PROJECT_NAME: str = "Smart Meeting Scribe Worker V5"
    
    # --- Infrastructure (Redis & MinIO) ---
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379")
    
    # Configuration MinIO (S3)
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "minio:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ROOT_USER", "admin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_ROOT_PASSWORD", "minio_admin_password")
    MINIO_BUCKET_AUDIO: str = "uploads"
    MINIO_BUCKET_RESULTS: str = "processed"
    
    # URL S3 complète pour fsspec (ex: s3://uploads)
    # Important : On force l'utilisation de s3fs
    STORAGE_PROTOCOL: str = "s3"
    
    # --- IA HuggingFace ---
    HF_TOKEN: str = os.getenv("HF_TOKEN", "")

    # --- Hardware (GPU/CPU) ---
    DEVICE: str = "cuda" if torch.cuda.is_available() else "cpu"
    COMPUTE_TYPE: str = "float16" if torch.cuda.is_available() else "int8"

settings = Settings()

# Exports pour compatibilité avec ton code existant
DEVICE = settings.DEVICE
COMPUTE_TYPE = settings.COMPUTE_TYPE
HF_TOKEN = settings.HF_TOKEN