# 🔍 Análisis de Errores CORS en tu Configuración de Axios

## ❌ Problemas Encontrados

### 1. **Headers CORS en el Cliente (INCORRECTO)**
```javascript
// ❌ NUNCA hagas esto en el cliente:
headers: {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET,OPTIONS,POST,PUT,DELETE",
}
```

**Por qué está mal:**
- Los headers `Access-Control-*` SOLO deben ser enviados por el **servidor**
- El navegador ignora estos headers del cliente
- Pueden causar conflictos con los headers del servidor
- El navegador ve headers duplicados y rechaza la petición

### 2. **Falta Manejo de Errores de Red/CORS**
```javascript
// ❌ No detecta errores CORS específicamente
function (error) {
  return Promise.reject(error);
}
```

**Por qué está mal:**
- No distingue entre error CORS y otros errores de red
- Dificulta el debugging
- No da información útil al usuario

### 3. **No hay Timeout Configurado**
```javascript
const Base = axios.create({
  baseURL: '...',
  // ❌ Sin timeout
});
```

**Por qué está mal:**
- Las peticiones pueden quedarse colgadas indefinidamente
- Mala experiencia de usuario

## ✅ Solución Implementada

### 1. **Headers Correctos**
```javascript
const Base = axios.create({
  baseURL: 'https://tareas-back-809525105092.us-west1.run.app',
  withCredentials: true, // ✅ Para enviar cookies/credenciales
  headers: {
    'Content-Type': 'application/json',
    // ✅ Solo headers que el cliente DEBE enviar
  },
  timeout: 30000, // ✅ 30 segundos
});
```

### 2. **Manejo Mejorado de Errores**
```javascript
function (error) {
  // ✅ Detecta errores CORS específicamente
  if (!error.response) {
    console.error('Network/CORS Error:', error.message);
    
    if (error.message === 'Network Error') {
      console.error('Possible CORS issue. Check:');
      console.error('1. Backend CORS_ORIGINS includes:', window.location.origin);
    }
  }
  
  return Promise.reject(error);
}
```

### 3. **Debugging en Desarrollo**
```javascript
if (import.meta.env.DEV) {
  console.log('Request:', config.method.toUpperCase(), config.url);
  console.log('Headers:', config.headers);
}
```

## 🚀 Implementación

### Paso 1: Reemplaza tu archivo axios actual

Reemplaza el contenido de tu archivo axios (probablemente `src/api/axios.js` o similar) con el contenido de `axios-fixed.js`

### Paso 2: Configura el Backend en Cloud Run

```bash
# ⚠️ CRÍTICO: Configura CORS_ORIGINS con tu dominio frontend
gcloud run services update tareas-back \
  --region us-west1 \
  --set-env-vars="CORS_ORIGINS=https://tu-frontend-domain.com,http://localhost:5173,http://localhost:3000"
```

**📝 Obtén tu origen actual:**
- Abre la consola del navegador en tu frontend
- Ejecuta: `console.log(window.location.origin)`
- Usa ese valor EXACTO en CORS_ORIGINS

### Paso 3: Configura Variables de Entorno en tu Frontend

#### `.env.development`
```env
VITE_APP_BASE_URL=http://localhost:5000
# O si usas Cloud Run en dev:
# VITE_APP_BASE_URL=https://tareas-back-809525105092.us-west1.run.app
```

#### `.env.production`
```env
VITE_APP_BASE_URL=https://tareas-back-809525105092.us-west1.run.app
```

#### Actualiza axios.js para usar la variable:
```javascript
const Base = axios.create({
  baseURL: import.meta.env.VITE_APP_BASE_URL,
  // ... resto de config
});
```

## 🔧 Checklist de Verificación

### En el Backend (Cloud Run):

- [ ] Variable `CORS_ORIGINS` incluye el origen de tu frontend
  ```bash
  gcloud run services describe tareas-back --region us-west1 \
    --format="value(spec.template.spec.containers[0].env)" | grep CORS
  ```

- [ ] Flask-Cors está instalado
  ```bash
  grep Flask-Cors requirements.txt
  ```

- [ ] No hay headers CORS en `uwsgi-production.ini` (ya corregido)

### En el Frontend:

- [ ] ❌ Removidos headers `Access-Control-*` del cliente
- [ ] ✅ `withCredentials: true` si usas autenticación
- [ ] ✅ Timeout configurado
- [ ] ✅ Variables de entorno configuradas

## 🧪 Testing

### Test 1: Verificar que el origen está permitido

