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

# Health check - simplificado para evitar dependencias extras
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/livez', timeout=5)" || exit 1

# Use ENTRYPOINT + CMD for better signal handling
ENTRYPOINT ["uwsgi"]
CMD ["--ini", "uwsgi.ini"]
