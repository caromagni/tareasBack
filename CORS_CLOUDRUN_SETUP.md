# Configuración CORS para Cloud Run

## Cambios Realizados

### 1. Actualización de Config (`app/config/config.py`)
Se agregaron las siguientes variables de configuración:
- `CORS_ORIGINS`: Lista de orígenes permitidos (separados por comas)
- `CORS_ALLOW_CREDENTIALS`: Permite el envío de credenciales

### 2. Actualización de CORS (`app/main.py`)
Se mejoró la configuración de CORS para:
- Usar orígenes específicos en lugar de `*`
- Configurar `supports_credentials` correctamente
- Agregar `expose_headers` para respuestas
- Configurar `max_age` para cachear respuestas preflight

## Configuración en Cloud Run

### Opción 1: Configurar en la consola de Cloud Run

1. Ve a Cloud Run console
2. Selecciona tu servicio
3. Click en "EDIT & DEPLOY NEW REVISION"
4. En la pestaña "Variables & Secrets", agrega:
   ```
   CORS_ORIGINS=https://tu-frontend.com,https://tu-dominio.com
   CORS_ALLOW_CREDENTIALS=true
   ```

### Opción 2: Usando gcloud CLI

```bash
gcloud run services update TU-SERVICIO \
  --set-env-vars="CORS_ORIGINS=https://tu-frontend.com,https://otro-dominio.com" \
  --set-env-vars="CORS_ALLOW_CREDENTIALS=true" \
  --region=REGION
```

### Opción 3: Usando archivo YAML

Agrega en tu `service.yaml`:
```yaml
spec:
  template:
    spec:
      containers:
      - env:
        - name: CORS_ORIGINS
          value: "https://tu-frontend.com,https://otro-dominio.com"
        - name: CORS_ALLOW_CREDENTIALS
          value: "true"
```

## Configuración en el Frontend (React + Vite)

### 1. Configurar axios o fetch con credenciales:

```javascript
// axios
import axios from 'axios';

const api = axios.create({
  baseURL: 'https://tu-backend-cloudrun.run.app',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
    'x-api-key': 'tu-api-key'
  }
});

export default api;
```

```javascript
// fetch
fetch('https://tu-backend-cloudrun.run.app/api/endpoint', {
  method: 'POST',
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
    'x-api-key': 'tu-api-key'
  },
  body: JSON.stringify(data)
});
```

### 2. Configurar variables de entorno en Vite:

Crea archivo `.env.production`:
```
VITE_API_URL=https://tu-backend-cloudrun.run.app
VITE_API_KEY=tu-api-key
```

Usa en tu código:
```javascript
const API_URL = import.meta.env.VITE_API_URL;
const API_KEY = import.meta.env.VITE_API_KEY;
```

## Verificación

### 1. Verifica que las variables estén configuradas:
```bash
gcloud run services describe TU-SERVICIO --region=REGION --format="value(spec.template.spec.containers[0].env)"
```

### 2. Prueba con curl:
```bash
curl -H "Origin: https://tu-frontend.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -X OPTIONS \
  --verbose \
  https://tu-backend-cloudrun.run.app/api/endpoint
```

Deberías ver en la respuesta:
```
Access-Control-Allow-Origin: https://tu-frontend.com
Access-Control-Allow-Methods: GET, PUT, POST, DELETE, PATCH, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization, ...
```

## Troubleshooting

### Error: "preflightMissingAllowOriginHeader"
Este es el error más común y significa que la respuesta OPTIONS no incluye `Access-Control-Allow-Origin`.

**Diagnóstico:**
```bash
# Test preflight request
curl -X OPTIONS https://tu-servicio.run.app/api/endpoint \
  -H "Origin: https://tu-frontend.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v
```

**Causas comunes:**
1. La variable `CORS_ORIGINS` no está configurada o no incluye tu frontend
2. Flask-CORS no está instalado correctamente
3. La configuración de CORS tiene un error de sintaxis

**Soluciones:**

1. **Verificar y configurar CORS_ORIGINS en Cloud Run:**
```bash
# Ver configuración actual
gcloud run services describe TU-SERVICIO --region REGION --format="value(spec.template.spec.containers[0].env)"

# Configurar correctamente (IMPORTANTE: sin espacios después de las comas)
gcloud run services update TU-SERVICIO \
  --region REGION \
  --set-env-vars="CORS_ORIGINS=https://tu-frontend.com,http://localhost:5173"
```

2. **Verificar que Flask-CORS esté en requirements.txt:**
```bash
grep Flask-Cors requirements.txt
# Debe aparecer: Flask-Cors==4.0.1
```

3. **Test local antes de desplegar:**
```bash
# Abrir test-cors.html en el navegador
python3 -m http.server 8080
# Luego abre: http://localhost:8080/test-cors.html
```

4. **Usar el script de test:**
```bash
./test-cors.sh https://tu-servicio.run.app https://tu-frontend.com
```

### Error: "No 'Access-Control-Allow-Origin' header"
- Verifica que la URL del frontend esté en `CORS_ORIGINS`
- Asegúrate de incluir el protocolo (https://)
- No uses espacios en la lista de orígenes

### Error: "CORS policy: Credentials flag is 'true'"
- Si usas credenciales, no puedes usar `origins: "*"`
- Debes especificar orígenes exactos

### Error: Preflight request failed
- Verifica que el método OPTIONS esté permitido
- Revisa los headers en `allow_headers`
- Comprueba que el servicio esté respondiendo correctamente

### Para desarrollo local:
En tu archivo `.env` local:
```
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
CORS_ALLOW_CREDENTIALS=true
```

## Notas Importantes

1. **No uses `origins: "*"` con credenciales**: Si necesitas enviar cookies o headers de autenticación, debes especificar orígenes exactos.

2. **Siempre incluye el protocolo**: Usa `https://` o `http://` en los orígenes.

3. **Sin barra final**: No incluyas `/` al final de las URLs.

4. **Wildcard subdominios**: Si necesitas permitir todos los subdominios, puedes usar lógica personalizada o listar cada subdominio explícitamente.

5. **Cloud Run + Load Balancer**: Si usas un Load Balancer delante de Cloud Run, asegúrate de que también permita los headers CORS.

## Testing Rápido

Para probar rápidamente sin desplegar:
```python
# En development, puedes temporalmente usar:
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,*
```

Pero **NUNCA** uses `*` en producción si envías credenciales.
