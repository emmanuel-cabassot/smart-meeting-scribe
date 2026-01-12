# ==============================================================================
# WORKER V5 - GPU AUDIO PROCESSING
# ==============================================================================
# On utilise l'image officielle NVIDIA CUDA 12.4 (Compatible RTX 4070)
FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04

# Variables d'environnement pour Python (Logs immédiats, pas de cache .pyc)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

# 1. Installation des dépendances système (FFmpeg est critique pour l'audio)
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    ffmpeg \
    # Libs nécessaires pour compiler certaines dépendances audio
    pkg-config \
    libavformat-dev \
    libavcodec-dev \
    libavdevice-dev \
    libavutil-dev \
    libswscale-dev \
    libswresample-dev \
    libavfilter-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 2. Configuration du dossier de travail
WORKDIR /code

# 3. Installation des dépendances Python
# On copie d'abord le requirements.txt pour profiter du cache Docker
COPY requirements.txt .
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

# 4. Copie du code source du Worker
COPY app ./app

# 5. Commande de démarrage par défaut
# Lance le Worker Taskiq qui écoute Redis
CMD ["taskiq", "worker", "app.broker:broker", "--fs-discover", "--workers", "1"]