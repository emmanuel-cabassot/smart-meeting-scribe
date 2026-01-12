# 📑 Docker Cheat Sheet — Smart Meeting Scribe V5

## 🏗️ Services & Conteneurs Clés

| Service | Nom du conteneur | Port |
|---------|------------------|------|
| API (FastAPI) | `sms_api` | 5000 |
| Worker (IA) | `sms_worker` | - |
| Frontend | `sms_frontend` | 3000 |
| Base de données | `sms_postgres` | 5432 |
| Stockage S3 | `sms_minio` | 9001 (Console) |

---

## � Commandes "Master" (Le raccourci V5)

Utilise le script à la racine pour un cycle propre (Clean -> Build -> Start -> Logs).

```bash
./manage.sh
```

---

## 🟢 Démarrage & Mise à jour (Manuel)

Si tu veux lancer une stack spécifique sans tout couper :

```bash
# Lancer l'interface et reconstruire
docker compose -f 03-interface/docker-compose.yml --env-file .env up -d --build
```

---

## 🟡 Arrêt & Nettoyage

```bash
# Arrêter proprement la stack interface
docker compose -f 03-interface/docker-compose.yml down

# Arrêt total avec suppression des images locales et des volumes (Reset)
docker compose -f 03-interface/docker-compose.yml down -v --rmi local
```

---

## 🟣 Surveillance (Logs)

```bash
# Voir les logs de l'API en temps réel
docker logs -f sms_api

# Voir les logs du Worker (IA) pour suivre la transcription
docker logs -f sms_worker
```

---

## 🟨 Exécution (Shell interne)

Entrer dans le conteneur pour inspecter les fichiers ou tester du code Python :

```bash
# Dans l'API
docker exec -it sms_api /bin/bash

# Dans le Worker
docker exec -it sms_worker /bin/bash
```

---

## � Inspection du Système

```bash
# Voir les conteneurs actifs (Ports, Status)
docker ps

# Voir tous les conteneurs (même arrêtés)
docker ps -a

# Voir les images stockées
docker images

# Voir l'utilisation des ressources (CPU/RAM/GPU)
docker stats
```

---

## 🧹 Maintenance Rapide

```bash
# Nettoyer les conteneurs arrêtés et images orphelines
docker system prune -f

# Nettoyer TOUT (y compris les volumes non utilisés - Attention !)
docker system prune -a --volumes
```

---

## � Rappel Utile

Pour le GPU, comme tu utilises `nvidia-smi` à l'intérieur du worker, tu peux tester la visibilité du GPU directement avec :

```bash
docker exec -it sms_worker nvidia-smi
```
