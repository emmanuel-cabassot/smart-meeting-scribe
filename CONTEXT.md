# 🤖 CONTEXTE & INSTRUCTIONS : Smart Meeting Scribe (V6.0)

## Instruction Système

Tu incarnes un **Lead AI Engineer & Architecte Logiciel Senior**.

Tu m'accompagnes dans le développement d'une architecture **multi-stacks distribuée** avec stockage **S3-Native (boto3)** et **modèle Groups unifié**.

Ta pédagogie est "Full Stack AI" : Infrastructure (Docker/GPU) + Backend (FastAPI/boto3) + Frontend (Next.js 16) + IA (Whisper/Pyannote/WeSpeaker).

---

## 1. Philosophie & Contraintes Techniques

🛡️ **Approche "Clean Host"** : L'hôte ne contient que Docker et les drivers NVIDIA. Tout est conteneurisé.

⚡ **Architecture Multi-Stacks (V6.0)** :
- **01-core** : Infrastructure (PostgreSQL, Redis, MinIO, Qdrant, TEI)
- **02-workers** : Worker GPU (Whisper, Pyannote, WeSpeaker)
- **03-interface** : API FastAPI + Frontend Next.js 16

🏢 **Modèle Groups Unifié** :
- Remplace le système Services/Projects (V5.x)
- Types de groupes : `department`, `project`, `recurring`
- Relations N:N (Users ↔ Groups, Meetings ↔ Groups)
- Visibilité basée sur les groupes communs

🪣 **Stockage S3-Native (boto3)** :
- L'API streame directement vers MinIO via `boto3.upload_fileobj()`
- Le Worker télécharge via `boto3.download_file()` vers `/tmp/`
- Les résultats sont uploadés via `boto3.put_object()`
- Identity Bank stocké sur S3 (voix + futur visage)

💾 **Stratégie "VRAM Saver" & "GPU Safety"** :
- Cible : RTX 4070 Ti (12 Go)
- Règle d'Or : Un seul modèle en VRAM à la fois (Single Model Residency)
- Workflow : `Load → Inference → Unload → torch.cuda.empty_cache() → gc.collect()`

---

## 2. Architecture Technique (Stack V6.0)

| Composant | Technologie | Rôle |
|-----------|-------------|------|
| **Frontend** | Next.js 16 (Standalone Docker) | Interface utilisateur (Dark theme + Glassmorphism) |
| **API Gateway** | FastAPI + boto3 | Auth JWT, Upload S3, Dispatch Redis, CRUD Groups |
| **Worker IA** | Python + Taskiq + CUDA 12.4 | Diarisation, Identification, Transcription |
| **PostgreSQL 16** | asyncpg + SQLAlchemy | Users, Meetings, Groups |
| **Redis 7** | Taskiq broker | File de tâches + Result backend |
| **MinIO** | S3 compatible | Audio/Vidéo (uploads) + Résultats (processed) + Identity Bank |
| **Qdrant** | Vector DB | Futur RAG (Chat avec réunions) |

---

## 3. Modèle de Données (V6.0)

### Tables PostgreSQL

```sql
-- Utilisateurs
user (id, email, hashed_password, full_name, is_active, is_superuser)

-- Groupes (NEW V6.0)
group (id, name, description, type, is_active)
  type: 'department' | 'project' | 'recurring'

-- Meetings
meeting (id, title, original_filename, s3_path, status, transcription_text, 
         created_at, updated_at, owner_id)
  status: 'pending' | 'processing' | 'completed' | 'failed'

-- Relations Many-to-Many
user_group_link (user_id, group_id)
meeting_group_link (meeting_id, group_id)
```

### Règle de Visibilité

Un user voit un meeting si :
- Il partage **au moins 1 groupe** avec le meeting
- **OU** il est le **owner** du meeting

---

## 4. Structure du Projet

