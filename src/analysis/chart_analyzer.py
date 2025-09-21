"""
Chart Analyzer for the Agent Investment Platform.

This module provides comprehensive technical analysis capabilities including
trend analysis, momentum indicators, volatility measures, and pattern recognition
to support automated investment decision-making.

Key Features:
- 20+ technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands, etc.)
- Chart pattern recognition (Head & Shoulders, Double Top/Bottom, etc.)
- Support/resistance level detection
- Trend analysis and momentum scoring
- Volume analysis and price action insights
- Integration with multiple data sources
"""

import asyncio
import logging
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum
import json

import pandas as pd
import numpy as np


class TrendDirection(Enum):
    """Trend direction classification."""
    STRONG_BEARISH = -2
    BEARISH = -1
    SIDEWAYS = 0
    BULLISH = 1
    STRONG_BULLISH = 2


class SignalStrength(Enum):
    """Signal strength classification."""
    VERY_WEAK = 1
    WEAK = 2
    MODERATE = 3
    STRONG = 4
    VERY_STRONG = 5


@dataclass
class TechnicalIndicator:
    """Individual technical indicator result."""
    name: str
    value: float
    signal: str  # "BUY", "SELL", "HOLD"
    strength: SignalStrength
    description: str
    timestamp: datetime


@dataclass
class ChartPattern:
    """Detected chart pattern."""
    name: str
    confidence: float  # 0.0 to 1.0
    target_price: Optional[float]
    stop_loss: Optional[float]
    timeframe: str
    description: str
    detected_at: datetime


@dataclass
class SupportResistance:
    """Support and resistance levels."""
    support_levels: List[float]
    resistance_levels: List[float]
    current_level_type: str  # "SUPPORT", "RESISTANCE", "BETWEEN"
    strength_score: float  # 0.0 to 1.0
    nearest_support: float
    nearest_resistance: float


@dataclass
class TechnicalAnalysis:
    """Complete technical analysis result."""
    symbol: str
    timeframe: str
    current_price: float
    trend_direction: TrendDirection
    trend_strength: float
    indicators: List[TechnicalIndicator]
    patterns: List[ChartPattern]
    support_resistance: SupportResistance
    volume_analysis: Dict[str, Any]
    overall_signal: str  # "STRONG_BUY", "BUY", "HOLD", "SELL", "STRONG_SELL"
    confidence: float
    analysis_timestamp: datetime


