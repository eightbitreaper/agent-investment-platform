# Development Guide

Comprehensive development guide for contributors to the Agent Investment Platform, covering setup, workflows, standards, and best practices.

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation Standards](#documentation-standards)
- [Contribution Process](#contribution-process)
- [Release Process](#release-process)

## Overview

The Agent Investment Platform welcomes contributions from developers of all skill levels. This guide provides everything you need to effectively contribute to the project.

### Project Philosophy

- **Modular Architecture** - Clean separation of concerns with MCP servers
- **Privacy First** - Local LLM support for sensitive financial data
- **Production Ready** - Enterprise-grade reliability and performance
- **Developer Friendly** - Comprehensive tooling and documentation
- **Open Source** - Transparent development with community involvement

### Technology Stack

- **Backend**: Python 3.11, FastAPI, SQLAlchemy, Redis
- **AI/ML**: Transformers, PyTorch, Hugging Face, Ollama
- **Data**: Pandas, NumPy, yfinance, financial APIs
- **Infrastructure**: Docker, PostgreSQL, Nginx, Prometheus
- **Frontend**: React, TypeScript, Chart.js (planned)
- **Testing**: pytest, pytest-asyncio, coverage
- **Development**: VS Code, Git, GitHub Actions

## Getting Started

### Prerequisites

- **Python 3.9+** (3.11 recommended)
- **Git** for version control
- **VS Code** (recommended) with Python extension
- **Docker Desktop** (optional but recommended)
- **Node.js 18+** (for JavaScript MCP servers)

### Quick Development Setup

```powershell
# Clone the repository
git clone https://github.com/your-username/agent-investment-platform.git
cd agent-investment-platform

# Set up development environment
python scripts/initialize.py --interactive

# Or use VS Code tasks (recommended)
# Open in VS Code and run: Tasks: Run Task -> 🚀 Initialize Platform
```

### Development Environment Setup

1. **Create Virtual Environment**:
   ```powershell
   python -m venv venv
   .\\venv\\Scripts\\activate  # Windows
   source venv/bin/activate     # Linux/Mac
   ```

2. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

3. **Configure Environment**:
   ```powershell
   copy .env.example .env
   # Edit .env with your development API keys
   ```

4. **Initialize Database**:
   ```powershell
   python scripts/setup/configure-environment.py --reset-database
   ```

5. **Start Development Services**:
   ```powershell
   # Option 1: Docker development environment
   docker compose --profile development up -d
   
   # Option 2: Local development servers
   python run_mcp_server.py --start-all
   python orchestrator.py --dev-mode
   ```

## Development Environment

### VS Code Configuration

The project includes comprehensive VS Code configuration:

- **`.vscode/settings.json`** - Optimized settings for Python development
- **`.vscode/tasks.json`** - 20+ automation tasks
- **`.vscode/launch.json`** - Debug configurations
- **`.vscode/extensions.json`** - Recommended extensions

**Recommended Extensions**:
- Python
- Pylance
- GitLens
- Docker
- YAML
- Markdown All in One

### Development Tasks

Use VS Code tasks or command line:

```powershell
# VS Code: Ctrl+Shift+P -> Tasks: Run Task

# Available tasks:
# - 🚀 Initialize Platform
# - 🔍 Validate Setup
# - 🧪 Run All Tests
# - 📊 Generate Test Report
# - 🔧 Install Dependencies
# - 🐋 Start Docker Services
# - And many more...
```

### Environment Configurations

#### Development Environment
```yaml
# config/environments/development.yaml
debug: true
log_level: DEBUG
mock_apis: false
cache_ttl: 300
database_url: sqlite:///data/dev.db
```

#### Testing Environment
```yaml
# config/environments/testing.yaml
debug: true
log_level: DEBUG
mock_apis: true
cache_ttl: 60
database_url: sqlite:///:memory:
```

#### Production Environment
```yaml
# config/environments/production.yaml
debug: false
log_level: INFO
mock_apis: false
cache_ttl: 3600
database_url: ${DATABASE_URL}
```

## Project Structure

### Directory Organization

```
agent-investment-platform/
├── src/                          # Core source code
│   ├── mcp_servers/             # MCP server implementations
│   ├── analysis/                # Analysis engines
│   ├── backtesting/             # Backtesting framework
│   ├── reports/                 # Report generation
│   ├── notifications/           # Notification system
│   ├── monitoring/              # System monitoring
│   └── utils/                   # Utility functions
├── config/                      # Configuration files
├── docs/                        # Documentation
├── scripts/                     # Automation scripts
├── tests/                       # Test suites
├── examples/                    # Usage examples
├── templates/                   # Report templates
├── .vscode/                     # VS Code configuration
├── .memory/                     # AI memory bank
└── deployment/                  # Deployment configs
```

### Module Structure

Each Python module follows consistent structure:

```python
# Standard module structure
\"\"\"
Module docstring explaining purpose and usage.
\"\"\"

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Module constants
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3

# Type definitions
@dataclass
class ConfigurationData:
    \"\"\"Configuration data structure.\"\"\"
    setting1: str
    setting2: int = 100

# Main classes
class ModuleClass:
    \"\"\"Main module class with clear responsibilities.\"\"\"
    
    def __init__(self, config: ConfigurationData):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    async def public_method(self, param: str) -> Dict[str, Any]:
        \"\"\"Public method with type hints and docstring.\"\"\"
        return await self._private_method(param)
    
    async def _private_method(self, param: str) -> Dict[str, Any]:
        \"\"\"Private method for internal use.\"\"\"
        # Implementation
        pass

# Module-level functions
def utility_function(param: str) -> str:
    \"\"\"Utility function for common operations.\"\"\"
    return param.upper()
```

## Development Workflow

### Branch Strategy

We use GitHub Flow with feature branches:

```bash
# Create feature branch
git checkout -b feature/add-new-analysis-tool

# Make changes and commit
git add .
git commit -m \"feat(analysis): Add new technical indicator tool\"

# Push and create pull request
git push origin feature/add-new-analysis-tool
```

### Commit Message Format

Follow Conventional Commits specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

**Types**:
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Test additions or modifications
- `chore`: Build process or auxiliary tool changes

**Examples**:
```bash
feat(mcp): Add sentiment analysis tool to news server
fix(backtesting): Resolve date range calculation bug
docs(api): Update MCP server reference documentation
```

### Pull Request Process

1. **Create Feature Branch** from main
2. **Implement Changes** following coding standards
3. **Add Tests** for new functionality
4. **Update Documentation** as needed
5. **Run Full Test Suite** and ensure all pass
6. **Create Pull Request** with clear description
7. **Address Review Comments** promptly
8. **Merge** after approval (squash and merge preferred)

### Code Review Guidelines

**For Authors**:
- Keep PRs focused and reasonably sized
- Write clear PR descriptions
- Add tests for new functionality
- Update documentation
- Respond to feedback constructively

**For Reviewers**:
- Review code for correctness, clarity, and maintainability
- Check test coverage and quality
- Verify documentation updates
- Be constructive and specific in feedback
- Approve when ready, request changes when needed

## Coding Standards

### Python Style Guide

We follow PEP 8 with some modifications:

```python
# Line length: 88 characters (Black formatter default)
# Imports: isort configuration
# Type hints: Required for public APIs
# Docstrings: Google style

class ExampleClass:
    \"\"\"Example class demonstrating coding standards.
    
    This class shows proper Python style including type hints,
    docstrings, and error handling.
    
    Args:
        config: Configuration object
        timeout: Request timeout in seconds
    
    Raises:
        ValueError: Invalid configuration
        ConnectionError: Network connection failed
    \"\"\"
    
    def __init__(self, config: Dict[str, Any], timeout: int = 30):
        self.config = config
        self.timeout = timeout
        self._validate_config()
    
    async def fetch_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        \"\"\"Fetch data for the given symbol.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Data dictionary or None if not found
            
        Raises:
            ValueError: Invalid symbol format
            APIError: External API error
        \"\"\"
        if not symbol or not symbol.isalpha():
            raise ValueError(f\"Invalid symbol: {symbol}\")
        
        try:
            response = await self._make_request(symbol)
            return self._parse_response(response)
        except Exception as e:
            self.logger.error(f\"Failed to fetch data for {symbol}: {e}\")
            raise APIError(f\"Data fetch failed: {e}\") from e
    
    def _validate_config(self) -> None:
        \"\"\"Validate configuration parameters.\"\"\"
        required_keys = ['api_key', 'base_url']
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f\"Missing required config: {key}\")
```

### JavaScript Style Guide

For Node.js MCP servers:

```javascript
// Use ES6+ features, async/await, proper error handling
const axios = require('axios');

class NewsAnalysisServer {
    /**
     * News analysis MCP server implementation.
     * @param {Object} config - Server configuration
     */
    constructor(config) {
        this.config = config;
        this.apiKey = process.env.NEWS_API_KEY;
        
        if (!this.apiKey) {
            throw new Error('NEWS_API_KEY environment variable required');
        }
    }
    
    /**
     * Analyze news sentiment for a stock.
     * @param {string} symbol - Stock ticker symbol
     * @param {number} daysBack - Days to analyze
     * @returns {Promise<Object>} Sentiment analysis result
     */
    async analyzeSentiment(symbol, daysBack = 7) {
        try {
            const articles = await this.fetchNews(symbol, daysBack);
            const sentiment = await this.calculateSentiment(articles);
            
            return {
                symbol,
                sentiment: sentiment.score,
                confidence: sentiment.confidence,
                articleCount: articles.length,
                timeRange: `${daysBack} days`
            };
        } catch (error) {
            this.logger.error(`Sentiment analysis failed for ${symbol}:`, error);
            throw new Error(`Failed to analyze sentiment: ${error.message}`);
        }
    }
    
    async fetchNews(symbol, daysBack) {
        // Implementation
    }
    
    async calculateSentiment(articles) {
        // Implementation
    }
}

module.exports = NewsAnalysisServer;
```

### Configuration Management

Use structured configuration with validation:

```python
from pydantic import BaseSettings, validator
from typing import List, Optional

class ServerConfig(BaseSettings):
    \"\"\"Server configuration with validation.\"\"\"
    
    # API Configuration
    api_key: str
    base_url: str = \"https://api.example.com\"
    timeout: int = 30
    
    # Feature flags
    enable_caching: bool = True
    enable_metrics: bool = True
    
    # Rate limiting
    requests_per_minute: int = 60
    burst_limit: int = 10
    
    @validator('api_key')
    def validate_api_key(cls, v):
        if not v or len(v) < 10:
            raise ValueError('Invalid API key')
        return v
    
    @validator('timeout')
    def validate_timeout(cls, v):
        if v < 1 or v > 300:
            raise ValueError('Timeout must be between 1 and 300 seconds')
        return v
    
    class Config:
        env_file = '.env'
        env_prefix = 'SERVER_'
```

## Testing Guidelines

### Test Structure

```
tests/
├── unit/                    # Unit tests
│   ├── test_analysis/
│   ├── test_mcp_servers/
│   └── test_utils/
├── integration/             # Integration tests
│   ├── test_api_endpoints/
│   └── test_mcp_integration/
├── e2e/                     # End-to-end tests
│   └── test_workflows/
├── fixtures/                # Test data and fixtures
└── conftest.py             # Pytest configuration
```

### Unit Testing

```python
import pytest
from unittest.mock import Mock, AsyncMock, patch
from src.analysis.sentiment_analyzer import SentimentAnalyzer

class TestSentimentAnalyzer:
    \"\"\"Test suite for SentimentAnalyzer.\"\"\"
    
    @pytest.fixture
    def analyzer(self):
        \"\"\"Create analyzer instance for testing.\"\"\"
        config = {
            'model_name': 'test-model',
            'confidence_threshold': 0.5
        }
        return SentimentAnalyzer(config)
    
    @pytest.mark.asyncio
    async def test_analyze_positive_sentiment(self, analyzer):
        \"\"\"Test positive sentiment analysis.\"\"\"
        text = \"Great company with strong fundamentals and growth prospects\"
        
        result = await analyzer.analyze(text)
        
        assert result.sentiment > 0
        assert result.confidence > 0.5
        assert result.label == 'POSITIVE'
    
    @pytest.mark.asyncio
    async def test_analyze_empty_text_raises_error(self, analyzer):
        \"\"\"Test that empty text raises appropriate error.\"\"\"
        with pytest.raises(ValueError, match=\"Text cannot be empty\"):
            await analyzer.analyze(\"\")
    
    @pytest.mark.asyncio
    @patch('src.analysis.sentiment_analyzer.model_client')
    async def test_model_api_error_handling(self, mock_client, analyzer):
        \"\"\"Test handling of model API errors.\"\"\"
        mock_client.analyze.side_effect = ConnectionError(\"API unavailable\")
        
        with pytest.raises(AnalysisError, match=\"Sentiment analysis failed\"):
            await analyzer.analyze(\"test text\")
    
    def test_confidence_threshold_validation(self):
        \"\"\"Test configuration validation.\"\"\"
        with pytest.raises(ValueError, match=\"Confidence threshold\"):
            SentimentAnalyzer({'confidence_threshold': 1.5})
```

### Integration Testing

```python
import pytest
import httpx
from fastapi.testclient import TestClient
from src.main import app

class TestMCPIntegration:
    \"\"\"Integration tests for MCP server communication.\"\"\"
    
    @pytest.fixture
    def client(self):
        \"\"\"Create test client.\"\"\"
        return TestClient(app)
    
    @pytest.mark.asyncio
    async def test_stock_quote_integration(self, client):
        \"\"\"Test full stock quote workflow.\"\"\"
        response = client.post(
            \"/api/v1/analysis\",
            json={\"symbol\": \"AAPL\", \"analysis_type\": \"quote\"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert \"price\" in data
        assert \"symbol\" in data
        assert data[\"symbol\"] == \"AAPL\"
    
    @pytest.mark.asyncio
    async def test_mcp_server_health_checks(self):
        \"\"\"Test that all MCP servers are healthy.\"\"\"
        servers = [
            \"http://localhost:3001\",
            \"http://localhost:3002\",
            \"http://localhost:3003\",
            \"http://localhost:3004\"
        ]
        
        async with httpx.AsyncClient() as client:
            for server_url in servers:
                response = await client.get(f\"{server_url}/health\")
                assert response.status_code == 200
```

### Test Configuration

```python
# conftest.py
import pytest
import asyncio
from typing import Generator
from unittest.mock import Mock

@pytest.fixture(scope=\"session\")
def event_loop() -> Generator:
    \"\"\"Create event loop for async tests.\"\"\"
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_api_client():
    \"\"\"Mock API client for testing.\"\"\"
    client = Mock()
    client.get_quote.return_value = {
        \"symbol\": \"AAPL\",
        \"price\": 150.00,
        \"change\": 2.50
    }
    return client

@pytest.fixture(scope=\"function\")
def clean_database():
    \"\"\"Ensure clean database state for tests.\"\"\"
    # Setup clean state
    yield
    # Cleanup after test
```

### Running Tests

```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_analysis/test_sentiment_analyzer.py

# Run tests matching pattern
pytest -k \"test_sentiment\"

# Run with verbose output
pytest -v

# Run only fast tests (exclude slow integration tests)
pytest -m \"not slow\"
```

## Documentation Standards

### Docstring Format

Use Google-style docstrings:

```python
def complex_function(param1: str, param2: int, param3: Optional[bool] = None) -> Dict[str, Any]:
    \"\"\"Perform complex operation with multiple parameters.
    
    This function demonstrates the standard docstring format used throughout
    the project. It includes detailed parameter and return descriptions.
    
    Args:
        param1: Description of the first parameter
        param2: Description of the second parameter with more detail about
            what values are acceptable and their meaning
        param3: Optional parameter with default behavior description
    
    Returns:
        Dictionary containing the results with the following keys:
            - 'status': Operation status ('success' or 'error')
            - 'data': Result data or None if error
            - 'message': Human-readable status message
    
    Raises:
        ValueError: When param1 is empty or param2 is negative
        ConnectionError: When external service is unavailable
        ProcessingError: When operation fails due to data issues
    
    Example:
        Basic usage with required parameters:
        
        >>> result = complex_function(\"test\", 42)
        >>> print(result['status'])
        'success'
        
        Usage with optional parameter:
        
        >>> result = complex_function(\"test\", 42, True)
        >>> print(result['data'])
        {'processed': True, 'value': 42}
    \"\"\"
    # Implementation here
    pass
```

### Markdown Documentation

Follow consistent markdown structure:

```markdown
# Document Title

Brief description of what this document covers and its purpose.

## Table of Contents

- [Section 1](#section-1)
- [Section 2](#section-2)
- [Examples](#examples)

## Section 1

### Subsection

Content with proper formatting:

- Use **bold** for emphasis
- Use `code` for inline code
- Use > for important notes

> **Note**: Important information that users should be aware of.

### Code Examples

Always include working examples:

\`\`\`python
# Example with clear comments
def example_function():
    \"\"\"Example function demonstrating best practices.\"\"\"
    return \"Hello World\"

# Usage
result = example_function()
print(result)
\`\`\`

### Related Documentation

Link to related documents using relative paths:
- [Configuration Guide](../setup/configuration-guide.md)
- [API Reference](../api/README.md)
```

## Contribution Process

### Getting Started

1. **Fork the Repository** on GitHub
2. **Clone Your Fork** locally
3. **Set Up Development Environment** following this guide
4. **Create Feature Branch** for your changes
5. **Make Changes** following coding standards
6. **Test Your Changes** thoroughly
7. **Submit Pull Request** with clear description

### Contribution Guidelines

**Good Contributions**:
- Bug fixes with tests
- New features with documentation
- Performance improvements
- Documentation improvements
- Test coverage improvements

**Before Contributing**:
- Check existing issues and PRs
- Discuss major changes in issues first
- Ensure your changes fit the project vision
- Follow the established patterns and conventions

**Pull Request Checklist**:
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Tests added for new functionality
- [ ] All tests pass
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
- [ ] Commit messages follow conventional format

### Issue Guidelines

**Bug Reports**:
- Clear, descriptive title
- Steps to reproduce
- Expected vs actual behavior
- Environment details
- Relevant logs or screenshots

**Feature Requests**:
- Clear problem statement
- Proposed solution
- Alternative solutions considered
- Additional context

**Questions**:
- Check documentation first
- Search existing issues
- Provide context about what you're trying to achieve

## Release Process

### Version Management

We use Semantic Versioning (SemVer):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Workflow

1. **Prepare Release Branch**
2. **Update Version Numbers**
3. **Update CHANGELOG.md**
4. **Run Full Test Suite**
5. **Create Release PR**
6. **Merge and Tag Release**
7. **Publish Release Notes**
8. **Deploy to Production**

### Deployment

Production deployment is handled via Docker containers:

```bash
# Build production image
docker build -t agent-investment-platform:latest .

# Deploy with Docker Compose
docker compose --profile production up -d

# Health check
curl http://localhost:8000/health
```

## Getting Help

### Resources

- **Documentation**: Comprehensive guides in `docs/`
- **Examples**: Working examples in `examples/`
- **Tests**: Reference implementations in `tests/`
- **Issues**: Ask questions and report bugs
- **Discussions**: Community support and ideas

### Community

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and community help
- **Code Reviews**: Learn from feedback on PRs
- **Documentation**: Contribute to improve guides

### Mentorship

New contributors can get help with:
- Setting up development environment
- Understanding project architecture
- Finding good first issues
- Code review process
- Best practices and conventions

---

## Related Documentation

- [Contributing Guide](contributing.md) - Detailed contribution guidelines
- [API Documentation](../api/README.md) - Complete API reference
- [Configuration Guide](../setup/configuration-guide.md) - System configuration
- [Troubleshooting Guide](../troubleshooting/common-issues.md) - Common issues

Welcome to the Agent Investment Platform development community! We're excited to have you contribute to building the future of AI-powered investment analysis.