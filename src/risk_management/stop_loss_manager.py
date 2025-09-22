"""
Stop-Loss Manager

This module provides comprehensive stop-loss and take-profit management for the investment platform.
It includes dynamic stop-loss algorithms, take-profit mechanisms, and risk-reward optimization.

Key Features:
- Multiple stop-loss algorithms (ATR-based, percentage-based, trailing stops)
- Take-profit mechanisms with risk-reward ratios
- Dynamic adjustment based on market conditions
- Technical level-based stops (support/resistance)
- Time-based position limits
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Union, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StopLossMethod(Enum):
    """Available stop-loss methods"""
    ATR_BASED = "atr_based"
    PERCENTAGE_BASED = "percentage_based"
    TRAILING_STOP = "trailing_stop"
    SUPPORT_RESISTANCE = "support_resistance"
    VOLATILITY_ADJUSTED = "volatility_adjusted"
    TIME_BASED = "time_based"

class TakeProfitMethod(Enum):
    """Available take-profit methods"""
    RISK_REWARD_RATIO = "risk_reward_ratio"
    FIBONACCI_LEVELS = "fibonacci_levels"
    MOVING_AVERAGE = "moving_average"
    PARTIAL_PROFIT = "partial_profit"
    VOLATILITY_TARGET = "volatility_target"

class OrderType(Enum):
    """Order types for stop-loss and take-profit"""
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    TRAILING_STOP = "trailing_stop"

@dataclass
class StopLossLevel:
    """Stop-loss level recommendation"""
    symbol: str
    method: str
    stop_price: float
    entry_price: float
    stop_distance: float
    stop_percentage: float
    confidence: float
    rationale: str
    dynamic_adjustment: bool = False
    trailing_activation: Optional[float] = None
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'symbol': self.symbol,
            'method': self.method,
            'stop_price': self.stop_price,
            'entry_price': self.entry_price,
            'stop_distance': self.stop_distance,
            'stop_percentage': self.stop_percentage,
            'confidence': self.confidence,
            'rationale': self.rationale,
            'dynamic_adjustment': self.dynamic_adjustment,
            'trailing_activation': self.trailing_activation,
            'warnings': self.warnings
        }

@dataclass
class TakeProfitLevel:
    """Take-profit level recommendation"""
    symbol: str
    method: str
    target_price: float
    entry_price: float
    profit_distance: float
    profit_percentage: float
    risk_reward_ratio: float
    confidence: float
    rationale: str
    partial_levels: List[float] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'symbol': self.symbol,
            'method': self.method,
            'target_price': self.target_price,
            'entry_price': self.entry_price,
            'profit_distance': self.profit_distance,
            'profit_percentage': self.profit_percentage,
            'risk_reward_ratio': self.risk_reward_ratio,
            'confidence': self.confidence,
            'rationale': self.rationale,
            'partial_levels': self.partial_levels,
            'warnings': self.warnings
        }

@dataclass
class RiskRewardRecommendation:
    """Combined stop-loss and take-profit recommendation"""
    symbol: str
    entry_price: float
    stop_loss: StopLossLevel
    take_profit: TakeProfitLevel
    risk_reward_ratio: float
    expected_return: float
    max_loss: float
    position_score: float  # 0-10 scoring for position quality
    overall_rationale: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'symbol': self.symbol,
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss.to_dict(),
            'take_profit': self.take_profit.to_dict(),
            'risk_reward_ratio': self.risk_reward_ratio,
            'expected_return': self.expected_return,
            'max_loss': self.max_loss,
            'position_score': self.position_score,
            'overall_rationale': self.overall_rationale
        }

@dataclass
class StopLossConfig:
    """Configuration for stop-loss calculations"""
    default_method: StopLossMethod = StopLossMethod.ATR_BASED
    atr_multiplier: float = 2.0
    atr_period: int = 14
    max_stop_percentage: float = 0.10  # 10% maximum stop
    min_stop_percentage: float = 0.01  # 1% minimum stop
    trailing_activation_pct: float = 0.03  # 3% profit before trailing
    volatility_lookback: int = 20
    support_resistance_buffer: float = 0.005  # 0.5% buffer from levels

class StopLossManager:
    """
    Comprehensive stop-loss and take-profit management system.

    This class provides advanced stop-loss and take-profit calculations using
    multiple methodologies including technical analysis, volatility-based stops,
    and dynamic adjustment mechanisms.
    """

    def __init__(self, config: Optional[StopLossConfig] = None):
        """
        Initialize the Stop-Loss Manager

        Args:
            config: Stop-loss configuration parameters
        """
        self.config = config or StopLossConfig()
        logger.info("StopLossManager initialized")

    def calculate_stop_loss(self,
                           symbol: str,
                           entry_price: float,
                           direction: str,  # 'long' or 'short'
                           method: StopLossMethod,
                           price_data: Optional[pd.DataFrame] = None,
                           **kwargs) -> StopLossLevel:
        """
        Calculate stop-loss level using specified method

        Args:
            symbol: Asset symbol
            entry_price: Entry price for the position
            direction: Position direction ('long' or 'short')
            method: Stop-loss calculation method
            price_data: Historical price data (OHLCV)
            **kwargs: Additional parameters for specific methods

        Returns:
            StopLossLevel with calculated stop-loss details
        """
        try:
            if method == StopLossMethod.ATR_BASED:
                return self._atr_based_stop_loss(
                    symbol, entry_price, direction, price_data, **kwargs
                )
            elif method == StopLossMethod.PERCENTAGE_BASED:
                return self._percentage_based_stop_loss(
                    symbol, entry_price, direction, **kwargs
                )
            elif method == StopLossMethod.TRAILING_STOP:
                return self._trailing_stop_loss(
                    symbol, entry_price, direction, price_data, **kwargs
                )
            elif method == StopLossMethod.SUPPORT_RESISTANCE:
                return self._support_resistance_stop_loss(
                    symbol, entry_price, direction, price_data, **kwargs
                )
            elif method == StopLossMethod.VOLATILITY_ADJUSTED:
                return self._volatility_adjusted_stop_loss(
                    symbol, entry_price, direction, price_data, **kwargs
                )
            elif method == StopLossMethod.TIME_BASED:
                return self._time_based_stop_loss(
                    symbol, entry_price, direction, **kwargs
                )
            else:
                raise ValueError(f"Unknown stop-loss method: {method}")

        except Exception as e:
            logger.error(f"Error calculating stop-loss for {symbol}: {str(e)}")
            return self._fallback_stop_loss(symbol, entry_price, direction, str(e))

    def calculate_take_profit(self,
                             symbol: str,
                             entry_price: float,
                             direction: str,
                             method: TakeProfitMethod,
                             stop_loss_price: Optional[float] = None,
                             price_data: Optional[pd.DataFrame] = None,
                             **kwargs) -> TakeProfitLevel:
        """
        Calculate take-profit level using specified method

        Args:
            symbol: Asset symbol
            entry_price: Entry price for the position
            direction: Position direction ('long' or 'short')
            method: Take-profit calculation method
            stop_loss_price: Stop-loss price for risk-reward calculation
            price_data: Historical price data (OHLCV)
            **kwargs: Additional parameters for specific methods

        Returns:
            TakeProfitLevel with calculated take-profit details
        """
        try:
            if method == TakeProfitMethod.RISK_REWARD_RATIO:
                return self._risk_reward_take_profit(
                    symbol, entry_price, direction, stop_loss_price, **kwargs
                )
            elif method == TakeProfitMethod.FIBONACCI_LEVELS:
                return self._fibonacci_take_profit(
                    symbol, entry_price, direction, price_data, **kwargs
                )
            elif method == TakeProfitMethod.MOVING_AVERAGE:
                return self._moving_average_take_profit(
                    symbol, entry_price, direction, price_data, **kwargs
                )
            elif method == TakeProfitMethod.PARTIAL_PROFIT:
                return self._partial_profit_take_profit(
                    symbol, entry_price, direction, stop_loss_price, **kwargs
                )
            elif method == TakeProfitMethod.VOLATILITY_TARGET:
                return self._volatility_target_take_profit(
                    symbol, entry_price, direction, price_data, **kwargs
                )
            else:
                raise ValueError(f"Unknown take-profit method: {method}")

        except Exception as e:
            logger.error(f"Error calculating take-profit for {symbol}: {str(e)}")
            return self._fallback_take_profit(symbol, entry_price, direction, str(e))

    def calculate_risk_reward(self,
                             symbol: str,
                             entry_price: float,
                             direction: str,
                             stop_method: StopLossMethod = StopLossMethod.ATR_BASED,
                             profit_method: TakeProfitMethod = TakeProfitMethod.RISK_REWARD_RATIO,
                             price_data: Optional[pd.DataFrame] = None,
                             **kwargs) -> RiskRewardRecommendation:
        """
        Calculate comprehensive risk-reward recommendation

        Args:
            symbol: Asset symbol
            entry_price: Entry price for the position
            direction: Position direction ('long' or 'short')
            stop_method: Stop-loss calculation method
            profit_method: Take-profit calculation method
            price_data: Historical price data (OHLCV)
            **kwargs: Additional parameters

        Returns:
            RiskRewardRecommendation with complete analysis
        """
        # Calculate stop-loss
        stop_loss = self.calculate_stop_loss(
            symbol, entry_price, direction, stop_method, price_data, **kwargs
        )

        # Calculate take-profit
        take_profit = self.calculate_take_profit(
            symbol, entry_price, direction, profit_method,
            stop_loss.stop_price, price_data, **kwargs
        )

        # Calculate risk-reward metrics
        risk_reward_ratio = take_profit.risk_reward_ratio
        expected_return = take_profit.profit_percentage
        max_loss = stop_loss.stop_percentage

        # Calculate position score (0-10)
        position_score = self._calculate_position_score(
            risk_reward_ratio, stop_loss.confidence, take_profit.confidence
        )

        overall_rationale = f"""