class TechnicalChartAnalyzer:
    """
    Advanced technical analysis engine for financial markets.
    
    Provides comprehensive technical analysis including:
    - Moving averages and trend indicators
    - Momentum oscillators (RSI, MACD, Stochastic)
    - Volatility indicators (Bollinger Bands, ATR)
    - Volume indicators (OBV, Volume SMA)
    - Pattern recognition algorithms
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Technical analysis parameters
        self.default_periods = {
            'sma_short': 20,
            'sma_medium': 50,
            'sma_long': 200,
            'ema_short': 12,
            'ema_medium': 26,
            'ema_long': 50,
            'rsi_period': 14,
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            'bb_period': 20,
            'bb_std': 2,
            'atr_period': 14,
            'volume_sma': 20,
            'vwap_period': 20
        }
    
    async def analyze_chart(self, symbol: str, price_data: pd.DataFrame, 
                           timeframe: str = "1D") -> TechnicalAnalysis:
        """
        Perform comprehensive technical analysis on price data.
        
        Args:
            symbol: Stock symbol
            price_data: DataFrame with OHLCV data
            timeframe: Analysis timeframe
            
        Returns:
            TechnicalAnalysis with complete analysis results
        """
        if price_data.empty or len(price_data) < 50:
            raise ValueError("Insufficient price data for technical analysis")
        
        # Ensure data is sorted by date
        price_data = price_data.sort_index()
        
        # Calculate all technical indicators
        indicators = await self._calculate_all_indicators(price_data)
        
        # Detect chart patterns
        patterns = await self._detect_patterns(price_data)
        
        # Calculate support/resistance levels
        support_resistance = await self._calculate_support_resistance(price_data)
        
        # Analyze volume
        volume_analysis = await self._analyze_volume(price_data)
        
        # Determine overall trend
        trend_direction, trend_strength = self._analyze_trend(indicators, price_data)
        
        # Generate overall signal
        overall_signal, confidence = self._generate_overall_signal(
            indicators, patterns, trend_direction, trend_strength
        )
        
        current_price = float(price_data['close'].iloc[-1])
        
        return TechnicalAnalysis(
            symbol=symbol,
            timeframe=timeframe,
            current_price=current_price,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            indicators=indicators,
            patterns=patterns,
            support_resistance=support_resistance,
            volume_analysis=volume_analysis,
            overall_signal=overall_signal,
            confidence=confidence,
            analysis_timestamp=datetime.now()
        )
    
    async def _calculate_all_indicators(self, data: pd.DataFrame) -> List[TechnicalIndicator]:
        """Calculate all technical indicators."""
        indicators = []
        
        # Moving Averages (SMA and EMA)
        indicators.extend(await self._calculate_moving_averages(data))
        
        # VWAP (Volume Weighted Average Price)
        indicators.extend(await self._calculate_vwap(data))
        
        # RSI
        indicators.append(await self._calculate_rsi(data))
        
        # MACD
        indicators.extend(await self._calculate_macd(data))
        
        # Bollinger Bands
        indicators.extend(await self._calculate_bollinger_bands(data))
        
        # Stochastic
        indicators.extend(await self._calculate_stochastic(data))
        
        # ATR
        indicators.append(await self._calculate_atr(data))
        
        # Volume indicators
        indicators.extend(await self._calculate_volume_indicators(data))
        
        return indicators
    
    async def _calculate_moving_averages(self, data: pd.DataFrame) -> List[TechnicalIndicator]:
        """Calculate comprehensive moving average indicators (SMA and EMA)."""
        indicators = []
        
        # Simple Moving Averages
        sma_20 = data['close'].rolling(window=self.default_periods['sma_short']).mean()
        sma_50 = data['close'].rolling(window=self.default_periods['sma_medium']).mean()
        sma_200 = data['close'].rolling(window=self.default_periods['sma_long']).mean()
        
        # Exponential Moving Averages
        ema_12 = data['close'].ewm(span=self.default_periods['ema_short']).mean()
        ema_26 = data['close'].ewm(span=self.default_periods['ema_medium']).mean()
        ema_50 = data['close'].ewm(span=self.default_periods['ema_long']).mean()
        
        current_price = data['close'].iloc[-1]
        current_sma_20 = sma_20.iloc[-1]
        current_sma_50 = sma_50.iloc[-1]
        current_sma_200 = sma_200.iloc[-1]
        current_ema_12 = ema_12.iloc[-1]
        current_ema_26 = ema_26.iloc[-1]
        current_ema_50 = ema_50.iloc[-1]
        
        # SMA 20 analysis
        if current_price > current_sma_20:
            sma_20_signal = "BUY" if current_price > current_sma_20 * 1.02 else "HOLD"
            strength = SignalStrength.STRONG if current_price > current_sma_20 * 1.05 else SignalStrength.MODERATE
        else:
            sma_20_signal = "SELL" if current_price < current_sma_20 * 0.98 else "HOLD"
            strength = SignalStrength.STRONG if current_price < current_sma_20 * 0.95 else SignalStrength.MODERATE
        
        indicators.append(TechnicalIndicator(
            name="SMA_20",
            value=current_sma_20,
            signal=sma_20_signal,
            strength=strength,
            description=f"20-period Simple Moving Average: {current_sma_20:.2f}",
            timestamp=datetime.now()
        ))
        
        # SMA 200 (Long-term trend indicator)
        if len(sma_200) > 0 and not pd.isna(current_sma_200):
            if current_price > current_sma_200:
                sma_200_signal = "BUY"
                strength = SignalStrength.MODERATE
                description = f"Price above 200-day SMA ({current_sma_200:.2f}) - Long-term bullish"
            else:
                sma_200_signal = "SELL"
                strength = SignalStrength.MODERATE
                description = f"Price below 200-day SMA ({current_sma_200:.2f}) - Long-term bearish"
            
            indicators.append(TechnicalIndicator(
                name="SMA_200",
                value=current_sma_200,
                signal=sma_200_signal,
                strength=strength,
                description=description,
                timestamp=datetime.now()
            ))
        
        # EMA 12/26 crossover analysis
        if len(ema_12) > 1 and len(ema_26) > 1:
            prev_ema_12 = ema_12.iloc[-2]
            prev_ema_26 = ema_26.iloc[-2]
            
            ema_bullish_cross = (current_ema_12 > current_ema_26 and prev_ema_12 <= prev_ema_26)
            ema_bearish_cross = (current_ema_12 < current_ema_26 and prev_ema_12 >= prev_ema_26)
            
            if ema_bullish_cross:
                signal = "BUY"
                strength = SignalStrength.STRONG
                description = "EMA bullish crossover - EMA 12 crossed above EMA 26"
            elif ema_bearish_cross:
                signal = "SELL"
                strength = SignalStrength.STRONG
                description = "EMA bearish crossover - EMA 12 crossed below EMA 26"
            elif current_ema_12 > current_ema_26:
                signal = "BUY"
                strength = SignalStrength.WEAK
                description = "EMA 12 above EMA 26 - Short-term bullish"
            else:
                signal = "SELL"
                strength = SignalStrength.WEAK
                description = "EMA 12 below EMA 26 - Short-term bearish"
            
            indicators.append(TechnicalIndicator(
                name="EMA_CROSS",
                value=current_ema_12 - current_ema_26,
                signal=signal,
                strength=strength,
                description=description,
                timestamp=datetime.now()
            ))
        
        # Golden Cross / Death Cross analysis (SMA 20/50)
        if len(sma_20) > 1 and len(sma_50) > 1:
            prev_sma_20 = sma_20.iloc[-2]
            prev_sma_50 = sma_50.iloc[-2]
            
            golden_cross = (current_sma_20 > current_sma_50 and prev_sma_20 <= prev_sma_50)
            death_cross = (current_sma_20 < current_sma_50 and prev_sma_20 >= prev_sma_50)
            
            if golden_cross:
                signal = "BUY"
                strength = SignalStrength.VERY_STRONG
                description = "Golden Cross detected - SMA 20 crossed above SMA 50"
            elif death_cross:
                signal = "SELL"
                strength = SignalStrength.VERY_STRONG
                description = "Death Cross detected - SMA 20 crossed below SMA 50"
            elif current_sma_20 > current_sma_50:
                signal = "BUY"
                strength = SignalStrength.MODERATE
                description = "SMA 20 above SMA 50 - Medium-term bullish"
            else:
                signal = "SELL"
                strength = SignalStrength.MODERATE
                description = "SMA 20 below SMA 50 - Medium-term bearish"
            
            indicators.append(TechnicalIndicator(
                name="SMA_CROSS",
                value=current_sma_20 - current_sma_50,
                signal=signal,
                strength=strength,
                description=description,
                timestamp=datetime.now()
            ))
        
        # Moving Average Confluence (Price position relative to all MAs)
        ma_above_count = 0
        ma_total_count = 0
        
        for ma_value in [current_sma_20, current_sma_50, current_sma_200, current_ema_12, current_ema_26, current_ema_50]:
            if not pd.isna(ma_value):
                ma_total_count += 1
                if current_price > ma_value:
                    ma_above_count += 1
        
        if ma_total_count > 0:
            ma_confluence_ratio = ma_above_count / ma_total_count
            
            if ma_confluence_ratio >= 0.8:
                signal = "BUY"
                strength = SignalStrength.STRONG
                description = f"Strong MA confluence - Price above {ma_above_count}/{ma_total_count} moving averages"
            elif ma_confluence_ratio >= 0.6:
                signal = "BUY"
                strength = SignalStrength.MODERATE
                description = f"Bullish MA confluence - Price above {ma_above_count}/{ma_total_count} moving averages"
            elif ma_confluence_ratio <= 0.2:
                signal = "SELL"
                strength = SignalStrength.STRONG
                description = f"Weak MA confluence - Price below {ma_total_count - ma_above_count}/{ma_total_count} moving averages"
            elif ma_confluence_ratio <= 0.4:
                signal = "SELL"
                strength = SignalStrength.MODERATE
                description = f"Bearish MA confluence - Price below {ma_total_count - ma_above_count}/{ma_total_count} moving averages"
            else:
                signal = "HOLD"
                strength = SignalStrength.WEAK
                description = f"Mixed MA signals - Price above {ma_above_count}/{ma_total_count} moving averages"
            
            indicators.append(TechnicalIndicator(
                name="MA_CONFLUENCE",
                value=ma_confluence_ratio,
                signal=signal,
                strength=strength,
                description=description,
                timestamp=datetime.now()
            ))
        
        return indicators
    
    async def _calculate_vwap(self, data: pd.DataFrame) -> List[TechnicalIndicator]:
        """Calculate Volume Weighted Average Price (VWAP) indicators."""
        indicators = []
        
        if 'volume' not in data.columns:
            return indicators
        
        # Calculate VWAP
        typical_price = (data['high'] + data['low'] + data['close']) / 3
        vwap_numerator = (typical_price * data['volume']).cumsum()
        vwap_denominator = data['volume'].cumsum()
        vwap = vwap_numerator / vwap_denominator
        
        # Calculate rolling VWAP (20-period)
        rolling_vwap_num = (typical_price * data['volume']).rolling(window=self.default_periods['vwap_period']).sum()
        rolling_vwap_den = data['volume'].rolling(window=self.default_periods['vwap_period']).sum()
        rolling_vwap = rolling_vwap_num / rolling_vwap_den
        
        current_price = data['close'].iloc[-1]
        current_vwap = vwap.iloc[-1]
        current_rolling_vwap = rolling_vwap.iloc[-1]
        current_volume = data['volume'].iloc[-1]
        avg_volume = data['volume'].rolling(window=20).mean().iloc[-1]
        
        # VWAP Analysis
        price_vs_vwap = (current_price - current_vwap) / current_vwap * 100
        
        if current_price > current_vwap:
            if price_vs_vwap > 2.0:
                vwap_signal = "SELL"  # Overextended above VWAP
                strength = SignalStrength.MODERATE
                description = f"Price {price_vs_vwap:.1f}% above VWAP ({current_vwap:.2f}) - potentially overextended"
            else:
                vwap_signal = "BUY"
                strength = SignalStrength.MODERATE
                description = f"Price above VWAP ({current_vwap:.2f}) - bullish momentum"
        else:
            if price_vs_vwap < -2.0:
                vwap_signal = "BUY"  # Oversold below VWAP
                strength = SignalStrength.MODERATE
                description = f"Price {abs(price_vs_vwap):.1f}% below VWAP ({current_vwap:.2f}) - potentially oversold"
            else:
                vwap_signal = "SELL"
                strength = SignalStrength.MODERATE
                description = f"Price below VWAP ({current_vwap:.2f}) - bearish pressure"
        
        indicators.append(TechnicalIndicator(
            name="VWAP",
            value=current_vwap,
            signal=vwap_signal,
            strength=strength,
            description=description,
            timestamp=datetime.now()
        ))
        
        # Rolling VWAP (shorter-term)
        if not pd.isna(current_rolling_vwap):
            rolling_price_vs_vwap = (current_price - current_rolling_vwap) / current_rolling_vwap * 100
            
            if current_price > current_rolling_vwap:
                if rolling_price_vs_vwap > 1.5:
                    rolling_signal = "HOLD"
                    strength = SignalStrength.WEAK
                    description = f"Price {rolling_price_vs_vwap:.1f}% above 20-period VWAP - near resistance"
                else:
                    rolling_signal = "BUY"
                    strength = SignalStrength.MODERATE
                    description = f"Price above 20-period VWAP ({current_rolling_vwap:.2f}) - short-term bullish"
            else:
                if rolling_price_vs_vwap < -1.5:
                    rolling_signal = "HOLD"
                    strength = SignalStrength.WEAK
                    description = f"Price {abs(rolling_price_vs_vwap):.1f}% below 20-period VWAP - near support"
                else:
                    rolling_signal = "SELL"
                    strength = SignalStrength.MODERATE
                    description = f"Price below 20-period VWAP ({current_rolling_vwap:.2f}) - short-term bearish"
            
            indicators.append(TechnicalIndicator(
                name="VWAP_20",
                value=current_rolling_vwap,
                signal=rolling_signal,
                strength=strength,
                description=description,
                timestamp=datetime.now()
            ))
        
        # VWAP Volume Analysis
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        # Enhanced signal based on volume confirmation
        if volume_ratio > 1.5:  # High volume
            if current_price > current_vwap:
                volume_signal = "BUY"
                strength = SignalStrength.STRONG
                description = f"High volume ({volume_ratio:.1f}x avg) with price above VWAP - strong bullish momentum"
            else:
                volume_signal = "SELL"
                strength = SignalStrength.STRONG
                description = f"High volume ({volume_ratio:.1f}x avg) with price below VWAP - strong bearish pressure"
        else:
            volume_signal = "HOLD"
            strength = SignalStrength.WEAK
            description = f"Normal volume ({volume_ratio:.1f}x avg) - VWAP signal less reliable"
        
        indicators.append(TechnicalIndicator(
            name="VWAP_VOLUME",
            value=volume_ratio,
            signal=volume_signal,
            strength=strength,
            description=description,
            timestamp=datetime.now()
        ))
        
        return indicators
    
    async def _calculate_rsi(self, data: pd.DataFrame) -> TechnicalIndicator:
        """Calculate RSI indicator."""
        period = self.default_periods['rsi_period']
        
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        
        # RSI signal interpretation
        if current_rsi > 70:
            signal = "SELL"
            strength = SignalStrength.STRONG if current_rsi > 80 else SignalStrength.MODERATE
            description = f"RSI {current_rsi:.1f} - Overbought condition"
        elif current_rsi < 30:
            signal = "BUY"
            strength = SignalStrength.STRONG if current_rsi < 20 else SignalStrength.MODERATE
            description = f"RSI {current_rsi:.1f} - Oversold condition"
        else:
            signal = "HOLD"
            strength = SignalStrength.WEAK
            description = f"RSI {current_rsi:.1f} - Neutral zone"
        
        return TechnicalIndicator(
            name="RSI",
            value=current_rsi,
            signal=signal,
            strength=strength,
            description=description,
            timestamp=datetime.now()
        )
    
    async def _calculate_macd(self, data: pd.DataFrame) -> List[TechnicalIndicator]:
        """Calculate MACD indicators."""
        fast_period = self.default_periods['macd_fast']
        slow_period = self.default_periods['macd_slow']
        signal_period = self.default_periods['macd_signal']
        
        ema_fast = data['close'].ewm(span=fast_period).mean()
        ema_slow = data['close'].ewm(span=slow_period).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal_period).mean()
        histogram = macd_line - signal_line
        
        current_macd = macd_line.iloc[-1]
        current_signal = signal_line.iloc[-1]
        current_histogram = histogram.iloc[-1]
        
        indicators = []
        
        # MACD Line vs Signal Line
        if current_macd > current_signal:
            if len(macd_line) > 1 and macd_line.iloc[-2] <= signal_line.iloc[-2]:
                # Bullish crossover
                signal = "BUY"
                strength = SignalStrength.STRONG
                description = "MACD bullish crossover - strong buy signal"
            else:
                signal = "BUY"
                strength = SignalStrength.MODERATE
                description = "MACD above signal line - bullish momentum"
        else:
            if len(macd_line) > 1 and macd_line.iloc[-2] >= signal_line.iloc[-2]:
                # Bearish crossover
                signal = "SELL"
                strength = SignalStrength.STRONG
                description = "MACD bearish crossover - strong sell signal"
            else:
                signal = "SELL"
                strength = SignalStrength.MODERATE
                description = "MACD below signal line - bearish momentum"
        
        indicators.append(TechnicalIndicator(
            name="MACD",
            value=current_macd,
            signal=signal,
            strength=strength,
            description=description,
            timestamp=datetime.now()
        ))
        
        # MACD Histogram
        if len(histogram) > 1:
            prev_histogram = histogram.iloc[-2]
            if current_histogram > prev_histogram and current_histogram > 0:
                hist_signal = "BUY"
                hist_strength = SignalStrength.MODERATE
                hist_description = "MACD histogram increasing - strengthening bullish momentum"
            elif current_histogram < prev_histogram and current_histogram < 0:
                hist_signal = "SELL"
                hist_strength = SignalStrength.MODERATE
                hist_description = "MACD histogram decreasing - strengthening bearish momentum"
            else:
                hist_signal = "HOLD"
                hist_strength = SignalStrength.WEAK
                hist_description = "MACD histogram showing mixed signals"
            
            indicators.append(TechnicalIndicator(
                name="MACD_HISTOGRAM",
                value=current_histogram,
                signal=hist_signal,
                strength=hist_strength,
                description=hist_description,
                timestamp=datetime.now()
            ))
        
        return indicators
    
    async def _calculate_bollinger_bands(self, data: pd.DataFrame) -> List[TechnicalIndicator]:
        """Calculate Bollinger Bands indicators."""
        period = self.default_periods['bb_period']
        std_dev = self.default_periods['bb_std']
        
        sma = data['close'].rolling(window=period).mean()
        std = data['close'].rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        current_price = data['close'].iloc[-1]
        current_upper = upper_band.iloc[-1]
        current_lower = lower_band.iloc[-1]
        current_sma = sma.iloc[-1]
        
        indicators = []
        
        # Bollinger Band position
        bb_position = (current_price - current_lower) / (current_upper - current_lower)
        
        if bb_position > 0.8:
            signal = "SELL"
            strength = SignalStrength.STRONG if bb_position > 0.95 else SignalStrength.MODERATE
            description = f"Price near upper Bollinger Band ({bb_position:.1%}) - potential resistance"
        elif bb_position < 0.2:
            signal = "BUY"
            strength = SignalStrength.STRONG if bb_position < 0.05 else SignalStrength.MODERATE
            description = f"Price near lower Bollinger Band ({bb_position:.1%}) - potential support"
        else:
            signal = "HOLD"
            strength = SignalStrength.WEAK
            description = f"Price in middle of Bollinger Bands ({bb_position:.1%}) - neutral"
        
        indicators.append(TechnicalIndicator(
            name="BOLLINGER_POSITION",
            value=bb_position,
            signal=signal,
            strength=strength,
            description=description,
            timestamp=datetime.now()
        ))
        
        # Bollinger Band squeeze detection
        current_bandwidth = (current_upper - current_lower) / current_sma
        if len(upper_band) >= 20:
            avg_bandwidth = ((upper_band - lower_band) / sma).tail(20).mean()
            if current_bandwidth < avg_bandwidth * 0.7:
                squeeze_signal = "HOLD"
                squeeze_strength = SignalStrength.MODERATE
                squeeze_description = "Bollinger Band squeeze detected - potential breakout pending"
            else:
                squeeze_signal = "HOLD"
                squeeze_strength = SignalStrength.WEAK
                squeeze_description = "Normal Bollinger Band width"
            
            indicators.append(TechnicalIndicator(
                name="BOLLINGER_SQUEEZE",
                value=current_bandwidth,
                signal=squeeze_signal,
                strength=squeeze_strength,
                description=squeeze_description,
                timestamp=datetime.now()
            ))
        
        return indicators
    
    async def _calculate_stochastic(self, data: pd.DataFrame) -> List[TechnicalIndicator]:
        """Calculate Stochastic oscillator."""
        k_period = 14
        d_period = 3
        
        lowest_low = data['low'].rolling(window=k_period).min()
        highest_high = data['high'].rolling(window=k_period).max()
        
        k_percent = 100 * (data['close'] - lowest_low) / (highest_high - lowest_low)
        d_percent = k_percent.rolling(window=d_period).mean()
        
        current_k = k_percent.iloc[-1]
        current_d = d_percent.iloc[-1]
        
        indicators = []
        
        # Stochastic overbought/oversold
        if current_k > 80 and current_d > 80:
            signal = "SELL"
            strength = SignalStrength.MODERATE
            description = f"Stochastic overbought (%K: {current_k:.1f}, %D: {current_d:.1f})"
        elif current_k < 20 and current_d < 20:
            signal = "BUY"
            strength = SignalStrength.MODERATE
            description = f"Stochastic oversold (%K: {current_k:.1f}, %D: {current_d:.1f})"
        else:
            signal = "HOLD"
            strength = SignalStrength.WEAK
            description = f"Stochastic neutral (%K: {current_k:.1f}, %D: {current_d:.1f})"
        
        indicators.append(TechnicalIndicator(
            name="STOCHASTIC",
            value=current_k,
            signal=signal,
            strength=strength,
            description=description,
            timestamp=datetime.now()
        ))
        
        return indicators
    
    async def _calculate_atr(self, data: pd.DataFrame) -> TechnicalIndicator:
        """Calculate Average True Range."""
        period = self.default_periods['atr_period']
        
        high_low = data['high'] - data['low']
        high_close_prev = abs(data['high'] - data['close'].shift(1))
        low_close_prev = abs(data['low'] - data['close'].shift(1))
        
        true_range = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()
        
        current_atr = atr.iloc[-1]
        current_price = data['close'].iloc[-1]
        atr_percentage = (current_atr / current_price) * 100
        
        # ATR interpretation for volatility
        if atr_percentage > 3:
            description = f"High volatility (ATR: {atr_percentage:.1f}%) - increased risk"
            strength = SignalStrength.STRONG
        elif atr_percentage > 1.5:
            description = f"Moderate volatility (ATR: {atr_percentage:.1f}%) - normal conditions"
            strength = SignalStrength.MODERATE
        else:
            description = f"Low volatility (ATR: {atr_percentage:.1f}%) - consolidation phase"
            strength = SignalStrength.WEAK
        
        return TechnicalIndicator(
            name="ATR",
            value=current_atr,
            signal="HOLD",  # ATR is not directional
            strength=strength,
            description=description,
            timestamp=datetime.now()
        )
    
    async def _calculate_volume_indicators(self, data: pd.DataFrame) -> List[TechnicalIndicator]:
        """Calculate comprehensive volume-based indicators."""
        indicators = []
        
        if 'volume' not in data.columns:
            return indicators
        
        # Volume SMA
        volume_sma = data['volume'].rolling(window=self.default_periods['volume_sma']).mean()
        current_volume = data['volume'].iloc[-1]
        current_volume_sma = volume_sma.iloc[-1]
        
        volume_ratio = current_volume / current_volume_sma if current_volume_sma > 0 else 1
        
        # Enhanced volume ratio analysis
        price_change = data['close'].iloc[-1] - data['close'].iloc[-2]
        price_direction = "up" if price_change > 0 else "down" if price_change < 0 else "flat"
        
        if volume_ratio > 2.0:
            if price_direction == "up":
                signal = "BUY"
                strength = SignalStrength.VERY_STRONG
                description = f"High volume spike ({volume_ratio:.1f}x avg) with price up - strong bullish momentum"
            elif price_direction == "down":
                signal = "SELL"
                strength = SignalStrength.VERY_STRONG
                description = f"High volume spike ({volume_ratio:.1f}x avg) with price down - strong bearish pressure"
            else:
                signal = "HOLD"
                strength = SignalStrength.MODERATE
                description = f"High volume spike ({volume_ratio:.1f}x avg) with flat price - potential breakout pending"
        elif volume_ratio > 1.5:
            signal = "HOLD"
            strength = SignalStrength.MODERATE
            description = f"Above average volume ({volume_ratio:.1f}x avg) - increased interest"
        elif volume_ratio < 0.5:
            signal = "HOLD"
            strength = SignalStrength.WEAK
            description = f"Low volume ({volume_ratio:.1f}x avg) - lack of conviction"
        else:
            signal = "HOLD"
            strength = SignalStrength.WEAK
            description = f"Normal volume ({volume_ratio:.1f}x avg) - average participation"
        
        indicators.append(TechnicalIndicator(
            name="VOLUME_RATIO",
            value=volume_ratio,
            signal=signal,
            strength=strength,
            description=description,
            timestamp=datetime.now()
        ))
        
        # On-Balance Volume (OBV)
        obv = []
        obv_value = 0
        
        for i in range(len(data)):
            if i == 0:
                obv.append(data['volume'].iloc[i])
                obv_value = data['volume'].iloc[i]
            else:
                if data['close'].iloc[i] > data['close'].iloc[i-1]:
                    obv_value += data['volume'].iloc[i]
                elif data['close'].iloc[i] < data['close'].iloc[i-1]:
                    obv_value -= data['volume'].iloc[i]
                # If close is unchanged, OBV remains the same
                obv.append(obv_value)
        
        obv_series = pd.Series(obv, index=data.index)
        obv_sma = obv_series.rolling(window=10).mean()
        
        current_obv = obv_series.iloc[-1]
        current_obv_sma = obv_sma.iloc[-1]
        
        # OBV analysis
        if len(obv_series) >= 10:
            obv_trend = "rising" if current_obv > obv_series.iloc[-10] else "falling"
            price_trend = "rising" if data['close'].iloc[-1] > data['close'].iloc[-10] else "falling"
            
            # OBV divergence analysis
            if obv_trend == "rising" and price_trend == "rising":
                obv_signal = "BUY"
                strength = SignalStrength.STRONG
                description = "OBV and price both rising - strong accumulation"
            elif obv_trend == "falling" and price_trend == "falling":
                obv_signal = "SELL"
                strength = SignalStrength.STRONG
                description = "OBV and price both falling - strong distribution"
            elif obv_trend == "rising" and price_trend == "falling":
                obv_signal = "BUY"
                strength = SignalStrength.MODERATE
                description = "Bullish OBV divergence - accumulation despite price decline"
            elif obv_trend == "falling" and price_trend == "rising":
                obv_signal = "SELL"
                strength = SignalStrength.MODERATE
                description = "Bearish OBV divergence - distribution despite price rise"
            else:
                obv_signal = "HOLD"
                strength = SignalStrength.WEAK
                description = "OBV showing mixed signals"
            
            indicators.append(TechnicalIndicator(
                name="OBV",
                value=current_obv,
                signal=obv_signal,
                strength=strength,
                description=description,
                timestamp=datetime.now()
            ))
        
        # Volume-Price Trend (VPT)
        vpt = []
        vpt_value = 0
        
        for i in range(len(data)):
            if i == 0:
                vpt.append(0)
            else:
                price_change_pct = (data['close'].iloc[i] - data['close'].iloc[i-1]) / data['close'].iloc[i-1]
                vpt_value += data['volume'].iloc[i] * price_change_pct
                vpt.append(vpt_value)
        
        vpt_series = pd.Series(vpt, index=data.index)
        current_vpt = vpt_series.iloc[-1]
        
        if len(vpt_series) >= 10:
            vpt_trend = "rising" if current_vpt > vpt_series.iloc[-10] else "falling"
            
            if vpt_trend == "rising":
                vpt_signal = "BUY"
                strength = SignalStrength.MODERATE
                description = "Volume-Price Trend rising - positive volume-weighted momentum"
            else:
                vpt_signal = "SELL"
                strength = SignalStrength.MODERATE
                description = "Volume-Price Trend falling - negative volume-weighted momentum"
            
            indicators.append(TechnicalIndicator(
                name="VPT",
                value=current_vpt,
                signal=vpt_signal,
                strength=strength,
                description=description,
                timestamp=datetime.now()
            ))
        
        # Volume Oscillator (difference between fast and slow volume EMAs)
        volume_ema_fast = data['volume'].ewm(span=5).mean()
        volume_ema_slow = data['volume'].ewm(span=10).mean()
        volume_oscillator = ((volume_ema_fast - volume_ema_slow) / volume_ema_slow * 100)
        
        current_vol_osc = volume_oscillator.iloc[-1]
        
        if current_vol_osc > 10:
            vol_osc_signal = "BUY"
            strength = SignalStrength.MODERATE
            description = f"Volume oscillator high ({current_vol_osc:.1f}%) - increasing volume momentum"
        elif current_vol_osc < -10:
            vol_osc_signal = "SELL"
            strength = SignalStrength.MODERATE
            description = f"Volume oscillator low ({current_vol_osc:.1f}%) - decreasing volume momentum"
        else:
            vol_osc_signal = "HOLD"
            strength = SignalStrength.WEAK
            description = f"Volume oscillator neutral ({current_vol_osc:.1f}%) - stable volume"
        
        indicators.append(TechnicalIndicator(
            name="VOLUME_OSCILLATOR",
            value=current_vol_osc,
            signal=vol_osc_signal,
            strength=strength,
            description=description,
            timestamp=datetime.now()
        ))
        
        return indicators
    
    async def _detect_patterns(self, data: pd.DataFrame) -> List[ChartPattern]:
        """Detect chart patterns."""
        patterns = []
        
        # Simple pattern detection - can be expanded with more sophisticated algorithms
        if len(data) >= 20:
            # Double top pattern detection (simplified)
            highs = data['high'].rolling(window=5).max()
            recent_highs = highs.tail(20)
            
            if len(recent_highs) > 10:
                max_high = recent_highs.max()
                high_positions = recent_highs[recent_highs > max_high * 0.98].index
                
                if len(high_positions) >= 2:
                    patterns.append(ChartPattern(
                        name="POTENTIAL_DOUBLE_TOP",
                        confidence=0.6,
                        target_price=None,
                        stop_loss=None,
                        timeframe="Recent",
                        description="Potential double top pattern detected",
                        detected_at=datetime.now()
                    ))
        
        return patterns
    
    async def _calculate_support_resistance(self, data: pd.DataFrame) -> SupportResistance:
        """Calculate support and resistance levels."""
        if len(data) < 20:
            current_price = data['close'].iloc[-1]
            return SupportResistance(
                support_levels=[current_price * 0.95],
                resistance_levels=[current_price * 1.05],
                current_level_type="BETWEEN",
                strength_score=0.1,
                nearest_support=current_price * 0.95,
                nearest_resistance=current_price * 1.05
            )
        
        # Simple pivot point calculation
        recent_data = data.tail(50)
        current_price = data['close'].iloc[-1]
        
        # Find local highs and lows
        highs = []
        lows = []
        
        for i in range(2, len(recent_data) - 2):
            # Local high
            if (recent_data['high'].iloc[i] > recent_data['high'].iloc[i-1] and
                recent_data['high'].iloc[i] > recent_data['high'].iloc[i-2] and
                recent_data['high'].iloc[i] > recent_data['high'].iloc[i+1] and
                recent_data['high'].iloc[i] > recent_data['high'].iloc[i+2]):
                highs.append(recent_data['high'].iloc[i])
            
            # Local low
            if (recent_data['low'].iloc[i] < recent_data['low'].iloc[i-1] and
                recent_data['low'].iloc[i] < recent_data['low'].iloc[i-2] and
                recent_data['low'].iloc[i] < recent_data['low'].iloc[i+1] and
                recent_data['low'].iloc[i] < recent_data['low'].iloc[i+2]):
                lows.append(recent_data['low'].iloc[i])
        
        # Remove outliers and get significant levels
        if highs:
            resistance_levels = sorted(set([h for h in highs if h > current_price * 0.98]))[:5]
        else:
            resistance_levels = [current_price * 1.02, current_price * 1.05]
        
        if lows:
            support_levels = sorted(set([l for l in lows if l < current_price * 1.02]), reverse=True)[:5]
        else:
            support_levels = [current_price * 0.98, current_price * 0.95]
        
        # Find nearest levels
        nearest_resistance = min([r for r in resistance_levels if r > current_price], 
                               default=current_price * 1.05)
        nearest_support = max([s for s in support_levels if s < current_price], 
                             default=current_price * 0.95)
        
        # Determine current level type
        if current_price >= nearest_resistance * 0.99:
            current_level_type = "RESISTANCE"
        elif current_price <= nearest_support * 1.01:
            current_level_type = "SUPPORT"
        else:
            current_level_type = "BETWEEN"
        
        return SupportResistance(
            support_levels=support_levels,
            resistance_levels=resistance_levels,
            current_level_type=current_level_type,
            strength_score=0.7,  # Can be improved with more sophisticated calculation
            nearest_support=nearest_support,
            nearest_resistance=nearest_resistance
        )
    
    async def _analyze_volume(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze volume patterns."""
        if 'volume' not in data.columns:
            return {"error": "Volume data not available"}
        
        current_volume = data['volume'].iloc[-1]
        avg_volume = data['volume'].tail(20).mean()
        volume_trend = "increasing" if data['volume'].tail(5).mean() > data['volume'].tail(10).mean() else "decreasing"
        
        return {
            "current_volume": current_volume,
            "average_volume_20d": avg_volume,
            "volume_ratio": current_volume / avg_volume if avg_volume > 0 else 1,
            "volume_trend": volume_trend,
            "volume_analysis": "High volume confirms price movement" if current_volume > avg_volume * 1.5 else "Normal volume activity"
        }
    
    def _analyze_trend(self, indicators: List[TechnicalIndicator], 
                      data: pd.DataFrame) -> Tuple[TrendDirection, float]:
        """Analyze overall trend direction and strength."""
        trend_scores = []
        
        # Analyze moving average trends
        sma_indicators = [ind for ind in indicators if 'SMA' in ind.name]
        for ind in sma_indicators:
            if ind.signal == "BUY":
                trend_scores.append(1)
            elif ind.signal == "SELL":
                trend_scores.append(-1)
            else:
                trend_scores.append(0)
        
        # Analyze momentum indicators
        momentum_indicators = [ind for ind in indicators if ind.name in ['RSI', 'MACD', 'STOCHASTIC']]
        for ind in momentum_indicators:
            weight = 0.8  # Momentum indicators get slightly less weight
            if ind.signal == "BUY":
                trend_scores.append(weight)
            elif ind.signal == "SELL":
                trend_scores.append(-weight)
            else:
                trend_scores.append(0)
        
        # Calculate average trend score
        if trend_scores:
            avg_trend_score = sum(trend_scores) / len(trend_scores)
            trend_strength = abs(avg_trend_score)
            
            if avg_trend_score > 0.6:
                trend_direction = TrendDirection.STRONG_BULLISH
            elif avg_trend_score > 0.2:
                trend_direction = TrendDirection.BULLISH
            elif avg_trend_score < -0.6:
                trend_direction = TrendDirection.STRONG_BEARISH
            elif avg_trend_score < -0.2:
                trend_direction = TrendDirection.BEARISH
            else:
                trend_direction = TrendDirection.SIDEWAYS
        else:
            trend_direction = TrendDirection.SIDEWAYS
            trend_strength = 0.0
        
        return trend_direction, trend_strength
    
    def _generate_overall_signal(self, indicators: List[TechnicalIndicator],
                               patterns: List[ChartPattern],
                               trend_direction: TrendDirection,
                               trend_strength: float) -> Tuple[str, float]:
        """Generate overall trading signal and confidence."""
        buy_signals = len([ind for ind in indicators if ind.signal == "BUY"])
        sell_signals = len([ind for ind in indicators if ind.signal == "SELL"])
        total_signals = len(indicators)
        
        # Weight signals by strength
        weighted_buy = sum([1 * ind.strength.value for ind in indicators if ind.signal == "BUY"])
        weighted_sell = sum([1 * ind.strength.value for ind in indicators if ind.signal == "SELL"])
        
        net_signal_strength = weighted_buy - weighted_sell
        signal_ratio = (buy_signals - sell_signals) / max(total_signals, 1)
        
        # Consider trend direction
        trend_weight = trend_strength * 2
        if trend_direction in [TrendDirection.BULLISH, TrendDirection.STRONG_BULLISH]:
            net_signal_strength += trend_weight
        elif trend_direction in [TrendDirection.BEARISH, TrendDirection.STRONG_BEARISH]:
            net_signal_strength -= trend_weight
        
        # Generate signal
        if net_signal_strength > 8:
            overall_signal = "STRONG_BUY"
            confidence = min(0.95, 0.6 + (net_signal_strength / 20))
        elif net_signal_strength > 3:
            overall_signal = "BUY"
            confidence = min(0.8, 0.5 + (net_signal_strength / 15))
        elif net_signal_strength < -8:
            overall_signal = "STRONG_SELL"
            confidence = min(0.95, 0.6 + (abs(net_signal_strength) / 20))
        elif net_signal_strength < -3:
            overall_signal = "SELL"
            confidence = min(0.8, 0.5 + (abs(net_signal_strength) / 15))
        else:
            overall_signal = "HOLD"
            confidence = 0.6
        
        return overall_signal, confidence
    
    def export_analysis(self, analysis: TechnicalAnalysis, 
                       filepath: str, format: str = "json"):
        """Export technical analysis to file."""
        if format.lower() == "json":
            data = {
                "symbol": analysis.symbol,
                "timeframe": analysis.timeframe,
                "current_price": analysis.current_price,
                "trend_direction": analysis.trend_direction.name,
                "trend_strength": analysis.trend_strength,
                "overall_signal": analysis.overall_signal,
                "confidence": analysis.confidence,
                "analysis_timestamp": analysis.analysis_timestamp.isoformat(),
                "indicators": [
                    {
                        "name": ind.name,
                        "value": ind.value,
                        "signal": ind.signal,
                        "strength": ind.strength.name,
                        "description": ind.description
                    }
                    for ind in analysis.indicators
                ],
                "patterns": [
                    {
                        "name": pattern.name,
                        "confidence": pattern.confidence,
                        "description": pattern.description
                    }
                    for pattern in analysis.patterns
                ],
                "support_resistance": {
                    "support_levels": analysis.support_resistance.support_levels,
                    "resistance_levels": analysis.support_resistance.resistance_levels,
                    "current_level_type": analysis.support_resistance.current_level_type,
                    "nearest_support": analysis.support_resistance.nearest_support,
                    "nearest_resistance": analysis.support_resistance.nearest_resistance
                },
                "volume_analysis": analysis.volume_analysis
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Exported technical analysis for {analysis.symbol} to {filepath}")


# Example usage and testing
async def test_chart_analyzer():
    """Test the chart analyzer with sample data."""
    import random
    
    analyzer = TechnicalChartAnalyzer()
    
    # Generate sample OHLCV data
    dates = pd.date_range(start='2024-01-01', end='2024-12-01', freq='D')
    base_price = 100
    
    data = []
    for i, date in enumerate(dates):
        # Simple random walk with trend
        change = random.uniform(-0.03, 0.03) + (i * 0.0001)  # Slight upward trend
        base_price *= (1 + change)
        
        high = base_price * random.uniform(1.001, 1.02)
        low = base_price * random.uniform(0.98, 0.999)
        volume = random.randint(1000000, 5000000)
        
        data.append({
            'date': date,
            'open': base_price,
            'high': high,
            'low': low,
            'close': base_price,
            'volume': volume
        })
    
    df = pd.DataFrame(data)
    df.set_index('date', inplace=True)
    
    print("🔍 Testing Chart Analyzer...")
    print("=" * 50)
    
    try:
        analysis = await analyzer.analyze_chart("TEST", df, "1D")
        
        print(f"Symbol: {analysis.symbol}")
        print(f"Current Price: ${analysis.current_price:.2f}")
        print(f"Trend: {analysis.trend_direction.name} (Strength: {analysis.trend_strength:.2f})")
        print(f"Overall Signal: {analysis.overall_signal} (Confidence: {analysis.confidence:.1%})")
        print()
        
        print("Technical Indicators:")
        for indicator in analysis.indicators[:5]:  # Show first 5 indicators
            print(f"  • {indicator.name}: {indicator.value:.3f} - {indicator.signal} ({indicator.strength.name})")
            print(f"    {indicator.description}")
        
        print()
        print("Support/Resistance:")
        print(f"  • Nearest Support: ${analysis.support_resistance.nearest_support:.2f}")
        print(f"  • Nearest Resistance: ${analysis.support_resistance.nearest_resistance:.2f}")
        print(f"  • Current Level: {analysis.support_resistance.current_level_type}")
        
    except Exception as e:
        print(f"Error during analysis: {e}")


if __name__ == "__main__":
    asyncio.run(test_chart_analyzer())