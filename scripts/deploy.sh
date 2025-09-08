#!/bin/bash

# GenAI Stack Deployment Script
# =============================
# This script deploys the application to various environments

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
PROJECT_NAME="genai-stack"
DEFAULT_ENVIRONMENT="staging"
DEPLOYMENT_TIMEOUT=300  # 5 minutes

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to load environment-specific configuration
load_env_config() {
    local env=$1
    
    case $env in
        development|dev)
            ENV_FILE=".env"
            COMPOSE_FILE="docker-compose.yml"
            ;;
        staging|stage)
            ENV_FILE=".env.staging"
            COMPOSE_FILE="docker-compose.prod.yml"
            ;;
        production|prod)
            ENV_FILE=".env.production"
            COMPOSE_FILE="docker-compose.prod.yml"
            ;;
        *)
            log_error "Unknown environment: $env"
            log_error "Supported environments: development, staging, production"
            exit 1
            ;;
    esac

    if [ ! -f "$ENV_FILE" ]; then
        log_error "Environment file $ENV_FILE not found"
        exit 1
    fi

    if [ ! -f "$COMPOSE_FILE" ]; then
        log_error "Compose file $COMPOSE_FILE not found"
        exit 1
    fi

    log_info "Using environment: $env"
    log_info "Environment file: $ENV_FILE"
    log_info "Compose file: $COMPOSE_FILE"
}

# Function to validate environment
validate_environment() {
    log_info "Validating deployment environment..."

    # Check required tools
    local required_tools=("docker" "docker-compose")
    
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            log_error "$tool is not installed"
            exit 1
        fi
    done

    # Check Docker daemon
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker daemon is not running"
        exit 1
    fi

    # Check environment file
    source "$ENV_FILE"
    
    # Validate required environment variables
    local required_vars=("DATABASE_URL" "SECRET_KEY" "JWT_SECRET_KEY")
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            log_error "Required environment variable $var is not set"
            exit 1
        fi
    done

    # Check if API keys are set for production
    if [ "$ENVIRONMENT" = "production" ]; then
        if [ -z "$OPENAI_API_KEY" ]; then
            log_error "OPENAI_API_KEY is required for production deployment"
            exit 1
        fi
    fi

    log_success "Environment validation passed"
}

# Function for Docker Compose deployment
deploy_docker_compose() {
    log_info "Deploying with Docker Compose..."

    # Pull latest images
    log_info "Pulling latest images..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" pull

    # Stop existing containers
    log_info "Stopping existing containers..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down

    # Start services
    log_info "Starting services..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d

    # Wait for services to be healthy
    wait_for_services

    log_success "Docker Compose deployment completed"
}

# Function for Kubernetes deployment
deploy_kubernetes() {
    log_info "Deploying to Kubernetes..."

    # Check kubectl
    if ! command -v kubectl >/dev/null 2>&1; then
        log_error "kubectl is not installed"
        exit 1
    fi

    # Check cluster connection
    if ! kubectl cluster-info >/dev/null 2>&1; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi

    # Apply configurations
    log_info "Applying Kubernetes manifests..."
    kubectl apply -f deployment/kubernetes/namespace.yaml
    kubectl apply -f deployment/kubernetes/configmap.yaml
    kubectl apply -f deployment/kubernetes/secrets.yaml
    
    # Deploy services
    kubectl apply -f deployment/kubernetes/postgres-statefulset.yaml
    kubectl apply -f deployment/kubernetes/redis-deployment.yaml
    kubectl apply -f deployment/kubernetes/chromadb-deployment.yaml
    kubectl apply -f deployment/kubernetes/backend-deployment.yaml
    kubectl apply -f deployment/kubernetes/frontend-deployment.yaml
    kubectl apply -f deployment/kubernetes/services.yaml
    kubectl apply -f deployment/kubernetes/ingress.yaml

    # Wait for rollout
    log_info "Waiting for deployments to be ready..."
    kubectl rollout status deployment/backend-deployment -n workflow-builder --timeout=300s
    kubectl rollout status deployment/frontend-deployment -n workflow-builder --timeout=300s

    log_success "Kubernetes deployment completed"
}

# Function to wait for services to be healthy
wait_for_services() {
    log_info "Waiting for services to be healthy..."

    local max_attempts=60
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if check_service_health; then
            log_success "All services are healthy"
            return 0
        fi

        if [ $attempt -eq $max_attempts ]; then
            log_error "Services failed to become healthy within timeout"
            show_service_logs
            exit 1
        fi

        log_info "Waiting for services... (attempt $attempt/$max_attempts)"
        sleep 5
        ((attempt++))
    done
}

