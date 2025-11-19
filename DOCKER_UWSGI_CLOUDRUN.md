# Configuración de Contenedor con uwsgi para Cloud Run

## Cambios Realizados

### 1. Dockerfile Optimizado
- ✅ Usa `python:3.11-slim-bullseye` (imagen más ligera)
- ✅ Multi-stage caching para dependencias
- ✅ Limpieza de paquetes innecesarios
- ✅ `ENTRYPOINT` + `CMD` para mejor manejo de señales
- ✅ Health check integrado
- ✅ Variables de entorno optimizadas

### 2. Configuración uwsgi-production.ini
- ✅ Eliminados headers CORS duplicados (Flask-CORS los maneja)
- ✅ Configuración optimizada para Cloud Run
- ✅ Manejo correcto de señales para graceful shutdown
- ✅ Timeouts apropiados (300s para Cloud Run)
- ✅ 2 procesos con 2 threads cada uno
- ✅ Buffer sizes optimizados

### 3. .dockerignore
- ✅ Excluye archivos innecesarios del build
- ✅ Reduce tamaño de la imagen
- ✅ Mejora velocidad de build

### 4. Script de deploy
- ✅ `deploy-cloudrun.sh` para automatizar despliegue

## Estructura del Entrypoint

### Dockerfile
```dockerfile
ENTRYPOINT ["uwsgi"]
CMD ["--ini", "uwsgi.ini"]
```

**Ventajas:**
- Mejor manejo de señales (SIGTERM, SIGINT)
- Permite override fácil del CMD sin cambiar ENTRYPOINT
- Graceful shutdown en Cloud Run

### uwsgi-production.ini
```ini
[uwsgi]
wsgi-file = main.py
callable = app
module = main:app
http-socket = :5000
master = true
processes = 2
threads = 2
```

## Construcción Local

```bash
# Build
docker build -t tareasback:latest .

# Test local
docker run -p 5000:5000 \
  -e CORS_ORIGINS=http://localhost:5173 \
  -e CORS_ALLOW_CREDENTIALS=true \
  -e postgres_user=user \
  -e postgres_password=pass \
  -e postgres_base=host:port/db \
  tareasback:latest

# Test con override de comando
docker run -p 5000:5000 \
  tareasback:latest --http :5000 --wsgi-file main.py --callable app
```

## Despliegue a Cloud Run

### Opción 1: Script automatizado
```bash
./deploy-cloudrun.sh mi-project us-central1 tareas-backend
```

### Opción 2: Comandos manuales

#### 1. Build y Push
```bash
# Configurar proyecto
gcloud config set project TU-PROJECT-ID

# Build para Cloud Run (linux/amd64)
docker build --platform linux/amd64 -t gcr.io/TU-PROJECT-ID/tareas-backend:latest .

# Push a Container Registry
docker push gcr.io/TU-PROJECT-ID/tareas-backend:latest
```

#### 2. Deploy inicial
```bash
gcloud run deploy tareas-backend \
  --image gcr.io/TU-PROJECT-ID/tareas-backend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 5000 \
  --cpu 1 \
  --memory 512Mi \
  --min-instances 0 \
  --max-instances 10 \
  --timeout 300 \
  --set-env-vars="CORS_ORIGINS=https://tu-frontend.com,http://localhost:5173,CORS_ALLOW_CREDENTIALS=true"
```

#### 3. Actualizar variables de entorno
```bash
gcloud run services update tareas-backend \
  --region us-central1 \
  --update-env-vars="postgres_user=user,postgres_password=pass,postgres_base=host/db"
```

### Opción 3: Usando Cloud Build

Crea `cloudbuild.yaml`:
```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/tareas-backend:$COMMIT_SHA', '.']
  
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/tareas-backend:$COMMIT_SHA']
  
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'tareas-backend'
      - '--image=gcr.io/$PROJECT_ID/tareas-backend:$COMMIT_SHA'
      - '--region=us-central1'
      - '--platform=managed'

images:
  - 'gcr.io/$PROJECT_ID/tareas-backend:$COMMIT_SHA'
```

