# Docker Container Health Monitoring

This guide covers the comprehensive Docker container health monitoring system that ensures all platform services remain operational and healthy.

## Overview

The Agent Investment Platform relies on multiple Docker containers for core functionality. After identifying a critical gap where the logging and monitoring systems failed to detect container failures, a comprehensive monitoring solution has been implemented.

## Critical Requirement

**All Docker containers must be monitored continuously** to prevent undetected service failures that could impact platform functionality.

## Monitoring Components

### 1. Docker Health Monitor Script

**Location**: `scripts/monitor-docker-health.py`

**Purpose**: Comprehensive monitoring of all platform Docker containers with health checks, resource monitoring, and automated alerting.

**Features**:
- Container status monitoring (running, stopped, missing)
- Health endpoint validation for services
- Port conflict detection
- Resource usage monitoring (CPU, memory)
- Automated alert generation
- JSON report generation
- Continuous monitoring mode

### 2. Monitored Container Categories

#### Core Platform Services
- `agent-investment-platform` - Main application (port 8000)

#### Data Layer
- `postgres-investment` - Database (port 5432)
- `redis-investment` - Cache (port 6379)
- `elasticsearch` - Search/logging (ports 9200, 9300)

#### MCP Servers
- `mcp-financial-server` - Financial data (port 3000)
- `mcp-report-server` - Report generation (port 3002)
- `mcp-stock-data-server` - Stock data (port 3003)
- `mcp-analysis-server` - Analysis engine (port 3004)

#### Monitoring Stack
- `logstash` - Log processing (ports 5000, 5044)
- `kibana` - Log visualization (port 5601)
- `grafana` - Metrics dashboard (port 3001)

#### AI Services
- `ollama-investment` - Local LLM server (port 11434)
- `ollama-webui` - Web interface (port 8080)

## Usage

### Single Health Check

```powershell
# Run one-time health check
python scripts/monitor-docker-health.py

# Save health report to JSON file
python scripts/monitor-docker-health.py --save-report
```

### Continuous Monitoring

```powershell
# Monitor every 60 seconds (default)
python scripts/monitor-docker-health.py --continuous

# Monitor every 30 seconds
python scripts/monitor-docker-health.py --continuous --interval 30

# Continuous monitoring with report saving
python scripts/monitor-docker-health.py --continuous --save-report
```

### VS Code Tasks

Use the integrated VS Code tasks for easy monitoring:

- **🩺 Monitor Docker Health** - Single health check
- **🩺 Continuous Docker Monitoring** - Background monitoring every 30 seconds

Access via `Ctrl+Shift+P` → "Tasks: Run Task"

## Health Check Types

### 1. Container Status
- **Running**: Container is active and operational
- **Stopped**: Container has exited or failed
- **Missing**: Required container does not exist

### 2. Health Endpoints
Services with HTTP health endpoints are validated:
```
GET http://localhost:{port}/health
```

Expected response: `200 OK` with healthy status

### 3. Port Accessibility
Network connectivity is tested for all configured service ports.

### 4. Resource Usage
CPU and memory usage is monitored with alerting for high usage (>80%).

## Alert Types

### Container Alerts
- **container_missing** - Required container not found
- **container_unhealthy** - Container failed health checks
- **container_stopped** - Running container has stopped

### Resource Alerts
- **high_cpu** - CPU usage >80%
- **high_memory** - Memory usage >80%

### Network Alerts
- **port_conflict** - Multiple containers claiming same port
- **port_unreachable** - Service port not accessible

## Health Report Format

```json
{
  "timestamp": "2025-09-25T21:50:10.796050",
  "total_containers": 13,
  "healthy_containers": 12,
  "unhealthy_containers": 1,
  "missing_containers": 0,
  "container_health": {
    "container-name": {
      "container": "container-name",
      "status": "healthy|unhealthy|missing",
      "healthy": true|false,
      "issues": ["list of issues"],
      "timestamp": "ISO timestamp"
    }
  },
  "port_conflicts": [],
  "resource_usage": {},
  "alerts": []
}
```

## Integration Requirements

### 1. Health Endpoints
All services **must** implement health endpoints:

```yaml
# docker-compose.yml health check example
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### 2. Prometheus Metrics (Future)
Services should expose metrics for advanced monitoring:
- Container resource usage
- Service-specific metrics
- Request counts and latency

### 3. Alerting Integration (Future)
Alerts can be integrated with:
- Email notifications
- Slack/Discord webhooks
- PagerDuty for critical alerts
- Grafana alert rules

## Monitoring Schedule

### Recommended Intervals
- **Production**: Every 30 seconds
- **Development**: Every 60 seconds
- **Testing**: On-demand

### Critical Response Times
- **Detection**: < 1 minute
- **Alert Generation**: < 30 seconds
- **Recovery Attempt**: < 2 minutes
- **Escalation**: < 5 minutes

## Troubleshooting

### Common Issues

#### 1. Health Endpoint Failures
```
[FAIL] container-name: unhealthy - Health endpoint /health failed
```

**Solutions**:
- Check if service is fully started
- Verify health endpoint implementation
- Check service logs for startup errors

#### 2. Port Conflicts
```
[WARN] Port conflict on 3000: container1, container2
```

**Solutions**:
- Review docker-compose.yml port mappings
- Ensure no duplicate port assignments
- Check for services running outside Docker

#### 3. Resource Exhaustion
```
[WARN] Container 'name' CPU usage is 95%
```

**Solutions**:
- Check service logs for performance issues
- Review resource limits in docker-compose.yml
- Consider scaling or optimization

### Script Debugging

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check Docker daemon connection:
```powershell
docker version
docker ps
```

## Never Again Promise

This monitoring system was implemented after a critical oversight where:
- Multiple containers failed silently
- Port conflicts went undetected
- Service degradation was not noticed
- Manual inspection was required to discover issues

**The monitoring system ensures this never happens again** by providing:
- ✅ Automated container health detection
- ✅ Real-time alerting for failures
- ✅ Comprehensive status reporting
- ✅ Proactive issue identification
- ✅ Historical health tracking

## Related Documentation

- [Docker Services Overview](docker-services.md)
- [Health Check Implementation](health-checks.md)
- [Monitoring and Alerting](monitoring-setup.md)
- [Troubleshooting Docker Issues](../troubleshooting/docker-issues.md)
