"""
Backtesting Framework for the Agent Investment Platform.

This module provides comprehensive backtesting capabilities to validate strategy
performance against historical data with detailed risk metrics and performance analytics.

Key Features:
- Historical strategy performance validation
- Risk metrics calculation (Sharpe ratio, max drawdown, volatility)
- Portfolio simulation with realistic transaction costs
- Performance comparison against benchmarks
- Detailed trade analysis and reporting
- Walk-forward analysis and out-of-sample testing
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

# Import our analysis components
try:
    from ..analysis.recommendation_engine import RecommendationEngine, InvestmentRecommendation, RecommendationType
    from ..analysis.sentiment_analyzer import FinancialSentimentAnalyzer
    from ..analysis.chart_analyzer import TechnicalChartAnalyzer
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from analysis.recommendation_engine import RecommendationEngine, InvestmentRecommendation, RecommendationType
    from analysis.sentiment_analyzer import FinancialSentimentAnalyzer
    from analysis.chart_analyzer import TechnicalChartAnalyzer


class BacktestStatus(Enum):
    """Backtest execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class OrderType(Enum):
    """Order types for backtesting."""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


@dataclass
class Trade:
    """Individual trade record."""
    symbol: str
    entry_date: datetime
    exit_date: Optional[datetime]
    entry_price: float
    exit_price: Optional[float]
    quantity: int
    trade_type: str  # "BUY" or "SELL"
    recommendation_score: float
    strategy_name: str
    commission: float
    pnl: Optional[float] = None
    pnl_percent: Optional[float] = None
    hold_days: Optional[int] = None
    exit_reason: Optional[str] = None


@dataclass
class PortfolioSnapshot:
    """Portfolio state at a point in time."""
    date: datetime
    total_value: float
    cash: float
    positions: Dict[str, Dict[str, Any]]  # symbol -> {quantity, value, weight}
    daily_return: float
    cumulative_return: float
    benchmark_return: Optional[float] = None


@dataclass
class RiskMetrics:
    """Comprehensive risk and performance metrics."""
    # Returns
    total_return: float
    annualized_return: float
    benchmark_return: Optional[float]
    excess_return: Optional[float]

    # Risk metrics
    volatility: float
    max_drawdown: float
    max_drawdown_duration: int
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float

    # Trade statistics
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    avg_win: float
    avg_loss: float
    profit_factor: float

    # Additional metrics
    beta: Optional[float]
    alpha: Optional[float]
    var_95: float  # Value at Risk
    expected_shortfall: float

    # Time-based metrics
    best_month: float
    worst_month: float
    positive_months: int
    negative_months: int


@dataclass
class BacktestConfig:
    """Backtesting configuration parameters."""
    start_date: datetime
    end_date: datetime
    initial_capital: float
    benchmark_symbol: str = "SPY"
    commission_per_trade: float = 5.0
    commission_percent: float = 0.001  # 0.1%
    slippage_percent: float = 0.0005  # 0.05%
    max_positions: int = 10
    position_sizing_method: str = "equal_weight"  # equal_weight, risk_parity, recommendation_based
    rebalance_frequency: str = "monthly"  # daily, weekly, monthly, quarterly
    min_position_size: float = 1000.0
    max_position_size: float = 50000.0
    enable_stop_loss: bool = True
    enable_take_profit: bool = True
    lookback_period: int = 252  # Trading days for analysis


@dataclass
class BacktestResult:
    """Complete backtesting results."""
    config: BacktestConfig
    status: BacktestStatus
    start_time: datetime
    end_time: Optional[datetime]

    # Performance data
    portfolio_history: List[PortfolioSnapshot]
    trades: List[Trade]
    risk_metrics: Optional[RiskMetrics]

    # Strategy performance
    strategy_name: str
    total_signals: int
    signals_executed: int
    execution_rate: float

    # Error information
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)


