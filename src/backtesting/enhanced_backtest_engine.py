"""
Enhanced Backtesting Engine with Risk Management Integration

This enhanced version of the BacktestEngine integrates the comprehensive Risk Management
Framework to provide institutional-grade backtesting with advanced position sizing,
stop-loss management, and portfolio risk monitoring.

Key Enhancements:
- Integration with RiskEngine for sophisticated position sizing algorithms
- Dynamic stop-loss and take-profit management via StopLossManager
- Real-time portfolio risk monitoring during backtests
- Risk-adjusted performance metrics and reporting
- Configuration-driven risk parameter management
"""

import asyncio
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import yaml

# Import existing backtesting components
try:
    from .backtest_engine import BacktestEngine, BacktestConfig, Trade, PortfolioSnapshot
    from ..analysis.recommendation_engine import RecommendationEngine, InvestmentRecommendation, RecommendationType
    from ..analysis.sentiment_analyzer import FinancialSentimentAnalyzer
    from ..analysis.chart_analyzer import TechnicalChartAnalyzer
    # Import risk management components
    from ..risk_management import (
        RiskEngine, PositionSizingMethod, RiskLimits,
        StopLossManager, StopLossMethod, TakeProfitMethod,
        PortfolioMonitor, AlertLevel, RiskAlert,
        RiskConfigManager, MarketRegime, RiskProfile
    )
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from backtesting.backtest_engine import BacktestEngine, BacktestConfig, Trade, PortfolioSnapshot
    from analysis.recommendation_engine import RecommendationEngine, InvestmentRecommendation, RecommendationType
    from analysis.sentiment_analyzer import FinancialSentimentAnalyzer
    from analysis.chart_analyzer import TechnicalChartAnalyzer
    from risk_management import (
        RiskEngine, PositionSizingMethod, RiskLimits,
        StopLossManager, StopLossMethod, TakeProfitMethod,
        PortfolioMonitor, AlertLevel, RiskAlert,
        RiskConfigManager, MarketRegime, RiskProfile
    )

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EnhancedTrade(Trade):
    """Enhanced trade record with risk management details."""
    # Risk management fields
    position_size_method: Optional[str] = None
    position_size_confidence: Optional[float] = None
    stop_loss_price: Optional[float] = None
    take_profit_price: Optional[float] = None
    stop_loss_method: Optional[str] = None
    risk_reward_ratio: Optional[float] = None
    initial_risk_amount: Optional[float] = None
    max_risk_percentage: Optional[float] = None
    trailing_stop_activated: bool = False
    risk_alerts: List[str] = field(default_factory=list)

@dataclass
class EnhancedBacktestConfig(BacktestConfig):
    """Enhanced backtest configuration with risk management settings."""

    # Risk management integration settings
    enable_risk_management: bool = True
    risk_config_path: Optional[str] = None
    strategy_name: str = "momentum"  # Strategy to use for risk config

    # Position sizing method override
    position_sizing_method_override: Optional[str] = None  # None = use config, or specify method

    # Risk limits (can override config file)
    max_portfolio_risk_override: Optional[float] = None
    max_position_size_override: Optional[float] = None
    max_drawdown_override: Optional[float] = None

    # Stop-loss settings
    enable_dynamic_stops: bool = True
    default_stop_method: str = "atr_based"
    default_profit_method: str = "risk_reward_ratio"

    # Portfolio monitoring
    enable_portfolio_monitoring: bool = True
    monitoring_frequency: int = 1  # Monitor every N days
    alert_on_risk_breach: bool = True

    # Risk regime detection
    enable_regime_detection: bool = False
    regime_detection_window: int = 60  # Days to look back for regime detection

