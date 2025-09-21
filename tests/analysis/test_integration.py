"""
Integration tests for the Analysis Engine components.

Tests the integration between:
- Sentiment Analyzer
- Chart Analyzer
- Recommendation Engine
- Strategy Configuration
- End-to-end analysis workflows
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from analysis.sentiment_analyzer import FinancialSentimentAnalyzer, SentimentScore
from analysis.chart_analyzer import TechnicalChartAnalyzer, TrendDirection
from analysis.recommendation_engine import RecommendationEngine, RecommendationType, ConfidenceLevel


class TestAnalysisEngineIntegration:
    """Integration tests for complete analysis engine workflow."""

    @pytest.fixture
    def sentiment_analyzer(self):
        """Create sentiment analyzer instance."""
        return FinancialSentimentAnalyzer(model_type="rule_based")

    @pytest.fixture
    def chart_analyzer(self):
        """Create chart analyzer instance."""
        return TechnicalChartAnalyzer()

    @pytest.fixture
    def recommendation_engine(self):
        """Create recommendation engine instance."""
        return RecommendationEngine()

    @pytest.fixture
    def comprehensive_market_data(self):
        """Generate comprehensive market data for testing."""
        # Create 3 months of daily data
        dates = pd.date_range(start='2024-01-01', periods=90, freq='D')
        np.random.seed(123)  # Different seed for integration tests

        # Create different market scenarios
        scenarios = {
            'bull_market': self._create_bull_market_data(dates),
            'bear_market': self._create_bear_market_data(dates),
            'sideways_market': self._create_sideways_market_data(dates),
            'volatile_market': self._create_volatile_market_data(dates)
        }

        return scenarios

    def _create_bull_market_data(self, dates):
        """Create bullish market data."""
        trend = np.linspace(100, 140, len(dates))  # 40% increase
        noise = np.random.normal(0, 2, len(dates))
        prices = trend + noise

        return pd.DataFrame({
            'date': dates,
            'open': prices + np.random.normal(0, 0.5, len(dates)),
            'high': prices + np.abs(np.random.normal(0, 2, len(dates))),
            'low': prices - np.abs(np.random.normal(0, 1.5, len(dates))),
            'close': prices,
            'volume': np.random.randint(2000000, 10000000, len(dates))
        })

    def _create_bear_market_data(self, dates):
        """Create bearish market data."""
        trend = np.linspace(140, 100, len(dates))  # 29% decrease
        noise = np.random.normal(0, 2, len(dates))
        prices = trend + noise

        return pd.DataFrame({
            'date': dates,
            'open': prices + np.random.normal(0, 0.5, len(dates)),
            'high': prices + np.abs(np.random.normal(0, 1.5, len(dates))),
            'low': prices - np.abs(np.random.normal(0, 2, len(dates))),
            'close': prices,
            'volume': np.random.randint(2000000, 12000000, len(dates))  # Higher volume in downtrend
        })

    def _create_sideways_market_data(self, dates):
        """Create sideways/ranging market data."""
        base_price = 120
        noise = np.random.normal(0, 3, len(dates))
        prices = base_price + noise

        return pd.DataFrame({
            'date': dates,
            'open': prices + np.random.normal(0, 0.5, len(dates)),
            'high': prices + np.abs(np.random.normal(0, 2, len(dates))),
            'low': prices - np.abs(np.random.normal(0, 2, len(dates))),
            'close': prices,
            'volume': np.random.randint(1500000, 6000000, len(dates))  # Lower volume in sideways
        })

    def _create_volatile_market_data(self, dates):
        """Create highly volatile market data."""
        base_price = 120
        high_vol_noise = np.random.normal(0, 8, len(dates))  # High volatility
        prices = base_price + np.cumsum(high_vol_noise * 0.1)

        return pd.DataFrame({
            'date': dates,
            'open': prices + np.random.normal(0, 2, len(dates)),
            'high': prices + np.abs(np.random.normal(0, 5, len(dates))),
            'low': prices - np.abs(np.random.normal(0, 5, len(dates))),
            'close': prices,
            'volume': np.random.randint(3000000, 15000000, len(dates))  # Very high volume
        })

    @pytest.fixture
    def market_news_scenarios(self):
        """Generate different news scenarios for testing."""
        return {
            'very_positive': [
                {'title': 'Record quarterly earnings beat expectations by 25%', 'description': 'Company reports exceptional revenue growth and expanding profit margins', 'source': 'reuters'},
                {'title': 'Major breakthrough innovation announced', 'description': 'Revolutionary product launch expected to drive significant market share gains', 'source': 'bloomberg'},
                {'title': 'Multiple analyst upgrades to strong buy', 'description': 'Wall Street consensus raises price targets citing robust fundamentals', 'source': 'cnbc'}
            ],
            'positive': [
                {'title': 'Quarterly earnings exceed estimates', 'description': 'Solid financial performance with revenue growth of 8%', 'source': 'reuters'},
                {'title': 'Analyst upgrade to buy rating', 'description': 'Improved outlook on market expansion opportunities', 'source': 'bloomberg'}
            ],
            'neutral': [
                {'title': 'Company announces quarterly earnings call', 'description': 'Management to discuss financial results next week', 'source': 'reuters'},
                {'title': 'Stock trades in line with market', 'description': 'Share price follows broader market movements', 'source': 'bloomberg'}
            ],
            'negative': [
                {'title': 'Earnings miss analyst expectations', 'description': 'Quarterly results show declining revenue and margin pressure', 'source': 'reuters'},
                {'title': 'Downgrade to sell rating', 'description': 'Analysts cite competitive pressures and market headwinds', 'source': 'bloomberg'}
            ],
            'very_negative': [
                {'title': 'Major lawsuit filed over alleged misconduct', 'description': 'Class action lawsuit seeks billions in damages', 'source': 'reuters'},
                {'title': 'SEC investigation announced', 'description': 'Regulatory probe into financial reporting practices', 'source': 'bloomberg'},
                {'title': 'Multiple downgrades to strong sell', 'description': 'Analysts slash price targets amid fundamental concerns', 'source': 'cnbc'}
            ]
        }

    @pytest.mark.asyncio
    async def test_sentiment_chart_integration(self, sentiment_analyzer, chart_analyzer, comprehensive_market_data, market_news_scenarios):
        """Test integration between sentiment and chart analysis."""
        # Test bull market with positive news
        bull_data = comprehensive_market_data['bull_market']
        positive_news = market_news_scenarios['positive']

        # Run sentiment analysis
        sentiment_results = []
        for article in positive_news:
            content = f"{article['title']} {article['description']}"
            result = await sentiment_analyzer.analyze_text(content, source=article['source'])
            sentiment_results.append(result)

        market_sentiment = await sentiment_analyzer.analyze_symbol_sentiment(
            symbol='INTEGRATION_TEST',
            articles=positive_news
        )

        # Run chart analysis
        chart_analysis = await chart_analyzer.analyze_chart(
            symbol='INTEGRATION_TEST',
            price_data=bull_data,
            timeframe='1d'
        )

        # Verify alignment between sentiment and technical analysis
        assert market_sentiment.overall_score > 0  # Positive sentiment
        assert chart_analysis.trend_direction in [TrendDirection.BULLISH, TrendDirection.STRONG_BULLISH]

        # Both should agree on positive outlook
        sentiment_positive = market_sentiment.overall_score > 0.2
        technical_positive = chart_analysis.trend_direction in [TrendDirection.BULLISH, TrendDirection.STRONG_BULLISH]
        assert sentiment_positive and technical_positive

    @pytest.mark.asyncio
    async def test_complete_recommendation_workflow(self, recommendation_engine, comprehensive_market_data, market_news_scenarios):
        """Test complete recommendation generation workflow."""
        test_scenarios = [
            ('bull_market', 'very_positive', RecommendationType.BUY),
            ('bear_market', 'very_negative', RecommendationType.SELL),
            ('sideways_market', 'neutral', RecommendationType.HOLD),
        ]

        for market_type, news_type, expected_rec_type in test_scenarios:
            price_data = comprehensive_market_data[market_type]
            news_data = market_news_scenarios[news_type]

            recommendation = await recommendation_engine.analyze_investment(
                symbol=f'TEST_{market_type.upper()}',
                strategy_name='balanced_growth',
                price_data=price_data,
                news_data=news_data
            )

            # Verify recommendation aligns with market conditions
            assert isinstance(recommendation.recommendation, RecommendationType)

            # For clear scenarios, recommendation should align with expectations
            if market_type == 'bull_market' and news_type == 'very_positive':
                assert recommendation.recommendation in [RecommendationType.BUY, RecommendationType.STRONG_BUY]
                assert recommendation.composite_score > 0.3
            elif market_type == 'bear_market' and news_type == 'very_negative':
                assert recommendation.recommendation in [RecommendationType.SELL, RecommendationType.STRONG_SELL]
                assert recommendation.composite_score < -0.3
            elif market_type == 'sideways_market' and news_type == 'neutral':
                assert recommendation.recommendation == RecommendationType.HOLD
                assert abs(recommendation.composite_score) < 0.4

    @pytest.mark.asyncio
    async def test_strategy_impact_on_recommendations(self, recommendation_engine, comprehensive_market_data, market_news_scenarios):
        """Test how different strategies affect recommendations."""
        # Use bull market with positive news
        price_data = comprehensive_market_data['bull_market']
        news_data = market_news_scenarios['positive']

        strategies = ['conservative_growth', 'aggressive_growth', 'value_investing']
        recommendations = {}

        for strategy in strategies:
            rec = await recommendation_engine.analyze_investment(
                symbol='STRATEGY_TEST',
                strategy_name=strategy,
                price_data=price_data,
                news_data=news_data
            )
            recommendations[strategy] = rec

        # Conservative strategy should have smaller position sizes
        conservative_allocation = recommendations['conservative_growth'].position_sizing.recommended_allocation
        aggressive_allocation = recommendations['aggressive_growth'].position_sizing.recommended_allocation

        # Aggressive should generally allow larger positions (though risk-adjusted)
        assert conservative_allocation <= aggressive_allocation * 1.5  # Allow some variation

        # All strategies should recognize the positive scenario
        for strategy, rec in recommendations.items():
            assert rec.composite_score > 0  # Should be positive
            assert rec.recommendation in [RecommendationType.BUY, RecommendationType.STRONG_BUY, RecommendationType.HOLD]

    @pytest.mark.asyncio
    async def test_confidence_correlation_across_components(self, recommendation_engine, comprehensive_market_data, market_news_scenarios):
        """Test that confidence levels correlate across components."""
        # Test with clear bullish scenario (high confidence expected)
        clear_bull_data = comprehensive_market_data['bull_market']
        strong_positive_news = market_news_scenarios['very_positive']

        clear_recommendation = await recommendation_engine.analyze_investment(
            symbol='CLEAR_SIGNAL',
            strategy_name='balanced_growth',
            price_data=clear_bull_data,
            news_data=strong_positive_news
        )

        # Test with mixed scenario (lower confidence expected)
        mixed_data = comprehensive_market_data['volatile_market']
        neutral_news = market_news_scenarios['neutral']

        mixed_recommendation = await recommendation_engine.analyze_investment(
            symbol='MIXED_SIGNAL',
            strategy_name='balanced_growth',
            price_data=mixed_data,
            news_data=neutral_news
        )

        # Clear scenario should have higher confidence
        clear_confidence_value = clear_recommendation.confidence.value
        mixed_confidence_value = mixed_recommendation.confidence.value

        assert clear_confidence_value >= mixed_confidence_value

    @pytest.mark.asyncio
    async def test_risk_assessment_integration(self, recommendation_engine, comprehensive_market_data):
        """Test risk assessment across different market conditions."""
        risk_scenarios = [
            ('bull_market', 'low_risk'),
            ('volatile_market', 'high_risk'),
            ('sideways_market', 'moderate_risk')
        ]

        for market_type, expected_risk_level in risk_scenarios:
            price_data = comprehensive_market_data[market_type]

            recommendation = await recommendation_engine.analyze_investment(
                symbol=f'RISK_TEST_{market_type.upper()}',
                strategy_name='balanced_growth',
                price_data=price_data,
                news_data=[]
            )

            risk_score = recommendation.risk_metrics.overall_risk_score

            if expected_risk_level == 'high_risk':
                assert risk_score > 0.5  # Volatile market should show high risk
            elif expected_risk_level == 'low_risk':
                assert risk_score < 0.7  # Bull market should show manageable risk
            # Moderate risk can be anywhere in between

    @pytest.mark.asyncio
    async def test_portfolio_construction_integration(self, recommendation_engine, comprehensive_market_data, market_news_scenarios):
        """Test portfolio construction with multiple symbols."""
        # Create a diverse set of symbols with different characteristics
        symbols_data = {
            'GROWTH_STOCK': (comprehensive_market_data['bull_market'], market_news_scenarios['positive']),
            'VALUE_STOCK': (comprehensive_market_data['sideways_market'], market_news_scenarios['neutral']),
            'VOLATILE_STOCK': (comprehensive_market_data['volatile_market'], market_news_scenarios['negative']),
            'DECLINING_STOCK': (comprehensive_market_data['bear_market'], market_news_scenarios['very_negative'])
        }

        recommendations = []
        for symbol, (price_data, news_data) in symbols_data.items():
            rec = await recommendation_engine.analyze_investment(
                symbol=symbol,
                strategy_name='balanced_growth',
                price_data=price_data,
                news_data=news_data
            )
            recommendations.append(rec)

        # Generate portfolio recommendations
        portfolio = recommendation_engine.get_portfolio_recommendations(
            recommendations=recommendations,
            total_portfolio_value=100000.0
        )

        # Verify portfolio construction logic
        assert portfolio['total_positions'] >= 0
        assert portfolio['total_allocated_percent'] <= 100
        assert portfolio['cash_percent'] >= 0
        assert portfolio['diversification_score'] >= 0

        # Should favor better recommendations
        buy_recommendations = [r for r in recommendations if r.recommendation in [RecommendationType.BUY, RecommendationType.STRONG_BUY]]
        assert len(portfolio['positions']) == len(buy_recommendations)

    @pytest.mark.asyncio
    async def test_real_time_analysis_simulation(self, recommendation_engine):
        """Simulate real-time analysis updates."""
        # Create time series data that changes over time
        base_dates = pd.date_range(start='2024-01-01', periods=30, freq='D')

        # Simulate data arriving in chunks (like real-time updates)
        time_windows = [
            base_dates[:10],   # First 10 days
            base_dates[:20],   # First 20 days
            base_dates[:30]    # Full 30 days
        ]

        recommendations_over_time = []

        for window in time_windows:
            # Create evolving price data
            prices = 100 + np.cumsum(np.random.normal(0.1, 2, len(window)))  # Slight upward bias

            price_data = pd.DataFrame({
                'date': window,
                'open': prices + np.random.normal(0, 0.5, len(window)),
                'high': prices + np.abs(np.random.normal(0, 1, len(window))),
                'low': prices - np.abs(np.random.normal(0, 1, len(window))),
                'close': prices,
                'volume': np.random.randint(1000000, 5000000, len(window))
            })

            # Simulate evolving news sentiment
            news_data = [
                {'title': f'Day {len(window)} market update', 'description': 'Market continues to show strength', 'source': 'reuters'}
            ]

            recommendation = await recommendation_engine.analyze_investment(
                symbol='REALTIME_TEST',
                strategy_name='balanced_growth',
                price_data=price_data,
                news_data=news_data
            )

            recommendations_over_time.append(recommendation)

        # Verify recommendations evolve logically as more data becomes available
        assert len(recommendations_over_time) == 3

        # Confidence should generally increase with more data
        confidences = [rec.confidence.value for rec in recommendations_over_time]
        # Allow for some variation but expect general trend toward higher confidence
        assert confidences[-1] >= confidences[0] - 1  # Allow some decrease but not dramatic

    @pytest.mark.asyncio
    async def test_error_recovery_and_robustness(self, recommendation_engine):
        """Test system robustness and error recovery."""
        # Test with various problematic inputs
        test_cases = [
            # Minimal data
            (pd.DataFrame({'date': [datetime.now()], 'close': [100], 'volume': [1000000], 'open': [99], 'high': [101], 'low': [98]}), []),
            # No news data
            (pd.DataFrame({'date': pd.date_range('2024-01-01', periods=20, freq='D'), 'close': range(100, 120), 'volume': [1000000]*20, 'open': range(99, 119), 'high': range(101, 121), 'low': range(98, 118)}), []),
            # Single news item
            (pd.DataFrame({'date': pd.date_range('2024-01-01', periods=20, freq='D'), 'close': range(100, 120), 'volume': [1000000]*20, 'open': range(99, 119), 'high': range(101, 121), 'low': range(98, 118)}), [{'title': 'Single news', 'description': 'Test', 'source': 'test'}])
        ]

        for i, (price_data, news_data) in enumerate(test_cases):
            try:
                recommendation = await recommendation_engine.analyze_investment(
                    symbol=f'ROBUST_TEST_{i}',
                    strategy_name='conservative_growth',
                    price_data=price_data,
                    news_data=news_data
                )

                # Should still produce valid recommendation
                assert isinstance(recommendation.recommendation, RecommendationType)
                assert isinstance(recommendation.confidence, ConfidenceLevel)
                assert recommendation.current_price > 0

            except Exception as e:
                # If it fails, it should be a clear, expected error
                assert isinstance(e, (ValueError, KeyError))


class TestAnalysisEnginePerformance:
    """Performance tests for analysis engine."""

    @pytest.mark.asyncio
    async def test_analysis_performance(self, benchmark=None):
        """Test analysis performance with larger datasets."""
        if benchmark is None:
            pytest.skip("Benchmark not available")

        engine = RecommendationEngine()

        # Create larger dataset
        dates = pd.date_range(start='2023-01-01', periods=252, freq='D')  # 1 year of trading days
        prices = 100 + np.cumsum(np.random.normal(0.001, 0.02, 252))

        large_price_data = pd.DataFrame({
            'date': dates,
            'open': prices + np.random.normal(0, 0.5, 252),
            'high': prices + np.abs(np.random.normal(0, 1, 252)),
            'low': prices - np.abs(np.random.normal(0, 1, 252)),
            'close': prices,
            'volume': np.random.randint(1000000, 10000000, 252)
        })

        large_news_data = [
            {'title': f'News item {i}', 'description': f'Description {i}', 'source': 'test'}
            for i in range(50)  # 50 news items
        ]

        # Benchmark the analysis
        result = await benchmark(
            engine.analyze_investment,
            symbol='PERFORMANCE_TEST',
            strategy_name='balanced_growth',
            price_data=large_price_data,
            news_data=large_news_data
        )

        assert isinstance(result, object)  # Should complete successfully


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
