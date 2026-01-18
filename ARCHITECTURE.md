# 🏗️ Architecture Technique : Smart Meeting Scribe V6.0

> **Version** : 6.0 (Stack "Groups Unified Model")  
> **Approche** : "Micro-services", "Cloud Native" & "GPU Optimized"  
> **Cible** : Déploiement multi-conteneurs sur GPU unique (Consumer Grade - ex: RTX 4070 Ti)

Ce document sert de référence pour comprendre les choix technologiques, la gestion des flux de données et la stratégie de persistance.

---

## 1. Vue d'Ensemble & Philosophie

La V6.0 introduit un **modèle de Groupes Unifié** inspiré d'Azure AD pour simplifier la gestion des droits d'accès. Elle remplace le système matriciel Services/Projets par une approche plus flexible basée sur des groupes typés.

### Les 4 Piliers de l'Architecture V6.0

| Pilier | Description |
|--------|-------------|
| **Clean Architecture** | Backend structuré en couches (Endpoints → Services → Models). BFF sécurisé par JWT. |
| **Boto3 Streaming** | Upload/Download S3 unifié via `boto3`. Pas de stockage intermédiaire sur disque. |
| **Groups Model** | Système de groupes typés (Department, Project, Recurring) pour une gestion flexible des droits. |
| **GPU Safety** | Single Model Residency + Garbage Collection VRAM systématique. |

---

## 2. La Stack Technologique

### 🌐 Couche Interface

| Composant | Technologie | Notes |
|-----------|-------------|-------|
| **Frontend** | Next.js 16 (Standalone) | Image Docker optimisée (~100MB) |
| **API Gateway** | FastAPI + boto3 | Streaming direct vers MinIO |

### ⚡ Couche Communication

| Composant | Rôle | Technologie |
|-----------|------|-------------|
| **Taskiq** | Orchestrateur async API ↔ Worker | Python native |
| **Redis 7** | Broker de messages + Result Backend | Mode AOF |

### 🧠 Couche Intelligence (Worker GPU)

| Modèle | Fonction | Version |
|--------|----------|---------|
| **Faster-Whisper** | Transcription audio → texte | Large-v3-Turbo (CTranslate2) |
| **Pyannote 3.1** | Diarisation ("Qui parle ?") | speaker-diarization-3.1 |
| **WeSpeaker** | Identification biométrique | ResNet34-LM |

### 💾 Couche Données

| Composant | Rôle | Accès |
|-----------|------|-------|
| **PostgreSQL 16** | Users, Meetings, Groups | asyncpg (SQLAlchemy) |
| **MinIO** | Audio (uploads) + Résultats (processed) | boto3 (S3 API) |
| **Qdrant** | Vecteurs (futur RAG) | REST API |
| **TEI** | Embeddings CPU | HuggingFace TGI |

---

## 3. Modèle de Données (Groups)

### Tables PostgreSQL

```sql
-- Utilisateurs
CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE
);

-- Groupes (NEW en V6.0)
CREATE TABLE "group" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(500),
    type VARCHAR(20) NOT NULL,  -- 'department', 'project', 'recurring'
    is_active BOOLEAN DEFAULT TRUE
);

-- Meetings
CREATE TABLE meeting (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    original_filename VARCHAR(500) NOT NULL,
    s3_path VARCHAR(1000) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    transcription_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    owner_id INTEGER REFERENCES "user"(id)
);

-- Relations Many-to-Many
CREATE TABLE user_group_link (
    user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE,
    group_id INTEGER REFERENCES "group"(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, group_id)
);

CREATE TABLE meeting_group_link (
    meeting_id INTEGER REFERENCES meeting(id) ON DELETE CASCADE,
    group_id INTEGER REFERENCES "group"(id) ON DELETE CASCADE,
    PRIMARY KEY (meeting_id, group_id)
);
```

### Types de Groupes

| Type | Description | Exemples |
|------|-------------|----------|
| `department` | Structure organisationnelle | R&D, Marketing, Direction, RH |
| `project` | Projets transversaux | Lancement V5, Audit Sécurité |
| `recurring` | Réunions récurrentes | COMOP, Daily, Café AGAM |

### Règle de Visibilité

Un utilisateur voit un meeting si :
- Il partage **au moins 1 groupe** avec le meeting
- **OU** il est le **owner** du meeting

---

## 4. Flux de Données (Workflow boto3)

```mermaid
sequenceDiagram
    participant User as 👤 Frontend (Next.js 16)
    participant API as ⚡ FastAPI
    participant S3 as 🪣 MinIO
    participant Redis as 📮 Redis
    participant Worker as 🧠 Worker GPU

    User->>API: POST /process (Audio + JWT + group_ids)
    API->>S3: boto3.upload_fileobj() → s3://uploads/
    API->>Redis: kicker.kiq(s3_path, meeting_id)
    API-->>User: 202 { task_id, meeting_id }
    
    Note over Worker: Listening Redis...
    
    Redis->>Worker: Pull task
    Worker->>S3: boto3.download_file() → /tmp/
    
    Note over Worker: 🎵 FFmpeg → WAV
    Note over Worker: 👥 Pyannote (Diarisation)
    Note over Worker: 🎯 WeSpeaker (Identification)
    Note over Worker: ✍️ Whisper (Transcription)
    Note over Worker: 🔗 Fusion JSON
    
    Worker->>S3: boto3.put_object() → s3://processed/
    Worker->>Worker: 🧹 Cleanup /tmp/
    Worker->>Redis: Task Success
```

