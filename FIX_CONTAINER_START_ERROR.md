# 🔧 Solución: Container Failed to Start in Cloud Run

## ❌ Error

```
ERROR: The user-provided container failed to start and listen on the port 
defined provided by the PORT=5000 environment variable within the allocated timeout.
```

## 🔍 Causas Comunes

1. **Variables de entorno faltantes** (más común) ⭐
   - Base de datos: `postgres_user`, `postgres_password`, `postgres_base`
   - Keycloak: `AUTH_URL`, `REALM`, `AUDIENCE`

2. **Puerto incorrecto**
   - uwsgi debe escuchar en `0.0.0.0:$PORT` (no solo `:5000`)

3. **Timeout de inicio**
   - La aplicación tarda mucho en iniciar (conexiones, setup)

4. **Errores de Python**
   - Imports fallidos
   - Conexiones a servicios externos

## ✅ Solución Implementada

### 1. **uwsgi-production.ini** - Configuración corregida

**Cambios críticos:**
```ini
# ✅ Antes: http-socket = :5000
# ✅ Ahora: http = 0.0.0.0:5000

http = 0.0.0.0:5000  # Escucha en todas las interfaces

# Logging a stdout (Cloud Run lo captura)
logto = /dev/stdout

# Un solo proceso para reducir uso de memoria
processes = 1
threads = 2
```

### 2. **Dockerfile** - CMD simplificado

```dockerfile
# ✅ Antes: ENTRYPOINT ["uwsgi"] + CMD ["--ini", "uwsgi.ini"]
# ✅ Ahora: CMD directo con variable PORT

ENV PORT=5000
CMD uwsgi --ini uwsgi.ini --http 0.0.0.0:$PORT
```

Esto permite que Cloud Run inyecte el `PORT` correcto.

### 3. **Variables de entorno requeridas**

Agregadas a `cloudbuild.yaml` y documentadas.

## 🚀 Pasos para Resolver

### Paso 1: Reconstruir y Redesplegar

```bash
# Opción A: Con script automatizado
./deploy-cloudrun.sh tu-project-id us-west1 tareas-back

# Opción B: Con Cloud Build
gcloud builds submit --config cloudbuild.yaml
```

### Paso 2: Configurar Variables de Entorno

**Opción A - Script interactivo (RECOMENDADO):**
```bash
./configure-env.sh tu-project-id us-west1 tareas-back
```

El script te pedirá todos los valores necesarios.

**Opción B - Comando directo:**
```bash
gcloud run services update tareas-back \
  --region us-west1 \
  --update-env-vars="postgres_user=YOUR_USER,\
postgres_password=YOUR_PASSWORD,\
postgres_base=YOUR_HOST:5432/YOUR_DB,\
AUTH_URL=https://your-keycloak.com,\
REALM=YOUR_REALM,\
AUDIENCE=YOUR_AUDIENCE,\
CORS_ORIGINS=https://your-frontend.com,\
CORS_ALLOW_CREDENTIALS=true,\
LOG_LEVEL=INFO,\
RUN_DB_SETUP=0,\
RUN_DB_CREATION=0"
```

**Opción C - Configurar una por una:**
```bash
# Database
gcloud run services update tareas-back --region us-west1 \
  --set-env-vars="postgres_user=myuser"

gcloud run services update tareas-back --region us-west1 \
  --set-env-vars="postgres_password=mypassword"

gcloud run services update tareas-back --region us-west1 \
  --set-env-vars="postgres_base=myhost:5432/mydb"

# Keycloak
gcloud run services update tareas-back --region us-west1 \
  --set-env-vars="AUTH_URL=https://keycloak.example.com"

gcloud run services update tareas-back --region us-west1 \
  --set-env-vars="REALM=myrealm"

gcloud run services update tareas-back --region us-west1 \
  --set-env-vars="AUDIENCE=myaudience"

# CORS
gcloud run services update tareas-back --region us-west1 \
  --set-env-vars="CORS_ORIGINS=https://my-frontend.com,http://localhost:5173"
```

