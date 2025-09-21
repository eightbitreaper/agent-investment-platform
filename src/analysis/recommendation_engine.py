"""
Recommendation Engine for the Agent Investment Platform.

This module combines sentiment analysis, technical analysis, and fundamental analysis
to generate comprehensive investment recommendations. It leverages all analysis
components to provide unified buy/sell/hold decisions with confidence scores.

Key Features:
- Multi-factor analysis combining sentiment, technical, and fundamental data
- Strategy-aware recommendations based on user's investment approach
- Risk assessment and position sizing recommendations
- Confidence scoring and uncertainty quantification
- Integration with all existing analysis components
- Support for different time horizons and risk tolerances
"""

import asyncio
import logging
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import yaml

try:
    import pandas as pd
    import numpy as np
    import yaml
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Please install required packages: pip install pandas numpy pyyaml")

from .sentiment_analyzer import FinancialSentimentAnalyzer, MarketSentiment, SentimentScore
from .chart_analyzer import TechnicalChartAnalyzer, TechnicalAnalysis, TrendDirection, SignalStrength


class RecommendationType(Enum):
    """Investment recommendation types."""
    STRONG_BUY = 2
    BUY = 1
    HOLD = 0
    SELL = -1
    STRONG_SELL = -2


class ConfidenceLevel(Enum):
    """Confidence level in recommendation."""
    VERY_LOW = 1
    LOW = 2
    MODERATE = 3
    HIGH = 4
    VERY_HIGH = 5


@dataclass
class AnalysisWeights:
    """Weights for different analysis components."""
    technical: float = 0.4
    sentiment: float = 0.3
    fundamental: float = 0.3

    def __post_init__(self):
        """Normalize weights to sum to 1.0."""
        total = self.technical + self.sentiment + self.fundamental
        if total != 1.0:
            self.technical /= total
            self.sentiment /= total
            self.fundamental /= total


@dataclass
class RiskMetrics:
    """Risk assessment metrics for a recommendation."""
    volatility_score: float  # 0.0 to 1.0 (higher = more volatile)
    beta: Optional[float]  # Market beta
    max_drawdown_risk: float  # Estimated maximum drawdown risk
    liquidity_risk: float  # 0.0 to 1.0 (higher = less liquid)
    concentration_risk: float  # Portfolio concentration risk
    overall_risk_score: float  # 0.0 to 1.0 (higher = riskier)


@dataclass
class PositionSizing:
    """Position sizing recommendations."""
    recommended_allocation: float  # Percentage of portfolio (0.0 to 1.0)
    max_position_size: float  # Maximum recommended position size
    suggested_entry_price: Optional[float]  # Suggested entry price
    stop_loss_price: Optional[float]  # Suggested stop loss
    take_profit_price: Optional[float]  # Suggested take profit
    time_horizon: str  # "short_term", "medium_term", "long_term"


@dataclass
class InvestmentRecommendation:
    """Comprehensive investment recommendation."""
    symbol: str
    recommendation: RecommendationType
    confidence: ConfidenceLevel
    target_price: Optional[float]
    current_price: float

    # Analysis scores (normalized -1.0 to 1.0)
    technical_score: float
    sentiment_score: float
    fundamental_score: Optional[float]
    composite_score: float

    # Risk and sizing
    risk_metrics: RiskMetrics
    position_sizing: PositionSizing

    # Supporting analysis
    technical_analysis: Optional[TechnicalAnalysis]
    market_sentiment: Optional[MarketSentiment]
    strategy_alignment: float  # How well it fits the chosen strategy

    # Metadata
    analysis_timestamp: datetime
    data_freshness: Dict[str, datetime]  # When each data source was last updated
    reasoning: List[str]  # Human-readable reasoning points
    warnings: List[str]  # Risk warnings and caveats

    # Strategy context
    strategy_name: str
    time_horizon: str
    risk_tolerance: str


