# 🌐 Interface - Application Web

Couche présentation de Smart Meeting Scribe.

## 📦 Composants

| Composant | Description | Port |
|-----------|-------------|------|
| **[Backend](./backend/)** | API FastAPI (Auth, Process, S3) | `:5000` |
| **[Frontend](./frontend-nextjs/)** | Next.js 16 (Standalone Docker) | `:3000` |

## 🚀 Démarrage

```bash
cd 03-interface
docker compose up -d
```

## 🔗 Dépendances

Nécessite que `01-core` soit démarré (PostgreSQL, Redis, MinIO).

## ⚙️ Configuration

Variables dans `.env` :
- `POSTGRES_*` - Connexion BDD
- `MINIO_*` - Accès S3
- `REDIS_URL` - Broker TaskIQ
- `JWT_SECRET_KEY` - Clé de signature JWT
