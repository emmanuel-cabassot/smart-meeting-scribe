# 🔌 Backend API - FastAPI

API Gateway pour Smart Meeting Scribe V6.0 avec support des Groupes (Départements, Projets, Réunions Récurrentes).

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
│   │   └── init_db.py               # Script de seed (Groupes par défaut)
│   │
│   ├── models/                      # 📊 Modèles SQLAlchemy
│   │   ├── user.py                  # User
│   │   ├── meeting.py               # Meeting
│   │   └── group.py                 # Group (Type: Department, Project, Recurring)
│   │
│   ├── schemas/                     # 📝 Schemas Pydantic
│   │   ├── user.py                  # UserOut
│   │   ├── meeting.py               # MeetingOut
│   │   ├── group.py                 # GroupRead
│   │   └── token.py                 # Token JWT
│   │
│   ├── services/                    # 🧠 Logique métier (CRUD)
│   │   ├── auth.py                  # Authentification
│   │   ├── user.py                  # CRUD User
│   │   ├── meeting.py               # Gestion Meetings
│   │   └── group.py                 # CRUD Groupes
│   │
│   ├── api/v1/                      # 🌐 Routes API
│   │   ├── router.py                # Agrège tous les endpoints
│   │   └── endpoints/
│   │       ├── auth.py              # /auth (login, register)
│   │       ├── users.py             # /users (profil)
│   │       ├── transcribe.py        # /process (upload sécurisé)
│   │       ├── meetings.py          # /meetings (CRUD)
│   │       ├── groups.py            # /groups (CRUD)
│   │       └── webhook.py           # /internal/webhook (callback Worker)
│   │
│   └── worker/                      # 🔄 Background tasks (TaskIQ)
│       └── broker.py                # Redis broker
│
├── alembic/                         # 🔄 Migrations DB
│   ├── versions/
│   │   └── 001_initial.py           # Migration initiale (Group model)
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
| `GET` | `/me` | ✅ | Profil utilisateur avec ses groupes |

### Process (`/api/v1/process`)

| Méthode | Route | Auth | Description |
|---------|-------|------|-------------|
| `POST` | `/` | ✅ | Upload audio → créer Meeting → dispatch Worker |
| `GET` | `/status/{task_id}` | ❌ | Polling du statut de transcription |

**Paramètres POST `/` :**
- `file`: Fichier audio/vidéo
- `title`: Titre (optionnel)
- `group_ids`: Liste des IDs de groupes (ex: `[1, 2]`) - **JSON Array requis**

### Meetings (`/api/v1/meetings`)

| Méthode | Route | Auth | Description |
|---------|-------|------|-------------|
| `GET` | `/` | ✅ | Liste meetings (visibles selon groupes) |
| `GET` | `/?group_id=1` | ✅ | Filtre par groupe |
| `GET` | `/?status=pending` | ✅ | Filtre par status |
| `GET` | `/mine` | ✅ | Liste mes meetings uniquement |
| `GET` | `/{id}` | ✅ | Détail d'un meeting |
| `GET` | `/{id}/transcript` | ✅ | **Transcription complète** (segments depuis S3) |
| `PATCH` | `/{id}` | ✅ Owner | Modifier un meeting |
| `DELETE` | `/{id}` | ✅ Owner | Supprimer un meeting |
| `GET` | `/stats/count` | ✅ | Compteur de meetings |

### Groups (`/api/v1/groups`)

| Méthode | Route | Auth | Description |
|---------|-------|------|-------------|
| `GET` | `/` | ✅ | Liste tous les groupes |
| `GET` | `/{id}` | ✅ | Détail d'un groupe |
| `POST` | `/` | 🔐 Admin | Créer un groupe |
| `PATCH` | `/{id}` | 🔐 Admin | Modifier un groupe |
| `DELETE` | `/{id}` | 🔐 Admin | Supprimer un groupe |

### Internal Webhook (`/api/v1/internal/webhook`)

| Méthode | Route | Auth | Description |
|---------|-------|------|-------------|
| `POST` | `/transcription-complete` | 🔑 API Key | Callback du Worker pour sync status |

> ⚠️ **Sécurité** : Le webhook requiert le header `X-Internal-Key` avec la clé interne.

## 🏢 Modèle de Groupes

Le système utilise un modèle de **Groupes Unifiés** pour simplifier la gestion des droits, inspiré d'Azure AD.

### Types de Groupes
1.  **Department** (`department`): Structure hiérarchique (R&D, Marketing, Direction...).
2.  **Project** (`project`): Projets transversaux ou temporaires.
3.  **Recurring** (`recurring`): Réunions récurrentes (COMOP, Daily...).

### Règles
- Un **Meeting** appartient à un ou plusieurs **Groupes**.
- Un **User** appartient à un ou plusieurs **Groupes**.
- Un User voit un Meeting si ils ont au moins un **Groupe en commun** (ou si il est le propriétaire).

## 🔐 Authentification & Usage

```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:5000/api/v1/auth/login \
  -d "username=admin@example.com&password=admin123" | jq -r '.access_token')

# 2. Upload un fichier audio
# IMPORTANT : group_ids doit être un tableau JSON stringify : "[1, 2]"
curl -X POST http://localhost:5000/api/v1/process/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@mon_audio.mp3" \
  -F "title=Comité Direction" \
  -F "group_ids=[1, 2]"

# 3. Lister les meetings
curl "http://localhost:5000/api/v1/meetings/?status=completed" \
  -H "Authorization: Bearer $TOKEN"

# 4. Récupérer la transcription complète
curl "http://localhost:5000/api/v1/meetings/1/transcript" \
  -H "Authorization: Bearer $TOKEN"
```

### Réponse `/meetings/{id}/transcript`

```json
{
  "meeting_id": 1,
  "title": "Docker et CUDA",
  "status": "completed",
  "created_at": "2026-01-17T23:56:11.666692",
  "segments": [
    {
      "start": 0.00,
      "end": 5.32,
      "text": "Bonjour, on va parler de l'architecture Docker...",
      "speaker": "femme"
    },
    {
      "start": 5.50,
      "end": 10.24,
      "text": "Oui, notamment la partie GPU avec nvidia-docker.",
      "speaker": "homme"
    }
  ]
}
```

> 📝 **Note** : Le meeting doit être en status `completed` pour que la transcription soit disponible. Les données sont lues depuis S3 (bucket `processed`).

## �️ Gestion (Manage Script)

Utilisez le script `manage.sh` à la racine pour gérer le projet :

```bash
# Lancer tous les services
./manage.sh start

# Voir les logs
./manage.sh logs

# Réinitialiser la base de données (SUPPRIME TOUTES LES DONNÉES)
./manage.sh reset-db
```

## 🌱 Données de Seed

| Groupe | Type | Description |
|--------|------|-------------|
| Tous | `department` | Groupe par défaut |
| Direction | `department` | Équipe de direction |
| R&D | `department` | Recherche & Développement |
| Marketing | `department` | Marketing & Com |
| COMOP | `recurring` | Comité opérationnel |
| Café AGAM | `recurring` | Présentation hebdo |

**Admin par défaut** : `admin@example.com` / `admin123`