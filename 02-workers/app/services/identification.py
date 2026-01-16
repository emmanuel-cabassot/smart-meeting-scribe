"""
Service d'identification des locuteurs par signature vocale (WeSpeaker).
Compare les segments audio avec une banque d'identités stockée sur S3/MinIO.

Structure S3:
    s3://identity-bank/{user_id}/{person_id}/voice/sample.wav
"""
import os
import logging
import tempfile
import numpy as np
from scipy.spatial.distance import cdist
from app.core.models import load_embedding_model
from app.worker.tasks.base import get_s3_client

logger = logging.getLogger(__name__)

# Configuration
IDENTITY_BANK_BUCKET = "identity-bank"
DEFAULT_USER_ID = "default"  # À remplacer par l'ID réel quand auth sera en place


def get_voice_bank_embeddings(user_id: str = DEFAULT_USER_ID):
    """
    Télécharge les échantillons vocaux depuis S3 et génère les embeddings.
    
    Args:
        user_id: ID de l'utilisateur/organisation
        
    Returns:
        dict: {person_id: embedding_vector}
    """
    embeddings = {}
    s3 = get_s3_client()
    
    try:
        # Lister tous les objets dans identity-bank/{user_id}/
        prefix = f"{user_id}/"
        response = s3.list_objects_v2(Bucket=IDENTITY_BANK_BUCKET, Prefix=prefix)
        
        if "Contents" not in response:
            logger.info(f"   ℹ️ Aucune identité trouvée pour user_id={user_id}")
            return {}
        
        # Trouver les fichiers voice/sample.wav
        voice_files = [
            obj["Key"] for obj in response["Contents"]
            if obj["Key"].endswith("/voice/sample.wav")
        ]
        
        if not voice_files:
            logger.info("   ⚠️ Aucun échantillon vocal trouvé dans l'identity-bank")
            return {}
        
        # Charger le modèle d'embedding
        model = load_embedding_model()
        
        # Télécharger et traiter chaque échantillon
        for s3_key in voice_files:
            # Extraire person_id du chemin: default/homme/voice/sample.wav -> homme
            parts = s3_key.split("/")
            if len(parts) >= 3:
                person_id = parts[1]  # Ex: "homme", "femme"
            else:
                continue
            
            # Télécharger dans un fichier temporaire
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_path = tmp_file.name
                
            try:
                s3.download_file(IDENTITY_BANK_BUCKET, s3_key, tmp_path)
                
                # Calculer l'embedding
                emb = model(tmp_path)
                embeddings[person_id] = emb
                logger.info(f"   👤 Signature vocale chargée : {person_id}")
                
            finally:
                # Nettoyer le fichier temporaire
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
        
        return embeddings
        
    except Exception as e:
        logger.warning(f"   ⚠️ Erreur lecture identity-bank: {e}")
        return {}


def identify_speaker(unknown_emb, bank_embeddings, threshold=0.5):
    """
    Compare un vecteur inconnu avec la banque via Similarité Cosinus.
    
    Args:
        unknown_emb: Embedding du segment audio à identifier
        bank_embeddings: Dictionnaire {nom: embedding} de la banque de voix
        threshold: Seuil de confiance minimum (0.0 à 1.0)
    
    Returns:
        tuple: (nom du locuteur ou None si non reconnu, score de similarité)
    """
    if not bank_embeddings:
        return None, 0.0
    
    best_match = None
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
        return None, best_score
