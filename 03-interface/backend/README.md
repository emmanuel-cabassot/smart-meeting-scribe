# 🔌 Backend API - FastAPI

API Gateway pour Smart Meeting Scribe.

## 🏗️ Architecture

```
app/
├── api/v1/
│   ├── endpoints/
│   │   ├── auth.py          # Login, Register, JWT
│   │   └── transcribe.py    # Upload, Status, Results
│   └── router.py
├── broker.py                # TaskIQ (dispatch vers Worker)
├── core/
│   ├── config.py            # Variables d'environnement
│   └── security.py          # JWT, Password hashing
├── db/
│   └── database.py          # AsyncPG PostgreSQL
├── models/                  # SQLAlchemy Models
├── schemas/                 # Pydantic Schemas
└── main.py                  # FastAPI App
```

## 🚀 Endpoints

### Auth (`/api/v1/auth`)

| Méthode | Route | Description |
|---------|-------|-------------|
| `POST` | `/register` | Créer un compte |
| `POST` | `/login` | Obtenir un JWT |

### Process (`/api/v1/process`)

| Méthode | Route | Description |
|---------|-------|-------------|
| `POST` | `/` | Upload audio → S3 → dispatch Worker |
| `GET` | `/status/{task_id}` | Polling du statut (pending/processing/completed) |

## 📤 Flux Upload

```
1. Frontend → POST /api/v1/process/ (multipart/form-data)
2. API → boto3.upload_fileobj() → s3://uploads/
3. API → kicker.kiq() → Redis (TaskIQ)
4. Return {task_id, status: "queued"}
```

## 📥 Flux Status

```
1. Frontend → GET /status/{task_id}
2. API → Redis (get_result)
   - Si null → {"status": "pending"}
   - Si en cours → {"status": "processing"}
   - Si terminé → Fetch s3://processed/.../fusion.json → {"status": "completed", result: [...]}
```

## 🐳 Docker

```bash
docker build -t sms-backend .
docker run -p 5000:8000 sms-backend
```

## 📚 Documentation

API Swagger disponible sur : http://localhost:5000/docs
