#!/bin/bash

# Startup script for MyShop in production

# Exit on any error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting MyShop production environment...${NC}"

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo -e "${RED}Error: manage.py not found. Please run this script from the project root directory.${NC}"
    exit 1
fi

# Load environment variables
if [ -f ".env" ]; then
    echo -e "${YELLOW}Loading environment variables...${NC}"
    export $(cat .env | xargs)
else
    echo -e "${YELLOW}No .env file found, using default settings...${NC}"
fi

# Create necessary directories
echo -e "${YELLOW}Creating necessary directories...${NC}"
mkdir -p logs media staticfiles

# Run health checks
echo -e "${YELLOW}Running health checks...${NC}"
python health_check.py
if [ $? -ne 0 ]; then
    echo -e "${RED}Health checks failed. Aborting startup.${NC}"
    exit 1
fi

# Collect static files
echo -e "${YELLOW}Collecting static files...${NC}"
python manage.py collectstatic --noinput

# Run migrations
echo -e "${YELLOW}Running database migrations...${NC}"
python manage.py migrate --noinput

# Start the application with Gunicorn
echo -e "${GREEN}Starting application with Gunicorn...${NC}"
exec gunicorn shopsite.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120 --keep-alive 5