# 🔧 Solución: Error Compilación uWSGI en Google Cloud Build

## ❌ Error Original

```
ERROR: build step 0 "gcr.io/cloud-builders/docker" failed
The command '/bin/sh -c apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev...' 
returned a non-zero code: 1
╰─> uWSGI
× Failed to build installable wheels for some pyproject.toml based projects
error: failed-wheel-build-for-install
```

## 🔍 Causa

uWSGI necesita compilarse desde código C, y requiere:
- Compiladores C/C++ (gcc, g++)
- Headers de desarrollo de Python
- Librerías de desarrollo (pcre, zlib)

El Dockerfile original no tenía todas las dependencias necesarias.

## ✅ Soluciones (3 Opciones)

### **Opción 1: Dockerfile Mejorado (RECOMENDADO)** ⭐

Ya actualizado en `Dockerfile`. Incluye todas las dependencias de compilación:

**Ventajas:**
- ✅ Imagen más pequeña al final
- ✅ Más rápido que multi-stage
- ✅ Mantiene solo librerías runtime

**Build:**
```bash
docker build --platform linux/amd64 -t gcr.io/PROJECT_ID/tareas-back:latest .
```

### **Opción 2: Multi-Stage Build**

Usa `Dockerfile.multistage` - Separa compilación de runtime:

**Ventajas:**
- ✅ Imagen final MUY pequeña
- ✅ No incluye herramientas de compilación
- ✅ Mejor para producción

**Build:**
```bash
docker build --platform linux/amd64 -f Dockerfile.multistage -t gcr.io/PROJECT_ID/tareas-back:latest .
```

### **Opción 3: Imagen Pre-compilada**

Usa `Dockerfile.prebuilt` - Imagen base con uWSGI ya compilado:

**Ventajas:**
- ✅ Build más rápido
- ✅ Sin problemas de compilación
- ✅ Base mantenida por tiangolo

**Desventajas:**
- ⚠️ Imagen base más pesada
- ⚠️ Incluye nginx (no necesario para Cloud Run)

**Build:**
```bash
docker build --platform linux/amd64 -f Dockerfile.prebuilt -t gcr.io/PROJECT_ID/tareas-back:latest .
```

## 🚀 Deploy Completo

### 1. Usando Dockerfile principal (Opción 1 - Recomendado)

```bash
#!/bin/bash

# Variables
PROJECT_ID="tu-project-id"
REGION="us-west1"
SERVICE_NAME="tareas-back"
IMAGE="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"

# Configurar proyecto
gcloud config set project ${PROJECT_ID}

# Build
echo "🔨 Building Docker image..."
docker build --platform linux/amd64 -t ${IMAGE} .

# Push
echo "⬆️ Pushing to Container Registry..."
docker push ${IMAGE}

# Deploy
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --port 5000 \
  --cpu 1 \
  --memory 512Mi \
  --min-instances 0 \
  --max-instances 10 \
  --timeout 300 \
  --set-env-vars="CORS_ORIGINS=https://tu-frontend.com,http://localhost:5173" \
  --set-env-vars="CORS_ALLOW_CREDENTIALS=true"

echo "✅ Deploy complete!"
```

### 2. Usando Cloud Build (YAML)

Crea `cloudbuild.yaml`:

```yaml
steps:
  # Build
  - name: 'gcr.io/cloud-builders/docker'
    args: 
      - 'build'
      - '--platform=linux/amd64'
      - '-t'
      - 'gcr.io/$PROJECT_ID/tareas-back:$COMMIT_SHA'
      - '-t'
      - 'gcr.io/$PROJECT_ID/tareas-back:latest'
      - '.'
    
  # Push
  - name: 'gcr.io/cloud-builders/docker'
    args: 
      - 'push'
      - 'gcr.io/$PROJECT_ID/tareas-back:$COMMIT_SHA'
  
  - name: 'gcr.io/cloud-builders/docker'
    args: 
      - 'push'
      - 'gcr.io/$PROJECT_ID/tareas-back:latest'
  
  # Deploy
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'tareas-back'
      - '--image=gcr.io/$PROJECT_ID/tareas-back:$COMMIT_SHA'
      - '--region=us-west1'
      - '--platform=managed'
      - '--port=5000'
      - '--cpu=1'
      - '--memory=512Mi'
      - '--timeout=300'
      - '--allow-unauthenticated'

images:
  - 'gcr.io/$PROJECT_ID/tareas-back:$COMMIT_SHA'
  - 'gcr.io/$PROJECT_ID/tareas-back:latest'

timeout: '1800s'

options:
  machineType: 'E2_HIGHCPU_8'  # Máquina más potente para build más rápido
  logging: CLOUD_LOGGING_ONLY
```

Ejecuta:
```bash
gcloud builds submit --config cloudbuild.yaml
```

### 3. Usando Cloud Build con Dockerfile alternativo

