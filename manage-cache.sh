#!/bin/bash
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${RED}🧹 1. Arrêt et Nettoyage complet (Containers + Volumes)...${NC}"
# On arrête tout pour éviter les conflits
docker compose -f 01-core/docker-compose.yml down -v
docker compose -f 02-workers/docker-compose.yml down -v
docker compose -f 03-interface/docker-compose.yml down -v

echo -e "${YELLOW}🏗️  2. Reconstruction FORCÉE (NO-CACHE)...${NC}"
echo -e "${YELLOW}   (Cela va prendre du temps car on retélécharge toutes les libs Python)${NC}"

# C'est ici que la magie opère : --no-cache force la réinstallation des requirements.txt
docker compose -f 02-workers/docker-compose.yml build --no-cache
docker compose -f 03-interface/docker-compose.yml build --no-cache

echo -e "${BLUE}🚀 3. Lancement des stacks...${NC}"
# Core (Base de données - Pas besoin de rebuild no-cache souvent)
docker compose -f 01-core/docker-compose.yml --env-file .env up -d

# Workers (Avec la nouvelle image fraîchement construite)
docker compose -f 02-workers/docker-compose.yml --env-file .env up -d

# Interface (Avec la nouvelle image)
docker compose -f 03-interface/docker-compose.yml --env-file .env up -d

echo -e "${GREEN}✅ 4. Tout est en ligne avec les nouvelles dépendances !${NC}"
echo -e "${BLUE}📜 Connexion aux logs du Worker (Pour vérifier le chargement V5.3)...${NC}"

# On regarde les logs du worker (c'est là qu'on veut voir "Whisper Turbo")
docker logs -f smart-meeting-scribe-master-worker-1