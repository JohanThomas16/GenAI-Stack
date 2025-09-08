# GenAI Stack Makefile
# ====================

# Variables
DOCKER_COMPOSE = docker-compose
DOCKER_COMPOSE_PROD = docker-compose -f docker-compose.prod.yml
PROJECT_NAME = genai-stack
FRONTEND_DIR = frontend
BACKEND_DIR = backend

# Colors for output
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

.PHONY: help install build start stop restart clean test lint format deploy

# Default target
.DEFAULT_GOAL := help

## Help
help: ## Show this help message
	@echo "$(BLUE)GenAI Stack - Available Commands$(NC)"
	@echo "=================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

## Development
install: ## Install dependencies for both frontend and backend
	@echo "$(YELLOW)Installing dependencies...$(NC)"
	@cd $(FRONTEND_DIR) && npm install
	@cd $(BACKEND_DIR) && pip install -r requirements.txt
	@echo "$(GREEN)Dependencies installed successfully!$(NC)"

setup: ## Setup development environment
	@echo "$(YELLOW)Setting up development environment...$(NC)"
	@cp .env.example .env
	@echo "$(GREEN)Environment file created. Please update .env with your configuration.$(NC)"
	@make install
	@echo "$(GREEN)Development environment setup complete!$(NC)"

build: ## Build Docker containers
	@echo "$(YELLOW)Building Docker containers...$(NC)"
	@$(DOCKER_COMPOSE) build
	@echo "$(GREEN)Docker containers built successfully!$(NC)"

build-prod: ## Build production Docker containers
	@echo "$(YELLOW)Building production Docker containers...$(NC)"
	@$(DOCKER_COMPOSE_PROD) build
	@echo "$(GREEN)Production Docker containers built successfully!$(NC)"

start: ## Start development services
	@echo "$(YELLOW)Starting development services...$(NC)"
	@$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)Development services started!$(NC)"
	@echo "$(BLUE)Frontend: http://localhost:3000$(NC)"
	@echo "$(BLUE)Backend: http://localhost:8000$(NC)"
	@echo "$(BLUE)API Docs: http://localhost:8000/docs$(NC)"

start-prod: ## Start production services
	@echo "$(YELLOW)Starting production services...$(NC)"
	@$(DOCKER_COMPOSE_PROD) up -d
	@echo "$(GREEN)Production services started!$(NC)"

stop: ## Stop all services
	@echo "$(YELLOW)Stopping services...$(NC)"
	@$(DOCKER_COMPOSE) down
	@$(DOCKER_COMPOSE_PROD) down 2>/dev/null || true
	@echo "$(GREEN)Services stopped!$(NC)"

restart: stop start ## Restart all services

restart-prod: ## Restart production services
	@$(DOCKER_COMPOSE_PROD) down
	@$(DOCKER_COMPOSE_PROD) up -d

logs: ## Show logs from all services
	@$(DOCKER_COMPOSE) logs -f

logs-backend: ## Show backend logs
	@$(DOCKER_COMPOSE) logs -f backend

logs-frontend: ## Show frontend logs
	@$(DOCKER_COMPOSE) logs -f frontend

## Database
db-migrate: ## Run database migrations
	@echo "$(YELLOW)Running database migrations...$(NC)"
	@$(DOCKER_COMPOSE) exec backend alembic upgrade head
	@echo "$(GREEN)Database migrations completed!$(NC)"

db-reset: ## Reset database (WARNING: This will delete all data)
	@echo "$(RED)WARNING: This will delete all database data!$(NC)"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ]
	@$(DOCKER_COMPOSE) down -v
	@$(DOCKER_COMPOSE) up -d postgres
	@sleep 10
	@$(DOCKER_COMPOSE) up -d
	@make db-migrate
	@echo "$(GREEN)Database reset completed!$(NC)"

db-backup: ## Backup database
	@echo "$(YELLOW)Creating database backup...$(NC)"
	@mkdir -p backups
	@$(DOCKER_COMPOSE) exec -T postgres pg_dump -U genai_user genai_stack_db > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)Database backup created!$(NC)"

db-restore: ## Restore database from backup (usage: make db-restore FILE=backup_file.sql)
	@if [ -z "$(FILE)" ]; then echo "$(RED)Usage: make db-restore FILE=backup_file.sql$(NC)"; exit 1; fi
	@echo "$(YELLOW)Restoring database from $(FILE)...$(NC)"
	@$(DOCKER_COMPOSE) exec -T postgres psql -U genai_user -d genai_stack_db < $(FILE)
	@echo "$(GREEN)Database restored!$(NC)"

## Testing
test: ## Run all tests
	@echo "$(YELLOW)Running tests...$(NC)"
	@make test-backend
	@make test-frontend
	@echo "$(GREEN)All tests completed!$(NC)"

test-backend: ## Run backend tests
	@echo "$(YELLOW)Running backend tests...$(NC)"
	@cd $(BACKEND_DIR) && python -m pytest tests/ -v
	@echo "$(GREEN)Backend tests completed!$(NC)"

test-frontend: ## Run frontend tests
	@echo "$(YELLOW)Running frontend tests...$(NC)"
	@cd $(FRONTEND_DIR) && npm test -- --coverage --watchAll=false
	@echo "$(GREEN)Frontend tests completed!$(NC)"

test-watch: ## Run tests in watch mode
	@echo "$(YELLOW)Running tests in watch mode...$(NC)"
	@cd $(BACKEND_DIR) && python -m pytest tests/ -f &
	@cd $(FRONTEND_DIR) && npm test

