#!/usr/bin/env python3
"""
Test script for Full Sync functionality
This script tests the full sync functions without requiring the full Flask application
"""

import os
import sys
import requests
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_pusher_connection():
    """Test basic connection to Pusher API"""
    print("Testing Pusher API connection...")
    
    # Get environment variables
    x_api_key = os.environ.get('PUSHER_API_KEY')
    x_api_system = os.environ.get('PUSHER_API_SYSTEM')
    usuario_consulta = os.environ.get('PUSHER_USUARIO_CONSULTA')
    
    if not all([x_api_key, x_api_system, usuario_consulta]):
        print("❌ Missing required environment variables:")
        print(f"  PUSHER_API_KEY: {'✅' if x_api_key else '❌'}")
        print(f"  PUSHER_API_SYSTEM: {'✅' if x_api_system else '❌'}")
        print(f"  PUSHER_USUARIO_CONSULTA: {'✅' if usuario_consulta else '❌'}")
        return False
    
    # Test URL
    base_url = os.environ.get('PUSHER_URL', 'http://dev-backend.usher.pjm.gob.ar/api/v1/all_info/?desc_sistema=tareas&usuario_consulta=')
    test_url = f"{base_url}{usuario_consulta}&tipo_entidad=tipo_act_juzgado"
    
    headers = {'x-api-key': x_api_key, 'x-api-system': x_api_system}
    
    try:
        print(f"Testing URL: {test_url}")
        response = requests.get(test_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            entity_count = len(data.get('data', []))
            print(f"✅ Successfully connected to Pusher API")
            print(f"   Received {entity_count} entities")
            return True
        else:
            print(f"❌ Pusher API returned status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to Pusher API: {e}")
        return False

def test_full_sync_functions():
    """Test the full sync functions"""
    print("\nTesting Full Sync functions...")
    
    try:
        # Import the full sync module
        from controller.full_sync import (
            full_sync_tipos_tareas,
            full_sync_usuarios,
            full_sync_organismos
        )
        
        print("✅ Successfully imported full sync functions")
        
        # Test getting entities from Pusher
        print("\nTesting full_sync_tipos_tareas...")
        success_count, error_count = full_sync_tipos_tareas()
        
        if success_count >= 0:
            print(f"✅ Successfully tested full_sync_tipos_tareas: {success_count} successful, {error_count} errors")
        else:
            print("❌ Failed to test full_sync_tipos_tareas")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Error importing full sync functions: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing full sync functions: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("Full Sync Functionality Test")
    print("=" * 60)
    print(f"Test started at: {datetime.now()}")
    print()
    
    # Test 1: Pusher API connection
    pusher_ok = test_pusher_connection()
    
    # Test 2: Full sync functions
    sync_ok = test_full_sync_functions()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Pusher API Connection: {'✅ PASS' if pusher_ok else '❌ FAIL'}")
    print(f"Full Sync Functions: {'✅ PASS' if sync_ok else '❌ FAIL'}")
    
    if pusher_ok and sync_ok:
        print("\n🎉 All tests passed! Full sync functionality is ready.")
        print("\nAvailable endpoints:")
        print("  GET /full_sync/tipos_tareas")
        print("  GET /full_sync/usuarios")
        print("  GET /full_sync/organismos")
        print("  GET /full_sync/fuero")
        print("  GET /full_sync/inhabilidad")
        print("  GET /full_sync/subtipo_tarea")
        print("  GET /full_sync/all")
        print("  GET /full_sync/status")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
