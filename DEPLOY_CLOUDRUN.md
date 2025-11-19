# Deploy a Cloud Run - Guía Rápida

## ✅ Cambios Realizados

### 1. Arreglado problema de CORS
- Agregado `ALLOWED_ORIGINS` en `config.py`
- Actualizado CORS en `main.py` con soporte para múltiples orígenes
- Por defecto permite: `http://localhost:3000,http://localhost:5173`

### 2. Arreglado problema de inicio en Cloud Run
- Agregado manejo seguro de `uwsgi.worker_id()` con try-except
- Creado script `start-uwsgi.sh` para manejar variable PORT dinámicamente
- Actualizado Dockerfile para usar el script de inicio

### 3. Configuración del puerto
- Cloud Run usa la variable `PORT` (por defecto 8080, pero puedes configurar 5000)
- El script `start-uwsgi.sh` lee la variable y configura uwsgi correctamente

## 🚀 Desplegar a Cloud Run

### Paso 1: Configurar variables de entorno

Asegúrate de tener estas variables configuradas en Cloud Run:

```bash
# Variables obligatorias
postgres_user=tu_usuario
postgres_password=tu_password
postgres_base=tu_conexion_postgresql

# Variables de JWT/Auth
AUTH_URL=https://tu-keycloak.com/auth
REALM=tu-realm
AUDIENCE=tu-audience

# CORS - IMPORTANTE: Agrega tu frontend aquí
ALLOWED_ORIGINS=https://tu-frontend.run.app,https://otro-dominio.com

# Redis (si usas caché)
redis_host=tu-redis-host
redis_port=6379
redis_password=tu-password
redis_user=default
redis_db=0
redis_uses_password=True
cache_enabled=True

# RabbitMQ (si usas mensajería)
RABBITMQ_USER=usuario
RABBITMQ_PASSWORD=password
RABBITMQ_HOST=host
RABBITMQ_PORT=5672
RABBITMQ_VHOST=/

# Configuración opcional
RUN_DB_SETUP=0
RUN_DB_CREATION=0
SQLALCHEMY_POOL_SIZE=5
MAX_ITEMS_PER_RESPONSE=100
LOG_LEVEL=INFO
ALL_USERS_SUPERADMIN=0
```

### Paso 2: Desplegar usando gcloud

```bash
# Autenticar
gcloud auth login
gcloud config set project TU_PROJECT_ID

# Build y Deploy en un solo comando
gcloud run deploy tareas-back \
  --source . \
  --region us-west1 \
  --allow-unauthenticated \
  --set-env-vars "ALLOWED_ORIGINS=https://tu-frontend.run.app" \
  --set-env-vars "postgres_user=USER,postgres_password=PASS,postgres_base=CONNECTION_STRING" \
  --min-instances 0 \
  --max-instances 10 \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --port 5000
```

### Paso 3: O usar Cloud Build (si tienes cloudbuild.yaml)

```bash
gcloud builds submit --config cloudbuild.yaml
```

## 🔧 Verificar Logs

Si el despliegue falla, revisa los logs:

```bash
# Ver logs del servicio
gcloud run services logs read tareas-back --region us-west1 --limit 50

# O en la consola web
https://console.cloud.google.com/run?project=TU_PROJECT
```

## 🐛 Troubleshooting

### Error: Container failed to start
- ✅ **ARREGLADO**: Ahora el contenedor usa `start-uwsgi.sh` que maneja PORT correctamente
- Verifica que todas las variables de entorno estén configuradas
- Revisa los logs para ver errores de conexión a BD o Redis

### Error: CORS
- ✅ **ARREGLADO**: Configuración de CORS actualizada
- Asegúrate de agregar tu dominio frontend en `ALLOWED_ORIGINS`
- Formato: `https://dominio1.com,https://dominio2.com` (sin espacios)

### Error: uwsgi.worker_id()
- ✅ **ARREGLADO**: Ahora hay try-except que previene crashes
- Los threads de background se ejecutan de forma segura

### El contenedor se reinicia constantemente
- Verifica conexión a PostgreSQL (debe ser accesible desde Cloud Run)
- Revisa que los health checks `/livez` y `/readyz` respondan correctamente
- Si usas Cloud SQL, asegúrate de usar el conector correcto

## 📝 Notas Importantes

1. **Health Checks**: El servicio tiene dos endpoints:
   - `/livez` - Liveness probe (siempre debe responder 200)
   - `/readyz` - Readiness probe (verifica conexión a BD)

2. **Puerto**: Cloud Run asigna PORT automáticamente (usualmente 8080), pero puedes forzar 5000 con `--port 5000`

3. **CORS**: Recuerda actualizar `ALLOWED_ORIGINS` cada vez que cambies el dominio del frontend

4. **Base de datos**: Asegúrate de que la BD esté accesible desde Cloud Run:
   - Si usas Cloud SQL, usa el conector de Cloud SQL
   - Si usas PostgreSQL externo, verifica firewall y IP allowlist

## 🔗 URLs útiles

- Consola Cloud Run: https://console.cloud.google.com/run
- Logs: https://console.cloud.google.com/logs
- Documentación: https://cloud.google.com/run/docs

## ✨ Próximos pasos

Después del despliegue exitoso:
1. Prueba los endpoints con Postman o curl
2. Verifica CORS desde tu frontend React
3. Monitorea logs en producción
4. Configura alertas para errores 5xx
