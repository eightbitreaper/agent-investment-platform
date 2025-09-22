"""
Portfolio Risk Monitor

This module provides real-time portfolio risk monitoring, correlation analysis,
concentration limits, and alert systems for risk threshold breaches.

Key Features:
- Real-time portfolio risk assessment
- Correlation matrix monitoring
- Concentration risk tracking
- Sector and asset allocation analysis
- Automated alert systems
- Risk reporting and visualization
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Union, Tuple, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime, timedelta
import json
import warnings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class RiskAlert(Enum):
    """Risk alert types"""
    VAR_BREACH = "var_breach"
    DRAWDOWN_LIMIT = "drawdown_limit"
    CONCENTRATION_RISK = "concentration_risk"
    CORRELATION_SPIKE = "correlation_spike"
    LIQUIDITY_RISK = "liquidity_risk"
    MARGIN_CALL = "margin_call"
    VOLATILITY_SPIKE = "volatility_spike"
    SECTOR_OVERWEIGHT = "sector_overweight"

@dataclass
class RiskAlertMessage:
    """Risk alert message structure"""
    alert_type: RiskAlert
    level: AlertLevel
    symbol: Optional[str]
    current_value: float
    threshold_value: float
    message: str
    recommendation: str
    timestamp: datetime = field(default_factory=datetime.now)
    portfolio_impact: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'alert_type': self.alert_type.value,
            'level': self.level.value,
            'symbol': self.symbol,
            'current_value': self.current_value,
            'threshold_value': self.threshold_value,
            'message': self.message,
            'recommendation': self.recommendation,
            'timestamp': self.timestamp.isoformat(),
            'portfolio_impact': self.portfolio_impact
        }

@dataclass
class PortfolioSnapshot:
    """Portfolio state snapshot for monitoring"""
    timestamp: datetime
    total_value: float
    positions: Dict[str, float]  # symbol -> value
    cash: float
    daily_pnl: float
    daily_pnl_pct: float
    var_95: float
    var_99: float
    max_drawdown: float
    risk_score: int
    correlation_risk: float
    concentration_risk: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'total_value': self.total_value,
            'positions': self.positions,
            'cash': self.cash,
            'daily_pnl': self.daily_pnl,
            'daily_pnl_pct': self.daily_pnl_pct,
            'var_95': self.var_95,
            'var_99': self.var_99,
            'max_drawdown': self.max_drawdown,
            'risk_score': self.risk_score,
            'correlation_risk': self.correlation_risk,
            'concentration_risk': self.concentration_risk
        }

@dataclass
class MonitoringConfig:
    """Configuration for portfolio monitoring"""
    # Risk thresholds
    max_var_95: float = 0.02  # 2% daily VaR
    max_var_99: float = 0.05  # 5% daily VaR
    max_drawdown: float = 0.15  # 15% maximum drawdown
    max_concentration: float = 0.20  # 20% single position limit
    max_sector_weight: float = 0.30  # 30% sector limit
    max_correlation: float = 0.80  # 80% correlation threshold

    # Monitoring frequency
    check_interval_minutes: int = 15  # Check every 15 minutes
    alert_cooldown_minutes: int = 60  # Minimum time between similar alerts

    # Risk score thresholds
    warning_risk_score: int = 6  # Warning at risk score 6
    critical_risk_score: int = 8  # Critical at risk score 8

    # Volatility thresholds
    volatility_spike_threshold: float = 2.0  # 2x normal volatility

    # Liquidity thresholds
    min_liquidity_ratio: float = 0.05  # 5% cash minimum

class PortfolioMonitor:
    """
    Real-time portfolio risk monitoring system.

    This class provides comprehensive portfolio monitoring including:
    - Real-time risk metric calculation
    - Alert generation for risk breaches
    - Historical risk tracking
    - Correlation and concentration monitoring
    - Automated reporting
    """

    def __init__(self,
                 config: Optional[MonitoringConfig] = None,
                 alert_callback: Optional[Callable[[RiskAlertMessage], None]] = None):
        """
        Initialize the Portfolio Monitor

        Args:
            config: Monitoring configuration
            alert_callback: Optional callback function for alerts
        """
        self.config = config or MonitoringConfig()
        self.alert_callback = alert_callback
        self.last_alerts: Dict[str, datetime] = {}
        self.portfolio_history: List[PortfolioSnapshot] = []
        self.active_alerts: List[RiskAlertMessage] = []

        logger.info("PortfolioMonitor initialized")

    def monitor_portfolio(self,
                         portfolio_positions: Dict[str, float],
                         portfolio_value: float,
                         current_prices: Dict[str, float],
                         historical_returns: Dict[str, pd.Series],
                         cash_balance: float = 0.0,
                         previous_value: Optional[float] = None) -> Tuple[PortfolioSnapshot, List[RiskAlertMessage]]:
        """
        Perform comprehensive portfolio monitoring

        Args:
            portfolio_positions: Current portfolio positions {symbol: value}
            portfolio_value: Total portfolio value
            current_prices: Current market prices {symbol: price}
            historical_returns: Historical returns data {symbol: returns_series}
            cash_balance: Cash holdings
            previous_value: Previous portfolio value for P&L calculation

        Returns:
            Tuple of (PortfolioSnapshot, List of alerts)
        """
        alerts = []

        try:
            # Calculate daily P&L
            daily_pnl = 0.0
            daily_pnl_pct = 0.0
            if previous_value is not None and previous_value > 0:
                daily_pnl = portfolio_value - previous_value
                daily_pnl_pct = daily_pnl / previous_value

            # Calculate risk metrics using RiskEngine (simplified here)
            var_95, var_99 = self._calculate_portfolio_var(
                portfolio_positions, historical_returns, portfolio_value
            )

            max_drawdown = self._calculate_current_drawdown()
            correlation_risk = self._calculate_correlation_risk(
                portfolio_positions, historical_returns
            )
            concentration_risk = self._calculate_concentration_risk(
                portfolio_positions, portfolio_value
            )

            # Calculate overall risk score
            risk_score = self._calculate_current_risk_score(
                var_95, max_drawdown, correlation_risk, concentration_risk
            )

            # Create portfolio snapshot
            snapshot = PortfolioSnapshot(
                timestamp=datetime.now(),
                total_value=portfolio_value,
                positions=portfolio_positions.copy(),
                cash=cash_balance,
                daily_pnl=daily_pnl,
                daily_pnl_pct=daily_pnl_pct,
                var_95=var_95,
                var_99=var_99,
                max_drawdown=max_drawdown,
                risk_score=risk_score,
                correlation_risk=correlation_risk,
                concentration_risk=concentration_risk
            )

            # Store snapshot
            self.portfolio_history.append(snapshot)

            # Keep only last 1000 snapshots to manage memory
            if len(self.portfolio_history) > 1000:
                self.portfolio_history = self.portfolio_history[-1000:]

            # Check for risk alerts
            alerts.extend(self._check_var_alerts(var_95, var_99))
            alerts.extend(self._check_drawdown_alerts(max_drawdown))
            alerts.extend(self._check_concentration_alerts(portfolio_positions, portfolio_value))
            alerts.extend(self._check_correlation_alerts(correlation_risk))
            alerts.extend(self._check_risk_score_alerts(risk_score))
            alerts.extend(self._check_liquidity_alerts(cash_balance, portfolio_value))

            # Filter alerts by cooldown
            filtered_alerts = self._filter_alerts_by_cooldown(alerts)

            # Update active alerts
            self.active_alerts.extend(filtered_alerts)

            # Send alerts via callback
            for alert in filtered_alerts:
                if self.alert_callback:
                    self.alert_callback(alert)
                logger.warning(f"Risk Alert: {alert.message}")

            return snapshot, filtered_alerts

        except Exception as e:
            logger.error(f"Error monitoring portfolio: {str(e)}")
            # Return minimal snapshot on error
            snapshot = PortfolioSnapshot(
                timestamp=datetime.now(),
                total_value=portfolio_value,
                positions=portfolio_positions,
                cash=cash_balance,
                daily_pnl=0.0,
                daily_pnl_pct=0.0,
                var_95=0.0,
                var_99=0.0,
                max_drawdown=0.0,
                risk_score=5,
                correlation_risk=0.0,
                concentration_risk=0.0
            )
            return snapshot, []

    def _calculate_portfolio_var(self,
                               portfolio_positions: Dict[str, float],
                               historical_returns: Dict[str, pd.Series],
                               portfolio_value: float) -> Tuple[float, float]:
        """Calculate portfolio VaR at 95% and 99% confidence levels"""
        try:
            if not portfolio_positions or not historical_returns:
                return 0.0, 0.0

            # Calculate portfolio returns
            portfolio_returns = self._calculate_portfolio_returns(
                portfolio_positions, historical_returns, portfolio_value
            )

            if portfolio_returns is None or len(portfolio_returns) < 30:
                return 0.0, 0.0

            var_95 = abs(np.percentile(portfolio_returns, 5))
            var_99 = abs(np.percentile(portfolio_returns, 1))

            return float(var_95), float(var_99)

        except Exception as e:
            logger.error(f"Error calculating portfolio VaR: {str(e)}")
            return 0.0, 0.0

    def _calculate_portfolio_returns(self,
                                   portfolio_positions: Dict[str, float],
                                   historical_returns: Dict[str, pd.Series],
                                   portfolio_value: float) -> Optional[pd.Series]:
        """Calculate historical portfolio returns"""
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

    def _calculate_current_drawdown(self) -> float:
        """Calculate current portfolio drawdown"""
        if len(self.portfolio_history) < 2:
            return 0.0

        try:
            values = [snapshot.total_value for snapshot in self.portfolio_history[-100:]]  # Last 100 snapshots
            if not values:
                return 0.0

            peak = max(values)
            current = values[-1]

            return (peak - current) / peak if peak > 0 else 0.0

        except Exception as e:
            logger.error(f"Error calculating drawdown: {str(e)}")
            return 0.0

    def _calculate_correlation_risk(self,
                                  portfolio_positions: Dict[str, float],
                                  historical_returns: Dict[str, pd.Series]) -> float:
        """Calculate average portfolio correlation risk"""
        symbols = list(portfolio_positions.keys())
        if len(symbols) < 2:
            return 0.0

        try:
            correlations = []
            for i, sym1 in enumerate(symbols):
                for j, sym2 in enumerate(symbols):
                    if i < j and sym1 in historical_returns and sym2 in historical_returns:
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

        except Exception as e:
            logger.error(f"Error calculating correlation risk: {str(e)}")
            return 0.0

    def _calculate_concentration_risk(self,
                                    portfolio_positions: Dict[str, float],
                                    portfolio_value: float) -> float:
        """Calculate portfolio concentration risk (HHI)"""
        if not portfolio_positions or portfolio_value == 0:
            return 0.0

        try:
            weights = [pos_value / portfolio_value for pos_value in portfolio_positions.values()]
            hhi = sum(w**2 for w in weights)

            # Normalize to 0-1 scale
            max_hhi = 1.0
            min_hhi = 1.0 / len(weights) if len(weights) > 0 else 1.0

            if max_hhi == min_hhi:
                return 0.0

            return (hhi - min_hhi) / (max_hhi - min_hhi)

        except Exception as e:
            logger.error(f"Error calculating concentration risk: {str(e)}")
            return 0.0

    def _calculate_current_risk_score(self,
                                    var_95: float,
                                    max_drawdown: float,
                                    correlation_risk: float,
                                    concentration_risk: float) -> int:
        """Calculate current risk score (1-10)"""
        score = 1

        # VaR component
        if var_95 > 0.05:
            score += 3
        elif var_95 > 0.03:
            score += 2
        elif var_95 > 0.02:
            score += 1

        # Drawdown component
        if max_drawdown > 0.20:
            score += 2
        elif max_drawdown > 0.10:
            score += 1

        # Concentration component
        if concentration_risk > 0.7:
            score += 2
        elif concentration_risk > 0.4:
            score += 1

        # Correlation component
        if correlation_risk > 0.7:
            score += 1

        return min(score, 10)

    def _check_var_alerts(self, var_95: float, var_99: float) -> List[RiskAlertMessage]:
        """Check for VaR threshold breaches"""
        alerts = []

        if var_95 > self.config.max_var_95:
            level = AlertLevel.CRITICAL if var_95 > self.config.max_var_95 * 1.5 else AlertLevel.WARNING
            alerts.append(RiskAlertMessage(
                alert_type=RiskAlert.VAR_BREACH,
                level=level,
                symbol=None,
                current_value=var_95,
                threshold_value=self.config.max_var_95,
                message=f"Portfolio VaR 95% breach: {var_95:.2%} > {self.config.max_var_95:.2%}",
                recommendation="Reduce position sizes or hedge portfolio risk",
                portfolio_impact=var_95 - self.config.max_var_95
            ))

        if var_99 > self.config.max_var_99:
            level = AlertLevel.EMERGENCY if var_99 > self.config.max_var_99 * 1.5 else AlertLevel.CRITICAL
            alerts.append(RiskAlertMessage(
                alert_type=RiskAlert.VAR_BREACH,
                level=level,
                symbol=None,
                current_value=var_99,
                threshold_value=self.config.max_var_99,
                message=f"Portfolio VaR 99% breach: {var_99:.2%} > {self.config.max_var_99:.2%}",
                recommendation="Immediate risk reduction required - consider closing positions",
                portfolio_impact=var_99 - self.config.max_var_99
            ))

        return alerts

    def _check_drawdown_alerts(self, current_drawdown: float) -> List[RiskAlertMessage]:
        """Check for drawdown limit breaches"""
        alerts = []

        if current_drawdown > self.config.max_drawdown:
            level = AlertLevel.EMERGENCY if current_drawdown > self.config.max_drawdown * 1.3 else AlertLevel.CRITICAL
            alerts.append(RiskAlertMessage(
                alert_type=RiskAlert.DRAWDOWN_LIMIT,
                level=level,
                symbol=None,
                current_value=current_drawdown,
                threshold_value=self.config.max_drawdown,
                message=f"Maximum drawdown exceeded: {current_drawdown:.1%} > {self.config.max_drawdown:.1%}",
                recommendation="Review stop-loss levels and consider de-risking portfolio",
                portfolio_impact=current_drawdown - self.config.max_drawdown
            ))

        return alerts

    def _check_concentration_alerts(self,
                                  portfolio_positions: Dict[str, float],
                                  portfolio_value: float) -> List[RiskAlertMessage]:
        """Check for concentration risk alerts"""
        alerts = []

        for symbol, position_value in portfolio_positions.items():
            position_weight = position_value / portfolio_value

            if position_weight > self.config.max_concentration:
                level = AlertLevel.CRITICAL if position_weight > self.config.max_concentration * 1.5 else AlertLevel.WARNING
                alerts.append(RiskAlertMessage(
                    alert_type=RiskAlert.CONCENTRATION_RISK,
                    level=level,
                    symbol=symbol,
                    current_value=position_weight,
                    threshold_value=self.config.max_concentration,
                    message=f"Position concentration risk: {symbol} {position_weight:.1%} > {self.config.max_concentration:.1%}",
                    recommendation=f"Reduce {symbol} position size to manage concentration risk",
                    portfolio_impact=position_weight - self.config.max_concentration
                ))

        return alerts

    def _check_correlation_alerts(self, correlation_risk: float) -> List[RiskAlertMessage]:
        """Check for correlation risk alerts"""
        alerts = []

        if correlation_risk > self.config.max_correlation:
            level = AlertLevel.CRITICAL if correlation_risk > 0.9 else AlertLevel.WARNING
            alerts.append(RiskAlertMessage(
                alert_type=RiskAlert.CORRELATION_SPIKE,
                level=level,
                symbol=None,
                current_value=correlation_risk,
                threshold_value=self.config.max_correlation,
                message=f"High portfolio correlation: {correlation_risk:.1%} > {self.config.max_correlation:.1%}",
                recommendation="Diversify portfolio with uncorrelated assets",
                portfolio_impact=correlation_risk - self.config.max_correlation
            ))

        return alerts

    def _check_risk_score_alerts(self, risk_score: int) -> List[RiskAlertMessage]:
        """Check for overall risk score alerts"""
        alerts = []

        if risk_score >= self.config.critical_risk_score:
            alerts.append(RiskAlertMessage(
                alert_type=RiskAlert.VAR_BREACH,  # Using VAR_BREACH as general risk alert
                level=AlertLevel.CRITICAL,
                symbol=None,
                current_value=float(risk_score),
                threshold_value=float(self.config.critical_risk_score),
                message=f"Critical risk score: {risk_score}/10",
                recommendation="Immediate risk reduction required across portfolio",
                portfolio_impact=float(risk_score - self.config.critical_risk_score)
            ))
        elif risk_score >= self.config.warning_risk_score:
            alerts.append(RiskAlertMessage(
                alert_type=RiskAlert.VAR_BREACH,
                level=AlertLevel.WARNING,
                symbol=None,
                current_value=float(risk_score),
                threshold_value=float(self.config.warning_risk_score),
                message=f"Elevated risk score: {risk_score}/10",
                recommendation="Monitor portfolio closely and consider risk reduction",
                portfolio_impact=float(risk_score - self.config.warning_risk_score)
            ))

        return alerts

    def _check_liquidity_alerts(self, cash_balance: float, portfolio_value: float) -> List[RiskAlertMessage]:
        """Check for liquidity risk alerts"""
        alerts = []

        if portfolio_value > 0:
            liquidity_ratio = cash_balance / portfolio_value

            if liquidity_ratio < self.config.min_liquidity_ratio:
                level = AlertLevel.WARNING if liquidity_ratio > 0 else AlertLevel.CRITICAL
                alerts.append(RiskAlertMessage(
                    alert_type=RiskAlert.LIQUIDITY_RISK,
                    level=level,
                    symbol=None,
                    current_value=liquidity_ratio,
                    threshold_value=self.config.min_liquidity_ratio,
                    message=f"Low liquidity: {liquidity_ratio:.1%} cash ratio < {self.config.min_liquidity_ratio:.1%}",
                    recommendation="Maintain adequate cash reserves for margin and opportunities",
                    portfolio_impact=self.config.min_liquidity_ratio - liquidity_ratio
                ))

        return alerts

    def _filter_alerts_by_cooldown(self, alerts: List[RiskAlertMessage]) -> List[RiskAlertMessage]:
        """Filter alerts by cooldown period to avoid spam"""
        filtered_alerts = []
        current_time = datetime.now()

        for alert in alerts:
            alert_key = f"{alert.alert_type.value}_{alert.symbol or 'portfolio'}"

            # Check if we're still in cooldown period
            if alert_key in self.last_alerts:
                time_since_last = current_time - self.last_alerts[alert_key]
                if time_since_last.total_seconds() < self.config.alert_cooldown_minutes * 60:
                    continue  # Skip this alert due to cooldown

            # Add alert and update last alert time
            filtered_alerts.append(alert)
            self.last_alerts[alert_key] = current_time

        return filtered_alerts

    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get current portfolio risk summary"""
        if not self.portfolio_history:
            return {'error': 'No portfolio data available'}

        latest = self.portfolio_history[-1]

        return {
            'timestamp': latest.timestamp.isoformat(),
            'total_value': latest.total_value,
            'daily_pnl': latest.daily_pnl,
            'daily_pnl_pct': latest.daily_pnl_pct,
            'risk_metrics': {
                'var_95': latest.var_95,
                'var_99': latest.var_99,
                'max_drawdown': latest.max_drawdown,
                'risk_score': latest.risk_score,
                'correlation_risk': latest.correlation_risk,
                'concentration_risk': latest.concentration_risk
            },
            'positions': latest.positions,
            'cash': latest.cash,
            'active_alerts': len(self.active_alerts),
            'alert_summary': self._get_alert_summary()
        }

    def _get_alert_summary(self) -> Dict[str, int]:
        """Get summary of active alerts by level"""
        summary = {level.value: 0 for level in AlertLevel}

        for alert in self.active_alerts[-50:]:  # Last 50 alerts
            if alert.level.value in summary:
                summary[alert.level.value] += 1

        return summary

    def get_risk_heatmap_data(self) -> Dict[str, Any]:
        """Generate data for risk heatmap visualization"""
        if not self.portfolio_history:
            return {}

        latest = self.portfolio_history[-1]

        # Create heatmap data structure
        heatmap_data = {
            'positions': [],
            'risk_levels': [],
            'portfolio_metrics': {
                'var_95': latest.var_95,
                'concentration_risk': latest.concentration_risk,
                'correlation_risk': latest.correlation_risk,
                'risk_score': latest.risk_score
            }
        }

        # Add position data
        total_value = latest.total_value
        for symbol, value in latest.positions.items():
            weight = value / total_value if total_value > 0 else 0

            # Simple risk level based on position size
            risk_level = 'high' if weight > 0.15 else 'medium' if weight > 0.05 else 'low'

            heatmap_data['positions'].append({
                'symbol': symbol,
                'value': value,
                'weight': weight,
                'risk_level': risk_level
            })

        return heatmap_data

    def clear_old_alerts(self, hours_old: int = 24):
        """Clear alerts older than specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours_old)
        self.active_alerts = [
            alert for alert in self.active_alerts
            if alert.timestamp > cutoff_time
        ]

        logger.info(f"Cleared alerts older than {hours_old} hours")

    def export_risk_report(self, filename: Optional[str] = None) -> str:
        """Export comprehensive risk report to JSON"""
        if filename is None:
            filename = f"risk_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        report_data = {
            'report_timestamp': datetime.now().isoformat(),
            'portfolio_summary': self.get_portfolio_summary(),
            'recent_snapshots': [
                snapshot.to_dict() for snapshot in self.portfolio_history[-10:]
            ],
            'active_alerts': [
                alert.to_dict() for alert in self.active_alerts
            ],
            'risk_heatmap': self.get_risk_heatmap_data(),
            'monitoring_config': {
                'max_var_95': self.config.max_var_95,
                'max_var_99': self.config.max_var_99,
                'max_drawdown': self.config.max_drawdown,
                'max_concentration': self.config.max_concentration,
                'max_correlation': self.config.max_correlation
            }
        }

        try:
            with open(filename, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)

            logger.info(f"Risk report exported to {filename}")
            return filename

        except Exception as e:
            logger.error(f"Error exporting risk report: {str(e)}")
            return f"Error: {str(e)}"
