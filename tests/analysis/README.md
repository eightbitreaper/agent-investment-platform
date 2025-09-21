# Analysis Engine Test Suite

Comprehensive test suite for the Agent Investment Platform analysis engine components.

## 📋 Test Overview

This test suite provides comprehensive testing for all analysis engine components:

### 🧪 Test Components

1. **Sentiment Analyzer Tests** (`test_sentiment_analyzer.py`)
   - Financial sentiment lexicon functionality
   - Rule-based sentiment analysis
   - Batch processing capabilities
   - Symbol-specific sentiment aggregation
   - Error handling and edge cases

2. **Chart Analyzer Tests** (`test_chart_analyzer.py`)
   - Technical indicator calculations (SMA, EMA, RSI, MACD, Bollinger Bands, VWAP)
   - Chart pattern recognition
   - Support/resistance level detection
   - Trend analysis and signal generation
   - Data validation and error handling

3. **Recommendation Engine Tests** (`test_recommendation_engine.py`)
   - Multi-factor analysis integration
   - Investment recommendation generation
   - Strategy-aware decision making
   - Risk assessment and position sizing
   - Portfolio optimization
   - Configuration handling

4. **Integration Tests** (`test_integration.py`)
   - End-to-end workflow testing
   - Component interaction validation
   - Real-world scenario simulation
   - Performance and robustness testing

## 🚀 Running Tests

### Prerequisites

Ensure all dependencies are installed:
```bash
pip install pytest pytest-asyncio pandas numpy pyyaml
```

### Test Execution Methods

#### Method 1: Direct Python Execution (Recommended)

Set the Python path and run tests directly:

```powershell
# Windows PowerShell
$env:PYTHONPATH = "src"
python -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'src'))

# Run specific test
from tests.analysis.test_sentiment_analyzer import TestFinancialSentimentAnalyzer
test_instance = TestFinancialSentimentAnalyzer()
test_instance.test_analyzer_initialization()
print('[PASS] Test completed successfully')
"
```

#### Method 2: Using Test Runner Script

```bash
cd tests/analysis
python run_tests.py [test_type]
```

Available test types:
- `all` - Run all analysis engine tests
- `quick` - Run quick tests (skip slow integration tests)
- `sentiment` - Run sentiment analyzer tests only
- `chart` - Run chart analyzer tests only
- `recommendation` - Run recommendation engine tests only
- `integration` - Run integration tests only

#### Method 3: Direct Module Testing

```python
# Example: Test sentiment analyzer
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'src'))

from analysis.sentiment_analyzer import FinancialSentimentAnalyzer

# Create and test analyzer
analyzer = FinancialSentimentAnalyzer(model_type="rule_based")
print(f"Analyzer created: {analyzer.model_type}")
```

## 📊 Test Coverage

### Sentiment Analyzer Coverage
- ✅ Initialization and configuration
- ✅ Text cleaning and preprocessing
- ✅ Financial keyword extraction
- ✅ Positive/negative/neutral sentiment analysis
- ✅ Batch processing
- ✅ Symbol-specific sentiment aggregation
- ✅ Confidence scoring
- ✅ Export functionality
- ✅ Error handling

### Chart Analyzer Coverage
- ✅ Basic analysis workflow
- ✅ Moving averages (SMA, EMA)
- ✅ VWAP calculations
- ✅ Momentum indicators (RSI, MACD)
- ✅ Volatility indicators (Bollinger Bands)
- ✅ Volume indicators (OBV)
- ✅ Support/resistance detection
- ✅ Trend analysis
- ✅ Pattern detection
- ✅ Error handling

### Recommendation Engine Coverage
- ✅ Engine initialization
- ✅ Analysis weights normalization
- ✅ Investment recommendation generation
- ✅ Strategy configuration loading
- ✅ Composite score calculation
- ✅ Risk assessment
- ✅ Position sizing
- ✅ Confidence calculation
- ✅ Batch recommendations
- ✅ Portfolio optimization
- ✅ Export functionality

