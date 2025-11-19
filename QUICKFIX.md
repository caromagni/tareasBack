# 🚀 Quick Fix Reference - Cloud Run Startup Error

## The Problem
```
Container failed to start and listen on the port defined provided by 
the PORT=5000 environment variable within the allocated timeout.
```

## The Solution (TL;DR)

### 1️⃣ Quick Deploy (Automated)
```bash
./fix-and-deploy.sh
```
Follow the prompts to configure environment variables.

### 2️⃣ Manual Deploy
```bash
# Build and deploy
gcloud builds submit --config cloudbuild.yaml

# Configure required env vars
gcloud run services update tareas-back --region=us-west1 \
  --set-env-vars="postgres_user=USER,\
postgres_password=PASS,\
postgres_base=HOST:5432/DB,\
AUTH_URL=https://auth.example.com,\
REALM=myrealm,\
AUDIENCE=myaudience"

# Check logs
gcloud run services logs tail tareas-back --region=us-west1
```

## What Was Fixed

### ✅ Code Changes
| File | Change | Why |
|------|--------|-----|
| `Dockerfile` | Reordered COPY commands | Ensures main.py is in correct location |
| `Dockerfile` | Added health check | Improves local testing |
| `start-uwsgi.sh` | Explicit `0.0.0.0:$PORT` binding | Cloud Run requires binding to all interfaces |
| `uwsgi-production.ini` | Increased timeouts (120s) | Allows more time for initialization |
| `uwsgi-production.ini` | More threads (4 vs 2) | Better performance |
| `service.yaml` | Added startup/liveness probes | Gives container 5 mins to start |
| `service.yaml` | Increased to 2 CPU, 1Gi memory | More resources for startup |
| `cloudbuild.yaml` | Added `--cpu-boost` flag | Faster container initialization |

### ⚠️ Configuration Required
You **MUST** set these environment variables:
- `postgres_user` - Database username
- `postgres_password` - Database password
- `postgres_base` - Connection string (host:port/database)
- `AUTH_URL` - Authentication server URL
- `REALM` - Auth realm name
- `AUDIENCE` - JWT audience

## Verification Checklist

After deployment, verify:

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe tareas-back \
  --region=us-west1 --format='value(status.url)')

# Test endpoints
curl $SERVICE_URL/livez          # Should return {"status":"live"}
curl $SERVICE_URL/readyz         # Should return {"status":"ready"}
curl $SERVICE_URL/docs           # Should load Swagger UI
```

## Common Issues

### Issue: "main.py not found"
**Cause**: COPY command issue in Dockerfile  
**Status**: ✅ Fixed in new Dockerfile

### Issue: "Connection refused"
**Cause**: Not binding to 0.0.0.0  
**Status**: ✅ Fixed in start-uwsgi.sh

### Issue: "Database connection failed"
**Cause**: Missing or wrong postgres_* env vars  
**Fix**: Configure env vars (see step 2 above)

### Issue: "KeyError: 'AUTH_URL'"
**Cause**: Missing authentication env vars  
**Fix**: Configure AUTH_URL, REALM, AUDIENCE

### Issue: Timeout during startup
**Cause**: App takes too long to initialize  
**Status**: ✅ Fixed with startup probes in service.yaml

## Quick Commands

```bash
# View real-time logs
gcloud run services logs tail tareas-back --region=us-west1

# View current configuration
gcloud run services describe tareas-back --region=us-west1

# Update single env var
gcloud run services update tareas-back --region=us-west1 \
  --update-env-vars="KEY=VALUE"

# Rollback to previous version
gcloud run revisions list --service=tareas-back --region=us-west1
gcloud run services update-traffic tareas-back --region=us-west1 \
  --to-revisions=REVISION_NAME=100

# Test CORS
curl -X OPTIONS $SERVICE_URL/api/usuario \
  -H "Origin: https://your-frontend.com" \
  -H "Access-Control-Request-Method: POST" -v
```

## Files Modified

- ✅ `Dockerfile` - Fixed COPY order and added health check
- ✅ `start-uwsgi.sh` - Explicit 0.0.0.0 binding
- ✅ `uwsgi-production.ini` - Better timeouts and logging
- ✅ `service.yaml` - Startup probes and more resources
- ✅ `cloudbuild.yaml` - CPU boost and clean env vars
- 📄 `DEPLOY_FIX.md` - Detailed troubleshooting guide
- 📄 `fix-and-deploy.sh` - Automated deployment script

## Next Steps

1. **Deploy**: Run `./fix-and-deploy.sh` or follow manual steps
2. **Configure**: Set all required environment variables
3. **Verify**: Test health endpoints
4. **Monitor**: Watch logs for any errors
5. **Test**: Verify your API endpoints work

## Need Help?

See detailed guide: `DEPLOY_FIX.md`

---
**Last Updated**: 2025-11-19
