"""
Unit tests for the Sentiment Analyzer module.

Tests cover:
- Financial sentiment lexicon functionality
- Rule-based sentiment analysis
- Batch processing capabilities
- Symbol-specific sentiment aggregation
- Error handling and edge cases
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from analysis.sentiment_analyzer import (
    FinancialSentimentAnalyzer,
    SentimentResult,
    SentimentScore,
    MarketSentiment
)


class TestFinancialSentimentAnalyzer:
    """Test suite for FinancialSentimentAnalyzer class."""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance for testing."""
        return FinancialSentimentAnalyzer(model_type="rule_based")

    @pytest.fixture
    def sample_texts(self):
        """Sample texts for testing sentiment analysis."""
        return {
            'positive': [
                "Company reports strong quarterly earnings with revenue growth of 15%",
                "Stock price surges on positive analyst upgrade to buy rating",
                "Innovation breakthrough drives bullish momentum in the market"
            ],
            'negative': [
                "Company faces lawsuit over alleged financial fraud",
                "Stock plunges on disappointing earnings miss and weak guidance",
                "Recession fears drive bearish sentiment across markets"
            ],
            'neutral': [
                "Company schedules quarterly earnings call for next week",
                "Stock trades sideways in low volume session",
                "Market participants await Federal Reserve decision"
            ]
        }

    def test_analyzer_initialization(self):
        """Test analyzer initialization with different modes."""
        # Rule-based analyzer
        analyzer_rule = FinancialSentimentAnalyzer(model_type="rule_based")
        assert analyzer_rule.model_type == "rule_based"
        assert analyzer_rule.transformer_model is None

        # Hybrid analyzer (should fallback to rule-based if no transformers)
        analyzer_hybrid = FinancialSentimentAnalyzer(model_type="hybrid")
        assert analyzer_hybrid.model_type == "hybrid"

    def test_text_cleaning(self, analyzer):
        """Test text preprocessing and cleaning."""
        dirty_text = "  STOCK: $AAPL   up 15%!!!   @mention #hashtag  "
        cleaned = analyzer._clean_text(dirty_text)

        assert cleaned == "stock aapl up"
        assert len(cleaned.split()) == 3

    def test_keyword_extraction(self, analyzer):
        """Test financial keyword extraction."""
        text = "Strong earnings beat expectations with revenue growth"
        keywords = analyzer._extract_keywords(text)

        assert "earnings" in keywords
        assert "revenue" in keywords
        assert "growth" in keywords
        assert len(keywords) > 0

    @pytest.mark.asyncio
    async def test_positive_sentiment_analysis(self, analyzer, sample_texts):
        """Test analysis of positive financial content."""
        for text in sample_texts['positive']:
            result = await analyzer.analyze_text(text, source="test")

            assert isinstance(result, SentimentResult)
            assert result.score > 0  # Positive score
            assert result.classification in [SentimentScore.POSITIVE, SentimentScore.VERY_POSITIVE]
            assert result.confidence > 0
            assert len(result.keywords) > 0
            assert result.source == "test"

    @pytest.mark.asyncio
    async def test_negative_sentiment_analysis(self, analyzer, sample_texts):
        """Test analysis of negative financial content."""
        for text in sample_texts['negative']:
            result = await analyzer.analyze_text(text, source="test")

            assert isinstance(result, SentimentResult)
            assert result.score < 0  # Negative score
            assert result.classification in [SentimentScore.NEGATIVE, SentimentScore.VERY_NEGATIVE]
            assert result.confidence > 0
            assert len(result.keywords) > 0

    @pytest.mark.asyncio
    async def test_neutral_sentiment_analysis(self, analyzer, sample_texts):
        """Test analysis of neutral financial content."""
        for text in sample_texts['neutral']:
            result = await analyzer.analyze_text(text, source="test")

            assert isinstance(result, SentimentResult)
            assert abs(result.score) < 0.3  # Near neutral
            assert result.classification == SentimentScore.NEUTRAL
            assert result.confidence >= 0

    @pytest.mark.asyncio
    async def test_batch_processing(self, analyzer, sample_texts):
        """Test batch processing of multiple texts."""
        # Prepare batch data
        batch_texts = []
        for category, texts in sample_texts.items():
            for text in texts:
                batch_texts.append((text, category))

        results = await analyzer.analyze_batch(batch_texts)

        assert len(results) == len(batch_texts)
        assert all(isinstance(result, SentimentResult) for result in results)
        assert all(result.confidence >= 0 for result in results)

    @pytest.mark.asyncio
    async def test_symbol_sentiment_analysis(self, analyzer):
        """Test symbol-specific sentiment aggregation."""
        articles = [
            {
                'title': 'AAPL reports strong earnings',
                'content': 'Apple Inc. exceeded analyst expectations with quarterly revenue growth',
                'source': 'reuters'
            },
            {
                'title': 'AAPL stock upgrade',
                'content': 'Analysts upgrade Apple to buy rating on innovation prospects',
                'source': 'bloomberg'
            },
            {
                'title': 'AAPL market position',
                'content': 'Apple maintains market leadership in smartphone segment',
                'source': 'techcrunch'
            }
        ]

        market_sentiment = await analyzer.analyze_symbol_sentiment(
            symbol='AAPL',
            articles=articles,
            timeframe='24h'
        )

        assert isinstance(market_sentiment, MarketSentiment)
        assert market_sentiment.symbol == 'AAPL'
        assert market_sentiment.total_articles == len(articles)
        assert market_sentiment.timeframe == '24h'
        assert market_sentiment.overall_score is not None
        assert market_sentiment.confidence > 0
        assert len(market_sentiment.trending_keywords) > 0

    def test_sentiment_classification(self, analyzer):
        """Test sentiment score to classification mapping."""
        # Test boundary conditions
        assert analyzer._classify_sentiment(-1.0) == SentimentScore.VERY_NEGATIVE
        assert analyzer._classify_sentiment(-0.6) == SentimentScore.NEGATIVE
        assert analyzer._classify_sentiment(0.0) == SentimentScore.NEUTRAL
        assert analyzer._classify_sentiment(0.6) == SentimentScore.POSITIVE
        assert analyzer._classify_sentiment(1.0) == SentimentScore.VERY_POSITIVE

    @pytest.mark.asyncio
    async def test_empty_text_handling(self, analyzer):
        """Test handling of empty or invalid text inputs."""
        # Empty text
        result = await analyzer.analyze_text("", source="test")
        assert result.classification == SentimentScore.NEUTRAL
        assert result.score == 0.0

        # Whitespace only
        result = await analyzer.analyze_text("   ", source="test")
        assert result.classification == SentimentScore.NEUTRAL

        # Very short text
        result = await analyzer.analyze_text("ok", source="test")
        assert isinstance(result, SentimentResult)

    @pytest.mark.asyncio
    async def test_financial_impact_terms(self, analyzer):
        """Test recognition of high-impact financial terms."""
        high_impact_text = "Company announces earnings guidance revision and dividend increase"
        result = await analyzer.analyze_text(high_impact_text, source="test")

        # Should have higher confidence due to financial impact terms
        assert result.confidence > 0.5
        assert "earnings" in result.keywords or "dividend" in result.keywords

    def test_export_functionality(self, analyzer):
        """Test sentiment analysis results export."""
        # Create sample results
        results = [
            SentimentResult(
                text="Sample positive text",
                score=0.8,
                classification=SentimentScore.POSITIVE,
                confidence=0.9,
                keywords=["positive", "good"],
                timestamp=datetime.now(),
                source="test"
            ),
            SentimentResult(
                text="Sample negative text",
                score=-0.6,
                classification=SentimentScore.NEGATIVE,
                confidence=0.7,
                keywords=["negative", "bad"],
                timestamp=datetime.now(),
                source="test"
            )
        ]

        # Test JSON export
        json_data = analyzer.export_analysis(results, format="json")
        assert "results" in json_data
        assert len(json_data["results"]) == 2
        assert "summary" in json_data

        # Test CSV export
        csv_data = analyzer.export_analysis(results, format="csv")
        assert isinstance(csv_data, str)
        assert "text,score,classification" in csv_data

    @pytest.mark.asyncio
    async def test_error_handling(self, analyzer):
        """Test error handling for various edge cases."""
        # None input
        with pytest.raises(TypeError):
            await analyzer.analyze_text(None, source="test")

        # Invalid source
        result = await analyzer.analyze_text("test text", source="")
        assert result.source == ""

        # Very long text (should be truncated)
        long_text = "word " * 1000
        result = await analyzer.analyze_text(long_text, source="test")
        assert isinstance(result, SentimentResult)

    @pytest.mark.asyncio
    async def test_confidence_scoring(self, analyzer):
        """Test confidence scoring accuracy."""
        # High confidence cases
        strong_positive = "Excellent quarterly earnings beat with record revenue growth"
        result = await analyzer.analyze_text(strong_positive, source="test")
        assert result.confidence > 0.7

        # Low confidence cases
        ambiguous = "Company reports mixed results with some challenges"
        result = await analyzer.analyze_text(ambiguous, source="test")
        assert result.confidence < 0.8

    def test_financial_lexicon_coverage(self, analyzer):
        """Test coverage of financial terminology."""
        # Check positive terms
        assert "earnings" in analyzer.positive_terms
        assert "revenue" in analyzer.positive_terms
        assert "growth" in analyzer.positive_terms

        # Check negative terms
        assert "loss" in analyzer.negative_terms
        assert "decline" in analyzer.negative_terms
        assert "bearish" in analyzer.negative_terms

        # Check impact terms
        assert "earnings" in analyzer.impact_terms
        assert "merger" in analyzer.impact_terms
        assert analyzer.impact_terms["earnings"] > 1.0


