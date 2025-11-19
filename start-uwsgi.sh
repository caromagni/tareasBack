#!/bin/bash
set -e

# Default PORT to 5000 if not set by Cloud Run
PORT="${PORT:-5000}"

echo "Starting uwsgi on port $PORT"

# Start uwsgi with port override
exec uwsgi --ini uwsgi.ini --http "0.0.0.0:${PORT}"
