"""
Unit tests for the Recommendation Engine module.

Tests cover:
- Multi-factor analysis integration
- Investment recommendation generation
- Strategy-aware decision making
- Risk assessment and position sizing
- Portfolio optimization
- Configuration handling and error cases
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from analysis.recommendation_engine import (
    RecommendationEngine,
    InvestmentRecommendation,
    RecommendationType,
    ConfidenceLevel,
    AnalysisWeights,
    RiskMetrics,
    PositionSizing
)


class TestRecommendationEngine:
    """Test suite for RecommendationEngine class."""

    @pytest.fixture
    def engine(self):
        """Create recommendation engine for testing."""
        return RecommendationEngine()

    @pytest.fixture
    def sample_price_data(self):
        """Generate sample price data for testing."""
        dates = pd.date_range(start='2024-01-01', periods=50, freq='D')
        np.random.seed(42)

        base_price = 100
        returns = np.random.normal(0.001, 0.02, 50)
        prices = base_price * np.exp(np.cumsum(returns))

        return pd.DataFrame({
            'date': dates,
            'open': prices + np.random.normal(0, 0.5, 50),
            'high': prices + np.abs(np.random.normal(0, 1, 50)),
            'low': prices - np.abs(np.random.normal(0, 1, 50)),
            'close': prices,
            'volume': np.random.randint(1000000, 5000000, 50)
        })

    @pytest.fixture
    def sample_news_data(self):
        """Generate sample news data for testing."""
        return [
            {
                'title': 'Company reports strong quarterly earnings',
                'description': 'Revenue increased 15% year over year with strong profit margins',
                'source': 'reuters'
            },
            {
                'title': 'Positive analyst upgrade',
                'description': 'Analysts upgrade stock to buy on growth prospects',
                'source': 'bloomberg'
            },
            {
                'title': 'Market outlook remains bullish',
                'description': 'Strong fundamentals support continued growth',
                'source': 'cnbc'
            }
        ]

    def test_engine_initialization(self):
        """Test recommendation engine initialization."""
        engine = RecommendationEngine()

        assert engine is not None
        assert hasattr(engine, 'sentiment_analyzer')
        assert hasattr(engine, 'chart_analyzer')
        assert hasattr(engine, 'strategies_config')
        assert hasattr(engine, 'default_weights')

        # Check default weights sum to 1.0
        weights = engine.default_weights
        total_weight = weights.technical + weights.sentiment + weights.fundamental
        assert abs(total_weight - 1.0) < 0.001

    def test_analysis_weights_normalization(self):
        """Test AnalysisWeights normalization."""
        # Test automatic normalization
        weights = AnalysisWeights(technical=0.6, sentiment=0.3, fundamental=0.3)
        total = weights.technical + weights.sentiment + weights.fundamental
        assert abs(total - 1.0) < 0.001

        # Test with equal weights
        equal_weights = AnalysisWeights(technical=1.0, sentiment=1.0, fundamental=1.0)
        assert abs(equal_weights.technical - 1.0/3) < 0.001
        assert abs(equal_weights.sentiment - 1.0/3) < 0.001
        assert abs(equal_weights.fundamental - 1.0/3) < 0.001

    @pytest.mark.asyncio
    async def test_basic_investment_analysis(self, engine, sample_price_data, sample_news_data):
        """Test basic investment analysis functionality."""
        recommendation = await engine.analyze_investment(
            symbol='TEST',
            strategy_name='conservative_growth',
            price_data=sample_price_data,
            news_data=sample_news_data
        )

        assert isinstance(recommendation, InvestmentRecommendation)
        assert recommendation.symbol == 'TEST'
        assert isinstance(recommendation.recommendation, RecommendationType)
        assert isinstance(recommendation.confidence, ConfidenceLevel)
        assert recommendation.current_price > 0
        assert -1.0 <= recommendation.composite_score <= 1.0
        assert isinstance(recommendation.risk_metrics, RiskMetrics)
        assert isinstance(recommendation.position_sizing, PositionSizing)
        assert recommendation.analysis_timestamp is not None
        assert recommendation.strategy_name == 'conservative_growth'

    @pytest.mark.asyncio
    async def test_recommendation_types(self, engine, sample_price_data):
        """Test different recommendation types based on scores."""
        # Test with mock scores to verify recommendation logic
        with patch.object(engine, '_calculate_composite_score') as mock_score:
            # Strong positive score should yield BUY recommendation
            mock_score.return_value = 0.8
            recommendation = await engine.analyze_investment(
                symbol='STRONG_BUY_TEST',
                strategy_name='aggressive_growth',
                price_data=sample_price_data
            )
            assert recommendation.recommendation in [RecommendationType.BUY, RecommendationType.STRONG_BUY]

            # Strong negative score should yield SELL recommendation
            mock_score.return_value = -0.8
            recommendation = await engine.analyze_investment(
                symbol='STRONG_SELL_TEST',
                strategy_name='aggressive_growth',
                price_data=sample_price_data
            )
            assert recommendation.recommendation in [RecommendationType.SELL, RecommendationType.STRONG_SELL]

            # Neutral score should yield HOLD recommendation
            mock_score.return_value = 0.1
            recommendation = await engine.analyze_investment(
                symbol='HOLD_TEST',
                strategy_name='conservative_growth',
                price_data=sample_price_data
            )
            assert recommendation.recommendation == RecommendationType.HOLD

    def test_strategy_configuration_loading(self, engine):
        """Test strategy configuration loading."""
        assert 'strategies' in engine.strategies_config
        strategies = engine.strategies_config['strategies']

        # Should have multiple strategies
        assert len(strategies) > 0

        # Test specific strategy exists
        assert 'conservative_growth' in strategies
        conservative = strategies['conservative_growth']
        assert 'risk_level' in conservative
        assert 'target_return' in conservative

    def test_strategy_weights_extraction(self, engine):
        """Test strategy-specific weights extraction."""
        # Test with strategy that has custom weights
        strategy_config = {
            'analysis_weights': {
                'technical': 0.5,
                'sentiment': 0.3,
                'fundamental': 0.2
            }
        }

        weights = engine._get_strategy_weights(strategy_config)
        assert abs(weights.technical - 0.5) < 0.001
        assert abs(weights.sentiment - 0.3) < 0.001
        assert abs(weights.fundamental - 0.2) < 0.001

        # Test with strategy without custom weights (should use defaults)
        empty_strategy = {}
        default_weights = engine._get_strategy_weights(empty_strategy)
        assert abs(default_weights.technical - 0.4) < 0.001

    def test_composite_score_calculation(self, engine):
        """Test composite score calculation with different component scores."""
        weights = AnalysisWeights(technical=0.5, sentiment=0.3, fundamental=0.2)

        # Test with all components
        score = engine._calculate_composite_score(
            technical_score=0.8,
            sentiment_score=0.6,
            fundamental_score=0.4,
            weights=weights
        )
        expected = 0.5 * 0.8 + 0.3 * 0.6 + 0.2 * 0.4
        assert abs(score - expected) < 0.001

        # Test without fundamental score (should renormalize)
        score_no_fund = engine._calculate_composite_score(
            technical_score=0.8,
            sentiment_score=0.6,
            fundamental_score=None,
            weights=weights
        )
        # Should renormalize weights and calculate
        tech_weight = 0.5 / (0.5 + 0.3)
        sent_weight = 0.3 / (0.5 + 0.3)
        expected_no_fund = tech_weight * 0.8 + sent_weight * 0.6
        assert abs(score_no_fund - expected_no_fund) < 0.001

    def test_risk_assessment(self, engine, sample_price_data):
        """Test risk metrics calculation."""
        strategy_config = {'risk_level': 'moderate'}

        risk_metrics = engine._assess_risk(
            symbol='RISK_TEST',
            technical_analysis=None,
            price_data=sample_price_data,
            strategy_config=strategy_config
        )

        assert isinstance(risk_metrics, RiskMetrics)
        assert 0 <= risk_metrics.volatility_score <= 1.0
        assert risk_metrics.beta is not None
        assert 0 <= risk_metrics.max_drawdown_risk <= 1.0
        assert 0 <= risk_metrics.liquidity_risk <= 1.0
        assert 0 <= risk_metrics.concentration_risk <= 1.0
        assert 0 <= risk_metrics.overall_risk_score <= 1.0

    def test_position_sizing_calculation(self, engine):
        """Test position sizing recommendations."""
        risk_metrics = RiskMetrics(
            volatility_score=0.3,
            beta=1.2,
            max_drawdown_risk=0.2,
            liquidity_risk=0.1,
            concentration_risk=0.15,
            overall_risk_score=0.2
        )

        strategy_config = {
            'position_sizing': {'max_single_position': 0.08},
            'risk_management': {
                'stop_loss_default': 0.08,
                'take_profit_default': 0.15
            }
        }

        position_sizing = engine._calculate_position_sizing(
            recommendation_type=RecommendationType.BUY,
            risk_metrics=risk_metrics,
            strategy_config=strategy_config,
            current_price=100.0
        )

        assert isinstance(position_sizing, PositionSizing)
        assert 0 <= position_sizing.recommended_allocation <= 0.08  # Max position limit
        assert position_sizing.max_position_size == 0.08
        assert position_sizing.suggested_entry_price == 100.0
        assert position_sizing.stop_loss_price == 92.0  # 8% below entry
        assert position_sizing.take_profit_price == 115.0  # 15% above entry

    def test_confidence_calculation(self, engine):
        """Test confidence level calculation."""
        # Mock technical analysis with high confidence
        mock_tech_analysis = Mock()
        mock_tech_analysis.confidence = 0.9

        # Mock market sentiment with high confidence
        mock_sentiment = Mock()
        mock_sentiment.confidence = 0.8

        data_availability = {
            'technical': datetime.now(),
            'sentiment': datetime.now()
        }

        confidence = engine._calculate_confidence(
            technical_analysis=mock_tech_analysis,
            market_sentiment=mock_sentiment,
            data_availability=data_availability
        )

        assert isinstance(confidence, ConfidenceLevel)
        # With good data and high component confidence, should be high
        assert confidence in [ConfidenceLevel.HIGH, ConfidenceLevel.VERY_HIGH]

    @pytest.mark.asyncio
    async def test_batch_recommendations(self, engine, sample_price_data):
        """Test batch recommendation generation."""
        symbols = ['AAPL', 'GOOGL', 'MSFT']

        # Mock data source functions
        async def mock_price_source(symbol):
            return sample_price_data

        async def mock_news_source(symbol):
            return [{'title': f'{symbol} news', 'description': 'Test news', 'source': 'test'}]

        recommendations = await engine.generate_batch_recommendations(
            symbols=symbols,
            strategy_name='balanced_growth',
            price_data_source=mock_price_source,
            news_data_source=mock_news_source
        )

        assert len(recommendations) == len(symbols)
        assert all(isinstance(rec, InvestmentRecommendation) for rec in recommendations)
        assert all(rec.symbol in symbols for rec in recommendations)

        # Should be sorted by composite score (best first)
        scores = [rec.composite_score for rec in recommendations]
        assert scores == sorted(scores, reverse=True)

    def test_portfolio_recommendations(self, engine):
        """Test portfolio-level recommendations."""
        # Create mock recommendations
        mock_recommendations = [
            Mock(
                symbol='AAPL',
                recommendation=RecommendationType.BUY,
                current_price=150.0,
                target_price=165.0,
                position_sizing=Mock(recommended_allocation=0.05),
                risk_metrics=Mock(overall_risk_score=0.3),
                confidence=ConfidenceLevel.HIGH
            ),
            Mock(
                symbol='GOOGL',
                recommendation=RecommendationType.STRONG_BUY,
                current_price=2500.0,
                target_price=2750.0,
                position_sizing=Mock(recommended_allocation=0.06),
                risk_metrics=Mock(overall_risk_score=0.25),
                confidence=ConfidenceLevel.VERY_HIGH
            ),
            Mock(
                symbol='MSFT',
                recommendation=RecommendationType.HOLD,
                current_price=300.0,
                target_price=315.0,
                position_sizing=Mock(recommended_allocation=0.03),
                risk_metrics=Mock(overall_risk_score=0.2),
                confidence=ConfidenceLevel.MODERATE
            )
        ]

        portfolio = engine.get_portfolio_recommendations(
            recommendations=mock_recommendations,
            total_portfolio_value=100000.0
        )

        assert 'total_positions' in portfolio
        assert 'total_allocated_percent' in portfolio
        assert 'cash_percent' in portfolio
        assert 'expected_annual_return' in portfolio
        assert 'portfolio_risk_score' in portfolio
        assert 'positions' in portfolio
        assert 'diversification_score' in portfolio

        # Should only include BUY recommendations
        assert portfolio['total_positions'] == 2  # AAPL and GOOGL
        assert portfolio['total_allocated_percent'] > 0
        assert portfolio['cash_percent'] >= 0

    def test_recommendation_export(self, engine):
        """Test recommendation export functionality."""
        # Create mock recommendation
        mock_recommendation = Mock(
            symbol='TEST',
            recommendation=RecommendationType.BUY,
            confidence=ConfidenceLevel.HIGH,
            target_price=110.0,
            current_price=100.0,
            technical_score=0.6,
            sentiment_score=0.8,
            fundamental_score=0.4,
            composite_score=0.6,
            risk_metrics=Mock(volatility_score=0.3, overall_risk_score=0.25),
            position_sizing=Mock(
                recommended_allocation=0.05,
                stop_loss_price=92.0,
                take_profit_price=115.0
            ),
            strategy_alignment=0.8,
            reasoning=['Strong technical signals', 'Positive sentiment'],
            warnings=['Market volatility risk'],
            analysis_timestamp=datetime.now(),
            strategy_name='test_strategy'
        )

        exported = engine.export_recommendation(mock_recommendation)

        assert isinstance(exported, dict)
        assert exported['symbol'] == 'TEST'
        assert exported['recommendation'] == 'BUY'
        assert exported['confidence'] == 'HIGH'
        assert 'scores' in exported
        assert 'risk_metrics' in exported
        assert 'position_sizing' in exported
        assert 'reasoning' in exported
        assert 'warnings' in exported

    @pytest.mark.asyncio
    async def test_error_handling(self, engine):
        """Test error handling for various edge cases."""
        # Test with invalid strategy
        recommendation = await engine.analyze_investment(
            symbol='ERROR_TEST',
            strategy_name='nonexistent_strategy',
            price_data=pd.DataFrame({'close': [100, 101, 102]}),  # Minimal data
            news_data=[]
        )

        # Should fallback gracefully
        assert isinstance(recommendation, InvestmentRecommendation)
        assert recommendation.symbol == 'ERROR_TEST'

        # Test with no data
        with pytest.raises((ValueError, KeyError)):
            await engine.analyze_investment(
                symbol='NO_DATA_TEST',
                strategy_name='conservative_growth',
                price_data=None,
                news_data=None
            )

    def test_strategy_alignment_calculation(self, engine):
        """Test strategy alignment scoring."""
        strategy_config = {
            'risk_level': 'moderate',
            'time_horizon': 'long_term'
        }

        # Mock technical analysis
        mock_tech_analysis = Mock()
        mock_tech_analysis.trend_direction = Mock()
        mock_tech_analysis.trend_direction.name = 'BULLISH'

        alignment = engine._calculate_strategy_alignment(
            composite_score=0.6,
            technical_analysis=mock_tech_analysis,
            strategy_config=strategy_config
        )

        assert 0 <= alignment <= 1.0

    def test_target_price_calculation(self, engine):
        """Test target price calculation."""
        # Test with BUY recommendation
        target = engine._calculate_target_price(
            current_price=100.0,
            technical_analysis=None,
            recommendation_type=RecommendationType.BUY
        )

        assert target > 100.0  # Should be above current price for BUY

        # Test with SELL recommendation
        target_sell = engine._calculate_target_price(
            current_price=100.0,
            technical_analysis=None,
            recommendation_type=RecommendationType.SELL
        )

        assert target_sell < 100.0  # Should be below current price for SELL


class TestRecommendationEngineIntegration:
    """Integration tests for recommendation engine."""

    @pytest.mark.asyncio
    async def test_end_to_end_recommendation_flow(self):
        """Test complete recommendation generation flow."""
        engine = RecommendationEngine()

        # Create realistic test data
        dates = pd.date_range(start='2024-01-01', periods=60, freq='D')
        np.random.seed(42)

        # Bullish trend data
        trend = np.linspace(100, 120, 60)
        noise = np.random.normal(0, 2, 60)
        prices = trend + noise

        price_data = pd.DataFrame({
            'date': dates,
            'open': prices + np.random.normal(0, 0.5, 60),
            'high': prices + np.abs(np.random.normal(0, 2, 60)),
            'low': prices - np.abs(np.random.normal(0, 2, 60)),
            'close': prices,
            'volume': np.random.randint(2000000, 8000000, 60)
        })

        news_data = [
            {'title': 'Strong earnings report', 'description': 'Company beats expectations', 'source': 'reuters'},
            {'title': 'Analyst upgrade', 'description': 'Raised to buy rating', 'source': 'bloomberg'},
            {'title': 'Positive outlook', 'description': 'Growth prospects look strong', 'source': 'cnbc'}
        ]

        # Test with different strategies
        strategies = ['conservative_growth', 'aggressive_growth', 'value_investing']

        for strategy in strategies:
            recommendation = await engine.analyze_investment(
                symbol='INTEGRATION_TEST',
                strategy_name=strategy,
                price_data=price_data,
                news_data=news_data
            )

            assert isinstance(recommendation, InvestmentRecommendation)
            assert recommendation.strategy_name == strategy
            assert recommendation.composite_score > 0  # Should be positive given bullish data
            assert len(recommendation.reasoning) > 0

            # Conservative strategy should have smaller position size
            if strategy == 'conservative_growth':
                assert recommendation.position_sizing.recommended_allocation <= 0.08

    @pytest.mark.asyncio
    async def test_multi_symbol_portfolio_optimization(self):
        """Test portfolio optimization with multiple symbols."""
        engine = RecommendationEngine()

        # Create sample data for multiple symbols
        symbols_data = {}
        for symbol in ['AAPL', 'GOOGL', 'MSFT', 'TSLA']:
            dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
            base_price = np.random.uniform(100, 300)
            trend_strength = np.random.uniform(-0.02, 0.02)  # Random trend

            trend = np.linspace(base_price, base_price * (1 + trend_strength * 30), 30)
            noise = np.random.normal(0, base_price * 0.02, 30)
            prices = trend + noise

            symbols_data[symbol] = pd.DataFrame({
                'date': dates,
                'open': prices + np.random.normal(0, base_price * 0.005, 30),
                'high': prices + np.abs(np.random.normal(0, base_price * 0.01, 30)),
                'low': prices - np.abs(np.random.normal(0, base_price * 0.01, 30)),
                'close': prices,
                'volume': np.random.randint(1000000, 10000000, 30)
            })

        # Generate recommendations for all symbols
        recommendations = []
        for symbol, price_data in symbols_data.items():
            rec = await engine.analyze_investment(
                symbol=symbol,
                strategy_name='balanced_growth',
                price_data=price_data,
                news_data=[{'title': f'{symbol} news', 'description': 'Test', 'source': 'test'}]
            )
            recommendations.append(rec)

        # Generate portfolio recommendations
        portfolio = engine.get_portfolio_recommendations(
            recommendations=recommendations,
            total_portfolio_value=100000.0
        )

        assert portfolio['total_positions'] >= 0
        assert portfolio['total_allocated_percent'] <= 100
        assert portfolio['cash_percent'] >= 0
        assert portfolio['diversification_score'] >= 0


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
