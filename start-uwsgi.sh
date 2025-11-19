#!/bin/bash
set -e

# Default PORT to 5000 if not set by Cloud Run
PORT="${PORT:-5000}"

echo "=========================================="
echo "Starting Tareas Backend"
echo "=========================================="
echo "PORT: $PORT"
echo "Python version: $(python --version)"
echo "Working directory: $(pwd)"
echo "=========================================="
echo "Directory contents:"
ls -la | head -20
echo "=========================================="

# Verify main.py exists
if [ ! -f "main.py" ]; then
    echo "ERROR: main.py not found!"
    echo "Current directory: $(pwd)"
    echo "Available files:"
    ls -la
    exit 1
fi

# Verify uwsgi is installed
if ! command -v uwsgi &> /dev/null; then
    echo "ERROR: uwsgi not found!"
    pip list | grep -i uwsgi
    exit 1
fi

echo "=========================================="
echo "Starting uwsgi on 0.0.0.0:${PORT}..."
echo "=========================================="

# Start uwsgi with port override
# CRITICAL: Must bind to 0.0.0.0, not 127.0.0.1 or localhost
exec uwsgi --ini uwsgi.ini --http "0.0.0.0:${PORT}"
