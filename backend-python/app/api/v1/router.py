"""
Router principal de l'API v1.

Ce fichier agit comme un "hub" qui centralise tous les endpoints de la version 1.
Il est lui-même importé par main.py avec :
    app.include_router(api_router, prefix="/api/v1")

Architecture des imports :
    main.py
        └── api/v1/router.py  (ce fichier)
            ├── endpoints/transcribe.py  → branchée sur /process
            └── endpoints/voice_bank.py  → branchée sur /voice-bank

Résultat final des routes :
    POST /api/v1/process/      → transcribe.transcribe_audio()
    GET  /api/v1/voice-bank/   → voice_bank.list_voices()
"""

from fastapi import APIRouter

# ══════════════════════════════════════════════════════════════════════════════
# IMPORT DES MODULES D'ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════
# Chaque module (transcribe, voice_bank) expose un objet `router` de type APIRouter
# On les importe ici pour les "brancher" sur notre router principal
# ══════════════════════════════════════════════════════════════════════════════
from app.api.v1.endpoints import transcribe, voice_bank

# ══════════════════════════════════════════════════════════════════════════════
# CRÉATION DU ROUTER PRINCIPAL V1
# ══════════════════════════════════════════════════════════════════════════════
# Ce router sera importé par main.py et monté sur /api/v1
# ══════════════════════════════════════════════════════════════════════════════
api_router = APIRouter()

# ══════════════════════════════════════════════════════════════════════════════
# BRANCHEMENT DES SOUS-ROUTERS
# ══════════════════════════════════════════════════════════════════════════════
# include_router() permet de "monter" un router sur un préfixe
# - prefix : ajoute ce chemin devant toutes les routes du module
# - tags : groupe les routes dans la documentation Swagger (http://localhost:5000/docs)
# ══════════════════════════════════════════════════════════════════════════════

# transcribe.router contient POST "/" → devient POST /api/v1/process/
api_router.include_router(
    transcribe.router, 
    prefix="/process", 
    tags=["Processing"]
)

# voice_bank.router contient GET "/" → devient GET /api/v1/voice-bank/
api_router.include_router(
    voice_bank.router, 
    prefix="/voice-bank", 
    tags=["Voice Bank"]
)
