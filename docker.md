# 📑 Commandes Docker — Cheat Sheet

## nom du conteneur
backend-python

## 🟢 Démarrer (ou Mettre à jour)
Construit l'image et lance tous les services en arrière-plan.

docker compose up -d --build

## 🟡 Arrêter
Arrête tous les services.

docker compose down --rmi local   

## 🟣 Voir les logs
docker compose logs -f backend-python

## ✅ Tester le GPU
curl http://localhost:5000/gpu-check

## 🧹 Nettoyage Rapide
docker system prune -f

## 🟤 Mettre à jour
docker compose up -d --build

## 🟨 Executer ligne de commande dans le conteneur backend-python
docker exec -it backend-python /bin/bash

## 🟥 Voir les images
docker images

## 🟦 Voir les conteneurs
docker ps

## 🟧 Voir les conteneurs (tous)
docker ps -a

