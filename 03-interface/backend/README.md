# 🔌 Backend API - FastAPI

API Gateway pour Smart Meeting Scribe V5 avec support organisationnel (Services & Projets).

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
│   │       ├── transcribe.py        # /process (upload, status)
│   │       └── organization.py      # /org (services, projects)
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

### Process (`/api/v1/process`)

| Méthode | Route | Auth | Description |
|---------|-------|------|-------------|
| `POST` | `/` | ❌ | Upload audio → S3 → dispatch Worker |
| `GET` | `/status/{task_id}` | ❌ | Polling du statut |

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

## 🧠 Logique Matricielle

Le système utilise une double appartenance :
- **Service** (1:N) : Département hiérarchique (R&D, Sales...)
- **Projet** (N:N) : Mission transversale (Lancement V5...)

Voir [ORGANIZATION_LOGIC.md](../ORGANIZATION_LOGIC.md) pour les détails.

## 🔐 Authentification

```bash
# 1. Login
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=admin123"

# 2. Utiliser le token
curl http://localhost:5000/api/v1/org/services \
  -H "Authorization: Bearer <TOKEN>"
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
