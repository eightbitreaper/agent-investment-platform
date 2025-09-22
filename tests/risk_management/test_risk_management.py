"""
Test suite for Risk Management Framework

This module contains comprehensive unit tests, integration tests, and scenario-based
validation tests for the risk management system.

Test Categories:
- Unit tests for individual risk calculation functions
- Integration tests with backtesting framework
- Scenario-based risk validation testing
- Configuration loading and validation tests
- Alert system and monitoring tests
"""

import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import tempfile
import os

# Import risk management modules
from src.risk_management import (
    RiskEngine, PositionSizingMethod, RiskMetrics, RiskLimits,
    StopLossManager, StopLossMethod, TakeProfitMethod,
    PortfolioMonitor, AlertLevel, RiskAlert,
    RiskConfigManager, MarketRegime, RiskProfile
)

class TestRiskEngine:
    """Test cases for the RiskEngine class"""

    @pytest.fixture
    def risk_engine(self):
        """Create a RiskEngine instance for testing"""
        return RiskEngine()

    @pytest.fixture
    def sample_returns(self):
        """Generate sample return data for testing"""
        np.random.seed(42)
        dates = pd.date_range('2023-01-01', periods=252, freq='D')
        returns = pd.Series(np.random.normal(0.001, 0.02, 252), index=dates)
        return returns

    @pytest.fixture
    def sample_portfolio_data(self):
        """Sample portfolio data for testing"""
        return {
            'positions': {'AAPL': 10000, 'GOOGL': 8000, 'MSFT': 7000},
            'portfolio_value': 25000,
            'current_prices': {'AAPL': 150.0, 'GOOGL': 2800.0, 'MSFT': 280.0}
        }

    def test_risk_engine_initialization(self, risk_engine):
        """Test RiskEngine initialization"""
        assert risk_engine is not None
        assert risk_engine.lookback_period == 252
        assert isinstance(risk_engine.risk_limits, RiskLimits)
        assert risk_engine.risk_free_rate == 0.02

    def test_kelly_position_sizing(self, risk_engine, sample_returns):
        """Test Kelly Criterion position sizing"""
        recommendation = risk_engine.calculate_position_size(
            symbol='AAPL',
            current_price=150.0,
            portfolio_value=100000,
            method=PositionSizingMethod.KELLY,
            historical_returns=sample_returns
        )

        assert recommendation.symbol == 'AAPL'
        assert recommendation.sizing_method == 'kelly'
        assert recommendation.recommended_size > 0
        assert recommendation.confidence > 0
        assert recommendation.risk_contribution > 0

    def test_risk_parity_position_sizing(self, risk_engine, sample_returns):
        """Test Risk Parity position sizing"""
        recommendation = risk_engine.calculate_position_size(
            symbol='AAPL',
            current_price=150.0,
            portfolio_value=100000,
            method=PositionSizingMethod.RISK_PARITY,
            historical_returns=sample_returns
        )

        assert recommendation.symbol == 'AAPL'
        assert recommendation.sizing_method == 'risk_parity'
        assert recommendation.recommended_size > 0
        assert recommendation.confidence == 0.8

    def test_volatility_based_position_sizing(self, risk_engine, sample_returns):
        """Test volatility-based position sizing"""
        recommendation = risk_engine.calculate_position_size(
            symbol='AAPL',
            current_price=150.0,
            portfolio_value=100000,
            method=PositionSizingMethod.VOLATILITY_BASED,
            historical_returns=sample_returns
        )

        assert recommendation.symbol == 'AAPL'
        assert recommendation.sizing_method == 'volatility_based'
        assert recommendation.recommended_size > 0
        assert recommendation.confidence == 0.75

    def test_fixed_fractional_position_sizing(self, risk_engine):
        """Test fixed fractional position sizing"""
        recommendation = risk_engine.calculate_position_size(
            symbol='AAPL',
            current_price=150.0,
            portfolio_value=100000,
            method=PositionSizingMethod.FIXED_FRACTIONAL,
            fraction=0.03
        )

        assert recommendation.symbol == 'AAPL'
        assert recommendation.sizing_method == 'fixed_fractional'
        assert recommendation.recommended_size == 20.0  # 3000 / 150
        assert recommendation.confidence == 1.0

    def test_portfolio_risk_calculation(self, risk_engine, sample_portfolio_data):
        """Test portfolio risk metrics calculation"""
        # Create mock historical returns
        np.random.seed(42)
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        historical_returns = {
            'AAPL': pd.Series(np.random.normal(0.001, 0.02, 100), index=dates),
            'GOOGL': pd.Series(np.random.normal(0.0008, 0.025, 100), index=dates),
            'MSFT': pd.Series(np.random.normal(0.0012, 0.018, 100), index=dates)
        }

        risk_metrics = risk_engine.calculate_portfolio_risk(
            portfolio_positions=sample_portfolio_data['positions'],
            historical_returns=historical_returns,
            portfolio_value=sample_portfolio_data['portfolio_value']
        )

        assert isinstance(risk_metrics, RiskMetrics)
        assert risk_metrics.portfolio_var_95 >= 0
        assert risk_metrics.portfolio_var_99 >= 0
        assert risk_metrics.portfolio_volatility >= 0
        assert 1 <= risk_metrics.risk_score <= 10

    def test_risk_limits_checking(self, risk_engine, sample_portfolio_data):
        """Test risk limits validation"""
        results = risk_engine.check_risk_limits(
            portfolio_positions=sample_portfolio_data['positions'],
            portfolio_value=sample_portfolio_data['portfolio_value']
        )

        assert 'within_limits' in results
        assert 'violations' in results
        assert 'warnings' in results
        assert 'recommendations' in results
        assert isinstance(results['within_limits'], bool)

    def test_insufficient_data_handling(self, risk_engine):
        """Test handling of insufficient historical data"""
        # Create very short returns series
        short_returns = pd.Series([0.01, -0.02, 0.005])

        recommendation = risk_engine.calculate_position_size(
            symbol='AAPL',
            current_price=150.0,
            portfolio_value=100000,
            method=PositionSizingMethod.KELLY,
            historical_returns=short_returns
        )

        # Should fallback to safe sizing
        assert recommendation.sizing_method == 'fallback'
        assert len(recommendation.warnings) > 0

