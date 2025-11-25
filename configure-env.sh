#!/bin/bash

# Script para configurar variables de entorno en Cloud Run
# Uso: ./configure-env.sh [project-id] [region] [service-name]

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Parámetros
PROJECT_ID=${1:-"tu-project-id"}
REGION=${2:-"us-west1"}
SERVICE_NAME=${3:-"tareas-back"}

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}  Configure Cloud Run Environment${NC}"
echo -e "${BLUE}========================================${NC}"
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Service: ${SERVICE_NAME}"
echo ""

# Verificar que gcloud esté instalado
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI no está instalado${NC}"
    exit 1
fi

# Configurar proyecto
gcloud config set project ${PROJECT_ID}

echo -e "${YELLOW}⚠️  Este script configurará las variables de entorno necesarias${NC}"
echo ""
echo "Ingresa los valores (presiona Enter para valores por defecto):"
echo ""

# Database
echo -e "${BLUE}=== Database Configuration ===${NC}"
read -p "postgres_user: " POSTGRES_USER
read -sp "postgres_password: " POSTGRES_PASSWORD
echo ""
read -p "postgres_base (host:port/database): " POSTGRES_BASE

# Keycloak
echo -e "\n${BLUE}=== Keycloak Configuration ===${NC}"
read -p "AUTH_URL (e.g., https://keycloak.example.com): " AUTH_URL
read -p "REALM: " REALM
read -p "AUDIENCE: " AUDIENCE

# CORS
echo -e "\n${BLUE}=== CORS Configuration ===${NC}"
read -p "CORS_ORIGINS (comma-separated, e.g., https://frontend.com,http://localhost:5173): " CORS_ORIGINS
CORS_ORIGINS=${CORS_ORIGINS:-"http://localhost:5173,http://localhost:3000"}

# Optional
echo -e "\n${BLUE}=== Optional Configuration ===${NC}"
read -p "LOG_LEVEL (DEBUG/INFO/WARNING/ERROR) [INFO]: " LOG_LEVEL
LOG_LEVEL=${LOG_LEVEL:-"INFO"}

read -p "RUN_DB_SETUP (0/1) [0]: " RUN_DB_SETUP
RUN_DB_SETUP=${RUN_DB_SETUP:-"0"}

read -p "RUN_DB_CREATION (0/1) [0]: " RUN_DB_CREATION
RUN_DB_CREATION=${RUN_DB_CREATION:-"0"}

# Validar campos requeridos
if [ -z "$POSTGRES_USER" ] || [ -z "$POSTGRES_PASSWORD" ] || [ -z "$POSTGRES_BASE" ]; then
    echo -e "\n${RED}❌ Error: Database configuration is required${NC}"
    exit 1
fi

if [ -z "$AUTH_URL" ] || [ -z "$REALM" ] || [ -z "$AUDIENCE" ]; then
    echo -e "\n${RED}❌ Error: Keycloak configuration is required${NC}"
    exit 1
fi

# Confirmar
echo -e "\n${YELLOW}========================================${NC}"
echo -e "${YELLOW}Configuration Summary:${NC}"
echo -e "${YELLOW}========================================${NC}"
echo "Database User: ${POSTGRES_USER}"
echo "Database: ${POSTGRES_BASE}"
echo "Auth URL: ${AUTH_URL}"
echo "Realm: ${REALM}"
echo "Audience: ${AUDIENCE}"
echo "CORS Origins: ${CORS_ORIGINS}"
echo "Log Level: ${LOG_LEVEL}"
echo ""

read -p "Apply these settings? (y/N): " CONFIRM
if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo "Cancelled."
    exit 0
fi

# Aplicar configuración
echo -e "\n${YELLOW}🔧 Updating Cloud Run service...${NC}"

gcloud run services update ${SERVICE_NAME} \
  --region ${REGION} \
  --update-env-vars="postgres_user=${POSTGRES_USER},postgres_password=${POSTGRES_PASSWORD},postgres_base=${POSTGRES_BASE},AUTH_URL=${AUTH_URL},REALM=${REALM},AUDIENCE=${AUDIENCE},CORS_ORIGINS=${CORS_ORIGINS},CORS_ALLOW_CREDENTIALS=true,LOG_LEVEL=${LOG_LEVEL},RUN_DB_SETUP=${RUN_DB_SETUP},RUN_DB_CREATION=${RUN_DB_CREATION}"

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ Environment variables configured successfully!${NC}"
    
    # Obtener URL del servicio
    SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)')
    
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}Service URL: ${SERVICE_URL}${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo "Test endpoints:"
    echo -e "  ${BLUE}curl ${SERVICE_URL}/livez${NC}"
    echo -e "  ${BLUE}curl ${SERVICE_URL}/readyz${NC}"
    echo ""
    echo "View logs:"
    echo -e "  ${BLUE}gcloud run services logs tail ${SERVICE_NAME} --region ${REGION}${NC}"
else
    echo -e "\n${RED}❌ Failed to update environment variables${NC}"
    exit 1
fi
