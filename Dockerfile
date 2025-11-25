FROM python:3.11-slim-bullseye

# Set timezone
ENV TZ=America/Argentina/Mendoza \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies (keep build tools during uwsgi install)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        make \
        libpq-dev \
        libpcre3-dev \
        zlib1g-dev \
        python3-dev && \
    python3 -m pip install --upgrade pip setuptools wheel && \
    pip install --progress-bar off -r requirements.txt && \
    apt-get purge -y --auto-remove gcc g++ make python3-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /app/tmp /app/logs

# Copy startup script first
COPY start-uwsgi.sh .
RUN chmod +x start-uwsgi.sh

# Copy uwsgi configuration
COPY uwsgi-production.ini ./uwsgi.ini

# Copy application (contents of app/ go into /app)
COPY app/ .

# Create necessary directories
RUN mkdir -p /app/logs /app/tmp

# Expose port (Cloud Run will override with PORT env var)
EXPOSE 5000

# Cloud Run provides PORT env var, default to 5000 if not set
ENV PORT=5000

# Health check for local testing (Cloud Run uses its own health checks)
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/livez')" || exit 1

# Use startup script that handles PORT variable
CMD ["./start-uwsgi.sh"]