class TestStopLossManager:
    """Test cases for the StopLossManager class"""

    @pytest.fixture
    def stop_loss_manager(self):
        """Create a StopLossManager instance for testing"""
        return StopLossManager()

    @pytest.fixture
    def sample_price_data(self):
        """Generate sample OHLCV price data"""
        np.random.seed(42)
        dates = pd.date_range('2023-01-01', periods=100, freq='D')

        # Generate realistic OHLCV data
        close_prices = 100 + np.cumsum(np.random.normal(0, 2, 100))
        high_prices = close_prices + np.random.uniform(0, 3, 100)
        low_prices = close_prices - np.random.uniform(0, 3, 100)
        open_prices = close_prices + np.random.uniform(-2, 2, 100)
        volume = np.random.uniform(1000000, 5000000, 100)

        return pd.DataFrame({
            'open': open_prices,
            'high': high_prices,
            'low': low_prices,
            'close': close_prices,
            'volume': volume
        }, index=dates)

    def test_atr_based_stop_loss(self, stop_loss_manager, sample_price_data):
        """Test ATR-based stop-loss calculation"""
        stop_loss = stop_loss_manager.calculate_stop_loss(
            symbol='AAPL',
            entry_price=150.0,
            direction='long',
            method=StopLossMethod.ATR_BASED,
            price_data=sample_price_data
        )

        assert stop_loss.symbol == 'AAPL'
        assert stop_loss.method == 'atr_based'
        assert stop_loss.stop_price < 150.0  # Long position stop should be below entry
        assert stop_loss.stop_percentage > 0
        assert stop_loss.confidence == 0.8
        assert stop_loss.dynamic_adjustment is True

    def test_percentage_based_stop_loss(self, stop_loss_manager):
        """Test percentage-based stop-loss calculation"""
        stop_loss = stop_loss_manager.calculate_stop_loss(
            symbol='AAPL',
            entry_price=150.0,
            direction='long',
            method=StopLossMethod.PERCENTAGE_BASED,
            stop_percentage=0.05
        )

        assert stop_loss.symbol == 'AAPL'
        assert stop_loss.method == 'percentage_based'
        assert stop_loss.stop_price == 142.5  # 150 * (1 - 0.05)
        assert stop_loss.stop_percentage == 0.05
        assert stop_loss.confidence == 1.0

    def test_trailing_stop_loss(self, stop_loss_manager, sample_price_data):
        """Test trailing stop-loss calculation"""
        stop_loss = stop_loss_manager.calculate_stop_loss(
            symbol='AAPL',
            entry_price=150.0,
            direction='long',
            method=StopLossMethod.TRAILING_STOP,
            price_data=sample_price_data,
            trail_percentage=0.05
        )

        assert stop_loss.symbol == 'AAPL'
        assert stop_loss.method == 'trailing_stop'
        assert stop_loss.dynamic_adjustment is True
        assert stop_loss.trailing_activation is not None

    def test_risk_reward_take_profit(self, stop_loss_manager):
        """Test risk-reward ratio take-profit calculation"""
        take_profit = stop_loss_manager.calculate_take_profit(
            symbol='AAPL',
            entry_price=150.0,
            direction='long',
            method=TakeProfitMethod.RISK_REWARD_RATIO,
            stop_loss_price=142.5,
            target_ratio=2.0
        )

        assert take_profit.symbol == 'AAPL'
        assert take_profit.method == 'risk_reward_ratio'
        assert take_profit.target_price == 165.0  # 150 + (150-142.5)*2
        assert take_profit.risk_reward_ratio == 2.0
        assert take_profit.confidence == 0.8

    def test_comprehensive_risk_reward_calculation(self, stop_loss_manager, sample_price_data):
        """Test comprehensive risk-reward recommendation"""
        recommendation = stop_loss_manager.calculate_risk_reward(
            symbol='AAPL',
            entry_price=150.0,
            direction='long',
            stop_method=StopLossMethod.ATR_BASED,
            profit_method=TakeProfitMethod.RISK_REWARD_RATIO,
            price_data=sample_price_data
        )

        assert recommendation.symbol == 'AAPL'
        assert recommendation.entry_price == 150.0
        assert recommendation.stop_loss.symbol == 'AAPL'
        assert recommendation.take_profit.symbol == 'AAPL'
        assert recommendation.risk_reward_ratio > 0
        assert 0 <= recommendation.position_score <= 10

    def test_trailing_stop_update(self, stop_loss_manager):
        """Test trailing stop update mechanism"""
        # Test long position trailing stop update
        new_stop = stop_loss_manager.update_trailing_stop(
            symbol='AAPL',
            current_price=160.0,
            entry_price=150.0,
            current_stop=140.0,
            direction='long',
            trail_percentage=0.05
        )

        assert new_stop is not None
        assert new_stop > 140.0  # Should move stop up
        assert new_stop == 152.0  # 160 * (1 - 0.05)

    def test_short_position_stops(self, stop_loss_manager):
        """Test stop-loss calculations for short positions"""
        stop_loss = stop_loss_manager.calculate_stop_loss(
            symbol='AAPL',
            entry_price=150.0,
            direction='short',
            method=StopLossMethod.PERCENTAGE_BASED,
            stop_percentage=0.05
        )

        assert stop_loss.stop_price == 157.5  # 150 * (1 + 0.05) for short

        take_profit = stop_loss_manager.calculate_take_profit(
            symbol='AAPL',
            entry_price=150.0,
            direction='short',
            method=TakeProfitMethod.RISK_REWARD_RATIO,
            stop_loss_price=157.5,
            target_ratio=2.0
        )

        assert take_profit.target_price == 135.0  # 150 - (157.5-150)*2

