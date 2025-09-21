"""
Sentiment Analyzer for the Agent Investment Platform.

This module provides comprehensive sentiment analysis capabilities for financial news,
social media content, and other text data to support investment decision-making.

Key Features:
- Multi-source sentiment analysis (news, social media, earnings calls)
- Financial domain-specific sentiment scoring
- Batch processing capabilities
- Integration with MCP servers for real-time analysis
- Support for both cloud and local NLP models
"""

import asyncio
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import json

import pandas as pd


class SentimentScore(Enum):
    """Sentiment classification levels."""
    VERY_NEGATIVE = -2
    NEGATIVE = -1
    NEUTRAL = 0
    POSITIVE = 1
    VERY_POSITIVE = 2


@dataclass
class SentimentResult:
    """Result of sentiment analysis."""
    text: str
    score: float  # -1.0 to 1.0
    classification: SentimentScore
    confidence: float  # 0.0 to 1.0
    keywords: List[str]
    timestamp: datetime
    source: str
    

@dataclass
class MarketSentiment:
    """Aggregated market sentiment for a symbol."""
    symbol: str
    overall_score: float
    sentiment_distribution: Dict[SentimentScore, int]
    total_articles: int
    confidence: float
    trending_keywords: List[str]
    timeframe: str
    last_updated: datetime


