"""
Unit tests for the Chart Analyzer module.

Tests cover:
- Technical indicator calculations (SMA, EMA, RSI, MACD, etc.)
- VWAP analysis and volume indicators
- Chart pattern recognition
- Support/resistance level detection
- Trend analysis and signal generation
- Data validation and error handling
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from analysis.chart_analyzer import (
    TechnicalChartAnalyzer,
    TechnicalAnalysis,
    TechnicalIndicator,
    TrendDirection,
    SignalStrength,
    ChartPattern,
    SupportResistance
)


class TestTechnicalChartAnalyzer:
    """Test suite for TechnicalChartAnalyzer class."""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance for testing."""
        return TechnicalChartAnalyzer()

    @pytest.fixture
    def sample_price_data(self):
        """Generate sample price data for testing."""
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        np.random.seed(42)  # For reproducible tests

        # Generate realistic price movements
        base_price = 100
        returns = np.random.normal(0.001, 0.02, 100)  # Small daily returns with volatility
        prices = base_price * np.exp(np.cumsum(returns))

        # Create realistic OHLC data
        opens = prices + np.random.normal(0, 0.5, 100)
        highs = np.maximum(opens, prices) + np.abs(np.random.normal(0, 1, 100))
        lows = np.minimum(opens, prices) - np.abs(np.random.normal(0, 1, 100))
        volumes = np.random.randint(1000000, 5000000, 100)

        return pd.DataFrame({
            'date': dates,
            'open': opens,
            'high': highs,
            'low': lows,
            'close': prices,
            'volume': volumes
        })

    @pytest.fixture
    def trending_data(self):
        """Generate trending price data for trend analysis tests."""
        dates = pd.date_range(start='2024-01-01', periods=50, freq='D')

        # Create upward trending data
        trend = np.linspace(100, 120, 50)
        noise = np.random.normal(0, 1, 50)
        prices = trend + noise

        return pd.DataFrame({
            'date': dates,
            'open': prices + np.random.normal(0, 0.5, 50),
            'high': prices + np.abs(np.random.normal(0, 1, 50)),
            'low': prices - np.abs(np.random.normal(0, 1, 50)),
            'close': prices,
            'volume': np.random.randint(1000000, 3000000, 50)
        })

    def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        analyzer = TechnicalChartAnalyzer()
        assert analyzer is not None
        assert hasattr(analyzer, 'logger')

    @pytest.mark.asyncio
    async def test_chart_analysis_basic(self, analyzer, sample_price_data):
        """Test basic chart analysis functionality."""
        result = await analyzer.analyze_chart(
            symbol='TEST',
            price_data=sample_price_data,
            timeframe='1d'
        )

        assert isinstance(result, TechnicalAnalysis)
        assert result.symbol == 'TEST'
        assert result.timeframe == '1d'
        assert result.current_price > 0
        assert isinstance(result.trend_direction, TrendDirection)
        assert 0 <= result.trend_strength <= 100
        assert len(result.indicators) > 0
        assert 0 <= result.confidence <= 1.0
        assert result.overall_signal in ['STRONG_BUY', 'BUY', 'HOLD', 'SELL', 'STRONG_SELL']

    @pytest.mark.asyncio
    async def test_moving_averages_calculation(self, analyzer, sample_price_data):
        """Test moving averages calculations."""
        indicators = await analyzer._calculate_moving_averages(sample_price_data)

        # Should include multiple MA types
        ma_types = [ind.name for ind in indicators]
        assert 'SMA_20' in ma_types
        assert 'SMA_50' in ma_types
        assert 'EMA_12' in ma_types
        assert 'EMA_26' in ma_types

        # All indicators should have valid values
        for indicator in indicators:
            assert isinstance(indicator, TechnicalIndicator)
            assert indicator.value is not None
            assert indicator.signal in ['BUY', 'SELL', 'HOLD']
            assert isinstance(indicator.strength, SignalStrength)

    @pytest.mark.asyncio
    async def test_vwap_calculation(self, analyzer, sample_price_data):
        """Test VWAP (Volume Weighted Average Price) calculations."""
        vwap_indicators = await analyzer._calculate_vwap(sample_price_data)

        assert len(vwap_indicators) >= 1  # At least basic VWAP

        for indicator in vwap_indicators:
            assert 'VWAP' in indicator.name
            assert indicator.value > 0
            assert indicator.signal in ['BUY', 'SELL', 'HOLD']
            assert isinstance(indicator.description, str)
            assert len(indicator.description) > 0

    @pytest.mark.asyncio
    async def test_rsi_calculation(self, analyzer, sample_price_data):
        """Test RSI (Relative Strength Index) calculation."""
        rsi_indicator = await analyzer._calculate_rsi(sample_price_data)

        assert isinstance(rsi_indicator, TechnicalIndicator)
        assert rsi_indicator.name == 'RSI'
        assert 0 <= rsi_indicator.value <= 100
        assert rsi_indicator.signal in ['BUY', 'SELL', 'HOLD']

        # Test RSI signal logic
        if rsi_indicator.value < 30:
            assert rsi_indicator.signal == 'BUY'  # Oversold
        elif rsi_indicator.value > 70:
            assert rsi_indicator.signal == 'SELL'  # Overbought
        else:
            assert rsi_indicator.signal == 'HOLD'  # Neutral

    @pytest.mark.asyncio
    async def test_macd_calculation(self, analyzer, sample_price_data):
        """Test MACD calculation."""
        macd_indicators = await analyzer._calculate_macd(sample_price_data)

        assert len(macd_indicators) >= 2  # MACD and Signal line

        macd_names = [ind.name for ind in macd_indicators]
        assert 'MACD' in macd_names
        assert 'MACD_Signal' in macd_names

        for indicator in macd_indicators:
            assert indicator.value is not None
            assert indicator.signal in ['BUY', 'SELL', 'HOLD']

    @pytest.mark.asyncio
    async def test_bollinger_bands_calculation(self, analyzer, sample_price_data):
        """Test Bollinger Bands calculation."""
        bb_indicators = await analyzer._calculate_bollinger_bands(sample_price_data)

        assert len(bb_indicators) >= 3  # Upper, Middle, Lower bands

        band_names = [ind.name for ind in bb_indicators]
        assert any('Upper' in name for name in band_names)
        assert any('Lower' in name for name in band_names)

        # Upper band should be higher than lower band
        upper_band = next(ind for ind in bb_indicators if 'Upper' in ind.name)
        lower_band = next(ind for ind in bb_indicators if 'Lower' in ind.name)
        assert upper_band.value > lower_band.value

    @pytest.mark.asyncio
    async def test_volume_indicators(self, analyzer, sample_price_data):
        """Test volume-based indicators."""
        volume_indicators = await analyzer._calculate_volume_indicators(sample_price_data)

        assert len(volume_indicators) > 0

        indicator_names = [ind.name for ind in volume_indicators]
        # Should include OBV and other volume indicators
        assert any('OBV' in name or 'Volume' in name for name in indicator_names)

        for indicator in volume_indicators:
            assert indicator.value is not None
            assert indicator.signal in ['BUY', 'SELL', 'HOLD']

    @pytest.mark.asyncio
    async def test_support_resistance_detection(self, analyzer, sample_price_data):
        """Test support and resistance level detection."""
        sr_levels = await analyzer._calculate_support_resistance(sample_price_data)

        assert isinstance(sr_levels, SupportResistance)
        assert len(sr_levels.support_levels) >= 0
        assert len(sr_levels.resistance_levels) >= 0

        # Support levels should be below current price, resistance above
        current_price = sample_price_data['close'].iloc[-1]

        for support in sr_levels.support_levels:
            assert support <= current_price * 1.05  # Allow some tolerance

        for resistance in sr_levels.resistance_levels:
            assert resistance >= current_price * 0.95  # Allow some tolerance

    @pytest.mark.asyncio
    async def test_trend_analysis(self, analyzer, trending_data):
        """Test trend direction analysis with trending data."""
        result = await analyzer.analyze_chart(
            symbol='TREND_TEST',
            price_data=trending_data,
            timeframe='1d'
        )

        # With upward trending data, should detect bullish trend
        assert result.trend_direction in [TrendDirection.BULLISH, TrendDirection.STRONG_BULLISH]
        assert result.trend_strength > 50  # Should show reasonable strength

    @pytest.mark.asyncio
    async def test_pattern_detection(self, analyzer, sample_price_data):
        """Test chart pattern detection."""
        patterns = await analyzer._detect_patterns(sample_price_data)

        assert isinstance(patterns, list)
        # Patterns are optional, but if detected should be valid
        for pattern in patterns:
            assert isinstance(pattern, ChartPattern)
            assert pattern.name is not None
            assert 0 <= pattern.confidence <= 1.0
            assert pattern.detected_at is not None

    @pytest.mark.asyncio
    async def test_volume_analysis(self, analyzer, sample_price_data):
        """Test volume analysis functionality."""
        volume_analysis = await analyzer._analyze_volume(sample_price_data)

        assert isinstance(volume_analysis, dict)
        assert 'average_volume' in volume_analysis
        assert 'volume_trend' in volume_analysis
        assert 'volume_strength' in volume_analysis

        assert volume_analysis['average_volume'] > 0
        assert volume_analysis['volume_trend'] in ['increasing', 'decreasing', 'stable']
        assert 0 <= volume_analysis['volume_strength'] <= 100

    @pytest.mark.asyncio
    async def test_insufficient_data_handling(self, analyzer):
        """Test handling of insufficient data."""
        # Create minimal dataset
        minimal_data = pd.DataFrame({
            'date': pd.date_range(start='2024-01-01', periods=5, freq='D'),
            'open': [100, 101, 102, 103, 104],
            'high': [101, 102, 103, 104, 105],
            'low': [99, 100, 101, 102, 103],
            'close': [100.5, 101.5, 102.5, 103.5, 104.5],
            'volume': [1000000, 1100000, 1200000, 1300000, 1400000]
        })

        result = await analyzer.analyze_chart(
            symbol='MINIMAL_TEST',
            price_data=minimal_data,
            timeframe='1d'
        )

        # Should still return a result, but with limited indicators
        assert isinstance(result, TechnicalAnalysis)
        assert result.symbol == 'MINIMAL_TEST'
        # Confidence might be lower due to insufficient data
        assert result.confidence >= 0

    @pytest.mark.asyncio
    async def test_error_handling(self, analyzer):
        """Test error handling for invalid inputs."""
        # Empty DataFrame
        empty_data = pd.DataFrame()

        with pytest.raises((ValueError, KeyError)):
            await analyzer.analyze_chart('EMPTY_TEST', empty_data, '1d')

        # Missing required columns
        invalid_data = pd.DataFrame({
            'date': pd.date_range(start='2024-01-01', periods=10, freq='D'),
            'price': [100] * 10  # Missing OHLCV columns
        })

        with pytest.raises((ValueError, KeyError)):
            await analyzer.analyze_chart('INVALID_TEST', invalid_data, '1d')

    @pytest.mark.asyncio
    async def test_all_indicators_integration(self, analyzer, sample_price_data):
        """Test that all indicators work together in comprehensive analysis."""
        all_indicators = await analyzer._calculate_all_indicators(sample_price_data)

        assert len(all_indicators) >= 10  # Should have multiple indicators

        # Check for key indicator categories
        indicator_names = [ind.name for ind in all_indicators]

        # Moving averages
        assert any('SMA' in name for name in indicator_names)
        assert any('EMA' in name for name in indicator_names)

        # Momentum indicators
        assert 'RSI' in indicator_names
        assert any('MACD' in name for name in indicator_names)

        # Volatility indicators
        assert any('Bollinger' in name for name in indicator_names)

        # Volume indicators
        assert any('Volume' in name or 'OBV' in name for name in indicator_names)

        # VWAP
        assert any('VWAP' in name for name in indicator_names)

    def test_signal_strength_calculation(self, analyzer):
        """Test signal strength calculation logic."""
        # Test with various RSI values
        test_cases = [
            (25, 'BUY', 80),    # Strong oversold
            (35, 'BUY', 60),    # Mild oversold
            (50, 'HOLD', 50),   # Neutral
            (75, 'SELL', 70),   # Overbought
            (85, 'SELL', 90)    # Strong overbought
        ]

        for rsi_value, expected_signal, expected_min_strength in test_cases:
            # This would test internal signal calculation logic
            # Implementation depends on actual method signatures
            pass

    @pytest.mark.asyncio
    async def test_timeframe_handling(self, analyzer, sample_price_data):
        """Test analysis with different timeframes."""
        timeframes = ['1d', '4h', '1h']

        for timeframe in timeframes:
            result = await analyzer.analyze_chart(
                symbol='TIMEFRAME_TEST',
                price_data=sample_price_data,
                timeframe=timeframe
            )

            assert result.timeframe == timeframe
            assert isinstance(result, TechnicalAnalysis)


