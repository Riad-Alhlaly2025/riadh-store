@echo off
REM Startup script for MyShop in production on Windows

echo Starting MyShop production environment...

REM Check if we're in the right directory
if not exist "manage.py" (
    echo Error: manage.py not found. Please run this script from the project root directory.
    pause
    exit /b 1
)

REM Create necessary directories
echo Creating necessary directories...
mkdir logs 2>nul
mkdir media 2>nul
mkdir staticfiles 2>nul

REM Run health checks
echo Running health checks...
python health_check.py
if %errorlevel% neq 0 (
    echo Health checks failed. Aborting startup.
    pause
    exit /b 1
)

REM Collect static files
echo Collecting static files...
python manage.py collectstatic --noinput

REM Run migrations
echo Running database migrations...
python manage.py migrate --noinput

REM Start the application
echo Starting application...
where gunicorn >nul 2>nul
if %errorlevel% == 0 (
    echo Starting with Gunicorn...
    gunicorn shopsite.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120 --keep-alive 5
) else (
    echo Gunicorn not found, starting with development server...
    echo WARNING: This is not recommended for production!
    python manage.py runserver 0.0.0.0:8000
)

pause