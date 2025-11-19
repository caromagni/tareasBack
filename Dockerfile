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

# Copy uwsgi configuration
COPY uwsgi-production.ini ./uwsgi.ini

# Copy application
COPY app/ .

# Expose port
EXPOSE 5000

# Cloud Run provides PORT env var, default to 5000
ENV PORT=5000

# Use uwsgi directly (simpler than startup.py for now)
CMD uwsgi --ini uwsgi.ini --http 0.0.0.0:$PORT