class BacktestEngine:
    """
    Comprehensive backtesting engine for investment strategies.

    This engine simulates strategy performance over historical data,
    providing detailed analytics on returns, risk, and trade execution.
    """

    def __init__(self, config: BacktestConfig):
        """
        Initialize the backtesting engine.

        Args:
            config: Backtesting configuration parameters
        """
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Initialize analysis components
        self.recommendation_engine = RecommendationEngine()

        # Portfolio state
        self.cash = config.initial_capital
        self.positions: Dict[str, Dict[str, Any]] = {}
        self.portfolio_history: List[PortfolioSnapshot] = []
        self.trades: List[Trade] = []

        # Benchmark data
        self.benchmark_data: Optional[pd.DataFrame] = None

        self.logger.info(f"Backtesting engine initialized with ${config.initial_capital:,.2f} initial capital")

    async def run_backtest(
        self,
        strategy_name: str,
        symbols: List[str],
        price_data: Dict[str, pd.DataFrame],
        news_data: Optional[Dict[str, List[Dict]]] = None,
        benchmark_data: Optional[pd.DataFrame] = None
    ) -> BacktestResult:
        """
        Execute comprehensive backtest for a given strategy.

        Args:
            strategy_name: Name of the investment strategy to test
            symbols: List of symbols to include in the backtest
            price_data: Historical price data for each symbol
            news_data: Historical news data for sentiment analysis
            benchmark_data: Benchmark price data for comparison

        Returns:
            Complete backtesting results with performance metrics
        """
        start_time = datetime.now()
        self.logger.info(f"Starting backtest for strategy '{strategy_name}' with {len(symbols)} symbols")

        try:
            # Initialize backtest result
            result = BacktestResult(
                config=self.config,
                status=BacktestStatus.RUNNING,
                start_time=start_time,
                end_time=None,
                portfolio_history=[],
                trades=[],
                risk_metrics=None,
                strategy_name=strategy_name,
                total_signals=0,
                signals_executed=0,
                execution_rate=0.0
            )

            # Store benchmark data
            self.benchmark_data = benchmark_data

            # Generate trading dates
            trading_dates = self._generate_trading_dates()

            # Initialize portfolio tracking
            self._initialize_portfolio(trading_dates[0])

            total_signals = 0
            executed_signals = 0

            # Execute backtest day by day
            for i, current_date in enumerate(trading_dates):
                # Get available data up to current date
                available_data = self._get_data_up_to_date(price_data, news_data, current_date)

                # Generate recommendations for current date
                recommendations = await self._generate_recommendations(
                    strategy_name=strategy_name,
                    symbols=symbols,
                    price_data=available_data['price'],
                    news_data=available_data.get('news'),
                    current_date=current_date
                )

                total_signals += len(recommendations)

                # Execute trades based on recommendations
                executed_count = await self._execute_trades(
                    recommendations=recommendations,
                    current_date=current_date,
                    price_data=available_data['price']
                )

                executed_signals += executed_count

                # Update portfolio valuation
                self._update_portfolio_value(current_date, available_data['price'])

                # Check for exits (stop loss, take profit, strategy changes)
                await self._check_exit_conditions(current_date, available_data['price'])

                # Record portfolio snapshot
                self._record_portfolio_snapshot(current_date)

                # Rebalance if needed
                if self._should_rebalance(current_date):
                    await self._rebalance_portfolio(current_date, available_data['price'])

                # Progress logging
                if i % 50 == 0:
                    self.logger.debug(f"Processed {i+1}/{len(trading_dates)} trading days")

            # Calculate final metrics
            result.portfolio_history = self.portfolio_history
            result.trades = self.trades
            result.total_signals = total_signals
            result.signals_executed = executed_signals
            result.execution_rate = executed_signals / total_signals if total_signals > 0 else 0.0
            result.risk_metrics = self._calculate_risk_metrics()
            result.status = BacktestStatus.COMPLETED
            result.end_time = datetime.now()

            duration = (result.end_time - start_time).total_seconds()
            self.logger.info(f"Backtest completed in {duration:.2f} seconds")
            self.logger.info(f"Total return: {result.risk_metrics.total_return:.2%}")
            self.logger.info(f"Sharpe ratio: {result.risk_metrics.sharpe_ratio:.3f}")
            self.logger.info(f"Max drawdown: {result.risk_metrics.max_drawdown:.2%}")

            return result

        except Exception as e:
            self.logger.error(f"Backtest failed: {e}")
            result.status = BacktestStatus.FAILED
            result.error_message = str(e)
            result.end_time = datetime.now()
            return result

    def _generate_trading_dates(self) -> List[datetime]:
        """Generate list of trading dates for the backtest period."""
        dates = []
        current = self.config.start_date

        while current <= self.config.end_date:
            # Skip weekends (simplified - could use trading calendar)
            if current.weekday() < 5:  # Monday = 0, Friday = 4
                dates.append(current)
            current += timedelta(days=1)

        return dates

    def _get_data_up_to_date(
        self,
        price_data: Dict[str, pd.DataFrame],
        news_data: Optional[Dict[str, List[Dict]]],
        current_date: datetime
    ) -> Dict[str, Any]:
        """Get all available data up to the current date (avoiding look-ahead bias)."""
        available_price_data = {}

        for symbol, data in price_data.items():
            # Filter data to avoid look-ahead bias
            mask = pd.to_datetime(data['date']) <= current_date
            available_data = data[mask].copy()

            # Ensure we have enough data for analysis
            if len(available_data) >= self.config.lookback_period:
                available_price_data[symbol] = available_data

        available_news_data = {}
        if news_data:
            for symbol, articles in news_data.items():
                # Filter news to current date
                available_articles = [
                    article for article in articles
                    if pd.to_datetime(article.get('date', current_date)) <= current_date
                ]
                available_news_data[symbol] = available_articles[-50:]  # Last 50 articles

        return {
            'price': available_price_data,
            'news': available_news_data if news_data else None
        }

    async def _generate_recommendations(
        self,
        strategy_name: str,
        symbols: List[str],
        price_data: Dict[str, pd.DataFrame],
        news_data: Optional[Dict[str, List[Dict]]],
        current_date: datetime
    ) -> List[InvestmentRecommendation]:
        """Generate investment recommendations for the current date."""
        recommendations = []

        for symbol in symbols:
            if symbol not in price_data:
                continue

            try:
                # Get recent price data for analysis
                symbol_price_data = price_data[symbol].tail(self.config.lookback_period)
                symbol_news_data = news_data.get(symbol, []) if news_data else []

                # Generate recommendation
                recommendation = await self.recommendation_engine.analyze_investment(
                    symbol=symbol,
                    strategy_name=strategy_name,
                    price_data=symbol_price_data,
                    news_data=symbol_news_data
                )

                recommendations.append(recommendation)

            except Exception as e:
                self.logger.warning(f"Failed to generate recommendation for {symbol}: {e}")
                continue

        return recommendations

    async def _execute_trades(
        self,
        recommendations: List[InvestmentRecommendation],
        current_date: datetime,
        price_data: Dict[str, pd.DataFrame]
    ) -> int:
        """Execute trades based on recommendations."""
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
            if self._execute_sell_order(recommendation, current_date, price_data):
                executed_count += 1

        # Execute buys
        for recommendation in buy_recommendations:
            if self._execute_buy_order(recommendation, current_date, price_data):
                executed_count += 1

        return executed_count

    def _execute_buy_order(
        self,
        recommendation: InvestmentRecommendation,
        current_date: datetime,
        price_data: Dict[str, pd.DataFrame]
    ) -> bool:
        """Execute a buy order based on recommendation."""
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

        # Calculate position size
        position_value = self._calculate_position_size(recommendation, current_price)

        if position_value < self.config.min_position_size:
            return False

        # Check if we have enough cash
        total_cost = position_value + self.config.commission_per_trade
        if total_cost > self.cash:
            # Try with available cash
            available_cash = self.cash - self.config.commission_per_trade
            if available_cash < self.config.min_position_size:
                return False
            position_value = available_cash

        # Calculate quantity
        quantity = int(position_value / execution_price)
        actual_cost = quantity * execution_price + self.config.commission_per_trade

        if quantity <= 0 or actual_cost > self.cash:
            return False

        # Execute trade
        self.cash -= actual_cost

        # Update positions
        if symbol in self.positions:
            # Add to existing position
            existing_qty = self.positions[symbol]['quantity']
            existing_avg_price = self.positions[symbol]['avg_price']

            new_qty = existing_qty + quantity
            new_avg_price = ((existing_qty * existing_avg_price) + (quantity * execution_price)) / new_qty

            self.positions[symbol].update({
                'quantity': new_qty,
                'avg_price': new_avg_price
            })
        else:
            # New position
            self.positions[symbol] = {
                'quantity': quantity,
                'avg_price': execution_price,
                'entry_date': current_date,
                'stop_loss': recommendation.position_sizing.stop_loss_price,
                'take_profit': recommendation.position_sizing.take_profit_price
            }

        # Record trade
        trade = Trade(
            symbol=symbol,
            entry_date=current_date,
            exit_date=None,
            entry_price=execution_price,
            exit_price=None,
            quantity=quantity,
            trade_type="BUY",
            recommendation_score=recommendation.composite_score,
            strategy_name=recommendation.strategy_name,
            commission=self.config.commission_per_trade
        )

        self.trades.append(trade)
        return True

    def _execute_sell_order(
        self,
        recommendation: InvestmentRecommendation,
        current_date: datetime,
        price_data: Dict[str, pd.DataFrame]
    ) -> bool:
        """Execute a sell order based on recommendation."""
        symbol = recommendation.symbol

        if symbol not in self.positions:
            return False  # No position to sell

        if symbol not in price_data:
            return False

        # Get current price
        symbol_data = price_data[symbol]
        current_price_row = symbol_data[pd.to_datetime(symbol_data['date']) <= current_date]

        if current_price_row.empty:
            return False

        current_price = float(current_price_row.iloc[-1]['close'])

        # Apply slippage (negative for sells)
        execution_price = current_price * (1 - self.config.slippage_percent)

        # Get position details
        position = self.positions[symbol]
        quantity = position['quantity']
        avg_entry_price = position['avg_price']

        # Calculate proceeds
        gross_proceeds = quantity * execution_price
        net_proceeds = gross_proceeds - self.config.commission_per_trade

        # Update cash
        self.cash += net_proceeds

        # Calculate P&L
        total_cost = quantity * avg_entry_price
        pnl = net_proceeds - total_cost
        pnl_percent = pnl / total_cost if total_cost > 0 else 0

        # Update trade record
        # Find the corresponding buy trade
        for trade in reversed(self.trades):
            if (trade.symbol == symbol and
                trade.trade_type == "BUY" and
                trade.exit_date is None):

                trade.exit_date = current_date
                trade.exit_price = execution_price
                trade.pnl = pnl
                trade.pnl_percent = pnl_percent
                trade.hold_days = (current_date - trade.entry_date).days
                trade.exit_reason = "STRATEGY_SIGNAL"
                break

        # Remove position
        del self.positions[symbol]

        return True

    def _calculate_position_size(
        self,
        recommendation: InvestmentRecommendation,
        current_price: float
    ) -> float:
        """Calculate position size based on strategy and risk management."""
        if self.config.position_sizing_method == "equal_weight":
            # Equal weight across max positions
            target_position_value = (self.cash + self._get_total_position_value()) / self.config.max_positions
            return min(target_position_value, self.config.max_position_size)

        elif self.config.position_sizing_method == "recommendation_based":
            # Size based on recommendation strength and confidence
            base_size = self.cash * 0.1  # 10% base allocation

            # Adjust based on composite score strength
            score_multiplier = max(0.5, min(2.0, abs(recommendation.composite_score) * 2))

            # Adjust based on confidence
            confidence_multiplier = recommendation.confidence.value / 5.0  # Normalize to 0-1

            position_size = base_size * score_multiplier * confidence_multiplier
            return min(position_size, self.config.max_position_size)

        else:  # Default to fixed percentage
            return min(self.cash * 0.1, self.config.max_position_size)

    def _get_total_position_value(self) -> float:
        """Calculate total value of current positions."""
        # This would need current prices, simplified for now
        return sum(pos['quantity'] * pos['avg_price'] for pos in self.positions.values())

    async def _check_exit_conditions(
        self,
        current_date: datetime,
        price_data: Dict[str, pd.DataFrame]
    ):
        """Check for stop loss, take profit, and other exit conditions."""
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

            # Check stop loss
            if (self.config.enable_stop_loss and
                position.get('stop_loss') and
                current_price <= position['stop_loss']):
                positions_to_exit.append((symbol, current_price, "STOP_LOSS"))

            # Check take profit
            elif (self.config.enable_take_profit and
                  position.get('take_profit') and
                  current_price >= position['take_profit']):
                positions_to_exit.append((symbol, current_price, "TAKE_PROFIT"))

        # Execute exits
        for symbol, exit_price, exit_reason in positions_to_exit:
            self._execute_exit(symbol, exit_price, current_date, exit_reason)

    def _execute_exit(
        self,
        symbol: str,
        exit_price: float,
        exit_date: datetime,
        exit_reason: str
    ):
        """Execute position exit."""
        if symbol not in self.positions:
            return

        position = self.positions[symbol]
        quantity = position['quantity']
        avg_entry_price = position['avg_price']

        # Apply slippage
        execution_price = exit_price * (1 - self.config.slippage_percent)

        # Calculate proceeds
        gross_proceeds = quantity * execution_price
        net_proceeds = gross_proceeds - self.config.commission_per_trade

        # Update cash
        self.cash += net_proceeds

        # Calculate P&L
        total_cost = quantity * avg_entry_price
        pnl = net_proceeds - total_cost
        pnl_percent = pnl / total_cost if total_cost > 0 else 0

        # Update trade record
        for trade in reversed(self.trades):
            if (trade.symbol == symbol and
                trade.trade_type == "BUY" and
                trade.exit_date is None):

                trade.exit_date = exit_date
                trade.exit_price = execution_price
                trade.pnl = pnl
                trade.pnl_percent = pnl_percent
                trade.hold_days = (exit_date - trade.entry_date).days
                trade.exit_reason = exit_reason
                break

        # Remove position
        del self.positions[symbol]

    def _initialize_portfolio(self, start_date: datetime):
        """Initialize portfolio tracking."""
        self.portfolio_history = []
        self.trades = []
        self.positions = {}

        # Initial portfolio snapshot
        snapshot = PortfolioSnapshot(
            date=start_date,
            total_value=self.config.initial_capital,
            cash=self.cash,
            positions={},
            daily_return=0.0,
            cumulative_return=0.0
        )

        self.portfolio_history.append(snapshot)

    def _update_portfolio_value(
        self,
        current_date: datetime,
        price_data: Dict[str, pd.DataFrame]
    ):
        """Update portfolio valuation for current date."""
        total_position_value = 0.0
        current_positions = {}

        for symbol, position in self.positions.items():
            if symbol in price_data:
                symbol_data = price_data[symbol]
                current_price_row = symbol_data[pd.to_datetime(symbol_data['date']) <= current_date]

                if not current_price_row.empty:
                    current_price = float(current_price_row.iloc[-1]['close'])
                    position_value = position['quantity'] * current_price
                    total_position_value += position_value

                    current_positions[symbol] = {
                        'quantity': position['quantity'],
                        'value': position_value,
                        'weight': 0.0  # Will be calculated below
                    }

        total_value = self.cash + total_position_value

        # Calculate weights
        for pos in current_positions.values():
            pos['weight'] = pos['value'] / total_value if total_value > 0 else 0.0

        return total_value, current_positions

    def _record_portfolio_snapshot(self, current_date: datetime):
        """Record daily portfolio snapshot."""
        if not self.portfolio_history:
            return

        previous_value = self.portfolio_history[-1].total_value
        total_value, current_positions = self._update_portfolio_value(current_date, {})

        # Calculate returns
        daily_return = (total_value - previous_value) / previous_value if previous_value > 0 else 0.0
        cumulative_return = (total_value - self.config.initial_capital) / self.config.initial_capital

        snapshot = PortfolioSnapshot(
            date=current_date,
            total_value=total_value,
            cash=self.cash,
            positions=current_positions,
            daily_return=daily_return,
            cumulative_return=cumulative_return
        )

        self.portfolio_history.append(snapshot)

    def _should_rebalance(self, current_date: datetime) -> bool:
        """Determine if portfolio should be rebalanced."""
        if not self.portfolio_history:
            return False

        last_rebalance = self.portfolio_history[0].date

        if self.config.rebalance_frequency == "daily":
            return True
        elif self.config.rebalance_frequency == "weekly":
            return (current_date - last_rebalance).days >= 7
        elif self.config.rebalance_frequency == "monthly":
            return (current_date - last_rebalance).days >= 30
        elif self.config.rebalance_frequency == "quarterly":
            return (current_date - last_rebalance).days >= 90

        return False

    async def _rebalance_portfolio(
        self,
        current_date: datetime,
        price_data: Dict[str, pd.DataFrame]
    ):
        """Rebalance portfolio according to strategy."""
        # Simplified rebalancing - could be more sophisticated
        # For now, just ensure we don't exceed position limits

        total_value = self.cash + self._get_total_position_value()
        max_position_value = total_value * (1.0 / self.config.max_positions)

        # Check if any positions are too large
        positions_to_trim = []
        for symbol, position in self.positions.items():
            if symbol in price_data:
                symbol_data = price_data[symbol]
                current_price_row = symbol_data[pd.to_datetime(symbol_data['date']) <= current_date]

                if not current_price_row.empty:
                    current_price = float(current_price_row.iloc[-1]['close'])
                    position_value = position['quantity'] * current_price

                    if position_value > max_position_value:
                        excess_value = position_value - max_position_value
                        positions_to_trim.append((symbol, excess_value, current_price))

        # Trim oversized positions
        for symbol, excess_value, current_price in positions_to_trim:
            shares_to_sell = int(excess_value / current_price)
            if shares_to_sell > 0:
                # Execute partial sell (simplified)
                pass

    def _calculate_risk_metrics(self) -> RiskMetrics:
        """Calculate comprehensive risk and performance metrics."""
        if not self.portfolio_history:
            raise ValueError("No portfolio history available for metrics calculation")

        # Extract returns
        returns = pd.Series([snapshot.daily_return for snapshot in self.portfolio_history[1:]])
        values = pd.Series([snapshot.total_value for snapshot in self.portfolio_history])

        # Basic return metrics
        total_return = (values.iloc[-1] - self.config.initial_capital) / self.config.initial_capital
        days = len(self.portfolio_history)
        annualized_return = (1 + total_return) ** (252 / days) - 1 if days > 0 else 0.0

        # Risk metrics
        volatility = returns.std() * np.sqrt(252) if len(returns) > 1 else 0.0

        # Drawdown calculation
        peak = values.expanding().max()
        drawdown = (values - peak) / peak
        max_drawdown = drawdown.min()

        # Drawdown duration
        drawdown_duration = 0
        current_dd_duration = 0
        max_dd_duration = 0

        for dd in drawdown:
            if dd < 0:
                current_dd_duration += 1
                max_dd_duration = max(max_dd_duration, current_dd_duration)
            else:
                current_dd_duration = 0

        # Sharpe ratio
        risk_free_rate = 0.02  # Assume 2% risk-free rate
        excess_returns = returns - (risk_free_rate / 252)
        sharpe_ratio = excess_returns.mean() / excess_returns.std() * np.sqrt(252) if excess_returns.std() > 0 else 0.0

        # Sortino ratio
        negative_returns = returns[returns < 0]
        downside_std = negative_returns.std() * np.sqrt(252) if len(negative_returns) > 0 else volatility
        sortino_ratio = (annualized_return - risk_free_rate) / downside_std if downside_std > 0 else 0.0

        # Calmar ratio
        calmar_ratio = annualized_return / abs(max_drawdown) if max_drawdown != 0 else 0.0

        # Trade statistics
        completed_trades = [t for t in self.trades if t.exit_date is not None]
        total_trades = len(completed_trades)
        winning_trades = len([t for t in completed_trades if t.pnl and t.pnl > 0])
        losing_trades = len([t for t in completed_trades if t.pnl and t.pnl <= 0])

        win_rate = winning_trades / total_trades if total_trades > 0 else 0.0

        wins = [t.pnl for t in completed_trades if t.pnl and t.pnl > 0]
        losses = [abs(t.pnl) for t in completed_trades if t.pnl and t.pnl <= 0]

        avg_win = np.mean(wins) if wins else 0.0
        avg_loss = np.mean(losses) if losses else 0.0

        profit_factor = sum(wins) / sum(losses) if losses and sum(losses) > 0 else float('inf') if wins else 0.0

        # VaR and Expected Shortfall
        var_95 = returns.quantile(0.05) if len(returns) > 0 else 0.0
        tail_returns = returns[returns <= var_95]
        expected_shortfall = tail_returns.mean() if len(tail_returns) > 0 else var_95

        # Monthly statistics
        monthly_returns = []
        if len(self.portfolio_history) > 30:
            # Group by month (simplified)
            current_month_start = 0
            for i in range(30, len(self.portfolio_history), 30):
                month_start_value = self.portfolio_history[current_month_start].total_value
                month_end_value = self.portfolio_history[i].total_value
                monthly_return = (month_end_value - month_start_value) / month_start_value
                monthly_returns.append(monthly_return)
                current_month_start = i

        best_month = max(monthly_returns) if monthly_returns else 0.0
        worst_month = min(monthly_returns) if monthly_returns else 0.0
        positive_months = len([r for r in monthly_returns if r > 0])
        negative_months = len([r for r in monthly_returns if r <= 0])

        return RiskMetrics(
            total_return=total_return,
            annualized_return=annualized_return,
            benchmark_return=None,  # Would need benchmark data
            excess_return=None,
            volatility=volatility,
            max_drawdown=max_drawdown,
            max_drawdown_duration=max_dd_duration,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            avg_win=avg_win,
            avg_loss=avg_loss,
            profit_factor=profit_factor,
            beta=None,  # Would need benchmark for calculation
            alpha=None,
            var_95=var_95,
            expected_shortfall=expected_shortfall,
            best_month=best_month,
            worst_month=worst_month,
            positive_months=positive_months,
            negative_months=negative_months
        )


