# 1. Image de base (CUDA 12.4 = Stable)
FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04

# 2. Outils système
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# 3. Dossier de travail
WORKDIR /app

# 4. Installation des dépendances
COPY requirements.txt .
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

# --- 🛠️ LA SOLUTION "EN DUR" 🛠️ ---
# On sait que c'est Python 3.10. On écrit le chemin directement.
# On pointe vers les dossiers où pip a installé les drivers NVIDIA.
ENV LD_LIBRARY_PATH=/usr/local/lib/python3.10/dist-packages/nvidia/cudnn/lib:/usr/local/lib/python3.10/dist-packages/nvidia/cublas/lib:$LD_LIBRARY_PATH
# -----------------------------------

# 5. Copie du code
COPY . .

# 6. Lancement direct (Plus de script intermédiaire)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]