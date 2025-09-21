# Development Tools

This directory is reserved for development and debugging utilities for the Agent Investment Platform.

## 🎯 Purpose

Development tools will be added here as needed for:
- Testing new API integrations
- Debugging specific issues
- Rapid prototyping with external services
- Manual verification of responses

## 🧪 Current Testing Approach

For comprehensive testing, use the organized test suites:

```bash
# Run all tests
python run_tests.py --all

# Run specific test categories
python run_tests.py --integration  # MCP server integration tests
python run_tests.py --api          # API integration tests (requires API keys)
python run_tests.py --unit         # Unit tests
```

## 📁 Test Organization

**Production Testing:**
- `tests/integration/` - MCP server integration tests
- `tests/api/` - External API tests (Polygon, etc.)

**API Testing Examples:**
```bash
# Test Polygon API integration
$env:POLYGON_API_KEY="your-key"; python tests/api/test_polygon_direct.py

# Test MCP server with Polygon
$env:POLYGON_API_KEY="your-key"; python tests/api/test_polygon_mcp.py
```