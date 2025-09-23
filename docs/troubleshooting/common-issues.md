# Common Issues and Troubleshooting

Comprehensive troubleshooting guide for the Agent Investment Platform covering setup, runtime, and operational issues.

## Table of Contents

- [Quick Diagnostics](#quick-diagnostics)
- [Installation Issues](#installation-issues)
- [Configuration Problems](#configuration-problems)
- [Runtime Errors](#runtime-errors)
- [API and Data Source Issues](#api-and-data-source-issues)
- [LLM Integration Problems](#llm-integration-problems)
- [MCP Server Issues](#mcp-server-issues)
- [Docker Deployment Issues](#docker-deployment-issues)
- [Performance Problems](#performance-problems)
- [Database and Storage Issues](#database-and-storage-issues)
- [Network and Connectivity Issues](#network-and-connectivity-issues)
- [Getting Help](#getting-help)

## Quick Diagnostics

### System Health Check

Run the comprehensive health check to identify issues:

```powershell
# Quick system validation
python scripts/setup/validate-setup.py --quick

# Detailed system validation
python scripts/setup/validate-setup.py --verbose

# Component-specific checks
python scripts/setup/validate-setup.py --component mcp-servers
python scripts/setup/validate-setup.py --component llm-integration
python scripts/setup/validate-setup.py --component database
```

### Log Analysis

Check logs for error patterns:

```powershell
# View recent logs
Get-Content logs\\platform.log -Tail 50

# Search for errors
Select-String -Path \"logs\\*.log\" -Pattern \"ERROR|CRITICAL|EXCEPTION\"

# MCP server logs
Get-Content logs\\mcp-servers.log -Tail 50
```

### Environment Verification

```powershell
# Check Python environment
python --version
python -c \"import sys; print('Python path:', sys.executable)\"

# Check required modules
python -c \"
import yaml, requests, mcp, pandas, numpy
print('Core modules imported successfully')
\"

# Check environment variables
python -c \"
import os
required = ['POLYGON_API_KEY', 'NEWS_API_KEY']
for var in required:
    value = os.getenv(var, 'NOT SET')
    print(f'{var}: {'SET' if value != 'NOT SET' else 'NOT SET'}')
\"
```

## Installation Issues

### Python Version Compatibility

**Problem**: Incompatible Python version or encoding errors

**Symptoms**:
- `SyntaxError` in Python code
- `UnicodeDecodeError` or `charmap` codec errors
- Module import failures

**Solutions**:
```powershell
# Check Python version (requires 3.9+)
python --version

# If using wrong version, install Python 3.11
winget install Python.Python.3.11

# For encoding issues, set environment variables
$env:PYTHONIOENCODING = \"utf-8\"
[System.Environment]::SetEnvironmentVariable(\"PYTHONIOENCODING\", \"utf-8\", \"User\")
```

### Dependency Installation Failures

**Problem**: Package installation errors or conflicts

**Symptoms**:
- `pip install` command failures
- ModuleNotFoundError for installed packages
- Version conflict errors

**Solutions**:
```powershell
# Upgrade pip to latest version
python -m pip install --upgrade pip>=25.2

# Clear pip cache
pip cache purge

# Install with verbose output to identify issues
pip install -r requirements.txt -v

# Use virtual environment to avoid conflicts
python -m venv venv
.\\venv\\Scripts\\activate  # Windows
pip install -r requirements.txt

# For specific package issues
pip install --no-cache-dir --force-reinstall package_name
```

### Permission and Path Issues

**Problem**: Access denied or file not found errors

**Symptoms**:
- `PermissionError` when running scripts
- `FileNotFoundError` for existing files
- Scripts not recognized as commands

**Solutions**:
```powershell
# Run PowerShell as Administrator for system-wide changes
# Right-click PowerShell → \"Run as administrator\"

# Set execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Add Python to PATH (if not already)
$env:PATH += \";C:\\Python311;C:\\Python311\\Scripts\"

# Verify PATH
python --version
pip --version
```

## Configuration Problems

### Environment Variables Not Loading

**Problem**: API keys or configuration not recognized

**Symptoms**:
- \"API key not found\" errors
- Default configuration values being used
- Authentication failures

**Solutions**:
```powershell
# Check if .env file exists and is readable
Test-Path .env
Get-Content .env | Select-Object -First 5

# Load environment variables manually
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], \"Process\")
    }
}

# Verify variables are loaded
$env:POLYGON_API_KEY
[System.Environment]::GetEnvironmentVariable(\"POLYGON_API_KEY\")

# Alternative: Use PowerShell profile
echo '$env:POLYGON_API_KEY=\"your_key_here\"' >> $PROFILE
```

### Configuration File Syntax Errors

**Problem**: YAML or JSON configuration files have syntax errors

**Symptoms**:
- `yaml.scanner.ScannerError`
- `json.decoder.JSONDecodeError`
- Configuration not loading

**Solutions**:
```powershell
# Validate YAML files
python -c \"
import yaml
import glob
for file in glob.glob('config/*.yaml'):
    try:
        with open(file) as f:
            yaml.safe_load(f)
        print(f'{file}: OK')
    except Exception as e:
        print(f'{file}: ERROR - {e}')
\"

# Validate JSON files
python -c \"
import json
import glob
for file in glob.glob('config/*.json'):
    try:
        with open(file) as f:
            json.load(f)
        print(f'{file}: OK')
    except Exception as e:
        print(f'{file}: ERROR - {e}')
\"

# Common YAML issues to check:
# - Consistent indentation (spaces, not tabs)
# - Proper quoting of string values
# - Correct list and dictionary syntax
```

### Model Configuration Issues

**Problem**: LLM models not loading or incorrect model paths

**Symptoms**:
- Model not found errors
- Slow model loading
- Out of memory errors

**Solutions**:
```powershell
# Check model directory structure
Get-ChildItem -Recurse models\\ | Select-Object Name, Length

# Verify Hugging Face cache
$env:HF_HOME = \"models\\.huggingface_cache\"
Get-ChildItem $env:HF_HOME

# Re-download models if corrupted
python scripts/setup/download-models.py --models \"microsoft/Phi-3-mini-4k-instruct\"

# For Ollama models
ollama list
ollama pull llama3.1:8b
```

## Runtime Errors

### Memory and Resource Issues

**Problem**: Out of memory or high CPU usage

**Symptoms**:
- `MemoryError` exceptions
- System becoming unresponsive
- Slow performance

**Solutions**:
```powershell
# Check system resources
Get-ComputerInfo | Select-Object TotalPhysicalMemory, AvailablePhysicalMemory
Get-Process python | Select-Object ProcessName, CPU, WorkingSet

# Use smaller models for limited memory
# Edit config/llm-config.yaml:
# default:
#   model: \"microsoft/Phi-3-mini-4k-instruct\"  # Smaller model

# Reduce batch sizes in config
# analysis:
#   batch_size: 10  # Reduce from default

# Close unnecessary applications
Get-Process | Where-Object {$_.WorkingSet -gt 100MB} | Select-Object Name, WorkingSet
```

### Import and Module Errors

**Problem**: Python modules not found or import errors

**Symptoms**:
- `ModuleNotFoundError`
- `ImportError`
- Circular import errors

**Solutions**:
```powershell
# Check if modules are installed
pip list | Select-String \"pandas|numpy|requests|yaml\"

# Install missing modules
pip install module_name

# For development imports, ensure PYTHONPATH is set
$env:PYTHONPATH = \".;src\"

# Check if __init__.py files exist in packages
Get-ChildItem -Recurse -Name \"__init__.py\"

# Reinstall if modules are corrupted
pip uninstall package_name
pip install package_name
```

### Database Connection Errors

**Problem**: Cannot connect to database or data persistence issues

**Symptoms**:
- `OperationalError` database errors
- Data not saving
- Connection timeout errors

**Solutions**:
```powershell
# Check if database file exists (SQLite)
Test-Path data\\investment_platform.db

# Test database connection
python -c \"
import sqlite3
conn = sqlite3.connect('data/investment_platform.db')
print('Database connection successful')
conn.close()
\"

# For PostgreSQL in Docker
docker compose exec postgres pg_isready -U postgres

# Reset database if corrupted
Remove-Item data\\investment_platform.db -ErrorAction SilentlyContinue
python scripts/setup/configure-environment.py --reset-database
```

## API and Data Source Issues

### API Key Authentication Failures

**Problem**: API authentication errors or rate limiting

**Symptoms**:
- \"401 Unauthorized\" errors
- \"403 Forbidden\" responses
- \"Rate limit exceeded\" messages

**Solutions**:
```powershell
# Test API keys
python -c \"
import requests
import os

# Test Polygon API
api_key = os.getenv('POLYGON_API_KEY')
if api_key:
    response = requests.get(f'https://api.polygon.io/v2/aggs/ticker/AAPL/prev?apikey={api_key}')
    print(f'Polygon API: {response.status_code}')
else:
    print('POLYGON_API_KEY not set')

# Test Alpha Vantage API
api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
if api_key:
    response = requests.get(f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=AAPL&apikey={api_key}')
    print(f'Alpha Vantage API: {response.status_code}')
else:
    print('ALPHA_VANTAGE_API_KEY not set')
\"

# Check API key validity
# - Ensure keys are not expired
# - Verify keys have proper permissions
# - Check account limits and usage

# For rate limiting, adjust request frequency in config/data-sources.yaml
```

### Network Connectivity Issues

**Problem**: Cannot reach external APIs or services

**Symptoms**:
- `ConnectionError` exceptions
- DNS resolution failures
- Timeout errors

**Solutions**:
```powershell
# Test internet connectivity
Test-NetConnection -ComputerName \"api.polygon.io\" -Port 443
Test-NetConnection -ComputerName \"www.alphavantage.co\" -Port 443

# Check DNS resolution
nslookup api.polygon.io
nslookup newsapi.org

# Test with curl
curl -I https://api.polygon.io/
curl -I https://newsapi.org/

# Check firewall settings
# Windows Defender Firewall might block Python
# Add Python to firewall exceptions

# Test with proxy if behind corporate firewall
# Set proxy in environment variables:
# $env:HTTP_PROXY = \"http://proxy.company.com:8080\"
# $env:HTTPS_PROXY = \"http://proxy.company.com:8080\"
```

### Data Quality and Validation Issues

**Problem**: Invalid or corrupted data from APIs

**Symptoms**:
- Unexpected data formats
- Missing required fields
- Data validation errors

**Solutions**:
```powershell
# Enable data validation in config/data-sources.yaml
# data_quality:
#   validation_enabled: true
#   anomaly_detection: true

# Check data cache for corruption
Get-ChildItem data_cache\\ | Select-Object Name, Length, LastWriteTime

# Clear data cache
Remove-Item data_cache\\* -Recurse -Force
python orchestrator.py --refresh-data

# Validate specific data sources
python -c \"
from src.mcp_servers.stock_data_server import test_data_quality
test_data_quality()
\"
```

## LLM Integration Problems

### Local Model Loading Issues

**Problem**: Hugging Face or local models not loading

**Symptoms**:
- Model download failures
- CUDA/GPU not detected
- Slow inference times

**Solutions**:
```powershell
# Check GPU availability
python -c \"
import torch
print(f'CUDA available: {torch.cuda.is_available()}')
print(f'GPU count: {torch.cuda.device_count()}')
if torch.cuda.is_available():
    print(f'GPU name: {torch.cuda.get_device_name(0)}')
\"

# Download models manually
python scripts/setup/download-models.py --models \"microsoft/Phi-3-mini-4k-instruct\"

# Check model cache
Get-ChildItem models\\.huggingface_cache -Recurse | Measure-Object -Property Length -Sum

# For GPU issues, install CUDA-enabled PyTorch
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Test model loading
python -c \"
from transformers import AutoTokenizer, AutoModelForCausalLM
model_name = 'microsoft/Phi-3-mini-4k-instruct'
tokenizer = AutoTokenizer.from_pretrained(model_name)
print('Model loaded successfully')
\"
```

### Ollama Connection Issues

**Problem**: Cannot connect to Ollama server

**Symptoms**:
- Connection refused errors
- Ollama server not responding
- Model not found errors

**Solutions**:
```powershell
# Check if Ollama is running
Get-Process -Name \"ollama\" -ErrorAction SilentlyContinue

# Start Ollama server
ollama serve

# Test connection
curl http://localhost:11434/api/tags

# Check available models
ollama list

# Download required models
ollama pull llama3.1:8b
ollama pull mistral:7b

# Test model inference
ollama run llama3.1:8b \"Hello, world!\"

# For Docker environments
docker compose exec ollama ollama list
docker compose logs ollama
```

### API-based LLM Issues

**Problem**: OpenAI or Anthropic API errors

**Symptoms**:
- Authentication errors
- Rate limit exceeded
- Invalid model names

**Solutions**:
```powershell
# Test OpenAI API
python -c \"
import openai
import os
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
response = client.models.list()
print('OpenAI API connection successful')
print(f'Available models: {[model.id for model in response.data[:3]]}')
\"

# Test Anthropic API
python -c \"
import anthropic
import os
client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
print('Anthropic API connection successful')
\"

# Check API quotas and billing
# Visit OpenAI/Anthropic dashboard to check usage

# Update model names in config/llm-config.yaml if deprecated
```

## MCP Server Issues

### MCP Server Connection Failures

**Problem**: Cannot connect to MCP servers or servers crashing

**Symptoms**:
- \"Connection refused\" errors
- MCP server process termination
- Timeout errors

**Solutions**:
```powershell
# Check MCP server status
python run_mcp_server.py --health-check

# View MCP server logs
Get-Content logs\\mcp-servers.log -Tail 50

# Restart individual servers
python run_mcp_server.py --restart stock-data-server

# Restart all servers
python run_mcp_server.py --restart-all

# Test server connectivity
python -c \"
import requests
try:
    response = requests.get('http://localhost:3001/health')
    print(f'Stock server: {response.status_code}')
except Exception as e:
    print(f'Stock server error: {e}')
\"

# Check for port conflicts
netstat -ano | findstr :3001
netstat -ano | findstr :3002
```

### MCP Server Configuration Issues

**Problem**: Server configuration or environment errors

**Symptoms**:
- Server starts but functions incorrectly
- Missing capabilities
- Configuration validation errors

**Solutions**:
```powershell
# Validate MCP server configuration
python -c \"
import json
with open('config/mcp-servers.json') as f:
    config = json.load(f)
    print('MCP config loaded successfully')
    for server, details in config['servers'].items():
        print(f'Server: {server}, Command: {details.get(\"command\")}')
\"

# Test individual server capabilities
python test_mcp_servers.py --server stock-data-server

# Check environment variables for servers
python -c \"
import os
servers_env = ['POLYGON_API_KEY', 'NEWS_API_KEY', 'REDDIT_CLIENT_ID']
for var in servers_env:
    print(f'{var}: {'SET' if os.getenv(var) else 'NOT SET'}')
\"

# Reset server configuration
Copy-Item config\\mcp-servers.json.example config\\mcp-servers.json
```

## Docker Deployment Issues

### Container Startup Failures

**Problem**: Docker containers not starting or crashing

**Symptoms**:
- Container exit codes (1, 125, 126, 127)
- \"No such file or directory\" errors
- Permission denied errors

**Solutions**:
```powershell
# Check container status
docker compose ps

# View container logs
docker compose logs agent-investment-platform
docker compose logs postgres

# Check for port conflicts
netstat -ano | findstr :8000
netstat -ano | findstr :5432

# Restart containers
docker compose down
docker compose up -d

# Rebuild containers if needed
docker compose build --no-cache
docker compose up -d

# Check Docker resources
docker system df
docker system prune -a  # Clean up unused resources
```

### Volume and Persistence Issues

**Problem**: Data not persisting or volume mount failures

**Symptoms**:
- Data loss after container restart
- File permission errors
- Volume not found errors

**Solutions**:
```powershell
# Check volume status
docker volume ls
docker volume inspect agent-investment-platform_postgres_data

# Fix volume permissions (Linux/Mac)
# docker compose exec agent-investment-platform chown -R appuser:appuser /app/data

# Recreate volumes if corrupted
docker compose down -v
docker volume prune
docker compose up -d

# Backup important data before volume operations
docker compose exec -T postgres pg_dump -U postgres investment_platform > backup.sql
```

### Network Connectivity in Docker

**Problem**: Services cannot communicate within Docker network

**Symptoms**:
- Connection refused between services
- DNS resolution failures
- Network timeout errors

**Solutions**:
```powershell
# Check Docker network
docker network ls
docker network inspect agent-investment-platform_investment-network

# Test connectivity between containers
docker compose exec agent-investment-platform ping postgres
docker compose exec agent-investment-platform nc -zv redis 6379

# Check service discovery
docker compose exec agent-investment-platform nslookup postgres

# Restart network if needed
docker compose down
docker network prune
docker compose up -d
```

## Performance Problems

### Slow Application Response

**Problem**: Slow API responses or UI interactions

**Symptoms**:
- Long page load times
- API timeouts
- High CPU or memory usage

**Solutions**:
```powershell
# Monitor resource usage
# Task Manager → Performance tab
# Or use PowerShell:
Get-Counter \"\\Processor(_Total)\\% Processor Time\" -MaxSamples 5
Get-Counter \"\\Memory\\Available MBytes\" -MaxSamples 5

# Check application performance
python -c \"
import psutil
import os
process = psutil.Process(os.getpid())
print(f'Memory usage: {process.memory_info().rss / 1024 / 1024:.1f} MB')
print(f'CPU percent: {process.cpu_percent()}%')
\"

# Enable performance monitoring
# Edit config/llm-config.yaml:
# logging:
#   log_performance: true
#   metrics_enabled: true

# Optimize configuration
# - Reduce batch sizes
# - Use smaller models
# - Enable caching
# - Increase timeout values
```

### Database Performance Issues

**Problem**: Slow database queries or high disk usage

**Symptoms**:
- Long query execution times
- Database locks
- Disk space warnings

**Solutions**:
```powershell
# Check database file size
Get-ChildItem data\\*.db | Select-Object Name, Length

# Analyze database performance
python -c \"
import sqlite3
conn = sqlite3.connect('data/investment_platform.db')
cursor = conn.cursor()
cursor.execute('ANALYZE')
conn.commit()
print('Database analysis complete')
conn.close()
\"

# Clean up old data
python -c \"
import sqlite3
from datetime import datetime, timedelta
conn = sqlite3.connect('data/investment_platform.db')
cursor = conn.cursor()
cutoff_date = datetime.now() - timedelta(days=90)
cursor.execute('DELETE FROM cache_data WHERE created_at < ?', (cutoff_date,))
print(f'Deleted {cursor.rowcount} old cache entries')
conn.commit()
conn.close()
\"

# Enable database optimization in config
# database:
#   enable_query_cache: true
#   optimize_on_startup: true
```

## Database and Storage Issues

### SQLite Database Corruption

**Problem**: Database file corruption or locking issues

**Symptoms**:
- \"Database is locked\" errors
- \"File is not a database\" errors
- Data inconsistencies

**Solutions**:
```powershell
# Check database integrity
python -c \"
import sqlite3
conn = sqlite3.connect('data/investment_platform.db')
cursor = conn.cursor()
cursor.execute('PRAGMA integrity_check')
result = cursor.fetchone()
print(f'Database integrity: {result[0]}')
conn.close()
\"

# Backup and restore database
Copy-Item data\\investment_platform.db data\\investment_platform.db.backup
python -c \"
import sqlite3
import shutil
# Create new database from backup
shutil.copy('data/investment_platform.db.backup', 'data/investment_platform_new.db')
# Test new database
conn = sqlite3.connect('data/investment_platform_new.db')
conn.execute('SELECT COUNT(*) FROM sqlite_master')
conn.close()
print('Database restored successfully')
\"

# If corruption is severe, reinitialize
Remove-Item data\\investment_platform.db
python scripts/setup/configure-environment.py --reset-database
```

### Disk Space Issues

**Problem**: Running out of disk space

**Symptoms**:
- \"No space left on device\" errors
- Write operation failures
- System slow performance

**Solutions**:
```powershell
# Check disk space
Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID, @{Name=\"Size(GB)\";Expression={[math]::Round($_.Size/1GB,2)}}, @{Name=\"FreeSpace(GB)\";Expression={[math]::Round($_.FreeSpace/1GB,2)}}

# Check directory sizes
Get-ChildItem | ForEach-Object {
    $size = (Get-ChildItem $_.FullName -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
    [PSCustomObject]@{
        Name = $_.Name
        \"Size(MB)\" = [math]::Round($size / 1MB, 2)
    }
} | Sort-Object \"Size(MB)\" -Descending

# Clean up cache and temporary files
Remove-Item data_cache\\* -Recurse -Force
Remove-Item logs\\*.log -ErrorAction SilentlyContinue
python -c \"
import tempfile, shutil
temp_dir = tempfile.gettempdir()
print(f'Temp directory: {temp_dir}')
# Manually clean if needed
\"

# Clean up model cache if not needed
# Remove-Item models\\.huggingface_cache\\* -Recurse -Force
```

## Network and Connectivity Issues

### Firewall and Port Blockin

**Problem**: Windows firewall or antivirus blocking connections

**Symptoms**:
- Connection timeouts
- \"Connection refused\" errors
- Services not accessible from outside

**Solutions**:
```powershell
# Check Windows Firewall rules
Get-NetFirewallRule | Where-Object {$_.DisplayName -like \"*Python*\" -or $_.DisplayName -like \"*Node*\"}

# Add firewall exception for Python
New-NetFirewallRule -DisplayName \"Python Investment Platform\" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow

# Check if ports are listening
netstat -ano | findstr :8000
netstat -ano | findstr :3001

# Test port accessibility
Test-NetConnection -ComputerName localhost -Port 8000

# Temporarily disable Windows Defender (for testing)
# Windows Security → Virus & threat protection → Manage settings → Real-time protection (OFF)
```

### DNS and Proxy Issues

**Problem**: Cannot resolve external domain names or proxy blocking

**Symptoms**:
- DNS resolution failures
- Proxy authentication errors
- Certificate verification failures

**Solutions**:
```powershell
# Test DNS resolution
nslookup api.polygon.io
Resolve-DnsName api.polygon.io

# Configure proxy if needed
$env:HTTP_PROXY = \"http://proxy.company.com:8080\"
$env:HTTPS_PROXY = \"http://proxy.company.com:8080\"
$env:NO_PROXY = \"localhost,127.0.0.1\"

# For corporate networks, configure certificates
# Import corporate certificates to Python certificate store
python -c \"
import requests
import ssl
print(f'Default CA bundle: {requests.certs.where()}')
context = ssl.create_default_context()
print(f'CA certificates loaded: {len(context.get_ca_certs())}')
\"

# Bypass SSL verification for testing (NOT for production)
# Set environment variable: PYTHONHTTPSVERIFY=0
```

## Getting Help

### Diagnostic Information Collection

Before seeking help, collect diagnostic information:

```powershell
# Create diagnostic report
$diagnostics = @\"
=== SYSTEM INFORMATION ===
OS: $(Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion)
Python: $(python --version)
Docker: $(docker --version 2>$null)

=== ENVIRONMENT VARIABLES ===
$(Get-ChildItem Env: | Where-Object {$_.Name -like '*API*' -or $_.Name -like '*LLM*'} | ForEach-Object {\"$($_.Name): $($_.Value -replace '(.{10}).*', '$1...')\"})

=== PROCESS STATUS ===
Python processes: $(Get-Process python -ErrorAction SilentlyContinue | Measure-Object | Select-Object -ExpandProperty Count)
Docker processes: $(Get-Process \"Docker Desktop\" -ErrorAction SilentlyContinue | Measure-Object | Select-Object -ExpandProperty Count)

=== DISK SPACE ===
$(Get-WmiObject -Class Win32_LogicalDisk | Where-Object {$_.DriveType -eq 3} | Select-Object DeviceID, @{Name=\"FreeSpace(GB)\";Expression={[math]::Round($_.FreeSpace/1GB,2)}})

=== RECENT ERRORS ===
$(Select-String -Path \"logs\\*.log\" -Pattern \"ERROR|CRITICAL\" | Select-Object -Last 5)
\"@

$diagnostics | Out-File \"diagnostic_report.txt\"
Write-Host \"Diagnostic report saved to diagnostic_report.txt\"
```

### Support Resources

1. **Documentation**:
   - [Installation Guide](../setup/installation-guide.md)
   - [Configuration Guide](../setup/configuration-guide.md)
   - [Local LLM Setup](../setup/local-llm-setup.md)
   - [Docker Deployment](../deployment/docker-deployment.md)

2. **Community Support**:
   - GitHub Issues: Report bugs and get community help
   - Discussion Forums: Ask questions and share solutions
   - Discord/Slack: Real-time community support

3. **Debugging Tools**:
   ```powershell
   # Enable debug mode
   $env:DEBUG = \"true\"
   $env:LOG_LEVEL = \"DEBUG\"

   # Run with verbose output
   python orchestrator.py --test-mode --verbose

   # Capture detailed logs
   python orchestrator.py --test-mode 2>&1 | Tee-Object debug_output.txt
   ```

### Reporting Issues

When reporting issues, include:

1. **System Information**: OS, Python version, Docker version (if applicable)
2. **Error Messages**: Complete error messages and stack traces
3. **Steps to Reproduce**: Exact steps that lead to the issue
4. **Configuration**: Relevant configuration file contents (remove API keys)
5. **Logs**: Recent log entries around the time of the issue
6. **Environment**: Whether using Docker, local installation, or development setup

### Emergency Recovery

If the system is completely broken:

```powershell
# Emergency reset (will lose data)
git clean -xdf  # Remove all untracked files
git reset --hard HEAD  # Reset to last commit

# Reinitialize from scratch
python scripts/initialize.py --interactive

# Or start fresh with Docker
docker compose down -v  # Remove volumes
docker compose build --no-cache
docker compose up -d
```

## Related Documentation

- [Installation Guide](../setup/installation-guide.md) - Complete setup instructions
- [Configuration Guide](../setup/configuration-guide.md) - Configuration options
- [Docker Deployment Guide](../deployment/docker-deployment.md) - Container deployment
- [API Documentation](../api/README.md) - Technical API reference

---

Remember: Most issues can be resolved by checking logs, verifying configuration, and ensuring all dependencies are properly installed. When in doubt, try the diagnostic tools first!
