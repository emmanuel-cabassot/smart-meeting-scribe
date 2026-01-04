from fastapi import FastAPI, UploadFile, File, HTTPException
import whisper
import torch
import shutil
import os

app = FastAPI(title="Smart Meeting Scribe")

# Variable globale pour savoir quel modèle est réellement chargé
LOADED_MODEL_NAME = "Inconnu"

# --- 1. CONFIGURATION MATÉRIELLE (Au démarrage) ---
print("⏳ Initialisation du système...")

# On vérifie si la RTX est bien là
if torch.cuda.is_available():
    DEVICE = "cuda"
    GPU_NAME = torch.cuda.get_device_name(0)
    print(f"🚀 GPU Détecté : {GPU_NAME}")
else:
    DEVICE = "cpu"
    print("⚠️ GPU non détecté, passage en mode CPU (Lent).")

# --- 2. CHARGEMENT DU MODÈLE (Une seule fois !) ---
# On charge le modèle au niveau global pour qu'il reste en mémoire RAM/VRAM
try:
    print(f"⏳ Tentative de chargement du modèle Whisper TURBO sur {DEVICE}...")
    model = whisper.load_model("turbo", device=DEVICE)
    LOADED_MODEL_NAME = "turbo"
    print("✅ Modèle TURBO chargé et prêt !")

except Exception as e:
    print(f"⚠️ Le modèle 'turbo' n'a pas pu être chargé (Erreur: {e})")
    print("🔄 Bascule automatique sur le modèle 'medium' (Valeur sûre)...")
    
    try:
        # Fallback : Medium est un excellent compromis pour une RTX 30xx/40xx
        model = whisper.load_model("medium", device=DEVICE)
        LOADED_MODEL_NAME = "medium"
        print("✅ Modèle MEDIUM chargé (Mode de secours activé) !")
    except Exception as e2:
        print(f"❌ Erreur critique : Impossible de charger un modèle. {e2}")
        raise e2


# --- 3. LES ROUTES API ---

@app.get("/")
def read_root():
    """Route de santé pour vérifier que l'API tourne"""
    return {
        "status": "Smart Meeting Scribe Ready", 
        "device": DEVICE,
        "model_loaded": LOADED_MODEL_NAME
    }

@app.get("/gpu-check")
def check_gpu():
    """Vérifie l'état de la carte graphique et de la mémoire"""
    try:
        gpu_stats = {
            "available": torch.cuda.is_available(),
            "device_count": torch.cuda.device_count(),
            "current_device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU",
            "active_model": LOADED_MODEL_NAME
        }
        return gpu_stats
    except Exception as e:
        return {"error": str(e)}

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Endpoint principal : Reçoit un fichier audio -> Renvoie le texte.
    """
    
    # 1. Sauvegarde temporaire du fichier reçu
    # On nettoie le nom de fichier pour éviter les bugs d'accents/espaces
    clean_name = "".join(x for x in file.filename if x.isalnum() or x in "._-")
    temp_filename = f"temp_{clean_name}"
    
    try:
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 2. Transcription
        print(f"🎙️ Traitement de {file.filename} avec le modèle {LOADED_MODEL_NAME}...")
        
        # L'appel magique à Whisper
        # Tu peux ajouter initial_prompt="Compte rendu de réunion" pour aider l'IA
        result = model.transcribe(temp_filename)
        
        print("✅ Transcription terminée.")
        
        return {
            "filename": file.filename,
            "language_detected": result["language"],
            "text": result["text"].strip()
        }

    except Exception as e:
        print(f"❌ Erreur pendant la transcription : {e}")
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        # 3. Nettoyage (Toujours supprimer le fichier temp, même si ça plante)
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
            print(f"🧹 Fichier temporaire supprimé.")