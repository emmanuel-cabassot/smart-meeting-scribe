from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.broker import broker
from app.api.v1.router import api_router
from app.db.session import engine
from app.db.base import Base

# IMPORTANT : Import des modèles pour que SQLAlchemy les connaisse
from app.models import user, meeting

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- PHASE STARTUP ---
    print("🚀 [API] Démarrage du cycle de vie...")
    
    # 1. Connexion au Broker Redis
    await broker.startup()
    print("🔗 [API] Connectée à Redis.")

    # 2. Création des tables SQL dans Postgres
    async with engine.begin() as conn:
        # Cette ligne crée les tables si elles n'existent pas
        await conn.run_sync(Base.metadata.create_all)
    print("🗄️ [API] Tables SQL synchronisées (Users, Meetings).")

    yield
    
    # --- PHASE SHUTDOWN ---
    print("🛑 [API] Arrêt...")
    await broker.shutdown()

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan
)

# Configuration CORS (Pour autoriser ton futur frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def status():
    return {"status": "online", "role": "Interface API V5"}