"""
Service d'identification des locuteurs par signature vocale (WeSpeaker).
Compare les segments audio avec une banque de voix pré-enregistrées.
"""
import os
import numpy as np
from scipy.spatial.distance import cdist
from core.models import load_embedding_model

# Chemin vers le dossier contenant les fichiers .wav de référence
VOICE_BANK_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "voice_bank")


def get_voice_bank_embeddings():
    """Scan le dossier voice_bank et génère les signatures vocales."""
    embeddings = {}
    
    if not os.path.exists(VOICE_BANK_PATH):
        print(f"   ⚠️ Dossier voice_bank non trouvé : {VOICE_BANK_PATH}")
        return {}

    files = [f for f in os.listdir(VOICE_BANK_PATH) if f.endswith(".wav")]
    
    if not files:
        print("   ⚠️ Aucun fichier .wav trouvé dans voice_bank/")
        return {}
    
    model = load_embedding_model()
    
    for f in files:
        name = os.path.splitext(f)[0]
        path = os.path.join(VOICE_BANK_PATH, f)
        # Calcul du vecteur (Embedding)
        emb = model(path)
        embeddings[name] = emb
        print(f"   👤 Signature vocale enregistrée pour : {name}")
    
    return embeddings


def identify_speaker(unknown_emb, bank_embeddings, threshold=0.5):
    """
    Compare un vecteur inconnu avec la banque via Similarité Cosinus.
    
    Args:
        unknown_emb: Embedding du segment audio à identifier
        bank_embeddings: Dictionnaire {nom: embedding} de la banque de voix
        threshold: Seuil de confiance minimum (0.0 à 1.0)
    
    Returns:
        tuple: (nom du locuteur ou "Inconnu", score de similarité)
    """
    if not bank_embeddings:
        return "Inconnu", 0.0
    
    best_match = "Inconnu"
    best_score = 0.0
    
    for name, known_emb in bank_embeddings.items():
        # Calcul de la similarité (1 - distance cosinus)
        # cdist attend des tableaux 2D, on reshape donc les vecteurs
        dist = cdist(
            unknown_emb.reshape(1, -1), 
            known_emb.reshape(1, -1), 
            metric="cosine"
        )[0, 0]
        score = 1 - dist
        
        if score > best_score:
            best_score = score
            best_match = name
            
    # On ne valide que si on dépasse le seuil de confiance
    if best_score > threshold:
        return best_match, best_score
    else:
        return "Inconnu", best_score
