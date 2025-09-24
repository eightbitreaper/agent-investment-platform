# Agent Investment Platform - Multi-stage Docker Build
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Upgrade pip to latest version for security updates
RUN pip install --upgrade pip>=25.2

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data logs reports models .memory

# Set permissions
RUN chmod +x scripts/*.py scripts/setup/*.py

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Production stage
FROM base as production

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose ports
EXPOSE 8000 3001 3002 3003 3004 3005 3006

# Default command
CMD ["python", "orchestrator.py", "--live"]

# Development stage
FROM base as development

# Ensure latest pip for development stage too
RUN pip install --upgrade pip>=25.2

# Install development dependencies
RUN pip install --no-cache-dir pytest pytest-cov black flake8 mypy jupyter

# Install Node.js for MCP servers
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Keep container running for development
CMD ["tail", "-f", "/dev/null"]

# Testing stage
FROM development as testing

# Copy test files
COPY tests/ tests/

# Run tests
RUN python -m pytest tests/ --cov=src/ --cov-report=html

# Validation stage
FROM base as validation

# Run comprehensive validation
RUN python scripts/setup/validate-setup.py --quick

# Default to production if no target specified
FROM production
