from fastapi import FastAPI
import torch
import os

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "online", "service": "Backend IA"}

@app.get("/gpu-check")
def check_gpu():
    """Diagnostic complet du GPU vu depuis le conteneur"""
    try:
        is_cuda = torch.cuda.is_available()
        return {
            "cuda_available": is_cuda,
            "device_count": torch.cuda.device_count(),
            "current_device": torch.cuda.get_device_name(0) if is_cuda else "None",
            "cuda_version_torch": torch.version.cuda,
            # On vérifie si le driver Nvidia est visible
            "driver_version": os.popen('nvidia-smi --query-gpu=driver_version --format=csv,noheader').read().strip()
        }
    except Exception as e:
        return {"error": str(e)}