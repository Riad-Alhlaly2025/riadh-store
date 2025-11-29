# MyShop Microservices Architecture

## Overview
This directory contains the complete microservices architecture for the MyShop e-commerce platform. The system has been decomposed into independent services that can be developed, deployed, and scaled independently.

## Services

### Core Services
1. **User Service** - Manages user authentication, authorization, and profiles
2. **Product Service** - Handles product catalog, search, and media management
3. **Order Service** - Manages order processing, cart functionality, and order tracking
4. **Payment Service** - Processes payments and manages transactions

### Supporting Services
5. **Inventory Service** - Tracks stock levels and manages inventory
6. **Notification Service** - Sends emails, SMS, and push notifications
7. **Analytics Service** - Collects and analyzes user behavior and business metrics

### Infrastructure
8. **API Gateway** - Centralized entry point for all client requests
9. **Database** - PostgreSQL instances for each service
10. **Cache** - Redis for caching and session management
11. **Search** - Elasticsearch for product search and analytics

## Architecture Diagram

![Architecture Diagram](complete_architecture.png)

See [complete_architecture.md](complete_architecture.md) for detailed architecture diagrams and documentation.

## Prerequisites
- Docker and Docker Compose
- Node.js (for API Gateway)
- Python 3.13

## Quick Start

1. **Start all services:**
   ```bash
   make start
   ```

2. **View logs:**
   ```bash
   make logs
   ```

3. **Run migrations:**
   ```bash
   make migrate
   ```

4. **Stop services:**
   ```bash
   make stop
   ```

## Service Endpoints

| Service | Local URL | API Prefix |
|---------|-----------|------------|
| API Gateway | http://localhost:8000 | N/A |
| User Service | http://localhost:8001 | /api/users |
| Product Service | http://localhost:8002 | /api/products |
| Order Service | http://localhost:8003 | /api/orders |
| Payment Service | http://localhost:8004 | /api/payments |
| Inventory Service | http://localhost:8005 | /api/inventory |
| Notification Service | http://localhost:8006 | /api/notifications |
| Analytics Service | http://localhost:8007 | /api/analytics |

## Makefile Commands

| Command | Description |
|---------|-------------|
| `make setup` | Install all dependencies |
| `make start` | Start all services with Docker Compose |
| `make stop` | Stop all services |
| `make restart` | Restart all services |
| `make logs` | View logs for all services |
| `make logs-service SERVICE=name` | View logs for a specific service |
| `make migrate` | Run migrations for all services |
| `make migrate-service SERVICE=name` | Run migrations for a specific service |
| `make test` | Run tests for all services |
| `make test-service SERVICE=name` | Run tests for a specific service |
| `make clean` | Remove all containers and volumes |
| `make prune` | Remove unused Docker data |

## Development Workflow

1. **Make changes to a service**
2. **Rebuild the service:**
   ```bash
   docker-compose build service-name
   ```
3. **Restart the service:**
   ```bash
   docker-compose up -d service-name
   ```

## Monitoring and Health Checks

Each service exposes a `/health/` endpoint that returns the service status.

The API Gateway provides a central `/health` endpoint that checks all services.

## Database Management

Each service has its own PostgreSQL database. To access a database directly:

```bash
docker-compose exec postgres psql -U postgres -d service_name
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

## License

This project is licensed under the MIT License.