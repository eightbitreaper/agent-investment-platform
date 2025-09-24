#!/usr/bin/env python3
"""
Direct Platform Test Runner
Tests platform components without Docker dependencies
"""

import sys
import os
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_logging():
    """Setup logging for direct testing"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('logs/direct-test.log')
        ]
    )

def test_core_imports():
    """Test core platform imports"""
    print("Testing core imports...")
    try:
        from src.analysis.market_analyzer import MarketAnalyzer
        print("✓ MarketAnalyzer imported successfully")
    except Exception as e:
        print(f"✗ Failed to import MarketAnalyzer: {e}")
        
    try:
        from src.data.data_collector import DataCollector
        print("✓ DataCollector imported successfully")
    except Exception as e:
        print(f"✗ Failed to import DataCollector: {e}")
        
    try:
        from src.strategies.strategy_manager import StrategyManager
        print("✓ StrategyManager imported successfully")
    except Exception as e:
        print(f"✗ Failed to import StrategyManager: {e}")

def test_basic_functionality():
    """Test basic functionality without external dependencies"""
    print("\nTesting basic functionality...")
    
    try:
        # Test configuration loading
        from src.config.config_manager import ConfigManager
        config = ConfigManager()
        print("✓ Configuration loaded successfully")
        
        # Test strategy loading
        strategies = config.get_strategies()
        print(f"✓ Loaded {len(strategies)} investment strategies")
        
        # Test data directory creation
        os.makedirs("data", exist_ok=True)
        os.makedirs("reports", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        print("✓ Required directories verified")
        
        return True
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False

def test_market_data_access():
    """Test market data access with fallback providers"""
    print("\nTesting market data access...")
    
    try:
        from src.data.data_collector import DataCollector
        collector = DataCollector()
        
        # Test with a simple stock symbol
        test_symbol = "AAPL"
        print(f"Testing data collection for {test_symbol}...")
        
        # This might fail if no API keys are configured, but that's expected
        try:
            data = collector.get_stock_data(test_symbol, period="1d")
            print(f"✓ Successfully retrieved data for {test_symbol}")
            return True
        except Exception as e:
            print(f"⚠ Market data access failed (expected without API keys): {e}")
            return False
            
    except Exception as e:
        print(f"✗ Market data test failed: {e}")
        return False

def test_analysis_engine():
    """Test analysis engine with mock data"""
    print("\nTesting analysis engine...")
    
    try:
        from src.analysis.market_analyzer import MarketAnalyzer
        analyzer = MarketAnalyzer()
        
        # Test basic analysis functions
        print("✓ MarketAnalyzer initialized successfully")
        
        # Test strategy loading
        from src.strategies.strategy_manager import StrategyManager
        strategy_manager = StrategyManager()
        strategies = strategy_manager.get_available_strategies()
        print(f"✓ Loaded {len(strategies)} strategies")
        
        return True
    except Exception as e:
        print(f"✗ Analysis engine test failed: {e}")
        return False

def main():
    """Run direct platform tests"""
    print("=" * 60)
    print("DIRECT PLATFORM TEST RUNNER")
    print("Testing core functionality without Docker")
    print("=" * 60)
    
    setup_logging()
    
    # Run tests
    results = []
    
    print("\n1. Core Imports Test")
    test_core_imports()
    
    print("\n2. Basic Functionality Test")
    results.append(test_basic_functionality())
    
    print("\n3. Market Data Access Test")
    results.append(test_market_data_access())
    
    print("\n4. Analysis Engine Test")
    results.append(test_analysis_engine())
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed! Core platform is working.")
        print("🚀 Ready for Docker deployment!")
    elif passed >= total // 2:
        print("⚠ Most tests passed. Platform is mostly functional.")
        print("🔧 Some components may need configuration.")
    else:
        print("✗ Many tests failed. Platform needs attention.")
        print("🔍 Check logs for detailed error information.")
    
    print("\nNext steps:")
    print("1. Configure API keys in .env file")
    print("2. Fix Docker Desktop connectivity")
    print("3. Deploy full Docker stack")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)