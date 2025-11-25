# 🔧 Solución al Error: Container Failed to Start

## ❌ Error Original
```
The user-provided container failed to start and listen on the port defined 
provided by the PORT=5000 environment variable within the allocated timeout.
```

## ✅ Cambios Realizados

### 1. **uwsgi-production.ini Simplificado**
- Eliminadas configuraciones complejas que podían causar timeouts
- Timeouts reducidos a 60 segundos (más rápido)
- Logging directo a stdout (Cloud Run requirement)

### 2. **start-uwsgi.sh Mejorado**
- Agregado logging detallado del inicio
- Verificación de archivos antes de iniciar
- Mejor manejo de la variable PORT

### 3. **main.py Más Resiliente**
- Try-catch en inicialización de base de datos
- Validación de configuración antes de intentar conectar
- Fallback a dummy connection si BD no está configurada
- Logging claro de cada paso del inicio

### 4. **config.py Con Defaults**
- Agregado default para `postgres_base` (antes causaba None → crash)
- Ahora la app puede iniciar incluso sin BD configurada

### 5. **cloudbuild.yaml Optimizado**
- Agregado `--startup-cpu-boost` para inicio más rápido
- `--no-cpu-throttling` para evitar throttling durante startup

## 🚀 Cómo Desplegar

### Paso 1: Probar Localmente (Recomendado)

```bash
./test-docker-local.sh
```

Este script:
- Construye la imagen Docker
- La ejecuta localmente en puerto 5000
- Prueba los endpoints de health check
- Muestra los logs

### Paso 2: Desplegar a Cloud Run

```bash
gcloud builds submit --config cloudbuild.yaml
```

### Paso 3: Verificar que las Variables de Entorno Estén Configuradas

**CRÍTICO**: Estas variables DEBEN estar configuradas en Cloud Run:

```bash
# Verificar variables actuales
gcloud run services describe tareas-back --region us-west1 --format="value(spec.template.spec.containers[0].env)"

# Configurar variables faltantes
gcloud run services update tareas-back \
  --region us-west1 \
  --set-env-vars "postgres_user=TU_USUARIO" \
  --set-env-vars "postgres_password=TU_PASSWORD" \
  --set-env-vars "postgres_base=TU_HOST:PUERTO/DB"
```

## 🔍 Debugging

### Ver Logs en Tiempo Real

```bash
# Mientras se despliega
gcloud run services logs tail tareas-back --region us-west1

# Últimos logs
gcloud run services logs read tareas-back --region us-west1 --limit 100
```

### Buscar Errores Específicos

```bash
# Ver logs del startup
gcloud run services logs read tareas-back --region us-west1 \
  --limit 200 | grep -A5 "Starting Tareas Backend"

# Ver errores de database
gcloud run services logs read tareas-back --region us-west1 \
  --limit 200 | grep -i "database\|postgres\|error"
```

### Verificar que el Puerto se Esté Usando Correctamente

En los logs deberías ver:
```
Starting Tareas Backend
==========================================
PORT: 5000  (o 8080 si Cloud Run lo asigna diferente)
```

## 🐛 Problemas Comunes

### 1. "Container failed to start" pero sin errores en logs
**Causa**: Variables de entorno faltantes, especialmente la BD

**Solución**: 
```bash
# Configurar TODAS las variables necesarias
gcloud run services update tareas-back \
  --region us-west1 \
  --set-env-vars "postgres_user=USER,postgres_password=PASS,postgres_base=HOST:PORT/DB,AUTH_URL=URL,REALM=realm,AUDIENCE=aud"
```

### 2. "Connection refused" o timeout en DB
**Causa**: PostgreSQL no es accesible desde Cloud Run

**Soluciones**:
- Si usas Cloud SQL: Usa el conector de Cloud SQL
- Si usas PostgreSQL externo: Verifica firewall y permite IPs de Cloud Run
- Para testing: Usa `RUN_DB_SETUP=0` y `RUN_DB_CREATION=0`

### 3. El contenedor se reinicia en loop
**Causa**: La app está crasheando después de iniciar

**Solución**: Ver logs completos
```bash
gcloud run services logs read tareas-back --region us-west1 --limit 500
```

### 4. CORS errors después de desplegar
**Causa**: `ALLOWED_ORIGINS` no incluye tu dominio frontend

**Solución**:
```bash
gcloud run services update tareas-back \
  --region us-west1 \
  --set-env-vars "ALLOWED_ORIGINS=http://localhost:3000,https://tu-frontend.run.app"
```

## 📋 Checklist Pre-Despliegue

- [ ] Probar imagen Docker localmente con `./test-docker-local.sh`
- [ ] Verificar que `start-uwsgi.sh` tiene permisos de ejecución
- [ ] Configurar variables de entorno en Cloud Run
- [ ] Verificar acceso a PostgreSQL desde Cloud Run
- [ ] Configurar `ALLOWED_ORIGINS` con el dominio del frontend
- [ ] Revisar que `RUN_DB_SETUP=0` y `RUN_DB_CREATION=0` (a menos que necesites lo contrario)

## 📞 Si Aún No Funciona

1. **Ejecuta localmente primero**:
   ```bash
   ./test-docker-local.sh
   ```

2. **Revisa los logs completos**:
   ```bash
   gcloud run services logs read tareas-back --region us-west1 --limit 500 > logs.txt
   cat logs.txt | grep -i "error\|warning\|failed"
   ```

3. **Verifica las variables de entorno**:
   ```bash
   gcloud run services describe tareas-back --region us-west1 \
     --format="table(spec.template.spec.containers[0].env)"
   ```

4. **Intenta con configuración mínima**:
   ```bash
   # Deploy con solo variables esenciales
   gcloud run deploy tareas-back \
     --source . \
     --region us-west1 \
     --allow-unauthenticated \
     --port 5000 \
     --set-env-vars "ALLOWED_ORIGINS=http://localhost:3000"
   ```

## 🎯 Próximos Pasos

Una vez que el contenedor inicie correctamente:

1. Configurar base de datos real
2. Configurar secretos con Secret Manager
3. Ajustar recursos (CPU/memoria) según necesidad
4. Configurar alertas y monitoreo
5. Configurar autoscaling apropiado
