#!/bin/bash

# GenAI Stack Setup Script
# =========================
# This script sets up the development environment for GenAI Stack

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="GenAI Stack"
REQUIRED_DOCKER_VERSION="20.10"
REQUIRED_NODE_VERSION="18"
REQUIRED_PYTHON_VERSION="3.9"

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to compare versions
version_ge() {
    printf '%s\n%s\n' "$2" "$1" | sort -V -C
}

# Function to check system requirements
check_system_requirements() {
    log_info "Checking system requirements..."

    # Check operating system
    OS="$(uname -s)"
    case "${OS}" in
        Linux*)     MACHINE=Linux;;
        Darwin*)    MACHINE=Mac;;
        CYGWIN*)    MACHINE=Cygwin;;
        MINGW*)     MACHINE=MinGw;;
        *)          MACHINE="UNKNOWN:${OS}";;
    esac
    log_info "Operating System: $MACHINE"

    # Check Docker
    if command_exists docker; then
        DOCKER_VERSION=$(docker --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
        if version_ge "$DOCKER_VERSION" "$REQUIRED_DOCKER_VERSION"; then
            log_success "Docker $DOCKER_VERSION is installed (required: $REQUIRED_DOCKER_VERSION+)"
        else
            log_error "Docker version $DOCKER_VERSION is too old (required: $REQUIRED_DOCKER_VERSION+)"
            exit 1
        fi
    else
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    # Check Docker Compose
    if command_exists docker-compose; then
        COMPOSE_VERSION=$(docker-compose --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
        log_success "Docker Compose $COMPOSE_VERSION is installed"
    else
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi

    # Check Node.js
    if command_exists node; then
        NODE_VERSION=$(node --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
        if version_ge "$NODE_VERSION" "$REQUIRED_NODE_VERSION.0"; then
            log_success "Node.js $NODE_VERSION is installed (required: $REQUIRED_NODE_VERSION+)"
        else
            log_error "Node.js version $NODE_VERSION is too old (required: $REQUIRED_NODE_VERSION+)"
            exit 1
        fi
    else
        log_error "Node.js is not installed. Please install Node.js first."
        exit 1
    fi

    # Check Python
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
        if version_ge "$PYTHON_VERSION" "$REQUIRED_PYTHON_VERSION.0"; then
            log_success "Python $PYTHON_VERSION is installed (required: $REQUIRED_PYTHON_VERSION+)"
        else
            log_error "Python version $PYTHON_VERSION is too old (required: $REQUIRED_PYTHON_VERSION+)"
            exit 1
        fi
    else
        log_error "Python 3 is not installed. Please install Python 3 first."
        exit 1
    fi

    # Check Git
    if command_exists git; then
        GIT_VERSION=$(git --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
        log_success "Git $GIT_VERSION is installed"
    else
        log_error "Git is not installed. Please install Git first."
        exit 1
    fi
}

# Function to setup environment file
setup_environment() {
    log_info "Setting up environment configuration..."

    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_success "Created .env file from .env.example"
            
            # Generate secure secrets
            SECRET_KEY=$(openssl rand -hex 32)
            JWT_SECRET_KEY=$(openssl rand -hex 32)
            
            # Update .env file with generated secrets
            if command_exists sed; then
                sed -i.bak "s/your-super-secret-key-change-in-production-min-32-chars/$SECRET_KEY/g" .env
                sed -i.bak "s/your-jwt-secret-key-change-in-production-min-32-chars/$JWT_SECRET_KEY/g" .env
                rm .env.bak 2>/dev/null || true
                log_success "Generated secure secret keys"
            fi
            
            log_warning "Please update .env file with your API keys:"
            log_warning "  - OPENAI_API_KEY (required)"
            log_warning "  - GEMINI_API_KEY (optional)"
            log_warning "  - SERP_API_KEY (optional)"
        else
            log_error ".env.example file not found"
            exit 1
        fi
    else
        log_info ".env file already exists, skipping..."
    fi
}

# Function to install backend dependencies
setup_backend() {
    log_info "Setting up backend dependencies..."

    if [ -d "backend" ]; then
        cd backend

        # Check if virtual environment exists
        if [ ! -d "venv" ]; then
            log_info "Creating Python virtual environment..."
            python3 -m venv venv
            log_success "Virtual environment created"
        fi

        # Activate virtual environment and install dependencies
        log_info "Installing Python dependencies..."
        source venv/bin/activate
        
        if [ -f "requirements.txt" ]; then
            pip install --upgrade pip
            pip install -r requirements.txt
            log_success "Backend dependencies installed"
        else
            log_error "requirements.txt not found in backend directory"
            cd ..
            exit 1
        fi

        cd ..
    else
        log_error "Backend directory not found"
        exit 1
    fi
}

# Function to install frontend dependencies
setup_frontend() {
    log_info "Setting up frontend dependencies..."

    if [ -d "frontend" ]; then
        cd frontend

        if [ -f "package.json" ]; then
            log_info "Installing Node.js dependencies..."
            npm install
            log_success "Frontend dependencies installed"
        else
            log_error "package.json not found in frontend directory"
            cd ..
            exit 1
        fi

        cd ..
    else
        log_error "Frontend directory not found"
        exit 1
    fi
}

# Function to setup Docker services
setup_docker() {
    log_info "Setting up Docker services..."

    # Pull required Docker images
    log_info "Pulling Docker images..."
    docker-compose pull postgres redis chromadb

    # Build application images
    log_info "Building application images..."
    docker-compose build

    log_success "Docker setup completed"
}

# Function to initialize database
init_database() {
    log_info "Initializing database..."

    # Start database service
    docker-compose up -d postgres

    # Wait for database to be ready
    log_info "Waiting for database to be ready..."
    sleep 10

    # Check if database is ready
    max_attempts=30
    attempt=1

    while [ $attempt -le $max_attempts ]; do
        if docker-compose exec -T postgres pg_isready -U genai_user -d genai_stack_db >/dev/null 2>&1; then
            log_success "Database is ready"
            break
        fi

        if [ $attempt -eq $max_attempts ]; then
            log_error "Database failed to start after $max_attempts attempts"
            exit 1
        fi

        log_info "Waiting for database... (attempt $attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done

    # Run database migrations
    if [ -d "backend" ]; then
        cd backend
        source venv/bin/activate
        
        # Check if alembic is configured
        if [ -f "alembic.ini" ]; then
            log_info "Running database migrations..."
            alembic upgrade head
            log_success "Database migrations completed"
        else
            log_warning "Alembic not configured, skipping migrations"
        fi
        
        cd ..
    fi
}

# Function to seed initial data
seed_data() {
    log_info "Seeding initial data..."

    if [ -f "scripts/seed_data.py" ]; then
        cd backend
        source venv/bin/activate
        python ../scripts/seed_data.py
        log_success "Initial data seeded"
        cd ..
    else
        log_warning "Seed data script not found, skipping..."
    fi
}

# Function to run health checks
health_check() {
    log_info "Running health checks..."

    # Start all services
    docker-compose up -d

    # Wait a bit for services to start
    sleep 10

    # Check backend health
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        log_success "Backend is healthy"
    else
        log_error "Backend health check failed"
        return 1
    fi

    # Check if frontend is accessible
    if curl -f http://localhost:3000 >/dev/null 2>&1; then
        log_success "Frontend is accessible"
    else
        log_error "Frontend is not accessible"
        return 1
    fi

    log_success "All health checks passed"
}

# Function to display final instructions
show_final_instructions() {
    echo ""
    log_success "🎉 $PROJECT_NAME setup completed successfully!"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Update your .env file with API keys:"
    echo "   - OPENAI_API_KEY (required for LLM functionality)"
    echo "   - GEMINI_API_KEY (optional)"
    echo "   - SERP_API_KEY (optional for web search)"
    echo ""
    echo "2. Access the application:"
    echo "   - Frontend: http://localhost:3000"
    echo "   - Backend API: http://localhost:8000"
    echo "   - API Documentation: http://localhost:8000/docs"
    echo ""
    echo "3. Useful commands:"
    echo "   - Start services: docker-compose up -d"
    echo "   - Stop services: docker-compose down"
    echo "   - View logs: docker-compose logs -f"
    echo "   - Run tests: make test"
    echo ""
    echo -e "${GREEN}Happy coding! 🚀${NC}"
}

# Function to cleanup on failure
cleanup_on_failure() {
    log_error "Setup failed. Cleaning up..."
    docker-compose down >/dev/null 2>&1 || true
    exit 1
}

# Main setup function
main() {
    echo ""
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                    $PROJECT_NAME Setup                      ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    # Set up error handling
    trap cleanup_on_failure ERR

    # Parse command line arguments
    SKIP_DEPS=false
    SKIP_DOCKER=false
    SKIP_DB=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-deps)
                SKIP_DEPS=true
                shift
                ;;
            --skip-docker)
                SKIP_DOCKER=true
                shift
                ;;
            --skip-db)
                SKIP_DB=true
                shift
                ;;
            -h|--help)
                echo "Usage: $0 [options]"
                echo ""
                echo "Options:"
                echo "  --skip-deps    Skip dependency installation"
                echo "  --skip-docker  Skip Docker setup"
                echo "  --skip-db      Skip database initialization"
                echo "  -h, --help     Show this help message"
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done

    # Run setup steps
    check_system_requirements
    setup_environment

    if [ "$SKIP_DEPS" = false ]; then
        setup_backend
        setup_frontend
    fi

    if [ "$SKIP_DOCKER" = false ]; then
        setup_docker
    fi

    if [ "$SKIP_DB" = false ]; then
        init_database
        seed_data
    fi

    health_check
    show_final_instructions
}

# Run main function
main "$@"
