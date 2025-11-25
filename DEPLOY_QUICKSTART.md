# 🚀 Deploy a Cloud Run - Guía Rápida

## ❌ Error Build Step 3 - Solución

El error "build step 3 failed: exit status 2" ocurre cuando hay un problema con los argumentos de gcloud deploy.

**Causa:** Múltiples `--set-env-vars` en lugar de uno solo con todas las variables.

**✅ Ya está corregido en `cloudbuild.yaml`**

## 📋 Opciones de Deploy

### Opción 1: Deploy Mínimo + Configurar después (RECOMENDADO) ⭐

**Paso 1 - Deploy sin env vars:**
```bash
gcloud builds submit --config cloudbuild-minimal.yaml
```

**Paso 2 - Configurar env vars:**
```bash
./configure-env.sh tu-project-id us-west1 tareas-back
```

**Ventajas:**
- ✅ No expone credenciales en build logs
- ✅ Deploy rápido
- ✅ Configuración segura después

---

### Opción 2: Deploy con env vars básicas

```bash
gcloud builds submit --config cloudbuild.yaml
```

Luego configura las variables críticas:
```bash
gcloud run services update tareas-back \
  --region us-west1 \
  --update-env-vars="postgres_user=USER,postgres_password=PASS,postgres_base=HOST:5432/DB,AUTH_URL=https://keycloak.com,REALM=realm,AUDIENCE=audience"
```

---

### Opción 3: Deploy con variables personalizadas

```bash
gcloud builds submit \
  --config cloudbuild-with-substitutions.yaml \
  --substitutions=_REGION=us-west1,_CORS_ORIGINS=https://tu-frontend.com,_MEMORY=1Gi
```

---

### Opción 4: Deploy manual (más control)

```bash
./deploy-cloudrun.sh tu-project-id us-west1 tareas-back
```

## 🔧 Comandos Útiles

### Ver estado del build
```bash
# Lista últimos builds
gcloud builds list --limit 5

# Ver detalles de un build
gcloud builds describe BUILD_ID

# Ver logs de un build
gcloud builds log BUILD_ID
```

### Después del deploy

```bash
# Ver URL del servicio
gcloud run services describe tareas-back \
  --region us-west1 \
  --format 'value(status.url)'

# Ver logs del servicio
gcloud run services logs tail tareas-back --region us-west1

# Ver configuración actual
gcloud run services describe tareas-back --region us-west1
```

### Configurar variables de entorno

```bash
# Todas a la vez
gcloud run services update tareas-back \
  --region us-west1 \
  --update-env-vars="VAR1=value1,VAR2=value2,VAR3=value3"

# Una por una
gcloud run services update tareas-back \
  --region us-west1 \
  --set-env-vars="NUEVA_VAR=valor"

# Remover una variable
gcloud run services update tareas-back \
  --region us-west1 \
  --remove-env-vars="VAR_A_REMOVER"

# Ver variables actuales
gcloud run services describe tareas-back \
  --region us-west1 \
  --format="table(spec.template.spec.containers[0].env)"
```

## 🐛 Troubleshooting

### Error: "exit status 2"
**Causa:** Argumentos inválidos en gcloud command
**Solución:** Usa `cloudbuild.yaml` corregido o `cloudbuild-minimal.yaml`

### Error: "Container failed to start"
**Causa:** Variables de entorno faltantes
**Solución:** 
```bash
./configure-env.sh tu-project-id us-west1 tareas-back
```

### Error: "Permission denied"
**Causa:** Permisos insuficientes
**Solución:**
```bash
# Habilitar Cloud Run API
gcloud services enable run.googleapis.com

# Dar permisos a Cloud Build
PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) --format="value(projectNumber)")
gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
  --member=serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com \
  --role=roles/run.admin
```

### Error: "Build timeout"
**Causa:** Build tarda más de 10 minutos
**Solución:** Ya está configurado con `timeout: 1800s` (30 min)

## 📊 Workflow Completo Recomendado

```bash
# 1. Build y deploy (sin env vars sensibles)
gcloud builds submit --config cloudbuild-minimal.yaml

# 2. Configurar variables de entorno
./configure-env.sh tu-project-id us-west1 tareas-back

# 3. Verificar que inició correctamente
gcloud run services logs tail tareas-back --region us-west1

# 4. Obtener URL y probar
SERVICE_URL=$(gcloud run services describe tareas-back --region us-west1 --format 'value(status.url)')
echo "Service URL: $SERVICE_URL"

# 5. Test endpoints
curl $SERVICE_URL/livez
curl $SERVICE_URL/readyz

# 6. Test CORS
./test-cors.sh $SERVICE_URL https://tu-frontend.com
```

## 🎯 Resumen de Archivos

| Archivo | Uso | Cuándo usar |
|---------|-----|-------------|
| `cloudbuild-minimal.yaml` | Deploy sin env vars | ✅ Primera vez / Producción |
| `cloudbuild.yaml` | Deploy con CORS básico | Testing rápido |
| `cloudbuild-with-substitutions.yaml` | Deploy con variables custom | CI/CD avanzado |
| `deploy-cloudrun.sh` | Deploy manual | Desarrollo local |
| `configure-env.sh` | Configurar env vars | Después del deploy |

## 🔐 Seguridad

**NO pongas credenciales en cloudbuild.yaml** porque:
- ❌ Aparecen en logs de Cloud Build
- ❌ Quedan en historial de git
- ❌ Visibles en Cloud Console

**Mejor práctica:**
1. Deploy sin credenciales (`cloudbuild-minimal.yaml`)
2. Configurar con `configure-env.sh` o Secret Manager
3. O usar variables de sustitución desde triggers

## 📚 Más Info

- [FIX_CONTAINER_START_ERROR.md](./FIX_CONTAINER_START_ERROR.md) - Errores de inicio
- [FIX_UWSGI_BUILD_ERROR.md](./FIX_UWSGI_BUILD_ERROR.md) - Errores de compilación
- [CORS_CLOUDRUN_SETUP.md](./CORS_CLOUDRUN_SETUP.md) - Configuración CORS
- [FIX_PREFLIGHT_ERROR.md](./FIX_PREFLIGHT_ERROR.md) - Errores preflight
