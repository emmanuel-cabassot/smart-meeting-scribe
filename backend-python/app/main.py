"""
Smart Meeting Scribe V3.1 - API Gateway
Versions : FastAPI 0.128.0 | Taskiq 0.12.1
"""

# 🛡️ 1. SHIELD TORCHAUDIO (Compatibilité Pyannote vs Versions 2026)
# Doit impérativement être placé avant l'import des routeurs ou modèles
import torchaudio
if not hasattr(torchaudio, "set_audio_backend"):
    setattr(torchaudio, "set_audio_backend", lambda x: None)

from fastapi import FastAPI
import uvicorn

# --- Imports V3.1 ---
from app.api.v1.router import api_router
from app.broker import broker
# On importe la vraie tâche IA définie dans app/worker/tasks.py
from app.worker.tasks import process_transcription_full

# ══════════════════════════════════════════════════════════════════════════════
# INITIALISATION DE L'APPLICATION
# ══════════════════════════════════════════════════════════════════════════════
app = FastAPI(
    title="Smart Meeting Scribe V3.1",
    description="API Gateway Asynchrone (FastAPI + Taskiq + Redis)",
    version="3.1.0"
)

# ══════════════════════════════════════════════════════════════════════════════
# GESTION DU CYCLE DE VIE (LIFECYCLE)
# ══════════════════════════════════════════════════════════════════════════════
@app.on_event("startup")
async def startup():
    """Connexion au Broker Redis au lancement pour pouvoir envoyer des tâches."""
    if not broker.is_worker_process:
        await broker.startup()
        print("🔗 [API] Connectée au Broker Redis.")

@app.on_event("shutdown")
async def shutdown():
    """Déconnexion propre de Redis à l'arrêt."""
    if not broker.is_worker_process:
        await broker.shutdown()
        print("👋 [API] Déconnexion du Broker.")

# ══════════════════════════════════════════════════════════════════════════════
# ROUTING & ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

# Inclusion du router principal (contient les endpoints transcribe, etc.)
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def status():
    """Health check simple."""
    return {
        "status": "online", 
        "version": "3.1.0", 
        "taskiq": "0.12.1",
        "role": "API Gateway (Producer)"
    }

@app.post("/test-queue")
async def send_test(msg: str = "Test-Audio"):
    """
    Endpoint de test pour vérifier la communication API -> Worker.
    On envoie une tâche factice au pipeline complet.
    """
    # On simule l'ID d'une réunion et un chemin de fichier
    meeting_id = "test-uuid-12345"
    fake_file_path = f"/data/uploads/{msg}.wav"
    
    # Envoi de la tâche vers Redis via .kiq()
    sent_task = await process_transcription_full.kiq(
        file_path=fake_file_path,
        meeting_id=meeting_id
    )
    
    return {
        "status": "Job IA envoyé au worker",
        "task_id": sent_task.task_id,
        "meeting_id": meeting_id,
        "note": "Le worker va tenter de traiter ce fichier fictif."
    }

# ══════════════════════════════════════════════════════════════════════════════
# DÉMARRAGE (LOCAL DEV)
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=5000, reload=True)