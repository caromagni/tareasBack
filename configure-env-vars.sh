#!/bin/bash

# Configure Cloud Run Environment Variables
# Use this script to update environment variables without rebuilding the container

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
PROJECT_ID="${1:-eng-scene-478112-k0}"
REGION="${2:-us-west1}"
SERVICE_NAME="${3:-tareas-back}"

echo -e "${GREEN}=========================================="
echo "Cloud Run Environment Configuration"
echo -e "==========================================${NC}"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"
echo ""

# Check if service exists
if ! gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID &> /dev/null; then
    echo -e "${RED}ERROR: Service '$SERVICE_NAME' not found in region '$REGION'${NC}"
    echo "Deploy first with: ./fix-and-deploy.sh"
    exit 1
fi

echo -e "${YELLOW}Current Environment Variables:${NC}"
gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --project=$PROJECT_ID \
    --format="table(spec.template.spec.containers[0].env)" | head -20

echo ""
echo "Select configuration method:"
echo "  1) Interactive configuration"
echo "  2) Load from file"
echo "  3) View current configuration"
echo "  4) Update single variable"
echo ""
read -p "Select option (1-4): " -n 1 -r option
echo ""

case $option in
    1)
        echo -e "${GREEN}Interactive Configuration${NC}"
        echo ""
        
        # Database
        echo -e "${YELLOW}=== Database Configuration ===${NC}"
        read -p "postgres_user: " POSTGRES_USER
        read -sp "postgres_password: " POSTGRES_PASSWORD
        echo ""
        read -p "postgres_base (format: host:port/database): " POSTGRES_BASE
        echo ""
        
        # Validate database config
        if [ -z "$POSTGRES_USER" ] || [ -z "$POSTGRES_PASSWORD" ] || [ -z "$POSTGRES_BASE" ]; then
            echo -e "${RED}ERROR: Database configuration is required${NC}"
            exit 1
        fi
        
        # Auth
        echo -e "${YELLOW}=== Authentication Configuration ===${NC}"
        read -p "AUTH_URL: " AUTH_URL
        read -p "REALM: " REALM
        read -p "AUDIENCE: " AUDIENCE
        echo ""
        
        # Validate auth config
        if [ -z "$AUTH_URL" ] || [ -z "$REALM" ] || [ -z "$AUDIENCE" ]; then
            echo -e "${RED}ERROR: Authentication configuration is required${NC}"
            exit 1
        fi
        
        # CORS
        echo -e "${YELLOW}=== CORS Configuration ===${NC}"
        echo "Enter allowed origins (comma-separated)"
        echo "Example: https://app.example.com,http://localhost:5173"
        read -p "ALLOWED_ORIGINS: " ALLOWED_ORIGINS
        echo ""
        
        # Optional settings
        echo -e "${YELLOW}=== Optional Settings ===${NC}"
        read -p "LOG_LEVEL [INFO]: " LOG_LEVEL
        LOG_LEVEL=${LOG_LEVEL:-INFO}
        
        read -p "RUN_DB_SETUP [0]: " RUN_DB_SETUP
        RUN_DB_SETUP=${RUN_DB_SETUP:-0}
        
        read -p "RUN_DB_CREATION [0]: " RUN_DB_CREATION
        RUN_DB_CREATION=${RUN_DB_CREATION:-0}
        
        read -p "cache_enabled [False]: " CACHE_ENABLED
        CACHE_ENABLED=${CACHE_ENABLED:-False}
        echo ""
        
        # Confirm
        echo -e "${YELLOW}Configuration Summary:${NC}"
        echo "Database User: $POSTGRES_USER"
        echo "Database: $POSTGRES_BASE"
        echo "Auth URL: $AUTH_URL"
        echo "Realm: $REALM"
        echo "Audience: $AUDIENCE"
        echo "Allowed Origins: $ALLOWED_ORIGINS"
        echo "Log Level: $LOG_LEVEL"
        echo ""
        
        read -p "Apply this configuration? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${RED}Configuration cancelled${NC}"
            exit 1
        fi
        
        # Apply configuration
        echo -e "${YELLOW}Updating Cloud Run service...${NC}"
        gcloud run services update $SERVICE_NAME \
            --region=$REGION \
            --project=$PROJECT_ID \
            --set-env-vars="postgres_user=$POSTGRES_USER,\
postgres_password=$POSTGRES_PASSWORD,\
postgres_base=$POSTGRES_BASE,\
AUTH_URL=$AUTH_URL,\
REALM=$REALM,\
AUDIENCE=$AUDIENCE,\
ALLOWED_ORIGINS=$ALLOWED_ORIGINS,\
LOG_LEVEL=$LOG_LEVEL,\
RUN_DB_SETUP=$RUN_DB_SETUP,\
RUN_DB_CREATION=$RUN_DB_CREATION,\
cache_enabled=$CACHE_ENABLED"
        
        echo -e "${GREEN}✓ Configuration applied successfully${NC}"
        ;;
    
    2)
        echo -e "${GREEN}Load from file${NC}"
        echo ""
        read -p "Enter path to env file: " ENV_FILE
        
        if [ ! -f "$ENV_FILE" ]; then
            echo -e "${RED}ERROR: File not found: $ENV_FILE${NC}"
            exit 1
        fi
        
        echo -e "${YELLOW}Loading from $ENV_FILE...${NC}"
        gcloud run services update $SERVICE_NAME \
            --region=$REGION \
            --project=$PROJECT_ID \
            --env-vars-file="$ENV_FILE"
        
        echo -e "${GREEN}✓ Configuration loaded from file${NC}"
        ;;
    
    3)
        echo -e "${GREEN}Current Configuration${NC}"
        echo ""
        gcloud run services describe $SERVICE_NAME \
            --region=$REGION \
            --project=$PROJECT_ID \
            --format="table(spec.template.spec.containers[0].env)"
        
        echo ""
        echo "Export to file:"
        echo "  gcloud run services describe $SERVICE_NAME --region=$REGION --format=yaml > service-config.yaml"
        exit 0
        ;;
    
    4)
        echo -e "${GREEN}Update single variable${NC}"
        echo ""
        read -p "Variable name: " VAR_NAME
        read -p "Variable value: " VAR_VALUE
        
        if [ -z "$VAR_NAME" ] || [ -z "$VAR_VALUE" ]; then
            echo -e "${RED}ERROR: Both name and value are required${NC}"
            exit 1
        fi
        
        echo -e "${YELLOW}Updating $VAR_NAME...${NC}"
        gcloud run services update $SERVICE_NAME \
            --region=$REGION \
            --project=$PROJECT_ID \
            --update-env-vars="$VAR_NAME=$VAR_VALUE"
        
        echo -e "${GREEN}✓ Variable updated${NC}"
        ;;
    
    *)
        echo -e "${RED}Invalid option${NC}"
        exit 1
        ;;
esac

# Wait for service to be ready
echo ""
echo -e "${YELLOW}Waiting for service to update...${NC}"
sleep 5

# Test the service
echo -e "${YELLOW}Testing service...${NC}"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --project=$PROJECT_ID \
    --format='value(status.url)')

if [ ! -z "$SERVICE_URL" ]; then
    echo "Service URL: $SERVICE_URL"
    echo ""
    
    echo -n "Testing /livez... "
    if curl -sf "$SERVICE_URL/livez" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
    fi
    
    echo -n "Testing /readyz... "
    if curl -sf "$SERVICE_URL/readyz" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${YELLOW}⚠${NC} (may need time to connect to database)"
    fi
fi

echo ""
echo -e "${GREEN}=========================================="
echo "Configuration Complete"
echo -e "==========================================${NC}"
echo ""
echo "View logs with:"
echo "  gcloud run services logs tail $SERVICE_NAME --region=$REGION"
echo ""
echo "Test endpoints:"
echo "  curl $SERVICE_URL/livez"
echo "  curl $SERVICE_URL/readyz"
echo "  curl $SERVICE_URL/docs"
