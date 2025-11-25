#!/bin/bash

# Script para probar el contenedor Docker localmente antes de desplegarlo a Cloud Run

echo "=========================================="
echo "Testing Docker Container Locally"
echo "=========================================="

# Build the image
echo "1. Building Docker image..."
docker build -t tareas-back-test:latest .

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo "✓ Build successful"
echo ""

# Run the container
echo "2. Running container on port 5000..."
docker run --rm \
    -p 5000:5000 \
    -e PORT=5000 \
    -e postgres_user=test_user \
    -e postgres_password=test_pass \
    -e postgres_base=localhost:5432/test_db \
    -e AUTH_URL=https://test.com \
    -e REALM=test \
    -e AUDIENCE=test \
    -e ALLOWED_ORIGINS=http://localhost:3000 \
    -e RUN_DB_SETUP=0 \
    -e RUN_DB_CREATION=0 \
    -e cache_enabled=False \
    --name tareas-back-test \
    tareas-back-test:latest &

CONTAINER_PID=$!

# Wait for container to start
echo "3. Waiting for container to start..."
sleep 5

# Test the endpoints
echo ""
echo "4. Testing health endpoints..."
echo ""

echo "Testing root endpoint (/)..."
curl -s http://localhost:5000/ | jq .
echo ""

echo "Testing liveness probe (/livez)..."
curl -s http://localhost:5000/livez | jq .
echo ""

echo "Testing readiness probe (/readyz)..."
curl -s http://localhost:5000/readyz | jq .
echo ""

# Check container logs
echo "=========================================="
echo "Container Logs (last 50 lines):"
echo "=========================================="
docker logs tareas-back-test 2>&1 | tail -50

# Cleanup
echo ""
echo "Stopping container..."
docker stop tareas-back-test

echo ""
echo "=========================================="
echo "Test Complete!"
echo "=========================================="
