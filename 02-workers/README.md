# 🔧 Workers - TaskIQ Background Processing

Service de traitement asynchrone des tâches audio/vidéo avec GPU.

## 🏗️ Architecture

```
app/
├── broker.py              # Configuration TaskIQ + Redis
├── core/
│   ├── config.py          # Variables d'environnement
│   └── models.py          # Chargement/libération modèles IA
├── services/              # Logique métier IA
│   ├── audio.py           # Conversion audio (FFmpeg)
│   ├── diarization.py     # Pyannote (GPU)
│   ├── transcription.py   # Whisper (GPU)
│   ├── identification.py  # WeSpeaker (GPU) - lit depuis S3
│   ├── fusion.py          # Merge diarization + transcription
│   └── storage.py         # Sauvegarde S3/MinIO
└── worker/
    └── tasks/             # 📁 Tâches TaskIQ modulaires
        ├── __init__.py    # Export central
        ├── base.py        # Utilitaires S3, cleanup
        ├── audio_tasks.py # Tâches audio (transcription)
        └── video_tasks.py # Tâches vidéo (templates)
```

## 🎯 Identity Bank (S3)

Les signatures vocales sont stockées sur MinIO pour l'identification des locuteurs :

```
📁 s3://identity-bank/
   └── {user_id}/                    # "default" pour l'instant
       └── {person_id}/              # Ex: "emmanuel"
           ├── profile.json          # Métadonnées
           ├── voice/sample.wav      # Échantillon vocal
           └── face/                 # (Prévu pour reconnaissance faciale)
```

**Ajouter une nouvelle voix :**
1. Uploader vers `s3://identity-bank/default/{nom}/voice/sample.wav`
2. Créer `profile.json` : `{"name": "Nom", "created_at": "..."}`

## 🚀 Tâches disponibles

| Tâche | Description | Fichier |
|-------|-------------|---------|
| `process_transcription_full` | Pipeline : diarisation → identification → transcription → fusion | `audio_tasks.py` |

## ➕ Ajouter une nouvelle tâche

### 1. Implémenter dans le fichier approprié

```python
# audio_tasks.py ou video_tasks.py
from app.broker import broker
from app.worker.tasks.base import smart_download, cleanup_files

@broker.task(task_name="ma_nouvelle_tache")
async def ma_nouvelle_tache(file_path: str, job_id: str):
    local_file = None
    try:
        local_file = f"/tmp/{job_id}_file.wav"
        smart_download(file_path, local_file)
        # ... traitement
        return {"status": "success", "job_id": job_id}
    finally:
        cleanup_files([local_file], job_id)
```

### 2. Exporter dans `tasks/__init__.py`

```python
from app.worker.tasks.audio_tasks import ma_nouvelle_tache

__all__ = [
    "process_transcription_full",
    "ma_nouvelle_tache",  # ← Ajouter
]
```

### 3. Appeler depuis l'API

```python
from app.worker.tasks import ma_nouvelle_tache

result = await ma_nouvelle_tache.kiq(file_path, job_id)
```

## 🐳 Docker

```bash
# Build
docker build -t smart-scribe-worker .

# Run (nécessite GPU)
docker run --gpus all smart-scribe-worker
```

## ⚙️ Variables d'environnement

| Variable | Description | Défaut |
|----------|-------------|--------|
| `REDIS_URL` | URL du broker Redis | `redis://redis:6379` |
| `MINIO_ENDPOINT` | Endpoint MinIO | `minio:9000` |
| `MINIO_ACCESS_KEY` | Clé d'accès MinIO | - |
| `MINIO_SECRET_KEY` | Clé secrète MinIO | - |
| `HF_TOKEN` | Token HuggingFace (Pyannote) | - |

## 📊 Gestion VRAM

Le worker optimise l'usage GPU en chargeant/déchargeant les modèles séquentiellement :

1. **Pyannote** (diarisation) → libéré
2. **WeSpeaker** (identification) → libéré  
3. **Whisper** (transcription) → libéré

Cela permet de faire tourner tous les modèles sur une GPU avec ~8GB VRAM.

## 📦 Buckets S3/MinIO

| Bucket | Usage |
|--------|-------|
| `uploads` | Fichiers audio/vidéo entrants |
| `processed` | Résultats (JSON transcription, diarisation, fusion) |
| `identity-bank` | Signatures vocales pour identification |
