"""
Backtesting Framework for the Agent Investment Platform.

This module provides comprehensive backtesting capabilities including:
- Backtesting engine for strategy performance validation
- Performance analysis and risk metrics calculation  
- Data management for historical market data
- Comprehensive reporting and visualization

Key Components:
- BacktestEngine: Core backtesting simulation engine
- PerformanceAnalyzer: Advanced performance metrics and analysis
- DataManager: Historical data fetching and management
"""

from .backtest_engine import (
    BacktestEngine,
    BacktestConfig,
    BacktestResult,
    BacktestStatus,
    Trade,
    PortfolioSnapshot,
    RiskMetrics,
    OrderType,
    create_sample_backtest_config,
    run_strategy_backtest
)

from .data_manager import (
    DataManager,
    DataSource,
    DataQuality,
    DataSourceConfig,
    DataQualityReport,
    MarketDataPoint,
    create_sample_data_manager,
    generate_backtest_dataset
)

# Note: PerformanceAnalyzer imports commented out due to missing dependencies
# from .performance_analyzer import (
#     PerformanceAnalyzer,
#     PerformanceReport,
#     PerformanceCategory,
#     BenchmarkComparison,
#     PerformanceAttribution,
#     RiskAnalysis,
#     compare_strategies,
#     generate_executive_summary
# )

__all__ = [
    # Core backtesting
    'BacktestEngine',
    'BacktestConfig', 
    'BacktestResult',
    'BacktestStatus',
    'Trade',
    'PortfolioSnapshot',
    'RiskMetrics',
    'OrderType',
    'create_sample_backtest_config',
    'run_strategy_backtest',
    
    # Data management
    'DataManager',
    'DataSource',
    'DataQuality',
    'DataSourceConfig', 
    'DataQualityReport',
    'MarketDataPoint',
    'create_sample_data_manager',
    'generate_backtest_dataset',
    
    # Performance analysis (commented out for now)
    # 'PerformanceAnalyzer',
    # 'PerformanceReport',
    # 'PerformanceCategory',
    # 'BenchmarkComparison',
    # 'PerformanceAttribution', 
    # 'RiskAnalysis',
    # 'compare_strategies',
    # 'generate_executive_summary'
]

# Version information
__version__ = "1.0.0"
__author__ = "Agent Investment Platform Team"
__description__ = "Comprehensive backtesting framework for investment strategies"