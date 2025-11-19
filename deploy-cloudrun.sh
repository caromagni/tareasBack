#!/bin/bash

# Script para construir y desplegar a Cloud Run
# Uso: ./deploy-cloudrun.sh [project-id] [region] [service-name]

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parámetros
PROJECT_ID=${1:-"tu-project-id"}
REGION=${2:-"us-west1"}
SERVICE_NAME=${3:-"tareas-back"}
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}    Deploy to Cloud Run${NC}"
echo -e "${BLUE}========================================${NC}"
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Service: ${SERVICE_NAME}"
echo "Image: ${IMAGE_NAME}:latest"
echo ""

# Verificar que gcloud esté instalado
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI no está instalado${NC}"
    echo "Instala: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Verificar que docker esté instalado
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker no está instalado${NC}"
    exit 1
fi

# Configurar proyecto
echo -e "${YELLOW}📋 Configurando proyecto...${NC}"
gcloud config set project ${PROJECT_ID}

# Autenticar Docker con GCR
echo -e "${YELLOW}🔐 Autenticando Docker...${NC}"
gcloud auth configure-docker --quiet

# Build de la imagen
echo -e "${YELLOW}🔨 Construyendo imagen Docker...${NC}"
echo "   Esto puede tomar 5-10 minutos..."
docker build --platform linux/amd64 -t ${IMAGE_NAME}:latest -f Dockerfile .

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Error al construir la imagen${NC}"
    echo "Revisa el Dockerfile y los errores anteriores"
    exit 1
fi

echo -e "${GREEN}✅ Imagen construida exitosamente${NC}"

# Push de la imagen
echo -e "${YELLOW}⬆️  Subiendo imagen a Container Registry...${NC}"
docker push ${IMAGE_NAME}:latest

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Error al subir la imagen${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Imagen subida exitosamente${NC}"

# Desplegar a Cloud Run
echo -e "${YELLOW}🚀 Desplegando a Cloud Run...${NC}"
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

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Error al desplegar en Cloud Run${NC}"
    exit 1
fi

# Obtener URL del servicio
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)')

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ Despliegue completado exitosamente${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}URL del servicio:${NC} ${SERVICE_URL}"
echo ""
echo -e "${YELLOW}⚠️  Próximos pasos importantes:${NC}"
echo ""
echo "1. 🔧 Actualiza CORS_ORIGINS con tu frontend real:"
echo -e "   ${BLUE}gcloud run services update ${SERVICE_NAME} --region ${REGION} \\${NC}"
echo -e "   ${BLUE}  --update-env-vars='CORS_ORIGINS=https://tu-frontend-real.com'${NC}"
echo ""
echo "2. 🗄️  Configura variables de base de datos:"
echo -e "   ${BLUE}gcloud run services update ${SERVICE_NAME} --region ${REGION} \\${NC}"
echo -e "   ${BLUE}  --set-env-vars='postgres_user=USER,postgres_password=PASS,postgres_base=HOST:PORT/DB'${NC}"
echo ""
echo "3. 🧪 Prueba los endpoints:"
echo -e "   ${BLUE}curl ${SERVICE_URL}/livez${NC}"
echo -e "   ${BLUE}curl ${SERVICE_URL}/readyz${NC}"
echo ""
echo "4. 🔍 Test CORS:"
echo -e "   ${BLUE}./test-cors.sh ${SERVICE_URL} https://tu-frontend.com${NC}"
echo ""
echo "5. 📊 Ver logs:"
echo -e "   ${BLUE}gcloud run services logs tail ${SERVICE_NAME} --region ${REGION}${NC}"
echo ""
