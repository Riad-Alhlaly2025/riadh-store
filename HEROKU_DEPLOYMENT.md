# Deploying MyShop to Heroku

## Prerequisites

1. Create a free account at [Heroku](https://heroku.com)
2. Install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
3. Install Git if you haven't already

## Deployment Steps

### 1. Prepare Your Project

Make sure you have the following files in your project root:
- `Procfile` - Tells Heroku how to run your app
- `requirements.txt` - Lists Python dependencies
- `runtime.txt` - Specifies Python version
- `shopsite/settings.py` - Updated for Heroku deployment

### 2. Initialize Git Repository (if not already done)

```bash
cd c:\Users\PC\Desktop\myshop
git init
git add .
git commit -m "Initial commit"
```

### 3. Login to Heroku

```bash
heroku login
```

### 4. Create Heroku App

```bash
heroku create your-app-name
```

Or let Heroku generate a name:

```bash
heroku create
```

### 5. Set Environment Variables

```bash
heroku config:set SECRET_KEY=your-secret-key-here
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com
```

### 6. Add PostgreSQL Database

```bash
heroku addons:create heroku-postgresql:hobby-dev
```

### 7. Deploy Your App

```bash
git push heroku master
```

### 8. Run Migrations

```bash
heroku run python manage.py migrate
```

### 9. Create Superuser (Optional)

```bash
heroku run python manage.py createsuperuser
```

### 10. Open Your App

```bash
heroku open
```

## Configuration

### Environment Variables

Set these environment variables in Heroku:

```bash
heroku config:set SECRET_KEY=your-very-secret-key-here
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com
```

### Database

Heroku automatically provides a DATABASE_URL environment variable when you add the PostgreSQL addon.

## Troubleshooting

### Common Issues

1. **Module not found errors**: Make sure all dependencies are in `requirements.txt`
2. **Static files not loading**: The app is configured to use WhiteNoise for static files
3. **Database errors**: Run migrations after deployment

### View Logs

```bash
heroku logs --tail
```

## Scaling

To scale your app:

```bash
heroku ps:scale web=1
```

## Custom Domain

To add a custom domain:

```bash
heroku domains:add yourdomain.com
```

Then configure your DNS provider to point to the Heroku domain provided.