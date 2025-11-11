#!/usr/bin/env python3
"""
Health check script for MyShop application
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopsite.settings')

# Setup Django
django.setup()

def check_database():
    """Check database connectivity"""
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✓ Database connection: OK")
        return True
    except Exception as e:
        print(f"✗ Database connection: FAILED - {e}")
        return False

def check_cache():
    """Check cache connectivity"""
    try:
        from django.core.cache import cache
        cache.set('health_check', 'ok', 30)
        if cache.get('health_check') == 'ok':
            print("✓ Cache connection: OK")
            return True
        else:
            print("✗ Cache connection: FAILED")
            return False
    except Exception as e:
        print(f"✗ Cache connection: FAILED - {e}")
        return False

def check_media_directory():
    """Check if media directory exists and is writable"""
    try:
        media_root = os.environ.get('MEDIA_ROOT', 'media')
        if not os.path.exists(media_root):
            os.makedirs(media_root)
        test_file = os.path.join(media_root, 'health_check_test.txt')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print("✓ Media directory: OK")
        return True
    except Exception as e:
        print(f"✗ Media directory: FAILED - {e}")
        return False

def check_static_files():
    """Check if static files directory exists"""
    try:
        static_root = os.environ.get('STATIC_ROOT', 'staticfiles')
        if not os.path.exists(static_root):
            print("⚠ Static files directory does not exist (will be created during collectstatic)")
            return True
        print("✓ Static files directory: OK")
        return True
    except Exception as e:
        print(f"✗ Static files directory: FAILED - {e}")
        return False

def check_required_env_vars():
    """Check if required environment variables are set"""
    required_vars = ['SECRET_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"✗ Missing environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("✓ Required environment variables: OK")
        return True

def main():
    """Run all health checks"""
    print("Running MyShop health checks...")
    print("=" * 40)
    
    checks = [
        check_required_env_vars,
        check_database,
        check_cache,
        check_media_directory,
        check_static_files,
    ]
    
    results = []
    for check in checks:
        results.append(check())
    
    print("=" * 40)
    if all(results):
        print("All health checks passed! ✓")
        return 0
    else:
        print("Some health checks failed! ✗")
        return 1

if __name__ == '__main__':
    sys.exit(main())