# Utility functions for backtesting
def create_sample_backtest_config(
    start_date: str = "2023-01-01",
    end_date: str = "2024-01-01",
    initial_capital: float = 100000.0
) -> BacktestConfig:
    """Create a sample backtesting configuration."""
    return BacktestConfig(
        start_date=datetime.strptime(start_date, "%Y-%m-%d"),
        end_date=datetime.strptime(end_date, "%Y-%m-%d"),
        initial_capital=initial_capital,
        benchmark_symbol="SPY",
        commission_per_trade=5.0,
        commission_percent=0.001,
        slippage_percent=0.0005,
        max_positions=10,
        position_sizing_method="recommendation_based",
        rebalance_frequency="monthly",
        min_position_size=1000.0,
        max_position_size=20000.0,
        enable_stop_loss=True,
        enable_take_profit=True,
        lookback_period=252
    )


async def run_strategy_backtest(
    strategy_name: str,
    symbols: List[str],
    price_data: Dict[str, pd.DataFrame],
    config: Optional[BacktestConfig] = None,
    news_data: Optional[Dict[str, List[Dict]]] = None
) -> BacktestResult:
    """
    Convenience function to run a complete strategy backtest.

    Args:
        strategy_name: Name of the strategy to test
        symbols: List of symbols to include
        price_data: Historical price data
        config: Backtesting configuration (uses default if None)
        news_data: Optional news data for sentiment analysis

    Returns:
        Complete backtesting results
    """
    if config is None:
        config = create_sample_backtest_config()

    engine = BacktestEngine(config)

    return await engine.run_backtest(
        strategy_name=strategy_name,
        symbols=symbols,
        price_data=price_data,
        news_data=news_data
    )


