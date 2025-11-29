#!/usr/bin/env python
"""
Database backup script for MyShop e-commerce platform
This script creates backups of the PostgreSQL database and uploads them to AWS S3
"""

import os
import sys
import boto3
import psycopg2
from datetime import datetime
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('db_backup.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def create_local_backup():
    """Create a local backup of the PostgreSQL database"""
    try:
        # Get database connection details from environment variables
        db_name = os.environ.get('DB_NAME')
        db_user = os.environ.get('DB_USER')
        db_password = os.environ.get('DB_PASSWORD')
        db_host = os.environ.get('DB_HOST')
        db_port = os.environ.get('DB_PORT', '5432')
        
        if not all([db_name, db_user, db_host]):
            logger.error("Missing database connection details in environment variables")
            return None
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"myshop_backup_{timestamp}.sql"
        
        # Construct pg_dump command
        cmd = [
            'pg_dump',
            f'--dbname=postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}',
            '--no-owner',
            '--no-privileges',
            '--clean',
            '--if-exists',
            '--create',
            '--file', backup_filename
        ]
        
        # Execute the backup command
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"Database backup created successfully: {backup_filename}")
            return backup_filename
        else:
            logger.error(f"Database backup failed: {result.stderr}")
            return None
            
    except Exception as e:
        logger.error(f"Error creating local backup: {str(e)}")
        return None

def upload_to_s3(local_file, bucket_name, s3_key):
    """Upload backup file to AWS S3"""
    try:
        # Create S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
        )
        
        # Upload file
        s3_client.upload_file(local_file, bucket_name, s3_key)
        logger.info(f"Backup uploaded to S3: s3://{bucket_name}/{s3_key}")
        return True
        
    except Exception as e:
        logger.error(f"Error uploading to S3: {str(e)}")
        return False

def cleanup_local_backup(local_file):
    """Remove local backup file after successful upload"""
    try:
        os.remove(local_file)
        logger.info(f"Local backup file removed: {local_file}")
        return True
    except Exception as e:
        logger.error(f"Error removing local backup file: {str(e)}")
        return False

def main():
    """Main backup function"""
    logger.info("Starting database backup process")
    
    # Check required environment variables
    required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_STORAGE_BUCKET_NAME']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        sys.exit(1)
    
    # Create local backup
    backup_file = create_local_backup()
    if not backup_file:
        logger.error("Failed to create local backup")
        sys.exit(1)
    
    # Upload to S3
    bucket_name = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    timestamp = datetime.now().strftime('%Y/%m/%d')
    s3_key = f"backups/database/{timestamp}/{backup_file}"
    
    if upload_to_s3(backup_file, bucket_name, s3_key):
        # Cleanup local file
        cleanup_local_backup(backup_file)
        logger.info("Database backup completed successfully")
    else:
        logger.error("Failed to upload backup to S3")
        sys.exit(1)

if __name__ == "__main__":
    main()