# Function to check service health
check_service_health() {
    # Check backend health
    if ! curl -f -s http://localhost:8000/health >/dev/null 2>&1; then
        return 1
    fi

    # Check frontend accessibility
    if ! curl -f -s http://localhost:3000 >/dev/null 2>&1; then
        return 1
    fi

    return 0
}

# Function to show service logs
show_service_logs() {
    log_info "Showing service logs for debugging..."
    
    echo ""
    log_info "Backend logs:"
    docker-compose -f "$COMPOSE_FILE" logs --tail=20 backend

    echo ""
    log_info "Frontend logs:"
    docker-compose -f "$COMPOSE_FILE" logs --tail=20 frontend

    echo ""
    log_info "Database logs:"
    docker-compose -f "$COMPOSE_FILE" logs --tail=20 postgres
}

# Function to run database migrations
run_migrations() {
    log_info "Running database migrations..."

    # Wait for database to be ready
    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_isready -U genai_user -d genai_stack_db >/dev/null 2>&1; then
            break
        fi

        if [ $attempt -eq $max_attempts ]; then
            log_error "Database is not ready after $max_attempts attempts"
            exit 1
        fi

        log_info "Waiting for database... (attempt $attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done

    # Run migrations
    docker-compose -f "$COMPOSE_FILE" exec backend alembic upgrade head

    log_success "Database migrations completed"
}

# Function to create database backup before deployment
backup_database() {
    if [ "$ENVIRONMENT" = "production" ]; then
        log_info "Creating database backup before deployment..."

        local backup_file="backup_$(date +%Y%m%d_%H%M%S).sql"
        
        # Create backup
        docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_dump -U genai_user genai_stack_db > "$backup_file"

        # Upload to cloud storage if configured
        if [ -n "$AWS_S3_BUCKET" ]; then
            aws s3 cp "$backup_file" "s3://$AWS_S3_BUCKET/backups/"
            rm "$backup_file"
            log_success "Database backup uploaded to S3"
        else
            log_warning "No backup storage configured, backup saved locally: $backup_file"
        fi
    fi
}

# Function to run smoke tests
run_smoke_tests() {
    log_info "Running smoke tests..."

    # Test health endpoint
    if ! curl -f http://localhost:8000/health >/dev/null 2>&1; then
        log_error "Backend health check failed"
        return 1
    fi

    # Test frontend
    if ! curl -f http://localhost:3000 >/dev/null 2>&1; then
        log_error "Frontend accessibility test failed"
        return 1
    fi

    # Test API functionality
    if ! curl -f -X GET http://localhost:8000/api/v1/nodes/types >/dev/null 2>&1; then
        log_error "API functionality test failed"
        return 1
    fi

    log_success "Smoke tests passed"
}

# Function to send deployment notification
send_notification() {
    local status=$1
    local environment=$2

    if [ -n "$SLACK_WEBHOOK_URL" ]; then
        local color="good"
        local message="✅ Deployment to $environment completed successfully"
        
        if [ "$status" = "failed" ]; then
            color="danger"
            message="❌ Deployment to $environment failed"
        fi

        curl -X POST -H 'Content-type: application/json' \
            --data "{
                \"attachments\": [{
                    \"color\": \"$color\",
                    \"title\": \"GenAI Stack Deployment\",
                    \"text\": \"$message\",
                    \"fields\": [
                        {\"title\": \"Environment\", \"value\": \"$environment\", \"short\": true},
                        {\"title\": \"Version\", \"value\": \"${VERSION:-latest}\", \"short\": true}
                    ]
                }]
            }" \
            "$SLACK_WEBHOOK_URL"
    fi
}

# Function to rollback deployment
rollback() {
    log_warning "Rolling back deployment..."

    # For Docker Compose, restart with previous images
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down
    
    # Pull previous version if specified
    if [ -n "$ROLLBACK_VERSION" ]; then
        docker pull "${DOCKER_REGISTRY:-localhost}/${PROJECT_NAME}-frontend:${ROLLBACK_VERSION}"
        docker pull "${DOCKER_REGISTRY:-localhost}/${PROJECT_NAME}-backend:${ROLLBACK_VERSION}"
    fi

    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d

    log_success "Rollback completed"
}

