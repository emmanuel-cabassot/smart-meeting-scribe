"""
Point d'entrée principal de l'application Smart Meeting Scribe.

Ce fichier est volontairement minimaliste (~25 lignes). Son rôle :
1. Créer l'instance FastAPI avec les métadonnées
2. Monter le router API v1 (qui contient tous les endpoints)
3. Fournir une route santé à la racine

Toute la logique métier est déléguée aux modules :
- api/v1/router.py → centralise les endpoints
- services/        → logique IA (diarisation, transcription, etc.)
- core/            → configuration et gestion des modèles

Architecture :
    main.py (ce fichier)
        └── api/v1/router.py
            ├── endpoints/transcribe.py  → POST /api/v1/process/
            └── endpoints/voice_bank.py  → GET /api/v1/voice-bank/
"""

from fastapi import FastAPI
from app.api.v1.router import api_router  # Import du router hub qui contient tous les endpoints
import torch  # Pour vérifier la disponibilité GPU

# ══════════════════════════════════════════════════════════════════════════════
# CRÉATION DE L'APPLICATION FASTAPI
# ══════════════════════════════════════════════════════════════════════════════
# Ces métadonnées apparaissent dans la documentation Swagger (http://localhost:5000/docs)
# ══════════════════════════════════════════════════════════════════════════════
app = FastAPI(
    title="Smart Meeting Scribe",
    description="API de transcription et diarisation optimisée VRAM",
    version="1.0.0"
)

# ══════════════════════════════════════════════════════════════════════════════
# MONTAGE DU ROUTER API V1
# ══════════════════════════════════════════════════════════════════════════════
# On "monte" le router principal sur le préfixe /api/v1
# Toutes les routes définies dans api_router seront préfixées par /api/v1
# Exemple : POST "/" dans transcribe.py → POST /api/v1/process/
# ══════════════════════════════════════════════════════════════════════════════
app.include_router(api_router, prefix="/api/v1")


# ══════════════════════════════════════════════════════════════════════════════
# ROUTE SANTÉ (HEALTH CHECK)
# ══════════════════════════════════════════════════════════════════════════════
# Route simple à la racine pour vérifier que le serveur fonctionne
# et que le GPU est disponible
# ══════════════════════════════════════════════════════════════════════════════
@app.get("/")
async def root():
    """
    Health check endpoint.
    
    Returns:
        JSON avec message de bienvenue et statut GPU
    """
    return {
        "message": "Bienvenue sur l'API Smart Meeting Scribe",
        "gpu_available": torch.cuda.is_available(),
        "device": "cuda" if torch.cuda.is_available() else "cpu"
    }


# ══════════════════════════════════════════════════════════════════════════════
# LANCEMENT EN MODE DÉVELOPPEMENT
# ══════════════════════════════════════════════════════════════════════════════
# Ce bloc n'est exécuté que si on lance directement : python main.py
# En production (Docker), uvicorn est lancé différemment via le Dockerfile
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import uvicorn
    # reload=True : redémarre automatiquement quand le code change
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)