from faster_whisper import WhisperModel
from pyannote.audio import Pipeline
import torch
import gc
from core.config import DEVICE, COMPUTE_TYPE

# Variables globales initialisées à None (chargement à la demande)
current_whisper = None
current_pipeline = None

def load_whisper():
    """Charge Whisper uniquement s'il n'est pas déjà là."""
    global current_whisper
    if current_whisper is None:
        print("   📥 Chargement Whisper en VRAM...")
        current_whisper = WhisperModel("large-v3", device=DEVICE, compute_type=COMPUTE_TYPE)
    return current_whisper

def load_pyannote():
    """Charge Pyannote uniquement s'il n'est pas déjà là."""
    global current_pipeline
    if current_pipeline is None:
        print("   📥 Chargement Pyannote en VRAM...")
        
        # --- PATCH SECURITE ---
        original_torch_load = torch.load
        def patched_torch_load(*args, **kwargs):
            kwargs["weights_only"] = False 
            return original_torch_load(*args, **kwargs)
        torch.load = patched_torch_load
        
        # Chargement
        current_pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1")
        current_pipeline.to(torch.device(DEVICE))
        
        # Restauration
        torch.load = original_torch_load
        
    return current_pipeline

def release_models():
    """Vide la VRAM violemment."""
    global current_whisper, current_pipeline
    
    # On supprime les références Python
    if current_whisper is not None:
        del current_whisper
        current_whisper = None
    
    if current_pipeline is not None:
        del current_pipeline
        current_pipeline = None
    
    # On force le Garbage Collector
    gc.collect()
    
    # On vide le cache CUDA
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
    
    print("   🧹 VRAM Nettoyée (Modèles déchargés).")

print("⚙️ Mode VRAM Économique activé (chargement à la demande)")
