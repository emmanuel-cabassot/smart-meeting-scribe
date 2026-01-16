# 🏗️ Core Infrastructure

Services d'infrastructure partagés pour Smart Meeting Scribe.

## 📦 Services

| Service | Image | Port | Usage |
|---------|-------|------|-------|
| **PostgreSQL** | `postgres:15-alpine` | `5432` | Base de données relationnelle |
| **Redis** | `redis:7-alpine` | - | Broker TaskIQ (queue de tâches) |
| **MinIO** | `minio/minio:latest` | `9000`, `9001` | Stockage S3 (fichiers, résultats) |
| **Qdrant** | `qdrant/qdrant:v1.7.4` | `6333` | Base vectorielle (embeddings) |
| **TEI** | `text-embeddings-inference:cpu` | `8081` | API embeddings texte |

## 🚀 Démarrage

```bash
# Depuis la racine du projet
cd 01-core
docker compose up -d
```

## 🌐 Interfaces Web

| Service | URL |
|---------|-----|
| MinIO Console | http://localhost:9001 |
| Qdrant Dashboard | http://localhost:6333/dashboard |

## 📊 Buckets MinIO

| Bucket | Contenu |
|--------|---------|
| `uploads` | Fichiers audio/vidéo entrants |
| `processed` | Résultats JSON (transcription, fusion) |
| `identity-bank` | Signatures vocales pour identification |

## 💾 Volumes

Les données sont persistées dans `../volumes/` :
- `postgres_data/`
- `redis_data/`
- `minio_data/`
- `qdrant_storage/`
- `huggingface_cache/`

## ⚙️ Configuration

Variables dans `.env` :
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD`
- `TEI_EMBEDDING_MODEL`

## 🔗 Réseau

Tous les services partagent le réseau `sms_network` (bridge).
