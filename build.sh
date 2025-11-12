#!/usr/bin/env bash
# Exit on error
set -o errexit

# Setup and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements-render.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate