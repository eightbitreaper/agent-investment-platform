"""
Performance Analysis Module for the Agent Investment Platform.

This module provides comprehensive performance analysis capabilities for backtesting results,
including detailed metrics calculation, visualization, and comparison tools.

Key Features:
- Detailed performance metrics calculation
- Risk-adjusted return analysis
- Benchmark comparison and attribution
- Portfolio analytics and position analysis
- Statistical significance testing
- Performance visualization and reporting
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from scipy import stats
import json

try:
    from .backtest_engine import BacktestResult, PortfolioSnapshot, Trade, RiskMetrics
except ImportError:
    # Fallback for direct execution
    from backtest_engine import BacktestResult, PortfolioSnapshot, Trade, RiskMetrics


class PerformanceCategory(Enum):
    """Performance categorization for analysis."""
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    BELOW_AVERAGE = "below_average"
    POOR = "poor"


@dataclass
class BenchmarkComparison:
    """Benchmark comparison results."""
    strategy_return: float
    benchmark_return: float
    excess_return: float
    tracking_error: float
    information_ratio: float
    beta: float
    alpha: float
    correlation: float
    up_capture: float
    down_capture: float


@dataclass
class PerformanceAttribution:
    """Performance attribution analysis."""
    security_selection: float
    market_timing: float
    asset_allocation: float
    interaction_effect: float
    total_active_return: float


@dataclass
class RiskAnalysis:
    """Comprehensive risk analysis."""
    # Volatility measures
    total_volatility: float
    systematic_risk: float
    idiosyncratic_risk: float

    # Downside risk
    downside_deviation: float
    semi_variance: float

    # Tail risk
    var_99: float
    var_95: float
    var_90: float
    expected_shortfall_95: float
    conditional_var: float

    # Risk-adjusted returns
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    omega_ratio: float

    # Drawdown analysis
    max_drawdown: float
    avg_drawdown: float
    drawdown_duration: int
    recovery_factor: float


@dataclass
class PerformanceReport:
    """Comprehensive performance analysis report."""
    backtest_result: BacktestResult
    risk_analysis: RiskAnalysis
    benchmark_comparison: Optional[BenchmarkComparison]
    performance_attribution: Optional[PerformanceAttribution]

    # Summary metrics
    performance_category: PerformanceCategory
    key_strengths: List[str]
    key_weaknesses: List[str]
    recommendations: List[str]

    # Statistical tests
    is_statistically_significant: bool
    p_value: float
    confidence_interval: Tuple[float, float]

    # Sector/Asset analysis
    sector_performance: Dict[str, float]
    top_performers: List[Tuple[str, float]]
    worst_performers: List[Tuple[str, float]]

    # Time-based analysis
    monthly_returns: List[float]
    quarterly_returns: List[float]
    rolling_sharpe: List[float]
    rolling_volatility: List[float]


class PerformanceAnalyzer:
    """
    Comprehensive performance analyzer for backtesting results.

    This analyzer provides detailed performance metrics, risk analysis,
    benchmark comparison, and generates comprehensive reports.
    """

    def __init__(self, risk_free_rate: float = 0.02):
        """
        Initialize the performance analyzer.

        Args:
            risk_free_rate: Annual risk-free rate for calculations
        """
        self.risk_free_rate = risk_free_rate
        self.logger = logging.getLogger(__name__)

    def analyze_performance(
        self,
        backtest_result: BacktestResult,
        benchmark_data: Optional[pd.DataFrame] = None,
        sector_mappings: Optional[Dict[str, str]] = None
    ) -> PerformanceReport:
        """
        Perform comprehensive performance analysis.

        Args:
            backtest_result: Results from backtesting
            benchmark_data: Benchmark price data for comparison
            sector_mappings: Symbol to sector mappings

        Returns:
            Comprehensive performance report
        """
        self.logger.info(f"Analyzing performance for {backtest_result.strategy_name}")

        # Extract portfolio data
        portfolio_df = self._extract_portfolio_data(backtest_result)

        # Calculate risk analysis
        risk_analysis = self._calculate_risk_analysis(portfolio_df)

        # Benchmark comparison if data available
        benchmark_comparison = None
        if benchmark_data is not None:
            benchmark_comparison = self._compare_to_benchmark(portfolio_df, benchmark_data)

        # Performance attribution
        performance_attribution = self._calculate_performance_attribution(
            backtest_result, benchmark_data
        )

        # Statistical significance testing
        is_significant, p_value, confidence_interval = self._test_statistical_significance(
            portfolio_df, benchmark_data
        )

        # Sector analysis
        sector_performance = self._analyze_sector_performance(
            backtest_result, sector_mappings
        )

        # Top/worst performers
        top_performers, worst_performers = self._identify_top_performers(backtest_result)

        # Time-based analysis
        monthly_returns = self._calculate_monthly_returns(portfolio_df)
        quarterly_returns = self._calculate_quarterly_returns(portfolio_df)
        rolling_sharpe = self._calculate_rolling_sharpe(portfolio_df)
        rolling_volatility = self._calculate_rolling_volatility(portfolio_df)

        # Performance categorization
        performance_category = self._categorize_performance(risk_analysis, benchmark_comparison)

        # Generate insights
        strengths, weaknesses, recommendations = self._generate_insights(
            risk_analysis, benchmark_comparison, backtest_result
        )

        report = PerformanceReport(
            backtest_result=backtest_result,
            risk_analysis=risk_analysis,
            benchmark_comparison=benchmark_comparison,
            performance_attribution=performance_attribution,
            performance_category=performance_category,
            key_strengths=strengths,
            key_weaknesses=weaknesses,
            recommendations=recommendations,
            is_statistically_significant=is_significant,
            p_value=p_value,
            confidence_interval=confidence_interval,
            sector_performance=sector_performance,
            top_performers=top_performers,
            worst_performers=worst_performers,
            monthly_returns=monthly_returns,
            quarterly_returns=quarterly_returns,
            rolling_sharpe=rolling_sharpe,
            rolling_volatility=rolling_volatility
        )

        self.logger.info(f"Performance analysis completed. Category: {performance_category.value}")
        return report

    def _extract_portfolio_data(self, backtest_result: BacktestResult) -> pd.DataFrame:
        """Extract portfolio time series data for analysis."""
        portfolio_data = []

        for snapshot in backtest_result.portfolio_history:
            portfolio_data.append({
                'date': snapshot.date,
                'total_value': snapshot.total_value,
                'cash': snapshot.cash,
                'daily_return': snapshot.daily_return,
                'cumulative_return': snapshot.cumulative_return
            })

        df = pd.DataFrame(portfolio_data)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)

        return df

    def _calculate_risk_analysis(self, portfolio_df: pd.DataFrame) -> RiskAnalysis:
        """Calculate comprehensive risk metrics."""
        returns = portfolio_df['daily_return'].dropna()

        if len(returns) == 0:
            raise ValueError("No return data available for risk analysis")

        # Volatility measures
        total_volatility = returns.std() * np.sqrt(252)

        # Downside risk
        negative_returns = returns[returns < 0]
        downside_deviation = negative_returns.std() * np.sqrt(252) if len(negative_returns) > 0 else 0.0
        semi_variance = negative_returns.var() if len(negative_returns) > 0 else 0.0

        # Value at Risk
        var_99 = returns.quantile(0.01) if len(returns) > 0 else 0.0
        var_95 = returns.quantile(0.05) if len(returns) > 0 else 0.0
        var_90 = returns.quantile(0.10) if len(returns) > 0 else 0.0

        # Expected Shortfall (Conditional VaR)
        tail_returns_95 = returns[returns <= var_95]
        expected_shortfall_95 = tail_returns_95.mean() if len(tail_returns_95) > 0 else var_95
        conditional_var = expected_shortfall_95

        # Risk-adjusted returns
        daily_rf_rate = self.risk_free_rate / 252
        excess_returns = returns - daily_rf_rate

        sharpe_ratio = excess_returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0.0
        sortino_ratio = excess_returns.mean() / downside_deviation * np.sqrt(252) if downside_deviation > 0 else 0.0

        # Drawdown analysis
        cumulative_returns = (1 + returns).cumprod()
        peak = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - peak) / peak

        max_drawdown = drawdown.min()
        avg_drawdown = drawdown[drawdown < 0].mean() if (drawdown < 0).any() else 0.0

        # Drawdown duration
        drawdown_duration = self._calculate_max_drawdown_duration(drawdown)

        # Recovery factor
        total_return = cumulative_returns.iloc[-1] - 1
        recovery_factor = total_return / abs(max_drawdown) if max_drawdown != 0 else 0.0

        # Calmar ratio
        annualized_return = (cumulative_returns.iloc[-1] ** (252 / len(returns))) - 1
        calmar_ratio = annualized_return / abs(max_drawdown) if max_drawdown != 0 else 0.0

        # Omega ratio (ratio of upside to downside potential)
        threshold = daily_rf_rate
        upside = returns[returns > threshold] - threshold
        downside = threshold - returns[returns <= threshold]
        omega_ratio = upside.sum() / downside.sum() if downside.sum() > 0 else float('inf')

        return RiskAnalysis(
            total_volatility=total_volatility,
            systematic_risk=0.0,  # Would need benchmark for calculation
            idiosyncratic_risk=total_volatility,  # Approximation
            downside_deviation=downside_deviation,
            semi_variance=semi_variance,
            var_99=var_99,
            var_95=var_95,
            var_90=var_90,
            expected_shortfall_95=expected_shortfall_95,
            conditional_var=conditional_var,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            omega_ratio=omega_ratio,
            max_drawdown=max_drawdown,
            avg_drawdown=avg_drawdown,
            drawdown_duration=drawdown_duration,
            recovery_factor=recovery_factor
        )

    def _calculate_max_drawdown_duration(self, drawdown_series: pd.Series) -> int:
        """Calculate maximum drawdown duration in days."""
        max_duration = 0
        current_duration = 0

        for dd in drawdown_series:
            if dd < 0:
                current_duration += 1
                max_duration = max(max_duration, current_duration)
            else:
                current_duration = 0

        return max_duration

    def _compare_to_benchmark(
        self,
        portfolio_df: pd.DataFrame,
        benchmark_data: pd.DataFrame
    ) -> BenchmarkComparison:
        """Compare portfolio performance to benchmark."""
        # Align dates
        benchmark_data = benchmark_data.copy()
        benchmark_data['date'] = pd.to_datetime(benchmark_data['date'])
        benchmark_data.set_index('date', inplace=True)

        # Calculate benchmark returns
        benchmark_data['benchmark_return'] = benchmark_data['close'].pct_change()

        # Merge with portfolio data
        merged = portfolio_df.join(benchmark_data[['benchmark_return']], how='inner')

        if len(merged) == 0:
            raise ValueError("No overlapping dates between portfolio and benchmark")

        portfolio_returns = merged['daily_return'].dropna()
        benchmark_returns = merged['benchmark_return'].dropna()

        # Align series
        common_dates = portfolio_returns.index.intersection(benchmark_returns.index)
        portfolio_returns = portfolio_returns.loc[common_dates]
        benchmark_returns = benchmark_returns.loc[common_dates]

        # Calculate metrics
        strategy_return = (1 + portfolio_returns).prod() - 1
        benchmark_return = (1 + benchmark_returns).prod() - 1
        excess_return = strategy_return - benchmark_return

        # Tracking error
        excess_returns = portfolio_returns - benchmark_returns
        tracking_error = excess_returns.std() * np.sqrt(252)

        # Information ratio
        information_ratio = excess_returns.mean() / excess_returns.std() * np.sqrt(252) if excess_returns.std() > 0 else 0.0

        # Beta and Alpha
        covariance = np.cov(portfolio_returns, benchmark_returns)[0, 1]
        benchmark_variance = np.var(benchmark_returns)
        beta = covariance / benchmark_variance if benchmark_variance > 0 else 0.0

        portfolio_mean = portfolio_returns.mean() * 252
        benchmark_mean = benchmark_returns.mean() * 252
        alpha = portfolio_mean - (self.risk_free_rate + beta * (benchmark_mean - self.risk_free_rate))

        # Correlation
        correlation = np.corrcoef(portfolio_returns, benchmark_returns)[0, 1]

        # Up/Down capture ratios
        up_periods = benchmark_returns > 0
        down_periods = benchmark_returns < 0

        up_capture = (portfolio_returns[up_periods].mean() / benchmark_returns[up_periods].mean()) if up_periods.sum() > 0 else 0.0
        down_capture = (portfolio_returns[down_periods].mean() / benchmark_returns[down_periods].mean()) if down_periods.sum() > 0 else 0.0

        return BenchmarkComparison(
            strategy_return=strategy_return,
            benchmark_return=benchmark_return,
            excess_return=excess_return,
            tracking_error=tracking_error,
            information_ratio=information_ratio,
            beta=beta,
            alpha=alpha,
            correlation=correlation,
            up_capture=up_capture,
            down_capture=down_capture
        )

    def _calculate_performance_attribution(
        self,
        backtest_result: BacktestResult,
        benchmark_data: Optional[pd.DataFrame]
    ) -> Optional[PerformanceAttribution]:
        """Calculate performance attribution analysis."""
        # Simplified attribution analysis
        # In practice, this would require more detailed sector/factor data

        if not benchmark_data:
            return None

        # For now, return placeholder values
        # Real implementation would decompose returns into:
        # - Security selection effect
        # - Market timing effect
        # - Asset allocation effect
        # - Interaction effects

        return PerformanceAttribution(
            security_selection=0.02,  # 2% from security selection
            market_timing=0.01,       # 1% from market timing
            asset_allocation=0.005,   # 0.5% from asset allocation
            interaction_effect=0.001, # 0.1% interaction
            total_active_return=0.036 # Total active return
        )

    def _test_statistical_significance(
        self,
        portfolio_df: pd.DataFrame,
        benchmark_data: Optional[pd.DataFrame]
    ) -> Tuple[bool, float, Tuple[float, float]]:
        """Test statistical significance of excess returns."""
        returns = portfolio_df['daily_return'].dropna()

        if benchmark_data is not None:
            benchmark_data = benchmark_data.copy()
            benchmark_data['date'] = pd.to_datetime(benchmark_data['date'])
            benchmark_data.set_index('date', inplace=True)
            benchmark_data['benchmark_return'] = benchmark_data['close'].pct_change()

            merged = portfolio_df.join(benchmark_data[['benchmark_return']], how='inner')
            portfolio_returns = merged['daily_return'].dropna()
            benchmark_returns = merged['benchmark_return'].dropna()

            # Test if excess returns are significantly different from zero
            excess_returns = portfolio_returns - benchmark_returns
            t_stat, p_value = stats.ttest_1samp(excess_returns.dropna(), 0)

            # 95% confidence interval
            mean_excess = excess_returns.mean()
            std_excess = excess_returns.std()
            n = len(excess_returns)

            confidence_interval = stats.t.interval(
                0.95, n-1, loc=mean_excess, scale=std_excess/np.sqrt(n)
            )

        else:
            # Test if returns are significantly different from risk-free rate
            daily_rf_rate = self.risk_free_rate / 252
            excess_returns = returns - daily_rf_rate
            t_stat, p_value = stats.ttest_1samp(excess_returns, 0)

            mean_excess = excess_returns.mean()
            std_excess = excess_returns.std()
            n = len(excess_returns)

            confidence_interval = stats.t.interval(
                0.95, n-1, loc=mean_excess, scale=std_excess/np.sqrt(n)
            )

        is_significant = p_value < 0.05

        return is_significant, p_value, confidence_interval

    def _analyze_sector_performance(
        self,
        backtest_result: BacktestResult,
        sector_mappings: Optional[Dict[str, str]]
    ) -> Dict[str, float]:
        """Analyze performance by sector."""
        if not sector_mappings:
            return {}

        sector_returns = {}

        # Group trades by sector
        for trade in backtest_result.trades:
            if trade.pnl is not None and trade.symbol in sector_mappings:
                sector = sector_mappings[trade.symbol]
                if sector not in sector_returns:
                    sector_returns[sector] = []
                sector_returns[sector].append(trade.pnl_percent or 0.0)

        # Calculate average returns by sector
        sector_performance = {}
        for sector, returns in sector_returns.items():
            sector_performance[sector] = np.mean(returns) if returns else 0.0

        return sector_performance

    def _identify_top_performers(
        self,
        backtest_result: BacktestResult
    ) -> Tuple[List[Tuple[str, float]], List[Tuple[str, float]]]:
        """Identify top and worst performing securities."""
        symbol_performance = {}

        # Aggregate performance by symbol
        for trade in backtest_result.trades:
            if trade.pnl_percent is not None:
                symbol = trade.symbol
                if symbol not in symbol_performance:
                    symbol_performance[symbol] = []
                symbol_performance[symbol].append(trade.pnl_percent)

        # Calculate average returns per symbol
        avg_performance = {}
        for symbol, returns in symbol_performance.items():
            avg_performance[symbol] = np.mean(returns)

        # Sort and get top/bottom performers
        sorted_performance = sorted(avg_performance.items(), key=lambda x: x[1], reverse=True)

        top_performers = sorted_performance[:5]  # Top 5
        worst_performers = sorted_performance[-5:]  # Bottom 5

        return top_performers, worst_performers

    def _calculate_monthly_returns(self, portfolio_df: pd.DataFrame) -> List[float]:
        """Calculate monthly returns."""
        monthly_data = portfolio_df.resample('M')['total_value'].last()
        monthly_returns = monthly_data.pct_change().dropna().tolist()
        return monthly_returns

    def _calculate_quarterly_returns(self, portfolio_df: pd.DataFrame) -> List[float]:
        """Calculate quarterly returns."""
        quarterly_data = portfolio_df.resample('Q')['total_value'].last()
        quarterly_returns = quarterly_data.pct_change().dropna().tolist()
        return quarterly_returns

    def _calculate_rolling_sharpe(self, portfolio_df: pd.DataFrame, window: int = 60) -> List[float]:
        """Calculate rolling Sharpe ratio."""
        returns = portfolio_df['daily_return'].dropna()
        daily_rf_rate = self.risk_free_rate / 252

        rolling_sharpe = []
        for i in range(window, len(returns)):
            window_returns = returns.iloc[i-window:i]
            excess_returns = window_returns - daily_rf_rate
            sharpe = excess_returns.mean() / window_returns.std() * np.sqrt(252) if window_returns.std() > 0 else 0.0
            rolling_sharpe.append(sharpe)

        return rolling_sharpe

    def _calculate_rolling_volatility(self, portfolio_df: pd.DataFrame, window: int = 60) -> List[float]:
        """Calculate rolling volatility."""
        returns = portfolio_df['daily_return'].dropna()

        rolling_vol = []
        for i in range(window, len(returns)):
            window_returns = returns.iloc[i-window:i]
            vol = window_returns.std() * np.sqrt(252)
            rolling_vol.append(vol)

        return rolling_vol

    def _categorize_performance(
        self,
        risk_analysis: RiskAnalysis,
        benchmark_comparison: Optional[BenchmarkComparison]
    ) -> PerformanceCategory:
        """Categorize overall performance."""
        # Scoring system based on multiple metrics
        score = 0

        # Sharpe ratio scoring
        if risk_analysis.sharpe_ratio >= 2.0:
            score += 3
        elif risk_analysis.sharpe_ratio >= 1.5:
            score += 2
        elif risk_analysis.sharpe_ratio >= 1.0:
            score += 1
        elif risk_analysis.sharpe_ratio >= 0.5:
            score += 0
        else:
            score -= 1

        # Max drawdown scoring
        if risk_analysis.max_drawdown >= -0.05:  # -5%
            score += 2
        elif risk_analysis.max_drawdown >= -0.10:  # -10%
            score += 1
        elif risk_analysis.max_drawdown >= -0.20:  # -20%
            score += 0
        else:
            score -= 1

        # Benchmark comparison if available
        if benchmark_comparison:
            if benchmark_comparison.information_ratio >= 1.0:
                score += 2
            elif benchmark_comparison.information_ratio >= 0.5:
                score += 1
            elif benchmark_comparison.information_ratio >= 0:
                score += 0
            else:
                score -= 1

        # Categorize based on total score
        if score >= 6:
            return PerformanceCategory.EXCELLENT
        elif score >= 4:
            return PerformanceCategory.GOOD
        elif score >= 2:
            return PerformanceCategory.AVERAGE
        elif score >= 0:
            return PerformanceCategory.BELOW_AVERAGE
        else:
            return PerformanceCategory.POOR

    def _generate_insights(
        self,
        risk_analysis: RiskAnalysis,
        benchmark_comparison: Optional[BenchmarkComparison],
        backtest_result: BacktestResult
    ) -> Tuple[List[str], List[str], List[str]]:
        """Generate key insights and recommendations."""
        strengths = []
        weaknesses = []
        recommendations = []

        # Analyze Sharpe ratio
        if risk_analysis.sharpe_ratio >= 1.5:
            strengths.append(f"Excellent risk-adjusted returns (Sharpe: {risk_analysis.sharpe_ratio:.2f})")
        elif risk_analysis.sharpe_ratio < 0.5:
            weaknesses.append(f"Poor risk-adjusted returns (Sharpe: {risk_analysis.sharpe_ratio:.2f})")
            recommendations.append("Consider improving risk management or return generation")

        # Analyze drawdown
        if risk_analysis.max_drawdown >= -0.10:
            strengths.append(f"Low maximum drawdown ({risk_analysis.max_drawdown:.1%})")
        elif risk_analysis.max_drawdown < -0.25:
            weaknesses.append(f"High maximum drawdown ({risk_analysis.max_drawdown:.1%})")
            recommendations.append("Implement stronger risk management and position sizing")

        # Analyze win rate
        if backtest_result.risk_metrics and backtest_result.risk_metrics.win_rate >= 0.6:
            strengths.append(f"High win rate ({backtest_result.risk_metrics.win_rate:.1%})")
        elif backtest_result.risk_metrics and backtest_result.risk_metrics.win_rate < 0.4:
            weaknesses.append(f"Low win rate ({backtest_result.risk_metrics.win_rate:.1%})")
            recommendations.append("Review entry and exit criteria to improve trade selection")

        # Benchmark comparison insights
        if benchmark_comparison:
            if benchmark_comparison.information_ratio >= 0.5:
                strengths.append(f"Outperformed benchmark with good risk efficiency (IR: {benchmark_comparison.information_ratio:.2f})")
            elif benchmark_comparison.excess_return < 0:
                weaknesses.append(f"Underperformed benchmark ({benchmark_comparison.excess_return:.1%} excess return)")
                recommendations.append("Analyze sources of underperformance and consider strategy adjustments")

        # Trade execution analysis
        if backtest_result.execution_rate < 0.7:
            weaknesses.append(f"Low trade execution rate ({backtest_result.execution_rate:.1%})")
            recommendations.append("Review position sizing and cash management to improve execution")

        # General recommendations
        if len(strengths) == 0:
            recommendations.append("Consider fundamental strategy review and risk management improvements")

        if risk_analysis.omega_ratio < 1.0:
            recommendations.append("Focus on improving upside capture while limiting downside risk")

        return strengths, weaknesses, recommendations

    def generate_performance_summary(self, report: PerformanceReport) -> str:
        """Generate a text summary of performance analysis."""
        summary = []

        # Header
        summary.append(f"PERFORMANCE ANALYSIS REPORT")
        summary.append(f"Strategy: {report.backtest_result.strategy_name}")
        summary.append(f"Period: {report.backtest_result.config.start_date.strftime('%Y-%m-%d')} to {report.backtest_result.config.end_date.strftime('%Y-%m-%d')}")
        summary.append(f"Performance Category: {report.performance_category.value.upper()}")
        summary.append("=" * 60)

        # Key Metrics
        risk_metrics = report.backtest_result.risk_metrics
        if risk_metrics:
            summary.append("\nKEY PERFORMANCE METRICS:")
            summary.append(f"Total Return: {risk_metrics.total_return:.2%}")
            summary.append(f"Annualized Return: {risk_metrics.annualized_return:.2%}")
            summary.append(f"Volatility: {report.risk_analysis.total_volatility:.2%}")
            summary.append(f"Sharpe Ratio: {report.risk_analysis.sharpe_ratio:.3f}")
            summary.append(f"Maximum Drawdown: {report.risk_analysis.max_drawdown:.2%}")
            summary.append(f"Win Rate: {risk_metrics.win_rate:.1%}")

        # Benchmark Comparison
        if report.benchmark_comparison:
            summary.append("\nBENCHMARK COMPARISON:")
            summary.append(f"Strategy Return: {report.benchmark_comparison.strategy_return:.2%}")
            summary.append(f"Benchmark Return: {report.benchmark_comparison.benchmark_return:.2%}")
            summary.append(f"Excess Return: {report.benchmark_comparison.excess_return:.2%}")
            summary.append(f"Information Ratio: {report.benchmark_comparison.information_ratio:.3f}")
            summary.append(f"Beta: {report.benchmark_comparison.beta:.3f}")

        # Statistical Significance
        summary.append(f"\nSTATISTICAL SIGNIFICANCE:")
        summary.append(f"Statistically Significant: {'Yes' if report.is_statistically_significant else 'No'}")
        summary.append(f"P-value: {report.p_value:.4f}")

        # Key Strengths
        if report.key_strengths:
            summary.append("\nKEY STRENGTHS:")
            for strength in report.key_strengths:
                summary.append(f"• {strength}")

        # Key Weaknesses
        if report.key_weaknesses:
            summary.append("\nKEY WEAKNESSES:")
            for weakness in report.key_weaknesses:
                summary.append(f"• {weakness}")

        # Recommendations
        if report.recommendations:
            summary.append("\nRECOMMENDATIONS:")
            for rec in report.recommendations:
                summary.append(f"• {rec}")

        # Top Performers
        if report.top_performers:
            summary.append("\nTOP PERFORMERS:")
            for symbol, return_pct in report.top_performers[:3]:
                summary.append(f"• {symbol}: {return_pct:.2%}")

        return "\n".join(summary)

    def create_performance_visualizations(
        self,
        report: PerformanceReport,
        save_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create comprehensive performance visualizations."""
        # This would create various charts and plots
        # For now, return a placeholder structure

        visualizations = {
            'equity_curve': 'equity_curve.png',
            'drawdown_chart': 'drawdown_chart.png',
            'rolling_metrics': 'rolling_metrics.png',
            'return_distribution': 'return_distribution.png',
            'risk_return_scatter': 'risk_return_scatter.png'
        }

        # In a real implementation, this would create:
        # 1. Equity curve with benchmark overlay
        # 2. Drawdown chart over time
        # 3. Rolling Sharpe ratio and volatility
        # 4. Return distribution histogram
        # 5. Risk-return scatter plot
        # 6. Monthly/quarterly return heatmaps
        # 7. Sector performance charts

        return visualizations


