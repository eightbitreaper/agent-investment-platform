#!/bin/bash
# Agent Investment Platform - Environment Setup Script
# This script helps set up environment variables and dependencies

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Script info
echo "=================================================="
echo "Agent Investment Platform - Environment Setup"
echo "=================================================="
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    log_info "Creating .env file from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        log_success ".env file created from template"
        log_warning "Please edit .env file with your actual API keys and configuration"
    else
        log_error ".env.example file not found!"
        exit 1
    fi
else
    log_info ".env file already exists"
fi

# Create required directories
log_info "Creating required directories..."
directories=("data" "reports" "logs" "models" "templates/reports")

for dir in "${directories[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        log_success "Created directory: $dir"
    else
        log_info "Directory already exists: $dir"
    fi
done

# Create .gitkeep files for empty directories
for dir in "${directories[@]}"; do
    if [ ! -f "$dir/.gitkeep" ] && [ -z "$(ls -A "$dir" 2>/dev/null)" ]; then
        touch "$dir/.gitkeep"
        log_success "Created .gitkeep in: $dir"
    fi
done

# Check Python version
log_info "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
log_info "Python version: $python_version"

# Check if Python version is 3.9+
python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)" 2>/dev/null
if [ $? -eq 0 ]; then
    log_success "Python version is compatible (3.9+)"
else
    log_warning "Python 3.9+ is recommended for best compatibility"
fi

# Check if virtual environment exists
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    log_info "Creating Python virtual environment..."
    python3 -m venv venv
    log_success "Virtual environment created"
    log_info "To activate: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)"
else
    log_info "Virtual environment already exists"
fi

# Install Python dependencies if virtual environment is active
if [[ "$VIRTUAL_ENV" != "" ]]; then
    log_info "Installing Python dependencies..."
    pip install -r requirements.txt
    log_success "Python dependencies installed"
else
    log_warning "Virtual environment not active. Run 'source venv/bin/activate' first, then install dependencies with 'pip install -r requirements.txt'"
fi

# Check Node.js for JavaScript MCP servers
if command -v node >/dev/null 2>&1; then
    node_version=$(node --version)
    log_success "Node.js found: $node_version"

    # Check if package.json exists for Node.js dependencies
    if [ -f "package.json" ]; then
        log_info "Installing Node.js dependencies..."
        npm install
        log_success "Node.js dependencies installed"
    else
        log_info "No package.json found, skipping Node.js dependencies"
    fi
else
    log_warning "Node.js not found. Install Node.js for JavaScript MCP servers"
fi

# Check Docker
if command -v docker >/dev/null 2>&1; then
    docker_version=$(docker --version)
    log_success "Docker found: $docker_version"

    # Check if Docker is running
    if docker info >/dev/null 2>&1; then
        log_success "Docker daemon is running"
    else
        log_warning "Docker daemon is not running. Start Docker for containerized deployment"
    fi
else
    log_warning "Docker not found. Install Docker for containerized deployment"
fi

# Check Git configuration
if command -v git >/dev/null 2>&1; then
    log_success "Git found"

    # Check if git is configured
    git_user=$(git config --global user.name 2>/dev/null || echo "")
    git_email=$(git config --global user.email 2>/dev/null || echo "")

    if [ -n "$git_user" ] && [ -n "$git_email" ]; then
        log_success "Git configured for: $git_user <$git_email>"
    else
        log_warning "Git not configured. Set up with:"
        echo "  git config --global user.name 'Your Name'"
        echo "  git config --global user.email 'your.email@example.com'"
    fi
else
    log_error "Git not found. Please install Git"
fi

# Check VS Code
if command -v code >/dev/null 2>&1; then
    log_success "VS Code found"
    log_info "You can open the project with: code ."
else
    log_warning "VS Code not found. Install VS Code for the best development experience"
fi

# Environment variable checks
log_info "Checking environment variables..."
source .env 2>/dev/null || true

# Check critical environment variables
env_vars=("ALPHA_VANTAGE_API_KEY" "NEWS_API_KEY" "OPENAI_API_KEY" "ANTHROPIC_API_KEY")
configured_vars=0

for var in "${env_vars[@]}"; do
    if [ -n "${!var}" ]; then
        log_success "$var is configured"
        ((configured_vars++))
    else
        log_warning "$var is not configured"
    fi
done

if [ $configured_vars -eq 0 ]; then
    log_warning "No API keys configured. The platform will have limited functionality."
    log_info "Edit .env file to add your API keys"
else
    log_success "$configured_vars out of ${#env_vars[@]} API keys configured"
fi

# Run health check if available
if [ -f "scripts/health-check.py" ]; then
    log_info "Running system health check..."
    python3 scripts/health-check.py || log_warning "Health check completed with warnings"
else
    log_warning "Health check script not found"
fi

# Final recommendations
echo ""
echo "=================================================="
echo "Setup Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Test the platform: python scripts/validate-setup.py"
echo "4. Open in VS Code: code ."
echo "5. Follow the initialization guide: docs/setup/initialize.prompt.md"
echo ""
echo "For help, see: docs/setup/installation-guide.md"
echo "=================================================="