Si quieres usar `Dockerfile.multistage`:

```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: 
      - 'build'
      - '--platform=linux/amd64'
      - '-f'
      - 'Dockerfile.multistage'  # ← Especifica el Dockerfile
      - '-t'
      - 'gcr.io/$PROJECT_ID/tareas-back:latest'
      - '.'
# ... resto igual
```

## 🧪 Test Local Antes de Desplegar

### Test 1: Build local
```bash
docker build --platform linux/amd64 -t tareas-back:test .
```

Si falla aquí, el problema está en el Dockerfile.

### Test 2: Run local
```bash
docker run -p 5000:5000 \
  -e CORS_ORIGINS=http://localhost:5173 \
  -e postgres_user=user \
  -e postgres_password=pass \
  -e postgres_base=host:5432/db \
  tareas-back:test
```

### Test 3: Verificar endpoints
```bash
# Health check
curl http://localhost:5000/livez

# Readiness
curl http://localhost:5000/readyz

# CORS
curl -X OPTIONS http://localhost:5000/api/usuario \
  -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: POST" \
  -v
```

## 🐛 Troubleshooting

### Error: "gcc: command not found"

**Causa:** No hay compilador C

**Solución:** Ya está en el Dockerfile actualizado:
```dockerfile
RUN apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make
```

### Error: "Python.h: No such file or directory"

**Causa:** Faltan headers de Python

**Solución:** Ya está en el Dockerfile:
```dockerfile
RUN apt-get install -y --no-install-recommends \
    python3-dev
```

### Error: "pcre.h: No such file or directory"

**Causa:** Falta librería PCRE

**Solución:** Ya está en el Dockerfile:
```dockerfile
RUN apt-get install -y --no-install-recommends \
    libpcre3-dev \
    zlib1g-dev
```

### Build muy lento en Cloud Build

**Solución 1:** Usa máquina más potente:
```yaml
options:
  machineType: 'E2_HIGHCPU_8'
```

**Solución 2:** Usa cache de Docker:
```yaml
options:
  machineType: 'E2_HIGHCPU_8'
  substitution_option: 'ALLOW_LOOSE'
  dynamic_substitutions: true
```

**Solución 3:** Usa Artifact Registry en lugar de Container Registry (más rápido):
```bash
gcloud artifacts repositories create tareas-back \
  --repository-format=docker \
  --location=us-west1

# Luego usa: us-west1-docker.pkg.dev/PROJECT_ID/tareas-back/image
```

### Error: "Image platform does not match host platform"

**Causa:** Cloud Run necesita linux/amd64

**Solución:** Siempre usa:
```bash
docker build --platform linux/amd64 ...
```

## 📊 Comparación de Opciones

| Característica | Dockerfile | Multistage | Prebuilt |
|----------------|-----------|------------|----------|
| Tiempo de build | ~5-8 min | ~6-10 min | ~3-5 min |
| Tamaño final | ~250 MB | ~200 MB | ~400 MB |
| Complejidad | Baja | Media | Baja |
| Mantenimiento | Fácil | Fácil | Depende de base |
| Recomendado | ✅ Sí | ✅ Producción | ⚠️ Prototipo |

## 🎯 Recomendación Final

**Para producción:** Usa el `Dockerfile` principal (ya actualizado)

**Para optimización extrema:** Usa `Dockerfile.multistage`

**Para pruebas rápidas:** Usa `Dockerfile.prebuilt`

## 📋 Checklist Pre-Deploy

- [ ] Dockerfile tiene todas las dependencias de compilación
- [ ] `requirements.txt` está actualizado
- [ ] Variables de entorno configuradas
- [ ] Test local exitoso
- [ ] `.dockerignore` configurado
- [ ] `uwsgi-production.ini` sin headers CORS duplicados
- [ ] CORS_ORIGINS incluye tu frontend

## 🔄 Comandos Rápidos

```bash
# Build y test local
docker build --platform linux/amd64 -t tareas-back:test .
docker run -p 5000:5000 tareas-back:test

# Deploy directo
./deploy-cloudrun.sh tu-project-id us-west1 tareas-back

# O con Cloud Build
gcloud builds submit --config cloudbuild.yaml

# Ver logs
gcloud run services logs tail tareas-back --region us-west1

# Rollback si algo falla
gcloud run services update-traffic tareas-back \
  --to-revisions=PREVIOUS_REVISION=100 \
  --region us-west1
```

## 📚 Archivos Relacionados

- `Dockerfile` - Principal (recomendado) ⭐
- `Dockerfile.multistage` - Multi-stage build (optimizado)
- `Dockerfile.prebuilt` - Con imagen pre-compilada (rápido)
- `cloudbuild.yaml` - Para Cloud Build CI/CD
- `deploy-cloudrun.sh` - Script de deploy automatizado
- `.dockerignore` - Optimización de build
