@echo off
REM Production deployment script for MyShop on Windows

echo Starting MyShop production deployment...

REM Check if we're in the right directory
if not exist "manage.py" (
    echo Error: manage.py not found. Please run this script from the project root directory.
    pause
    exit /b 1
)

REM Create logs directory if it doesn't exist
echo Creating logs directory...
mkdir logs 2>nul

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Collect static files
echo Collecting static files...
python manage.py collectstatic --noinput

REM Run migrations
echo Running database migrations...
python manage.py migrate

REM Create superuser if it doesn't exist
echo Creating superuser if needed...
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print('Superuser already exists' if User.objects.filter(is_superuser=True).exists() else 'Creating superuser...' if User.objects.create_superuser('admin', 'admin@yourdomain.com', 'adminpassword') else 'Superuser created')"

REM Start the application with Gunicorn (if available) or development server
echo Starting application...
where gunicorn >nul 2>nul
if %errorlevel% == 0 (
    echo Starting with Gunicorn...
    gunicorn shopsite.wsgi:application --bind 0.0.0.0:8000 --workers 3
) else (
    echo Gunicorn not found, starting with development server...
    echo WARNING: This is not recommended for production!
    python manage.py runserver 0.0.0.0:8000
)

echo Deployment completed!
pause