class TestPortfolioMonitor:
    """Test cases for the PortfolioMonitor class"""

    @pytest.fixture
    def portfolio_monitor(self):
        """Create a PortfolioMonitor instance for testing"""
        return PortfolioMonitor()

    @pytest.fixture
    def sample_monitoring_data(self):
        """Sample data for portfolio monitoring tests"""
        np.random.seed(42)
        dates = pd.date_range('2023-01-01', periods=60, freq='D')

        return {
            'portfolio_positions': {'AAPL': 15000, 'GOOGL': 12000, 'MSFT': 8000},
            'portfolio_value': 35000,
            'current_prices': {'AAPL': 150.0, 'GOOGL': 2800.0, 'MSFT': 280.0},
            'historical_returns': {
                'AAPL': pd.Series(np.random.normal(0.001, 0.02, 60), index=dates),
                'GOOGL': pd.Series(np.random.normal(0.0008, 0.025, 60), index=dates),
                'MSFT': pd.Series(np.random.normal(0.0012, 0.018, 60), index=dates)
            },
            'cash_balance': 5000
        }

    def test_portfolio_monitoring(self, portfolio_monitor, sample_monitoring_data):
        """Test comprehensive portfolio monitoring"""
        snapshot, alerts = portfolio_monitor.monitor_portfolio(
            portfolio_positions=sample_monitoring_data['portfolio_positions'],
            portfolio_value=sample_monitoring_data['portfolio_value'],
            current_prices=sample_monitoring_data['current_prices'],
            historical_returns=sample_monitoring_data['historical_returns'],
            cash_balance=sample_monitoring_data['cash_balance']
        )

        # Verify snapshot
        assert snapshot.total_value == sample_monitoring_data['portfolio_value']
        assert snapshot.cash == sample_monitoring_data['cash_balance']
        assert snapshot.var_95 >= 0
        assert snapshot.var_99 >= 0
        assert 1 <= snapshot.risk_score <= 10

        # Alerts should be a list
        assert isinstance(alerts, list)

    def test_concentration_risk_alert(self, portfolio_monitor):
        """Test concentration risk alert generation"""
        # Create portfolio with high concentration
        high_concentration_positions = {'AAPL': 25000}  # 100% concentration

        snapshot, alerts = portfolio_monitor.monitor_portfolio(
            portfolio_positions=high_concentration_positions,
            portfolio_value=25000,
            current_prices={'AAPL': 150.0},
            historical_returns={'AAPL': pd.Series([0.01, -0.02, 0.005])},
            cash_balance=0
        )

        # Should generate concentration risk alerts
        concentration_alerts = [a for a in alerts if a.alert_type == RiskAlert.CONCENTRATION_RISK]
        assert len(concentration_alerts) > 0

        # Check alert properties
        alert = concentration_alerts[0]
        assert alert.symbol == 'AAPL'
        assert alert.current_value > alert.threshold_value

    def test_liquidity_risk_alert(self, portfolio_monitor):
        """Test liquidity risk alert generation"""
        snapshot, alerts = portfolio_monitor.monitor_portfolio(
            portfolio_positions={'AAPL': 10000},
            portfolio_value=10000,
            current_prices={'AAPL': 150.0},
            historical_returns={'AAPL': pd.Series([0.01, -0.02, 0.005])},
            cash_balance=0  # No cash - liquidity risk
        )

        # Should generate liquidity risk alerts
        liquidity_alerts = [a for a in alerts if a.alert_type == RiskAlert.LIQUIDITY_RISK]
        assert len(liquidity_alerts) > 0

    def test_alert_cooldown(self, portfolio_monitor):
        """Test alert cooldown mechanism"""
        # Generate same alert twice in quick succession
        portfolio_data = {
            'portfolio_positions': {'AAPL': 25000},
            'portfolio_value': 25000,
            'current_prices': {'AAPL': 150.0},
            'historical_returns': {'AAPL': pd.Series([0.01, -0.02, 0.005])},
            'cash_balance': 0
        }

        # First monitoring call
        snapshot1, alerts1 = portfolio_monitor.monitor_portfolio(**portfolio_data)

        # Second monitoring call immediately after
        snapshot2, alerts2 = portfolio_monitor.monitor_portfolio(**portfolio_data)

        # Second call should have fewer alerts due to cooldown
        assert len(alerts2) <= len(alerts1)

    def test_portfolio_summary(self, portfolio_monitor, sample_monitoring_data):
        """Test portfolio summary generation"""
        # First create some monitoring data
        snapshot, alerts = portfolio_monitor.monitor_portfolio(
            **sample_monitoring_data
        )

        summary = portfolio_monitor.get_portfolio_summary()

        assert 'timestamp' in summary
        assert 'total_value' in summary
        assert 'risk_metrics' in summary
        assert 'positions' in summary
        assert 'active_alerts' in summary

    def test_risk_heatmap_data(self, portfolio_monitor, sample_monitoring_data):
        """Test risk heatmap data generation"""
        # Create monitoring data first
        snapshot, alerts = portfolio_monitor.monitor_portfolio(
            **sample_monitoring_data
        )

        heatmap_data = portfolio_monitor.get_risk_heatmap_data()

        assert 'positions' in heatmap_data
        assert 'portfolio_metrics' in heatmap_data
        assert len(heatmap_data['positions']) > 0

        # Check position data structure
        position = heatmap_data['positions'][0]
        assert 'symbol' in position
        assert 'value' in position
        assert 'weight' in position
        assert 'risk_level' in position