class FinancialSentimentAnalyzer:
    """
    Advanced sentiment analyzer optimized for financial content.
    
    Supports multiple analysis methods:
    - Rule-based financial lexicon
    - Transformer models (local/cloud)
    - Hybrid approach combining multiple methods
    """
    
    def __init__(self, model_type: str = "hybrid"):
        """
        Initialize the sentiment analyzer.
        
        Args:
            model_type: "rule_based", "transformer", or "hybrid"
        """
        self.model_type = model_type
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Financial sentiment lexicon
        self.positive_terms = {
            "strong", "growth", "profit", "revenue", "earnings", "beat", "exceed",
            "outperform", "bullish", "rally", "surge", "gain", "increase", "rise",
            "upgrade", "buy", "positive", "optimistic", "momentum", "breakthrough",
            "innovation", "expansion", "success", "record", "milestone", "robust"
        }
        
        self.negative_terms = {
            "weak", "decline", "loss", "deficit", "miss", "underperform", "bearish",
            "crash", "plunge", "fall", "decrease", "drop", "downgrade", "sell",
            "negative", "pessimistic", "concern", "risk", "threat", "crisis",
            "recession", "bankruptcy", "lawsuit", "scandal", "fraud", "volatile"
        }
        
        # Financial impact multipliers
        self.impact_terms = {
            "earnings": 2.0,
            "revenue": 1.8,
            "guidance": 1.5,
            "merger": 1.7,
            "acquisition": 1.6,
            "dividend": 1.3,
            "stock split": 1.2,
            "layoffs": -1.5,
            "restructuring": -1.2
        }
        
        # Initialize transformer model if requested
        self.transformer_model = None
        if model_type in ["transformer", "hybrid"]:
            self._initialize_transformer()
    
    def _initialize_transformer(self):
        """Initialize transformer model for advanced sentiment analysis."""
        try:
            # Try to import and initialize transformer model
            from transformers import pipeline
            self.transformer_model = pipeline(
                "sentiment-analysis",
                model="ProsusAI/finbert",  # Financial domain-specific BERT
                device=-1  # Use CPU (set to 0 for GPU)
            )
            self.logger.info("Initialized FinBERT transformer model")
        except ImportError:
            self.logger.warning("Transformers library not available, falling back to rule-based analysis")
            self.transformer_model = None
        except Exception as e:
            self.logger.error(f"Failed to initialize transformer model: {e}")
            self.transformer_model = None
    
    async def analyze_text(self, text: str, source: str = "unknown") -> SentimentResult:
        """
        Analyze sentiment of a single text.
        
        Args:
            text: Text to analyze
            source: Source of the text (news, twitter, reddit, etc.)
            
        Returns:
            SentimentResult with detailed analysis
        """
        if not text or not text.strip():
            return SentimentResult(
                text="",
                score=0.0,
                classification=SentimentScore.NEUTRAL,
                confidence=0.0,
                keywords=[],
                timestamp=datetime.now(),
                source=source
            )
        
        # Clean text
        cleaned_text = self._clean_text(text)
        
        # Extract keywords
        keywords = self._extract_keywords(cleaned_text)
        
        # Calculate sentiment based on model type
        if self.model_type == "rule_based":
            score, confidence = self._rule_based_sentiment(cleaned_text)
        elif self.model_type == "transformer" and self.transformer_model:
            score, confidence = await self._transformer_sentiment(cleaned_text)
        else:  # hybrid
            rule_score, rule_conf = self._rule_based_sentiment(cleaned_text)
            if self.transformer_model:
                trans_score, trans_conf = await self._transformer_sentiment(cleaned_text)
                # Weight transformer more heavily but include rule-based insights
                score = (trans_score * 0.7) + (rule_score * 0.3)
                confidence = max(rule_conf, trans_conf)
            else:
                score, confidence = rule_score, rule_conf
        
        # Classify sentiment
        classification = self._classify_sentiment(score)
        
        return SentimentResult(
            text=text[:200] + "..." if len(text) > 200 else text,
            score=score,
            classification=classification,
            confidence=confidence,
            keywords=keywords,
            timestamp=datetime.now(),
            source=source
        )
    
    async def analyze_batch(self, texts: List[Tuple[str, str]]) -> List[SentimentResult]:
        """
        Analyze sentiment for multiple texts.
        
        Args:
            texts: List of (text, source) tuples
            
        Returns:
            List of SentimentResult objects
        """
        tasks = []
        for text, source in texts:
            task = asyncio.create_task(self.analyze_text(text, source))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and log errors
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Failed to analyze text {i}: {result}")
            else:
                valid_results.append(result)
        
        return valid_results
    
    async def analyze_symbol_sentiment(self, symbol: str, articles: List[Dict[str, Any]], 
                                     timeframe: str = "24h") -> MarketSentiment:
        """
        Analyze overall market sentiment for a specific symbol.
        
        Args:
            symbol: Stock symbol (e.g., "AAPL")
            articles: List of article dictionaries with 'title', 'content', 'source'
            timeframe: Time window for analysis
            
        Returns:
            MarketSentiment with aggregated analysis
        """
        if not articles:
            return MarketSentiment(
                symbol=symbol,
                overall_score=0.0,
                sentiment_distribution={s: 0 for s in SentimentScore},
                total_articles=0,
                confidence=0.0,
                trending_keywords=[],
                timeframe=timeframe,
                last_updated=datetime.now()
            )
        
        # Prepare texts for analysis
        texts_to_analyze = []
        for article in articles:
            # Combine title and content for analysis
            full_text = f"{article.get('title', '')} {article.get('content', '')}"
            source = article.get('source', 'unknown')
            texts_to_analyze.append((full_text, source))
        
        # Analyze all articles
        results = await self.analyze_batch(texts_to_analyze)
        
        if not results:
            return MarketSentiment(
                symbol=symbol,
                overall_score=0.0,
                sentiment_distribution={s: 0 for s in SentimentScore},
                total_articles=0,
                confidence=0.0,
                trending_keywords=[],
                timeframe=timeframe,
                last_updated=datetime.now()
            )
        
        # Calculate aggregated metrics
        total_score = sum(result.score for result in results)
        total_confidence = sum(result.confidence for result in results)
        overall_score = total_score / len(results)
        avg_confidence = total_confidence / len(results)
        
        # Calculate sentiment distribution
        sentiment_distribution = {s: 0 for s in SentimentScore}
        for result in results:
            sentiment_distribution[result.classification] += 1
        
        # Extract trending keywords
        all_keywords = []
        for result in results:
            all_keywords.extend(result.keywords)
        
        keyword_counts = {}
        for keyword in all_keywords:
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        trending_keywords = sorted(
            keyword_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]  # Top 10 keywords
        
        return MarketSentiment(
            symbol=symbol,
            overall_score=overall_score,
            sentiment_distribution=sentiment_distribution,
            total_articles=len(results),
            confidence=avg_confidence,
            trending_keywords=[kw[0] for kw in trending_keywords],
            timeframe=timeframe,
            last_updated=datetime.now()
        )
    
    def _clean_text(self, text: str) -> str:
        """Clean and preprocess text for analysis."""
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\!\?\,\-\$\%]', ' ', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text.lower()
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant financial keywords from text."""
        words = text.split()
        keywords = []
        
        # Look for financial terms, company indicators, and sentiment words
        financial_indicators = {
            'earnings', 'revenue', 'profit', 'loss', 'guidance', 'forecast',
            'quarter', 'quarterly', 'annual', 'dividend', 'split', 'merger',
            'acquisition', 'ipo', 'sec', 'filing', 'analyst', 'upgrade',
            'downgrade', 'target', 'price', 'volume', 'shares'
        }
        
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word)
            if (clean_word in financial_indicators or 
                clean_word in self.positive_terms or 
                clean_word in self.negative_terms or
                clean_word in self.impact_terms):
                keywords.append(clean_word)
        
        return list(set(keywords))  # Remove duplicates
    
    def _rule_based_sentiment(self, text: str) -> Tuple[float, float]:
        """
        Calculate sentiment using rule-based approach.
        
        Returns:
            Tuple of (sentiment_score, confidence)
        """
        words = text.split()
        positive_count = 0
        negative_count = 0
        impact_multiplier = 1.0
        
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word)
            
            if clean_word in self.positive_terms:
                positive_count += 1
            elif clean_word in self.negative_terms:
                negative_count += 1
            
            # Apply impact multipliers
            if clean_word in self.impact_terms:
                impact_multiplier *= abs(self.impact_terms[clean_word])
        
        # Calculate base sentiment
        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words == 0:
            return 0.0, 0.1  # Low confidence for neutral
        
        # Normalize sentiment score
        net_sentiment = positive_count - negative_count
        base_score = net_sentiment / max(len(words) / 10, 1)  # Adjust for text length
        
        # Apply impact multiplier
        final_score = base_score * impact_multiplier
        
        # Clamp to [-1, 1] range
        final_score = max(-1.0, min(1.0, final_score))
        
        # Calculate confidence based on number of sentiment words
        confidence = min(0.9, total_sentiment_words / 10)
        
        return final_score, confidence
    
    async def _transformer_sentiment(self, text: str) -> Tuple[float, float]:
        """
        Calculate sentiment using transformer model.
        
        Returns:
            Tuple of (sentiment_score, confidence)
        """
        if not self.transformer_model:
            return 0.0, 0.0
        
        try:
            # Run transformer analysis
            result = self.transformer_model(text)
            
            # Extract sentiment and confidence
            label = result[0]['label'].lower()
            confidence = result[0]['score']
            
            # Convert to our scoring system
            if 'positive' in label:
                score = confidence
            elif 'negative' in label:
                score = -confidence
            else:
                score = 0.0
            
            return score, confidence
            
        except Exception as e:
            self.logger.error(f"Transformer sentiment analysis failed: {e}")
            return 0.0, 0.0
    
    def _classify_sentiment(self, score: float) -> SentimentScore:
        """Classify sentiment score into categories."""
        if score <= -0.6:
            return SentimentScore.VERY_NEGATIVE
        elif score <= -0.2:
            return SentimentScore.NEGATIVE
        elif score <= 0.2:
            return SentimentScore.NEUTRAL
        elif score <= 0.6:
            return SentimentScore.POSITIVE
        else:
            return SentimentScore.VERY_POSITIVE
    
    def export_analysis(self, results: List[SentimentResult], 
                       filepath: str, format: str = "json"):
        """
        Export sentiment analysis results to file.
        
        Args:
            results: List of SentimentResult objects
            filepath: Output file path
            format: Export format ("json", "csv")
        """
        if format.lower() == "json":
            data = []
            for result in results:
                data.append({
                    "text": result.text,
                    "score": result.score,
                    "classification": result.classification.name,
                    "confidence": result.confidence,
                    "keywords": result.keywords,
                    "timestamp": result.timestamp.isoformat(),
                    "source": result.source
                })
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        elif format.lower() == "csv":
            data = []
            for result in results:
                data.append({
                    "text": result.text,
                    "score": result.score,
                    "classification": result.classification.name,
                    "confidence": result.confidence,
                    "keywords": "|".join(result.keywords),
                    "timestamp": result.timestamp.isoformat(),
                    "source": result.source
                })
            
            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False, encoding='utf-8')
        
        self.logger.info(f"Exported {len(results)} sentiment results to {filepath}")


# Example usage and testing functions
async def test_sentiment_analyzer():
    """Test the sentiment analyzer with sample financial texts."""
    analyzer = FinancialSentimentAnalyzer(model_type="rule_based")
    
    test_texts = [
        ("Apple reports record quarterly earnings, beating analyst expectations by 15%", "news"),
        ("Tesla stock plunges 10% on disappointing delivery numbers and production issues", "news"),
        ("Microsoft announces major acquisition deal, expanding cloud services portfolio", "news"),
        ("Market volatility continues as investors react to mixed economic indicators", "news"),
        ("Amazon's revenue growth slows, raising concerns about future profitability", "news")
    ]
    
    print("🔍 Testing Sentiment Analyzer...")
    print("=" * 50)
    
    for text, source in test_texts:
        result = await analyzer.analyze_text(text, source)
        print(f"Text: {result.text}")
        print(f"Score: {result.score:.3f} ({result.classification.name})")
        print(f"Confidence: {result.confidence:.3f}")
        print(f"Keywords: {', '.join(result.keywords)}")
        print("-" * 30)


if __name__ == "__main__":
    asyncio.run(test_sentiment_analyzer())