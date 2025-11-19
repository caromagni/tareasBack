# 🔧 Cloud Run Container Startup Error - Complete Fix

## ❌ Error You're Seeing

```
The user-provided container failed to start and listen on the port 
defined provided by the PORT=5000 environment variable within the 
allocated timeout.
```

## ✅ Root Causes & Solutions Applied

### 1. **Port Binding Issue** ⭐ CRITICAL
**Problem**: Container must bind to `0.0.0.0:$PORT`, not `127.0.0.1` or just `:5000`

**Fixed in**:
- ✅ `start-uwsgi.sh` - Now explicitly binds to `0.0.0.0:${PORT}`
- ✅ `uwsgi-production.ini` - Removed hardcoded port, uses command-line flag

### 2. **Insufficient Resources**
**Problem**: 512Mi memory and 1 CPU may not be enough for startup

**Fixed in**:
- ✅ `service.yaml` - Increased to 1Gi memory, 2 CPUs
- ✅ `cloudbuild.yaml` - Added `--cpu-boost` for faster startup
- ✅ Added startup probes with 5-minute timeout

### 3. **Missing Environment Variables**
**Problem**: App requires database and auth config to start

**Action Required**: See deployment steps below

---

## 🚀 Deployment Steps

### Step 1: Build and Push Image

```bash
# Set your project ID
export PROJECT_ID="eng-scene-478112-k0"
export REGION="us-west1"

# Build and push
gcloud builds submit --config cloudbuild.yaml \
  --project=$PROJECT_ID
```

This will:
- ✅ Build the Docker image with fixes
- ✅ Push to Google Container Registry
- ✅ Deploy to Cloud Run (but needs env vars!)

### Step 2: Configure Environment Variables

**Option A - Using a script (Recommended)**:

```bash
# Create a temporary env config file
cat > /tmp/cloudrun-env.yaml << 'EOF'
# Database Configuration (REQUIRED)
postgres_user: "your_db_user"
postgres_password: "your_db_password"
postgres_base: "your_host:5432/your_database"

# Keycloak/Auth Configuration (REQUIRED)
AUTH_URL: "https://your-keycloak.com/auth"
REALM: "your-realm"
AUDIENCE: "your-audience"

# CORS (Recommended)
ALLOWED_ORIGINS: "https://your-frontend.com,http://localhost:5173"

# Application Settings
LOG_LEVEL: "INFO"
RUN_DB_SETUP: "0"
RUN_DB_CREATION: "0"
cache_enabled: "False"
EOF

# Apply the configuration
gcloud run services update tareas-back \
  --region=$REGION \
  --env-vars-file=/tmp/cloudrun-env.yaml
```

**Option B - One command with all variables**:

```bash
gcloud run services update tareas-back \
  --region=us-west1 \
  --set-env-vars="postgres_user=YOUR_USER,\
postgres_password=YOUR_PASSWORD,\
postgres_base=YOUR_HOST:5432/YOUR_DB,\
AUTH_URL=https://your-keycloak.com/auth,\
REALM=YOUR_REALM,\
AUDIENCE=YOUR_AUDIENCE,\
ALLOWED_ORIGINS=https://your-frontend.com,\
LOG_LEVEL=INFO,\
RUN_DB_SETUP=0,\
RUN_DB_CREATION=0,\
cache_enabled=False"
```

**Option C - Individual variables (for testing)**:

```bash
# Database
gcloud run services update tareas-back --region=us-west1 \
  --update-env-vars="postgres_user=myuser"
gcloud run services update tareas-back --region=us-west1 \
  --update-env-vars="postgres_password=mypass"
gcloud run services update tareas-back --region=us-west1 \
  --update-env-vars="postgres_base=10.1.2.3:5432/mydb"

# Auth
gcloud run services update tareas-back --region=us-west1 \
  --update-env-vars="AUTH_URL=https://keycloak.example.com/auth"
gcloud run services update tareas-back --region=us-west1 \
  --update-env-vars="REALM=myrealm"
gcloud run services update tareas-back --region=us-west1 \
  --update-env-vars="AUDIENCE=myaudience"
```

### Step 3: Verify Deployment

