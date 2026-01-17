from fastapi import APIRouter
from app.api.v1.endpoints import transcribe, auth, meetings, users, webhook, groups

api_router = APIRouter()

# Routes d'Authentification (/api/v1/auth/login, /api/v1/auth/register)
api_router.include_router(auth.router, prefix="/auth", tags=["Authentification"])

# Routes Utilisateur (/api/v1/users/me)
api_router.include_router(users.router, prefix="/users", tags=["Users"])

# Routes de Process (IA)
api_router.include_router(transcribe.router, prefix="/process", tags=["Processing"])

# Routes Groupes (CRUD + membres)
api_router.include_router(groups.router, prefix="/groups", tags=["Groups"])

# Routes Meetings (CRUD avec visibilité par groupes)
api_router.include_router(meetings.router, prefix="/meetings", tags=["Meetings"])

# Routes Webhook internes (appelées par le Worker)
api_router.include_router(webhook.router, prefix="/internal/webhook", tags=["Internal"])
