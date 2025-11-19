#!/bin/bash

# Script para construir y desplegar a Cloud Run
# Uso: ./deploy-cloudrun.sh [project-id] [region] [service-name]

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parámetros
PROJECT_ID=${1:-"tu-project-id"}
REGION=${2:-"us-central1"}
SERVICE_NAME=${3:-"tareas-backend"}
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo -e "${GREEN}=== Deploy to Cloud Run ===${NC}"
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Service: ${SERVICE_NAME}"
echo "Image: ${IMAGE_NAME}"
echo ""

# Verificar que gcloud esté instalado
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI no está instalado${NC}"
    exit 1
fi

# Configurar proyecto
echo -e "${YELLOW}Configurando proyecto...${NC}"
gcloud config set project ${PROJECT_ID}

# Build de la imagen
echo -e "${YELLOW}Construyendo imagen Docker...${NC}"
docker build --platform linux/amd64 -t ${IMAGE_NAME}:latest -f Dockerfile .

# Push de la imagen
echo -e "${YELLOW}Subiendo imagen a Container Registry...${NC}"
docker push ${IMAGE_NAME}:latest

# Desplegar a Cloud Run
echo -e "${YELLOW}Desplegando a Cloud Run...${NC}"
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME}:latest \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --port 5000 \
  --cpu 1 \
  --memory 512Mi \
  --min-instances 0 \
  --max-instances 10 \
  --timeout 300 \
  --set-env-vars="CORS_ORIGINS=https://tu-frontend.com,http://localhost:5173" \
  --set-env-vars="CORS_ALLOW_CREDENTIALS=true"

# Obtener URL del servicio
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)')

echo ""
echo -e "${GREEN}=== Despliegue completado ===${NC}"
echo -e "URL del servicio: ${GREEN}${SERVICE_URL}${NC}"
echo ""
echo -e "${YELLOW}Próximos pasos:${NC}"
echo "1. Actualiza la variable CORS_ORIGINS con la URL de tu frontend"
echo "2. Configura el resto de variables de entorno necesarias"
echo "3. Prueba los endpoints:"
echo "   curl ${SERVICE_URL}/readyz"
echo "   curl ${SERVICE_URL}/livez"
echo ""
echo "Para actualizar variables de entorno:"
echo "gcloud run services update ${SERVICE_NAME} --region ${REGION} --set-env-vars='VARIABLE=valor'"
