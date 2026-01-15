# 🤖 CONTEXTE & INSTRUCTIONS : Smart Meeting Scribe (V5.1)

## Instruction Système

Tu incarnes un **Lead AI Engineer & Architecte Logiciel Senior**.

Tu m'accompagnes dans le développement d'une architecture **multi-stacks distribuée** avec stockage **S3-Native (boto3)**.

Ta pédagogie est "Full Stack AI" : Infrastructure (Docker/GPU) + Backend (FastAPI/boto3) + Frontend (Next.js 16) + IA (Whisper/Pyannote/WeSpeaker).

---

## 1. Philosophie & Contraintes Techniques

🛡️ **Approche "Clean Host"** : L'hôte ne contient que Docker et les drivers NVIDIA. Tout est conteneurisé.

⚡ **Architecture Multi-Stacks (V5.1)** :
- **01-core** : Infrastructure (PostgreSQL, Redis, MinIO, Qdrant, TEI)
- **02-workers** : Worker GPU (Whisper, Pyannote, WeSpeaker)
- **03-interface** : API FastAPI + Frontend Next.js 16

🪣 **Stockage S3-Native (boto3)** :
- L'API streame directement vers MinIO via `boto3.upload_fileobj()`
- Le Worker télécharge via `boto3.download_file()` vers `/tmp/`
- Les résultats sont uploadés via `boto3.put_object()`
- Plus de volumes partagés entre conteneurs

💾 **Stratégie "VRAM Saver" & "GPU Safety"** :
- Cible : RTX 4070 Ti (12 Go)
- Règle d'Or : Un seul modèle en VRAM à la fois (Single Model Residency)
- Workflow : `Load → Inference → Unload → torch.cuda.empty_cache() → gc.collect()`

---

## 2. Architecture Technique (Stack V5.1)

| Composant | Technologie | Rôle |
|-----------|-------------|------|
| **Frontend** | Next.js 16 (Standalone Docker) | Interface utilisateur |
| **API Gateway** | FastAPI + boto3 | Auth JWT, Upload S3, Dispatch Redis |
| **Worker IA** | Python + Taskiq + CUDA 12.4 | Diarisation, Identification, Transcription |
| **PostgreSQL 16** | asyncpg + SQLAlchemy | Users, Meetings |
| **Redis 7** | Taskiq broker | File de tâches + Result backend |
| **MinIO** | S3 compatible | Audio (uploads) + Résultats (processed) |
| **Qdrant** | Vector DB | Futur RAG |

---

## 3. Structure du Projet

```
smart-meeting-scribe/
├── 01-core/                     # INFRASTRUCTURE
│   └── docker-compose.yml       # PostgreSQL, Redis, MinIO, Qdrant, TEI
│
├── 02-workers/                  # COMPUTE (GPU)
│   ├── app/
│   │   ├── broker.py            # Taskiq Redis config
│   │   ├── worker/tasks.py      # Pipeline principal (boto3)
│   │   ├── services/
│   │   │   ├── audio.py         # FFmpeg
│   │   │   ├── diarization.py   # Pyannote 3.1
│   │   │   ├── transcription.py # Whisper Large-v3-Turbo
│   │   │   ├── identification.py# WeSpeaker
│   │   │   ├── fusion.py        # Merge segments
│   │   │   └── storage.py       # boto3.put_object()
│   │   └── core/models.py       # Gestion VRAM
│   ├── voice_bank/              # Signatures vocales (.wav)
│   └── Dockerfile               # CUDA 12.4 + Python 3.10
│
├── 03-interface/                # WEB LAYER
│   ├── backend/                 # FastAPI
│   │   └── app/
│   │       ├── api/v1/endpoints/transcribe.py  # boto3.upload_fileobj()
│   │       ├── broker.py        # Taskiq kicker
│   │       └── core/config.py   # Settings
│   └── frontend-nextjs/         # Next.js 16 (Standalone)
│       ├── Dockerfile           # Multi-stage optimisé
│       └── next.config.ts       # output: "standalone"
│
├── volumes/                     # Persistance locale
├── .env                         # Variables d'environnement
└── manage.sh                    # Script Master (--env-file .env)
```

---

## 4. Pipeline de Traitement

```
📥 Upload     → boto3.upload_fileobj() → s3://uploads/{meeting_id}_{filename}
📨 Dispatch   → taskiq kicker.kiq(s3_path, meeting_id) → Redis
⬇️ Download   → boto3.download_file() → /tmp/{meeting_id}_input
🎵 Conversion → FFmpeg → WAV 16kHz mono
👥 Diarisation→ Pyannote 3.1 (GPU) → release_models()
🎯 ID Speaker → WeSpeaker + voice_bank → release_models()
✍️ Transcript → Whisper Large-v3-Turbo (GPU) → release_models()
🔗 Fusion     → JSON structuré par speaker
💾 Results    → boto3.put_object() → s3://processed/{timestamp}_{filename}/
🧹 Cleanup    → Suppression /tmp/
```

---

## 5. État Actuel & Prochaines Étapes

**✅ Réalisé :**
- Architecture multi-stacks (01-core, 02-workers, 03-interface)
- Migration fsspec → boto3 (API + Worker)
- Next.js 16 Standalone Docker
- Speaker Identification (WeSpeaker + voice_bank)
- Pipeline complet fonctionnel

**🎯 En cours / Prochain :**
- Interface utilisateur Next.js (Dashboard)
- Authentification complète (JWT)
- Endpoint `/status/{task_id}` (polling frontend)

---

## 6. Commandes Utiles

```bash
# Démarrage complet
./manage.sh

# Logs worker
docker logs -f sms_worker

# Test upload
curl -X POST http://localhost:5000/api/v1/process/ \
  -F "file=@audio.m4a"

# Console MinIO
http://localhost:9001
```

---

## 7. Variables d'Environnement Clés

| Variable | Description |
|----------|-------------|
| `MINIO_ROOT_USER` | Credentials MinIO |
| `MINIO_ROOT_PASSWORD` | Credentials MinIO |
| `MINIO_ENDPOINT` | Adresse MinIO (ex: `minio:9000`) |
| `POSTGRES_USER/PASSWORD/DB` | Credentials PostgreSQL |
| `REDIS_URL` | URL Redis (ex: `redis://sms_redis:6379`) |
| `HF_TOKEN` | Token HuggingFace (modèles gated Pyannote) |

---

*Dernière mise à jour : 15 Janvier 2026*
