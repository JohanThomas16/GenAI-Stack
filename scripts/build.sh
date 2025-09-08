#!/bin/bash

# GenAI Stack Build Script
# ========================
# This script builds Docker images for production deployment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
PROJECT_NAME="genai-stack"
REGISTRY=${DOCKER_REGISTRY:-"localhost"}
VERSION=${VERSION:-"latest"}
BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
GIT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

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

# Function to check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Function to build frontend
build_frontend() {
    log_info "Building frontend Docker image..."

    cd frontend

    # Build production image
    docker build \
        --tag "${REGISTRY}/${PROJECT_NAME}-frontend:${VERSION}" \
        --tag "${REGISTRY}/${PROJECT_NAME}-frontend:latest" \
        --label "org.opencontainers.image.title=GenAI Stack Frontend" \
        --label "org.opencontainers.image.description=React frontend for GenAI Stack" \
        --label "org.opencontainers.image.version=${VERSION}" \
        --label "org.opencontainers.image.created=${BUILD_DATE}" \
        --label "org.opencontainers.image.revision=${GIT_COMMIT}" \
        --label "org.opencontainers.image.source=https://github.com/your-username/genai-stack" \
        --file Dockerfile.prod \
        .

    cd ..
    log_success "Frontend image built successfully"
}

# Function to build backend
build_backend() {
    log_info "Building backend Docker image..."

    cd backend

    # Build production image
    docker build \
        --tag "${REGISTRY}/${PROJECT_NAME}-backend:${VERSION}" \
        --tag "${REGISTRY}/${PROJECT_NAME}-backend:latest" \
        --label "org.opencontainers.image.title=GenAI Stack Backend" \
        --label "org.opencontainers.image.description=FastAPI backend for GenAI Stack" \
        --label "org.opencontainers.image.version=${VERSION}" \
        --label "org.opencontainers.image.created=${BUILD_DATE}" \
        --label "org.opencontainers.image.revision=${GIT_COMMIT}" \
        --label "org.opencontainers.image.source=https://github.com/your-username/genai-stack" \
        --file Dockerfile.prod \
        .

    cd ..
    log_success "Backend image built successfully"
}

# Function to run tests
run_tests() {
    log_info "Running tests..."

    # Frontend tests
    log_info "Running frontend tests..."
    cd frontend
    if [ -f "package.json" ]; then
        npm test -- --coverage --watchAll=false
        log_success "Frontend tests passed"
    else
        log_warning "No frontend package.json found, skipping tests"
    fi
    cd ..

    # Backend tests
    log_info "Running backend tests..."
    cd backend
    if [ -f "requirements.txt" ] && [ -d "tests" ]; then
        # Use Docker to run tests in isolated environment
        docker run --rm \
            -v $(pwd):/app \
            -w /app \
            python:3.9-slim \
            bash -c "pip install -r requirements.txt && python -m pytest tests/ -v"
        log_success "Backend tests passed"
    else
        log_warning "No backend tests found, skipping"
    fi
    cd ..
}

# Function to scan images for vulnerabilities
security_scan() {
    log_info "Running security scan..."

    if command -v trivy >/dev/null 2>&1; then
        log_info "Scanning frontend image..."
        trivy image "${REGISTRY}/${PROJECT_NAME}-frontend:${VERSION}"

        log_info "Scanning backend image..."
        trivy image "${REGISTRY}/${PROJECT_NAME}-backend:${VERSION}"

        log_success "Security scan completed"
    else
        log_warning "Trivy not found, skipping security scan"
        log_warning "Install Trivy for vulnerability scanning: https://trivy.dev/"
    fi
}

# Function to push images to registry
push_images() {
    if [ "$REGISTRY" != "localhost" ]; then
        log_info "Pushing images to registry..."

        # Login to registry if credentials are available
        if [ -n "$DOCKER_USERNAME" ] && [ -n "$DOCKER_PASSWORD" ]; then
            echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin "$REGISTRY"
        fi

        # Push frontend
        docker push "${REGISTRY}/${PROJECT_NAME}-frontend:${VERSION}"
        docker push "${REGISTRY}/${PROJECT_NAME}-frontend:latest"

        # Push backend
        docker push "${REGISTRY}/${PROJECT_NAME}-backend:${VERSION}"
        docker push "${REGISTRY}/${PROJECT_NAME}-backend:latest"

        log_success "Images pushed to registry"
    else
        log_info "Using local registry, skipping push"
    fi
}

# Function to save build artifacts
save_artifacts() {
    log_info "Saving build artifacts..."

    # Create artifacts directory
    mkdir -p artifacts

    # Save image information
    cat > artifacts/images.txt << EOF
Frontend Image: ${REGISTRY}/${PROJECT_NAME}-frontend:${VERSION}
Backend Image: ${REGISTRY}/${PROJECT_NAME}-backend:${VERSION}
Build Date: ${BUILD_DATE}
Git Commit: ${GIT_COMMIT}
Registry: ${REGISTRY}
EOF

    # Export images for offline deployment
    if [ "$EXPORT_IMAGES" = "true" ]; then
        log_info "Exporting images..."
        docker save \
            "${REGISTRY}/${PROJECT_NAME}-frontend:${VERSION}" \
            "${REGISTRY}/${PROJECT_NAME}-backend:${VERSION}" \
            | gzip > "artifacts/${PROJECT_NAME}-${VERSION}.tar.gz"
        log_success "Images exported to artifacts/${PROJECT_NAME}-${VERSION}.tar.gz"
    fi

    log_success "Build artifacts saved"
}

