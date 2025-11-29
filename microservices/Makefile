# Makefile for MyShop Microservices

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

# Default target
.PHONY: help
help:
	@echo "$(GREEN)MyShop Microservices Management Commands$(NC)"
	@echo ""
	@echo "$(YELLOW)Development Commands:$(NC)"
	@echo "  make setup             - Install all dependencies"
	@echo "  make start             - Start all services with Docker Compose"
	@echo "  make stop              - Stop all services"
	@echo "  make restart           - Restart all services"
	@echo "  make logs              - View logs for all services"
	@echo "  make logs-service      - View logs for a specific service"
	@echo ""
	@echo "$(YELLOW)Database Commands:$(NC)"
	@echo "  make migrate           - Run migrations for all services"
	@echo "  make migrate-service   - Run migrations for a specific service"
	@echo ""
	@echo "$(YELLOW)Testing Commands:$(NC)"
	@echo "  make test              - Run tests for all services"
	@echo "  make test-service      - Run tests for a specific service"
	@echo ""
	@echo "$(YELLOW)Cleanup Commands:$(NC)"
	@echo "  make clean             - Remove all containers and volumes"
	@echo "  make prune             - Remove unused Docker data"

# Setup all services
.PHONY: setup
setup:
	@echo "$(GREEN)Setting up all services...$(NC)"
	cd user_service && pip install -r requirements.txt
	cd product_service && pip install -r requirements.txt
	cd order_service && pip install -r requirements.txt
	cd payment_service && pip install -r requirements.txt
	cd inventory_service && pip install -r requirements.txt
	cd notification_service && pip install -r requirements.txt
	cd analytics_service && pip install -r requirements.txt
	cd api_gateway && npm install
	@echo "$(GREEN)Setup complete!$(NC)"

# Start all services
.PHONY: start
start:
	@echo "$(GREEN)Starting all services...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)Services started!$(NC)"

# Stop all services
.PHONY: stop
stop:
	@echo "$(YELLOW)Stopping all services...$(NC)"
	docker-compose down
	@echo "$(GREEN)Services stopped!$(NC)"

# Restart all services
.PHONY: restart
restart:
	@echo "$(YELLOW)Restarting all services...$(NC)"
	docker-compose down
	docker-compose up -d
	@echo "$(GREEN)Services restarted!$(NC)"

# View logs for all services
.PHONY: logs
logs:
	@echo "$(GREEN)Viewing logs for all services...$(NC)"
	docker-compose logs -f

# View logs for a specific service
.PHONY: logs-service
logs-service:
ifndef SERVICE
	@echo "$(RED)Error: SERVICE is not set. Usage: make logs-service SERVICE=service-name$(NC)"
	@exit 1
endif
	@echo "$(GREEN)Viewing logs for $(SERVICE)...$(NC)"
	docker-compose logs -f $(SERVICE)

# Run migrations for all services
.PHONY: migrate
migrate:
	@echo "$(GREEN)Running migrations for all services...$(NC)"
	docker-compose exec user-service python manage.py migrate
	docker-compose exec product-service python manage.py migrate
	docker-compose exec order-service python manage.py migrate
	docker-compose exec payment-service python manage.py migrate
	docker-compose exec inventory-service python manage.py migrate
	docker-compose exec notification-service python manage.py migrate
	docker-compose exec analytics-service python manage.py migrate
	@echo "$(GREEN)Migrations complete!$(NC)"

# Run migrations for a specific service
.PHONY: migrate-service
migrate-service:
ifndef SERVICE
	@echo "$(RED)Error: SERVICE is not set. Usage: make migrate-service SERVICE=service-name$(NC)"
	@exit 1
endif
	@echo "$(GREEN)Running migrations for $(SERVICE)...$(NC)"
	docker-compose exec $(SERVICE) python manage.py migrate
	@echo "$(GREEN)Migrations complete for $(SERVICE)!$(NC)"

# Run tests for all services
.PHONY: test
test:
	@echo "$(GREEN)Running tests for all services...$(NC)"
	docker-compose exec user-service python manage.py test
	docker-compose exec product-service python manage.py test
	docker-compose exec order-service python manage.py test
	docker-compose exec payment-service python manage.py test
	docker-compose exec inventory-service python manage.py test
	docker-compose exec notification-service python manage.py test
	docker-compose exec analytics-service python manage.py test
	@echo "$(GREEN)Tests complete!$(NC)"

# Run tests for a specific service
.PHONY: test-service
test-service:
ifndef SERVICE
	@echo "$(RED)Error: SERVICE is not set. Usage: make test-service SERVICE=service-name$(NC)"
	@exit 1
endif
	@echo "$(GREEN)Running tests for $(SERVICE)...$(NC)"
	docker-compose exec $(SERVICE) python manage.py test
	@echo "$(GREEN)Tests complete for $(SERVICE)!$(NC)"

# Clean up all containers and volumes
.PHONY: clean
clean:
	@echo "$(YELLOW)Cleaning up all containers and volumes...$(NC)"
	docker-compose down -v
	@echo "$(GREEN)Cleanup complete!$(NC)"

# Prune unused Docker data
.PHONY: prune
prune:
	@echo "$(YELLOW)Pruning unused Docker data...$(NC)"
	docker system prune -af
	@echo "$(GREEN)Pruning complete!$(NC)"