Desde la consola del navegador:
```javascript
console.log('Mi origen:', window.location.origin);
// Debe estar en CORS_ORIGINS del backend
```

### Test 2: Test de petición simple

```javascript
import Base from './api/axios';

Base.get('/livez')
  .then(response => console.log('✅ Success:', response.data))
  .catch(error => console.error('❌ Error:', error));
```

### Test 3: Test de petición con headers custom

```javascript
Base.get('/api/usuario')
  .then(response => console.log('✅ Success:', response.data))
  .catch(error => {
    if (error.message === 'Network Error') {
      console.error('❌ CORS Error - Backend CORS_ORIGINS no incluye:', window.location.origin);
    } else {
      console.error('❌ Other Error:', error.message);
    }
  });
```

### Test 4: Usar el test HTML

```bash
# En la raíz del proyecto backend
python3 -m http.server 8080

# Abrir en navegador:
# http://localhost:8080/test-cors.html
```

## 🐛 Troubleshooting

### Error: "Network Error" en axios

**Síntomas:**
```
Error: Network Error
    at createError (createError.js:16)
```

**Causa:** Error CORS - El backend no permite el origen del frontend

**Solución:**
```bash
# 1. Verifica tu origen
console.log(window.location.origin)
# Output: https://tu-frontend.com

# 2. Agrega a CORS_ORIGINS en Cloud Run
gcloud run services update tareas-back \
  --region us-west1 \
  --set-env-vars="CORS_ORIGINS=https://tu-frontend.com,http://localhost:5173"

# 3. Verifica los logs
gcloud run services logs read tareas-back --region us-west1 --limit 50
```

### Error: "Request failed with status code 403"

**Síntomas:**
```
Error: Request failed with status code 403
```

**Causa:** Error de permisos (no CORS)

**Solución:** 
- Verifica headers de autenticación (`x-api-key`, `x-user-role`)
- Revisa que el usuario tenga permisos

### Error: "Request has been blocked by CORS policy"

**Síntomas:**
```
Access to XMLHttpRequest at 'https://...' from origin 'https://...' 
has been blocked by CORS policy: Response to preflight request 
doesn't pass access control check: No 'Access-Control-Allow-Origin' 
header is present on the requested resource.
```

**Causa:** Preflight (OPTIONS) no devuelve headers CORS

**Solución:**
```bash
# Test preflight
curl -X OPTIONS https://tareas-back-809525105092.us-west1.run.app/api/usuario \
  -H "Origin: https://tu-frontend.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v

# Debe responder con:
# access-control-allow-origin: https://tu-frontend.com
# access-control-allow-methods: GET, POST, PUT, PATCH, DELETE, OPTIONS
```

Si no responde correctamente:
```bash
# Redespliega el backend
gcloud run deploy tareas-back \
  --image gcr.io/PROJECT_ID/tareas-back \
  --region us-west1
```

## 📋 Resumen de Cambios en Axios

### Antes (Incorrecto):
```javascript
const Base = axios.create({
  baseURL: '...',
  withCredentials: true,
  headers: {
    "Access-Control-Allow-Origin": "*",        // ❌ MAL
    "Access-Control-Allow-Methods": "...",     // ❌ MAL
  },
});

// Sin manejo de errores CORS
// Sin timeout
```

### Después (Correcto):
```javascript
const Base = axios.create({
  baseURL: '...',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',        // ✅ BIEN
  },
  timeout: 30000,                              // ✅ BIEN
});

// Con manejo de errores CORS
if (!error.response && error.message === 'Network Error') {
  console.error('Possible CORS issue');
}
```

## 🎯 Comandos Rápidos

```bash
# Ver configuración actual Cloud Run
gcloud run services describe tareas-back --region us-west1 \
  --format="value(spec.template.spec.containers[0].env)"

# Actualizar CORS_ORIGINS
gcloud run services update tareas-back --region us-west1 \
  --set-env-vars="CORS_ORIGINS=https://tu-frontend.com,http://localhost:5173"

# Ver logs en tiempo real
gcloud run services logs tail tareas-back --region us-west1

# Test desde terminal
./test-cors.sh https://tareas-back-809525105092.us-west1.run.app https://tu-frontend.com
```

## 📚 Referencias

- `axios-fixed.js` - Configuración correcta de axios
- `test-cors.html` - Test visual CORS
- `test-cors.sh` - Test por línea de comandos
- `FIX_PREFLIGHT_ERROR.md` - Guía completa de errores preflight
- `CORS_CLOUDRUN_SETUP.md` - Configuración CORS para Cloud Run