class RecommendationEngine:
    """
    Unified recommendation engine combining all analysis components.

    This class orchestrates sentiment analysis, technical analysis, and
    fundamental analysis to generate comprehensive investment recommendations
    tailored to specific investment strategies and risk profiles.
    """

    def __init__(self, config_path: str = "config/strategies.yaml"):
        """
        Initialize recommendation engine.

        Args:
            config_path: Path to strategies configuration file
        """
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path
        self.strategies_config = self._load_strategies_config()

        # Initialize analysis components
        self.sentiment_analyzer = FinancialSentimentAnalyzer()
        self.chart_analyzer = TechnicalChartAnalyzer()

        # Default analysis weights (can be overridden by strategy)
        self.default_weights = AnalysisWeights()

        self.logger.info("Recommendation engine initialized successfully")

    def _load_strategies_config(self) -> Dict[str, Any]:
        """Load investment strategies configuration."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                self.logger.info(f"Loaded strategies configuration from {self.config_path}")
                return config
        except Exception as e:
            self.logger.error(f"Failed to load strategies config: {e}")
            return {}

    async def analyze_investment(
        self,
        symbol: str,
        strategy_name: str = "balanced_growth",
        price_data: Optional[pd.DataFrame] = None,
        news_data: Optional[List[Dict]] = None,
        fundamental_data: Optional[Dict] = None,
        custom_weights: Optional[AnalysisWeights] = None
    ) -> InvestmentRecommendation:
        """
        Generate comprehensive investment recommendation.

        Args:
            symbol: Stock symbol to analyze
            strategy_name: Investment strategy to use
            price_data: Historical price data
            news_data: Recent news articles for sentiment analysis
            fundamental_data: Fundamental analysis data
            custom_weights: Custom analysis weights

        Returns:
            Comprehensive investment recommendation
        """
        self.logger.info(f"Analyzing investment for {symbol} using {strategy_name} strategy")

        start_time = datetime.now()
        analysis_timestamp = start_time
        data_freshness = {}
        reasoning = []
        warnings = []

        # Get strategy configuration
        strategy_config = self._get_strategy_config(strategy_name)
        weights = custom_weights or self._get_strategy_weights(strategy_config)

        # Initialize scores
        technical_score = 0.0
        sentiment_score = 0.0
        fundamental_score = None

        # 1. Technical Analysis
        technical_analysis = None
        if price_data is not None and not price_data.empty:
            try:
                technical_analysis = await self.chart_analyzer.analyze_chart(
                    symbol=symbol,
                    price_data=price_data
                )
                technical_score = self._convert_technical_to_score(technical_analysis)
                data_freshness['technical'] = analysis_timestamp
                reasoning.append(f"Technical analysis shows {technical_analysis.trend_direction.name.lower()} trend")

                self.logger.debug(f"Technical analysis completed for {symbol}: score {technical_score:.3f}")

            except Exception as e:
                self.logger.warning(f"Technical analysis failed for {symbol}: {e}")
                warnings.append("Technical analysis data unavailable or incomplete")
        else:
            warnings.append("No price data available for technical analysis")

        # 2. Sentiment Analysis
        market_sentiment = None
        if news_data:
            try:
                # Process news articles
                sentiment_results = []
                for article in news_data[:20]:  # Limit to recent 20 articles
                    content = f"{article.get('title', '')} {article.get('description', '')}"
                    if content.strip():
                        result = await self.sentiment_analyzer.analyze_text(
                            text=content,
                            source=article.get('source', 'news')
                        )
                        sentiment_results.append(result)

                if sentiment_results:
                    market_sentiment = await self.sentiment_analyzer.analyze_symbol_sentiment(
                        symbol=symbol,
                        articles=[{'title': '', 'description': '', 'content': r.text} for r in sentiment_results]
                    )
                    sentiment_score = market_sentiment.overall_score
                    data_freshness['sentiment'] = analysis_timestamp
                    reasoning.append(f"Market sentiment score: {sentiment_score:.2f}")

                    self.logger.debug(f"Sentiment analysis completed for {symbol}: score {sentiment_score:.3f}")

            except Exception as e:
                self.logger.warning(f"Sentiment analysis failed for {symbol}: {e}")
                warnings.append("Sentiment analysis data unavailable or incomplete")
        else:
            warnings.append("No news data available for sentiment analysis")

        # 3. Fundamental Analysis (placeholder - to be enhanced)
        if fundamental_data:
            try:
                fundamental_score = self._analyze_fundamentals(fundamental_data, strategy_config)
                data_freshness['fundamental'] = analysis_timestamp
                reasoning.append("Fundamental analysis incorporated")
            except Exception as e:
                self.logger.warning(f"Fundamental analysis failed for {symbol}: {e}")
                warnings.append("Fundamental analysis data unavailable or incomplete")

        # 4. Composite Score Calculation
        composite_score = self._calculate_composite_score(
            technical_score=technical_score,
            sentiment_score=sentiment_score,
            fundamental_score=fundamental_score,
            weights=weights
        )

        # 5. Generate Recommendation
        recommendation_type = self._score_to_recommendation(composite_score, strategy_config)
        confidence = self._calculate_confidence(
            technical_analysis=technical_analysis,
            market_sentiment=market_sentiment,
            data_availability=data_freshness
        )

        # 6. Risk Assessment
        risk_metrics = self._assess_risk(
            symbol=symbol,
            technical_analysis=technical_analysis,
            price_data=price_data,
            strategy_config=strategy_config
        )

        # 7. Position Sizing
        position_sizing = self._calculate_position_sizing(
            recommendation_type=recommendation_type,
            risk_metrics=risk_metrics,
            strategy_config=strategy_config,
            current_price=price_data.iloc[-1]['close'].item() if price_data is not None and not price_data.empty else None
        )

        # 8. Strategy Alignment
        strategy_alignment = self._calculate_strategy_alignment(
            composite_score=composite_score,
            technical_analysis=technical_analysis,
            strategy_config=strategy_config
        )

        # 9. Target Price Calculation
        target_price = self._calculate_target_price(
            current_price=position_sizing.suggested_entry_price or (price_data.iloc[-1]['close'].item() if price_data is not None and not price_data.empty else None),
            technical_analysis=technical_analysis,
            recommendation_type=recommendation_type
        )

        # Create final recommendation
        recommendation = InvestmentRecommendation(
            symbol=symbol,
            recommendation=recommendation_type,
            confidence=confidence,
            target_price=target_price,
            current_price=price_data.iloc[-1]['close'].item() if price_data is not None and not price_data.empty else 0.0,
            technical_score=technical_score,
            sentiment_score=sentiment_score,
            fundamental_score=fundamental_score,
            composite_score=composite_score,
            risk_metrics=risk_metrics,
            position_sizing=position_sizing,
            technical_analysis=technical_analysis,
            market_sentiment=market_sentiment,
            strategy_alignment=strategy_alignment,
            analysis_timestamp=analysis_timestamp,
            data_freshness=data_freshness,
            reasoning=reasoning,
            warnings=warnings,
            strategy_name=strategy_name,
            time_horizon=strategy_config.get('time_horizon', 'medium_term'),
            risk_tolerance=strategy_config.get('risk_level', 'moderate')
        )

        duration = (datetime.now() - start_time).total_seconds()
        self.logger.info(f"Analysis completed for {symbol} in {duration:.2f}s: {recommendation_type.name}")

        return recommendation

    def _get_strategy_config(self, strategy_name: str) -> Dict[str, Any]:
        """Get configuration for specified strategy."""
        strategies = self.strategies_config.get('strategies', {})
        if strategy_name in strategies:
            return strategies[strategy_name]

        # Fallback to default strategy
        default_name = self.strategies_config.get('default_strategy', {}).get('name', 'balanced_growth')
        if default_name in strategies:
            self.logger.warning(f"Strategy '{strategy_name}' not found, using default '{default_name}'")
            return strategies[default_name]

        # Ultimate fallback
        self.logger.warning(f"Neither '{strategy_name}' nor default strategy found, using conservative defaults")
        return {
            'name': 'Conservative Default',
            'risk_level': 'low',
            'time_horizon': 'long_term',
            'analysis_weights': {'technical': 0.4, 'sentiment': 0.3, 'fundamental': 0.3}
        }

    def _get_strategy_weights(self, strategy_config: Dict[str, Any]) -> AnalysisWeights:
        """Get analysis weights for strategy."""
        weights_config = strategy_config.get('analysis_weights', {})
        return AnalysisWeights(
            technical=weights_config.get('technical', 0.4),
            sentiment=weights_config.get('sentiment', 0.3),
            fundamental=weights_config.get('fundamental', 0.3)
        )

    def _convert_technical_to_score(self, technical_analysis: TechnicalAnalysis) -> float:
        """Convert technical analysis to normalized score (-1.0 to 1.0)."""
        if not technical_analysis:
            return 0.0

        # Weight different aspects of technical analysis
        trend_score = self._trend_to_score(technical_analysis.trend_direction)
        momentum_score = technical_analysis.trend_strength / 100.0  # Normalize to -1 to 1

        # Combine indicators
        bullish_signals = sum(1 for indicator in technical_analysis.indicators if indicator.signal == 'BUY')
        bearish_signals = sum(1 for indicator in technical_analysis.indicators if indicator.signal == 'SELL')
        total_signals = len(technical_analysis.indicators)

        signal_score = 0.0
        if total_signals > 0:
            signal_score = (bullish_signals - bearish_signals) / total_signals

        # Weighted combination
        score = 0.4 * trend_score + 0.3 * momentum_score + 0.3 * signal_score
        return max(-1.0, min(1.0, score))

    def _trend_to_score(self, trend: TrendDirection) -> float:
        """Convert trend direction to score."""
        mapping = {
            TrendDirection.STRONG_BEARISH: -1.0,
            TrendDirection.BEARISH: -0.5,
            TrendDirection.SIDEWAYS: 0.0,
            TrendDirection.BULLISH: 0.5,
            TrendDirection.STRONG_BULLISH: 1.0
        }
        return mapping.get(trend, 0.0)

    def _analyze_fundamentals(self, fundamental_data: Dict, strategy_config: Dict) -> float:
        """
        Analyze fundamental data (placeholder implementation).

        This is a simplified fundamental analysis. In a production system,
        this would include comprehensive financial metrics analysis.
        """
        score = 0.0

        # P/E Ratio analysis
        pe_ratio = fundamental_data.get('pe_ratio')
        if pe_ratio:
            max_pe = strategy_config.get('screening_criteria', {}).get('max_pe', 25)
            if pe_ratio <= max_pe:
                score += 0.2
            elif pe_ratio > max_pe * 1.5:
                score -= 0.2

        # Revenue growth
        revenue_growth = fundamental_data.get('revenue_growth')
        if revenue_growth:
            if revenue_growth > 0.1:  # 10% growth
                score += 0.3
            elif revenue_growth < 0:
                score -= 0.2

        # Profit margins
        profit_margin = fundamental_data.get('profit_margin')
        if profit_margin:
            if profit_margin > 0.1:  # 10% margin
                score += 0.2
            elif profit_margin < 0:
                score -= 0.3

        # Debt to equity
        debt_to_equity = fundamental_data.get('debt_to_equity')
        if debt_to_equity:
            max_debt = strategy_config.get('screening_criteria', {}).get('max_debt_to_equity', 0.5)
            if debt_to_equity <= max_debt:
                score += 0.2
            elif debt_to_equity > max_debt * 2:
                score -= 0.3

        return max(-1.0, min(1.0, score))

    def _calculate_composite_score(
        self,
        technical_score: float,
        sentiment_score: float,
        fundamental_score: Optional[float],
        weights: AnalysisWeights
    ) -> float:
        """Calculate weighted composite score."""
        if fundamental_score is not None:
            # All three components available
            return (
                weights.technical * technical_score +
                weights.sentiment * sentiment_score +
                weights.fundamental * fundamental_score
            )
        else:
            # Only technical and sentiment available, renormalize weights
            total_weight = weights.technical + weights.sentiment
            if total_weight > 0:
                tech_weight = weights.technical / total_weight
                sent_weight = weights.sentiment / total_weight
                return tech_weight * technical_score + sent_weight * sentiment_score
            else:
                return 0.0

    def _score_to_recommendation(self, score: float, strategy_config: Dict) -> RecommendationType:
        """Convert composite score to recommendation type."""
        risk_level = strategy_config.get('risk_level', 'moderate')

        # Adjust thresholds based on risk level
        if risk_level == 'low':
            # More conservative thresholds
            if score >= 0.6:
                return RecommendationType.BUY
            elif score >= 0.3:
                return RecommendationType.HOLD
            elif score <= -0.4:
                return RecommendationType.SELL
            else:
                return RecommendationType.HOLD
        elif risk_level == 'high':
            # More aggressive thresholds
            if score >= 0.4:
                return RecommendationType.STRONG_BUY if score >= 0.7 else RecommendationType.BUY
            elif score <= -0.3:
                return RecommendationType.STRONG_SELL if score <= -0.6 else RecommendationType.SELL
            else:
                return RecommendationType.HOLD
        else:
            # Moderate risk thresholds
            if score >= 0.5:
                return RecommendationType.BUY
            elif score >= 0.2:
                return RecommendationType.HOLD
            elif score <= -0.3:
                return RecommendationType.SELL
            else:
                return RecommendationType.HOLD

    def _calculate_confidence(
        self,
        technical_analysis: Optional[TechnicalAnalysis],
        market_sentiment: Optional[MarketSentiment],
        data_availability: Dict[str, datetime]
    ) -> ConfidenceLevel:
        """Calculate confidence level in recommendation."""
        confidence_score = 0

        # Data availability contributes to confidence
        available_sources = len(data_availability)
        confidence_score += available_sources * 0.2

        # Technical analysis confidence
        if technical_analysis:
            if technical_analysis.confidence > 0.8:
                confidence_score += 0.3
            elif technical_analysis.confidence > 0.6:
                confidence_score += 0.2

        # Sentiment analysis confidence
        if market_sentiment and market_sentiment.confidence > 0.7:
            confidence_score += 0.3
        elif market_sentiment and market_sentiment.confidence > 0.5:
            confidence_score += 0.2

        # Convert to confidence level
        if confidence_score >= 0.8:
            return ConfidenceLevel.VERY_HIGH
        elif confidence_score >= 0.6:
            return ConfidenceLevel.HIGH
        elif confidence_score >= 0.4:
            return ConfidenceLevel.MODERATE
        elif confidence_score >= 0.2:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW

    def _assess_risk(
        self,
        symbol: str,
        technical_analysis: Optional[TechnicalAnalysis],
        price_data: Optional[pd.DataFrame],
        strategy_config: Dict
    ) -> RiskMetrics:
        """Assess investment risk metrics."""
        # Calculate volatility from price data
        volatility_score = 0.5  # Default moderate volatility
        if price_data is not None and len(price_data) > 20:
            returns = price_data['close'].pct_change().dropna()
            volatility = returns.std() * math.sqrt(252)  # Annualized volatility
            volatility_score = min(1.0, volatility / 0.5)  # Normalize to 0-1 scale

        # Estimate beta (simplified - would need market data for accurate calculation)
        beta = 1.0  # Default market beta

        # Max drawdown risk based on volatility and technical signals
        max_drawdown_risk = volatility_score * 0.6
        if technical_analysis and technical_analysis.trend_direction in [TrendDirection.BEARISH, TrendDirection.STRONG_BEARISH]:
            max_drawdown_risk *= 1.5

        # Liquidity risk (simplified - would need volume data)
        liquidity_risk = 0.3  # Assume moderate liquidity for most stocks

        # Concentration risk based on strategy
        max_position = strategy_config.get('position_sizing', {}).get('max_single_position', 0.08)
        concentration_risk = max_position * 2  # Higher allowed position = higher concentration risk

        # Overall risk score
        overall_risk_score = (
            0.3 * volatility_score +
            0.2 * max_drawdown_risk +
            0.2 * liquidity_risk +
            0.3 * concentration_risk
        )

        return RiskMetrics(
            volatility_score=volatility_score,
            beta=beta,
            max_drawdown_risk=max_drawdown_risk,
            liquidity_risk=liquidity_risk,
            concentration_risk=concentration_risk,
            overall_risk_score=overall_risk_score
        )

    def _calculate_position_sizing(
        self,
        recommendation_type: RecommendationType,
        risk_metrics: RiskMetrics,
        strategy_config: Dict,
        current_price: Optional[float]
    ) -> PositionSizing:
        """Calculate position sizing recommendations."""
        # Base allocation based on recommendation strength
        base_allocation = {
            RecommendationType.STRONG_BUY: 0.08,
            RecommendationType.BUY: 0.05,
            RecommendationType.HOLD: 0.03,
            RecommendationType.SELL: 0.0,
            RecommendationType.STRONG_SELL: 0.0
        }.get(recommendation_type, 0.0)

        # Adjust for risk
        risk_adjustment = 1.0 - risk_metrics.overall_risk_score * 0.5
        recommended_allocation = base_allocation * risk_adjustment

        # Strategy-specific limits
        max_position = strategy_config.get('position_sizing', {}).get('max_single_position', 0.08)
        recommended_allocation = min(recommended_allocation, max_position)

        # Stop loss and take profit
        stop_loss_pct = strategy_config.get('risk_management', {}).get('stop_loss_default', 0.08)
        take_profit_pct = strategy_config.get('risk_management', {}).get('take_profit_default', 0.15)

        stop_loss_price = None
        take_profit_price = None
        if current_price:
            stop_loss_price = current_price * (1 - stop_loss_pct)
            take_profit_price = current_price * (1 + take_profit_pct)

        return PositionSizing(
            recommended_allocation=recommended_allocation,
            max_position_size=max_position,
            suggested_entry_price=current_price,
            stop_loss_price=stop_loss_price,
            take_profit_price=take_profit_price,
            time_horizon=strategy_config.get('time_horizon', 'medium_term')
        )

    def _calculate_strategy_alignment(
        self,
        composite_score: float,
        technical_analysis: Optional[TechnicalAnalysis],
        strategy_config: Dict
    ) -> float:
        """Calculate how well the investment aligns with the strategy."""
        alignment_score = 0.0

        # Check if score aligns with strategy risk tolerance
        risk_level = strategy_config.get('risk_level', 'moderate')
        if risk_level == 'low' and abs(composite_score) < 0.5:
            alignment_score += 0.3  # Conservative strategy likes moderate signals
        elif risk_level == 'high' and abs(composite_score) > 0.4:
            alignment_score += 0.3  # Aggressive strategy likes strong signals
        elif risk_level == 'moderate':
            alignment_score += 0.3  # Moderate strategy is flexible

        # Time horizon alignment
        time_horizon = strategy_config.get('time_horizon', 'medium_term')
        if technical_analysis:
            if time_horizon == 'long_term' and technical_analysis.trend_direction in [TrendDirection.BULLISH, TrendDirection.STRONG_BULLISH]:
                alignment_score += 0.4
            elif time_horizon == 'short_term' and technical_analysis.trend_strength > 50:
                alignment_score += 0.4
            else:
                alignment_score += 0.2

        # Strategy-specific criteria alignment
        # (This would be expanded based on specific strategy requirements)
        alignment_score += 0.3  # Base alignment

        return min(1.0, alignment_score)

    def _calculate_target_price(
        self,
        current_price: Optional[float],
        technical_analysis: Optional[TechnicalAnalysis],
        recommendation_type: RecommendationType
    ) -> Optional[float]:
        """Calculate target price based on analysis."""
        if not current_price:
            return None

        # Base target based on recommendation
        multiplier = {
            RecommendationType.STRONG_BUY: 1.20,
            RecommendationType.BUY: 1.10,
            RecommendationType.HOLD: 1.05,
            RecommendationType.SELL: 0.95,
            RecommendationType.STRONG_SELL: 0.85
        }.get(recommendation_type, 1.0)

        # Adjust based on technical analysis
        if technical_analysis:
            # Use support/resistance levels if available
            if hasattr(technical_analysis, 'support_resistance') and technical_analysis.support_resistance:
                resistance_levels = getattr(technical_analysis.support_resistance, 'resistance_levels', [])
                if resistance_levels:
                    nearest_resistance = min(resistance_levels,
                                           key=lambda x: abs(x - current_price))
                    if nearest_resistance > current_price:
                        multiplier = min(multiplier, nearest_resistance / current_price)

        return current_price * multiplier

    async def generate_batch_recommendations(
        self,
        symbols: List[str],
        strategy_name: str = "balanced_growth",
        price_data_source: Optional[Any] = None,
        news_data_source: Optional[Any] = None
    ) -> List[InvestmentRecommendation]:
        """
        Generate recommendations for multiple symbols.

        Args:
            symbols: List of stock symbols to analyze
            strategy_name: Investment strategy to use
            price_data_source: Function to fetch price data for a symbol
            news_data_source: Function to fetch news data for a symbol

        Returns:
            List of investment recommendations
        """
        self.logger.info(f"Generating batch recommendations for {len(symbols)} symbols")

        recommendations = []

        for symbol in symbols:
            try:
                # Fetch data if sources provided
                price_data = None
                news_data = None

                if price_data_source:
                    price_data = await price_data_source(symbol)
                if news_data_source:
                    news_data = await news_data_source(symbol)

                # Generate recommendation
                recommendation = await self.analyze_investment(
                    symbol=symbol,
                    strategy_name=strategy_name,
                    price_data=price_data,
                    news_data=news_data
                )

                recommendations.append(recommendation)

            except Exception as e:
                self.logger.error(f"Failed to analyze {symbol}: {e}")
                continue

        # Sort by composite score (best recommendations first)
        recommendations.sort(key=lambda x: x.composite_score, reverse=True)

        self.logger.info(f"Generated {len(recommendations)} recommendations")
        return recommendations

    def export_recommendation(self, recommendation: InvestmentRecommendation) -> Dict[str, Any]:
        """Export recommendation to dictionary format."""
        return {
            'symbol': recommendation.symbol,
            'recommendation': recommendation.recommendation.name,
            'confidence': recommendation.confidence.name,
            'target_price': recommendation.target_price,
            'current_price': recommendation.current_price,
            'scores': {
                'technical': recommendation.technical_score,
                'sentiment': recommendation.sentiment_score,
                'fundamental': recommendation.fundamental_score,
                'composite': recommendation.composite_score
            },
            'risk_metrics': {
                'volatility': recommendation.risk_metrics.volatility_score,
                'overall_risk': recommendation.risk_metrics.overall_risk_score
            },
            'position_sizing': {
                'recommended_allocation': recommendation.position_sizing.recommended_allocation,
                'stop_loss': recommendation.position_sizing.stop_loss_price,
                'take_profit': recommendation.position_sizing.take_profit_price
            },
            'strategy_alignment': recommendation.strategy_alignment,
            'reasoning': recommendation.reasoning,
            'warnings': recommendation.warnings,
            'analysis_timestamp': recommendation.analysis_timestamp.isoformat(),
            'strategy_name': recommendation.strategy_name
        }

    def get_portfolio_recommendations(
        self,
        recommendations: List[InvestmentRecommendation],
        total_portfolio_value: float = 100000.0
    ) -> Dict[str, Any]:
        """
        Generate portfolio-level recommendations and allocation.

        Args:
            recommendations: List of individual stock recommendations
            total_portfolio_value: Total portfolio value for position sizing

        Returns:
            Portfolio recommendations and allocation
        """
        # Filter to only buy recommendations
        buy_recommendations = [
            r for r in recommendations
            if r.recommendation in [RecommendationType.BUY, RecommendationType.STRONG_BUY]
        ]

        # Calculate total recommended allocation
        total_allocation = sum(r.position_sizing.recommended_allocation for r in buy_recommendations)

        # Scale allocations if they exceed 100%
        if total_allocation > 1.0:
            scale_factor = 0.9 / total_allocation  # Leave 10% cash
            for rec in buy_recommendations:
                rec.position_sizing.recommended_allocation *= scale_factor

        # Calculate dollar amounts
        portfolio_allocation = []
        for rec in buy_recommendations:
            dollar_amount = total_portfolio_value * rec.position_sizing.recommended_allocation
            current_price = float(rec.current_price) if hasattr(rec.current_price, '__float__') else rec.current_price
            shares = int(dollar_amount / current_price) if current_price > 0 else 0

            portfolio_allocation.append({
                'symbol': rec.symbol,
                'allocation_percent': rec.position_sizing.recommended_allocation * 100,
                'dollar_amount': dollar_amount,
                'shares': shares,
                'recommendation': rec.recommendation.name,
                'confidence': rec.confidence.name,
                'expected_return': ((rec.target_price or rec.current_price) - rec.current_price) / rec.current_price if rec.current_price > 0 else 0
            })

        # Portfolio metrics
        portfolio_risk = np.mean([r.risk_metrics.overall_risk_score for r in buy_recommendations]) if buy_recommendations else 0.0
        expected_return = np.mean([a['expected_return'] for a in portfolio_allocation]) if portfolio_allocation else 0.0

        return {
            'total_positions': len(portfolio_allocation),
            'total_allocated_percent': sum(a['allocation_percent'] for a in portfolio_allocation),
            'cash_percent': max(0, 100 - sum(a['allocation_percent'] for a in portfolio_allocation)),
            'expected_annual_return': expected_return,
            'portfolio_risk_score': portfolio_risk,
            'positions': portfolio_allocation,
            'rebalance_needed': total_allocation > 1.0,
            'diversification_score': min(1.0, len(portfolio_allocation) / 10)  # Assume 10 positions is well diversified
        }


# Example usage and testing functions
async def example_usage():
    """Example usage of the RecommendationEngine."""
    engine = RecommendationEngine()

    # Example price data (would normally come from MCP stock data server)
    price_data = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=100),
        'open': np.random.randn(100).cumsum() + 100,
        'high': np.random.randn(100).cumsum() + 102,
        'low': np.random.randn(100).cumsum() + 98,
        'close': np.random.randn(100).cumsum() + 100,
        'volume': np.random.randint(1000000, 5000000, 100)
    })

    # Example news data
    news_data = [
        {'title': 'Company reports strong earnings', 'description': 'Revenue up 15%', 'source': 'reuters'},
        {'title': 'Market outlook positive', 'description': 'Analysts bullish', 'source': 'bloomberg'}
    ]

    # Generate recommendation
    recommendation = await engine.analyze_investment(
        symbol='AAPL',
        strategy_name='conservative_growth',
        price_data=price_data,
        news_data=news_data
    )

    print(f"Recommendation for AAPL: {recommendation.recommendation.name}")
    print(f"Confidence: {recommendation.confidence.name}")
    print(f"Target Price: ${recommendation.target_price:.2f}")
    print(f"Composite Score: {recommendation.composite_score:.3f}")


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Run example
    asyncio.run(example_usage())
