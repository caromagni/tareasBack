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

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    python3 -m pip install --upgrade pip && \
    pip install --progress-bar off -r requirements.txt && \
    apt-get purge -y --auto-remove gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /app/tmp /app/logs

# Copy uwsgi configuration
COPY uwsgi-production.ini ./uwsgi.ini

# Copy application
COPY app/ .

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/readyz', timeout=5)" || exit 1

# Use ENTRYPOINT + CMD for better signal handling
ENTRYPOINT ["uwsgi"]
CMD ["--ini", "uwsgi.ini"]
