from fastapi import APIRouter
from app.api.v1.endpoints import transcribe, auth

api_router = APIRouter()

# Routes d'Authentification (/api/v1/auth/login, /api/v1/auth/register)
api_router.include_router(auth.router, prefix="/auth", tags=["Authentification"])

# Routes de Process (IA)
api_router.include_router(transcribe.router, prefix="/process", tags=["Processing"])