class TestRiskConfigManager:
    """Test cases for the RiskConfigManager class"""

    @pytest.fixture
    def temp_config_file(self):
        """Create a temporary config file for testing"""
        config_data = {
            'global_risk': {
                'max_portfolio_risk': 0.02,
                'max_position_size': 0.05,
                'max_drawdown': 0.15
            },
            'strategies': {
                'test_strategy': {
                    'max_portfolio_risk': 0.025,
                    'position_sizing_method': 'kelly',
                    'stop_loss_method': 'atr_based'
                }
            },
            'position_sizing': {
                'default_method': 'volatility_based'
            }
        }

        # Create temporary file
        import yaml
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        yaml.dump(config_data, temp_file, default_flow_style=False)
        temp_file.close()

        yield temp_file.name

        # Cleanup
        os.unlink(temp_file.name)

    def test_config_loading(self, temp_config_file):
        """Test configuration loading from YAML file"""
        config_manager = RiskConfigManager(config_path=temp_config_file)

        assert config_manager.config_data is not None
        assert config_manager.global_config is not None
        assert len(config_manager.strategy_configs) > 0
        assert 'test_strategy' in config_manager.strategy_configs

    def test_global_config_access(self, temp_config_file):
        """Test global configuration access"""
        config_manager = RiskConfigManager(config_path=temp_config_file)
        global_config = config_manager.get_global_config()

        assert global_config.max_portfolio_risk == 0.02
        assert global_config.max_position_size == 0.05
        assert global_config.max_drawdown == 0.15

    def test_strategy_config_access(self, temp_config_file):
        """Test strategy-specific configuration access"""
        config_manager = RiskConfigManager(config_path=temp_config_file)
        strategy_config = config_manager.get_strategy_config('test_strategy')

        assert strategy_config.strategy_name == 'test_strategy'
        assert strategy_config.max_portfolio_risk == 0.025
        assert strategy_config.position_sizing_method == 'kelly'
        assert strategy_config.stop_loss_method == 'atr_based'

    def test_nonexistent_strategy_config(self, temp_config_file):
        """Test handling of non-existent strategy configuration"""
        config_manager = RiskConfigManager(config_path=temp_config_file)
        strategy_config = config_manager.get_strategy_config('nonexistent_strategy')

        # Should return default config
        assert strategy_config.strategy_name == 'nonexistent_strategy'
        assert strategy_config.max_portfolio_risk == 0.02  # Default value

    def test_market_regime_application(self, temp_config_file):
        """Test market regime adjustment application"""
        # Add market regime config to temp file
        import yaml
        with open(temp_config_file, 'r') as f:
            config_data = yaml.safe_load(f)

        config_data['market_regimes'] = {
            'bull_market': {
                'risk_multiplier': 1.2,
                'position_size_multiplier': 1.1
            }
        }

        with open(temp_config_file, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False)

        config_manager = RiskConfigManager(config_path=temp_config_file)
        global_config = config_manager.get_global_config()
        original_risk = global_config.max_portfolio_risk

        # Apply bull market regime
        success = config_manager.apply_market_regime(MarketRegime.BULL_MARKET)

        assert success is True
        assert config_manager.current_regime == MarketRegime.BULL_MARKET
        # Risk should be increased by multiplier
        updated_global_config = config_manager.get_global_config()
        assert updated_global_config.max_portfolio_risk > original_risk

    def test_config_validation(self, temp_config_file):
        """Test configuration validation"""
        config_manager = RiskConfigManager(config_path=temp_config_file)
        validation_results = config_manager.validate_configuration()

        assert 'errors' in validation_results
        assert 'warnings' in validation_results
        assert isinstance(validation_results['errors'], list)
        assert isinstance(validation_results['warnings'], list)

    def test_strategy_config_update(self, temp_config_file):
        """Test dynamic strategy configuration updates"""
        config_manager = RiskConfigManager(config_path=temp_config_file)

        updates = {
            'max_portfolio_risk': 0.03,
            'target_risk_reward': 2.5,
            'custom_param': 'test_value'
        }

        success = config_manager.update_strategy_config('test_strategy', updates)
        assert success is True

        # Verify updates
        updated_config = config_manager.get_strategy_config('test_strategy')
        assert updated_config.max_portfolio_risk == 0.03
        assert updated_config.target_risk_reward == 2.5
        assert updated_config.custom_params['custom_param'] == 'test_value'

    def test_settings_summary(self, temp_config_file):
        """Test current settings summary"""
        config_manager = RiskConfigManager(config_path=temp_config_file)
        summary = config_manager.get_current_settings_summary()

        assert 'config_path' in summary
        assert 'current_regime' in summary
        assert 'current_profile' in summary
        assert 'global_config' in summary
        assert 'strategy_count' in summary
        assert 'strategies' in summary

