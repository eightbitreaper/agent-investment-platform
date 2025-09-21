"""
Analysis Engine MCP Server for the Agent Investment Platform.

This server provides core financial analysis and strategy engine capabilities
including technical analysis, fundamental analysis, risk assessment, and
portfolio optimization.
"""

import asyncio
import json
import os
import sqlite3
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import numpy as np
import pandas as pd
from pathlib import Path

from .base import MCPServerBase, MCPTool, MCPError, MCPValidationError, create_tool_schema


@dataclass
class TechnicalIndicator:
    """Represents a technical indicator result."""
    name: str
    value: float
    signal: str  # "buy", "sell", "hold"
    confidence: float
    timestamp: datetime

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AnalysisResult:
    """Represents a complete analysis result."""
    symbol: str
    analysis_type: str
    score: float  # 0-100 scale
    recommendation: str  # "strong_buy", "buy", "hold", "sell", "strong_sell"
    confidence: float  # 0-1 scale
    factors: List[Dict[str, Any]]
    timestamp: datetime

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result["timestamp"] = result["timestamp"].isoformat()
        return result


@dataclass
class RiskMetrics:
    """Represents risk assessment metrics."""
    symbol: str
    volatility: float
    beta: float
    var_95: float  # Value at Risk 95%
    max_drawdown: float
    sharpe_ratio: float
    sortino_ratio: float
    risk_score: float  # 0-100 scale

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class TechnicalAnalyzer:
    """Technical analysis calculations."""

    @staticmethod
    def sma(prices: List[float], period: int) -> Optional[float]:
        """Simple Moving Average."""
        if len(prices) < period:
            return None
        return sum(prices[-period:]) / period

    @staticmethod
    def ema(prices: List[float], period: int) -> Optional[float]:
        """Exponential Moving Average."""
        if len(prices) < period:
            return None

        multiplier = 2 / (period + 1)
        ema = prices[0]

        for price in prices[1:]:
            ema = (price - ema) * multiplier + ema

        return ema

    @staticmethod
    def rsi(prices: List[float], period: int = 14) -> Optional[float]:
        """Relative Strength Index."""
        if len(prices) < period + 1:
            return None

        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [delta if delta > 0 else 0 for delta in deltas]
        losses = [-delta if delta < 0 else 0 for delta in deltas]

        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period

        if avg_loss == 0:
            return 100

        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Optional[Dict[str, float]]:
        """MACD (Moving Average Convergence Divergence)."""
        if len(prices) < slow:
            return None

        ema_fast = TechnicalAnalyzer.ema(prices, fast)
        ema_slow = TechnicalAnalyzer.ema(prices, slow)

        if ema_fast is None or ema_slow is None:
            return None

        macd_line = ema_fast - ema_slow

        # For signal line, we'd need historical MACD values
        # Simplified calculation for demonstration
        signal_line = macd_line * 0.9  # Simplified
        histogram = macd_line - signal_line

        return {
            "macd": macd_line,
            "signal": signal_line,
            "histogram": histogram
        }

    @staticmethod
    def bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2) -> Optional[Dict[str, float]]:
        """Bollinger Bands."""
        if len(prices) < period:
            return None

        recent_prices = prices[-period:]
        sma = sum(recent_prices) / period
        variance = sum([(price - sma) ** 2 for price in recent_prices]) / period
        std = variance ** 0.5

        return {
            "upper": sma + (std_dev * std),
            "middle": sma,
            "lower": sma - (std_dev * std)
        }