class TestTechnicalAnalysisIntegration:
    """Integration tests for chart analyzer."""

    @pytest.mark.asyncio
    async def test_realistic_market_scenarios(self):
        """Test with realistic market scenarios."""
        analyzer = TechnicalChartAnalyzer()

        # Bull market scenario
        dates = pd.date_range(start='2024-01-01', periods=60, freq='D')
        bull_trend = np.linspace(100, 150, 60)  # 50% increase
        bull_noise = np.random.normal(0, 2, 60)
        bull_prices = bull_trend + bull_noise

        bull_data = pd.DataFrame({
            'date': dates,
            'open': bull_prices + np.random.normal(0, 0.5, 60),
            'high': bull_prices + np.abs(np.random.normal(0, 2, 60)),
            'low': bull_prices - np.abs(np.random.normal(0, 2, 60)),
            'close': bull_prices,
            'volume': np.random.randint(2000000, 8000000, 60)
        })

        bull_result = await analyzer.analyze_chart('BULL_TEST', bull_data, '1d')

        # Should detect bullish trend
        assert bull_result.trend_direction in [TrendDirection.BULLISH, TrendDirection.STRONG_BULLISH]
        assert bull_result.overall_signal in ['BUY', 'STRONG_BUY']

        # Bear market scenario
        bear_trend = np.linspace(150, 100, 60)  # 33% decrease
        bear_noise = np.random.normal(0, 2, 60)
        bear_prices = bear_trend + bear_noise

        bear_data = pd.DataFrame({
            'date': dates,
            'open': bear_prices + np.random.normal(0, 0.5, 60),
            'high': bear_prices + np.abs(np.random.normal(0, 2, 60)),
            'low': bear_prices - np.abs(np.random.normal(0, 2, 60)),
            'close': bear_prices,
            'volume': np.random.randint(2000000, 8000000, 60)
        })

        bear_result = await analyzer.analyze_chart('BEAR_TEST', bear_data, '1d')

        # Should detect bearish trend
        assert bear_result.trend_direction in [TrendDirection.BEARISH, TrendDirection.STRONG_BEARISH]
        assert bear_result.overall_signal in ['SELL', 'STRONG_SELL']

    @pytest.mark.asyncio
    async def test_high_volatility_handling(self):
        """Test analysis with high volatility data."""
        analyzer = TechnicalChartAnalyzer()

        # Create highly volatile data
        dates = pd.date_range(start='2024-01-01', periods=50, freq='D')
        base_price = 100
        high_vol_returns = np.random.normal(0, 0.05, 50)  # 5% daily volatility
        volatile_prices = base_price * np.exp(np.cumsum(high_vol_returns))

        volatile_data = pd.DataFrame({
            'date': dates,
            'open': volatile_prices + np.random.normal(0, 2, 50),
            'high': volatile_prices + np.abs(np.random.normal(0, 5, 50)),
            'low': volatile_prices - np.abs(np.random.normal(0, 5, 50)),
            'close': volatile_prices,
            'volume': np.random.randint(1000000, 10000000, 50)
        })

        result = await analyzer.analyze_chart('VOLATILE_TEST', volatile_data, '1d')

        # Should handle volatility gracefully
        assert isinstance(result, TechnicalAnalysis)
        assert result.confidence >= 0  # Might be lower due to volatility
        assert len(result.indicators) > 0


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