```bash
# Check service status
gcloud run services describe tareas-back \
  --region=us-west1 \
  --format="value(status.url,status.conditions)"

# Get the service URL
SERVICE_URL=$(gcloud run services describe tareas-back \
  --region=us-west1 \
  --format='value(status.url)')

echo "Service URL: $SERVICE_URL"

# Test health endpoints
curl -v $SERVICE_URL/livez
curl -v $SERVICE_URL/readyz
```

### Step 4: Monitor Logs

```bash
# Stream logs in real-time
gcloud run services logs tail tareas-back \
  --region=us-west1

# View recent logs
gcloud run services logs read tareas-back \
  --region=us-west1 \
  --limit=100
```

**Look for these SUCCESS indicators**:
```
✅ "Starting Tareas Backend"
✅ "PORT: 5000"
✅ "Starting uwsgi on 0.0.0.0:5000..."
✅ "spawned uWSGI master process"
✅ "spawned uWSGI worker 1"
✅ "Database connected: ..."
```

**Look for these ERROR indicators**:
```
❌ "main.py not found"
❌ "Connection refused"
❌ "KeyError: 'postgres_user'"
❌ "could not connect to server"
❌ "Timeout waiting for server"
```

---

## 🔍 Troubleshooting Common Issues

### Issue 1: Container Still Won't Start

**Check logs first**:
```bash
gcloud run services logs read tareas-back \
  --region=us-west1 \
  --limit=200 | grep -E "ERROR|CRITICAL|Exception"
```

**Common causes**:

1. **Database unreachable**
   ```
   Error: could not connect to server
   ```
   
   **Fix**: Verify database connectivity
   ```bash
   # If using Cloud SQL, add connection
   gcloud run services update tareas-back \
     --region=us-west1 \
     --add-cloudsql-instances=PROJECT:REGION:INSTANCE
   
   # Update connection string to use unix socket
   gcloud run services update tareas-back \
     --region=us-west1 \
     --update-env-vars="postgres_base=/cloudsql/PROJECT:REGION:INSTANCE/dbname"
   ```

2. **Missing environment variable**
   ```
   KeyError: 'postgres_user'
   ```
   
   **Fix**: Check current env vars
   ```bash
   gcloud run services describe tareas-back \
     --region=us-west1 \
     --format="table(spec.template.spec.containers[0].env)"
   ```

3. **Port mismatch**
   ```
   Failed to listen on port 5000
   ```
   
   **Fix**: This should be fixed by the code changes. Redeploy.

### Issue 2: Startup Timeout

**Symptoms**: Container takes more than 5 minutes to start

**Solution**: Increase startup probe timeout in `service.yaml`:
```yaml
startupProbe:
  httpGet:
    path: /livez
    port: 5000
  initialDelaySeconds: 10
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 60  # Increase from 30 to 60 (10 minutes max)
```

Then redeploy:
```bash
gcloud run services replace service.yaml --region=us-west1
```

### Issue 3: Memory Errors

**Symptoms**: 
```
Container exceeded memory limit
```

**Solution**: Increase memory
```bash
gcloud run services update tareas-back \
  --region=us-west1 \
  --memory=2Gi
```

### Issue 4: uwsgi Not Starting

**Check if uwsgi is installed**:
```bash
# View build logs
gcloud builds list --limit=1

# Get build details
BUILD_ID=$(gcloud builds list --limit=1 --format="value(id)")
gcloud builds log $BUILD_ID | grep -i uwsgi
```

**Should see**:
```
Successfully installed uWSGI-2.0.XX
```

---

## 🧪 Local Testing

Test the container locally before deploying:

```bash
# Build locally
docker build -t tareas-back-test .

# Run with all required env vars
docker run -p 5000:5000 \
  -e PORT=5000 \
  -e postgres_user=test \
  -e postgres_password=test \
  -e postgres_base=host.docker.internal:5432/testdb \
  -e AUTH_URL=https://test.com/auth \
  -e REALM=test \
  -e AUDIENCE=test \
  -e ALLOWED_ORIGINS=http://localhost:5173 \
  -e cache_enabled=False \
  tareas-back-test

# Test in another terminal
curl http://localhost:5000/livez
curl http://localhost:5000/readyz
curl http://localhost:5000/docs
```

