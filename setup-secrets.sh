#!/bin/bash
# Script para crear secrets en Google Secret Manager
# Uso: ./setup-secrets.sh

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_ID="eng-scene-478112-k0"
REGION="us-west1"
SERVICE_NAME="tareas-back"

echo -e "${YELLOW}=== Configuración de Secrets en Google Secret Manager ===${NC}"
echo ""
echo "Project ID: $PROJECT_ID"
echo ""

# Función para crear secret
create_secret() {
    local secret_name=$1
    local secret_value=$2
    
    echo -e "${YELLOW}Creando secret: ${secret_name}${NC}"
    
    # Check if secret exists
    if gcloud secrets describe $secret_name --project=$PROJECT_ID &>/dev/null; then
        echo "Secret $secret_name ya existe. Agregando nueva versión..."
        echo -n "$secret_value" | gcloud secrets versions add $secret_name \
            --data-file=- \
            --project=$PROJECT_ID
    else
        echo "Creando nuevo secret $secret_name..."
        echo -n "$secret_value" | gcloud secrets create $secret_name \
            --data-file=- \
            --replication-policy="automatic" \
            --project=$PROJECT_ID
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Secret $secret_name creado/actualizado${NC}"
    else
        echo -e "${RED}✗ Error creando secret $secret_name${NC}"
        return 1
    fi
    echo ""
}

# Función para dar acceso al Cloud Run service account
grant_secret_access() {
    local secret_name=$1
    
    echo -e "${YELLOW}Otorgando acceso al secret $secret_name...${NC}"
    
    # Get the Cloud Run service account
    SERVICE_ACCOUNT="$PROJECT_ID@appspot.gserviceaccount.com"
    
    gcloud secrets add-iam-policy-binding $secret_name \
        --member="serviceAccount:$SERVICE_ACCOUNT" \
        --role="roles/secretmanager.secretAccessor" \
        --project=$PROJECT_ID
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Acceso otorgado${NC}"
    fi
    echo ""
}

echo -e "${YELLOW}IMPORTANTE: Este script te pedirá los valores sensibles${NC}"
echo "Los valores NO se mostrarán en pantalla mientras los escribes"
echo ""

# Database credentials
echo -e "${YELLOW}=== Configuración de Base de Datos ===${NC}"
read -p "PostgreSQL User: " POSTGRES_USER
read -sp "PostgreSQL Password: " POSTGRES_PASSWORD
echo ""
read -p "PostgreSQL Base (connection string): " POSTGRES_BASE
echo ""

create_secret "postgres-user" "$POSTGRES_USER"
grant_secret_access "postgres-user"

create_secret "postgres-password" "$POSTGRES_PASSWORD"
grant_secret_access "postgres-password"

create_secret "postgres-base" "$POSTGRES_BASE"
grant_secret_access "postgres-base"

# Auth credentials
echo -e "${YELLOW}=== Configuración de Autenticación ===${NC}"
read -p "AUTH_URL: " AUTH_URL
read -p "REALM: " REALM
read -p "AUDIENCE: " AUDIENCE
echo ""

create_secret "auth-url" "$AUTH_URL"
grant_secret_access "auth-url"

create_secret "auth-realm" "$REALM"
grant_secret_access "auth-realm"

create_secret "auth-audience" "$AUDIENCE"
grant_secret_access "auth-audience"

echo -e "${GREEN}=== ✓ Todos los secrets han sido creados ===${NC}"
echo ""
echo "Para usar estos secrets en Cloud Run, actualiza cloudbuild.yaml"
echo "y descomenta las secciones de availableSecrets y secretEnv"
echo ""
echo "Verificar secrets creados:"
echo "gcloud secrets list --project=$PROJECT_ID"
