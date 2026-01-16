#!/usr/bin/env python3
"""
Script de migration : voice_bank -> identity-bank (S3/MinIO)
Exécuter depuis le container API ou worker qui a accès à MinIO.
"""
import boto3
import json
import os
from datetime import datetime

# Configuration MinIO
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")

BUCKET_NAME = "identity-bank"
USER_ID = "default"

# Mapping des fichiers existants
VOICE_FILES = {
    "homme": "/code/voice_bank/Homme.wav",
    "femme": "/code/voice_bank/Femme.wav",
}

def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=f"http://{MINIO_ENDPOINT}",
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY
    )

def create_bucket(s3):
    """Crée le bucket identity-bank s'il n'existe pas."""
    try:
        s3.create_bucket(Bucket=BUCKET_NAME)
        print(f"✅ Bucket '{BUCKET_NAME}' créé")
    except s3.exceptions.BucketAlreadyOwnedByYou:
        print(f"ℹ️ Bucket '{BUCKET_NAME}' existe déjà")
    except Exception as e:
        if "BucketAlreadyOwnedByYou" in str(e) or "BucketAlreadyExists" in str(e):
            print(f"ℹ️ Bucket '{BUCKET_NAME}' existe déjà")
        else:
            raise

def upload_voice_samples(s3):
    """Upload les échantillons vocaux vers S3."""
    for person_id, local_path in VOICE_FILES.items():
        if not os.path.exists(local_path):
            print(f"⚠️ Fichier non trouvé : {local_path}")
            continue
        
        # Structure: identity-bank/default/homme/voice/sample.wav
        s3_key = f"{USER_ID}/{person_id}/voice/sample.wav"
        
        print(f"📤 Upload : {local_path} -> s3://{BUCKET_NAME}/{s3_key}")
        s3.upload_file(local_path, BUCKET_NAME, s3_key)
        
        # Créer aussi le profile.json
        profile = {
            "name": person_id.capitalize(),
            "created_at": datetime.utcnow().isoformat(),
            "type": "voice"
        }
        profile_key = f"{USER_ID}/{person_id}/profile.json"
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=profile_key,
            Body=json.dumps(profile, indent=2),
            ContentType="application/json"
        )
        print(f"📄 Profile créé : s3://{BUCKET_NAME}/{profile_key}")

def main():
    print("🚀 Migration voice_bank -> identity-bank")
    print(f"   Endpoint: {MINIO_ENDPOINT}")
    print(f"   Bucket: {BUCKET_NAME}")
    print(f"   User ID: {USER_ID}")
    print()
    
    s3 = get_s3_client()
    create_bucket(s3)
    upload_voice_samples(s3)
    
    print()
    print("✅ Migration terminée !")

if __name__ == "__main__":
    main()