### Integration Testing Coverage
- ✅ Sentiment + Chart analysis integration
- ✅ Complete recommendation workflow
- ✅ Strategy impact on recommendations
- ✅ Confidence correlation across components
- ✅ Risk assessment integration
- ✅ Portfolio construction
- ✅ Real-time analysis simulation
- ✅ Error recovery and robustness

## 🎯 Test Scenarios

### Market Scenarios Tested
- **Bull Market**: Upward trending data with positive sentiment
- **Bear Market**: Downward trending data with negative sentiment
- **Sideways Market**: Range-bound data with neutral sentiment
- **Volatile Market**: High volatility data with mixed signals

### News Sentiment Scenarios
- **Very Positive**: Record earnings, breakthroughs, upgrades
- **Positive**: Good earnings, analyst upgrades
- **Neutral**: Scheduled calls, market-following movements
- **Negative**: Earnings misses, downgrades
- **Very Negative**: Lawsuits, investigations, multiple downgrades

### Strategy Testing
- **Conservative Growth**: Lower risk tolerance, smaller positions
- **Aggressive Growth**: Higher risk tolerance, larger positions
- **Value Investing**: Focus on fundamentals and valuation
- **Balanced Growth**: Moderate approach across factors

## 🔧 Test Configuration

### Key Test Files
- `conftest.py` - Pytest configuration and fixtures
- `pytest.ini` - Test execution configuration
- `pyproject.toml` - Project and test metadata
- `run_tests.py` - Test runner script

### Test Data Generation
Tests use reproducible random data generation with fixed seeds for consistency:
- Price data with realistic OHLCV patterns
- News articles with varying sentiment
- Market scenarios with different volatility patterns

## 🚨 Troubleshooting

### Common Issues

**Import Errors:**
```
ModuleNotFoundError: No module named 'analysis.sentiment_analyzer'
```
**Solution:** Ensure Python path includes `src` directory:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'src'))
```

**Missing Dependencies:**
```
ModuleNotFoundError: No module named 'pytest'
```
**Solution:** Install test dependencies:
```bash
pip install pytest pytest-asyncio pandas numpy pyyaml
```

**Async Test Issues:**
```
RuntimeError: There is no current event loop
```
**Solution:** Tests use `pytest-asyncio` for async test support.

### Running Individual Tests

To run specific test methods:
```python
# Direct execution
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'src'))

from tests.analysis.test_sentiment_analyzer import TestFinancialSentimentAnalyzer
test = TestFinancialSentimentAnalyzer()
test.test_analyzer_initialization()
```

## 📈 Performance Expectations

### Test Execution Times
- **Unit Tests**: < 1 second per test
- **Integration Tests**: 1-5 seconds per test
- **Performance Tests**: 5-30 seconds per test
- **Full Suite**: 2-10 minutes total

### Memory Usage
- **Typical Test**: < 100MB RAM
- **Large Dataset Tests**: < 500MB RAM
- **Full Suite**: < 1GB RAM

## 🎛️ Test Customization

### Adding New Tests

1. Create test methods following naming convention `test_*`
2. Use appropriate fixtures for test data
3. Include both positive and negative test cases
4. Add error handling tests
5. Document expected behavior

### Test Data Customization

Modify fixtures in test files to customize:
- Price data patterns
- News sentiment scenarios
- Market volatility levels
- Strategy configurations

## 📋 Continuous Integration

The test suite is designed for CI/CD integration:
- Fast execution for quick feedback
- Comprehensive coverage for quality assurance
- Clear pass/fail indicators
- Detailed error reporting

## 🔍 Test Maintenance

### Regular Updates Required
- Update test data as market conditions change
- Add tests for new features and indicators
- Maintain compatibility with dependency updates
- Review and update performance benchmarks

### Quality Metrics
- **Code Coverage**: Aim for >90% coverage
- **Test Reliability**: <1% flaky test rate
- **Execution Speed**: <10 minute full suite
- **Maintenance Burden**: <5% test code to production code ratio

---

**The analysis engine test suite ensures robust, reliable, and accurate financial analysis capabilities for the Agent Investment Platform.** 🚀📊
