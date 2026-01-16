# 🏗️ Core Infrastructure

Services d'infrastructure partagés pour Smart Meeting Scribe.

## 📦 Services

| Service | Image | Port | Usage |
|---------|-------|------|-------|
| **PostgreSQL** | `postgres:16-alpine` | `5432` | Base de données relationnelle (Users, Meetings, Services, Projects) |
| **Redis** | `redis:7-alpine` | `6379` | Broker TaskIQ (queue de tâches) |
| **MinIO** | `minio/minio:latest` | `9000`, `9001` | Stockage S3 (fichiers, résultats, identity-bank) |
| **Qdrant** | `qdrant/qdrant:v1.7.4` | `6333` | Base vectorielle (embeddings pour RAG futur) |
| **TEI** | `text-embeddings-inference:cpu` | `8081` | API embeddings texte |

## 🚀 Démarrage

```bash
# Depuis la racine du projet
cd 01-core
docker compose up -d

# Vérifier les services
docker compose ps
```

## 🌐 Interfaces Web

| Service | URL | Credentials |
|---------|-----|-------------|
| MinIO Console | http://localhost:9001 | Voir `.env` |
| Qdrant Dashboard | http://localhost:6333/dashboard | - |

## 📊 Buckets MinIO

| Bucket | Contenu |
|--------|---------|
| `uploads` | Fichiers audio/vidéo entrants |
| `processed` | Résultats JSON (transcription, fusion) |
| `identity-bank` | Signatures vocales/faciales pour identification |

## 🗄️ Tables PostgreSQL

| Table | Description |
|-------|-------------|
| `user` | Utilisateurs (email, password, service_id) |
| `meeting` | Réunions (s3_path, status, transcription) |
| `service` | Départements (R&D, Sales, Marketing...) |
| `project` | Projets transversaux |
| `user_project_link` | Relation N:N User ↔ Project |
| `meeting_project_link` | Relation N:N Meeting ↔ Project |

## 💾 Volumes

Les données sont persistées dans `../volumes/` :

| Volume | Contenu |
|--------|---------|
| `postgres_data/` | Base de données SQL |
| `redis_data/` | Cache et queues Redis |
| `minio_data/` | Stockage objet S3 |
| `qdrant_storage/` | Index vectoriels |
| `huggingface_cache/` | Modèles IA pré-téléchargés |

## ⚙️ Configuration

Variables dans `.env` (à la racine du projet) :

```bash
# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=app

# MinIO
MINIO_ROOT_USER=admin
MINIO_ROOT_PASSWORD=your_minio_password

# TEI
TEI_EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
```

## 🔗 Réseau

Tous les services partagent le réseau Docker `sms_network` (bridge).

Les autres stacks (02-workers, 03-interface) se connectent à ce réseau pour communiquer avec l'infrastructure.

```yaml
networks:
  sms_network:
    driver: bridge
```

## 🩺 Health Checks

```bash
# PostgreSQL
docker exec sms_postgres pg_isready -U postgres

# Redis
docker exec sms_redis redis-cli ping

# MinIO
curl http://localhost:9000/minio/health/live
```
