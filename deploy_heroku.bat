@echo off
REM Simple Heroku deployment script for MyShop

echo Deploying MyShop to Heroku...

REM Check if Heroku CLI is installed
where heroku >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Heroku CLI not found. Please install it from https://devcenter.heroku.com/articles/heroku-cli
    pause
    exit /b 1
)

REM Check if Git is initialized
if not exist ".git" (
    echo Initializing Git repository...
    git init
    git add .
    git commit -m "Initial commit for Heroku deployment"
)

REM Login to Heroku
echo Please login to Heroku when prompted...
heroku login

REM Create Heroku app
echo Creating Heroku app...
heroku create

REM Add PostgreSQL database
echo Adding PostgreSQL database...
heroku addons:create heroku-postgresql:hobby-dev

REM Set environment variables
echo Setting environment variables...
heroku config:set SECRET_KEY=myshop-production-secret-key-change-this
heroku config:set DEBUG=False

REM Deploy the app
echo Deploying the app...
git push heroku master

REM Run migrations
echo Running database migrations...
heroku run python manage.py migrate

echo Deployment completed!
echo Use "heroku open" to open your app in the browser
pause