# Function to cleanup old images
cleanup() {
    log_info "Cleaning up old images..."

    # Remove dangling images
    docker image prune -f >/dev/null 2>&1 || true

    # Remove old tagged images (keep last 3)
    OLD_IMAGES=$(docker images "${REGISTRY}/${PROJECT_NAME}-frontend" --format "table {{.Repository}}:{{.Tag}}\t{{.CreatedAt}}" | tail -n +2 | sort -k2 -r | tail -n +4 | cut -f1)
    if [ -n "$OLD_IMAGES" ]; then
        echo "$OLD_IMAGES" | xargs docker rmi >/dev/null 2>&1 || true
    fi

    OLD_IMAGES=$(docker images "${REGISTRY}/${PROJECT_NAME}-backend" --format "table {{.Repository}}:{{.Tag}}\t{{.CreatedAt}}" | tail -n +2 | sort -k2 -r | tail -n +4 | cut -f1)
    if [ -n "$OLD_IMAGES" ]; then
        echo "$OLD_IMAGES" | xargs docker rmi >/dev/null 2>&1 || true
    fi

    log_success "Cleanup completed"
}

# Function to display build summary
show_summary() {
    echo ""
    log_success "🎉 Build completed successfully!"
    echo ""
    echo -e "${BLUE}Build Summary:${NC}"
    echo "  Project: $PROJECT_NAME"
    echo "  Version: $VERSION"
    echo "  Registry: $REGISTRY"
    echo "  Git Commit: $GIT_COMMIT"
    echo "  Build Date: $BUILD_DATE"
    echo ""
    echo -e "${BLUE}Images Built:${NC}"
    echo "  Frontend: ${REGISTRY}/${PROJECT_NAME}-frontend:${VERSION}"
    echo "  Backend:  ${REGISTRY}/${PROJECT_NAME}-backend:${VERSION}"
    echo ""
    
    if [ "$REGISTRY" != "localhost" ]; then
        echo -e "${BLUE}Deployment Command:${NC}"
        echo "  docker-compose -f docker-compose.prod.yml pull"
        echo "  docker-compose -f docker-compose.prod.yml up -d"
    else
        echo -e "${BLUE}Local Testing:${NC}"
        echo "  docker-compose up -d"
    fi
    echo ""
}

# Main build function
main() {
    echo ""
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                     GenAI Stack Build                       ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    # Parse command line arguments
    RUN_TESTS=true
    RUN_SECURITY_SCAN=false
    PUSH_IMAGES=false
    EXPORT_IMAGES=false
    CLEANUP_OLD=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            --version)
                VERSION="$2"
                shift 2
                ;;
            --registry)
                REGISTRY="$2"
                shift 2
                ;;
            --skip-tests)
                RUN_TESTS=false
                shift
                ;;
            --security-scan)
                RUN_SECURITY_SCAN=true
                shift
                ;;
            --push)
                PUSH_IMAGES=true
                shift
                ;;
            --export)
                EXPORT_IMAGES=true
                shift
                ;;
            --cleanup)
                CLEANUP_OLD=true
                shift
                ;;
            -h|--help)
                echo "Usage: $0 [options]"
                echo ""
                echo "Options:"
                echo "  --version VERSION      Set build version (default: latest)"
                echo "  --registry REGISTRY    Set Docker registry (default: localhost)"
                echo "  --skip-tests           Skip running tests"
                echo "  --security-scan        Run security vulnerability scan"
                echo "  --push                 Push images to registry"
                echo "  --export               Export images as tar.gz"
                echo "  --cleanup              Clean up old images"
                echo "  -h, --help             Show this help message"
                echo ""
                echo "Environment Variables:"
                echo "  DOCKER_REGISTRY        Docker registry URL"
                echo "  DOCKER_USERNAME        Registry username"
                echo "  DOCKER_PASSWORD        Registry password"
                echo "  VERSION               Build version"
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done

    # Validate inputs
    if [ -z "$VERSION" ]; then
        log_error "Version is required"
        exit 1
    fi

    log_info "Building version: $VERSION"
    log_info "Registry: $REGISTRY"
    log_info "Git commit: $GIT_COMMIT"

    # Run build steps
    check_docker

    if [ "$RUN_TESTS" = true ]; then
        run_tests
    fi

    build_frontend
    build_backend

    if [ "$RUN_SECURITY_SCAN" = true ]; then
        security_scan
    fi

    if [ "$PUSH_IMAGES" = true ]; then
        push_images
    fi

    save_artifacts

    if [ "$CLEANUP_OLD" = true ]; then
        cleanup
    fi

    show_summary
}

# Run main function
main "$@"
