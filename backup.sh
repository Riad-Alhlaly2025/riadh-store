#!/bin/bash

# Backup script for MyShop

# Configuration
BACKUP_DIR="/backups/myshop"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="myshop"
DB_USER="myshopuser"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Backup database
echo "Backing up database..."
pg_dump -U $DB_USER -h localhost $DB_NAME > $BACKUP_DIR/myshop_db_$DATE.sql

# Backup media files
echo "Backing up media files..."
tar -czf $BACKUP_DIR/myshop_media_$DATE.tar.gz media/

# Backup logs
echo "Backing up logs..."
tar -czf $BACKUP_DIR/myshop_logs_$DATE.tar.gz logs/

# Keep only last 30 days of backups
find $BACKUP_DIR -name "myshop_*" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/myshop_$DATE"