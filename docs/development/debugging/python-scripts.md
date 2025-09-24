# Debugging Python Scripts

This guide provides debugging instructions for all Python scripts and components in the Agent Investment Platform.

## Overview

The platform consists of several Python components that may require debugging:

- **Financial Data Scripts** - Real-time data fetching and processing
- **MCP Servers** - Model Context Protocol servers for data integration
- **Analysis Engine** - Investment analysis and recommendation engine
- **Report Generator** - Automated report creation and publishing
- **Setup Scripts** - Installation and configuration automation

## General Debugging Approach

### 1. Enable Debug Logging

Most scripts support debug logging via environment variables or command-line flags:

```bash
# Enable debug logging
export DEBUG=1
export LOG_LEVEL=DEBUG

# Or use command-line flags
python script.py --debug --verbose
```

### 2. Check System Health

Always start debugging by checking overall system health:

```bash
# Run health check script
python scripts/health-check.py

# Validate system setup
python scripts/setup/validate-setup.py --quick
```

### 3. Review Log Files

Check log files for error details:

```bash
# Main platform logs
cat logs/platform.log

# MCP server logs
cat logs/mcp-servers.log

# Initialization logs
cat logs/initialization.log
```

## Component-Specific Debugging

### Financial Data Tools (`src/ollama_integration/`)

**Common Issues:**
- Network connectivity problems
- API rate limiting
- Data parsing errors
- Encoding issues

**Debug Commands:**
```bash
# Test individual financial functions
python -c "from src.ollama_integration.financial_functions import get_stock_quote; print(get_stock_quote('AAPL'))"

# Test command-line tool with debug output
python src/ollama_integration/financial_data_tool.py quote AAPL --debug

# Test TradingView API connectivity
python -c "from src.ollama_integration.financial_functions import TradingViewAPI; api = TradingViewAPI(); print(api.get_stock_data('AAPL'))"
```

**Troubleshooting Steps:**
1. Check internet connectivity: `ping tradingview.com`
2. Verify required packages: `pip list | grep -E "(requests|feedparser|yfinance)"`
3. Test with different symbols: Try 'MSFT', 'GOOGL' instead of 'AAPL'
4. Check for rate limiting: Wait 30 seconds between requests

### MCP Servers (`src/mcp_servers/`)

**Common Issues:**
- Server startup failures
- Port conflicts
- Missing dependencies
- Configuration errors

**Debug Commands:**
```bash
# Test MCP server directly
python -m src.mcp_servers.financial_data_server

# Check server health
python -c "import requests; print(requests.get('http://localhost:3000/health').json())"

# Test server with Docker logs
docker-compose logs mcp-financial-server --tail=50

# Debug server initialization
python -c "from src.mcp_servers.financial_data_server import FinancialDataServer; server = FinancialDataServer(); print('Server initialized')"
```

**Troubleshooting Steps:**
1. Check port availability: `netstat -an | grep :3000`
2. Verify Docker is running: `docker ps`
3. Check server dependencies: `python -c "import asyncio, json, logging"`
4. Test server startup manually: `python -m src.mcp_servers.financial_data_server`

### Analysis Engine (`src/analysis/`)

**Common Issues:**
- Missing market data
- Calculation errors
- Memory limitations
- Database connectivity

**Debug Commands:**
```bash
# Test individual analysis components
python -c "from src.analysis.chart_analyzer import ChartAnalyzer; analyzer = ChartAnalyzer(); print('Analyzer ready')"

# Run analysis with debug output
python scripts/run-analysis.py --symbol AAPL --debug

# Test database connectivity
python -c "import sqlite3; conn = sqlite3.connect('data/analysis.db'); print('Database connected')"
```

**Troubleshooting Steps:**
1. Check data availability: Ensure market data is downloaded
2. Verify calculations: Test with known values
3. Check memory usage: `ps aux | grep python`
4. Validate database schema: Check table structure

### Setup Scripts (`scripts/`)

**Common Issues:**
- Permission errors
- Missing system dependencies
- Network timeouts
- Configuration file errors

**Debug Commands:**
```bash
# Run setup with verbose output
python scripts/initialize.py --debug --verbose

# Test individual setup components
python scripts/setup/install-dependencies.py --dry-run

# Validate configuration
python scripts/setup/validate-setup.py --comprehensive
```

**Troubleshooting Steps:**
1. Check permissions: Run with appropriate user rights
2. Verify network access: Test external URL access
3. Check system requirements: Validate OS and Python version
4. Review configuration files: Check YAML/JSON syntax

## Advanced Debugging Techniques

### Using Python Debugger (pdb)

Add breakpoints to investigate issues:

```python
import pdb; pdb.set_trace()
```

### Memory Profiling

Monitor memory usage during execution:

```bash
# Install memory profiler
pip install memory-profiler

# Profile memory usage
python -m memory_profiler script.py
```

### Performance Profiling

Identify performance bottlenecks:

```bash
# Install profiling tools
pip install line-profiler

# Profile line-by-line performance
kernprof -l -v script.py
```

### Network Debugging

Monitor network requests and responses:

```bash
# Enable HTTP request logging
export PYTHONHTTPDEBUG=1

# Monitor network traffic
tcpdump -i any -s 0 -w network.pcap host tradingview.com
```

## Common Error Patterns

### Import Errors
```
ModuleNotFoundError: No module named 'src.module'
```
**Solution**: Check PYTHONPATH and ensure proper project structure

### Encoding Errors
```
UnicodeDecodeError: 'charmap' codec can't decode byte
```
**Solution**: Use ASCII characters only, avoid Unicode symbols

### Network Timeouts
```
requests.exceptions.Timeout: HTTPSConnectionPool
```
**Solution**: Increase timeout values, check internet connectivity

### Docker Issues
```
docker: Cannot connect to the Docker daemon
```
**Solution**: Ensure Docker Desktop is running, check service status

## Getting Additional Help

1. **Check Platform Health**: Run health check scripts first
2. **Review Documentation**: Check relevant API documentation
3. **Search Issues**: Look for similar problems in GitHub issues
4. **Create Issue**: Provide debug output and system information
5. **Enable Logging**: Always include log files with issue reports

## Related Documentation

- [Development Setup](development-setup.md) - Setting up development environment
- [Contributing Guidelines](contributing.md) - Code contribution standards
- [Troubleshooting Guide](../troubleshooting/common-issues.md) - Common platform issues
- [API Documentation](../api/) - MCP server and API references
