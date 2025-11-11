#!/bin/bash

# Production deployment script for MyShop

# Exit on any error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting MyShop production deployment...${NC}"

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo -e "${RED}Error: manage.py not found. Please run this script from the project root directory.${NC}"
    exit 1
fi

# Create logs directory if it doesn't exist
echo -e "${YELLOW}Creating logs directory...${NC}"
mkdir -p logs

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt

# Collect static files
echo -e "${YELLOW}Collecting static files...${NC}"
python manage.py collectstatic --noinput

# Run migrations
echo -e "${YELLOW}Running database migrations...${NC}"
python manage.py migrate

# Create superuser if it doesn't exist
echo -e "${YELLOW}Creating superuser if needed...${NC}"
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@yourdomain.com', 'adminpassword')
    print('Superuser created')
else:
    print('Superuser already exists')
"

# Start the application with Gunicorn
echo -e "${GREEN}Starting application with Gunicorn...${NC}"
gunicorn shopsite.wsgi:application --bind 0.0.0.0:8000 --workers 3

echo -e "${GREEN}Deployment completed successfully!${NC}"