# 1. On part de l'image Runtime NVIDIA (Note le 12.6.3) pour la trouver aller sur docker hub et choisir la version qui vous correspond https://hub.docker.com/r/nvidia/cuda/tags
FROM nvidia/cuda:12.6.3-cudnn-runtime-ubuntu22.04

# 2. Variables d'environnement pour Python
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 3. Installation des dépendances système
# ffmpeg est ajouté en prévision de l'audio, curl pour la santé du conteneur
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    ffmpeg \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 4. Installation de PyTorch (Optimisé pour CUDA 12.6)
# On force l'index-url pour ne pas télécharger la version CPU par défaut aller voir sur le site de PyTorch pour trouver le bon index-url : https://pytorch.org/get-started/locally/
RUN pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu126

# 5. DÉPENDANCES PYTHON 
# Crée le dossier /app et se place dedans (équivalent à mkdir + cd mais dans notre conteneur Docker)
WORKDIR /app
# On copie d'abord les requirements pour optimiser le cache Docker
COPY requirements.txt .
# --no-cache-dir réduit la taille de l'image finale
RUN pip3 install --no-cache-dir -r requirements.txt

# 6. On copie le code
COPY main.py .

# 7. Lancement
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]