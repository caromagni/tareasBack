#!/bin/bash
# Script para configurar variables de entorno en Cloud Run
# Uso: ./set-env-vars.sh

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Configurando variables de entorno en Cloud Run...${NC}"

# Configuración del proyecto y región
PROJECT_ID="eng-scene-478112-k0"  # Tu project ID actual
REGION="us-west1"
SERVICE_NAME="tareas-back"

echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"
echo ""

# Actualizar variables de entorno
gcloud run services update $SERVICE_NAME \
  --region=$REGION \
  --project=$PROJECT_ID \
  --update-env-vars="
ALLOWED_ORIGINS=https://tu-frontend.run.app,http://localhost:3000,http://localhost:5173,
AUTH_URL=https://tu-keycloak.com/auth,
REALM=tu-realm,
AUDIENCE=tu-audience,
postgres_user=tu_usuario,
postgres_password=tu_password,
postgres_base=tu_conexion_postgresql,
redis_host=localhost,
redis_port=6379,
redis_password=,
redis_user=default,
redis_db=0,
redis_uses_password=False,
cache_enabled=False,
RABBITMQ_USER=guest,
RABBITMQ_PASSWORD=guest,
RABBITMQ_HOST=localhost,
RABBITMQ_PORT=5672,
RABBITMQ_VHOST=/,
RABBITMQ_QUEUE_NAME=tareas_queue,
RUN_DB_SETUP=0,
RUN_DB_CREATION=0,
SQLALCHEMY_POOL_SIZE=5,
MAX_ITEMS_PER_RESPONSE=100,
LOG_LEVEL=INFO,
ALL_USERS_SUPERADMIN=0,
SWAGGER_VERSION=5.27.0
"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Variables de entorno configuradas exitosamente${NC}"
    echo ""
    echo "Verifica las variables con:"
    echo "gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(spec.template.spec.containers[0].env)'"
else
    echo "Error al configurar variables de entorno"
    exit 1
fi