# Function to show deployment status
show_status() {
    echo ""
    log_success "🎉 Deployment completed successfully!"
    echo ""
    echo -e "${BLUE}Deployment Summary:${NC}"
    echo "  Environment: $ENVIRONMENT"
    echo "  Version: ${VERSION:-latest}"
    echo "  Deploy Time: $(date)"
    echo ""
    echo -e "${BLUE}Service URLs:${NC}"
    
    if [ "$ENVIRONMENT" = "production" ]; then
        echo "  Frontend: https://${FRONTEND_DOMAIN}"
        echo "  Backend: https://${API_DOMAIN}"
        echo "  API Docs: https://${API_DOMAIN}/docs"
    else
        echo "  Frontend: http://localhost:3000"
        echo "  Backend: http://localhost:8000"
        echo "  API Docs: http://localhost:8000/docs"
    fi
    
    echo ""
    echo -e "${BLUE}Monitoring:${NC}"
    if [ -n "$GRAFANA_URL" ]; then
        echo "  Grafana: $GRAFANA_URL"
    fi
    if [ -n "$PROMETHEUS_URL" ]; then
        echo "  Prometheus: $PROMETHEUS_URL"
    fi
    echo ""
}

# Main deployment function
main() {
    echo ""
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                   GenAI Stack Deployment                    ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    # Parse command line arguments
    ENVIRONMENT="$DEFAULT_ENVIRONMENT"
    DEPLOYMENT_METHOD="docker-compose"
    SKIP_MIGRATIONS=false
    SKIP_BACKUP=false
    SKIP_TESTS=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -m|--method)
                DEPLOYMENT_METHOD="$2"
                shift 2
                ;;
            --skip-migrations)
                SKIP_MIGRATIONS=true
                shift
                ;;
            --skip-backup)
                SKIP_BACKUP=true
                shift
                ;;
            --skip-tests)
                SKIP_TESTS=true
                shift
                ;;
            --rollback)
                ROLLBACK_VERSION="$2"
                shift 2
                ;;
            -h|--help)
                echo "Usage: $0 [options] <environment>"
                echo ""
                echo "Arguments:"
                echo "  environment            Target environment (development, staging, production)"
                echo ""
                echo "Options:"
                echo "  -e, --environment ENV  Target environment"
                echo "  -m, --method METHOD    Deployment method (docker-compose, kubernetes)"
                echo "  --skip-migrations      Skip database migrations"
                echo "  --skip-backup          Skip database backup"
                echo "  --skip-tests           Skip smoke tests"
                echo "  --rollback VERSION     Rollback to specific version"
                echo "  -h, --help             Show this help message"
                echo ""
                echo "Examples:"
                echo "  $0 staging"
                echo "  $0 --environment production --method kubernetes"
                echo "  $0 --rollback v1.0.0 production"
                exit 0
                ;;
            *)
                if [ -z "$ENVIRONMENT" ] || [ "$ENVIRONMENT" = "$DEFAULT_ENVIRONMENT" ]; then
                    ENVIRONMENT="$1"
                else
                    log_error "Unknown option: $1"
                    exit 1
                fi
                shift
                ;;
        esac
    done

    # Handle rollback
    if [ -n "$ROLLBACK_VERSION" ]; then
        load_env_config "$ENVIRONMENT"
        rollback
        exit 0
    fi

    log_info "Starting deployment to $ENVIRONMENT"
    log_info "Deployment method: $DEPLOYMENT_METHOD"

    # Set up error handling for notifications
    trap 'send_notification "failed" "$ENVIRONMENT"' ERR

    # Run deployment steps
    load_env_config "$ENVIRONMENT"
    validate_environment

    if [ "$SKIP_BACKUP" = false ]; then
        backup_database
    fi

    # Deploy based on method
    case $DEPLOYMENT_METHOD in
        docker-compose)
            deploy_docker_compose
            ;;
        kubernetes)
            deploy_kubernetes
            ;;
        *)
            log_error "Unknown deployment method: $DEPLOYMENT_METHOD"
            exit 1
            ;;
    esac

    if [ "$SKIP_MIGRATIONS" = false ]; then
        run_migrations
    fi

    if [ "$SKIP_TESTS" = false ]; then
        run_smoke_tests
    fi

    # Send success notification
    send_notification "success" "$ENVIRONMENT"
    
    show_status
}

# Run main function
main "$@"