class FundamentalAnalyzer:
    """Fundamental analysis calculations."""

    @staticmethod
    def intrinsic_value_dcf(cash_flows: List[float], discount_rate: float, terminal_growth: float = 0.02) -> float:
        """Discounted Cash Flow intrinsic value calculation."""
        if not cash_flows:
            return 0

        present_value = 0
        for i, cf in enumerate(cash_flows):
            present_value += cf / ((1 + discount_rate) ** (i + 1))

        # Terminal value
        terminal_cf = cash_flows[-1] * (1 + terminal_growth)
        terminal_value = terminal_cf / (discount_rate - terminal_growth)
        terminal_pv = terminal_value / ((1 + discount_rate) ** len(cash_flows))

        return present_value + terminal_pv

    @staticmethod
    def pe_analysis(current_pe: float, industry_avg_pe: float, market_pe: float) -> Dict[str, Any]:
        """P/E ratio analysis."""
        analysis = {
            "current_pe": current_pe,
            "vs_industry": current_pe / industry_avg_pe if industry_avg_pe > 0 else None,
            "vs_market": current_pe / market_pe if market_pe > 0 else None,
            "valuation": "fair"
        }

        if current_pe < industry_avg_pe * 0.8:
            analysis["valuation"] = "undervalued"
        elif current_pe > industry_avg_pe * 1.2:
            analysis["valuation"] = "overvalued"

        return analysis

    @staticmethod
    def financial_strength_score(debt_to_equity: float, current_ratio: float,
                               roe: float, profit_margin: float) -> float:
        """Calculate financial strength score (0-100)."""
        score = 50  # Base score

        # Debt to equity (lower is better)
        if debt_to_equity < 0.3:
            score += 15
        elif debt_to_equity < 0.6:
            score += 10
        elif debt_to_equity > 1.0:
            score -= 15

        # Current ratio (around 1.5-3 is good)
        if 1.5 <= current_ratio <= 3.0:
            score += 15
        elif current_ratio > 3.0:
            score += 5  # Too much cash might be inefficient
        elif current_ratio < 1.0:
            score -= 20

        # ROE (higher is better)
        if roe > 0.15:
            score += 15
        elif roe > 0.10:
            score += 10
        elif roe < 0.05:
            score -= 10

        # Profit margin (higher is better)
        if profit_margin > 0.20:
            score += 15
        elif profit_margin > 0.10:
            score += 10
        elif profit_margin < 0.05:
            score -= 10

        return max(0, min(100, score))