## Code Quality
lint: ## Run linters
	@echo "$(YELLOW)Running linters...$(NC)"
	@make lint-backend
	@make lint-frontend
	@echo "$(GREEN)Linting completed!$(NC)"

lint-backend: ## Run backend linter
	@echo "$(YELLOW)Running backend linter...$(NC)"
	@cd $(BACKEND_DIR) && flake8 . --max-line-length=88 --exclude=venv,__pycache__
	@cd $(BACKEND_DIR) && black --check .
	@cd $(BACKEND_DIR) && isort --check-only .

lint-frontend: ## Run frontend linter
	@echo "$(YELLOW)Running frontend linter...$(NC)"
	@cd $(FRONTEND_DIR) && npm run lint

format: ## Format code
	@echo "$(YELLOW)Formatting code...$(NC)"
	@cd $(BACKEND_DIR) && black .
	@cd $(BACKEND_DIR) && isort .
	@cd $(FRONTEND_DIR) && npm run format
	@echo "$(GREEN)Code formatting completed!$(NC)"

## Deployment
deploy: ## Deploy to staging
	@echo "$(YELLOW)Deploying to staging...$(NC)"
	@./scripts/deploy.sh staging
	@echo "$(GREEN)Deployment to staging completed!$(NC)"

deploy-prod: ## Deploy to production
	@echo "$(RED)WARNING: This will deploy to production!$(NC)"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ]
	@echo "$(YELLOW)Deploying to production...$(NC)"
	@./scripts/deploy.sh production
	@echo "$(GREEN)Deployment to production completed!$(NC)"

## Utilities
clean: ## Clean up Docker resources
	@echo "$(YELLOW)Cleaning up Docker resources...$(NC)"
	@docker system prune -f
	@docker volume prune -f
	@echo "$(GREEN)Cleanup completed!$(NC)"

clean-all: ## Clean up everything (containers, images, volumes)
	@echo "$(RED)WARNING: This will remove all Docker containers, images, and volumes!$(NC)"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ]
	@$(DOCKER_COMPOSE) down -v --rmi all
	@$(DOCKER_COMPOSE_PROD) down -v --rmi all 2>/dev/null || true
	@docker system prune -af
	@echo "$(GREEN)Complete cleanup finished!$(NC)"

status: ## Show service status
	@echo "$(BLUE)Service Status:$(NC)"
	@$(DOCKER_COMPOSE) ps

health: ## Check service health
	@echo "$(BLUE)Health Check:$(NC)"
	@curl -f http://localhost:8000/health || echo "$(RED)Backend unhealthy$(NC)"
	@curl -f http://localhost:3000 > /dev/null 2>&1 && echo "$(GREEN)Frontend healthy$(NC)" || echo "$(RED)Frontend unhealthy$(NC)"

shell-backend: ## Open shell in backend container
	@$(DOCKER_COMPOSE) exec backend /bin/bash

shell-frontend: ## Open shell in frontend container
	@$(DOCKER_COMPOSE) exec frontend /bin/sh

shell-db: ## Open database shell
	@$(DOCKER_COMPOSE) exec postgres psql -U genai_user -d genai_stack_db

## Documentation
docs: ## Generate documentation
	@echo "$(YELLOW)Generating documentation...$(NC)"
	@cd docs && python -m mkdocs build
	@echo "$(GREEN)Documentation generated!$(NC)"

docs-serve: ## Serve documentation locally
	@echo "$(BLUE)Serving documentation at http://localhost:8001$(NC)"
	@cd docs && python -m mkdocs serve -a 0.0.0.0:8001

## Monitoring
monitor: ## Start monitoring stack
	@echo "$(YELLOW)Starting monitoring stack...$(NC)"
	@$(DOCKER_COMPOSE) --profile monitoring up -d
	@echo "$(GREEN)Monitoring stack started!$(NC)"
	@echo "$(BLUE)Prometheus: http://localhost:9090$(NC)"
	@echo "$(BLUE)Grafana: http://localhost:3001 (admin/admin123)$(NC)"

## Security
security-scan: ## Run security scan
	@echo "$(YELLOW)Running security scan...$(NC)"
	@cd $(BACKEND_DIR) && safety check
	@cd $(FRONTEND_DIR) && npm audit
	@echo "$(GREEN)Security scan completed!$(NC)"

## Release
version: ## Show version information
	@echo "$(BLUE)GenAI Stack Version Information:$(NC)"
	@echo "Project: $(PROJECT_NAME)"
	@cat $(FRONTEND_DIR)/package.json | grep '"version"' | head -1
	@cat $(BACKEND_DIR)/app/main.py | grep 'version=' | head -1

release: ## Create a new release (usage: make release VERSION=x.x.x)
	@if [ -z "$(VERSION)" ]; then echo "$(RED)Usage: make release VERSION=x.x.x$(NC)"; exit 1; fi
	@echo "$(YELLOW)Creating release $(VERSION)...$(NC)"
	@git tag -a v$(VERSION) -m "Release v$(VERSION)"
	@git push origin v$(VERSION)
	@echo "$(GREEN)Release v$(VERSION) created!$(NC)"

## Development shortcuts
dev: start ## Alias for start
prod: start-prod ## Alias for start-prod
down: stop ## Alias for stop
up: start ## Alias for start

# Include custom targets if they exist
-include Makefile.local
