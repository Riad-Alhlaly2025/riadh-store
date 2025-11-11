# MyShop Production Deployment Guide

## Prerequisites

1. Python 3.13
2. PostgreSQL (or MySQL)
3. Redis
4. Nginx (optional but recommended)
5. Gunicorn (for production server)

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd myshop
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file and modify it:

```bash
cp .env.example .env
```

Edit the `.env` file with your production settings:
- Set `DEBUG=False`
- Generate a new `SECRET_KEY`
- Configure database settings
- Set payment gateway credentials
- Configure email settings

### 5. Database Setup

Create the database and run migrations:

```bash
python manage.py migrate
```

### 6. Collect Static Files

```bash
python manage.py collectstatic
```

### 7. Create Superuser

```bash
python manage.py createsuperuser
```

## Deployment Options

### Option 1: Using Docker (Recommended)

1. Install Docker and Docker Compose
2. Run the application:

```bash
docker-compose up -d
```

### Option 2: Manual Deployment

1. Run the deployment script:

```bash
./deploy.sh  # On Windows: deploy.bat
```

### Option 3: Using Gunicorn with Nginx

1. Install Gunicorn:

```bash
pip install gunicorn
```

2. Start Gunicorn:

```bash
gunicorn shopsite.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

3. Configure Nginx using the provided `nginx.conf` file

## Environment Variables

The following environment variables should be set in production:

- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to `False` in production
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DB_ENGINE`: Database engine (e.g., `django.db.backends.postgresql`)
- `DB_NAME`: Database name
- `DB_USER`: Database user
- `DB_PASSWORD`: Database password
- `DB_HOST`: Database host
- `DB_PORT`: Database port
- `STRIPE_PUBLISHABLE_KEY`: Stripe publishable key
- `STRIPE_SECRET_KEY`: Stripe secret key
- `PAYPAL_CLIENT_ID`: PayPal client ID
- `PAYPAL_CLIENT_SECRET`: PayPal client secret

## Security Considerations

1. Always set `DEBUG=False` in production
2. Use a strong `SECRET_KEY`
3. Configure `ALLOWED_HOSTS` properly
4. Use HTTPS in production
5. Set proper file permissions
6. Regularly update dependencies
7. Implement proper backup strategy

## Backup Strategy

Use the provided backup scripts to regularly backup:
- Database
- Media files
- Logs

## Monitoring

- Check logs in the `logs/` directory
- Monitor application performance
- Set up error notifications

## Maintenance

- Regularly update dependencies
- Apply security patches
- Monitor disk space
- Check backup integrity