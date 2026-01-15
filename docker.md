# 🐳 Docker Cheat Sheet — Smart Meeting Scribe V5.1

## 🏗️ Architecture Multi-Stacks

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          RÉSEAU : sms_network                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────── 01-core ───────────────┐                                  │
│  │                                       │                                  │
│  │  📦 sms_postgres   (5432)             │                                  │
│  │  📦 sms_redis                         │                                  │
│  │  📦 sms_minio      (9000, 9001)       │                                  │
│  │  📦 sms_qdrant     (6333)             │                                  │
│  │  📦 sms_tei        (8081)             │                                  │
│  │                                       │                                  │
│  └───────────────────────────────────────┘                                  │
│                                                                             │
│  ┌─────────────── 02-workers ────────────┐                                  │
│  │                                       │                                  │
│  │  📦 sms_worker     (GPU - CUDA 12.4)  │                                  │
│  │     ├─ Pyannote (Diarisation)         │                                  │
│  │     ├─ WeSpeaker (Identification)     │                                  │
│  │     └─ Whisper (Transcription)        │                                  │
│  │                                       │                                  │
│  └───────────────────────────────────────┘                                  │
│                                                                             │
│  ┌─────────────── 03-interface ──────────┐                                  │
│  │                                       │                                  │
│  │  📦 sms_api        (5000 → 8000)      │                                  │
│  │     └─ FastAPI + boto3                │                                  │
│  │                                       │                                  │
│  │  📦 sms_frontend   (3000)             │                                  │
│  │     └─ Next.js 16 (Standalone)        │                                  │
│  │                                       │                                  │
│  └───────────────────────────────────────┘                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📦 Containers & Services

| Stack | Container | Image | Ports | Rôle |
|-------|-----------|-------|-------|------|
| **01-core** | `sms_postgres` | postgres:15-alpine | 5432 | Base de données SQL |
| | `sms_redis` | redis:7-alpine | 6379 | Broker de tâches (Taskiq) |
| | `sms_minio` | minio/minio:latest | 9000, 9001 | Stockage S3 (audio + résultats) |
| | `sms_qdrant` | qdrant/qdrant:v1.7.4 | 6333 | Vector DB (futur RAG) |
| | `sms_tei` | text-embeddings-inference | 8081 | Embeddings CPU |
| **02-workers** | `sms_worker` | smart-meeting-scribe-worker:v5 | - | Pipeline IA (GPU) |
| **03-interface** | `sms_api` | smart-meeting-scribe-api:v5 | 5000 | API Gateway (FastAPI) |
| | `sms_frontend` | sms-interface-frontend | 3000 | UI (Next.js 16) |

---

## 🚀 Commande Master

```bash
./manage.sh
```

Ce script :
1. 🧹 Nettoie les containers et volumes
2. 🚀 Lance 01-core → 02-workers → 03-interface
3. 📋 Affiche les logs de l'API

---

## 🟢 Démarrage Manuel (par stack)

```bash
# Infrastructure
docker compose -f 01-core/docker-compose.yml up -d

# Worker GPU
docker compose -f 02-workers/docker-compose.yml up -d

# Interface (avec rebuild)
docker compose -f 03-interface/docker-compose.yml up -d --build
```

---

## 🟡 Arrêt & Nettoyage

```bash
# Arrêter une stack
docker compose -f 03-interface/docker-compose.yml down

# Arrêt total + suppression volumes
docker compose -f 03-interface/docker-compose.yml down -v

# Reset complet (images incluses)
docker compose -f 03-interface/docker-compose.yml down -v --rmi local
```

---

## 📋 Logs

```bash
# API Gateway
docker logs -f sms_api

# Worker IA (transcription)
docker logs -f sms_worker

# Frontend Next.js
docker logs -f sms_frontend

# Tous les logs MinIO
docker logs -f sms_minio
```

---

## 🔧 Shell & Debug

```bash
# Entrer dans un container
docker exec -it sms_api /bin/bash
docker exec -it sms_worker /bin/bash

# Vérifier le GPU
docker exec -it sms_worker nvidia-smi

# Vérifier Redis
docker exec -it sms_redis redis-cli ping
```

---

## 📊 Inspection

```bash
# Containers actifs
docker ps

# Tous les containers
docker ps -a

# Images
docker images

# Ressources (CPU/RAM/GPU)
docker stats

# Réseaux
docker network ls
```

---

## 🧹 Maintenance

```bash
# Nettoyer orphelins
docker system prune -f

# Nettoyage total (⚠️ supprime tout)
docker system prune -a --volumes
```

---

## 🌐 URLs d'accès

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| API Docs (Swagger) | http://localhost:5000/docs |
| MinIO Console | http://localhost:9001 |
| Qdrant Dashboard | http://localhost:6333/dashboard |

---

## 📁 Volumes Persistants

| Volume | Chemin | Contenu |
|--------|--------|---------|
| `postgres_data` | `./volumes/postgres_data` | Tables SQL |
| `redis_data` | `./volumes/redis_data` | Cache Redis |
| `minio_data` | `./volumes/minio_data` | Fichiers S3 |
| `qdrant_storage` | `./volumes/qdrant_storage` | Vecteurs |
| `huggingface_cache` | `./volumes/huggingface_cache` | Modèles IA |

---

## ⚙️ Variables d'Environnement

Chaque stack a son propre `.env` :

```
01-core/.env
02-workers/.env
03-interface/.env
```

Variables clés :
- `MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD`
- `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB`
- `HF_TOKEN` (HuggingFace pour Pyannote)
- `REDIS_URL`

---

*Dernière mise à jour : 16 Janvier 2026*