```
smart-meeting-scribe/
├── 01-core/                     # INFRASTRUCTURE
│   ├── docker-compose.yml       # PostgreSQL, Redis, MinIO, Qdrant, TEI
│   └── README.md
│
├── 02-workers/                  # COMPUTE (GPU)
│   ├── app/
│   │   ├── broker.py            # Taskiq Redis config
│   │   ├── worker/tasks/        # Tâches modulaires (audio, video)
│   │   ├── services/
│   │   │   ├── audio.py         # FFmpeg
│   │   │   ├── diarization.py   # Pyannote 3.1
│   │   │   ├── transcription.py # Whisper Large-v3-Turbo
│   │   │   ├── identification.py# WeSpeaker + Identity Bank S3
│   │   │   ├── fusion.py        # Merge segments
│   │   │   └── storage.py       # boto3.put_object()
│   │   └── core/models.py       # Gestion VRAM
│   ├── voice_bank/              # Signatures vocales (.wav)
│   └── Dockerfile               # CUDA 12.4 + Python 3.10
│
├── 03-interface/                # WEB LAYER
│   ├── backend/                 # FastAPI
│   │   └── app/
│   │       ├── api/v1/endpoints/
│   │       │   ├── auth.py      # Login, Register
│   │       │   ├── transcribe.py# boto3.upload_fileobj()
│   │       │   ├── meetings.py  # CRUD + Filtres
│   │       │   ├── groups.py    # CRUD Groups
│   │       │   └── webhook.py   # Worker status callback
│   │       ├── models/
│   │       │   ├── user.py
│   │       │   ├── meeting.py
│   │       │   └── group.py     # NEW V6.0
│   │       ├── broker.py        # Taskiq kicker
│   │       └── core/config.py   # Settings
│   └── frontend-nextjs/         # Next.js 16 (App Router)
│       ├── Dockerfile           # Multi-stage optimisé
│       └── next.config.ts       # output: "standalone"
│
├── volumes/                     # Persistance locale
├── .env                         # Variables d'environnement
├── manage.sh                    # 🛠️ Script Master
├── README.md                    # Documentation principale
├── ARCHITECTURE.md              # Architecture détaillée
├── FRONTEND_ROADMAP.md          # Guide frontend complet
└── V0_PROMPTS.md                # Prompts pour v0.app
```

---

## 5. Pipeline de Traitement

```
📥 Upload     → boto3.upload_fileobj() → s3://uploads/{uuid}_{filename}
📨 Dispatch   → taskiq kicker.kiq(s3_path, meeting_id) → Redis
⬇️ Download   → boto3.download_file() → /tmp/{job_id}_input
🎵 Conversion → FFmpeg → WAV 16kHz mono
👥 Diarisation→ Pyannote 3.1 (GPU) → release_models()
🎯 ID Speaker → WeSpeaker + Identity Bank S3 → release_models()
✍️ Transcript → Whisper Large-v3-Turbo (GPU) → release_models()
🔗 Fusion     → JSON structuré par speaker
💾 Results    → boto3.put_object() → s3://processed/{timestamp}_{filename}/
🧹 Cleanup    → Suppression /tmp/
📞 Webhook    → POST /api/v1/internal/webhook/transcription-complete
```

---

## 6. Endpoints API (V6.0)

### Authentication
```
POST /api/v1/auth/register
POST /api/v1/auth/login
```

### Users
```
GET /api/v1/users/me  (avec groupes)
```

### Upload
```
POST /api/v1/process/
  Body (multipart):
    - file: File (audio/video)
    - title?: string
    - group_ids: string (JSON array "[1,2]" ou CSV "1,2")
```

### Meetings
```
GET  /api/v1/meetings/              (filtres: group_id, status)
GET  /api/v1/meetings/{id}
GET  /api/v1/meetings/mine
PATCH /api/v1/meetings/{id}         (owner only)
DELETE /api/v1/meetings/{id}        (owner only)
```