### Paso 3: Verificar Logs

```bash
# Ver logs en tiempo real
gcloud run services logs tail tareas-back --region us-west1

# Ver últimos 100 logs
gcloud run services logs read tareas-back --region us-west1 --limit 100
```

Busca estos errores comunes:
- `KeyError: 'postgres_user'` → Falta variable de entorno
- `Connection refused` → DB no accesible
- `ModuleNotFoundError` → Falta dependencia en requirements.txt
- `unable to load configuration from uwsgi.ini` → Problema config uwsgi

### Paso 4: Test Endpoints

```bash
# Obtener URL del servicio
SERVICE_URL=$(gcloud run services describe tareas-back --region us-west1 --format 'value(status.url)')

# Test liveness
curl $SERVICE_URL/livez

# Test readiness
curl $SERVICE_URL/readyz

# Test con CORS
curl -X OPTIONS $SERVICE_URL/api/usuario \
  -H "Origin: https://your-frontend.com" \
  -H "Access-Control-Request-Method: POST" \
  -v
```

## 🐛 Troubleshooting Específico

### Error: "Connection to database failed"

**Logs mostrarán:**
```
psycopg2.OperationalError: could not connect to server
```

**Solución:**
1. Verifica que `postgres_base` tenga el formato correcto:
   ```
   postgres_base=IP_O_HOST:5432/nombre_database
   ```

2. Si usas Cloud SQL:
   ```bash
   # Habilita Cloud SQL Admin API
   gcloud services enable sqladmin.googleapis.com
   
   # Conecta Cloud Run con Cloud SQL
   gcloud run services update tareas-back \
     --region us-west1 \
     --add-cloudsql-instances=PROJECT:REGION:INSTANCE
   
   # Usa socket en lugar de IP
   gcloud run services update tareas-back \
     --region us-west1 \
     --set-env-vars="postgres_base=/cloudsql/PROJECT:REGION:INSTANCE/database"
   ```

### Error: "Keycloak connection failed"

**Logs mostrarán:**
```
Error fetching Keycloak public key
```

**Solución:**
```bash
# Verifica que AUTH_URL sea accesible desde Cloud Run
curl https://your-keycloak.com/auth/realms/YOUR_REALM

# Debe devolver JSON con configuración del realm
```

### Error: "Port 5000 already in use"

**Causa:** uwsgi no está usando la variable `PORT` de Cloud Run

**Solución:** Ya está corregida en el Dockerfile:
```dockerfile
CMD uwsgi --ini uwsgi.ini --http 0.0.0.0:$PORT
```

### Error: "Memory limit exceeded"

**Logs mostrarán:**
```
Container exceeded memory limit
```

**Solución:**
```bash
# Aumentar memoria
gcloud run services update tareas-back \
  --region us-west1 \
  --memory 1Gi
```

### Error: "Startup timeout"

**Logs mostrarán:**
```
Container failed to start within allocated timeout
```

**Solución:**
```bash
# Aumentar timeout y CPU para startup más rápido
gcloud run services update tareas-back \
  --region us-west1 \
  --timeout 900 \
  --cpu 2 \
  --cpu-boost  # CPU boost durante startup
```

## 📊 Checklist de Variables de Entorno

### ✅ Requeridas (críticas)
- [ ] `postgres_user`
- [ ] `postgres_password`
- [ ] `postgres_base`
- [ ] `AUTH_URL`
- [ ] `REALM`
- [ ] `AUDIENCE`

### ⚠️ Recomendadas
- [ ] `CORS_ORIGINS`
- [ ] `CORS_ALLOW_CREDENTIALS`
- [ ] `LOG_LEVEL`