class RiskAnalyzer:
    """Risk assessment calculations."""

    @staticmethod
    def calculate_volatility(returns: List[float]) -> float:
        """Calculate annualized volatility."""
        if len(returns) < 2:
            return 0

        mean_return = sum(returns) / len(returns)
        variance = sum([(r - mean_return) ** 2 for r in returns]) / (len(returns) - 1)
        daily_vol = variance ** 0.5
        return daily_vol * (252 ** 0.5)  # Annualize

    @staticmethod
    def calculate_var(returns: List[float], confidence: float = 0.95) -> float:
        """Calculate Value at Risk."""
        if not returns:
            return 0

        sorted_returns = sorted(returns)
        index = int((1 - confidence) * len(sorted_returns))
        return abs(sorted_returns[index])

    @staticmethod
    def calculate_beta(stock_returns: List[float], market_returns: List[float]) -> float:
        """Calculate beta coefficient."""
        if len(stock_returns) != len(market_returns) or len(stock_returns) < 2:
            return 1.0

        stock_mean = sum(stock_returns) / len(stock_returns)
        market_mean = sum(market_returns) / len(market_returns)

        covariance = sum([(stock_returns[i] - stock_mean) * (market_returns[i] - market_mean)
                         for i in range(len(stock_returns))]) / (len(stock_returns) - 1)

        market_variance = sum([(r - market_mean) ** 2 for r in market_returns]) / (len(market_returns) - 1)

        return covariance / market_variance if market_variance != 0 else 1.0

    @staticmethod
    def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio."""
        if not returns:
            return 0

        mean_return = sum(returns) / len(returns) * 252  # Annualize
        volatility = RiskAnalyzer.calculate_volatility(returns)

        return (mean_return - risk_free_rate) / volatility if volatility != 0 else 0


class AnalysisEngineServer(MCPServerBase):
    """
    MCP Server for financial analysis operations.

    Provides tools for:
    - Technical analysis with various indicators
    - Fundamental analysis and valuation
    - Risk assessment and metrics
    - Portfolio optimization strategies
    """

    def __init__(self):
        super().__init__(
            name="analysis-engine-server",
            version="1.0.0",
            description="Core financial analysis and strategy engine"
        )

        # Initialize database
        self.db_path = Path("data/analysis.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

        # Initialize analyzers
        self.technical_analyzer = TechnicalAnalyzer()
        self.fundamental_analyzer = FundamentalAnalyzer()
        self.risk_analyzer = RiskAnalyzer()

    def _init_database(self):
        """Initialize SQLite database for analysis storage."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS analyses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        analysis_type TEXT NOT NULL,
                        score REAL NOT NULL,
                        recommendation TEXT NOT NULL,
                        confidence REAL NOT NULL,
                        factors TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS risk_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        volatility REAL,
                        beta REAL,
                        var_95 REAL,
                        max_drawdown REAL,
                        sharpe_ratio REAL,
                        sortino_ratio REAL,
                        risk_score REAL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                conn.commit()

        except Exception as e:
            self.logger.error(f"Database initialization error: {e}")

    def _register_capabilities(self):
        """Register analysis engine tools."""

        # Technical analysis tool
        technical_tool = MCPTool(
            name="technical_analysis",
            description="Perform technical analysis on stock price data",
            inputSchema=create_tool_schema(
                name="technical_analysis",
                description="Technical analysis",
                properties={
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol"
                    },
                    "prices": {
                        "type": "array",
                        "description": "Array of historical prices",
                        "items": {"type": "number"},
                        "minItems": 10
                    },
                    "indicators": {
                        "type": "array",
                        "description": "Technical indicators to calculate",
                        "items": {
                            "type": "string",
                            "enum": ["sma", "ema", "rsi", "macd", "bollinger"]
                        },
                        "default": ["sma", "rsi"]
                    }
                },
                required=["symbol", "prices"]
            )
        )
        self.register_tool(technical_tool, self._handle_technical_analysis)

        # Fundamental analysis tool
        fundamental_tool = MCPTool(
            name="fundamental_analysis",
            description="Perform fundamental analysis on company data",
            inputSchema=create_tool_schema(
                name="fundamental_analysis",
                description="Fundamental analysis",
                properties={
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol"
                    },
                    "financials": {
                        "type": "object",
                        "description": "Company financial data",
                        "properties": {
                            "pe_ratio": {"type": "number"},
                            "debt_to_equity": {"type": "number"},
                            "current_ratio": {"type": "number"},
                            "roe": {"type": "number"},
                            "profit_margin": {"type": "number"},
                            "revenue_growth": {"type": "number"}
                        }
                    },
                    "industry_averages": {
                        "type": "object",
                        "description": "Industry average metrics",
                        "properties": {
                            "pe_ratio": {"type": "number"},
                            "debt_to_equity": {"type": "number"},
                            "roe": {"type": "number"}
                        }
                    }
                },
                required=["symbol", "financials"]
            )
        )
        self.register_tool(fundamental_tool, self._handle_fundamental_analysis)

        # Risk assessment tool
        risk_tool = MCPTool(
            name="risk_assessment",
            description="Perform risk assessment and calculate risk metrics",
            inputSchema=create_tool_schema(
                name="risk_assessment",
                description="Risk assessment",
                properties={
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol"
                    },
                    "returns": {
                        "type": "array",
                        "description": "Array of historical returns",
                        "items": {"type": "number"},
                        "minItems": 30
                    },
                    "market_returns": {
                        "type": "array",
                        "description": "Array of market returns for beta calculation",
                        "items": {"type": "number"}
                    },
                    "risk_free_rate": {
                        "type": "number",
                        "description": "Risk-free rate for Sharpe ratio",
                        "default": 0.02
                    }
                },
                required=["symbol", "returns"]
            )
        )
        self.register_tool(risk_tool, self._handle_risk_assessment)

        # Portfolio optimization tool
        portfolio_tool = MCPTool(
            name="portfolio_optimization",
            description="Optimize portfolio allocation based on risk and return",
            inputSchema=create_tool_schema(
                name="portfolio_optimization",
                description="Portfolio optimization",
                properties={
                    "symbols": {
                        "type": "array",
                        "description": "Array of stock symbols",
                        "items": {"type": "string"},
                        "minItems": 2,
                        "maxItems": 20
                    },
                    "returns_data": {
                        "type": "object",
                        "description": "Historical returns for each symbol",
                        "additionalProperties": {
                            "type": "array",
                            "items": {"type": "number"}
                        }
                    },
                    "optimization_method": {
                        "type": "string",
                        "description": "Optimization method",
                        "enum": ["max_sharpe", "min_volatility", "equal_weight"],
                        "default": "max_sharpe"
                    },
                    "risk_free_rate": {
                        "type": "number",
                        "description": "Risk-free rate",
                        "default": 0.02
                    }
                },
                required=["symbols", "returns_data"]
            )
        )
        self.register_tool(portfolio_tool, self._handle_portfolio_optimization)

    async def _handle_technical_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle technical analysis request."""
        symbol = params.get("symbol", "").upper()
        prices = params.get("prices", [])
        indicators = params.get("indicators", ["sma", "rsi"])

        if not symbol or not prices:
            raise MCPValidationError("Symbol and prices are required")

        if len(prices) < 10:
            raise MCPValidationError("At least 10 price points required")

        results = {}
        signals = []

        # Calculate requested indicators
        for indicator in indicators:
            if indicator == "sma":
                sma_20 = self.technical_analyzer.sma(prices, 20)
                if sma_20:
                    results["sma_20"] = sma_20
                    current_price = prices[-1]
                    signal = "buy" if current_price > sma_20 else "sell"
                    signals.append({
                        "indicator": "SMA_20",
                        "signal": signal,
                        "strength": abs(current_price - sma_20) / sma_20
                    })

            elif indicator == "ema":
                ema_12 = self.technical_analyzer.ema(prices, 12)
                if ema_12:
                    results["ema_12"] = ema_12
                    current_price = prices[-1]
                    signal = "buy" if current_price > ema_12 else "sell"
                    signals.append({
                        "indicator": "EMA_12",
                        "signal": signal,
                        "strength": abs(current_price - ema_12) / ema_12
                    })

            elif indicator == "rsi":
                rsi = self.technical_analyzer.rsi(prices)
                if rsi:
                    results["rsi"] = rsi
                    if rsi > 70:
                        signal = "sell"
                        strength = (rsi - 70) / 30
                    elif rsi < 30:
                        signal = "buy"
                        strength = (30 - rsi) / 30
                    else:
                        signal = "hold"
                        strength = 0.5

                    signals.append({
                        "indicator": "RSI",
                        "signal": signal,
                        "strength": strength
                    })

            elif indicator == "macd":
                macd = self.technical_analyzer.macd(prices)
                if macd:
                    results["macd"] = macd
                    signal = "buy" if macd["histogram"] > 0 else "sell"
                    signals.append({
                        "indicator": "MACD",
                        "signal": signal,
                        "strength": abs(macd["histogram"]) / prices[-1]
                    })

            elif indicator == "bollinger":
                bands = self.technical_analyzer.bollinger_bands(prices)
                if bands:
                    results["bollinger_bands"] = bands
                    current_price = prices[-1]
                    if current_price > bands["upper"]:
                        signal = "sell"
                        strength = (current_price - bands["upper"]) / bands["middle"]
                    elif current_price < bands["lower"]:
                        signal = "buy"
                        strength = (bands["lower"] - current_price) / bands["middle"]
                    else:
                        signal = "hold"
                        strength = 0.5

                    signals.append({
                        "indicator": "Bollinger",
                        "signal": signal,
                        "strength": strength
                    })

        # Calculate overall recommendation
        buy_signals = sum(1 for s in signals if s["signal"] == "buy")
        sell_signals = sum(1 for s in signals if s["signal"] == "sell")
        avg_strength = sum(s["strength"] for s in signals) / len(signals) if signals else 0

        if buy_signals > sell_signals:
            recommendation = "buy" if buy_signals - sell_signals > 1 else "weak_buy"
        elif sell_signals > buy_signals:
            recommendation = "sell" if sell_signals - buy_signals > 1 else "weak_sell"
        else:
            recommendation = "hold"

        # Store analysis
        analysis = AnalysisResult(
            symbol=symbol,
            analysis_type="technical",
            score=avg_strength * 100,
            recommendation=recommendation,
            confidence=min(1.0, avg_strength),
            factors=[{"type": "technical_indicators", "data": results}],
            timestamp=datetime.now()
        )

        await self._store_analysis(analysis)

        return {
            "success": True,
            "data": {
                "symbol": symbol,
                "indicators": results,
                "signals": signals,
                "recommendation": recommendation,
                "confidence": min(1.0, avg_strength),
                "timestamp": datetime.now().isoformat()
            }
        }

    async def _handle_fundamental_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle fundamental analysis request."""
        symbol = params.get("symbol", "").upper()
        financials = params.get("financials", {})
        industry_avg = params.get("industry_averages", {})

        if not symbol or not financials:
            raise MCPValidationError("Symbol and financials are required")

        results = {}
        factors = []

        # Financial strength analysis
        debt_to_equity = financials.get("debt_to_equity", 0.5)
        current_ratio = financials.get("current_ratio", 1.5)
        roe = financials.get("roe", 0.10)
        profit_margin = financials.get("profit_margin", 0.10)

        strength_score = self.fundamental_analyzer.financial_strength_score(
            debt_to_equity, current_ratio, roe, profit_margin
        )

        results["financial_strength_score"] = strength_score
        factors.append({
            "type": "financial_strength",
            "score": strength_score,
            "components": {
                "debt_to_equity": debt_to_equity,
                "current_ratio": current_ratio,
                "roe": roe,
                "profit_margin": profit_margin
            }
        })

        # P/E analysis if available
        if "pe_ratio" in financials:
            pe_analysis = self.fundamental_analyzer.pe_analysis(
                financials["pe_ratio"],
                industry_avg.get("pe_ratio", financials["pe_ratio"]),
                20  # Market average assumption
            )
            results["pe_analysis"] = pe_analysis
            factors.append({
                "type": "valuation",
                "data": pe_analysis
            })

        # Overall recommendation
        if strength_score >= 80:
            recommendation = "strong_buy"
        elif strength_score >= 65:
            recommendation = "buy"
        elif strength_score >= 50:
            recommendation = "hold"
        elif strength_score >= 35:
            recommendation = "sell"
        else:
            recommendation = "strong_sell"

        confidence = strength_score / 100.0

        # Store analysis
        analysis = AnalysisResult(
            symbol=symbol,
            analysis_type="fundamental",
            score=strength_score,
            recommendation=recommendation,
            confidence=confidence,
            factors=factors,
            timestamp=datetime.now()
        )

        await self._store_analysis(analysis)

        return {
            "success": True,
            "data": {
                "symbol": symbol,
                "results": results,
                "recommendation": recommendation,
                "confidence": confidence,
                "factors": factors,
                "timestamp": datetime.now().isoformat()
            }
        }

    async def _handle_risk_assessment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle risk assessment request."""
        symbol = params.get("symbol", "").upper()
        returns = params.get("returns", [])
        market_returns = params.get("market_returns", [])
        risk_free_rate = params.get("risk_free_rate", 0.02)

        if not symbol or not returns:
            raise MCPValidationError("Symbol and returns are required")

        if len(returns) < 30:
            raise MCPValidationError("At least 30 return observations required")

        # Calculate risk metrics
        volatility = self.risk_analyzer.calculate_volatility(returns)
        var_95 = self.risk_analyzer.calculate_var(returns, 0.95)
        sharpe_ratio = self.risk_analyzer.calculate_sharpe_ratio(returns, risk_free_rate)

        beta = 1.0
        if market_returns and len(market_returns) == len(returns):
            beta = self.risk_analyzer.calculate_beta(returns, market_returns)

        # Calculate max drawdown
        cumulative_returns = [1]
        for ret in returns:
            cumulative_returns.append(cumulative_returns[-1] * (1 + ret))

        peak = cumulative_returns[0]
        max_drawdown = 0
        for value in cumulative_returns:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            max_drawdown = max(max_drawdown, drawdown)

        # Calculate overall risk score (0-100, lower is better)
        risk_score = 50  # Base score

        if volatility > 0.3:  # High volatility
            risk_score += 20
        elif volatility < 0.15:  # Low volatility
            risk_score -= 10

        if beta > 1.5:  # High beta
            risk_score += 15
        elif beta < 0.5:  # Low beta
            risk_score -= 10

        if sharpe_ratio > 1.0:  # Good risk-adjusted returns
            risk_score -= 15
        elif sharpe_ratio < 0:  # Poor risk-adjusted returns
            risk_score += 20

        risk_score = max(0, min(100, risk_score))

        # Create risk metrics object
        risk_metrics = RiskMetrics(
            symbol=symbol,
            volatility=volatility,
            beta=beta,
            var_95=var_95,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sharpe_ratio,  # Simplified
            risk_score=risk_score
        )

        # Store risk metrics
        await self._store_risk_metrics(risk_metrics)

        return {
            "success": True,
            "data": risk_metrics.to_dict()
        }

    async def _handle_portfolio_optimization(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle portfolio optimization request."""
        symbols = params.get("symbols", [])
        returns_data = params.get("returns_data", {})
        method = params.get("optimization_method", "max_sharpe")
        risk_free_rate = params.get("risk_free_rate", 0.02)

        if not symbols or not returns_data:
            raise MCPValidationError("Symbols and returns_data are required")

        if len(symbols) < 2:
            raise MCPValidationError("At least 2 symbols required for optimization")

        # Validate that all symbols have returns data
        for symbol in symbols:
            if symbol not in returns_data:
                raise MCPValidationError(f"No returns data provided for {symbol}")

        # Simple portfolio optimization (equal weight or basic calculations)
        if method == "equal_weight":
            weights = {symbol: 1.0 / len(symbols) for symbol in symbols}
        else:
            # Simplified optimization - in practice would use modern portfolio theory
            # Calculate individual Sharpe ratios
            sharpe_ratios = {}
            for symbol in symbols:
                returns = returns_data[symbol]
                sharpe = self.risk_analyzer.calculate_sharpe_ratio(returns, risk_free_rate)
                sharpe_ratios[symbol] = max(0, sharpe)  # Ensure non-negative

            total_sharpe = sum(sharpe_ratios.values())
            if total_sharpe > 0:
                weights = {symbol: sharpe / total_sharpe for symbol, sharpe in sharpe_ratios.items()}
            else:
                weights = {symbol: 1.0 / len(symbols) for symbol in symbols}

        # Calculate portfolio metrics
        portfolio_return = 0
        portfolio_variance = 0

        for symbol, weight in weights.items():
            returns = returns_data[symbol]
            mean_return = sum(returns) / len(returns) * 252  # Annualize
            portfolio_return += weight * mean_return

            volatility = self.risk_analyzer.calculate_volatility(returns)
            portfolio_variance += (weight ** 2) * (volatility ** 2)

        # Simplified - doesn't account for correlations
        portfolio_volatility = portfolio_variance ** 0.5
        portfolio_sharpe = (portfolio_return - risk_free_rate) / portfolio_volatility if portfolio_volatility > 0 else 0

        result = {
            "symbols": symbols,
            "weights": weights,
            "expected_return": portfolio_return,
            "volatility": portfolio_volatility,
            "sharpe_ratio": portfolio_sharpe,
            "optimization_method": method,
            "timestamp": datetime.now().isoformat()
        }

        return {
            "success": True,
            "data": result
        }

    async def _store_analysis(self, analysis: AnalysisResult):
        """Store analysis result in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO analyses (symbol, analysis_type, score, recommendation, confidence, factors)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    analysis.symbol,
                    analysis.analysis_type,
                    analysis.score,
                    analysis.recommendation,
                    analysis.confidence,
                    json.dumps(analysis.factors)
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Error storing analysis: {e}")

    async def _store_risk_metrics(self, risk_metrics: RiskMetrics):
        """Store risk metrics in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO risk_metrics (symbol, volatility, beta, var_95, max_drawdown,
                                            sharpe_ratio, sortino_ratio, risk_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    risk_metrics.symbol,
                    risk_metrics.volatility,
                    risk_metrics.beta,
                    risk_metrics.var_95,
                    risk_metrics.max_drawdown,
                    risk_metrics.sharpe_ratio,
                    risk_metrics.sortino_ratio,
                    risk_metrics.risk_score
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Error storing risk metrics: {e}")

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": self.version,
            "database": "connected"
        }

        # Test database connection
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("SELECT 1").fetchone()
        except Exception as e:
            status["database"] = f"error: {str(e)}"
            status["status"] = "degraded"

        return status


async def main():
    """Main entry point for the Analysis Engine Server."""
    server = AnalysisEngineServer()
    await server.run_stdio()


if __name__ == "__main__":
    asyncio.run(main())
