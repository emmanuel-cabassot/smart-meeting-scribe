"""
Endpoint de gestion de la banque de voix.

Ce fichier gère les routes pour consulter et gérer les voix enregistrées.
La banque de voix est utilisée pour l'identification des locuteurs.

Structure du dossier voice_bank/ :
    voice_bank/
    ├── Emmanuel/
    │   ├── sample1.wav
    │   └── sample2.wav
    └── Marie/
        └── sample1.wav

L'objet `router` créé ici est importé par api/v1/router.py qui le branche
sur le préfixe "/voice-bank". Résultat : GET /api/v1/voice-bank/
"""

from fastapi import APIRouter
import os

# ══════════════════════════════════════════════════════════════════════════════
# CRÉATION DU ROUTER
# ══════════════════════════════════════════════════════════════════════════════
# Ce router sera importé par api/v1/router.py avec la ligne :
#   api_router.include_router(voice_bank.router, prefix="/voice-bank")
# ══════════════════════════════════════════════════════════════════════════════
router = APIRouter()

# Chemin vers le dossier contenant les échantillons vocaux
VOICE_BANK_PATH = "voice_bank"


@router.get("/")
async def list_voices():
    """
    Liste les voix enregistrées dans la banque.
    
    Scanne le dossier voice_bank/ et retourne la liste des sous-dossiers
    (chaque sous-dossier = une personne avec ses échantillons audio).
    
    Returns:
        {"voices": [{"name": "Emmanuel", "files_count": 2}, ...]}
    """
    # Si le dossier n'existe pas, retourner une liste vide
    if not os.path.exists(VOICE_BANK_PATH):
        return {"voices": []}
    
    voices = []
    # Parcourir chaque élément du dossier voice_bank/
    for item in os.listdir(VOICE_BANK_PATH):
        item_path = os.path.join(VOICE_BANK_PATH, item)
        # On ne garde que les sous-dossiers (chaque dossier = une personne)
        if os.path.isdir(item_path):
            files = os.listdir(item_path)
            voices.append({
                "name": item,           # Nom du dossier = nom de la personne
                "files_count": len(files)  # Nombre d'échantillons audio
            })
    
    return {"voices": voices}