class EnhancedBacktestEngine(BacktestEngine):
    """
    Enhanced Backtesting Engine with comprehensive Risk Management integration.

    This engine extends the basic BacktestEngine with institutional-grade risk management
    capabilities including advanced position sizing, dynamic stop-loss management,
    and real-time portfolio risk monitoring.
    """

    def __init__(self, config: EnhancedBacktestConfig):
        """
        Initialize the Enhanced Backtest Engine

        Args:
            config: Enhanced backtest configuration with risk management settings
        """
        # Initialize parent class
        super().__init__(config)

        self.enhanced_config = config

        # Initialize risk management components if enabled
        if config.enable_risk_management:
            logger.info("Initializing risk management components...")

            # Risk configuration manager
            self.risk_config_manager = RiskConfigManager(config.risk_config_path)

            # Get strategy-specific risk configuration
            self.strategy_config = self.risk_config_manager.get_strategy_config(config.strategy_name)

            # Apply any configuration overrides
            self._apply_config_overrides()

            # Initialize risk management engines
            self.risk_engine = RiskEngine(
                risk_limits=self._create_risk_limits(),
                lookback_period=252
            )

            self.stop_loss_manager = StopLossManager()

            if config.enable_portfolio_monitoring:
                self.portfolio_monitor = PortfolioMonitor()
                self.portfolio_snapshots: List[Any] = []
                self.risk_alerts_history: List[Any] = []

            logger.info(f"Risk management initialized for strategy: {config.strategy_name}")
        else:
            logger.info("Risk management disabled - using basic backtesting")
            self.risk_engine = None
            self.stop_loss_manager = None
            self.portfolio_monitor = None

        # Enhanced trade tracking
        self.enhanced_trades: List[EnhancedTrade] = []
        self.daily_risk_metrics: List[Dict[str, Any]] = []

        # Performance tracking
        self.risk_adjusted_metrics: Dict[str, float] = {}

    def _apply_config_overrides(self):
        """Apply configuration overrides to strategy config"""
        if self.enhanced_config.max_portfolio_risk_override is not None:
            self.strategy_config.max_portfolio_risk = self.enhanced_config.max_portfolio_risk_override

        if self.enhanced_config.max_position_size_override is not None:
            self.strategy_config.max_position_size = self.enhanced_config.max_position_size_override

        if self.enhanced_config.position_sizing_method_override is not None:
            self.strategy_config.position_sizing_method = self.enhanced_config.position_sizing_method_override

    def _create_risk_limits(self) -> RiskLimits:
        """Create risk limits from strategy configuration"""
        return RiskLimits(
            max_portfolio_risk=self.strategy_config.max_portfolio_risk,
            max_position_size=self.strategy_config.max_position_size,
            max_sector_concentration=0.30,  # 30% sector limit
            max_correlation=self.strategy_config.max_correlation,
            max_leverage=1.0,
            max_daily_loss=0.05,  # 5% daily loss limit
            min_liquidity_score=0.1
        )

    async def _execute_trades(
        self,
        recommendations: List[InvestmentRecommendation],
        current_date: datetime,
        price_data: Dict[str, pd.DataFrame]
    ) -> int:
        """Enhanced trade execution with risk management."""
        if not self.enhanced_config.enable_risk_management:
            # Fall back to parent implementation
            return await super()._execute_trades(recommendations, current_date, price_data)

        executed_count = 0

        # Filter to actionable recommendations
        buy_recommendations = [
            r for r in recommendations
            if r.recommendation in [RecommendationType.BUY, RecommendationType.STRONG_BUY]
        ]

        sell_recommendations = [
            r for r in recommendations
            if r.recommendation in [RecommendationType.SELL, RecommendationType.STRONG_SELL]
        ]

        # Execute sells first to free up cash
        for recommendation in sell_recommendations:
            if await self._execute_enhanced_sell_order(recommendation, current_date, price_data):
                executed_count += 1

        # Portfolio risk check before new positions
        if self.enhanced_config.enable_portfolio_monitoring:
            await self._monitor_portfolio_risk(current_date, price_data)

        # Execute buys with risk management
        for recommendation in buy_recommendations:
            if await self._execute_enhanced_buy_order(recommendation, current_date, price_data):
                executed_count += 1

        # Check stop-loss and take-profit conditions
        if self.enhanced_config.enable_dynamic_stops:
            await self._check_enhanced_exit_conditions(current_date, price_data)

        return executed_count

    async def _execute_enhanced_buy_order(
        self,
        recommendation: InvestmentRecommendation,
        current_date: datetime,
        price_data: Dict[str, pd.DataFrame]
    ) -> bool:
        """Execute buy order with advanced risk management."""
        symbol = recommendation.symbol

        if symbol not in price_data:
            return False

        # Get current price
        symbol_data = price_data[symbol]
        current_price_row = symbol_data[pd.to_datetime(symbol_data['date']) <= current_date]

        if current_price_row.empty:
            return False

        current_price = float(current_price_row.iloc[-1]['close'])

        # Apply slippage
        execution_price = current_price * (1 + self.config.slippage_percent)

        # Get historical returns for position sizing
        historical_returns = self._get_historical_returns(symbol, current_date, price_data)

        # Calculate position size using risk engine
        if not self.risk_engine:
            # Fallback to basic position sizing
            position_value = self.cash * 0.1  # 10% of cash
            return super()._execute_buy_order(recommendation, current_date, price_data)

        position_size_rec = self.risk_engine.calculate_position_size(
            symbol=symbol,
            current_price=execution_price,
            portfolio_value=self._get_total_portfolio_value(current_date, price_data),
            method=self._get_position_sizing_method(),
            historical_returns=historical_returns
        )

        # Convert to dollar value
        position_value = position_size_rec.recommended_size * execution_price

        # Apply minimum position size check
        if position_value < self.config.min_position_size:
            logger.debug(f"Position size too small for {symbol}: ${position_value:.2f}")
            return False

        # Check portfolio risk limits
        portfolio_value = self._get_total_portfolio_value(current_date, price_data)
        portfolio_positions = self._get_current_positions_value(current_date, price_data)

        if not self.risk_engine:
            risk_check = {'within_limits': True, 'violations': [], 'warnings': []}
        else:
            risk_check = self.risk_engine.check_risk_limits(
                portfolio_positions=portfolio_positions,
                portfolio_value=portfolio_value,
                new_position=(symbol, position_value)
            )

        if not risk_check['within_limits']:
            logger.warning(f"Position rejected for {symbol} due to risk limits: {risk_check['violations']}")
            return False

        # Calculate stop-loss and take-profit levels
        stop_loss_rec = None
        take_profit_rec = None

        if self.enhanced_config.enable_dynamic_stops and self.stop_loss_manager:
            # Get price data for technical analysis
            symbol_price_data = self._get_symbol_ohlcv_data(symbol, current_date, price_data)

            # Calculate stop-loss
            stop_loss_rec = self.stop_loss_manager.calculate_stop_loss(
                symbol=symbol,
                entry_price=execution_price,
                direction='long',
                method=StopLossMethod(self.enhanced_config.default_stop_method),
                price_data=symbol_price_data
            )

            # Calculate take-profit
            take_profit_rec = self.stop_loss_manager.calculate_take_profit(
                symbol=symbol,
                entry_price=execution_price,
                direction='long',
                method=TakeProfitMethod(self.enhanced_config.default_profit_method),
                stop_loss_price=stop_loss_rec.stop_price if stop_loss_rec else None,
                price_data=symbol_price_data
            )

        # Check if we have enough cash
        total_cost = position_value + self.config.commission_per_trade
        if total_cost > self.cash:
            # Adjust position size to available cash
            available_cash = self.cash - self.config.commission_per_trade
            if available_cash < self.config.min_position_size:
                return False
            position_value = available_cash

        # Calculate final quantity
        quantity = int(position_value / execution_price)
        actual_cost = quantity * execution_price + self.config.commission_per_trade

        if quantity <= 0 or actual_cost > self.cash:
            return False

        # Execute trade
        self.cash -= actual_cost

        # Create enhanced trade record
        enhanced_trade = EnhancedTrade(
            symbol=symbol,
            entry_date=current_date,
            exit_date=None,
            entry_price=execution_price,
            exit_price=None,
            quantity=quantity,
            trade_type="BUY",
            recommendation_score=recommendation.composite_score,
            strategy_name=self.enhanced_config.strategy_name,
            commission=self.config.commission_per_trade,
            # Risk management fields
            position_size_method=position_size_rec.sizing_method,
            position_size_confidence=position_size_rec.confidence,
            stop_loss_price=stop_loss_rec.stop_price if stop_loss_rec else None,
            take_profit_price=take_profit_rec.target_price if take_profit_rec else None,
            stop_loss_method=stop_loss_rec.method if stop_loss_rec else None,
            risk_reward_ratio=take_profit_rec.risk_reward_ratio if take_profit_rec else None,
            initial_risk_amount=abs(execution_price - stop_loss_rec.stop_price) * quantity if stop_loss_rec else None,
            max_risk_percentage=position_size_rec.risk_contribution
        )

        self.enhanced_trades.append(enhanced_trade)

        # Update positions
        if symbol in self.positions:
            # Add to existing position (average price calculation)
            existing_qty = self.positions[symbol]['quantity']
            existing_avg_price = self.positions[symbol]['avg_price']

            new_qty = existing_qty + quantity
            new_avg_price = ((existing_qty * existing_avg_price) + (quantity * execution_price)) / new_qty

            self.positions[symbol].update({
                'quantity': new_qty,
                'avg_price': new_avg_price,
                'stop_loss': stop_loss_rec.stop_price if stop_loss_rec else None,
                'take_profit': take_profit_rec.target_price if take_profit_rec else None
            })
        else:
            # New position
            self.positions[symbol] = {
                'quantity': quantity,
                'avg_price': execution_price,
                'entry_date': current_date,
                'stop_loss': stop_loss_rec.stop_price if stop_loss_rec else None,
                'take_profit': take_profit_rec.target_price if take_profit_rec else None
            }

        logger.info(f"Enhanced BUY executed: {quantity} shares of {symbol} at ${execution_price:.2f}")
        if stop_loss_rec:
            logger.info(f"  Stop-loss set at: ${stop_loss_rec.stop_price:.2f}")
        if take_profit_rec:
            logger.info(f"  Take-profit set at: ${take_profit_rec.target_price:.2f}")

        return True

    async def _execute_enhanced_sell_order(
        self,
        recommendation: InvestmentRecommendation,
        current_date: datetime,
        price_data: Dict[str, pd.DataFrame]
    ) -> bool:
        """Execute sell order with enhanced tracking."""
        symbol = recommendation.symbol

        if symbol not in self.positions:
            return False

        position = self.positions[symbol]

        if symbol not in price_data:
            return False

        # Get current price
        symbol_data = price_data[symbol]
        current_price_row = symbol_data[pd.to_datetime(symbol_data['date']) <= current_date]

        if current_price_row.empty:
            return False

        current_price = float(current_price_row.iloc[-1]['close'])

        # Apply slippage
        execution_price = current_price * (1 - self.config.slippage_percent)

        # Calculate proceeds
        quantity = position['quantity']
        proceeds = quantity * execution_price - self.config.commission_per_trade

        # Update cash
        self.cash += proceeds

        # Calculate P&L
        total_cost = quantity * position['avg_price']
        pnl = proceeds - total_cost
        pnl_percent = (pnl / total_cost) * 100 if total_cost > 0 else 0

        # Find and update corresponding enhanced trade
        for trade in reversed(self.enhanced_trades):
            if trade.symbol == symbol and trade.exit_date is None and trade.trade_type == "BUY":
                # Update trade with exit information
                trade.exit_date = current_date
                trade.exit_price = execution_price
                trade.pnl = pnl
                trade.pnl_percent = pnl_percent
                trade.hold_days = (current_date - trade.entry_date).days
                trade.exit_reason = "recommendation_sell"
                break

        # Remove position
        del self.positions[symbol]

        logger.info(f"Enhanced SELL executed: {quantity} shares of {symbol} at ${execution_price:.2f} "
                   f"(P&L: ${pnl:.2f}, {pnl_percent:.1f}%)")

        return True

    async def _check_enhanced_exit_conditions(
        self,
        current_date: datetime,
        price_data: Dict[str, pd.DataFrame]
    ):
        """Check for enhanced exit conditions including dynamic stops."""
        positions_to_exit = []

        for symbol, position in self.positions.items():
            if symbol not in price_data:
                continue

            # Get current price
            symbol_data = price_data[symbol]
            current_price_row = symbol_data[pd.to_datetime(symbol_data['date']) <= current_date]

            if current_price_row.empty:
                continue

            current_price = float(current_price_row.iloc[-1]['close'])
            exit_reason = None

            # Check stop-loss
            if position.get('stop_loss') and current_price <= position['stop_loss']:
                exit_reason = "stop_loss"

            # Check take-profit
            elif position.get('take_profit') and current_price >= position['take_profit']:
                exit_reason = "take_profit"

            # Check for trailing stop updates
            elif (self.enhanced_config.enable_dynamic_stops and
                  self.stop_loss_manager and position.get('stop_loss')):
                # Update trailing stops if applicable
                new_stop = self.stop_loss_manager.update_trailing_stop(
                    symbol=symbol,
                    current_price=current_price,
                    entry_price=position['avg_price'],
                    current_stop=position['stop_loss'],
                    direction='long',
                    trail_percentage=0.05  # 5% trailing stop
                )

                if new_stop and new_stop > position['stop_loss']:
                    position['stop_loss'] = new_stop
                    logger.info(f"Updated trailing stop for {symbol}: ${new_stop:.2f}")

                    # Mark trailing stop as activated in trade record
                    for trade in reversed(self.enhanced_trades):
                        if trade.symbol == symbol and trade.exit_date is None and trade.trade_type == "BUY":
                            trade.trailing_stop_activated = True
                            break

            if exit_reason:
                positions_to_exit.append((symbol, exit_reason))

        # Execute exit orders
        for symbol, exit_reason in positions_to_exit:
            await self._execute_exit_order(symbol, current_date, price_data, exit_reason)

    async def _execute_exit_order(
        self,
        symbol: str,
        current_date: datetime,
        price_data: Dict[str, pd.DataFrame],
        exit_reason: str
    ) -> bool:
        """Execute exit order due to stop-loss or take-profit."""
        if symbol not in self.positions:
            return False

        position = self.positions[symbol]

        # Get current price
        symbol_data = price_data[symbol]
        current_price_row = symbol_data[pd.to_datetime(symbol_data['date']) <= current_date]

        if current_price_row.empty:
            return False

        current_price = float(current_price_row.iloc[-1]['close'])

        # Apply slippage (worse for market orders due to urgency)
        slippage_multiplier = 1.5 if exit_reason == "stop_loss" else 1.0
        execution_price = current_price * (1 - self.config.slippage_percent * slippage_multiplier)

        # Calculate proceeds
        quantity = position['quantity']
        proceeds = quantity * execution_price - self.config.commission_per_trade

        # Update cash
        self.cash += proceeds

        # Calculate P&L
        total_cost = quantity * position['avg_price']
        pnl = proceeds - total_cost
        pnl_percent = (pnl / total_cost) * 100 if total_cost > 0 else 0

        # Find and update corresponding enhanced trade
        for trade in reversed(self.enhanced_trades):
            if trade.symbol == symbol and trade.exit_date is None and trade.trade_type == "BUY":
                # Update trade with exit information
                trade.exit_date = current_date
                trade.exit_price = execution_price
                trade.pnl = pnl
                trade.pnl_percent = pnl_percent
                trade.hold_days = (current_date - trade.entry_date).days
                trade.exit_reason = exit_reason
                break

        # Remove position
        del self.positions[symbol]

        logger.info(f"EXIT executed ({exit_reason}): {quantity} shares of {symbol} at ${execution_price:.2f} "
                   f"(P&L: ${pnl:.2f}, {pnl_percent:.1f}%)")

        return True

    async def _monitor_portfolio_risk(
        self,
        current_date: datetime,
        price_data: Dict[str, pd.DataFrame]
    ):
        """Monitor portfolio risk and generate alerts."""
        if not self.portfolio_monitor:
            return

        # Calculate current portfolio state
        portfolio_value = self._get_total_portfolio_value(current_date, price_data)
        portfolio_positions = self._get_current_positions_value(current_date, price_data)
        current_prices = self._get_current_prices(current_date, price_data)
        historical_returns = self._get_all_historical_returns(current_date, price_data)

        # Monitor portfolio
        snapshot, alerts = self.portfolio_monitor.monitor_portfolio(
            portfolio_positions=portfolio_positions,
            portfolio_value=portfolio_value,
            current_prices=current_prices,
            historical_returns=historical_returns,
            cash_balance=self.cash
        )

        # Store snapshot
        self.portfolio_snapshots.append(snapshot)

        # Store and process alerts
        if alerts:
            self.risk_alerts_history.extend(alerts)

            if self.enhanced_config.alert_on_risk_breach:
                for alert in alerts:
                    logger.warning(f"RISK ALERT: {alert.message}")

                    # Add alert to recent trades
                    for trade in reversed(self.enhanced_trades):
                        if trade.exit_date is None:  # Open positions
                            trade.risk_alerts.append(f"{alert.alert_type.value}: {alert.message}")

        # Store daily risk metrics
        risk_metrics = {
            'date': current_date,
            'portfolio_value': portfolio_value,
            'var_95': snapshot.var_95,
            'var_99': snapshot.var_99,
            'risk_score': snapshot.risk_score,
            'concentration_risk': snapshot.concentration_risk,
            'correlation_risk': snapshot.correlation_risk,
            'num_alerts': len(alerts)
        }

        self.daily_risk_metrics.append(risk_metrics)

    def _get_position_sizing_method(self) -> PositionSizingMethod:
        """Get position sizing method from configuration."""
        method_name = self.strategy_config.position_sizing_method.lower()

        method_mapping = {
            'kelly': PositionSizingMethod.KELLY,
            'risk_parity': PositionSizingMethod.RISK_PARITY,
            'volatility_based': PositionSizingMethod.VOLATILITY_BASED,
            'fixed_fractional': PositionSizingMethod.FIXED_FRACTIONAL,
            'max_drawdown': PositionSizingMethod.MAX_DRAWDOWN,
            'equal_weight': PositionSizingMethod.EQUAL_WEIGHT
        }

        return method_mapping.get(method_name, PositionSizingMethod.VOLATILITY_BASED)

    def _get_historical_returns(
        self,
        symbol: str,
        current_date: datetime,
        price_data: Dict[str, pd.DataFrame],
        lookback_days: int = 252
    ) -> Optional[pd.Series]:
        """Get historical returns for a symbol."""
        if symbol not in price_data:
            return None

        symbol_data = price_data[symbol]
        symbol_data['date'] = pd.to_datetime(symbol_data['date'])

        # Filter data up to current date
        historical_data = symbol_data[symbol_data['date'] <= current_date].tail(lookback_days + 1)

        if len(historical_data) < 2:
            return None

        # Calculate returns
        prices = historical_data['close']
        returns = prices.pct_change().dropna()

        # Set proper index using pd.Index
        returns = returns.set_axis(pd.Index(historical_data['date'].iloc[1:].values))

        return returns

    def _get_symbol_ohlcv_data(
        self,
        symbol: str,
        current_date: datetime,
        price_data: Dict[str, pd.DataFrame],
        lookback_days: int = 100
    ) -> Optional[pd.DataFrame]:
        """Get OHLCV data for technical analysis."""
        if symbol not in price_data:
            return None

        symbol_data = price_data[symbol]
        symbol_data['date'] = pd.to_datetime(symbol_data['date'])

        # Filter and format data
        historical_data = symbol_data[symbol_data['date'] <= current_date].tail(lookback_days)

        if len(historical_data) < 20:  # Need minimum data for technical analysis
            return None

        # Ensure required columns exist
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in historical_data.columns for col in required_columns):
            # Create mock OHLCV data from close prices
            close_prices = historical_data['close']
            ohlcv_data = pd.DataFrame({
                'open': close_prices * (1 + np.random.uniform(-0.01, 0.01, len(close_prices))),
                'high': close_prices * (1 + np.random.uniform(0, 0.02, len(close_prices))),
                'low': close_prices * (1 - np.random.uniform(0, 0.02, len(close_prices))),
                'close': close_prices,
                'volume': np.random.uniform(100000, 1000000, len(close_prices))
            }, index=historical_data.index)
            return ohlcv_data

        return historical_data[required_columns]

    def _get_total_portfolio_value(self, current_date: datetime, price_data: Dict[str, pd.DataFrame]) -> float:
        """Calculate total portfolio value including cash and positions."""
        total_value = self.cash

        for symbol, position in self.positions.items():
            if symbol in price_data:
                symbol_data = price_data[symbol]
                current_price_row = symbol_data[pd.to_datetime(symbol_data['date']) <= current_date]

                if not current_price_row.empty:
                    current_price = float(current_price_row.iloc[-1]['close'])
                    position_value = position['quantity'] * current_price
                    total_value += position_value

        return total_value

    def _get_current_positions_value(self, current_date: datetime, price_data: Dict[str, pd.DataFrame]) -> Dict[str, float]:
        """Get current positions with their market values."""
        positions_value = {}

        for symbol, position in self.positions.items():
            if symbol in price_data:
                symbol_data = price_data[symbol]
                current_price_row = symbol_data[pd.to_datetime(symbol_data['date']) <= current_date]

                if not current_price_row.empty:
                    current_price = float(current_price_row.iloc[-1]['close'])
                    position_value = position['quantity'] * current_price
                    positions_value[symbol] = position_value

        return positions_value

    def _get_current_prices(self, current_date: datetime, price_data: Dict[str, pd.DataFrame]) -> Dict[str, float]:
        """Get current prices for all symbols."""
        current_prices = {}

        for symbol in price_data.keys():
            symbol_data = price_data[symbol]
            current_price_row = symbol_data[pd.to_datetime(symbol_data['date']) <= current_date]

            if not current_price_row.empty:
                current_prices[symbol] = float(current_price_row.iloc[-1]['close'])

        return current_prices

    def _get_all_historical_returns(self, current_date: datetime, price_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.Series]:
        """Get historical returns for all symbols."""
        all_returns = {}

        for symbol in price_data.keys():
            returns = self._get_historical_returns(symbol, current_date, price_data)
            if returns is not None:
                all_returns[symbol] = returns

        return all_returns

    def get_enhanced_results(self) -> Dict[str, Any]:
        """Get comprehensive backtest results with risk management metrics."""
        # Get basic backtest results (simplified since parent get_results may not exist)
        basic_results = {
            'start_date': getattr(self, 'start_date', None),
            'end_date': getattr(self, 'end_date', None),
            'initial_cash': getattr(self.config, 'initial_cash', 100000),
            'final_cash': self.cash,
            'total_positions': len(self.positions),
            'total_trades': len(getattr(self, 'trades', []))
        }

        # Add enhanced risk management results
        enhanced_results = basic_results.copy()

        # Enhanced trade analysis
        if self.enhanced_trades:
            enhanced_results['enhanced_trades'] = [
                {
                    'symbol': trade.symbol,
                    'entry_date': trade.entry_date.isoformat(),
                    'exit_date': trade.exit_date.isoformat() if trade.exit_date else None,
                    'entry_price': trade.entry_price,
                    'exit_price': trade.exit_price,
                    'quantity': trade.quantity,
                    'pnl': trade.pnl,
                    'pnl_percent': trade.pnl_percent,
                    'hold_days': trade.hold_days,
                    'exit_reason': trade.exit_reason,
                    'position_size_method': trade.position_size_method,
                    'position_size_confidence': trade.position_size_confidence,
                    'stop_loss_price': trade.stop_loss_price,
                    'take_profit_price': trade.take_profit_price,
                    'risk_reward_ratio': trade.risk_reward_ratio,
                    'max_risk_percentage': trade.max_risk_percentage,
                    'trailing_stop_activated': trade.trailing_stop_activated,
                    'risk_alerts': trade.risk_alerts
                }
                for trade in self.enhanced_trades
            ]

            # Risk management statistics
            total_trades = len([t for t in self.enhanced_trades if t.exit_date is not None])
            stop_loss_exits = len([t for t in self.enhanced_trades if t.exit_reason == "stop_loss"])
            take_profit_exits = len([t for t in self.enhanced_trades if t.exit_reason == "take_profit"])
            trailing_stop_activations = len([t for t in self.enhanced_trades if t.trailing_stop_activated])

            enhanced_results['risk_management_stats'] = {
                'total_completed_trades': total_trades,
                'stop_loss_exits': stop_loss_exits,
                'take_profit_exits': take_profit_exits,
                'trailing_stop_activations': trailing_stop_activations,
                'stop_loss_rate': stop_loss_exits / total_trades if total_trades > 0 else 0,
                'take_profit_rate': take_profit_exits / total_trades if total_trades > 0 else 0,
                'trailing_stop_usage_rate': trailing_stop_activations / total_trades if total_trades > 0 else 0
            }

        # Daily risk metrics
        if self.daily_risk_metrics:
            enhanced_results['daily_risk_metrics'] = self.daily_risk_metrics

            # Risk summary statistics
            risk_scores = [d['risk_score'] for d in self.daily_risk_metrics]
            var_95_values = [d['var_95'] for d in self.daily_risk_metrics if d['var_95'] > 0]

            enhanced_results['risk_summary'] = {
                'avg_risk_score': np.mean(risk_scores) if risk_scores else 0,
                'max_risk_score': max(risk_scores) if risk_scores else 0,
                'avg_var_95': np.mean(var_95_values) if var_95_values else 0,
                'max_var_95': max(var_95_values) if var_95_values else 0,
                'total_risk_alerts': sum(d['num_alerts'] for d in self.daily_risk_metrics)
            }

        # Portfolio monitoring results
        if hasattr(self, 'portfolio_snapshots') and self.portfolio_snapshots:
            enhanced_results['portfolio_monitoring'] = {
                'total_snapshots': len(self.portfolio_snapshots),
                'total_alerts': len(self.risk_alerts_history) if hasattr(self, 'risk_alerts_history') else 0,
                'alert_breakdown': self._analyze_alert_breakdown()
            }

        # Configuration summary
        enhanced_results['risk_configuration'] = {
            'strategy_name': self.enhanced_config.strategy_name,
            'position_sizing_method': self.strategy_config.position_sizing_method,
            'max_portfolio_risk': self.strategy_config.max_portfolio_risk,
            'max_position_size': self.strategy_config.max_position_size,
            'stop_loss_method': self.enhanced_config.default_stop_method,
            'take_profit_method': self.enhanced_config.default_profit_method,
            'risk_management_enabled': self.enhanced_config.enable_risk_management,
            'dynamic_stops_enabled': self.enhanced_config.enable_dynamic_stops,
            'portfolio_monitoring_enabled': self.enhanced_config.enable_portfolio_monitoring
        }

        return enhanced_results

    def _analyze_alert_breakdown(self) -> Dict[str, int]:
        """Analyze risk alert breakdown by type and severity."""
        if not hasattr(self, 'risk_alerts_history'):
            return {}

        breakdown = {'total': len(self.risk_alerts_history)}

        # Count by alert level
        for level in AlertLevel:
            count = len([a for a in self.risk_alerts_history if a.level == level])
            breakdown[f'level_{level.value}'] = count

        # Count by alert type
        for alert_type in RiskAlert:
            count = len([a for a in self.risk_alerts_history if a.alert_type == alert_type])
            breakdown[f'type_{alert_type.value}'] = count

        return breakdown

    def export_enhanced_results(self, filepath: str) -> bool:
        """Export enhanced backtest results to JSON file."""
        try:
            results = self.get_enhanced_results()

            with open(filepath, 'w') as f:
                json.dump(results, f, indent=2, default=str)

            logger.info(f"Enhanced backtest results exported to: {filepath}")
            return True

        except Exception as e:
            logger.error(f"Error exporting enhanced results: {str(e)}")
            return False
