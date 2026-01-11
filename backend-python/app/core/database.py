"""
Module de configuration de la Base de Données (PostgreSQL).
Gère la connexion asynchrone pour l'API (FastAPI) et le Worker (Taskiq).
"""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from contextlib import asynccontextmanager

# ══════════════════════════════════════════════════════════════════════════════
# 1. CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════

# Récupération de l'URL depuis les variables d'environnement (définies dans docker-compose)
# Par défaut, on pointe vers localhost pour le dev hors docker, mais dans Docker ce sera "postgres"
DATABASE_URL = os.getenv(
    "POSTGRES_URL", 
    "postgresql+asyncpg://user:password@localhost:5432/smart_meeting"
)

# Création du Moteur Asynchrone (Engine)
# echo=False : Désactive les logs SQL (mettre à True pour le debug)
# pool_pre_ping=True : Vérifie que la connexion est vivante avant de l'utiliser (anti-déconnexion)
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

# Usine à Sessions (Factory)
# C'est ce qui va fabriquer les sessions "jetables" pour chaque requête
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False, # Important pour l'async : garde les objets en mémoire après commit
    autoflush=False
)

# Classe de base pour tous les futurs modèles (Tables)
Base = declarative_base()

# ══════════════════════════════════════════════════════════════════════════════
# 2. DÉPENDANCE POUR L'API (FastAPI)
# ══════════════════════════════════════════════════════════════════════════════
async def get_db():
    """
    Dependency Injection pour FastAPI.
    Crée une session au début de la requête HTTP et la ferme à la fin.
    
    Usage dans une route :
        @router.get("/")
        async def ma_route(db: AsyncSession = Depends(get_db)):
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            # Le commit est fait manuellement dans la route si besoin
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# ══════════════════════════════════════════════════════════════════════════════
# 3. CONTEXTE POUR LE WORKER (Taskiq)
# ══════════════════════════════════════════════════════════════════════════════
@asynccontextmanager
async def get_worker_db():
    """
    Context Manager pour le Worker Taskiq.
    Le Worker n'étant pas une requête HTTP, il doit ouvrir sa session manuellement.
    
    Usage dans tasks.py :
        async with get_worker_db() as db:
            db.add(mon_objet)
            await db.commit()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()