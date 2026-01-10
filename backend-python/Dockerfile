# On utilise l'image officielle NVIDIA CUDA (Compatible RTX 4070)
FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04

# Variables d'environnement pour Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

# 1. Installation des dépendances système
# Ajout de 'pkg-config', 'gcc' et des lib de dev FFmpeg pour que PyAV puisse compiler
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    ffmpeg \
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

# 3. Copie des fichiers de dépendances
COPY requirements.txt .

# 4. Mise à jour de pip et installation des requirements
# On upgrade pip pour éviter les soucis de wheel
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

# 5. Copie du code source
COPY app ./app

# Note: La commande de lancement est définie dans docker-compose.yml