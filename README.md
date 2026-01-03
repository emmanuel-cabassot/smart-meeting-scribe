# 🧠 AI-Stack-Starter : Base Architecture for Local AI

![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![NVIDIA](https://img.shields.io/badge/nVIDIA-%2376B900.svg?style=for-the-badge&logo=nvidia&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![PyTorch](https://img.shields.io/badge/PyTorch-%23EE4C2C.svg?style=for-the-badge&logo=PyTorch&logoColor=white)

Ce dépôt est un **modèle d'architecture (Template)** pour développer des applications d'Intelligence Artificielle professionnelles en local (On-Premise).

Il met en œuvre une politique **"Clean Host"** : toute la stack IA est isolée dans des conteneurs Docker, avec un accès direct au GPU via le NVIDIA Container Toolkit.

## 🏗️ Architecture Technique

* **Philosophie :** "Clean Host" (Aucune pollution de la machine hôte, tout est isolé dans Docker).
* **Hôte requis :** Linux (Ubuntu recommandé) + Drivers NVIDIA uniquement.
* **Virtualisation :** Docker + Docker Compose.
* **Backend IA :** Python 3.10+, FastAPI.
* **Accélération :** CUDA 12.6 + PyTorch (Optimisé pour RTX 30xx/40xx).

### Structure des dossiers
.
├── docker-compose.yml       # Orchestration des services et du GPU
├── README.md                # Documentation
└── backend-python/          # Microservice IA
    ├── Dockerfile           # Définition de l'environnement (System layer)
    ├── requirements.txt     # Dépendances Python (App layer)
    └── main.py              # Point d'entrée de l'API

## 📋 Pré-requis (Sur la machine hôte)
- Drivers NVIDIA installés et fonctionnels (nvidia-smi doit renvoyer un résultat).

- Docker Engine & Docker Compose.

- NVIDIA Container Toolkit configuré.

## 🚀 Installation & Démarrage
1. Cloner le projet

2. Lancer la stack
```bash
docker compose up -d --build
```

3. Vérifier l'accès GPU
```bash
# Via le terminal
curl http://localhost:5000/gpu-check

# Ou via le navigateur
# http://localhost:5000/gpu-check
```


Réponse attendue :
```json
{
    "cuda_available": true,
    "device_count": 1,
    "current_device": "NVIDIA GeForce RTX 4090",
    "cuda_version_torch": "12.6.1",
    "driver_version": "535.124.06"
}
``` 

## 🔧 Personnalisation

### Ajouter une librairie Python
Ajouter la ligne dans backend-python/requirements.txt.

Relancer avec docker compose up -d --build.

### Changer de port
Si le port 5000 est occupé sur votre machine, modifiez le fichier docker-compose.yml :
```yaml
ports:
  - "NOUVEAU_PORT:8000"
```