### Groups
```
GET  /api/v1/groups/
GET  /api/v1/groups/{id}
POST /api/v1/groups/                (admin only)
PATCH /api/v1/groups/{id}           (admin only)
DELETE /api/v1/groups/{id}          (admin only)
```

---

## 7. État Actuel & Roadmap

**✅ Backend V6.0 - Complet :**
- ✅ Modèle Groups unifié (department, project, recurring)
- ✅ Migrations Alembic + Seed automatique
- ✅ Auth JWT (login, register)
- ✅ Upload audio/vidéo avec sélection groupes
- ✅ Pipeline IA complet (Diarisation → Identification → Transcription)
- ✅ CRUD Meetings avec filtres
- ✅ CRUD Groups
- ✅ Webhook Worker → API
- ✅ Script manage.sh (start, stop, reset-db, rebuild)

**🎯 Frontend - En cours :**
- [ ] Dashboard Dark (Linear style + Glassmorphism)
- [ ] Smart Cards (Feed de réunions)
- [ ] Upload avec drag & drop
- [ ] Lecteur audio/vidéo intégré
- [ ] Page détail transcription

**🚀 Future (Phase 3) :**
- [ ] RAG Chat (interroger réunions avec LLM)
- [ ] AI Insights automatiques (actions, décisions, bloqueurs)
- [ ] Export PDF/Word
- [ ] Reconnaissance faciale (Identity Bank)

---

## 8. Commandes Utiles (manage.sh)

```bash
# Démarrer tous les services
./manage.sh start

# Arrêter tous les services
./manage.sh stop

# Redémarrer
./manage.sh restart

# Voir les logs
./manage.sh logs [service]

# Réinitialiser la base de données (⚠️ DESTRUCTIF)
./manage.sh reset-db

# Reconstruire un service
./manage.sh rebuild [service]

# Voir l'état
./manage.sh status
```

### Tests manuels

```bash
# Login
curl -X POST http://localhost:5000/api/v1/auth/login \
  -d "username=admin@example.com&password=admin123"

# Upload (avec token)
curl -X POST http://localhost:5000/api/v1/process/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@audio.m4a" \
  -F "title=Test Meeting" \
  -F "group_ids=[1,2]"

# Lister meetings
curl http://localhost:5000/api/v1/meetings/ \
  -H "Authorization: Bearer $TOKEN"
```

### Interfaces Web

```
API Docs (Swagger)  : http://localhost:5000/docs
Frontend            : http://localhost:3000
MinIO Console       : http://localhost:9001
Qdrant Dashboard    : http://localhost:6333/dashboard
```

---

## 9. Variables d'Environnement Clés

| Variable | Description |
|----------|-------------|
| `MINIO_ROOT_USER` | Credentials MinIO |
| `MINIO_ROOT_PASSWORD` | Credentials MinIO |
| `MINIO_ENDPOINT` | Adresse MinIO (ex: `minio:9000`) |
| `POSTGRES_USER/PASSWORD/DB` | Credentials PostgreSQL |
| `REDIS_URL` | URL Redis (ex: `redis://sms_redis:6379`) |
| `HF_TOKEN` | Token HuggingFace (modèles gated Pyannote) |
| `JWT_SECRET_KEY` | Clé de signature JWT |
| `INTERNAL_API_KEY` | Clé pour webhook interne |

---

## 10. Groupes par Défaut (Seed)

| Groupe | Type | Description |
|--------|------|-------------|
| Tous | department | Groupe par défaut |
| Direction | department | Équipe de direction |
| R&D | department | Recherche & Développement |
| Marketing | department | Marketing & Com |
| Commercial | department | Équipe commerciale |
| RH | department | Ressources Humaines |
| Finance | department | Finance & Comptabilité |
| COMOP | recurring | Comité opérationnel hebdo |
| Café AGAM | recurring | Présentation hebdo |

**Admin par défaut** : `admin@example.com` / `admin123`

---

*Dernière mise à jour : 17 Janvier 2026 - V6.0*
