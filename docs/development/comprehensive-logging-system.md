# Comprehensive Logging System Documentation

## Overview

The Agent Investment Platform now includes a comprehensive, platform-wide logging system designed to provide complete visibility into system operations, facilitate debugging, and enable real-time monitoring.

## Table of Contents

- [System Architecture](#system-architecture)
- [Quick Start Guide](#quick-start-guide)
- [Components Overview](#components-overview)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [Dashboard Access](#dashboard-access)
- [Health Monitoring](#health-monitoring)
- [MCP Server Integration](#mcp-server-integration)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## System Architecture

The logging system consists of several integrated components:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Application   │───▷│  Core Logging    │───▷│  Log Handlers   │
│   Components    │    │     Module       │    │ (File/Console)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  WebSocket      │◀───│  Log Aggregator  │───▷│ Elasticsearch   │
│   Streaming     │    │   (Real-time)    │    │    Storage      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Log Dashboard  │    │   MCP Server     │    │     Kibana      │
│  (Web Interface)│    │ (Query/Manage)   │    │  (Analytics)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │    Grafana       │
                       │  (Health/Metrics)│
                       └──────────────────┘
```

## Quick Start Guide

### 1. Start the Logging System

Enable the logging profile in Docker Compose:

```bash
# Start with logging and monitoring
docker-compose --profile logging --profile monitoring up -d

# Or start all services
docker-compose --profile logging --profile monitoring --profile local-llm up -d
```

### 2. Access the Dashboards

- **Log Dashboard**: http://localhost:8764
- **Kibana**: http://localhost:5601
- **Grafana**: http://localhost:3000 (admin/admin123)
- **Health Check**: http://localhost:3005/health

### 3. Initialize Logging in Your Code

```python
from src.logging import initialize_platform_logging, get_platform_logger

# Initialize the logging system
await initialize_platform_logging(log_level="INFO")

# Get a logger for your component
logger = get_platform_logger(__name__, "my_component")

# Use the logger
logger.info("Application started")
logger.error("Something went wrong", exc_info=True)
```

## Components Overview

### Core Logging Module (`src/logging/core.py`)

Provides the foundational logging infrastructure:

- **Structured JSON Logging**: All logs are stored in structured JSON format
- **Multiple Handlers**: Console, file, rotating file, and real-time streaming
- **Context Enrichment**: Automatic addition of trace IDs, component info, and metadata
- **Performance Monitoring**: Built-in function timing and performance tracking

### Log Aggregation System (`src/logging/aggregation.py`)

Handles centralized log collection:

- **Elasticsearch Integration**: Stores logs in Elasticsearch for fast searching
- **Bulk Processing**: Efficient batch processing of log entries
- **Index Management**: Automatic daily index rotation
- **Query Interface**: Advanced filtering and search capabilities

### Real-time API (`src/logging/websocket_server.py`)

Provides real-time log streaming:

- **WebSocket Server**: Real-time log streaming to connected clients
- **REST API**: HTTP endpoints for log querying and statistics
- **Filtering**: Advanced filtering by level, component, time range, and content
- **CORS Support**: Cross-origin requests for web dashboards

### Web Dashboard (`src/logging/dashboard/`)

Interactive web interface for log monitoring:

- **Real-time Updates**: Live log streaming with WebSocket connection
- **Advanced Filtering**: Filter by level, component, time range, and search terms
- **Statistics**: Visual charts and metrics about log patterns
- **Export**: Download logs in CSV format for analysis

### Health Monitoring (`src/logging/health_monitoring.py`)

Comprehensive system health monitoring:

- **Component Health Checks**: Monitor all platform components
- **System Metrics**: CPU, memory, disk, and network monitoring
- **Alert Detection**: Automatic detection of critical issues
- **Historical Data**: Track health metrics over time

### MCP Server (`src/mcp_servers/log_management_server.py`)

MCP server for programmatic log access:

- **Query Tools**: Advanced log querying through MCP interface
- **Statistics**: Get log statistics and patterns
- **Health Status**: System health information
- **Search**: Full-text search capabilities

## Configuration

### Main Configuration File

The logging system is configured via `config/logging-config.yaml`:

```yaml
# Global logging level
LOG_LEVEL: INFO

# Enable structured JSON logging
STRUCTURED_LOGGING: true

# Component-specific log levels
component_levels:
  orchestrator: INFO
  mcp_servers: DEBUG
  analysis_engine: INFO

# Handler configuration
handlers:
  console:
    enabled: true
    level: INFO
    format: colored

  file:
    enabled: true
    level: DEBUG
    format: json
    rotation:
      max_size_mb: 50
      backup_count: 10

  elasticsearch:
    enabled: true
    hosts:
      - "elasticsearch:9200"
    index_pattern: "investment-platform-logs-%Y.%m.%d"

# Real-time streaming
realtime:
  websocket_enabled: true
  websocket_port: 8765
  buffer_size: 1000

# Performance monitoring
performance:
  function_timing: true
  slow_operation_threshold_ms: 1000
```

### Environment Variables

Override configuration with environment variables:

```bash
# Logging levels
export LOG_LEVEL=DEBUG
export LOG_LEVEL_ORCHESTRATOR=INFO
export LOG_LEVEL_MCP_SERVERS=DEBUG

# Handlers
export CONSOLE_LOG_ENABLED=true
export FILE_LOG_ENABLED=true
export ELASTICSEARCH_ENABLED=true

# Real-time features
export WEBSOCKET_LOGGING=true
export WEBSOCKET_PORT=8765

# Performance
export PERFORMANCE_LOGGING=true
export SLOW_OPERATION_THRESHOLD=500
```

## Usage Examples

### Basic Logging

```python
from src.logging import get_platform_logger

logger = get_platform_logger(__name__, "my_component")

# Basic logging
logger.debug("Debug information")
logger.info("Information message")
logger.warning("Warning message")
logger.error("Error occurred", exc_info=True)

# Structured logging with extra data
logger.info("User action completed", extra={
    'user_id': '12345',
    'action': 'portfolio_update',
    'duration_ms': 150
})
```

### Context-Aware Logging

```python
from src.logging import create_log_context, get_platform_logger

logger = get_platform_logger(__name__, "trading")

# Create logging context
with create_log_context(
    user_id="user123",
    session_id="sess456",
    request_id="req789"
) as ctx:
    ctx.log(logger, "info", "Processing trade order")

    # Your business logic here
    process_trade_order()

    ctx.log(logger, "info", "Trade order completed")
```

### Performance Monitoring

```python
from src.logging import performance_monitor, get_platform_logger

logger = get_platform_logger(__name__, "analysis")

@performance_monitor
def analyze_portfolio():
    """Analyze portfolio performance."""
    # This function's execution time will be automatically logged
    return perform_analysis()

# Manual performance tracking
import time
start_time = time.time()
result = expensive_operation()
duration = (time.time() - start_time) * 1000

logger.info("Operation completed", extra={
    'operation': 'expensive_operation',
    'duration_ms': duration,
    'result_count': len(result)
})
```

### Querying Logs via MCP

```python
# Using the MCP server to query logs
mcp_client = MCPClient("http://localhost:3005")

# Query recent errors
result = await mcp_client.call_tool("get_recent_errors", {
    "hours": 24,
    "limit": 100
})

# Search for specific patterns
result = await mcp_client.call_tool("search_logs", {
    "search_term": "portfolio update",
    "hours": 6,
    "level": "INFO"
})

# Get system health
health = await mcp_client.call_tool("get_system_health", {
    "hours": 1
})
```

## Dashboard Access

### Log Dashboard Features

The web dashboard (http://localhost:8764) provides:

1. **Real-time Log Streaming**
   - Live updates via WebSocket
   - Configurable refresh rates
   - Automatic scrolling

2. **Advanced Filtering**
   - Log level filtering (DEBUG, INFO, WARNING, ERROR, CRITICAL)
   - Component-based filtering
   - Time range selection (5m, 15m, 1h, 6h, 24h, custom)
   - Text search in messages

3. **Statistics and Analytics**
   - Log count by level
   - Top active components
   - Timeline charts
   - Error rate analysis

4. **Export and Management**
   - CSV export functionality
   - Log entry details view
   - Pagination support
   - Search highlighting

### Kibana Integration

Access Kibana at http://localhost:5601 for advanced analytics:

1. **Index Patterns**
   - `investment-platform-logs-*` - All application logs
   - `investment-platform-errors-*` - Error logs only
   - `investment-platform-performance-*` - Performance metrics

2. **Pre-built Visualizations**
   - Log level distribution
   - Component activity
   - Error trends
   - Performance metrics

3. **Dashboards**
   - System Overview
   - Error Analysis
   - Performance Monitoring
   - Component Health

## Health Monitoring

### Health Check Endpoints

- **Overall Health**: `GET /health`
- **Component Health**: Individual component status
- **System Metrics**: CPU, memory, disk usage

### Monitored Components

The health monitoring system checks:

- **Elasticsearch**: Cluster health and connectivity
- **Logstash**: Service availability
- **Kibana**: API status
- **Log Aggregator**: Service status and performance
- **WebSocket Server**: Connection availability
- **MCP Servers**: All registered MCP servers
- **Orchestrator**: Main application health
- **PostgreSQL**: Database connectivity
- **Redis**: Cache service status

### Health Status Levels

- **Healthy**: All systems operating normally
- **Warning**: Minor issues that don't affect core functionality
- **Critical**: Major issues requiring immediate attention
- **Unknown**: Cannot determine status

### Grafana Health Dashboards

Access Grafana at http://localhost:3000 for health monitoring:

1. **System Overview Dashboard**
   - Overall platform health status
   - Component status grid
   - Recent alerts and incidents

2. **Performance Dashboard**
   - System resource utilization
   - Response time metrics
   - Throughput statistics

3. **Error Analysis Dashboard**
   - Error rate trends
   - Top error sources
   - Error pattern analysis

## MCP Server Integration

### Available Tools

The MCP log management server provides these tools:

1. **query_logs**: Advanced log querying with filters
2. **get_log_statistics**: Statistical analysis of logs
3. **get_recent_errors**: Recent error and critical logs
4. **analyze_log_patterns**: Pattern analysis and trends
5. **search_logs**: Full-text search in log messages
6. **get_system_health**: Current system health status
7. **get_log_config**: Current logging configuration

### Example Usage

```python
# Query logs with advanced filtering
result = await mcp_client.call_tool("query_logs", {
    "start_time": "2025-09-25T00:00:00Z",
    "end_time": "2025-09-25T23:59:59Z",
    "level": "ERROR",
    "component": "orchestrator",
    "limit": 100
})

# Analyze patterns
patterns = await mcp_client.call_tool("analyze_log_patterns", {
    "hours": 24
})

# Get health status
health = await mcp_client.call_tool("get_system_health", {
    "hours": 1
})
```

## Troubleshooting

### Common Issues

#### 1. Logs Not Appearing in Dashboard

**Symptoms**: Dashboard shows no logs despite application activity

**Solutions**:
- Check Elasticsearch connectivity: `curl http://localhost:9200/_cluster/health`
- Verify log aggregator is running: Check Docker container status
- Confirm WebSocket connection: Check browser console for connection errors
- Check log levels: Ensure components are logging at appropriate levels

#### 2. High Memory Usage

**Symptoms**: Elasticsearch or logging components consuming excessive memory

**Solutions**:
- Adjust Elasticsearch heap size in `docker-compose.yml`
- Reduce log retention period in configuration
- Increase log rotation frequency
- Check for log loops or excessive debug logging

#### 3. Missing Health Check Data

**Symptoms**: Health monitoring shows components as "unknown"

**Solutions**:
- Verify network connectivity between containers
- Check Docker network configuration
- Ensure health endpoints are accessible
- Review container logs for connection errors

#### 4. Dashboard Performance Issues

**Symptoms**: Slow dashboard loading or unresponsive interface

**Solutions**:
- Reduce query time ranges
- Limit the number of logs displayed
- Check browser network tab for slow requests
- Verify adequate system resources

### Debug Mode

Enable debug logging for troubleshooting:

```bash
# Set debug level for all components
export LOG_LEVEL=DEBUG

# Enable debug for specific components
export LOG_LEVEL_LOGGING_SYSTEM=DEBUG
export LOG_LEVEL_HEALTH_MONITOR=DEBUG

# Enable performance monitoring
export PERFORMANCE_LOGGING=true
```

### Log File Locations

- **Application logs**: `logs/*.log`
- **Docker container logs**: `docker logs <container_name>`
- **Elasticsearch logs**: In Elasticsearch container
- **Logstash logs**: In Logstash container

## Best Practices

### 1. Log Level Guidelines

- **DEBUG**: Detailed diagnostic information for development
- **INFO**: General operational messages and business logic flow
- **WARNING**: Potentially harmful situations that don't stop execution
- **ERROR**: Error events that might still allow continued execution
- **CRITICAL**: Very severe errors that may cause application termination

### 2. Structured Logging

Always use structured logging with meaningful context:

```python
# Good - structured with context
logger.info("Trade executed successfully", extra={
    'trade_id': trade.id,
    'symbol': trade.symbol,
    'quantity': trade.quantity,
    'price': trade.price,
    'execution_time_ms': execution_time
})

# Avoid - unstructured string formatting
logger.info(f"Trade {trade.id} for {trade.quantity} {trade.symbol} at {trade.price}")
```

### 3. Performance Considerations

- Use appropriate log levels in production (INFO or WARNING)
- Implement log sampling for high-frequency events
- Use async logging for performance-critical paths
- Monitor log volume and adjust retention policies

### 4. Security Best Practices

- Never log sensitive information (passwords, API keys, PII)
- Use log masking for potentially sensitive data
- Implement proper access controls for log data
- Regular security audits of logged information

### 5. Monitoring and Alerting

- Set up alerts for critical error patterns
- Monitor log volume trends
- Track system performance metrics
- Regular health check reviews

### 6. Documentation and Training

- Document component-specific logging patterns
- Train team members on dashboard usage
- Maintain troubleshooting runbooks
- Regular review of logging effectiveness

## Conclusion

This comprehensive logging system provides complete visibility into the Agent Investment Platform operations. It enables:

- **Real-time monitoring** of all system components
- **Advanced debugging** capabilities with structured logs
- **Performance tracking** and optimization insights
- **Health monitoring** with automated alerting
- **Historical analysis** for trend identification
- **Integrated tooling** through MCP server interface

The system is designed to scale with your needs while providing the observability required for a production investment platform.

For additional support or feature requests, please refer to the project documentation or contact the development team.