Risk-Reward Analysis for {symbol}:
- Entry: ${entry_price:.2f}
- Stop-Loss: ${stop_loss.stop_price:.2f} ({stop_loss.stop_percentage:.1%} risk)
- Take-Profit: ${take_profit.target_price:.2f} ({take_profit.profit_percentage:.1%} target)
- Risk-Reward Ratio: {risk_reward_ratio:.1f}:1
- Position Score: {position_score:.1f}/10
        """.strip()

        return RiskRewardRecommendation(
            symbol=symbol,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_reward_ratio=risk_reward_ratio,
            expected_return=expected_return,
            max_loss=max_loss,
            position_score=position_score,
            overall_rationale=overall_rationale
        )

    def _atr_based_stop_loss(self,
                           symbol: str,
                           entry_price: float,
                           direction: str,
                           price_data: Optional[pd.DataFrame],
                           atr_multiplier: Optional[float] = None) -> StopLossLevel:
        """Calculate ATR-based stop-loss"""
        if price_data is None or len(price_data) < self.config.atr_period:
            return self._fallback_stop_loss(
                symbol, entry_price, direction, "Insufficient data for ATR calculation"
            )

        # Calculate ATR
        atr = self._calculate_atr(price_data, self.config.atr_period)
        if atr == 0:
            return self._fallback_stop_loss(
                symbol, entry_price, direction, "Zero ATR calculated"
            )

        multiplier = atr_multiplier or self.config.atr_multiplier
        stop_distance = atr * multiplier

        # Calculate stop price based on direction
        if direction.lower() == 'long':
            stop_price = entry_price - stop_distance
        else:  # short
            stop_price = entry_price + stop_distance

        stop_percentage = stop_distance / entry_price

        # Apply limits
        if stop_percentage > self.config.max_stop_percentage:
            stop_percentage = self.config.max_stop_percentage
            if direction.lower() == 'long':
                stop_price = entry_price * (1 - stop_percentage)
            else:
                stop_price = entry_price * (1 + stop_percentage)
            stop_distance = abs(entry_price - stop_price)

        return StopLossLevel(
            symbol=symbol,
            method="atr_based",
            stop_price=stop_price,
            entry_price=entry_price,
            stop_distance=stop_distance,
            stop_percentage=stop_percentage,
            confidence=0.8,
            rationale=f"ATR-based stop: {atr:.2f} ATR x {multiplier} = {stop_distance:.2f}",
            dynamic_adjustment=True
        )

    def _percentage_based_stop_loss(self,
                                  symbol: str,
                                  entry_price: float,
                                  direction: str,
                                  stop_percentage: float = 0.05) -> StopLossLevel:
        """Calculate percentage-based stop-loss"""
        stop_percentage = min(stop_percentage, self.config.max_stop_percentage)
        stop_percentage = max(stop_percentage, self.config.min_stop_percentage)

        if direction.lower() == 'long':
            stop_price = entry_price * (1 - stop_percentage)
        else:  # short
            stop_price = entry_price * (1 + stop_percentage)

        stop_distance = abs(entry_price - stop_price)

        return StopLossLevel(
            symbol=symbol,
            method="percentage_based",
            stop_price=stop_price,
            entry_price=entry_price,
            stop_distance=stop_distance,
            stop_percentage=stop_percentage,
            confidence=1.0,
            rationale=f"Fixed percentage stop: {stop_percentage:.1%}",
            dynamic_adjustment=False
        )

    def _trailing_stop_loss(self,
                           symbol: str,
                           entry_price: float,
                           direction: str,
                           price_data: Optional[pd.DataFrame],
                           trail_percentage: float = 0.05) -> StopLossLevel:
        """Calculate trailing stop-loss"""
        # Initial stop is percentage-based
        initial_stop = self._percentage_based_stop_loss(
            symbol, entry_price, direction, trail_percentage
        )

        # Add trailing functionality
        initial_stop.method = "trailing_stop"
        initial_stop.dynamic_adjustment = True
        initial_stop.trailing_activation = entry_price * self.config.trailing_activation_pct
        initial_stop.rationale = f"Trailing stop: {trail_percentage:.1%} trail, " \
                                f"activates at {self.config.trailing_activation_pct:.1%} profit"

        return initial_stop

    def _support_resistance_stop_loss(self,
                                     symbol: str,
                                     entry_price: float,
                                     direction: str,
                                     price_data: Optional[pd.DataFrame]) -> StopLossLevel:
        """Calculate support/resistance-based stop-loss"""
        if price_data is None or len(price_data) < 20:
            return self._fallback_stop_loss(
                symbol, entry_price, direction, "Insufficient data for S/R analysis"
            )

        # Simple support/resistance calculation using recent highs/lows
        lookback = min(20, len(price_data))
        recent_data = price_data.tail(lookback)

        if direction.lower() == 'long':
            # Find recent support level
            support_level = recent_data['low'].min()
            stop_price = support_level - (support_level * self.config.support_resistance_buffer)
        else:  # short
            # Find recent resistance level
            resistance_level = recent_data['high'].max()
            stop_price = resistance_level + (resistance_level * self.config.support_resistance_buffer)

        stop_distance = abs(entry_price - stop_price)
        stop_percentage = stop_distance / entry_price

        # Apply limits
        if stop_percentage > self.config.max_stop_percentage:
            return self._percentage_based_stop_loss(
                symbol, entry_price, direction, self.config.max_stop_percentage
            )

        level_type = "support" if direction.lower() == 'long' else "resistance"

        return StopLossLevel(
            symbol=symbol,
            method="support_resistance",
            stop_price=stop_price,
            entry_price=entry_price,
            stop_distance=stop_distance,
            stop_percentage=stop_percentage,
            confidence=0.7,
            rationale=f"{level_type.title()}-based stop at ${stop_price:.2f}",
            dynamic_adjustment=False
        )

    def _volatility_adjusted_stop_loss(self,
                                     symbol: str,
                                     entry_price: float,
                                     direction: str,
                                     price_data: Optional[pd.DataFrame]) -> StopLossLevel:
        """Calculate volatility-adjusted stop-loss"""
        if price_data is None or len(price_data) < self.config.volatility_lookback:
            return self._fallback_stop_loss(
                symbol, entry_price, direction, "Insufficient data for volatility calculation"
            )

        # Calculate volatility using price returns
        returns = price_data['close'].pct_change().dropna()
        if len(returns) < 10:
            return self._fallback_stop_loss(
                symbol, entry_price, direction, "Insufficient returns for volatility"
            )

        volatility = returns.tail(self.config.volatility_lookback).std()
        if volatility == 0:
            return self._fallback_stop_loss(
                symbol, entry_price, direction, "Zero volatility calculated"
            )

        # Adjust stop based on volatility (higher volatility = wider stop)
        base_stop_pct = 0.03  # 3% base stop
        volatility_multiplier = min(3.0, max(0.5, volatility * 50))  # Scale volatility
        stop_percentage = base_stop_pct * volatility_multiplier

        # Apply limits
        stop_percentage = min(stop_percentage, self.config.max_stop_percentage)
        stop_percentage = max(stop_percentage, self.config.min_stop_percentage)

        if direction.lower() == 'long':
            stop_price = entry_price * (1 - stop_percentage)
        else:  # short
            stop_price = entry_price * (1 + stop_percentage)

        stop_distance = abs(entry_price - stop_price)

        return StopLossLevel(
            symbol=symbol,
            method="volatility_adjusted",
            stop_price=stop_price,
            entry_price=entry_price,
            stop_distance=stop_distance,
            stop_percentage=stop_percentage,
            confidence=0.75,
            rationale=f"Volatility-adjusted: {volatility:.1%} volatility, " \
                     f"{volatility_multiplier:.1f}x multiplier",
            dynamic_adjustment=True
        )

    def _time_based_stop_loss(self,
                            symbol: str,
                            entry_price: float,
                            direction: str,
                            max_holding_days: int = 30) -> StopLossLevel:
        """Calculate time-based stop-loss (position expiration)"""
        # This is more conceptual - actual implementation would need order management
        stop_percentage = 0.05  # 5% default for time stops

        if direction.lower() == 'long':
            stop_price = entry_price * (1 - stop_percentage)
        else:  # short
            stop_price = entry_price * (1 + stop_percentage)

        stop_distance = abs(entry_price - stop_price)

        return StopLossLevel(
            symbol=symbol,
            method="time_based",
            stop_price=stop_price,
            entry_price=entry_price,
            stop_distance=stop_distance,
            stop_percentage=stop_percentage,
            confidence=0.6,
            rationale=f"Time-based stop: Close position after {max_holding_days} days",
            dynamic_adjustment=False,
            warnings=[f"Position will be closed after {max_holding_days} days regardless of price"]
        )

    def _risk_reward_take_profit(self,
                               symbol: str,
                               entry_price: float,
                               direction: str,
                               stop_loss_price: Optional[float],
                               target_ratio: float = 2.0) -> TakeProfitLevel:
        """Calculate take-profit based on risk-reward ratio"""
        if stop_loss_price is None:
            # Use default 5% stop for calculation
            if direction.lower() == 'long':
                stop_loss_price = entry_price * 0.95
            else:
                stop_loss_price = entry_price * 1.05

        risk_amount = abs(entry_price - stop_loss_price)
        profit_target = risk_amount * target_ratio

        if direction.lower() == 'long':
            target_price = entry_price + profit_target
        else:  # short
            target_price = entry_price - profit_target

        profit_percentage = profit_target / entry_price

        return TakeProfitLevel(
            symbol=symbol,
            method="risk_reward_ratio",
            target_price=target_price,
            entry_price=entry_price,
            profit_distance=profit_target,
            profit_percentage=profit_percentage,
            risk_reward_ratio=target_ratio,
            confidence=0.8,
            rationale=f"Risk-reward ratio: {target_ratio}:1 target"
        )

    def _fibonacci_take_profit(self,
                             symbol: str,
                             entry_price: float,
                             direction: str,
                             price_data: Optional[pd.DataFrame]) -> TakeProfitLevel:
        """Calculate Fibonacci-based take-profit levels"""
        if price_data is None or len(price_data) < 50:
            # Fallback to risk-reward
            return self._risk_reward_take_profit(symbol, entry_price, direction, None, 2.0)

        # Find recent swing high/low for Fibonacci calculation
        lookback = min(50, len(price_data))
        recent_data = price_data.tail(lookback)

        if direction.lower() == 'long':
            swing_low = recent_data['low'].min()
            swing_high = recent_data['high'].max()

            # Fibonacci extension levels (61.8%, 100%, 161.8%)
            fib_range = swing_high - swing_low
            target_price = entry_price + (fib_range * 0.618)  # 61.8% extension

        else:  # short
            swing_high = recent_data['high'].max()
            swing_low = recent_data['low'].min()

            fib_range = swing_high - swing_low
            target_price = entry_price - (fib_range * 0.618)  # 61.8% extension

        profit_distance = abs(target_price - entry_price)
        profit_percentage = profit_distance / entry_price

        # Calculate approximate risk-reward ratio
        assumed_risk = entry_price * 0.05  # Assume 5% risk
        risk_reward_ratio = profit_distance / assumed_risk

        return TakeProfitLevel(
            symbol=symbol,
            method="fibonacci_levels",
            target_price=target_price,
            entry_price=entry_price,
            profit_distance=profit_distance,
            profit_percentage=profit_percentage,
            risk_reward_ratio=risk_reward_ratio,
            confidence=0.7,
            rationale=f"Fibonacci 61.8% extension target at ${target_price:.2f}"
        )

    def _moving_average_take_profit(self,
                                  symbol: str,
                                  entry_price: float,
                                  direction: str,
                                  price_data: Optional[pd.DataFrame],
                                  ma_period: int = 50) -> TakeProfitLevel:
        """Calculate moving average-based take-profit"""
        if price_data is None or len(price_data) < ma_period:
            return self._risk_reward_take_profit(symbol, entry_price, direction, None, 1.5)

        # Calculate moving average
        ma = price_data['close'].rolling(window=ma_period).mean().iloc[-1]

        if direction.lower() == 'long':
            # Target is above current MA
            target_price = ma * 1.05  # 5% above MA
        else:  # short
            # Target is below current MA
            target_price = ma * 0.95  # 5% below MA

        profit_distance = abs(target_price - entry_price)
        profit_percentage = profit_distance / entry_price

        # Calculate risk-reward ratio
        assumed_risk = entry_price * 0.05
        risk_reward_ratio = profit_distance / assumed_risk

        return TakeProfitLevel(
            symbol=symbol,
            method="moving_average",
            target_price=target_price,
            entry_price=entry_price,
            profit_distance=profit_distance,
            profit_percentage=profit_percentage,
            risk_reward_ratio=risk_reward_ratio,
            confidence=0.6,
            rationale=f"MA{ma_period} target at ${target_price:.2f} (MA: ${ma:.2f})"
        )

    def _partial_profit_take_profit(self,
                                  symbol: str,
                                  entry_price: float,
                                  direction: str,
                                  stop_loss_price: Optional[float],
                                  levels: List[float] = [1.5, 2.5, 4.0]) -> TakeProfitLevel:
        """Calculate partial profit-taking levels"""
        # Use first level as primary target
        primary_target = self._risk_reward_take_profit(
            symbol, entry_price, direction, stop_loss_price, levels[0]
        )

        # Calculate additional levels
        if stop_loss_price is None:
            if direction.lower() == 'long':
                stop_loss_price = entry_price * 0.95
            else:
                stop_loss_price = entry_price * 1.05

        risk_amount = abs(entry_price - stop_loss_price)
        partial_levels = []

        for ratio in levels:
            profit_target = risk_amount * ratio
            if direction.lower() == 'long':
                level_price = entry_price + profit_target
            else:
                level_price = entry_price - profit_target
            partial_levels.append(level_price)

        primary_target.method = "partial_profit"
        primary_target.partial_levels = partial_levels
        primary_target.rationale = f"Partial profit levels at {levels} risk-reward ratios"

        return primary_target

    def _volatility_target_take_profit(self,
                                     symbol: str,
                                     entry_price: float,
                                     direction: str,
                                     price_data: Optional[pd.DataFrame]) -> TakeProfitLevel:
        """Calculate volatility-based take-profit target"""
        if price_data is None or len(price_data) < 20:
            return self._risk_reward_take_profit(symbol, entry_price, direction, None, 2.0)

        # Calculate recent volatility
        returns = price_data['close'].pct_change().dropna()
        volatility = returns.tail(20).std()

        if volatility == 0:
            return self._risk_reward_take_profit(symbol, entry_price, direction, None, 2.0)

        # Target is 2 standard deviations of price movement
        price_volatility = entry_price * volatility * 2

        if direction.lower() == 'long':
            target_price = entry_price + price_volatility
        else:  # short
            target_price = entry_price - price_volatility

        profit_distance = abs(target_price - entry_price)
        profit_percentage = profit_distance / entry_price

        # Calculate risk-reward ratio
        assumed_risk = entry_price * 0.05
        risk_reward_ratio = profit_distance / assumed_risk

        return TakeProfitLevel(
            symbol=symbol,
            method="volatility_target",
            target_price=target_price,
            entry_price=entry_price,
            profit_distance=profit_distance,
            profit_percentage=profit_percentage,
            risk_reward_ratio=risk_reward_ratio,
            confidence=0.75,
            rationale=f"2-sigma volatility target: {volatility:.1%} daily volatility"
        )

    def _fallback_stop_loss(self,
                           symbol: str,
                           entry_price: float,
                           direction: str,
                           reason: str) -> StopLossLevel:
        """Fallback stop-loss when calculations fail"""
        fallback_pct = 0.05  # 5% fallback stop

        if direction.lower() == 'long':
            stop_price = entry_price * (1 - fallback_pct)
        else:
            stop_price = entry_price * (1 + fallback_pct)

        stop_distance = abs(entry_price - stop_price)

        return StopLossLevel(
            symbol=symbol,
            method="fallback",
            stop_price=stop_price,
            entry_price=entry_price,
            stop_distance=stop_distance,
            stop_percentage=fallback_pct,
            confidence=0.3,
            rationale=f"Fallback 5% stop due to: {reason}",
            warnings=[f"Using fallback stop: {reason}"]
        )

    def _fallback_take_profit(self,
                            symbol: str,
                            entry_price: float,
                            direction: str,
                            reason: str) -> TakeProfitLevel:
        """Fallback take-profit when calculations fail"""
        fallback_pct = 0.10  # 10% fallback target

        if direction.lower() == 'long':
            target_price = entry_price * (1 + fallback_pct)
        else:
            target_price = entry_price * (1 - fallback_pct)

        profit_distance = abs(target_price - entry_price)

        return TakeProfitLevel(
            symbol=symbol,
            method="fallback",
            target_price=target_price,
            entry_price=entry_price,
            profit_distance=profit_distance,
            profit_percentage=fallback_pct,
            risk_reward_ratio=2.0,  # Assume 2:1 ratio
            confidence=0.3,
            rationale=f"Fallback 10% target due to: {reason}",
            warnings=[f"Using fallback target: {reason}"]
        )

    def _calculate_atr(self, price_data: pd.DataFrame, period: int) -> float:
        """Calculate Average True Range"""
        high = price_data['high']
        low = price_data['low']
        close = price_data['close'].shift(1)

        true_range = pd.DataFrame({
            'tr1': high - low,
            'tr2': abs(high - close),
            'tr3': abs(low - close)
        }).max(axis=1)

        return true_range.rolling(window=period).mean().iloc[-1] if len(true_range) >= period else 0.0

    def _calculate_position_score(self,
                                risk_reward_ratio: float,
                                stop_confidence: float,
                                profit_confidence: float) -> float:
        """Calculate position quality score (0-10)"""
        score = 5.0  # Base score

        # Risk-reward component (0-3 points)
        if risk_reward_ratio >= 3.0:
            score += 3
        elif risk_reward_ratio >= 2.0:
            score += 2
        elif risk_reward_ratio >= 1.5:
            score += 1
        elif risk_reward_ratio < 1.0:
            score -= 2

        # Confidence component (0-2 points)
        avg_confidence = (stop_confidence + profit_confidence) / 2
        if avg_confidence >= 0.8:
            score += 2
        elif avg_confidence >= 0.6:
            score += 1
        elif avg_confidence < 0.4:
            score -= 1

        return max(0, min(10, score))

    def update_trailing_stop(self,
                           symbol: str,
                           current_price: float,
                           entry_price: float,
                           current_stop: float,
                           direction: str,
                           trail_percentage: float = 0.05) -> Optional[float]:
        """
        Update trailing stop-loss based on current price

        Args:
            symbol: Asset symbol
            current_price: Current market price
            entry_price: Original entry price
            current_stop: Current stop-loss price
            direction: Position direction ('long' or 'short')
            trail_percentage: Trailing percentage

        Returns:
            New stop-loss price or None if no update needed
        """
        try:
            if direction.lower() == 'long':
                # For long positions, only move stop up
                new_stop = current_price * (1 - trail_percentage)
                if new_stop > current_stop:
                    logger.info(f"Updating trailing stop for {symbol}: {current_stop:.2f} -> {new_stop:.2f}")
                    return new_stop
            else:  # short
                # For short positions, only move stop down
                new_stop = current_price * (1 + trail_percentage)
                if new_stop < current_stop:
                    logger.info(f"Updating trailing stop for {symbol}: {current_stop:.2f} -> {new_stop:.2f}")
                    return new_stop

            return None  # No update needed

        except Exception as e:
            logger.error(f"Error updating trailing stop for {symbol}: {str(e)}")
            return None
