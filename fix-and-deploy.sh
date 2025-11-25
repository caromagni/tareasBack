#!/bin/bash

# Cloud Run Deployment Fix Script
# This script deploys your application with all necessary fixes

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${1:-eng-scene-478112-k0}"
REGION="${2:-us-west1}"
SERVICE_NAME="${3:-tareas-back}"

echo -e "${GREEN}=========================================="
echo "Cloud Run Deployment Fix"
echo -e "==========================================${NC}"
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}ERROR: gcloud CLI is not installed${NC}"
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Set project
echo -e "${YELLOW}Setting project...${NC}"
gcloud config set project $PROJECT_ID

# Step 1: Build and Deploy
echo -e "${GREEN}=========================================="
echo "Step 1: Building and Deploying Container"
echo -e "==========================================${NC}"
echo ""
echo "This will:"
echo "  - Build Docker image with fixes"
echo "  - Push to Google Container Registry"
echo "  - Deploy to Cloud Run"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}Deployment cancelled${NC}"
    exit 1
fi

gcloud builds submit --config cloudbuild.yaml

echo -e "${GREEN}✓ Build and deployment completed${NC}"
echo ""

# Step 2: Configure Environment Variables
echo -e "${GREEN}=========================================="
echo "Step 2: Configure Environment Variables"
echo -e "==========================================${NC}"
echo ""
echo "The application requires the following environment variables:"
echo ""
echo -e "${YELLOW}REQUIRED:${NC}"
echo "  - postgres_user"
echo "  - postgres_password"
echo "  - postgres_base (format: host:port/database)"
echo "  - AUTH_URL (Keycloak URL)"
echo "  - REALM"
echo "  - AUDIENCE"
echo ""
echo -e "${YELLOW}OPTIONAL:${NC}"
echo "  - ALLOWED_ORIGINS (CORS)"
echo ""
echo "Choose configuration method:"
echo "  1) Interactive setup (recommended)"
echo "  2) Use environment variables from current shell"
echo "  3) Skip (configure manually later)"
echo ""
read -p "Select option (1-3): " -n 1 -r option
echo

case $option in
    1)
        echo -e "${YELLOW}Interactive Configuration${NC}"
        echo ""
        
        # Database
        echo -e "${GREEN}Database Configuration:${NC}"
        read -p "postgres_user: " POSTGRES_USER
        read -sp "postgres_password: " POSTGRES_PASSWORD
        echo ""
        read -p "postgres_base (host:port/database): " POSTGRES_BASE
        echo ""
        
        # Auth
        echo -e "${GREEN}Authentication Configuration:${NC}"
        read -p "AUTH_URL: " AUTH_URL
        read -p "REALM: " REALM
        read -p "AUDIENCE: " AUDIENCE
        echo ""
        
        # CORS
        echo -e "${GREEN}CORS Configuration:${NC}"
        read -p "ALLOWED_ORIGINS (comma-separated): " ALLOWED_ORIGINS
        echo ""
        
        # Apply configuration
        echo -e "${YELLOW}Applying configuration...${NC}"
        gcloud run services update $SERVICE_NAME \
            --region=$REGION \
            --set-env-vars="postgres_user=$POSTGRES_USER,\
postgres_password=$POSTGRES_PASSWORD,\
postgres_base=$POSTGRES_BASE,\
AUTH_URL=$AUTH_URL,\
REALM=$REALM,\
AUDIENCE=$AUDIENCE,\
ALLOWED_ORIGINS=$ALLOWED_ORIGINS,\
LOG_LEVEL=INFO,\
RUN_DB_SETUP=0,\
RUN_DB_CREATION=0,\
cache_enabled=False"
        
        echo -e "${GREEN}✓ Environment variables configured${NC}"
        ;;
    
    2)
        echo -e "${YELLOW}Using shell environment variables${NC}"
        
        if [ -z "$POSTGRES_USER" ] || [ -z "$POSTGRES_PASSWORD" ] || [ -z "$POSTGRES_BASE" ]; then
            echo -e "${RED}ERROR: Missing required database variables${NC}"
            echo "Set: POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_BASE"
            exit 1
        fi
        
        if [ -z "$AUTH_URL" ] || [ -z "$REALM" ] || [ -z "$AUDIENCE" ]; then
            echo -e "${RED}ERROR: Missing required auth variables${NC}"
            echo "Set: AUTH_URL, REALM, AUDIENCE"
            exit 1
        fi
        
        gcloud run services update $SERVICE_NAME \
            --region=$REGION \
            --set-env-vars="postgres_user=$POSTGRES_USER,\
postgres_password=$POSTGRES_PASSWORD,\
postgres_base=$POSTGRES_BASE,\
AUTH_URL=$AUTH_URL,\
REALM=$REALM,\
AUDIENCE=$AUDIENCE,\
ALLOWED_ORIGINS=${ALLOWED_ORIGINS:-http://localhost:5173},\
LOG_LEVEL=INFO,\
RUN_DB_SETUP=0,\
RUN_DB_CREATION=0,\
cache_enabled=False"
        
        echo -e "${GREEN}✓ Environment variables configured${NC}"
        ;;
    
    3)
        echo -e "${YELLOW}Skipping environment variable configuration${NC}"
        echo ""
        echo "Configure manually with:"
        echo "  gcloud run services update $SERVICE_NAME --region=$REGION --set-env-vars=..."
        echo ""
        echo "See DEPLOY_FIX.md for details"
        ;;
    
    *)
        echo -e "${RED}Invalid option${NC}"
        exit 1
        ;;
