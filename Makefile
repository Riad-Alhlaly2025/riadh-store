# Makefile for MyShop e-commerce platform

# Variables
DOCKER_COMPOSE = docker-compose
MANAGE_PY = python manage.py
TEST_FLAGS = 

# Default target
.PHONY: help
help:
	@echo "MyShop Development Commands:"
	@echo "  make run              - Start development server"
	@echo "  make stop             - Stop development server"
	@echo "  make build            - Build Docker images"
	@echo "  make test             - Run all tests"
	@echo "  make test-unit        - Run unit tests"
	@echo "  make test-api         - Run API tests"
	@echo "  make migrate          - Run database migrations"
	@echo "  make makemigrations   - Create database migrations"
	@echo "  make shell            - Open Django shell"
	@echo "  make superuser        - Create superuser"
	@echo "  make collectstatic    - Collect static files"
	@echo "  make logs             - View container logs"
	@echo "  make clean            - Remove Docker containers and volumes"
	@echo "  make docs             - Generate API documentation"
	@echo "  make deploy           - Deploy to production"
	@echo "  make setup-prod       - Setup production environment"
	@echo "  make backup           - Run database backup"
	@echo "  make monitor          - Run system monitoring"

# Development server
.PHONY: run
run:
	$(DOCKER_COMPOSE) up

.PHONY: stop
stop:
	$(DOCKER_COMPOSE) down

.PHONY: build
build:
	$(DOCKER_COMPOSE) build

# Testing
.PHONY: test
test:
	$(DOCKER_COMPOSE) run --rm web $(MANAGE_PY) test $(TEST_FLAGS)

.PHONY: test-unit
test-unit:
	$(DOCKER_COMPOSE) run --rm web $(MANAGE_PY) test store.tests.test_services $(TEST_FLAGS)

.PHONY: test-api
test-api:
	$(DOCKER_COMPOSE) run --rm web $(MANAGE_PY) test store.tests.test_api $(TEST_FLAGS)

# Database
.PHONY: migrate
migrate:
	$(DOCKER_COMPOSE) run --rm web $(MANAGE_PY) migrate

.PHONY: makemigrations
makemigrations:
	$(DOCKER_COMPOSE) run --rm web $(MANAGE_PY) makemigrations

# Django management
.PHONY: shell
shell:
	$(DOCKER_COMPOSE) run --rm web $(MANAGE_PY) shell

.PHONY: superuser
superuser:
	$(DOCKER_COMPOSE) run --rm web $(MANAGE_PY) createsuperuser

.PHONY: collectstatic
collectstatic:
	$(DOCKER_COMPOSE) run --rm web $(MANAGE_PY) collectstatic --noinput

# Monitoring
.PHONY: logs
logs:
	$(DOCKER_COMPOSE) logs -f

.PHONY: clean
clean:
	$(DOCKER_COMPOSE) down -v --remove-orphans

# Documentation
.PHONY: docs
docs:
	@echo "API documentation available at:"
	@echo "  http://localhost:8000/swagger/"
	@echo "  http://localhost:8000/redoc/"

# Production deployment
.PHONY: deploy
deploy:
	@echo "To deploy to production:"
	@echo "1. Set up your production environment variables in .env.prod"
	@echo "2. Run: docker-compose -f docker-compose.prod.yml up -d"
	@echo "3. Run migrations: docker-compose -f docker-compose.prod.yml exec web python manage.py migrate"
	@echo "4. Collect static files: docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput"
	@echo "5. Create superuser: docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser"

# Production setup
.PHONY: setup-prod
setup-prod:
	@echo "Setting up production environment..."
	python scripts/setup_production_env.py

# Backup
.PHONY: backup
backup:
	@echo "Running database backup..."
	docker-compose -f docker-compose.prod.yml exec web python scripts/backup_db.py

# Monitoring
.PHONY: monitor
monitor:
	@echo "Running system monitoring..."
	docker-compose -f docker-compose.prod.yml exec web python scripts/monitoring.py