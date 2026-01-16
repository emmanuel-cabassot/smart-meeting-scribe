# 🔌 Backend API - FastAPI

API Gateway pour Smart Meeting Scribe V5.4 avec support organisationnel (Services & Projets).

## 🏗️ Architecture

```
backend/
├── app/
│   ├── main.py                      # Point d'entrée FastAPI
│   │
│   ├── core/                        # 🔧 Configuration & Sécurité
│   │   ├── config.py                # Variables d'environnement (Pydantic)
│   │   ├── security.py              # JWT, Password hashing
│   │   └── deps.py                  # Dépendances (get_db, get_current_user)
│   │
│   ├── db/                          # 🗄️ Base de données
│   │   ├── base_class.py            # Classe Base SQLAlchemy
│   │   ├── base.py                  # Import des modèles (Alembic)
│   │   ├── session.py               # AsyncPG PostgreSQL
│   │   └── init_db.py               # Script de seed (Services, Projets)
│   │
│   ├── models/                      # 📊 Modèles SQLAlchemy
│   │   ├── user.py                  # User (avec service_id, projects)
│   │   ├── meeting.py               # Meeting (avec is_confidential, projects)
│   │   └── organization.py          # Service, Project, tables M2M
│   │
│   ├── schemas/                     # 📝 Schemas Pydantic
│   │   ├── user.py                  # UserOut, UserWithContext
│   │   ├── meeting.py               # MeetingOut, MeetingWithContext
│   │   ├── organization.py          # ServiceRead, ProjectRead
│   │   └── token.py                 # Token JWT
│   │
│   ├── services/                    # 🧠 Logique métier (CRUD)
│   │   ├── auth.py                  # Authentification
│   │   ├── user.py                  # CRUD User
│   │   ├── meeting.py               # Visibilité matricielle
│   │   └── organization.py          # CRUD Services/Projets
│   │
│   ├── api/v1/                      # 🌐 Routes API
│   │   ├── router.py                # Agrège tous les endpoints
│   │   └── endpoints/
│   │       ├── auth.py              # /auth (login, register)
│   │       ├── users.py             # /users (profil avec contexte)
│   │       ├── transcribe.py        # /process (upload sécurisé)
│   │       ├── meetings.py          # /meetings (CRUD + visibilité)
│   │       ├── organization.py      # /org (services, projects)
│   │       └── webhook.py           # /internal/webhook (callback Worker)
│   │
│   └── worker/                      # 🔄 Background tasks (TaskIQ)
│       └── broker.py                # Redis broker
│
├── alembic/                         # 🔄 Migrations DB
│   ├── versions/
│   │   └── 001_initial.py           # Migration initiale
│   └── env.py
│
├── tests/                           # 🧪 Tests
├── alembic.ini
├── requirements.txt
├── Dockerfile
└── start.sh                         # Script démarrage (migrations + seed)
```

## 🚀 Endpoints

### Auth (`/api/v1/auth`)

| Méthode | Route | Auth | Description |
|---------|-------|------|-------------|
| `POST` | `/register` | ❌ | Créer un compte |
| `POST` | `/login` | ❌ | Obtenir un JWT |

### Users (`/api/v1/users`)

| Méthode | Route | Auth | Description |
|---------|-------|------|-------------|
| `GET` | `/me` | ✅ | Profil utilisateur avec service et projets |

### Process (`/api/v1/process`)

| Méthode | Route | Auth | Description |
|---------|-------|------|-------------|
| `POST` | `/` | ✅ | Upload audio → créer Meeting → dispatch Worker |
| `GET` | `/status/{task_id}` | ❌ | Polling du statut de transcription |

### Meetings (`/api/v1/meetings`)

| Méthode | Route | Auth | Description |
|---------|-------|------|-------------|
| `GET` | `/` | ✅ | Liste meetings visibles (logique matricielle) |
| `GET` | `/?service_id=1` | ✅ | Filtre par service |
| `GET` | `/?project_id=2` | ✅ | Filtre par projet |
| `GET` | `/?status=pending` | ✅ | Filtre par status |
| `GET` | `/mine` | ✅ | Liste mes meetings uniquement |
| `GET` | `/{id}` | ✅ | Détail d'un meeting (check visibilité) |
| `PATCH` | `/{id}` | ✅ Owner | Modifier un meeting |
| `DELETE` | `/{id}` | ✅ Owner | Supprimer un meeting |
| `GET` | `/stats/count` | ✅ | Compteur de meetings |

### Organization (`/api/v1/org`)

| Méthode | Route | Auth | Description |
|---------|-------|------|-------------|
| `GET` | `/services` | ✅ | Liste tous les services |
| `GET` | `/services/{id}` | ✅ | Détail d'un service |
| `POST` | `/services` | 🔐 Admin | Créer un service |
| `PATCH` | `/services/{id}` | 🔐 Admin | Modifier un service |
| `DELETE` | `/services/{id}` | 🔐 Admin | Supprimer un service |
| `GET` | `/projects` | ✅ | Liste tous les projets |
| `GET` | `/projects/me` | ✅ | Projets de l'utilisateur |
| `GET` | `/projects/{id}` | ✅ | Détail d'un projet |
| `POST` | `/projects` | 🔐 Admin | Créer un projet |
| `PATCH` | `/projects/{id}` | 🔐 Admin | Modifier un projet |
| `DELETE` | `/projects/{id}` | 🔐 Admin | Supprimer un projet |

### Internal Webhook (`/api/v1/internal/webhook`)

| Méthode | Route | Auth | Description |
|---------|-------|------|-------------|
| `POST` | `/transcription-complete` | 🔑 API Key | Callback du Worker pour sync status |

> ⚠️ **Sécurité** : Le webhook requiert le header `X-Internal-Key` avec la clé interne.

## 🧠 Logique Matricielle

Le système utilise une double appartenance :
- **Service** (1:N) : Département hiérarchique (R&D, Sales...)
- **Projet** (N:N) : Mission transversale (Lancement V5...)

### Algorithme de visibilité

Un utilisateur voit un meeting si :
- ✅ Il est dans le **même Service** que le meeting
- ✅ OU il partage un **Projet** avec le meeting (sauf si `is_confidential=true`)

Voir [ORGANIZATION_LOGIC.md](../ORGANIZATION_LOGIC.md) pour les détails.

## 🔐 Authentification

```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:5000/api/v1/auth/login \
  -d "username=admin@example.com&password=admin123" | jq -r '.access_token')

# 2. Profil utilisateur avec contexte
curl http://localhost:5000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN"

# 3. Upload un fichier audio (avec auth)
curl -X POST http://localhost:5000/api/v1/process/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@mon_audio.mp3" \
  -F "title=Ma réunion"

# 4. Lister mes meetings visibles (avec filtres)
curl "http://localhost:5000/api/v1/meetings/?status=completed" \
  -H "Authorization: Bearer $TOKEN"
```

## 🐳 Docker

```bash
# Build
docker compose build backend

# Run
docker compose up -d

# Logs
docker logs sms_api -f
```

Au démarrage, le script `start.sh` :
1. Attend PostgreSQL
2. Exécute les migrations Alembic
3. Seed la DB (Services, Projets, Admin)
4. Lance Uvicorn

## 🌱 Données de Seed

| Type | Valeurs |
|------|---------|
| Services | R&D, Sales, Marketing, HR, Finance |
| Projets | Lancement V5, Audit Sécurité |
| Admin | `admin@example.com` / `admin123` |

## 📚 Documentation

| URL | Description |
|-----|-------------|
| http://localhost:5000/docs | Swagger UI |
| http://localhost:5000/redoc | ReDoc |
