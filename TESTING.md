# Testing Strategy

## 📁 Test Organization

```
tests/
├── integration/           # Integration tests for MCP servers
│   └── test_mcp_servers.py
├── api/                   # External API integration tests  
│   ├── test_polygon_direct.py
│   └── test_polygon_mcp.py
├── analysis/              # Financial analysis tests
└── agents/                # Agent behavior tests

dev-tools/                 # Development utilities
├── test_polygon_api.py    # Ad-hoc Polygon API testing
├── test_yfinance_data.py  # Yahoo Finance testing
└── README.md

run_tests.py              # Main test runner
```

## 🎯 Test Categories

### Integration Tests (`tests/integration/`)
- **Purpose**: Test MCP server functionality and inter-component communication
- **Coverage**: All 4 production MCP servers
- **Usage**: `python run_tests.py --integration`
- **Status**: ✅ 100% pass rate

### API Tests (`tests/api/`)
- **Purpose**: Test external API integrations (Polygon, Alpha Vantage, etc.)
- **Coverage**: Real API calls with actual data
- **Usage**: `python run_tests.py --api`
- **Requirements**: API keys configured
- **Status**: ✅ Polygon API validated

### Development Tools (`dev-tools/`)
- **Purpose**: Rapid prototyping and debugging utilities
- **Coverage**: Ad-hoc testing and validation
- **Usage**: Direct script execution
- **Status**: ✅ Polygon integration working

## ✅ Recommendation

**KEEP** both approaches:

1. **Organized Test Suites** - For CI/CD, comprehensive validation, production readiness
2. **Development Tools** - For rapid iteration, debugging, and prototyping

This gives us both **reliability** (comprehensive tests) and **agility** (quick dev tools).