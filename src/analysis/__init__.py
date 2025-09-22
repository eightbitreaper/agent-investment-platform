"""
Analysis Module for Agent Investment Platform

This package contains analysis components for financial data processing,
including sentiment analysis, technical analysis, and recommendation generation.

Components:
- FinancialSentimentAnalyzer: News and social media sentiment analysis
- TechnicalChartAnalyzer: Technical indicator analysis and chart patterns
- RecommendationEngine: Investment recommendation generation
"""

from .sentiment_analyzer import FinancialSentimentAnalyzer
from .chart_analyzer import TechnicalChartAnalyzer
from .recommendation_engine import (
    RecommendationEngine,
    InvestmentRecommendation,
    RecommendationType,
    ConfidenceLevel
)

__all__ = [
    'FinancialSentimentAnalyzer',
    'TechnicalChartAnalyzer',
    'RecommendationEngine',
    'InvestmentRecommendation',
    'RecommendationType',
    'ConfidenceLevel'
]
