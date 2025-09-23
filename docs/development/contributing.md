# Contributing to Agent Investment Platform

Thank you for your interest in contributing to the Agent Investment Platform! This guide will help you get started with contributing code, documentation, and ideas to make this project better.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Ways to Contribute](#ways-to-contribute)
- [Development Process](#development-process)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Issue Guidelines](#issue-guidelines)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Documentation Guidelines](#documentation-guidelines)
- [Community Guidelines](#community-guidelines)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](../CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

### Prerequisites

Before you start contributing, make sure you have:

- **Python 3.9+** (3.11 recommended)
- **Git** for version control
- **GitHub account** for submitting contributions
- **VS Code** (recommended) with Python extension
- **Docker Desktop** (optional but helpful for testing)

### Development Setup

1. **Fork the Repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/YOUR-USERNAME/agent-investment-platform.git
   cd agent-investment-platform
   ```

2. **Set Up Development Environment**
   ```powershell
   # Quick setup
   python scripts/initialize.py --interactive
   
   # Or manual setup
   python -m venv venv
   .\\venv\\Scripts\\activate  # Windows
   pip install -r requirements.txt
   ```

3. **Verify Setup**
   ```powershell
   # Run health check
   python scripts/setup/validate-setup.py --quick
   
   # Run tests
   python -m pytest tests/ -v
   ```

4. **Configure Git**
   ```bash
   git config user.name \"Your Name\"
   git config user.email \"your.email@example.com\"
   ```

## Ways to Contribute

### 🐛 Bug Reports

Help us improve by reporting bugs:

- **Search existing issues** first to avoid duplicates
- **Use the bug report template** when creating new issues
- **Provide clear reproduction steps**
- **Include system information** (OS, Python version, etc.)
- **Add logs or screenshots** when helpful

### 💡 Feature Requests

Suggest new features or improvements:

- **Check existing feature requests** to avoid duplicates
- **Clearly describe the problem** you're trying to solve
- **Propose a specific solution** with examples
- **Consider alternative approaches** and their trade-offs
- **Explain the use case** and potential impact

### 📝 Documentation

Improve project documentation:

- **Fix typos and grammar** in existing docs
- **Add missing documentation** for features
- **Create tutorials and examples** for common use cases
- **Improve API documentation** and code comments
- **Update outdated information**

### 🔧 Code Contributions

Contribute code improvements:

- **Bug fixes** - Fix reported issues
- **New features** - Implement requested functionality
- **Performance improvements** - Optimize existing code
- **Test improvements** - Add tests and improve coverage
- **Refactoring** - Improve code structure and maintainability

### 🧪 Testing and Quality Assurance

Help improve code quality:

- **Write tests** for existing functionality
- **Improve test coverage** in low-coverage areas
- **Test on different platforms** (Windows, Linux, macOS)
- **Performance testing** and benchmarking
- **Security testing** and vulnerability assessment

## Development Process

### Workflow Overview

1. **Choose or Create Issue** - Find an issue to work on or create one
2. **Fork and Clone** - Fork the repo and clone to your machine
3. **Create Branch** - Create a feature branch for your work
4. **Make Changes** - Implement your changes following standards
5. **Test Changes** - Run tests and ensure everything works
6. **Document Changes** - Update documentation as needed
7. **Submit PR** - Create a pull request with clear description
8. **Review Process** - Respond to feedback and make improvements
9. **Merge** - Once approved, your changes will be merged

### Branch Naming

Use descriptive branch names:

```bash
# Feature branches
git checkout -b feature/add-sentiment-analysis
git checkout -b feature/improve-backtesting-performance

# Bug fix branches
git checkout -b fix/resolve-api-timeout-issue
git checkout -b fix/correct-calculation-error

# Documentation branches
git checkout -b docs/update-installation-guide
git checkout -b docs/add-api-examples
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat` - New features
- `fix` - Bug fixes
- `docs` - Documentation changes
- `style` - Code formatting (no logic changes)
- `refactor` - Code restructuring (no behavior changes)
- `test` - Adding or updating tests
- `chore` - Build/tooling changes

**Examples:**
```bash
feat(analysis): Add RSI technical indicator calculation
fix(mcp): Resolve connection timeout in stock data server
docs(api): Update MCP server integration examples
test(backtesting): Add comprehensive performance analyzer tests
```

## Pull Request Guidelines

### Before Submitting

- **Check for existing PRs** that might conflict
- **Ensure your fork is up to date** with main branch
- **Run all tests** and ensure they pass
- **Update documentation** for any new features
- **Follow coding standards** and style guidelines

### PR Description Template

Use this template for your pull request description:

```markdown
## Description
Brief description of what this PR does and why.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that causes existing functionality to change)
- [ ] Documentation update

## How Has This Been Tested?
Describe the tests you ran and how to reproduce them.

## Screenshots (if applicable)
Add screenshots to help explain your changes.

## Checklist
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or my feature works
- [ ] New and existing unit tests pass locally with my changes
```

### Review Process

1. **Automated Checks** - CI/CD pipeline runs tests
2. **Code Review** - Maintainers review your code
3. **Feedback** - Address any requested changes
4. **Approval** - Once approved, PR will be merged
5. **Cleanup** - Delete your feature branch after merge

### What We Look For

**Code Quality:**
- Follows established patterns and conventions
- Proper error handling and edge cases
- Clear, readable code with good variable names
- Appropriate comments and docstrings

**Testing:**
- Adequate test coverage for new functionality
- Tests are clear and maintainable
- Edge cases are covered
- Tests run reliably

**Documentation:**
- API changes are documented
- User-facing changes include documentation updates
- Code comments explain complex logic
- Examples are provided where helpful

## Issue Guidelines

### Creating Good Issues

**For Bug Reports:**
```markdown
## Bug Description
Clear description of what's wrong.

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen.

## Actual Behavior
What actually happens.

## Environment
- OS: Windows 10
- Python: 3.11.5
- Version: 1.0.0

## Additional Context
Any other relevant information.
```

**For Feature Requests:**
```markdown
## Problem Statement
What problem does this solve?

## Proposed Solution
Describe your proposed solution.

## Alternatives Considered
Other approaches you've considered.

## Additional Context
Any other relevant information.
```

### Issue Labels

We use labels to categorize issues:

- **Type**: `bug`, `feature`, `documentation`, `question`
- **Priority**: `high`, `medium`, `low`
- **Difficulty**: `good first issue`, `help wanted`, `advanced`
- **Component**: `mcp-servers`, `analysis`, `docs`, `infrastructure`
- **Status**: `needs-triage`, `blocked`, `in-progress`

## Coding Standards

### Python Code Style

We follow PEP 8 with these tools:

- **Black** - Code formatting (88 character line length)
- **isort** - Import sorting
- **flake8** - Linting
- **mypy** - Type checking

```python
# Good example
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

def analyze_stock_data(
    symbol: str,
    data: Dict[str, float],
    indicators: Optional[List[str]] = None
) -> Dict[str, float]:
    \"\"\"Analyze stock data with specified indicators.
    
    Args:
        symbol: Stock ticker symbol
        data: Price and volume data
        indicators: List of indicators to calculate
        
    Returns:
        Dictionary of calculated indicators
        
    Raises:
        ValueError: Invalid symbol or data format
    \"\"\"
    if not symbol or not data:
        raise ValueError(\"Symbol and data are required\")
    
    indicators = indicators or ['SMA', 'RSI']
    results = {}
    
    for indicator in indicators:
        try:
            results[indicator] = calculate_indicator(indicator, data)
        except Exception as e:
            logger.error(f\"Failed to calculate {indicator} for {symbol}: {e}\")
            continue
    
    return results
```

### JavaScript Code Style

For MCP servers written in JavaScript:

```javascript
// Good example
const axios = require('axios');

class NewsAnalysisServer {
    /**
     * Initialize news analysis server.
     * @param {Object} config - Server configuration
     */
    constructor(config) {
        this.config = config;
        this.apiKey = process.env.NEWS_API_KEY;
        
        if (!this.apiKey) {
            throw new Error('NEWS_API_KEY environment variable is required');
        }
    }
    
    /**
     * Analyze sentiment for news articles.
     * @param {string} symbol - Stock symbol
     * @param {number} days - Days to analyze
     * @returns {Promise<Object>} Sentiment analysis results
     */
    async analyzeSentiment(symbol, days = 7) {
        try {
            const articles = await this.fetchNews(symbol, days);
            return this.calculateSentiment(articles);
        } catch (error) {
            console.error(`Sentiment analysis failed: ${error.message}`);
            throw error;
        }
    }
}

module.exports = NewsAnalysisServer;
```

### Configuration Standards

Use structured configuration with validation:

```python
from pydantic import BaseSettings, validator

class ServerConfig(BaseSettings):
    \"\"\"Server configuration with validation.\"\"\"
    
    api_key: str
    timeout: int = 30
    max_retries: int = 3
    
    @validator('timeout')
    def validate_timeout(cls, v):
        if v < 1 or v > 300:
            raise ValueError('Timeout must be between 1 and 300')
        return v
    
    class Config:
        env_file = '.env'
```

## Testing Requirements

### Test Coverage

- **Minimum 80% coverage** for new code
- **All public APIs** must have tests
- **Critical paths** require comprehensive testing
- **Error conditions** should be tested

### Test Types

**Unit Tests:**
```python
import pytest
from unittest.mock import Mock, patch
from src.analysis.sentiment_analyzer import SentimentAnalyzer

class TestSentimentAnalyzer:
    def test_positive_sentiment(self):
        analyzer = SentimentAnalyzer()
        result = analyzer.analyze(\"Great company with strong growth\")
        assert result.sentiment > 0.5
        assert result.label == 'POSITIVE'
    
    def test_empty_input_raises_error(self):
        analyzer = SentimentAnalyzer()
        with pytest.raises(ValueError):
            analyzer.analyze(\"\")
```

**Integration Tests:**
```python
import pytest
from fastapi.testclient import TestClient
from src.main import app

def test_stock_analysis_endpoint():
    client = TestClient(app)
    response = client.post(
        \"/api/v1/analyze\",
        json={\"symbol\": \"AAPL\"}
    )
    assert response.status_code == 200
    assert \"recommendation\" in response.json()
```

### Running Tests

```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_analysis.py

# Run tests in parallel
pytest -n auto
```

## Documentation Guidelines

### Documentation Types

1. **API Documentation** - Generated from docstrings
2. **User Guides** - How-to guides for end users
3. **Developer Guides** - Technical implementation details
4. **Examples** - Working code examples
5. **Reference** - Complete parameter and option lists

### Writing Style

- **Clear and concise** - Avoid unnecessary complexity
- **Actionable** - Provide specific steps and examples
- **Complete** - Cover all necessary information  
- **Accurate** - Keep information up-to-date
- **Accessible** - Write for your target audience

### Markdown Standards

```markdown
# Main Title (H1)

Brief introduction explaining what this document covers.

## Section Title (H2)

### Subsection (H3)

Content with proper formatting:

- Use **bold** for important terms
- Use `code` for inline code elements
- Use > for important notes and warnings

> **Warning**: Critical information that could cause problems.

### Code Examples

Always provide working examples:

\`\`\`python
# Example with clear context
def example_function():
    return \"Hello World\"

result = example_function()
print(result)  # Output: Hello World
\`\`\`

### Links and References

- [Documentation Home](../README.md)
- [GitHub Documentation](https://docs.github.com)
- [Python Style Guide (PEP 8)](https://pep8.org)
```

## Community Guidelines

### Communication

- **Be respectful** - Treat everyone with kindness and respect
- **Be constructive** - Provide helpful feedback and suggestions
- **Be patient** - Remember that people have different experience levels
- **Be inclusive** - Welcome contributors from all backgrounds

### Getting Help

**For Questions:**
1. **Check documentation** first
2. **Search existing issues** for similar questions
3. **Ask in discussions** for general questions
4. **Create an issue** for specific problems

**For Support:**
- **GitHub Issues** - Bug reports and feature requests
- **GitHub Discussions** - Questions and general discussion
- **Code Reviews** - Learning opportunity through feedback

### Recognition

We appreciate all contributions and recognize contributors through:

- **Contributor credits** in release notes
- **GitHub contributor graphs** showing your impact
- **Special thanks** for significant contributions
- **Maintainer status** for long-term contributors

## Getting Started with Your First Contribution

### Good First Issues

Look for issues labeled `good first issue`:
- Usually small, well-defined tasks
- Don't require deep project knowledge
- Have clear acceptance criteria
- Maintainers provide guidance

### Suggested Areas for New Contributors

1. **Documentation improvements** - Fix typos, add examples
2. **Test additions** - Add tests for existing functionality
3. **Bug fixes** - Fix small, well-defined bugs
4. **Code cleanup** - Improve code formatting and style
5. **Example scripts** - Create usage examples

### Mentorship

New contributors can get help with:
- Understanding project architecture
- Setting up development environment
- Finding appropriate tasks
- Code review process
- Best practices and patterns

## Questions?

If you have questions about contributing, please:

1. **Check this guide** and other documentation
2. **Search existing issues** and discussions
3. **Ask in GitHub Discussions** for general questions
4. **Create an issue** for specific problems
5. **Reach out to maintainers** if you need direct help

We're here to help you succeed and make meaningful contributions to the project!

---

## Related Documentation

- [Development Guide](README.md) - Complete development documentation
- [Code of Conduct](../CODE_OF_CONDUCT.md) - Community standards
- [API Documentation](../api/README.md) - Technical API reference
- [Installation Guide](../setup/installation-guide.md) - Setup instructions

Thank you for contributing to the Agent Investment Platform! Your contributions help make this project better for everyone. 🚀