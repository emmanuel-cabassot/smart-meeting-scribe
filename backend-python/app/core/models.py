from faster_whisper import WhisperModel
from pyannote.audio import Pipeline, Model, Inference
import torch
import gc
from app.core.config import DEVICE, COMPUTE_TYPE, HF_TOKEN

# Variables globales
current_whisper = None
current_pipeline = None
current_embedding = None

def load_whisper():
    global current_whisper
    if current_whisper is None:
        print("   📥 Chargement Whisper en VRAM...")
        current_whisper = WhisperModel("large-v3", device=DEVICE, compute_type=COMPUTE_TYPE)
    return current_whisper

def load_pyannote():
    """Charge Pyannote avec un patch de sécurité compatible PyTorch 2.6."""
    global current_pipeline
    if current_pipeline is None:
        print("   📥 Chargement Pyannote en VRAM...")
        
        # Patch sécurité
        original_load = torch.load
        def robust_load(*args, **kwargs):
            kwargs["weights_only"] = False
            return original_load(*args, **kwargs)
        torch.load = robust_load
        
        try:
            # --- CORRECTION : use_auth_token -> token ---
            current_pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1", 
                token=HF_TOKEN
            )
            # --------------------------------------------
            current_pipeline.to(torch.device(DEVICE))
        finally:
            torch.load = original_load 
            
    return current_pipeline

def load_embedding_model():
    """Charge WeSpeaker."""
    global current_embedding
    if current_embedding is None:
        print("   📥 Chargement du modèle d'identification (WeSpeaker)...")
        
        original_load = torch.load
        def robust_load(*args, **kwargs):
            kwargs["weights_only"] = False
            return original_load(*args, **kwargs)
        torch.load = robust_load
        
        try:
            # --- CORRECTION : use_auth_token -> token ---
            model = Model.from_pretrained(
                "pyannote/wespeaker-voxceleb-resnet34-LM", 
                token=HF_TOKEN
            )
            # --------------------------------------------
            current_embedding = Inference(model, window="whole")
            current_embedding.to(torch.device(DEVICE))
        finally:
            torch.load = original_load
            
    return current_embedding

def release_models():
    """Vide la VRAM proprement."""
    global current_whisper, current_pipeline, current_embedding
    
    if current_whisper is not None:
        del current_whisper
        current_whisper = None
    
    if current_pipeline is not None:
        del current_pipeline
        current_pipeline = None
    
    if current_embedding is not None:
        del current_embedding
        current_embedding = None
    
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
    
    print("   🧹 VRAM Nettoyée (Modèles déchargés).")