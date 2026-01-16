"""
Base utilities for worker tasks.

Contient les fonctions partagées entre toutes les tâches:
- Client S3/MinIO
- Téléchargement/Upload de fichiers
- Nettoyage des fichiers temporaires
"""

import logging
import os
import boto3
from urllib.parse import urlparse
from pathlib import Path
from typing import List, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


# =============================================================================
# CLIENT S3 (MinIO)
# =============================================================================

def get_s3_client():
    """
    Crée un client S3 boto3 configuré pour MinIO.
    
    Returns:
        boto3.client: Client S3 configuré
    """
    return boto3.client(
        "s3",
        endpoint_url=f"http://{settings.MINIO_ENDPOINT}",
        aws_access_key_id=settings.MINIO_ACCESS_KEY,
        aws_secret_access_key=settings.MINIO_SECRET_KEY
    )


# =============================================================================
# TÉLÉCHARGEMENT / UPLOAD
# =============================================================================

def smart_download(remote_path: str, local_dest: str) -> None:
    """
    Télécharge un fichier depuis S3 via Boto3.
    Gère les URL s3://bucket/key
    
    Args:
        remote_path: Chemin S3 (s3://bucket/key) ou chemin local
        local_dest: Destination locale
    """
    if remote_path.startswith("s3://"):
        logger.info(f"⬇️ [Boto3] Téléchargement de {remote_path}...")
        
        parsed = urlparse(remote_path)
        bucket_name = parsed.netloc
        object_key = parsed.path.lstrip('/')
        
        s3 = get_s3_client()
        s3.download_file(bucket_name, object_key, local_dest)
        
        logger.info(f"   ✅ Téléchargé vers {local_dest}")
    else:
        # Fallback pour tests locaux
        import shutil
        shutil.copy(remote_path, local_dest)


def smart_upload(local_path: str, bucket: str, object_key: str) -> str:
    """
    Upload un fichier vers S3/MinIO.
    
    Args:
        local_path: Chemin du fichier local
        bucket: Nom du bucket S3
        object_key: Clé de l'objet dans le bucket
        
    Returns:
        str: URL S3 du fichier uploadé (s3://bucket/key)
    """
    logger.info(f"⬆️ [Boto3] Upload de {local_path} vers s3://{bucket}/{object_key}...")
    
    s3 = get_s3_client()
    s3.upload_file(local_path, bucket, object_key)
    
    s3_url = f"s3://{bucket}/{object_key}"
    logger.info(f"   ✅ Uploadé vers {s3_url}")
    return s3_url


# =============================================================================
# NETTOYAGE
# =============================================================================

def cleanup_files(files: List[Optional[str]], job_id: str = "") -> None:
    """
    Supprime une liste de fichiers temporaires.
    
    Args:
        files: Liste de chemins de fichiers à supprimer (peut contenir None)
        job_id: ID du job pour les logs
    """
    prefix = f"[JOB {job_id}] " if job_id else ""
    
    for f in files:
        if f and os.path.exists(f):
            try:
                os.remove(f)
                logger.info(f"   🧹 {prefix}Supprimé : {f}")
            except Exception as clean_err:
                logger.warning(f"   ⚠️ {prefix}Impossible de supprimer {f}: {clean_err}")


def get_temp_path(meeting_id: str, filename: str, suffix: str = "") -> str:
    """
    Génère un chemin temporaire unique pour un fichier.
    
    Args:
        meeting_id: ID de la réunion
        filename: Nom du fichier
        suffix: Suffixe optionnel (ex: "_speaker_00")
        
    Returns:
        str: Chemin temporaire
    """
    base_name = Path(filename).stem
    extension = Path(filename).suffix
    return f"/tmp/{meeting_id}_{base_name}{suffix}{extension}"
