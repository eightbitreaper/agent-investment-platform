"""
Risk Management Engine

This module provides comprehensive risk management capabilities for the investment platform,
including position sizing algorithms, portfolio risk calculations, and risk assessment tools.

Key Features:
- Multiple position sizing algorithms (Kelly Criterion, Risk Parity, Volatility-based)
- Portfolio risk metrics (VaR, Expected Shortfall, Maximum Drawdown)
- Real-time risk assessment and scoring
- Integration with backtesting framework
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Union, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import logging
from scipy import stats
from scipy.optimize import minimize
import warnings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PositionSizingMethod(Enum):
    """Available position sizing methods"""
    KELLY = "kelly"
    RISK_PARITY = "risk_parity"
    VOLATILITY_BASED = "volatility_based"
    FIXED_FRACTIONAL = "fixed_fractional"
    MAX_DRAWDOWN = "max_drawdown"
    EQUAL_WEIGHT = "equal_weight"

class RiskLevel(Enum):
    """Risk level classifications"""
    VERY_LOW = 1
    LOW = 2
    MODERATE = 3
    HIGH = 4
    VERY_HIGH = 5
    EXTREME = 6

@dataclass
class RiskMetrics:
    """Container for portfolio risk metrics"""
    portfolio_var_95: float = 0.0
    portfolio_var_99: float = 0.0
    expected_shortfall_95: float = 0.0
    expected_shortfall_99: float = 0.0
    max_drawdown: float = 0.0
    portfolio_volatility: float = 0.0
    sharpe_ratio: float = 0.0
    portfolio_beta: float = 0.0
    concentration_risk: float = 0.0
    correlation_risk: float = 0.0
    liquidity_risk: float = 0.0
    risk_score: int = 1  # 1-10 scale

    def to_dict(self) -> Dict[str, float]:
        """Convert risk metrics to dictionary"""
        return {
            'portfolio_var_95': self.portfolio_var_95,
            'portfolio_var_99': self.portfolio_var_99,
            'expected_shortfall_95': self.expected_shortfall_95,
            'expected_shortfall_99': self.expected_shortfall_99,
            'max_drawdown': self.max_drawdown,
            'portfolio_volatility': self.portfolio_volatility,
            'sharpe_ratio': self.sharpe_ratio,
            'portfolio_beta': self.portfolio_beta,
            'concentration_risk': self.concentration_risk,
            'correlation_risk': self.correlation_risk,
            'liquidity_risk': self.liquidity_risk,
            'risk_score': self.risk_score
        }

@dataclass
class PositionSizeRecommendation:
    """Position sizing recommendation with rationale"""
    symbol: str
    recommended_size: float
    max_size: float
    min_size: float
    sizing_method: str
    confidence: float
    risk_contribution: float
    rationale: str
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'symbol': self.symbol,
            'recommended_size': self.recommended_size,
            'max_size': self.max_size,
            'min_size': self.min_size,
            'sizing_method': self.sizing_method,
            'confidence': self.confidence,
            'risk_contribution': self.risk_contribution,
            'rationale': self.rationale,
            'warnings': self.warnings
        }

@dataclass
class RiskLimits:
    """Risk limits configuration"""
    max_portfolio_risk: float = 0.02  # 2% daily VaR
    max_position_size: float = 0.05   # 5% of portfolio
    max_sector_concentration: float = 0.20  # 20% per sector
    max_correlation: float = 0.7      # Maximum position correlation
    max_leverage: float = 1.0         # No leverage by default
    max_daily_loss: float = 0.03      # 3% daily loss limit
    min_liquidity_score: float = 0.5  # Minimum liquidity requirement

class RiskEngine:
    """
    Comprehensive risk management engine for position sizing and portfolio risk assessment.

    This class provides institutional-grade risk management capabilities including:
    - Multiple position sizing algorithms
    - Portfolio risk metrics calculation
    - Real-time risk assessment
    - Risk limit enforcement
    """

    def __init__(self,
                 risk_limits: Optional[RiskLimits] = None,
                 lookback_period: int = 252,
                 confidence_levels: List[float] = [0.95, 0.99]):
        """
        Initialize the Risk Engine

        Args:
            risk_limits: Risk limits configuration
            lookback_period: Days to use for historical calculations
            confidence_levels: Confidence levels for VaR calculations
        """
        self.risk_limits = risk_limits or RiskLimits()
        self.lookback_period = lookback_period
        self.confidence_levels = confidence_levels
        self.risk_free_rate = 0.02  # 2% annual risk-free rate

        logger.info(f"RiskEngine initialized with {lookback_period} day lookback")

    def calculate_position_size(self,
                              symbol: str,
                              current_price: float,
                              portfolio_value: float,
                              method: PositionSizingMethod,
                              historical_returns: Optional[pd.Series] = None,
                              portfolio_returns: Optional[pd.Series] = None,
                              **kwargs) -> PositionSizeRecommendation:
        """
        Calculate optimal position size using specified method

        Args:
            symbol: Asset symbol
            current_price: Current asset price
            portfolio_value: Total portfolio value
            method: Position sizing method to use
            historical_returns: Historical returns for the asset
            portfolio_returns: Historical portfolio returns
            **kwargs: Additional parameters for specific methods

        Returns:
            PositionSizeRecommendation with sizing details
        """
        try:
            if method == PositionSizingMethod.KELLY:
                return self._kelly_position_size(
                    symbol, current_price, portfolio_value, historical_returns, **kwargs
                )
            elif method == PositionSizingMethod.RISK_PARITY:
                return self._risk_parity_position_size(
                    symbol, current_price, portfolio_value, historical_returns, **kwargs
                )
            elif method == PositionSizingMethod.VOLATILITY_BASED:
                return self._volatility_based_position_size(
                    symbol, current_price, portfolio_value, historical_returns, **kwargs
                )
            elif method == PositionSizingMethod.FIXED_FRACTIONAL:
                return self._fixed_fractional_position_size(
                    symbol, current_price, portfolio_value, **kwargs
                )
            elif method == PositionSizingMethod.MAX_DRAWDOWN:
                return self._max_drawdown_position_size(
                    symbol, current_price, portfolio_value, historical_returns, **kwargs
                )
            elif method == PositionSizingMethod.EQUAL_WEIGHT:
                return self._equal_weight_position_size(
                    symbol, current_price, portfolio_value, **kwargs
                )
            else:
                raise ValueError(f"Unknown position sizing method: {method}")

        except Exception as e:
            logger.error(f"Error calculating position size for {symbol}: {str(e)}")
            # Return minimum position size as fallback
            min_size = portfolio_value * 0.01  # 1% minimum
            return PositionSizeRecommendation(
                symbol=symbol,
                recommended_size=min_size,
                max_size=min_size,
                min_size=min_size,
                sizing_method="fallback",
                confidence=0.1,
                risk_contribution=0.01,
                rationale="Error in calculation, using minimum position size",
                warnings=[f"Calculation error: {str(e)}"]
            )

    def _kelly_position_size(self,
                           symbol: str,
                           current_price: float,
                           portfolio_value: float,
                           historical_returns: Optional[pd.Series],
                           max_kelly_fraction: float = 0.25) -> PositionSizeRecommendation:
        """Calculate position size using Kelly Criterion"""
        if historical_returns is None or len(historical_returns) < 30:
            return self._fallback_position_size(symbol, current_price, portfolio_value,
                                              "Insufficient data for Kelly calculation")

        # Calculate win rate and average win/loss
        positive_returns = historical_returns[historical_returns > 0]
        negative_returns = historical_returns[historical_returns < 0]

        if len(positive_returns) == 0 or len(negative_returns) == 0:
            return self._fallback_position_size(symbol, current_price, portfolio_value,
                                              "No wins or losses in historical data")

        win_rate = len(positive_returns) / len(historical_returns)
        avg_win = positive_returns.mean()
        avg_loss = abs(negative_returns.mean())

        # Kelly formula: f* = (bp - q) / b
        # where b = avg_win/avg_loss, p = win_rate, q = 1 - win_rate
        if avg_loss == 0:
            kelly_fraction = 0.01  # Conservative fallback
        else:
            b = avg_win / avg_loss
            kelly_fraction = (b * win_rate - (1 - win_rate)) / b

        # Apply maximum Kelly fraction limit
        kelly_fraction = max(0, min(kelly_fraction, max_kelly_fraction))

        # Apply portfolio risk limits
        max_position_value = portfolio_value * self.risk_limits.max_position_size
        kelly_position_value = portfolio_value * kelly_fraction
        recommended_value = min(kelly_position_value, max_position_value)

        # Calculate number of shares
        shares = recommended_value / current_price

        return PositionSizeRecommendation(
            symbol=symbol,
            recommended_size=shares,
            max_size=max_position_value / current_price,
            min_size=portfolio_value * 0.01 / current_price,
            sizing_method="kelly",
            confidence=win_rate,
            risk_contribution=recommended_value / portfolio_value,
            rationale=f"Kelly Criterion: {kelly_fraction:.3f} fraction, "
                     f"Win rate: {win_rate:.2%}, Avg Win/Loss: {avg_win/avg_loss:.2f}",
            warnings=[] if kelly_fraction > 0 else ["Kelly fraction is zero or negative"]
        )

    def _risk_parity_position_size(self,
                                 symbol: str,
                                 current_price: float,
                                 portfolio_value: float,
                                 historical_returns: Optional[pd.Series],
                                 portfolio_returns: Optional[pd.Series] = None,
                                 target_positions: int = 10) -> PositionSizeRecommendation:
        """Calculate position size using Risk Parity approach"""
        if historical_returns is None or len(historical_returns) < 30:
            return self._fallback_position_size(symbol, current_price, portfolio_value,
                                              "Insufficient data for Risk Parity calculation")

        # Calculate asset volatility
        asset_volatility = historical_returns.std() * np.sqrt(252)

        if asset_volatility == 0:
            return self._fallback_position_size(symbol, current_price, portfolio_value,
                                              "Zero volatility in historical data")

        # Risk parity weight = 1/volatility normalized
        # Assuming equal risk budget across target number of positions
        risk_budget_per_position = 1.0 / target_positions

        # Position size = risk_budget / (price * volatility)
        # Target volatility contribution = risk_budget * portfolio_volatility
        if portfolio_returns is not None and len(portfolio_returns) > 30:
            portfolio_volatility = portfolio_returns.std() * np.sqrt(252)
        else:
            portfolio_volatility = 0.15  # Assume 15% portfolio volatility

        target_risk_contribution = risk_budget_per_position * portfolio_volatility
        position_value = (target_risk_contribution * portfolio_value) / asset_volatility

        # Apply position size limits
        max_position_value = portfolio_value * self.risk_limits.max_position_size
        position_value = min(position_value, max_position_value)

        shares = position_value / current_price

        return PositionSizeRecommendation(
            symbol=symbol,
            recommended_size=shares,
            max_size=max_position_value / current_price,
            min_size=portfolio_value * 0.01 / current_price,
            sizing_method="risk_parity",
            confidence=0.8,  # High confidence in volatility-based sizing
            risk_contribution=position_value / portfolio_value,
            rationale=f"Risk Parity: {asset_volatility:.1%} volatility, "
                     f"Target risk contribution: {target_risk_contribution:.1%}",
            warnings=[]
        )

    def _volatility_based_position_size(self,
                                      symbol: str,
                                      current_price: float,
                                      portfolio_value: float,
                                      historical_returns: Optional[pd.Series],
                                      target_volatility: float = 0.15) -> PositionSizeRecommendation:
        """Calculate position size inversely proportional to volatility"""
        if historical_returns is None or len(historical_returns) < 20:
            return self._fallback_position_size(symbol, current_price, portfolio_value,
                                              "Insufficient data for volatility calculation")

        # Calculate annualized volatility
        asset_volatility = historical_returns.std() * np.sqrt(252)

        if asset_volatility == 0:
            return self._fallback_position_size(symbol, current_price, portfolio_value,
                                              "Zero volatility in historical data")

        # Position size inversely proportional to volatility
        # Higher volatility = smaller position size
        volatility_scalar = target_volatility / asset_volatility
        base_position_fraction = 0.05  # 5% base allocation

        position_fraction = base_position_fraction * volatility_scalar
        position_fraction = min(position_fraction, self.risk_limits.max_position_size)

        position_value = portfolio_value * position_fraction
        shares = position_value / current_price

        return PositionSizeRecommendation(
            symbol=symbol,
            recommended_size=shares,
            max_size=portfolio_value * self.risk_limits.max_position_size / current_price,
            min_size=portfolio_value * 0.01 / current_price,
            sizing_method="volatility_based",
            confidence=0.75,
            risk_contribution=position_fraction,
            rationale=f"Volatility-based: {asset_volatility:.1%} volatility, "
                     f"Scalar: {volatility_scalar:.2f}",
            warnings=[] if volatility_scalar <= 2.0 else ["High volatility scalar"]
        )

    def _fixed_fractional_position_size(self,
                                       symbol: str,
                                       current_price: float,
                                       portfolio_value: float,
                                       fraction: float = 0.02) -> PositionSizeRecommendation:
        """Calculate fixed fractional position size"""
        fraction = min(fraction, self.risk_limits.max_position_size)
        position_value = portfolio_value * fraction
        shares = position_value / current_price

        return PositionSizeRecommendation(
            symbol=symbol,
            recommended_size=shares,
            max_size=portfolio_value * self.risk_limits.max_position_size / current_price,
            min_size=portfolio_value * 0.01 / current_price,
            sizing_method="fixed_fractional",
            confidence=1.0,
            risk_contribution=fraction,
            rationale=f"Fixed fractional: {fraction:.1%} of portfolio",
            warnings=[]
        )

    def _max_drawdown_position_size(self,
                                  symbol: str,
                                  current_price: float,
                                  portfolio_value: float,
                                  historical_returns: Optional[pd.Series],
                                  max_acceptable_drawdown: float = 0.20) -> PositionSizeRecommendation:
        """Calculate position size based on maximum acceptable drawdown"""
        if historical_returns is None or len(historical_returns) < 30:
            return self._fallback_position_size(symbol, current_price, portfolio_value,
                                              "Insufficient data for drawdown calculation")

        # Calculate historical maximum drawdown
        cumulative_returns = (1 + historical_returns).cumprod()
        rolling_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - rolling_max) / rolling_max
        max_historical_drawdown = abs(drawdown.min())

        if max_historical_drawdown == 0:
            max_historical_drawdown = 0.05  # Assume 5% if no drawdown observed

        # Position size = max_acceptable_drawdown / max_historical_drawdown
        drawdown_scalar = max_acceptable_drawdown / max_historical_drawdown
        base_fraction = 0.05  # 5% base allocation

        position_fraction = base_fraction * drawdown_scalar
        position_fraction = min(position_fraction, self.risk_limits.max_position_size)

        position_value = portfolio_value * position_fraction
        shares = position_value / current_price

        return PositionSizeRecommendation(
            symbol=symbol,
            recommended_size=shares,
            max_size=portfolio_value * self.risk_limits.max_position_size / current_price,
            min_size=portfolio_value * 0.01 / current_price,
            sizing_method="max_drawdown",
            confidence=0.7,
            risk_contribution=position_fraction,
            rationale=f"Max Drawdown: {max_historical_drawdown:.1%} historical, "
                     f"Acceptable: {max_acceptable_drawdown:.1%}",
            warnings=[] if drawdown_scalar <= 2.0 else ["High drawdown risk"]
        )

    def _equal_weight_position_size(self,
                                  symbol: str,
                                  current_price: float,
                                  portfolio_value: float,
                                  num_positions: int = 20) -> PositionSizeRecommendation:
        """Calculate equal weight position size"""
        equal_weight_fraction = 1.0 / num_positions
        equal_weight_fraction = min(equal_weight_fraction, self.risk_limits.max_position_size)

        position_value = portfolio_value * equal_weight_fraction
        shares = position_value / current_price

        return PositionSizeRecommendation(
            symbol=symbol,
            recommended_size=shares,
            max_size=portfolio_value * self.risk_limits.max_position_size / current_price,
            min_size=portfolio_value * 0.01 / current_price,
            sizing_method="equal_weight",
            confidence=1.0,
            risk_contribution=equal_weight_fraction,
            rationale=f"Equal weight: 1/{num_positions} = {equal_weight_fraction:.1%}",
            warnings=[]
        )

    def _fallback_position_size(self,
                              symbol: str,
                              current_price: float,
                              portfolio_value: float,
                              reason: str) -> PositionSizeRecommendation:
        """Fallback position size when calculations fail"""
        fallback_fraction = 0.01  # 1% fallback
        position_value = portfolio_value * fallback_fraction
        shares = position_value / current_price

        return PositionSizeRecommendation(
            symbol=symbol,
            recommended_size=shares,
            max_size=portfolio_value * self.risk_limits.max_position_size / current_price,
            min_size=shares,
            sizing_method="fallback",
            confidence=0.1,
            risk_contribution=fallback_fraction,
            rationale=f"Fallback sizing due to: {reason}",
            warnings=[f"Using fallback sizing: {reason}"]
        )

    def calculate_portfolio_risk(self,
                               portfolio_positions: Dict[str, float],
                               historical_returns: Dict[str, pd.Series],
                               portfolio_value: float) -> RiskMetrics:
        """
        Calculate comprehensive portfolio risk metrics

        Args:
            portfolio_positions: Dict of {symbol: position_value}
            historical_returns: Dict of {symbol: returns_series}
            portfolio_value: Total portfolio value

        Returns:
            RiskMetrics object with all risk calculations
        """
        try:
            if not portfolio_positions or not historical_returns:
                return RiskMetrics()  # Return empty metrics

            # Create portfolio returns series
            portfolio_returns = self._calculate_portfolio_returns(
                portfolio_positions, historical_returns, portfolio_value
            )

            if portfolio_returns is None or len(portfolio_returns) < 30:
                logger.warning("Insufficient data for portfolio risk calculation")
                return RiskMetrics()

            # Calculate risk metrics
            risk_metrics = RiskMetrics()

            # VaR calculations
            risk_metrics.portfolio_var_95 = self._calculate_var(portfolio_returns, 0.95)
            risk_metrics.portfolio_var_99 = self._calculate_var(portfolio_returns, 0.99)

            # Expected Shortfall
            risk_metrics.expected_shortfall_95 = self._calculate_expected_shortfall(
                portfolio_returns, 0.95
            )
            risk_metrics.expected_shortfall_99 = self._calculate_expected_shortfall(
                portfolio_returns, 0.99
            )

            # Maximum Drawdown
            risk_metrics.max_drawdown = self._calculate_max_drawdown(portfolio_returns)

            # Portfolio volatility
            risk_metrics.portfolio_volatility = portfolio_returns.std() * np.sqrt(252)

            # Sharpe ratio
            excess_returns = portfolio_returns - (self.risk_free_rate / 252)
            if portfolio_returns.std() != 0:
                risk_metrics.sharpe_ratio = (
                    excess_returns.mean() * 252 / risk_metrics.portfolio_volatility
                )

            # Concentration and correlation risk
            risk_metrics.concentration_risk = self._calculate_concentration_risk(
                portfolio_positions, portfolio_value
            )
            risk_metrics.correlation_risk = self._calculate_correlation_risk(
                historical_returns, portfolio_positions
            )

            # Overall risk score (1-10 scale)
            risk_metrics.risk_score = self._calculate_risk_score(risk_metrics)

            logger.info(f"Portfolio risk calculated: VaR 95%: {risk_metrics.portfolio_var_95:.2%}")
            return risk_metrics

        except Exception as e:
            logger.error(f"Error calculating portfolio risk: {str(e)}")
            return RiskMetrics()

    def _calculate_portfolio_returns(self,
                                   portfolio_positions: Dict[str, float],
                                   historical_returns: Dict[str, pd.Series],
                                   portfolio_value: float) -> Optional[pd.Series]:
        """Calculate portfolio returns from individual asset returns"""
        try:
            # Get common date range
            common_dates = None
            for symbol in portfolio_positions.keys():
                if symbol in historical_returns:
                    if common_dates is None:
                        common_dates = historical_returns[symbol].index
                    else:
                        common_dates = common_dates.intersection(historical_returns[symbol].index)

            if common_dates is None or len(common_dates) < 30:
                return None

            # Calculate weighted returns
            portfolio_returns = pd.Series(0.0, index=common_dates)

            for symbol, position_value in portfolio_positions.items():
                if symbol in historical_returns:
                    weight = position_value / portfolio_value
                    asset_returns = historical_returns[symbol].reindex(common_dates).fillna(0)
                    portfolio_returns += weight * asset_returns

            return portfolio_returns

        except Exception as e:
            logger.error(f"Error calculating portfolio returns: {str(e)}")
            return None

    def _calculate_var(self, returns: pd.Series, confidence_level: float) -> float:
        """Calculate Value at Risk"""
        if len(returns) == 0:
            return 0.0
        return float(abs(np.percentile(returns, (1 - confidence_level) * 100)))

    def _calculate_expected_shortfall(self, returns: pd.Series, confidence_level: float) -> float:
        """Calculate Expected Shortfall (Conditional VaR)"""
        if len(returns) == 0:
            return 0.0
        var = self._calculate_var(returns, confidence_level)
        return abs(returns[returns <= -var].mean()) if len(returns[returns <= -var]) > 0 else var

    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """Calculate Maximum Drawdown"""
        if len(returns) == 0:
            return 0.0

        cumulative = (1 + returns).cumprod()
        rolling_max = cumulative.expanding().max()
        drawdown = (cumulative - rolling_max) / rolling_max
        return abs(drawdown.min())

    def _calculate_concentration_risk(self,
                                    portfolio_positions: Dict[str, float],
                                    portfolio_value: float) -> float:
        """Calculate concentration risk (Herfindahl-Hirschman Index)"""
        if not portfolio_positions or portfolio_value == 0:
            return 0.0

        weights = [pos_value / portfolio_value for pos_value in portfolio_positions.values()]
        hhi = sum(w**2 for w in weights)

        # Normalize HHI to 0-1 scale (1 = maximum concentration)
        max_hhi = 1.0  # All in one position
        min_hhi = 1.0 / len(weights)  # Equal weighted

        if max_hhi == min_hhi:
            return 0.0

        return (hhi - min_hhi) / (max_hhi - min_hhi)

    def _calculate_correlation_risk(self,
                                  historical_returns: Dict[str, pd.Series],
                                  portfolio_positions: Dict[str, float]) -> float:
        """Calculate average correlation risk"""
        symbols = list(portfolio_positions.keys())
        if len(symbols) < 2:
            return 0.0

        correlations = []
        for i, sym1 in enumerate(symbols):
            for j, sym2 in enumerate(symbols):
                if i < j and sym1 in historical_returns and sym2 in historical_returns:
                    # Get overlapping periods
                    returns1 = historical_returns[sym1]
                    returns2 = historical_returns[sym2]
                    common_dates = returns1.index.intersection(returns2.index)

                    if len(common_dates) > 30:
                        corr = returns1.reindex(common_dates).corr(
                            returns2.reindex(common_dates)
                        )
                        if not np.isnan(corr):
                            correlations.append(abs(corr))

        return float(np.mean(correlations)) if correlations else 0.0

    def _calculate_risk_score(self, risk_metrics: RiskMetrics) -> int:
        """Calculate overall risk score (1-10 scale)"""
        score = 1

        # VaR component (0-3 points)
        if risk_metrics.portfolio_var_95 > 0.05:  # >5% daily VaR
            score += 3
        elif risk_metrics.portfolio_var_95 > 0.03:  # >3% daily VaR
            score += 2
        elif risk_metrics.portfolio_var_95 > 0.02:  # >2% daily VaR
            score += 1

        # Volatility component (0-2 points)
        if risk_metrics.portfolio_volatility > 0.25:  # >25% annual volatility
            score += 2
        elif risk_metrics.portfolio_volatility > 0.15:  # >15% annual volatility
            score += 1

        # Drawdown component (0-2 points)
        if risk_metrics.max_drawdown > 0.20:  # >20% max drawdown
            score += 2
        elif risk_metrics.max_drawdown > 0.10:  # >10% max drawdown
            score += 1

        # Concentration component (0-2 points)
        if risk_metrics.concentration_risk > 0.7:  # High concentration
            score += 2
        elif risk_metrics.concentration_risk > 0.4:  # Moderate concentration
            score += 1

        # Correlation component (0-1 point)
        if risk_metrics.correlation_risk > 0.7:  # High correlation
            score += 1

        return min(score, 10)  # Cap at 10

    def check_risk_limits(self,
                         portfolio_positions: Dict[str, float],
                         portfolio_value: float,
                         new_position: Optional[Tuple[str, float]] = None) -> Dict[str, Any]:
        """
        Check if portfolio meets risk limits

        Args:
            portfolio_positions: Current portfolio positions
            portfolio_value: Total portfolio value
            new_position: Optional new position to check (symbol, value)

        Returns:
            Dict with risk limit check results
        """
        results = {
            'within_limits': True,
            'violations': [],
            'warnings': [],
            'recommendations': []
        }

        # Create test portfolio including new position
        test_positions = portfolio_positions.copy()
        if new_position:
            symbol, value = new_position
            test_positions[symbol] = test_positions.get(symbol, 0) + value

        # Check position size limits
        for symbol, position_value in test_positions.items():
            position_fraction = position_value / portfolio_value
            if position_fraction > self.risk_limits.max_position_size:
                results['within_limits'] = False
                results['violations'].append(
                    f"{symbol}: {position_fraction:.1%} exceeds max position size "
                    f"{self.risk_limits.max_position_size:.1%}"
                )

        # Check concentration limits (simplified sector check)
        total_positions = len(test_positions)
        if total_positions > 0:
            max_position_fraction = max(pos / portfolio_value for pos in test_positions.values())
            if max_position_fraction > self.risk_limits.max_position_size:
                results['warnings'].append(
                    f"Largest position: {max_position_fraction:.1%} of portfolio"
                )

        # Add recommendations
        if not results['within_limits']:
            results['recommendations'].append("Reduce position sizes to meet risk limits")

        if len(results['violations']) == 0 and len(results['warnings']) == 0:
            results['recommendations'].append("Portfolio within acceptable risk limits")

        return results

    def get_risk_summary(self, risk_metrics: RiskMetrics) -> str:
        """Generate human-readable risk summary"""
        risk_level_map = {
            1: "Very Low", 2: "Very Low", 3: "Low", 4: "Low",
            5: "Moderate", 6: "Moderate", 7: "High", 8: "High",
            9: "Very High", 10: "Extreme"
        }

        risk_level = risk_level_map.get(risk_metrics.risk_score, "Unknown")

        summary = f"""
Portfolio Risk Summary:
- Risk Level: {risk_level} ({risk_metrics.risk_score}/10)
- Daily VaR (95%): {risk_metrics.portfolio_var_95:.2%}
- Daily VaR (99%): {risk_metrics.portfolio_var_99:.2%}
- Expected Shortfall (95%): {risk_metrics.expected_shortfall_95:.2%}
- Annual Volatility: {risk_metrics.portfolio_volatility:.1%}
- Maximum Drawdown: {risk_metrics.max_drawdown:.1%}
- Sharpe Ratio: {risk_metrics.sharpe_ratio:.2f}
- Concentration Risk: {risk_metrics.concentration_risk:.1%}
- Correlation Risk: {risk_metrics.correlation_risk:.1%}
        """.strip()

        return summary
