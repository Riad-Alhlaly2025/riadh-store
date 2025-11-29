# MyShop E-commerce Platform

A modern e-commerce platform built with Django, featuring microservices architecture, Docker containerization, and advanced features.

## Features

- **Microservices Architecture**: Modular design with separated services
- **Docker Containerization**: Easy deployment and scaling
- **API Gateway**: RESTful API with Swagger documentation
- **AI Product Recommendations**: Machine learning-powered product suggestions
- **Advanced Search**: Faceted search with filters
- **Mobile Application Support**: Dedicated API for mobile apps
- **Technical Debt Reduction**: Clean code structure with services layer
- **Comprehensive Testing**: Unit and integration tests
- **Production Deployment**: Docker Compose configuration for production

## Architecture

### Services Layer
Business logic has been moved from views to dedicated service classes:
- `OrderService`: Order management operations
- `RecommendationService`: AI-powered product recommendations

### API Layer
- RESTful API endpoints for web and mobile applications
- Swagger/OpenAPI documentation
- Mobile-specific API endpoints

### Containerization
- Docker Compose for development and production
- PostgreSQL database
- Redis for caching and sessions
- Nginx for reverse proxy and SSL termination
- Celery for background tasks

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Python 3.9+

### Development Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd myshop
   ```

2. Copy environment file:
   ```bash
   cp .env.example .env
   ```

3. Start the development server:
   ```bash
   make run
   ```

4. Run migrations:
   ```bash
   make migrate
   ```

5. Create a superuser:
   ```bash
   make superuser
   ```

6. Access the application:
   - Web: http://localhost:8000
   - API Docs: http://localhost:8000/swagger/

### Production Deployment

1. Set up production environment variables:
   ```bash
   cp .env.prod .env
   # Edit .env with your production settings
   ```

2. Deploy with Docker Compose:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

## API Documentation

API documentation is available at:
- Swagger UI: `/swagger/`
- ReDoc: `/redoc/`

## Testing

Run all tests:
```bash
make test
```

Run specific test suites:
```bash
make test-unit    # Unit tests
make test-api     # API tests
```

## Project Structure

```
myshop/
├── store/                 # Main Django app
│   ├── api/              # REST API endpoints
│   ├── services/         # Business logic services
│   ├── tests/            # Unit and integration tests
│   └── templates/        # HTML templates
├── mobile/               # Mobile application API
├── nginx/                # Nginx configuration
├── static/               # Static files
├── media/                # Media files
├── docker-compose.yml    # Development Docker Compose
├── docker-compose.prod.yml # Production Docker Compose
├── Dockerfile           # Application Dockerfile
├── requirements.txt     # Python dependencies
└── Makefile             # Development commands
```

## Key Improvements

1. **Microservices Architecture**: Separated concerns with dedicated services
2. **Docker Containerization**: Consistent development and production environments
3. **API Gateway**: Standardized RESTful API with documentation
4. **AI Recommendations**: Machine learning for personalized product suggestions
5. **Advanced Search**: Comprehensive filtering and sorting capabilities
6. **Mobile Support**: Dedicated API for mobile applications
7. **Technical Debt Reduction**: Clean code organization with services layer
8. **Testing Framework**: Comprehensive unit and integration tests
9. **Deployment Automation**: Makefile for common development tasks
10. **Documentation**: API documentation with Swagger/OpenAPI

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.