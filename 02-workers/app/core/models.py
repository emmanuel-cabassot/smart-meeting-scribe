"""
Gestionnaire de modèles IA (Cycle de vie & VRAM).
"""
from faster_whisper import WhisperModel
from pyannote.audio import Pipeline, Model, Inference
import torch
import gc
from app.core.config import DEVICE, COMPUTE_TYPE, HF_TOKEN

# Variables globales (Singletons)
current_whisper = None
current_pipeline = None
current_embedding = None

# ID Spécifique pour Whisper Turbo optimisé CTranslate2 (Gain VRAM ~1.5GB)
WHISPER_MODEL_ID = "deepdml/faster-whisper-large-v3-turbo-ct2"

# ══════════════════════════════════════════════════════════════════════════════
# UTILITAIRE VRAM
# ══════════════════════════════════════════════════════════════════════════════
def log_vram(action: str, model_name: str):
    """Affiche l'état de la mémoire GPU."""
    if torch.cuda.is_available():
        free_mem, total_mem = torch.cuda.mem_get_info()
        free_gb = free_mem / 1024**3
        total_gb = total_mem / 1024**3
        used_gb = total_gb - free_gb
        print(f"   💾 [VRAM] {action} {model_name} | Occupé: {used_gb:.2f}GB / {total_gb:.2f}GB (Libre: {free_gb:.2f}GB)")
    else:
        print(f"   💻 [CPU] {action} {model_name}")

# ══════════════════════════════════════════════════════════════════════════════
# CHARGEMENT DES MODÈLES
# ══════════════════════════════════════════════════════════════════════════════

def load_whisper():
    global current_whisper
    if current_whisper is None:
        print(f"   ⏳ Initialisation du chargement de Whisper Turbo ({WHISPER_MODEL_ID}) en {COMPUTE_TYPE}...")
        # On charge le modèle Turbo optimisé (CTranslate2)
        # Note : compute_type="int8" est recommandé pour maximiser le gain VRAM sur la RTX 4070
        current_whisper = WhisperModel(
            WHISPER_MODEL_ID, 
            device=DEVICE, 
            compute_type=COMPUTE_TYPE
        )
        # On loggue l'état APRÈS le chargement pour voir le poids réel
        log_vram("✅ Modèle Chargé :", "Whisper Large-v3-Turbo")
    return current_whisper

def load_pyannote():
    """Charge Pyannote avec un patch de sécurité compatible PyTorch 2.6."""
    global current_pipeline
    if current_pipeline is None:
        print("   ⏳ Initialisation du chargement de Pyannote (Segmentation)...")
        
        # Patch sécurité pour torch.load
        original_load = torch.load
        def robust_load(*args, **kwargs):
            kwargs["weights_only"] = False
            return original_load(*args, **kwargs)
        torch.load = robust_load
        
        try:
            current_pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1", 
                token=HF_TOKEN
            )
            current_pipeline.to(torch.device(DEVICE))
            # On loggue l'état APRÈS l'envoi sur le GPU
            log_vram("✅ Modèle Chargé :", "Pyannote Diarization")
        finally:
            torch.load = original_load 
            
    return current_pipeline

def load_embedding_model():
    """Charge WeSpeaker (Natif Pyannote)."""
    global current_embedding
    if current_embedding is None:
        print("   ⏳ Initialisation du chargement de WeSpeaker (Identification)...")
        
        original_load = torch.load
        def robust_load(*args, **kwargs):
            kwargs["weights_only"] = False
            return original_load(*args, **kwargs)
        torch.load = robust_load
        
        try:
            model = Model.from_pretrained(
                "pyannote/wespeaker-voxceleb-resnet34-LM", 
                token=HF_TOKEN
            )
            current_embedding = Inference(model, window="whole")
            current_embedding.to(torch.device(DEVICE))
            # On loggue l'état APRÈS l'envoi sur le GPU
            log_vram("✅ Modèle Chargé :", "WeSpeaker (ResNet34)")
        finally:
            torch.load = original_load
            
    return current_embedding

# ══════════════════════════════════════════════════════════════════════════════
# NETTOYAGE
# ══════════════════════════════════════════════════════════════════════════════

def release_models():
    """Vide la VRAM proprement et loggue ce qui a été libéré."""
    global current_whisper, current_pipeline, current_embedding
    
    freed_models = []
    
    if current_whisper is not None:
        del current_whisper
        current_whisper = None
        freed_models.append("Whisper Turbo")
    
    if current_pipeline is not None:
        del current_pipeline
        current_pipeline = None
        freed_models.append("Pyannote")
    
    if current_embedding is not None:
        del current_embedding
        current_embedding = None
        freed_models.append("WeSpeaker")
    
    # Garbage Collection
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
    
    # Log si quelque chose a été libéré
    if freed_models:
        print(f"   🧹 [NETTOYAGE] Modèles déchargés : {', '.join(freed_models)}")
        if torch.cuda.is_available():
            free_mem, total_mem = torch.cuda.mem_get_info()
            # On affiche combien on a récupéré
            print(f"        ↳ VRAM Libre maintenant : {free_mem / 1024**3:.2f} GB / {total_mem / 1024**3:.2f} GB")