---

## 5. Communication S3 (boto3)

### API Gateway (`transcribe.py`)

```python
# Upload streaming (pas de fichier local)
s3_client.upload_fileobj(
    file.file,                    # Stream HTTP entrant
    settings.MINIO_BUCKET_AUDIO,  # "uploads"
    object_name,
    ExtraArgs={"ContentType": file.content_type}
)
```

### Worker (`tasks.py`)

```python
# Download vers /tmp pour traitement GPU
s3.download_file(bucket_name, object_key, local_dest)
```

### Storage (`storage.py`)

```python
# Upload résultats JSON
s3.put_object(
    Bucket=settings.MINIO_BUCKET_RESULTS,  # "processed"
    Key=object_key,
    Body=json.dumps(data).encode('utf-8'),
    ContentType='application/json'
)
```

---

## 6. Stratégie GPU & VRAM

### Protocole Single Model Residency

| Phase | Modèle chargé | VRAM utilisée |
|-------|---------------|---------------|
| Diarisation | Pyannote 3.1 | ~1 GB |
| Identification | WeSpeaker (+ Pyannote) | ~2.6 GB |
| Transcription | Whisper Large-v3-Turbo | ~3.1 GB |

### Garbage Collection

```python
# Après chaque phase GPU
def release_models():
    for model in loaded_models.values():
        del model
    loaded_models.clear()
    gc.collect()
    torch.cuda.empty_cache()
```

---

## 7. Structure du Projet

```
smart-meeting-scribe/
├── 01-core/                     # INFRASTRUCTURE
│   └── docker-compose.yml       # PostgreSQL, Redis, MinIO, Qdrant, TEI
│
├── 02-workers/                  # COMPUTE (GPU)
│   ├── app/
│   │   ├── worker/tasks.py      # Pipeline principal (boto3)
│   │   ├── services/
│   │   │   ├── audio.py         # FFmpeg conversion
│   │   │   ├── diarization.py   # Pyannote
│   │   │   ├── transcription.py # Whisper
│   │   │   ├── identification.py# WeSpeaker
│   │   │   ├── fusion.py        # Merge segments
│   │   │   └── storage.py       # boto3 upload
│   │   └── core/models.py       # Gestion VRAM
│   ├── voice_bank/              # Signatures vocales
│   └── Dockerfile               # CUDA 12.4
│
├── 03-interface/                # WEB LAYER
│   ├── backend/                 # FastAPI
│   │   └── app/
│   │       ├── api/v1/          # Routes (auth, process, groups)
│   │       ├── models/          # User, Meeting, Group
│   │       ├── broker.py        # Taskiq Redis
│   │       └── core/config.py   # Settings boto3
│   └── frontend-nextjs/         # Next.js 16 (Standalone)
│
├── volumes/                     # Persistance
├── .env                         # Configuration
└── manage.sh                    # 🛠️ Script Master
```

---

## 8. Endpoints API

### Authentification

| Méthode | Route | Description |
|---------|-------|-------------|
| `POST` | `/api/v1/auth/register` | Inscription utilisateur |
| `POST` | `/api/v1/auth/login` | Connexion (retourne JWT) |

### Users

| Méthode | Route | Description |
|---------|-------|-------------|
| `GET` | `/api/v1/users/me` | Profil avec groupes |

### Process

| Méthode | Route | Description |
|---------|-------|-------------|
| `POST` | `/api/v1/process/` | Upload audio + group_ids → dispatch task |
| `GET` | `/api/v1/process/status/{task_id}` | Statut de la transcription |

### Meetings

| Méthode | Route | Description |
|---------|-------|-------------|
| `GET` | `/api/v1/meetings/` | Liste meetings (avec filtres group_id, status) |
| `GET` | `/api/v1/meetings/{id}` | Détail d'un meeting |

### Groups

| Méthode | Route | Description |
|---------|-------|-------------|
| `GET` | `/api/v1/groups/` | Liste tous les groupes |
| `POST` | `/api/v1/groups/` | Créer un groupe (Admin) |

---

## 9. Variables d'Environnement

| Variable | Description |
|----------|-------------|
| `MINIO_ROOT_USER` | Credentials MinIO |
| `MINIO_ROOT_PASSWORD` | Credentials MinIO |
| `MINIO_ENDPOINT` | Adresse MinIO (ex: `minio:9000`) |
| `POSTGRES_USER/PASSWORD/DB` | Credentials PostgreSQL |
| `REDIS_URL` | URL Redis (ex: `redis://sms_redis:6379`) |
| `HF_TOKEN` | Token HuggingFace (modèles gated) |

---

## 10. Évolutions (Roadmap)

- [x] Migration fsspec → boto3
- [x] Next.js 16 Standalone Docker
- [x] Speaker Identification (WeSpeaker)
- [x] **Modèle Groups Unifié (Department, Project, Recurring)**
- [x] **Script manage.sh pour gestion simplifiée**
- [ ] Dashboard utilisateur (Next.js)
- [ ] Gestion des erreurs et retry
- [ ] RAG Integration (Qdrant + LLM)
- [ ] Export Word/PDF
- [ ] Multi-Tenant isolation

---

> **Dernière mise à jour** : 17 Janvier 2026
