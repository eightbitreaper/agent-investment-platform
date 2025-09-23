# Docker Deployment Guide

Comprehensive guide for deploying the Agent Investment Platform using Docker containers in development, staging, and production environments.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Development Deployment](#development-deployment)
- [Production Deployment](#production-deployment)
- [Service Architecture](#service-architecture)
- [Environment Configuration](#environment-configuration)
- [Scaling and Load Balancing](#scaling-and-load-balancing)
- [Monitoring and Logging](#monitoring-and-logging)
- [Backup and Recovery](#backup-and-recovery)
- [Security Configuration](#security-configuration)
- [Troubleshooting](#troubleshooting)

## Overview

The Agent Investment Platform uses Docker Compose for orchestrating multiple services:

- **Main Application** - Core platform with web interface
- **MCP Servers** - 4 specialized analysis servers
- **Database Services** - PostgreSQL and Redis
- **Local LLM** - Ollama for private AI processing
- **Monitoring** - Prometheus and Grafana (optional)
- **Reverse Proxy** - Nginx with SSL (production)

## Prerequisites

### System Requirements

**Minimum Requirements**:
- **CPU**: 4 cores
- **RAM**: 8 GB
- **Storage**: 50 GB free space
- **OS**: Docker-compatible (Linux, Windows, macOS)

**Recommended for Production**:
- **CPU**: 8+ cores
- **RAM**: 32 GB (for local LLMs)
- **Storage**: 100+ GB SSD
- **Network**: Stable internet connection

### Required Software

1. **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
2. **Docker Compose** v2.0+
3. **Git** for repository access

#### Installation Commands

**Windows (PowerShell)**:
```powershell
# Install Docker Desktop
winget install Docker.DockerDesktop

# Verify installation
docker --version
docker-compose --version
```

**macOS**:
```bash
# Install Docker Desktop
brew install --cask docker

# Or download from: https://www.docker.com/products/docker-desktop
```

**Linux (Ubuntu/Debian)**:
```bash
# Install Docker
sudo apt update
sudo apt install -y docker.io docker-compose-v2

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
docker compose version
```

## Quick Start

Get the platform running in under 5 minutes:

### 1. Clone and Configure

```bash
# Clone repository
git clone https://github.com/your-username/agent-investment-platform.git
cd agent-investment-platform

# Create environment file
cp .env.example .env

# Edit .env with your API keys (optional for basic functionality)
# At minimum, set:
# POSTGRES_PASSWORD=your_secure_password
# REDIS_PASSWORD=your_redis_password
```

### 2. Start Core Services

```bash
# Start with basic services (no monitoring, no local LLM)
docker compose up -d

# Check service status
docker compose ps

# View logs
docker compose logs -f
```

### 3. Access the Platform

- **Web Interface**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **API Documentation**: http://localhost:8000/docs

### 4. Test the Setup

```bash
# Run health check
docker compose exec agent-investment-platform python scripts/setup/validate-setup.py --quick

# Generate test report
docker compose exec agent-investment-platform python orchestrator.py --test-mode
```

## Development Deployment

For development and testing environments:

### Development Profile

```bash
# Start development services
docker compose --profile development up -d

# This includes:
# - Hot reload for code changes
# - Jupyter notebook access
# - Development debugging tools
# - Direct volume mounts for live editing
```

### Development Configuration

The development profile includes additional features:

```yaml
# docker-compose.yml development section
dev-environment:
  volumes:
    - .:/app                    # Live code mounting
    - /app/node_modules        # Preserve node_modules
  ports:
    - \"8000:8000\"            # Main application
    - \"8888:8888\"            # Jupyter notebook
  environment:
    - ENVIRONMENT=development
    - DEBUG=true
```

### Development Workflow

```bash
# Start development environment
docker compose --profile development up -d

# Access development container
docker compose exec dev-environment bash

# Run tests inside container
docker compose exec dev-environment python -m pytest tests/ -v

# Access Jupyter notebook
# Navigate to http://localhost:8888

# Stop development services
docker compose --profile development down
```

## Production Deployment

### Production Profile

```bash
# Start production services with monitoring and SSL
docker compose --profile production --profile monitoring up -d
```

### Production Architecture

Production deployment includes:

- **Load Balancer** - Nginx reverse proxy with SSL
- **Monitoring Stack** - Prometheus + Grafana
- **Health Checks** - Automated service health monitoring
- **Log Aggregation** - Centralized logging
- **Backup Services** - Automated data backup

### SSL Configuration

1. **Obtain SSL Certificates**:
   ```bash
   # Using Let's Encrypt (recommended)
   sudo apt install certbot
   sudo certbot certonly --standalone -d your-domain.com

   # Copy certificates to nginx config
   sudo cp /etc/letsencrypt/live/your-domain.com/*.pem config/nginx/ssl/
   ```

2. **Configure Nginx**:
   ```nginx
   # config/nginx/nginx.conf
   server {
       listen 443 ssl http2;
       server_name your-domain.com;

       ssl_certificate /etc/nginx/ssl/fullchain.pem;
       ssl_certificate_key /etc/nginx/ssl/privkey.pem;

       location / {
           proxy_pass http://agent-investment-platform:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### Production Environment Variables

```bash
# .env for production
ENVIRONMENT=production

# Database settings
POSTGRES_PASSWORD=your_very_secure_password
POSTGRES_DB=investment_platform
DATABASE_URL=postgresql://postgres:${POSTGRES_PASSWORD}@postgres:5432/investment_platform

# Redis settings
REDIS_PASSWORD=your_secure_redis_password
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0

# SSL and security
SSL_CERT_PATH=/etc/nginx/ssl/fullchain.pem
SSL_KEY_PATH=/etc/nginx/ssl/privkey.pem
SECURE_COOKIES=true
SESSION_SECRET=your_session_secret_key

# Monitoring
GRAFANA_PASSWORD=your_grafana_admin_password
PROMETHEUS_RETENTION=90d

# Email notifications (production alerts)
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USER=your_email@gmail.com
EMAIL_SMTP_PASSWORD=your_app_password
```

## Service Architecture

### Core Services

#### Main Application
```yaml
agent-investment-platform:
  ports: [\"8000:8000\"]
  depends_on: [postgres, redis]
  healthcheck: Custom health endpoint
  restart: unless-stopped
```

#### MCP Servers
```yaml
# Stock Data Server (Python)
mcp-stock-server:
  ports: [\"3001:3001\"]
  command: [\"python\", \"src/mcp_servers/stock_data_server.py\"]

# News Analysis Server (Node.js)
mcp-news-server:
  ports: [\"3002:3002\"]
  command: [\"node\", \"src/mcp-servers/news-analysis-server.js\"]

# YouTube Server (Node.js)
mcp-youtube-server:
  ports: [\"3003:3003\"]
  command: [\"node\", \"src/mcp-servers/youtube-transcript-server.js\"]

# Analysis Engine Server (Python)
mcp-analysis-server:
  ports: [\"3004:3004\"]
  command: [\"python\", \"-m\", \"src.mcp_servers.analysis_engine_server\"]
```

#### Database Services
```yaml
# PostgreSQL for persistent data
postgres:
  image: postgres:15-alpine
  ports: [\"5432:5432\"]
  volumes: [\"postgres_data:/var/lib/postgresql/data\"]

# Redis for caching and sessions
redis:
  image: redis:7-alpine
  ports: [\"6379:6379\"]
  volumes: [\"redis_data:/data\"]
```

### Optional Services

#### Local LLM (Ollama)
```bash
# Start with local LLM support
docker compose --profile local-llm up -d ollama

# Download models after startup
docker compose exec ollama ollama pull llama3.1:8b
```

#### Monitoring Stack
```bash
# Start monitoring services
docker compose --profile monitoring up -d

# Access dashboards
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000 (admin/admin123)
```

## Environment Configuration

### Environment File Template

```bash
# .env.example - Copy to .env and customize

# === CORE CONFIGURATION ===
ENVIRONMENT=production                          # development, staging, production
DEBUG=false
LOG_LEVEL=INFO

# === API KEYS (Get free keys from providers) ===
POLYGON_API_KEY=your_polygon_api_key           # https://polygon.io/
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key   # https://www.alphavantage.co/
NEWS_API_KEY=your_news_api_key                 # https://newsapi.org/
FINNHUB_API_KEY=your_finnhub_key               # https://finnhub.io/

# === LLM CONFIGURATION ===
LLM_PROVIDER=local                             # local, openai, anthropic
OPENAI_API_KEY=your_openai_key                 # Optional
ANTHROPIC_API_KEY=your_anthropic_key           # Optional
OLLAMA_HOST=http://ollama:11434                # For Docker network

# === DATABASE CONFIGURATION ===
POSTGRES_PASSWORD=investment_platform_secure_2024
POSTGRES_DB=investment_platform
POSTGRES_USER=postgres
DATABASE_URL=postgresql://postgres:${POSTGRES_PASSWORD}@postgres:5432/investment_platform

# === REDIS CONFIGURATION ===
REDIS_PASSWORD=redis_secure_password_2024
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0

# === SECURITY ===
SESSION_SECRET=your_32_character_session_secret
JWT_SECRET=your_jwt_secret_key
SECURE_COOKIES=true

# === MONITORING ===
GRAFANA_PASSWORD=secure_grafana_password_2024
PROMETHEUS_RETENTION=30d

# === NOTIFICATIONS ===
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USER=your_email@gmail.com
EMAIL_SMTP_PASSWORD=your_gmail_app_password

DISCORD_WEBHOOK_URL=your_discord_webhook_url
SLACK_WEBHOOK_URL=your_slack_webhook_url

# === GITHUB INTEGRATION ===
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_REPO=your-username/investment-reports

# === STORAGE ===
DATA_DIRECTORY=/app/data
CACHE_DIRECTORY=/app/data_cache
MODELS_DIRECTORY=/app/models
```

### Profile-Based Deployment

Use Docker Compose profiles for different deployment scenarios:

```bash
# Basic deployment (core services only)
docker compose up -d

# Development with debugging tools
docker compose --profile development up -d

# Production with monitoring and SSL
docker compose --profile production --profile monitoring up -d

# Local LLM support
docker compose --profile local-llm up -d

# Full deployment (all services)
docker compose --profile production --profile monitoring --profile local-llm up -d
```

## Scaling and Load Balancing

### Horizontal Scaling

Scale individual services based on load:

```bash
# Scale MCP servers for high load
docker compose up -d --scale mcp-stock-server=3
docker compose up -d --scale mcp-news-server=2

# Scale analysis servers
docker compose up -d --scale mcp-analysis-server=2
```

### Load Balancer Configuration

```nginx
# config/nginx/nginx.conf
upstream stock_servers {
    server mcp-stock-server:3001;
    server mcp-stock-server:3001;
    server mcp-stock-server:3001;
}

upstream analysis_servers {
    server mcp-analysis-server:3004;
    server mcp-analysis-server:3004;
}

server {
    location /api/stock/ {
        proxy_pass http://stock_servers;
    }

    location /api/analysis/ {
        proxy_pass http://analysis_servers;
    }
}
```

### Resource Limits

```yaml
# docker-compose.yml
services:
  agent-investment-platform:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
```

## Monitoring and Logging

### Health Checks

All services include health checks:

```bash
# Check service health
docker compose ps

# View health check logs
docker inspect agent-investment-platform | grep -A 10 Health

# Manual health check
curl http://localhost:8000/health
```

### Log Management

```bash
# View logs for all services
docker compose logs -f

# View logs for specific service
docker compose logs -f agent-investment-platform

# View logs with timestamps
docker compose logs -f -t

# Follow logs from last 100 lines
docker compose logs -f --tail=100
```

### Monitoring Dashboard

Access monitoring services:

```bash
# Start monitoring stack
docker compose --profile monitoring up -d

# Access Grafana (admin/password from .env)
open http://localhost:3000

# Access Prometheus
open http://localhost:9090

# Pre-configured dashboards available at:
# - Investment Platform Overview
# - MCP Server Performance
# - Database Metrics
# - System Resources
```

## Backup and Recovery

### Automated Backups

```bash
# Create backup script
cat > scripts/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=\"./backups/$(date +%Y%m%d_%H%M%S)\"
mkdir -p \"$BACKUP_DIR\"

# Backup PostgreSQL
docker compose exec -T postgres pg_dump -U postgres investment_platform > \"$BACKUP_DIR/database.sql\"

# Backup Redis
docker compose exec -T redis redis-cli --rdb - > \"$BACKUP_DIR/redis.rdb\"

# Backup application data
docker compose exec -T agent-investment-platform tar -czf - /app/data > \"$BACKUP_DIR/app_data.tar.gz\"

echo \"Backup completed: $BACKUP_DIR\"
EOF

chmod +x scripts/backup.sh
```

### Restore Procedures

```bash
# Restore from backup
BACKUP_DIR=\"./backups/20241201_120000\"

# Restore PostgreSQL
docker compose exec -T postgres psql -U postgres -c \"DROP DATABASE IF EXISTS investment_platform;\"
docker compose exec -T postgres psql -U postgres -c \"CREATE DATABASE investment_platform;\"
docker compose exec -T postgres psql -U postgres investment_platform < \"$BACKUP_DIR/database.sql\"

# Restore Redis
docker compose exec -T redis redis-cli FLUSHALL
docker compose exec -T redis sh -c \"cat > /tmp/dump.rdb\" < \"$BACKUP_DIR/redis.rdb\"
docker compose restart redis

# Restore application data
docker compose exec -T agent-investment-platform tar -xzf - -C / < \"$BACKUP_DIR/app_data.tar.gz\"
```

### Automated Backup Schedule

```yaml
# Add to docker-compose.yml
backup-service:
  image: alpine:latest
  container_name: backup-service
  restart: unless-stopped
  volumes:
    - ./backups:/backups
    - ./scripts:/scripts
    - /var/run/docker.sock:/var/run/docker.sock
  command: crond -f
  profiles:
    - production
```

## Security Configuration

### Network Security

```yaml
# Secure network configuration
networks:
  investment-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
    driver_opts:
      com.docker.network.bridge.enable_icc: \"false\"
      com.docker.network.bridge.enable_ip_masquerade: \"true\"
```

### Secrets Management

```bash
# Use Docker secrets for sensitive data
echo \"your_database_password\" | docker secret create db_password -
echo \"your_redis_password\" | docker secret create redis_password -

# Reference in docker-compose.yml
services:
  postgres:
    secrets:
      - db_password
    environment:
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password
```

### SSL/TLS Configuration

```bash
# Generate self-signed certificates for development
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout config/nginx/ssl/privkey.pem \
  -out config/nginx/ssl/fullchain.pem \
  -subj \"/C=US/ST=State/L=City/O=Organization/CN=localhost\"

# For production, use Let's Encrypt:
# sudo certbot certonly --standalone -d your-domain.com
```

### Container Security

```dockerfile
# Dockerfile security best practices
# Run as non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser
USER appuser

# Read-only root filesystem
docker run --read-only --tmpfs /tmp --tmpfs /var/tmp

# Drop capabilities
docker run --cap-drop=ALL --cap-add=NET_BIND_SERVICE
```

## Troubleshooting

### Common Issues and Solutions

#### Port Conflicts
```bash
# Problem: Port already in use
# Solution: Check and stop conflicting services
netstat -tulpn | grep :8000
docker ps | grep 8000

# Kill conflicting process
sudo lsof -ti:8000 | xargs kill -9
```

#### Database Connection Issues
```bash
# Problem: Cannot connect to PostgreSQL
# Solution: Check database status and credentials
docker compose logs postgres
docker compose exec postgres pg_isready -U postgres

# Reset database
docker compose down
docker volume rm agent-investment-platform_postgres_data
docker compose up -d postgres
```

#### Memory Issues
```bash
# Problem: Out of memory errors
# Solution: Increase Docker memory limits
# Docker Desktop → Settings → Resources → Memory

# Check memory usage
docker stats

# Restart services with memory limits
docker compose down
docker compose up -d --memory=4g
```

#### MCP Server Connection Errors
```bash
# Problem: MCP servers not responding
# Solution: Check server health and restart
docker compose ps
docker compose logs mcp-stock-server

# Restart specific MCP server
docker compose restart mcp-stock-server

# Restart all MCP servers
docker compose restart mcp-stock-server mcp-news-server mcp-youtube-server mcp-analysis-server
```

#### Local LLM Issues
```bash
# Problem: Ollama not downloading models
# Solution: Manual model download
docker compose exec ollama ollama pull llama3.1:8b

# Check model status
docker compose exec ollama ollama list

# Test model
docker compose exec ollama ollama run llama3.1:8b \"Hello, test\"
```

### Debugging Commands

```bash
# Service status and health
docker compose ps
docker compose top

# Resource usage
docker stats

# Network connectivity
docker compose exec agent-investment-platform ping postgres
docker compose exec agent-investment-platform nc -zv redis 6379

# Container logs with timestamps
docker compose logs -f -t --tail=50

# Execute commands in containers
docker compose exec agent-investment-platform bash
docker compose exec postgres psql -U postgres

# Inspect container configuration
docker inspect agent-investment-platform

# View container processes
docker compose exec agent-investment-platform ps aux
```

### Performance Optimization

```bash
# Enable BuildKit for faster builds
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Use multi-stage builds for smaller images
# (Already implemented in Dockerfile)

# Optimize image layers
docker system prune -a

# Monitor resource usage
docker compose exec agent-investment-platform top
docker compose exec agent-investment-platform free -m
```

## Related Documentation

- [Installation Guide](../setup/installation-guide.md) - Complete platform setup
- [Configuration Guide](../setup/configuration-guide.md) - Configuration customization
- [Local LLM Setup Guide](../setup/local-llm-setup.md) - Local AI model setup
- [Troubleshooting Guide](../troubleshooting/common-issues.md) - Common problems and solutions
- [API Documentation](../api/README.md) - Technical API reference

## Next Steps

1. **Choose Deployment Type**: Select development, staging, or production deployment
2. **Configure Environment**: Set up your `.env` file with appropriate values
3. **Start Services**: Use Docker Compose to start your chosen service profile
4. **Monitor Health**: Set up monitoring and alerting for production deployments
5. **Scale as Needed**: Add additional service instances based on load requirements

---

Docker deployment provides a consistent, scalable environment for the Agent Investment Platform across all stages of development and production use.