### 📋 Opcionales
- [ ] `RUN_DB_SETUP` (default: 0)
- [ ] `RUN_DB_CREATION` (default: 0)
- [ ] `RABBITMQ_USER`
- [ ] `RABBITMQ_PASSWORD`
- [ ] `RABBITMQ_HOST`
- [ ] `REDIS_HOST` (si usas Redis)

## 🔍 Ver Configuración Actual

```bash
# Ver todas las variables de entorno
gcloud run services describe tareas-back \
  --region us-west1 \
  --format="table(spec.template.spec.containers[0].env)"

# Ver en formato JSON
gcloud run services describe tareas-back \
  --region us-west1 \
  --format=json | jq '.spec.template.spec.containers[0].env'

# Ver una variable específica
gcloud run services describe tareas-back \
  --region us-west1 \
  --format="value(spec.template.spec.containers[0].env)" | grep CORS_ORIGINS
```

## 🚀 Workflow Completo

```bash
# 1. Build y Deploy
gcloud builds submit --config cloudbuild.yaml

# 2. Configurar variables de entorno
./configure-env.sh tu-project-id us-west1 tareas-back

# 3. Ver logs para verificar inicio
gcloud run services logs tail tareas-back --region us-west1

# 4. Test endpoints
SERVICE_URL=$(gcloud run services describe tareas-back --region us-west1 --format 'value(status.url)')
curl $SERVICE_URL/livez
curl $SERVICE_URL/readyz

# 5. Test CORS
./test-cors.sh $SERVICE_URL https://your-frontend.com
```

## 📈 Monitoreo Post-Deploy

### Ver métricas en consola
```bash
# Abrir en navegador
echo "https://console.cloud.google.com/run/detail/us-west1/tareas-back/metrics?project=$(gcloud config get-value project)"
```

### Ver logs filtrados
```bash
# Solo errores
gcloud run services logs read tareas-back --region us-west1 \
  --filter="severity=ERROR" --limit 50

# Por timestamp
gcloud run services logs read tareas-back --region us-west1 \
  --filter="timestamp>\"2025-11-19T10:00:00Z\"" --limit 50
```

## 🎯 Puntos Clave

1. **uwsgi debe escuchar en `0.0.0.0:$PORT`** - No solo `:5000`
2. **Todas las variables de entorno deben estar configuradas** antes del primer request
3. **Logs en stdout** (`logto = /dev/stdout`) para que Cloud Run los capture
4. **Reduce procesos** en Cloud Run (1 proceso, múltiples threads)
5. **Timeout generoso** durante testing (300-900s)

## 📚 Archivos Relacionados

- `uwsgi-production.ini` - Configuración uwsgi optimizada ⭐
- `Dockerfile` - Con CMD correcto para Cloud Run ⭐
- `configure-env.sh` - Script interactivo para configurar env vars
- `cloudbuild.yaml` - Build y deploy automatizado
- `deploy-cloudrun.sh` - Deploy manual con validaciones
- `app/startup.py` - Validación de env vars (opcional)

## 🆘 Si Nada Funciona

1. **Deploy sin variables (solo para debug):**
   ```bash
   # Comenta las env vars en cloudbuild.yaml temporalmente
   # Solo para ver si el container inicia
   ```

2. **Test local con Docker:**
   ```bash
   docker build -t test .
   docker run -p 5000:5000 \
     -e postgres_user=test \
     -e postgres_password=test \
     -e postgres_base=localhost:5432/test \
     -e AUTH_URL=https://test.com \
     -e REALM=test \
     -e AUDIENCE=test \
     test
   ```

3. **Ver revisiones anteriores:**
   ```bash
   # Listar revisiones
   gcloud run revisions list --service tareas-back --region us-west1
   
   # Revertir a una que funcionaba
   gcloud run services update-traffic tareas-back \
     --region us-west1 \
     --to-revisions=REVISION_NAME=100
   ```

4. **Contactar soporte:**
   - Logs completos
   - Variables de entorno (sin contraseñas)
   - Output de `gcloud run services describe`