---

## 📋 Pre-Deployment Checklist

Before deploying to Cloud Run, ensure:

### Required Environment Variables
- [ ] `postgres_user` - Database username
- [ ] `postgres_password` - Database password
- [ ] `postgres_base` - Database connection string (host:port/dbname)
- [ ] `AUTH_URL` - Keycloak/Auth server URL
- [ ] `REALM` - Auth realm name
- [ ] `AUDIENCE` - JWT audience

### Recommended Environment Variables
- [ ] `ALLOWED_ORIGINS` - Frontend URLs for CORS
- [ ] `LOG_LEVEL` - Set to INFO or DEBUG
- [ ] `RUN_DB_SETUP` - Set to 0 for production
- [ ] `RUN_DB_CREATION` - Set to 0 for production

### Infrastructure
- [ ] Database is accessible from Cloud Run
- [ ] If using Cloud SQL: connection is configured
- [ ] Keycloak/Auth server is accessible
- [ ] Network/firewall rules allow traffic

### Files Updated
- [x] `Dockerfile` - Fixed COPY order and health check
- [x] `start-uwsgi.sh` - Explicit 0.0.0.0 binding
- [x] `uwsgi-production.ini` - Increased timeouts and logging
- [x] `service.yaml` - Added probes, increased resources
- [x] `cloudbuild.yaml` - Better resource allocation

---

## 🎯 Quick Recovery Commands

If you need to rollback or debug:

```bash
# List all revisions
gcloud run revisions list \
  --service=tareas-back \
  --region=us-west1

# Rollback to previous revision
gcloud run services update-traffic tareas-back \
  --region=us-west1 \
  --to-revisions=PREVIOUS_REVISION_NAME=100

# Get current configuration
gcloud run services describe tareas-back \
  --region=us-west1 \
  --format=yaml > current-config.yaml

# Scale down to zero (stop all instances)
gcloud run services update tareas-back \
  --region=us-west1 \
  --min-instances=0

# Delete and recreate (last resort)
gcloud run services delete tareas-back --region=us-west1
# Then redeploy with cloudbuild.yaml
```

---

## 📊 Monitoring

### View Metrics
```bash
# Open Cloud Console metrics
echo "https://console.cloud.google.com/run/detail/us-west1/tareas-back/metrics?project=$PROJECT_ID"
```

### Set up Alerts
```bash
# CPU usage alert
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="Cloud Run CPU High" \
  --condition-threshold-value=0.8 \
  --condition-threshold-duration=300s

# Request count alert
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="Cloud Run Errors" \
  --condition-threshold-value=10 \
  --condition-threshold-duration=60s
```

---

## 🆘 Still Having Issues?

1. **Capture full logs**:
   ```bash
   gcloud run services logs read tareas-back \
     --region=us-west1 \
     --limit=500 > cloudrun-logs.txt
   ```

2. **Capture configuration**:
   ```bash
   gcloud run services describe tareas-back \
     --region=us-west1 \
     --format=yaml > cloudrun-config.yaml
   ```

3. **Test locally first**:
   Use Docker to reproduce the issue locally (see Local Testing section)

4. **Check Cloud Run documentation**:
   https://cloud.google.com/run/docs/troubleshooting#container-failed-to-start

---

## 📚 Related Files

- `Dockerfile` - Container definition
- `start-uwsgi.sh` - Startup script
- `uwsgi-production.ini` - uWSGI configuration
- `service.yaml` - Cloud Run service definition
- `cloudbuild.yaml` - Build and deploy pipeline
- `app/main.py` - Application entry point with health checks

---

## ✅ Success Criteria

Your deployment is successful when:

1. ✅ Build completes without errors
2. ✅ Container starts within 5 minutes
3. ✅ `/livez` endpoint returns 200 OK
4. ✅ `/readyz` endpoint returns 200 OK
5. ✅ `/docs` (Swagger UI) loads successfully
6. ✅ No ERROR logs in Cloud Run logs
7. ✅ Application responds to API requests

---

**Last Updated**: 2025-11-19
**Version**: 1.0
