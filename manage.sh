#!/bin/bash
# ============================================================================
# Smart Meeting Scribe - Script de gestion
# ============================================================================

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m'

# Répertoire racine du projet
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ============================================================================
# COMMANDES
# ============================================================================

case "$1" in
  start)
    echo -e "${BLUE}🚀 Démarrage de tous les services...${NC}"
    docker compose -f "$PROJECT_ROOT/01-core/docker-compose.yml" up -d
    docker compose -f "$PROJECT_ROOT/02-workers/docker-compose.yml" up -d
    docker compose -f "$PROJECT_ROOT/03-interface/docker-compose.yml" up -d
    echo -e "${GREEN}✅ Tous les services sont démarrés.${NC}"
    ;;
    
  stop)
    echo -e "${RED}🛑 Arrêt de tous les services...${NC}"
    docker compose -f "$PROJECT_ROOT/03-interface/docker-compose.yml" down
    docker compose -f "$PROJECT_ROOT/02-workers/docker-compose.yml" down
    docker compose -f "$PROJECT_ROOT/01-core/docker-compose.yml" down
    echo -e "${GREEN}✅ Tous les services sont arrêtés.${NC}"
    ;;
    
  restart)
    echo -e "${YELLOW}🔄 Redémarrage de tous les services...${NC}"
    $0 stop
    $0 start
    ;;
    
  logs)
    SERVICE=${2:-sms_api}
    echo -e "${BLUE}📋 Logs du service $SERVICE...${NC}"
    docker logs -f "$SERVICE"
    ;;
    
  reset-db)
    echo -e "${RED}⚠️  ATTENTION: Cette commande va SUPPRIMER toutes les données PostgreSQL !${NC}"
    read -p "Êtes-vous sûr ? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      echo -e "${RED}🧹 Arrêt des services...${NC}"
      docker compose -f "$PROJECT_ROOT/03-interface/docker-compose.yml" down
      docker compose -f "$PROJECT_ROOT/01-core/docker-compose.yml" down
      
      echo -e "${RED}🗑️  Suppression des données PostgreSQL...${NC}"
      sudo rm -rf "$PROJECT_ROOT/volumes/postgres_data"
      mkdir -p "$PROJECT_ROOT/volumes/postgres_data"
      
      echo -e "${BLUE}🚀 Redémarrage des services...${NC}"
      docker compose -f "$PROJECT_ROOT/01-core/docker-compose.yml" up -d
      sleep 5
      docker compose -f "$PROJECT_ROOT/03-interface/docker-compose.yml" up -d
      
      echo -e "${GREEN}✅ Base de données réinitialisée !${NC}"
      docker logs sms_api -f
    else
      echo -e "${YELLOW}Opération annulée.${NC}"
    fi
    ;;
    
  rebuild)
    SERVICE=${2:-backend}
    echo -e "${BLUE}🔨 Rebuild du service $SERVICE...${NC}"
    docker compose -f "$PROJECT_ROOT/03-interface/docker-compose.yml" build "$SERVICE" --no-cache
    docker compose -f "$PROJECT_ROOT/03-interface/docker-compose.yml" up -d "$SERVICE"
    echo -e "${GREEN}✅ Service $SERVICE reconstruit.${NC}"
    ;;
    
  status)
    echo -e "${BLUE}📊 État des services...${NC}"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    ;;
    
  clean)
    echo -e "${RED}🧹 Nettoyage complet (containers + volumes + images)...${NC}"
    docker compose -f "$PROJECT_ROOT/03-interface/docker-compose.yml" down -v
    docker compose -f "$PROJECT_ROOT/02-workers/docker-compose.yml" down -v
    docker compose -f "$PROJECT_ROOT/01-core/docker-compose.yml" down -v
    docker builder prune -f
    echo -e "${GREEN}✅ Nettoyage terminé.${NC}"
    ;;
    
  *)
    echo -e "${BLUE}Smart Meeting Scribe - Commandes disponibles:${NC}"
    echo ""
    echo "  ./manage.sh start       - Démarrer tous les services"
    echo "  ./manage.sh stop        - Arrêter tous les services"
    echo "  ./manage.sh restart     - Redémarrer tous les services"
    echo "  ./manage.sh logs [svc]  - Voir les logs (défaut: sms_api)"
    echo "  ./manage.sh status      - État des services Docker"
    echo ""
    echo -e "${YELLOW}Commandes de développement:${NC}"
    echo "  ./manage.sh reset-db    - Réinitialiser la base de données"
    echo "  ./manage.sh rebuild     - Reconstruire l'image backend"
    echo "  ./manage.sh clean       - Nettoyage complet (⚠️  destructif)"
    echo ""
    ;;
esac
