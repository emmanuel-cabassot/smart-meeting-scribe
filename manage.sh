#!/bin/bash
GREEN='\033[0,32m'
BLUE='\033[0,34m'
RED='\033[0,31m'
NC='\033[0m'

echo -e "${RED}🧹 1. Nettoyage des containers et volumes...${NC}"
docker compose -f 01-core/docker-compose.yml down -v
docker compose -f 02-workers/docker-compose.yml down -v
docker compose -f 03-interface/docker-compose.yml down -v

echo -e "${BLUE}🚀 2. Lancement synchronisé des stacks...${NC}"
docker compose -f 01-core/docker-compose.yml --env-file .env up -d
docker compose -f 02-workers/docker-compose.yml --env-file .env up -d
docker compose -f 03-interface/docker-compose.yml --env-file .env up -d --build

echo -e "${GREEN}✅ 3. Tout est en ligne. Connexion aux logs de l'API...${NC}"
docker logs -f sms_api
