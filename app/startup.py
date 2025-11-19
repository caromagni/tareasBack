#!/usr/bin/env python3
"""
Startup script for Cloud Run - validates environment before starting uwsgi
"""
import os
import sys
import subprocess

def check_required_env_vars():
    """Check if critical environment variables are set"""
    critical_vars = {
        'postgres_user': 'Database user',
        'postgres_password': 'Database password', 
        'postgres_base': 'Database connection string',
        'AUTH_URL': 'Keycloak auth URL',
        'REALM': 'Keycloak realm',
        'AUDIENCE': 'JWT audience',
    }
    
    missing = []
    for var, description in critical_vars.items():
        if not os.getenv(var):
            missing.append(f"  - {var} ({description})")
    
    if missing:
        print("❌ ERROR: Missing required environment variables:")
        print("\n".join(missing))
        print("\nConfigure them with:")
        print("gcloud run services update SERVICE_NAME \\")
        print("  --region REGION \\")
        print("  --set-env-vars='postgres_user=USER,postgres_password=PASS,...'")
        return False
    
    return True

def check_optional_env_vars():
    """Warn about optional environment variables"""
    optional_vars = {
        'CORS_ORIGINS': 'http://localhost:5173',
        'CORS_ALLOW_CREDENTIALS': 'true',
        'LOG_LEVEL': 'INFO',
        'RUN_DB_SETUP': '0',
        'RUN_DB_CREATION': '0',
    }
    
    for var, default in optional_vars.items():
        value = os.getenv(var, default)
        print(f"ℹ️  {var}: {value}")

def main():
    print("=" * 60)
    print("🚀 Starting Tareas Backend on Cloud Run")
    print("=" * 60)
    
    # Check environment
    print("\n📋 Checking environment variables...")
    
    if not check_required_env_vars():
        print("\n❌ Cannot start: Missing critical environment variables")
        sys.exit(1)
    
    print("✅ All required environment variables are set")
    
    print("\n📋 Optional environment variables:")
    check_optional_env_vars()
    
    # Get PORT from Cloud Run (default 5000)
    port = os.getenv('PORT', '5000')
    print(f"\n🌐 Starting server on port {port}")
    
    # Start uwsgi
    print("\n🔧 Starting uwsgi...")
    print("=" * 60)
    
    try:
        subprocess.run([
            'uwsgi',
            '--ini', 'uwsgi.ini',
            '--http', f'0.0.0.0:{port}'
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ uwsgi failed with exit code {e.returncode}")
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        print("\n⚠️  Shutting down gracefully...")
        sys.exit(0)

if __name__ == '__main__':
    main()
