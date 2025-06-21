#!/bin/bash

# Personal Finance API Deployment Script
# This script helps set up and deploy the API

set -e

echo "🚀 Personal Finance API Deployment Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_status "Docker and Docker Compose are installed"
}

# Check if Python is installed
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.11+ first."
        exit 1
    fi
    
    python_version=$(python3 --version | cut -d' ' -f2)
    print_status "Python version: $python_version"
}

# Setup environment file
setup_env() {
    if [ ! -f .env ]; then
        print_status "Creating .env file from template..."
        cp env.example .env
        print_warning "Please edit .env file with your configuration before continuing"
        print_status "You can now edit .env file and run this script again"
        exit 0
    else
        print_status ".env file already exists"
    fi
}

# Build and run with Docker
deploy_docker() {
    print_status "Building Docker image..."
    docker build -t finance-api .
    
    print_status "Starting services with Docker Compose..."
    docker-compose up -d
    
    print_status "Waiting for services to start..."
    sleep 10
    
    # Check if API is running
    if curl -f http://localhost:8000/health &> /dev/null; then
        print_status "✅ API is running successfully!"
        print_status "📚 API Documentation: http://localhost:8000/docs"
        print_status "🏥 Health Check: http://localhost:8000/health"
    else
        print_error "❌ API failed to start. Check logs with: docker-compose logs api"
        exit 1
    fi
}

# Setup local development
setup_local() {
    print_status "Setting up local development environment..."
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Create logs directory
    mkdir -p logs
    
    print_status "✅ Local environment setup complete!"
    print_status "To start the API: source venv/bin/activate && uvicorn app.main:app --reload"
}

# Run tests
run_tests() {
    print_status "Running API tests..."
    
    if [ -f "test_api.py" ]; then
        python3 test_api.py
    else
        print_warning "Test file not found"
    fi
}

# Show logs
show_logs() {
    print_status "Showing API logs..."
    docker-compose logs -f api
}

# Stop services
stop_services() {
    print_status "Stopping services..."
    docker-compose down
    print_status "✅ Services stopped"
}

# Clean up
cleanup() {
    print_status "Cleaning up..."
    docker-compose down -v
    docker system prune -f
    print_status "✅ Cleanup complete"
}

# Main menu
show_menu() {
    echo ""
    echo "Choose an option:"
    echo "1) Setup environment file"
    echo "2) Deploy with Docker"
    echo "3) Setup local development"
    echo "4) Run tests"
    echo "5) Show logs"
    echo "6) Stop services"
    echo "7) Cleanup"
    echo "8) Exit"
    echo ""
    read -p "Enter your choice (1-8): " choice
    
    case $choice in
        1)
            setup_env
            ;;
        2)
            check_docker
            setup_env
            deploy_docker
            ;;
        3)
            check_python
            setup_env
            setup_local
            ;;
        4)
            run_tests
            ;;
        5)
            show_logs
            ;;
        6)
            stop_services
            ;;
        7)
            cleanup
            ;;
        8)
            print_status "Goodbye!"
            exit 0
            ;;
        *)
            print_error "Invalid choice. Please try again."
            show_menu
            ;;
    esac
}

# Check if running in interactive mode
if [ "$1" = "--non-interactive" ]; then
    check_docker
    setup_env
    deploy_docker
else
    show_menu
fi 