class TestSentimentIntegration:
    """Integration tests for sentiment analyzer."""

    @pytest.mark.asyncio
    async def test_real_world_financial_news(self):
        """Test with realistic financial news scenarios."""
        analyzer = FinancialSentimentAnalyzer(model_type="rule_based")

        # Realistic financial news samples
        news_samples = [
            {
                'text': 'Apple Inc. (AAPL) reported quarterly earnings that beat Wall Street expectations, with iPhone sales driving a 15% revenue increase year-over-year.',
                'expected_sentiment': 'positive'
            },
            {
                'text': 'Tesla shares plunged 8% in after-hours trading following reports of production delays and supply chain disruptions affecting Q4 deliveries.',
                'expected_sentiment': 'negative'
            },
            {
                'text': 'Microsoft announced its quarterly earnings call scheduled for next Thursday, with analysts expecting modest growth in cloud services revenue.',
                'expected_sentiment': 'neutral'
            }
        ]

        for sample in news_samples:
            result = await analyzer.analyze_text(sample['text'], source="financial_news")

            if sample['expected_sentiment'] == 'positive':
                assert result.score > 0.2
            elif sample['expected_sentiment'] == 'negative':
                assert result.score < -0.2
            else:  # neutral
                assert abs(result.score) < 0.3

    @pytest.mark.asyncio
    async def test_market_sentiment_aggregation(self):
        """Test market sentiment aggregation for multiple symbols."""
        analyzer = FinancialSentimentAnalyzer(model_type="rule_based")

        symbols_data = {
            'AAPL': [
                {'title': 'Apple earnings beat', 'content': 'Strong iPhone sales drive revenue growth', 'source': 'reuters'},
                {'title': 'AAPL upgrade', 'content': 'Analysts raise target price on innovation', 'source': 'bloomberg'}
            ],
            'TSLA': [
                {'title': 'Tesla production issues', 'content': 'Supply chain disruptions affect deliveries', 'source': 'reuters'},
                {'title': 'TSLA stock decline', 'content': 'Shares drop on production concerns', 'source': 'bloomberg'}
            ]
        }

        results = {}
        for symbol, articles in symbols_data.items():
            sentiment = await analyzer.analyze_symbol_sentiment(
                symbol=symbol,
                articles=articles,
                timeframe='24h'
            )
            results[symbol] = sentiment

        # AAPL should be more positive than TSLA
        assert results['AAPL'].overall_score > results['TSLA'].overall_score
        assert results['AAPL'].confidence > 0.5
        assert results['TSLA'].confidence > 0.5


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
