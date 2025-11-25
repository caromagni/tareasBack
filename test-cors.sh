#!/bin/bash

# Script para probar CORS en Cloud Run o local
# Uso: ./test-cors.sh https://tu-servicio.run.app https://tu-frontend.com

set -e

BACKEND_URL=${1:-"http://localhost:5000"}
ORIGIN=${2:-"http://localhost:5173"}

echo "========================================="
echo "Testing CORS Configuration"
echo "========================================="
echo "Backend: $BACKEND_URL"
echo "Origin: $ORIGIN"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test 1: Health check
echo -e "${YELLOW}Test 1: Health Check${NC}"
echo "GET $BACKEND_URL/readyz"
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $BACKEND_URL/readyz)
if [ "$HEALTH_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✓ Health check passed (200)${NC}"
else
    echo -e "${RED}✗ Health check failed ($HEALTH_RESPONSE)${NC}"
fi
echo ""

# Test 2: Preflight request (OPTIONS)
echo -e "${YELLOW}Test 2: Preflight Request (OPTIONS)${NC}"
echo "OPTIONS $BACKEND_URL/api/usuario"
echo "Origin: $ORIGIN"
echo ""

PREFLIGHT_RESPONSE=$(curl -s -i -X OPTIONS "$BACKEND_URL/api/usuario" \
  -H "Origin: $ORIGIN" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type, Authorization, x-api-key")

echo "$PREFLIGHT_RESPONSE"
echo ""

# Check for CORS headers
if echo "$PREFLIGHT_RESPONSE" | grep -qi "access-control-allow-origin"; then
    echo -e "${GREEN}✓ Access-Control-Allow-Origin header present${NC}"
    ALLOW_ORIGIN=$(echo "$PREFLIGHT_RESPONSE" | grep -i "access-control-allow-origin" | cut -d' ' -f2-)
    echo "  Value: $ALLOW_ORIGIN"
else
    echo -e "${RED}✗ Access-Control-Allow-Origin header MISSING${NC}"
fi

if echo "$PREFLIGHT_RESPONSE" | grep -qi "access-control-allow-methods"; then
    echo -e "${GREEN}✓ Access-Control-Allow-Methods header present${NC}"
else
    echo -e "${RED}✗ Access-Control-Allow-Methods header missing${NC}"
fi

if echo "$PREFLIGHT_RESPONSE" | grep -qi "access-control-allow-headers"; then
    echo -e "${GREEN}✓ Access-Control-Allow-Headers header present${NC}"
else
    echo -e "${RED}✗ Access-Control-Allow-Headers header missing${NC}"
fi

if echo "$PREFLIGHT_RESPONSE" | grep -qi "access-control-allow-credentials"; then
    echo -e "${GREEN}✓ Access-Control-Allow-Credentials header present${NC}"
else
    echo -e "${YELLOW}⚠ Access-Control-Allow-Credentials header missing (optional)${NC}"
fi

echo ""

# Test 3: Actual GET request with CORS
echo -e "${YELLOW}Test 3: Actual Request (GET)${NC}"
echo "GET $BACKEND_URL/livez"
echo "Origin: $ORIGIN"
echo ""

ACTUAL_RESPONSE=$(curl -s -i -X GET "$BACKEND_URL/livez" \
  -H "Origin: $ORIGIN")

echo "$ACTUAL_RESPONSE"
echo ""

if echo "$ACTUAL_RESPONSE" | grep -qi "access-control-allow-origin"; then
    echo -e "${GREEN}✓ CORS headers present in actual response${NC}"
else
    echo -e "${RED}✗ CORS headers missing in actual response${NC}"
fi

echo ""
echo "========================================="
echo "Test Complete"
echo "========================================="
echo ""
echo "Next steps if tests fail:"
echo "1. Verify CORS_ORIGINS environment variable includes: $ORIGIN"
echo "2. Check application logs for errors"
echo "3. Ensure Flask-CORS is installed: pip install Flask-Cors"
echo "4. For Cloud Run, update env vars:"
echo "   gcloud run services update SERVICE_NAME --set-env-vars=\"CORS_ORIGINS=$ORIGIN\""