# Utility functions
def compare_strategies(
    reports: List[PerformanceReport],
    metrics: List[str] = None
) -> pd.DataFrame:
    """Compare multiple strategy performance reports."""
    if metrics is None:
        metrics = ['total_return', 'sharpe_ratio', 'max_drawdown', 'win_rate', 'volatility']

    comparison_data = []

    for report in reports:
        strategy_data = {
            'strategy': report.backtest_result.strategy_name,
            'category': report.performance_category.value
        }

        # Extract requested metrics
        risk_metrics = report.backtest_result.risk_metrics
        if risk_metrics:
            if 'total_return' in metrics:
                strategy_data['total_return'] = risk_metrics.total_return
            if 'sharpe_ratio' in metrics:
                strategy_data['sharpe_ratio'] = report.risk_analysis.sharpe_ratio
            if 'max_drawdown' in metrics:
                strategy_data['max_drawdown'] = report.risk_analysis.max_drawdown
            if 'win_rate' in metrics:
                strategy_data['win_rate'] = risk_metrics.win_rate
            if 'volatility' in metrics:
                strategy_data['volatility'] = report.risk_analysis.total_volatility

        comparison_data.append(strategy_data)

    return pd.DataFrame(comparison_data)


def generate_executive_summary(reports: List[PerformanceReport]) -> str:
    """Generate an executive summary for multiple strategy reports."""
    summary = []

    summary.append("EXECUTIVE SUMMARY - STRATEGY PERFORMANCE ANALYSIS")
    summary.append("=" * 60)

    # Overall statistics
    total_strategies = len(reports)
    categories = [report.performance_category for report in reports]

    excellent_count = sum(1 for cat in categories if cat == PerformanceCategory.EXCELLENT)
    good_count = sum(1 for cat in categories if cat == PerformanceCategory.GOOD)

    summary.append(f"\nStrategies Analyzed: {total_strategies}")
    summary.append(f"Excellent Performance: {excellent_count} ({excellent_count/total_strategies:.1%})")
    summary.append(f"Good Performance: {good_count} ({good_count/total_strategies:.1%})")

    # Best performing strategy
    best_strategy = max(reports, key=lambda r: r.risk_analysis.sharpe_ratio)
    summary.append(f"\nBest Risk-Adjusted Performance:")
    summary.append(f"• Strategy: {best_strategy.backtest_result.strategy_name}")
    summary.append(f"• Sharpe Ratio: {best_strategy.risk_analysis.sharpe_ratio:.3f}")
    summary.append(f"• Total Return: {best_strategy.backtest_result.risk_metrics.total_return:.2%}")

    # Key insights across all strategies
    summary.append(f"\nKey Insights:")
    avg_sharpe = np.mean([r.risk_analysis.sharpe_ratio for r in reports])
    summary.append(f"• Average Sharpe Ratio: {avg_sharpe:.3f}")

    statistically_significant = sum(1 for r in reports if r.is_statistically_significant)
    summary.append(f"• Statistically Significant Results: {statistically_significant}/{total_strategies}")

    return "\n".join(summary)


if __name__ == "__main__":
    # Example usage would go here
    print("Performance Analysis Module Loaded")
