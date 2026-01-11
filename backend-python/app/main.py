"""
Smart Meeting Scribe V3.1 - API Gateway
Versions : FastAPI 0.128.0 | Taskiq 0.12.1 | Postgres 18
"""

# 🛡️ 1. SHIELD TORCHAUDIO (Compatibilité Pyannote vs Versions 2026)
# Doit impérativement être placé avant l'import des routeurs ou modèles IA
import torchaudio
if not hasattr(torchaudio, "set_audio_backend"):
    setattr(torchaudio, "set_audio_backend", lambda x: None)

from fastapi import FastAPI
import uvicorn

# --- Imports Application V3.1 ---
from app.api.v1.router import api_router
from app.broker import broker
from app.worker.tasks import process_transcription_full

# --- Imports Base de Données (Nouveauté V3.1) ---
from app.core.database import engine, Base
# ⚠️ IMPORT CRITIQUE : On importe le module des modèles pour que SQLAlchemy les détecte.
# Sans cet import, Base.metadata.create_all ne créera aucune table.
from app.core import models_db 

# ══════════════════════════════════════════════════════════════════════════════
# INITIALISATION DE L'APPLICATION
# ══════════════════════════════════════════════════════════════════════════════
app = FastAPI(
    title="Smart Meeting Scribe V3.1",
    description="API Gateway Asynchrone (FastAPI + Taskiq + Redis + Postgres)",
    version="3.1.0"
)

# ══════════════════════════════════════════════════════════════════════════════
# GESTION DU CYCLE DE VIE (LIFECYCLE)
# ══════════════════════════════════════════════════════════════════════════════
@app.on_event("startup")
async def startup():
    """
    Séquence de démarrage V3.1 :
    1. Initialisation de la Base de Données (Création des tables).
    2. Connexion au Broker de Tâches (Redis).
    """
    print("🚀 [BOOT] Démarrage de Smart Meeting Scribe V3.1...")

    # A. INITIALISATION DB (Auto-Migration)
    # On se connecte à Postgres et on crée les tables si elles n'existent pas
    try:
        async with engine.begin() as conn:
            # create_all lit tous les modèles enregistrés dans Base (d'où l'import de models_db)
            await conn.run_sync(Base.metadata.create_all)
        print("💾 [DB] Tables synchronisées avec succès (PostgreSQL).")
    except Exception as e:
        print(f"❌ [DB] Erreur critique lors de l'init DB : {e}")
        # On ne bloque pas forcément le boot, mais c'est grave.

    # B. CONNEXION BROKER TASKIQ
    # On ne lance le broker que si on est dans le processus API (pas le worker)
    if not broker.is_worker_process:
        await broker.startup()
        print("🔗 [TASKIQ] Connecté au Broker Redis.")

@app.on_event("shutdown")
async def shutdown():
    """Déconnexion propre des services à l'arrêt."""
    if not broker.is_worker_process:
        await broker.shutdown()
        print("👋 [TASKIQ] Déconnexion du Broker.")
    
    # Note : Le moteur SQLAlchemy (engine) gère son pool tout seul, 
    # pas besoin de close() explicite ici en asyncpg généralement.

# ══════════════════════════════════════════════════════════════════════════════
# ROUTING & ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

# Inclusion du router principal (endpoints /process, /voice-bank...)
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def status():
    """Health check global."""
    return {
        "status": "online", 
        "version": "3.1.0", 
        "components": {
            "api": "FastAPI",
            "worker": "Taskiq",
            "database": "PostgreSQL 18",
            "storage": "fsspec"
        }
    }

@app.post("/test-queue")
async def send_test(msg: str = "Test-Audio"):
    """
    Endpoint de debug pour tester la communication API -> Worker.
    Envoie une tâche factice sans passer par l'upload de fichier.
    """
    meeting_id = "test-uuid-debug-123"
    fake_file_path = f"/data/uploads/{msg}.wav"
    
    # Envoi asynchrone via .kiq()
    sent_task = await process_transcription_full.kiq(
        file_path=fake_file_path,
        meeting_id=meeting_id
    )
    
    return {
        "status": "Job IA simulé envoyé",
        "task_id": sent_task.task_id,
        "meeting_id": meeting_id,
        "info": "Vérifier les logs du conteneur 'worker' pour voir la réception."
    }

# ══════════════════════════════════════════════════════════════════════════════
# DÉMARRAGE (DEV LOCAL)
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=5000, reload=True)