#!/usr/bin/env python
"""
Production environment setup script for MyShop e-commerce platform
This script helps configure environment variables for production deployment
"""

import os
import sys
import secrets
import boto3
from pathlib import Path

def generate_secret_key():
    """Generate a secure secret key"""
    return secrets.token_urlsafe(50)

def setup_aws_credentials():
    """Guide user through AWS credentials setup"""
    print("=== AWS Credentials Setup ===")
    print("Please provide your AWS credentials for S3 storage and backups:")
    
    aws_access_key = input("AWS Access Key ID: ").strip()
    aws_secret_key = input("AWS Secret Access Key: ").strip()
    aws_region = input("AWS Region (default: us-east-1): ").strip() or "us-east-1"
    s3_bucket = input("S3 Bucket Name: ").strip()
    
    return {
        'AWS_ACCESS_KEY_ID': aws_access_key,
        'AWS_SECRET_ACCESS_KEY': aws_secret_key,
        'AWS_S3_REGION_NAME': aws_region,
        'AWS_STORAGE_BUCKET_NAME': s3_bucket
    }

def setup_database_config():
    """Guide user through database configuration"""
    print("\n=== Database Configuration ===")
    print("Please provide your database configuration:")
    
    db_name = input("Database Name (default: myshop): ").strip() or "myshop"
    db_user = input("Database User: ").strip()
    db_password = input("Database Password: ").strip()
    db_host = input("Database Host: ").strip()
    db_port = input("Database Port (default: 5432): ").strip() or "5432"
    
    return {
        'DB_NAME': db_name,
        'DB_USER': db_user,
        'DB_PASSWORD': db_password,
        'DB_HOST': db_host,
        'DB_PORT': db_port
    }

def setup_redis_config():
    """Guide user through Redis configuration"""
    print("\n=== Redis Configuration ===")
    print("Please provide your Redis configuration:")
    
    redis_url = input("Redis URL (default: redis://localhost:6379/1): ").strip() or "redis://localhost:6379/1"
    
    return {
        'REDIS_URL': redis_url
    }

def setup_email_config():
    """Guide user through email configuration"""
    print("\n=== Email Configuration ===")
    print("Please provide your email configuration (for alerts):")
    
    smtp_server = input("SMTP Server (e.g., smtp.gmail.com): ").strip()
    smtp_port = input("SMTP Port (default: 587): ").strip() or "587"
    smtp_user = input("SMTP Username/Email: ").strip()
    smtp_password = input("SMTP Password: ").strip()
    alert_email = input("Alert Email Address: ").strip()
    
    return {
        'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
        'EMAIL_HOST': smtp_server,
        'EMAIL_PORT': smtp_port,
        'EMAIL_USE_TLS': 'True',
        'EMAIL_HOST_USER': smtp_user,
        'EMAIL_HOST_PASSWORD': smtp_password,
        'ALERT_EMAIL': alert_email
    }

def setup_domain_config():
    """Guide user through domain configuration"""
    print("\n=== Domain Configuration ===")
    print("Please provide your domain configuration:")
    
    domain = input("Domain Name (e.g., yourdomain.com): ").strip()
    allowed_hosts = input("Allowed Hosts (comma separated, default: yourdomain.com,www.yourdomain.com): ").strip() or f"{domain},www.{domain}"
    
    return {
        'DOMAIN': domain,
        'ALLOWED_HOSTS': allowed_hosts
    }

