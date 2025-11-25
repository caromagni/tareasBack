# 🔧 FIX: preflightMissingAllowOriginHeader

## ¿Qué es este error?

El navegador hace una petición OPTIONS (preflight) antes de la petición real, pero el servidor no devuelve el header `Access-Control-Allow-Origin`, causando que el navegador bloquee la petición.

## ✅ Solución Rápida

### 1. Configurar variable de entorno en Cloud Run

```bash
gcloud run services update TU-SERVICIO-NAME \
  --region us-central1 \
  --set-env-vars="CORS_ORIGINS=https://tu-frontend.com,http://localhost:5173,CORS_ALLOW_CREDENTIALS=true"
```

**⚠️ IMPORTANTE:** 
- Reemplaza `https://tu-frontend.com` con la URL EXACTA de tu frontend
- NO uses espacios después de las comas
- Incluye el protocolo (https:// o http://)
- NO incluyas barra final (/)

### 2. Verificar que funciona

Opción A - Script de test:
```bash
./test-cors.sh https://tu-servicio.run.app https://tu-frontend.com
```

Opción B - Curl manual:
```bash
curl -X OPTIONS https://tu-servicio.run.app/api/usuario \
  -H "Origin: https://tu-frontend.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v
```

Deberías ver:
```
< access-control-allow-origin: https://tu-frontend.com
< access-control-allow-methods: GET, POST, PUT, PATCH, DELETE, OPTIONS
< access-control-allow-headers: Content-Type, Authorization, ...
```

Opción C - Test visual (navegador):
```bash
# Sirve el archivo HTML
python3 -m http.server 8080

# Abre en el navegador:
# http://localhost:8080/test-cors.html
```

## 🔍 Diagnóstico

### Verificar configuración actual:

```bash
# Ver todas las variables de entorno
gcloud run services describe TU-SERVICIO \
  --region us-central1 \
  --format="value(spec.template.spec.containers[0].env)"

# Ver solo CORS_ORIGINS
gcloud run services describe TU-SERVICIO \
  --region us-central1 \
  --format="value(spec.template.spec.containers[0].env)" | grep CORS
```

### Ver logs en tiempo real:

```bash
gcloud run services logs read TU-SERVICIO \
  --region us-central1 \
  --limit 50 \
  --format "table(timestamp, textPayload)"
```

## 🚀 Cambios Realizados en el Código

### 1. `app/config/config.py`
```python
# Parsea correctamente la lista de orígenes
_cors_origins_str = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://localhost:3000')
CORS_ORIGINS = [origin.strip() for origin in _cors_origins_str.split(',') if origin.strip()]
CORS_ALLOW_CREDENTIALS = os.getenv('CORS_ALLOW_CREDENTIALS', 'true').lower() == 'true'
```

### 2. `app/main.py`
```python
# Configuración explícita de CORS
CORS(app, resources={r"/*": cors_config})

# Handler adicional para preflight
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        # Maneja explícitamente OPTIONS requests
```

## 📝 Frontend - Configuración Correcta

### React + Vite + Axios

```javascript
// src/api/axios.js
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'https://tu-servicio.run.app',
  withCredentials: true, // Si usas cookies/autenticación
  headers: {
    'Content-Type': 'application/json',
  }
});

// Agregar API key si es necesario
api.interceptors.request.use(config => {
  const apiKey = import.meta.env.VITE_API_KEY;
  if (apiKey) {
    config.headers['x-api-key'] = apiKey;
  }
  return config;
});

export default api;
```

### Archivo `.env.production` (Frontend)
```env
VITE_API_URL=https://tu-servicio.run.app
VITE_API_KEY=tu-api-key
```

### Archivo `.env.local` (Frontend - desarrollo)
```env
VITE_API_URL=http://localhost:5000
VITE_API_KEY=tu-api-key
```

### Usar en componentes:
```javascript
import api from './api/axios';

// GET
const response = await api.get('/api/usuario');

// POST
const response = await api.post('/api/usuario', { nombre: 'Juan' });

// Con headers personalizados
const response = await api.get('/api/usuario', {
  headers: {
    'x-user-role': 'admin'
  }
});
```

## 🐛 Errores Comunes y Soluciones

### ❌ Error: "The CORS policy... credentials flag is 'true'"
**Causa:** Usas `withCredentials: true` pero CORS_ORIGINS tiene "*"

**Solución:**
```bash
# NO uses "*" con credenciales
gcloud run services update TU-SERVICIO \
  --set-env-vars="CORS_ORIGINS=https://tu-frontend.com"  # URLs específicas
```

### ❌ Error: "Origin http://localhost:5173 is not allowed"
**Causa:** CORS_ORIGINS no incluye localhost para desarrollo

**Solución:**
```bash
gcloud run services update TU-SERVICIO \
  --set-env-vars="CORS_ORIGINS=https://tu-frontend.com,http://localhost:5173"
```

### ❌ Error: Headers duplicados
**Causa:** uwsgi.ini tiene headers CORS Y Flask-CORS también

**Solución:** Ya está arreglado en `uwsgi-production.ini` (headers CORS removidos)

### ❌ Error: Request timeout
**Causa:** Backend tarda más de 300 segundos

**Solución:**
```bash
gcloud run services update TU-SERVICIO \
  --timeout 900  # Máximo: 3600s (1 hora)
```

## 📦 Checklist de Despliegue

Antes de desplegar, verifica:

- [ ] `requirements.txt` incluye `Flask-Cors==4.0.1`
- [ ] `CORS_ORIGINS` configurado con URLs exactas
- [ ] No hay espacios en la lista de orígenes
- [ ] Protocolo incluido (https:// o http://)
- [ ] Sin barra final en las URLs
- [ ] Variables de DB configuradas
- [ ] Health checks responden: `/readyz` y `/livez`

## 🔄 Workflow Completo

```bash
# 1. Build y push
docker build --platform linux/amd64 -t gcr.io/PROJECT/tareas-backend .
docker push gcr.io/PROJECT/tareas-backend

# 2. Deploy
gcloud run deploy tareas-backend \
  --image gcr.io/PROJECT/tareas-backend \
  --region us-central1 \
  --set-env-vars="CORS_ORIGINS=https://tu-frontend.com"

# 3. Test
./test-cors.sh https://tareas-backend-xxx-uc.a.run.app https://tu-frontend.com

# 4. Ver logs
gcloud run services logs tail tareas-backend --region us-central1
```

## 📚 Archivos de Ayuda

- `test-cors.sh` - Script de test CORS por línea de comandos
- `test-cors.html` - Test visual CORS en navegador
- `CORS_CLOUDRUN_SETUP.md` - Documentación completa
- `DOCKER_UWSGI_CLOUDRUN.md` - Configuración Docker + uwsgi
- `deploy-cloudrun.sh` - Script de deploy automatizado

## 🆘 Soporte

Si el error persiste después de aplicar estos cambios:

1. Verifica los logs:
   ```bash
   gcloud run services logs read tareas-backend --limit 100
   ```

2. Comprueba la configuración:
   ```bash
   gcloud run services describe tareas-backend --format json | grep -A5 env
   ```

3. Test directo a Cloud Run:
   ```bash
   curl -v https://tu-servicio.run.app/livez
   ```

4. Revisa el código en `app/main.py` líneas 169-210 (configuración CORS)
