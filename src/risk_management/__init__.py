"""
Risk Management Module

This module provides comprehensive risk management capabilities for the investment platform.

Components:
- RiskEngine: Core risk calculations and position sizing
- StopLossManager: Dynamic stop-loss and take-profit management
- PortfolioMonitor: Real-time portfolio risk monitoring
- ConfigManager: Risk configuration management

Key Features:
- Multiple position sizing algorithms (Kelly Criterion, Risk Parity, Volatility-based)
- Portfolio risk metrics (VaR, Expected Shortfall, Maximum Drawdown)
- Dynamic stop-loss and take-profit strategies
- Real-time risk monitoring and alerting
- Flexible configuration system
"""

from .risk_engine import (
    RiskEngine,
    PositionSizingMethod,
    RiskLevel,
    RiskMetrics,
    PositionSizeRecommendation,
    RiskLimits
)

from .stop_loss_manager import (
    StopLossManager,
    StopLossMethod,
    TakeProfitMethod,
    StopLossLevel,
    TakeProfitLevel,
    RiskRewardRecommendation,
    StopLossConfig
)

from .portfolio_monitor import (
    PortfolioMonitor,
    AlertLevel,
    RiskAlert,
    RiskAlertMessage,
    PortfolioSnapshot,
    MonitoringConfig
)

from .config_manager import (
    RiskConfigManager,
    MarketRegime,
    RiskProfile,
    StrategyRiskConfig,
    GlobalRiskConfig
)

__all__ = [
    # Risk Engine
    'RiskEngine',
    'PositionSizingMethod',
    'RiskLevel',
    'RiskMetrics',
    'PositionSizeRecommendation',
    'RiskLimits',

    # Stop Loss Manager
    'StopLossManager',
    'StopLossMethod',
    'TakeProfitMethod',
    'StopLossLevel',
    'TakeProfitLevel',
    'RiskRewardRecommendation',
    'StopLossConfig',

    # Portfolio Monitor
    'PortfolioMonitor',
    'AlertLevel',
    'RiskAlert',
    'RiskAlertMessage',
    'PortfolioSnapshot',
    'MonitoringConfig',

    # Config Manager
    'RiskConfigManager',
    'MarketRegime',
    'RiskProfile',
    'StrategyRiskConfig',
    'GlobalRiskConfig'
]

__version__ = '1.0.0'