esac

echo ""

# Step 3: Verify Deployment
echo -e "${GREEN}=========================================="
echo "Step 3: Verifying Deployment"
echo -e "==========================================${NC}"
echo ""

echo -e "${YELLOW}Fetching service URL...${NC}"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format='value(status.url)')

if [ -z "$SERVICE_URL" ]; then
    echo -e "${RED}ERROR: Could not get service URL${NC}"
    exit 1
fi

echo "Service URL: $SERVICE_URL"
echo ""

echo -e "${YELLOW}Checking service status...${NC}"
gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="table(status.conditions.type,status.conditions.status,status.conditions.message)"

echo ""
echo -e "${YELLOW}Testing health endpoints...${NC}"

# Wait a bit for the service to be ready
echo "Waiting 10 seconds for service to be ready..."
sleep 10

# Test /livez
echo -n "Testing /livez... "
if curl -sf "$SERVICE_URL/livez" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
    echo "The service may still be starting. Check logs:"
    echo "  gcloud run services logs tail $SERVICE_NAME --region=$REGION"
fi

# Test /readyz
echo -n "Testing /readyz... "
if curl -sf "$SERVICE_URL/readyz" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${YELLOW}⚠ FAILED (this is expected if DB is not configured)${NC}"
fi

echo ""

# Step 4: Show Logs
echo -e "${GREEN}=========================================="
echo "Step 4: Recent Logs"
echo -e "==========================================${NC}"
echo ""

gcloud run services logs read $SERVICE_NAME \
    --region=$REGION \
    --limit=20

echo ""

# Summary
echo -e "${GREEN}=========================================="
echo "Deployment Summary"
echo -e "==========================================${NC}"
echo ""
echo "Service URL: $SERVICE_URL"
echo ""
echo "Useful commands:"
echo ""
echo "  # View logs in real-time"
echo "  gcloud run services logs tail $SERVICE_NAME --region=$REGION"
echo ""
echo "  # View service configuration"
echo "  gcloud run services describe $SERVICE_NAME --region=$REGION"
echo ""
echo "  # Update environment variables"
echo "  gcloud run services update $SERVICE_NAME --region=$REGION --set-env-vars=KEY=VALUE"
echo ""
echo "  # Test API endpoints"
echo "  curl $SERVICE_URL/livez"
echo "  curl $SERVICE_URL/readyz"
echo "  curl $SERVICE_URL/docs"
echo ""
echo -e "${GREEN}For detailed troubleshooting, see DEPLOY_FIX.md${NC}"