if __name__ == "__main__":
    # Example usage
    import asyncio

    async def example_backtest():
        # Create sample data (in real use, this would come from data sources)
        symbols = ['AAPL', 'GOOGL', 'MSFT']

        # This would normally load real historical data
        sample_data = {}
        for symbol in symbols:
            dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='D')
            prices = 100 + np.cumsum(np.random.normal(0.001, 0.02, len(dates)))

            sample_data[symbol] = pd.DataFrame({
                'date': dates,
                'open': prices + np.random.normal(0, 0.5, len(dates)),
                'high': prices + np.abs(np.random.normal(0, 1, len(dates))),
                'low': prices - np.abs(np.random.normal(0, 1, len(dates))),
                'close': prices,
                'volume': np.random.randint(1000000, 10000000, len(dates))
            })

        # Run backtest
        result = await run_strategy_backtest(
            strategy_name='conservative_growth',
            symbols=symbols,
            price_data=sample_data
        )

        print(f"Backtest Status: {result.status.value}")
        if result.risk_metrics:
            print(f"Total Return: {result.risk_metrics.total_return:.2%}")
            print(f"Sharpe Ratio: {result.risk_metrics.sharpe_ratio:.3f}")
            print(f"Max Drawdown: {result.risk_metrics.max_drawdown:.2%}")
            print(f"Win Rate: {result.risk_metrics.win_rate:.2%}")

    # Run example
    asyncio.run(example_backtest())
