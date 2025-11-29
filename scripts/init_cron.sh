#!/bin/bash
# Script to initialize cron jobs in Docker container

echo "Initializing cron jobs..."

# Create logs directory if it doesn't exist
mkdir -p /app/logs

# Copy crontab file to the correct location
cp /app/scripts/crontab.txt /etc/cron.d/myshop-cron

# Give execution rights on the cron job
chmod 0644 /etc/cron.d/myshop-cron

# Apply cron job
crontab /etc/cron.d/myshop-cron

# Create log files
touch /app/logs/backup.log
touch /app/logs/monitoring.log
touch /app/logs/cache_cleanup.log
touch /app/logs/session_cleanup.log

# Start cron service
service cron start

echo "Cron jobs initialized successfully!"