def generate_env_file(env_vars, filename='.env.prod'):
    """Generate environment file"""
    env_path = Path(filename)
    
    with open(env_path, 'w') as f:
        f.write("# MyShop Production Environment Variables\n")
        f.write("# Generated on: $(date)\n\n")
        
        # Security settings
        f.write("# Security Settings\n")
        f.write(f"SECRET_KEY={env_vars.get('SECRET_KEY', generate_secret_key())}\n")
        f.write("DEBUG=0\n\n")
        
        # Domain settings
        f.write("# Domain Settings\n")
        f.write(f"DOMAIN={env_vars.get('DOMAIN', 'yourdomain.com')}\n")
        f.write(f"ALLOWED_HOSTS={env_vars.get('ALLOWED_HOSTS', 'yourdomain.com,www.yourdomain.com')}\n\n")
        
        # Database settings
        f.write("# Database Settings\n")
        f.write(f"DB_ENGINE=django.db.backends.postgresql\n")
        f.write(f"DB_NAME={env_vars.get('DB_NAME', 'myshop')}\n")
        f.write(f"DB_USER={env_vars.get('DB_USER', '')}\n")
        f.write(f"DB_PASSWORD={env_vars.get('DB_PASSWORD', '')}\n")
        f.write(f"DB_HOST={env_vars.get('DB_HOST', '')}\n")
        f.write(f"DB_PORT={env_vars.get('DB_PORT', '5432')}\n\n")
        
        # Redis settings
        f.write("# Redis Settings\n")
        f.write(f"REDIS_URL={env_vars.get('REDIS_URL', 'redis://localhost:6379/1')}\n\n")
        
        # AWS settings
        f.write("# AWS Settings\n")
        f.write(f"AWS_ACCESS_KEY_ID={env_vars.get('AWS_ACCESS_KEY_ID', '')}\n")
        f.write(f"AWS_SECRET_ACCESS_KEY={env_vars.get('AWS_SECRET_ACCESS_KEY', '')}\n")
        f.write(f"AWS_S3_REGION_NAME={env_vars.get('AWS_S3_REGION_NAME', 'us-east-1')}\n")
        f.write(f"AWS_STORAGE_BUCKET_NAME={env_vars.get('AWS_STORAGE_BUCKET_NAME', '')}\n\n")
        
        # Email settings
        f.write("# Email Settings\n")
        f.write(f"EMAIL_BACKEND={env_vars.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')}\n")
        f.write(f"EMAIL_HOST={env_vars.get('EMAIL_HOST', '')}\n")
        f.write(f"EMAIL_PORT={env_vars.get('EMAIL_PORT', '587')}\n")
        f.write(f"EMAIL_USE_TLS={env_vars.get('EMAIL_USE_TLS', 'True')}\n")
        f.write(f"EMAIL_HOST_USER={env_vars.get('EMAIL_HOST_USER', '')}\n")
        f.write(f"EMAIL_HOST_PASSWORD={env_vars.get('EMAIL_HOST_PASSWORD', '')}\n")
        f.write(f"ALERT_EMAIL={env_vars.get('ALERT_EMAIL', '')}\n\n")
        
        # Alert settings
        f.write("# Alert Settings\n")
        f.write("ALERTS_ENABLED=true\n\n")
        
        # Scaling settings
        f.write("# Scaling Settings\n")
        f.write("LOAD_BALANCER_TYPE=nginx\n")
        f.write("SCALING_MIN_INSTANCES=2\n")
        f.write("SCALING_MAX_INSTANCES=10\n")
        f.write("SCALING_UP_THRESHOLD=70\n")
        f.write("SCALING_DOWN_THRESHOLD=30\n")
        f.write("SCALING_UP_STEP=1\n")
        f.write("SCALING_DOWN_STEP=1\n\n")
        
        # Cache settings
        f.write("# Cache Settings\n")
        f.write("CACHE_DEFAULT_TIMEOUT=300\n")
        f.write("CACHE_PRODUCT_TIMEOUT=3600\n")
        f.write("CACHE_CATEGORY_TIMEOUT=1800\n")
        f.write("CACHE_SESSION_TIMEOUT=300\n\n")
        
        # Redis connection settings
        f.write("# Redis Connection Settings\n")
        f.write("REDIS_MAX_CONNECTIONS=20\n")
        f.write("REDIS_SOCKET_TIMEOUT=5\n")
        f.write("REDIS_SOCKET_CONNECT_TIMEOUT=5\n")
        f.write("REDIS_HEALTH_CHECK_INTERVAL=30\n")
    
    print(f"\nEnvironment file created: {env_path}")
    print("Please review and update the file with your actual credentials.")

def main():
    """Main setup function"""
    print("MyShop Production Environment Setup")
    print("==================================")
    print("This script will help you configure environment variables for production deployment.")
    print("You will be prompted for various configuration details.\n")
    
    # Check if .env.prod already exists
    if Path('.env.prod').exists():
        response = input("A .env.prod file already exists. Do you want to overwrite it? (y/N): ").strip().lower()
        if response != 'y':
            print("Setup cancelled.")
            sys.exit(0)
    
    # Collect all environment variables
    env_vars = {}
    
    # Generate secret key
    env_vars['SECRET_KEY'] = generate_secret_key()
    
    # Setup configurations
    env_vars.update(setup_domain_config())
    env_vars.update(setup_database_config())
    env_vars.update(setup_redis_config())
    env_vars.update(setup_aws_credentials())
    env_vars.update(setup_email_config())
    
    # Generate environment file
    generate_env_file(env_vars)
    
    print("\nSetup completed successfully!")
    print("\nNext steps:")
    print("1. Review the .env.prod file and update any missing values")
    print("2. Set the environment variables on your production server")
    print("3. Run database migrations: python manage.py migrate")
    print("4. Collect static files: python manage.py collectstatic")
    print("5. Create a superuser: python manage.py createsuperuser")
    print("6. Start the application server")

if __name__ == "__main__":
    main()