Ejecuta:
```bash
gcloud builds submit --config cloudbuild.yaml
```

## Variables de Entorno Necesarias

### Mínimas requeridas:
```bash
CORS_ORIGINS=https://tu-frontend.com
CORS_ALLOW_CREDENTIALS=true
postgres_user=usuario
postgres_password=password
postgres_base=host:port/database
```

### Todas las variables:
```bash
# CORS
CORS_ORIGINS=https://frontend.com,https://otro-dominio.com
CORS_ALLOW_CREDENTIALS=true

# Database
postgres_user=usuario
postgres_password=password
postgres_base=host:5432/database

# Auth
AUTH_URL=https://keycloak-url
REALM=nombre-realm
AUDIENCE=tu-audience

# Redis (si aplica)
REDIS_HOST=redis-host
REDIS_PORT=6379
REDIS_PASSWORD=password

# RabbitMQ (si aplica)
RABBITMQ_USER=usuario
RABBITMQ_PASSWORD=password
RABBITMQ_HOST=host
RABBITMQ_PORT=5672

# Config
RUN_DB_SETUP=0
RUN_DB_CREATION=0
MAX_ITEMS_PER_RESPONSE=100
LOG_LEVEL=INFO
```

## Verificación

### 1. Health checks
```bash
# Liveness
curl https://tu-servicio.run.app/livez

# Readiness
curl https://tu-servicio.run.app/readyz
```

### 2. CORS
```bash
curl -H "Origin: https://tu-frontend.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type,Authorization" \
  -X OPTIONS \
  --verbose \
  https://tu-servicio.run.app/api/endpoint
```

Deberías ver:
```
< HTTP/2 200
< access-control-allow-origin: https://tu-frontend.com
< access-control-allow-methods: GET, PUT, POST, DELETE, PATCH, OPTIONS
< access-control-allow-headers: Content-Type, Authorization, ...
< access-control-allow-credentials: true
```

### 3. Logs
```bash
gcloud run services logs read tareas-backend --region us-central1 --limit 50
```

## Troubleshooting

### Container no inicia
```bash
# Ver logs
gcloud run services logs read tareas-backend --region us-central1 --limit 100

# Verificar configuración
gcloud run services describe tareas-backend --region us-central1
```

### Error 502/503
- Verifica que el puerto sea 5000
- Revisa que las variables de entorno estén configuradas
- Comprueba los health checks

### Timeout
- Aumenta timeout: `--timeout 900` (máx 60 min)
- Revisa configuración de uwsgi: `harakiri = 300`

### Performance
```bash
# Aumentar recursos
gcloud run services update tareas-backend \
  --region us-central1 \
  --cpu 2 \
  --memory 1Gi

# Aumentar instancias mínimas (reduce cold starts)
gcloud run services update tareas-backend \
  --region us-central1 \
  --min-instances 1
```

## Monitoreo

### Cloud Console
- Métricas: CPU, Memoria, Latencia, Errores
- Logs: Filtrar por nivel, buscar errores
- Traces: Request tracing

### Comando rápido
```bash
# Ver estado
gcloud run services describe tareas-backend --region us-central1

# Ver últimas revisiones
gcloud run revisions list --service tareas-backend --region us-central1

# Revertir a revisión anterior
gcloud run services update-traffic tareas-backend \
  --region us-central1 \
  --to-revisions REVISION-NAME=100
```

## Optimizaciones Adicionales

### 1. Reducir cold starts
```bash
--min-instances 1  # Mantener siempre 1 instancia caliente
--cpu-boost        # CPU boost durante startup
```

### 2. Optimizar imagen
- Usar multi-stage builds
- Minimizar capas
- Usar .dockerignore

### 3. Configurar concurrencia
```bash
--concurrency 80  # Número de requests por instancia
```

## Costos Aproximados

- Request: $0.40 / millón
- CPU: $0.00002400 / vCPU-second
- Memoria: $0.0000025 / GiB-second
- Con min-instances=0: Solo pagas por uso real
- Con min-instances=1: ~$8-15/mes por instancia base