class TestIntegrationScenarios:
    """Integration tests and scenario-based validation"""

    @pytest.fixture
    def integrated_system(self):
        """Create an integrated risk management system for testing"""
        config_manager = RiskConfigManager()
        risk_engine = RiskEngine()
        stop_loss_manager = StopLossManager()
        portfolio_monitor = PortfolioMonitor()

        return {
            'config_manager': config_manager,
            'risk_engine': risk_engine,
            'stop_loss_manager': stop_loss_manager,
            'portfolio_monitor': portfolio_monitor
        }

    def test_complete_risk_workflow(self, integrated_system):
        """Test complete risk management workflow"""
        # Setup test data
        np.random.seed(42)
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        historical_returns = {
            'AAPL': pd.Series(np.random.normal(0.001, 0.02, 100), index=dates),
            'GOOGL': pd.Series(np.random.normal(0.0008, 0.025, 100), index=dates)
        }

        portfolio_positions = {'AAPL': 50000, 'GOOGL': 40000}
        portfolio_value = 90000
        current_prices = {'AAPL': 150.0, 'GOOGL': 2800.0}

        # 1. Calculate position sizes
        risk_engine = integrated_system['risk_engine']
        aapl_sizing = risk_engine.calculate_position_size(
            symbol='AAPL',
            current_price=current_prices['AAPL'],
            portfolio_value=portfolio_value,
            method=PositionSizingMethod.VOLATILITY_BASED,
            historical_returns=historical_returns['AAPL']
        )

        assert aapl_sizing.recommended_size > 0

        # 2. Calculate stop-loss and take-profit
        stop_loss_manager = integrated_system['stop_loss_manager']

        # Generate sample price data
        close_prices = 150 + np.cumsum(np.random.normal(0, 2, 50))
        price_data = pd.DataFrame({
            'open': close_prices + np.random.uniform(-2, 2, 50),
            'high': close_prices + np.random.uniform(0, 3, 50),
            'low': close_prices - np.random.uniform(0, 3, 50),
            'close': close_prices,
            'volume': np.random.uniform(1000000, 5000000, 50)
        })

        risk_reward = stop_loss_manager.calculate_risk_reward(
            symbol='AAPL',
            entry_price=150.0,
            direction='long',
            price_data=price_data
        )

        assert risk_reward.risk_reward_ratio > 0
        assert risk_reward.position_score > 0

        # 3. Monitor portfolio
        portfolio_monitor = integrated_system['portfolio_monitor']
        snapshot, alerts = portfolio_monitor.monitor_portfolio(
            portfolio_positions=portfolio_positions,
            portfolio_value=portfolio_value,
            current_prices=current_prices,
            historical_returns=historical_returns,
            cash_balance=10000
        )

        assert snapshot.total_value == portfolio_value
        assert isinstance(alerts, list)

        # 4. Check portfolio risk metrics
        portfolio_risk = risk_engine.calculate_portfolio_risk(
            portfolio_positions=portfolio_positions,
            historical_returns=historical_returns,
            portfolio_value=portfolio_value
        )

        assert portfolio_risk.portfolio_var_95 >= 0
        assert portfolio_risk.risk_score >= 1

    def test_stress_scenario_high_volatility(self, integrated_system):
        """Test system behavior under high volatility scenario"""
        # Create high volatility returns
        np.random.seed(42)
        dates = pd.date_range('2023-01-01', periods=60, freq='D')
        high_vol_returns = {
            'AAPL': pd.Series(np.random.normal(0, 0.05, 60), index=dates),  # 5% daily volatility
            'MSFT': pd.Series(np.random.normal(0, 0.06, 60), index=dates)   # 6% daily volatility
        }

        risk_engine = integrated_system['risk_engine']

        # Test position sizing under high volatility
        aapl_sizing = risk_engine.calculate_position_size(
            symbol='AAPL',
            current_price=150.0,
            portfolio_value=100000,
            method=PositionSizingMethod.VOLATILITY_BASED,
            historical_returns=high_vol_returns['AAPL']
        )

        # Position size should be smaller due to high volatility
        assert aapl_sizing.recommended_size > 0
        assert aapl_sizing.risk_contribution < 0.05  # Should be conservative

        # Test portfolio monitoring under high volatility
        portfolio_monitor = integrated_system['portfolio_monitor']
        snapshot, alerts = portfolio_monitor.monitor_portfolio(
            portfolio_positions={'AAPL': 30000, 'MSFT': 25000},
            portfolio_value=55000,
            current_prices={'AAPL': 150.0, 'MSFT': 280.0},
            historical_returns=high_vol_returns,
            cash_balance=5000
        )

        # Should generate risk alerts due to high volatility
        assert snapshot.risk_score >= 5  # Higher risk score expected

    def test_crash_scenario(self, integrated_system):
        """Test system behavior during market crash scenario"""
        # Create crash scenario returns (large negative returns)
        np.random.seed(42)
        dates = pd.date_range('2023-01-01', periods=30, freq='D')

        # First 20 days normal, then 10 days of crash
        normal_returns = np.random.normal(0.001, 0.02, 20)
        crash_returns = np.random.normal(-0.05, 0.03, 10)  # -5% daily average

        crash_scenario_returns = {
            'AAPL': pd.Series(np.concatenate([normal_returns, crash_returns]), index=dates),
            'MSFT': pd.Series(np.concatenate([normal_returns, crash_returns]), index=dates)
        }

        portfolio_monitor = integrated_system['portfolio_monitor']

        # Monitor during crash
        snapshot, alerts = portfolio_monitor.monitor_portfolio(
            portfolio_positions={'AAPL': 40000, 'MSFT': 35000},
            portfolio_value=75000,
            current_prices={'AAPL': 120.0, 'MSFT': 220.0},  # Lower prices
            historical_returns=crash_scenario_returns,
            cash_balance=2000,
            previous_value=85000  # Portfolio lost value
        )

        # Should have negative P&L and high risk score
        assert snapshot.daily_pnl < 0
        assert snapshot.risk_score >= 7  # High risk during crash

        # Should generate multiple alerts
        assert len(alerts) > 0

        # Check for specific alert types
        alert_types = [alert.alert_type for alert in alerts]
        assert RiskAlert.VAR_BREACH in alert_types or RiskAlert.DRAWDOWN_LIMIT in alert_types

# Performance benchmarking tests
class TestPerformanceBenchmarks:
    """Performance and benchmark tests for risk management system"""

    def test_risk_calculation_performance(self):
        """Test performance of risk calculations with large datasets"""
        import time

        # Create large dataset
        np.random.seed(42)
        dates = pd.date_range('2020-01-01', periods=1000, freq='D')
        large_returns = pd.Series(np.random.normal(0.001, 0.02, 1000), index=dates)

        risk_engine = RiskEngine()

        # Time the calculation
        start_time = time.time()

        for _ in range(100):  # Run 100 times
            recommendation = risk_engine.calculate_position_size(
                symbol='AAPL',
                current_price=150.0,
                portfolio_value=100000,
                method=PositionSizingMethod.KELLY,
                historical_returns=large_returns
            )

        end_time = time.time()
        avg_time = (end_time - start_time) / 100

        # Should complete within reasonable time (< 0.1 seconds per calculation)
        assert avg_time < 0.1
        assert recommendation.recommended_size > 0

    def test_monitoring_scalability(self):
        """Test portfolio monitoring scalability with many positions"""
        import time

        # Create portfolio with many positions
        num_positions = 50
        portfolio_positions = {f'STOCK_{i}': np.random.uniform(1000, 10000)
                             for i in range(num_positions)}
        portfolio_value = sum(portfolio_positions.values())

        # Create historical returns for all positions
        np.random.seed(42)
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        historical_returns = {}
        for symbol in portfolio_positions.keys():
            historical_returns[symbol] = pd.Series(
                np.random.normal(0.001, 0.02, 100), index=dates
            )

        current_prices = {symbol: np.random.uniform(50, 200)
                         for symbol in portfolio_positions.keys()}

        portfolio_monitor = PortfolioMonitor()

        # Time the monitoring
        start_time = time.time()

        snapshot, alerts = portfolio_monitor.monitor_portfolio(
            portfolio_positions=portfolio_positions,
            portfolio_value=portfolio_value,
            current_prices=current_prices,
            historical_returns=historical_returns,
            cash_balance=5000
        )

        end_time = time.time()
        calculation_time = end_time - start_time

        # Should handle large portfolios efficiently (< 2 seconds)
        assert calculation_time < 2.0
        assert snapshot.total_value == portfolio_value
        assert len(snapshot.positions) == num_positions

if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])
