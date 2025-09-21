"""
Data Management Module for the Agent Investment Platform.

This module provides comprehensive data management capabilities for the backtesting framework,
including historical price data fetching, caching, validation, and preprocessing.

Key Features:
- Multiple data source integration (Yahoo Finance, Alpha Vantage, Quandl, etc.)
- Intelligent data caching and storage
- Data quality validation and cleaning
- Corporate actions adjustment
- Missing data handling and interpolation
- Real-time and historical data synchronization
"""

import asyncio
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import sqlite3
import aiohttp
import time
from pathlib import Path
import hashlib


class DataSource(Enum):
    """Supported data sources."""
    YAHOO_FINANCE = "yahoo_finance"
    ALPHA_VANTAGE = "alpha_vantage"
    IEX_CLOUD = "iex_cloud"
    QUANDL = "quandl"
    POLYGON = "polygon"
    MOCK = "mock"  # For testing


class DataQuality(Enum):
    """Data quality assessment levels."""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    INVALID = "invalid"


@dataclass
class DataSourceConfig:
    """Configuration for data sources."""
    source: DataSource
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    rate_limit: int = 5  # Requests per second
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0


@dataclass
class DataQualityReport:
    """Data quality assessment report."""
    symbol: str
    start_date: datetime
    end_date: datetime
    total_points: int
    missing_points: int
    invalid_points: int
    outliers: int
    gaps: List[Tuple[datetime, datetime]]
    quality_score: float
    quality_level: DataQuality
    issues: List[str]
    recommendations: List[str]


@dataclass
class MarketDataPoint:
    """Individual market data point."""
    symbol: str
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    adjusted_close: Optional[float] = None
    dividend: Optional[float] = None
    split_ratio: Optional[float] = None


class DataManager:
    """
    Comprehensive data management system for financial market data.

    This manager handles data fetching, caching, validation, and preprocessing
    to ensure reliable data for backtesting and analysis.
    """

    def __init__(self, cache_dir: str = "data_cache", database_path: str = "market_data.db"):
        """
        Initialize the data manager.

        Args:
            cache_dir: Directory for caching data files
            database_path: Path to SQLite database for data storage
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

        self.database_path = database_path
        self.logger = logging.getLogger(__name__)

        # Data source configurations
        self.data_sources: Dict[DataSource, DataSourceConfig] = {}

        # Initialize database
        self._initialize_database()

        # Rate limiting
        self._last_request_times: Dict[DataSource, float] = {}

        self.logger.info(f"Data manager initialized with cache dir: {cache_dir}")

    def add_data_source(self, config: DataSourceConfig):
        """Add a data source configuration."""
        self.data_sources[config.source] = config
        self.logger.info(f"Added data source: {config.source.value}")

    async def get_historical_data(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime,
        data_source: DataSource = DataSource.MOCK,
        force_refresh: bool = False,
        validate_quality: bool = True
    ) -> Dict[str, pd.DataFrame]:
        """
        Get historical market data for multiple symbols.

        Args:
            symbols: List of symbols to fetch
            start_date: Start date for data
            end_date: End date for data
            data_source: Preferred data source
            force_refresh: Force refresh of cached data
            validate_quality: Perform data quality validation

        Returns:
            Dictionary mapping symbols to their historical data
        """
        self.logger.info(f"Fetching historical data for {len(symbols)} symbols from {start_date} to {end_date}")

        results = {}

        for symbol in symbols:
            try:
                # Check cache first
                cached_data = None
                if not force_refresh:
                    cached_data = await self._get_cached_data(symbol, start_date, end_date)

                if cached_data is not None:
                    self.logger.debug(f"Using cached data for {symbol}")
                    data = cached_data
                else:
                    # Fetch from data source
                    data = await self._fetch_from_source(symbol, start_date, end_date, data_source)

                    if data is not None:
                        # Cache the data
                        await self._cache_data(symbol, data)
                    else:
                        self.logger.warning(f"No data retrieved for {symbol}")
                        continue

                # Validate data quality if requested
                if validate_quality and data is not None:
                    quality_report = self._assess_data_quality(symbol, data, start_date, end_date)

                    if quality_report.quality_level == DataQuality.INVALID:
                        self.logger.error(f"Invalid data quality for {symbol}: {quality_report.issues}")
                        continue
                    elif quality_report.quality_level == DataQuality.POOR:
                        self.logger.warning(f"Poor data quality for {symbol}: {quality_report.issues}")
                        # Apply data cleaning
                        data = self._clean_data(data, quality_report)

                if data is not None:
                    results[symbol] = data

            except Exception as e:
                self.logger.error(f"Failed to get data for {symbol}: {e}")
                continue

        self.logger.info(f"Successfully retrieved data for {len(results)} symbols")
        return results

    async def get_news_data(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime,
        max_articles_per_symbol: int = 100
    ) -> Dict[str, List[Dict]]:
        """
        Get news data for symbols (mock implementation for now).

        Args:
            symbols: List of symbols
            start_date: Start date for news
            end_date: End date for news
            max_articles_per_symbol: Maximum articles per symbol

        Returns:
            Dictionary mapping symbols to their news articles
        """
        # Mock news data for testing
        news_data = {}

        for symbol in symbols:
            articles = []
            current_date = start_date

            while current_date <= end_date and len(articles) < max_articles_per_symbol:
                # Generate mock news articles
                if current_date.weekday() < 5:  # Weekdays only
                    sentiment_score = np.random.uniform(-1, 1)

                    article = {
                        'date': current_date.isoformat(),
                        'title': f"Market analysis for {symbol}",
                        'content': f"Analysis content for {symbol} on {current_date.strftime('%Y-%m-%d')}",
                        'sentiment_score': sentiment_score,
                        'source': 'MockNews',
                        'url': f"https://mocknews.com/{symbol}/{current_date.strftime('%Y%m%d')}"
                    }
                    articles.append(article)

                current_date += timedelta(days=1)

            news_data[symbol] = articles

        return news_data

    async def _fetch_from_source(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        data_source: DataSource
    ) -> Optional[pd.DataFrame]:
        """Fetch data from specified source."""
        if data_source == DataSource.MOCK:
            return self._generate_mock_data(symbol, start_date, end_date)

        # For now, only implement mock data
        # In a real implementation, this would handle:
        # - Yahoo Finance API calls
        # - Alpha Vantage API calls
        # - IEX Cloud API calls
        # - etc.

        self.logger.warning(f"Data source {data_source.value} not implemented, using mock data")
        return self._generate_mock_data(symbol, start_date, end_date)

    def _generate_mock_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime
    ) -> pd.DataFrame:
        """Generate realistic mock market data for testing."""
        # Create date range (business days only)
        dates = pd.bdate_range(start=start_date, end=end_date)

        if len(dates) == 0:
            return pd.DataFrame()

        # Generate realistic price data using geometric Brownian motion
        np.random.seed(hash(symbol) % 2**32)  # Consistent data for same symbol

        # Base parameters
        initial_price = 50 + (hash(symbol) % 200)  # Price between 50-250
        drift = 0.08 / 252  # 8% annual drift
        volatility = 0.25 / np.sqrt(252)  # 25% annual volatility

        # Generate returns
        returns = np.random.normal(drift, volatility, len(dates))

        # Calculate prices
        prices = [initial_price]
        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))

        # Generate OHLC data
        data = []
        for i, (date, close_price) in enumerate(zip(dates, prices)):
            # Generate realistic OHLC from close price
            daily_range = abs(np.random.normal(0, 0.02))  # 2% average daily range

            high = close_price * (1 + daily_range * np.random.uniform(0.3, 1.0))
            low = close_price * (1 - daily_range * np.random.uniform(0.3, 1.0))

            # Ensure open is between high and low
            open_price = low + (high - low) * np.random.uniform(0.2, 0.8)

            # Generate volume (higher volume on larger price moves)
            base_volume = 1000000 + (hash(f"{symbol}{i}") % 5000000)
            volume_multiplier = 1 + abs(returns[i]) * 10
            volume = int(base_volume * volume_multiplier)

            data.append({
                'date': date,
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(close_price, 2),
                'volume': volume,
                'adjusted_close': round(close_price, 2)  # Simplified
            })

        return pd.DataFrame(data)

    async def _get_cached_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[pd.DataFrame]:
        """Get data from cache if available and up to date."""
        cache_key = self._generate_cache_key(symbol, start_date, end_date)
        cache_file = self.cache_dir / f"{cache_key}.parquet"

        if cache_file.exists():
            try:
                # Check if cache is still valid (not older than 1 day for this example)
                cache_age = time.time() - cache_file.stat().st_mtime
                if cache_age < 86400:  # 24 hours
                    data = pd.read_parquet(cache_file)
                    self.logger.debug(f"Loaded cached data for {symbol}: {len(data)} records")
                    return data
                else:
                    self.logger.debug(f"Cache expired for {symbol}")
            except Exception as e:
                self.logger.warning(f"Failed to load cached data for {symbol}: {e}")

        return None

    async def _cache_data(self, symbol: str, data: pd.DataFrame):
        """Cache data to disk."""
        if data.empty:
            return

        try:
            start_date = pd.to_datetime(data['date']).min()
            end_date = pd.to_datetime(data['date']).max()

            cache_key = self._generate_cache_key(symbol, start_date, end_date)
            cache_file = self.cache_dir / f"{cache_key}.parquet"

            data.to_parquet(cache_file, index=False)
            self.logger.debug(f"Cached data for {symbol}: {len(data)} records")

        except Exception as e:
            self.logger.warning(f"Failed to cache data for {symbol}: {e}")

    def _generate_cache_key(self, symbol: str, start_date: datetime, end_date: datetime) -> str:
        """Generate cache key for data."""
        key_string = f"{symbol}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"
        return hashlib.md5(key_string.encode()).hexdigest()

    def _assess_data_quality(
        self,
        symbol: str,
        data: pd.DataFrame,
        start_date: datetime,
        end_date: datetime
    ) -> DataQualityReport:
        """Assess data quality and identify issues."""
        issues = []
        recommendations = []

        # Convert date column to datetime if needed
        if 'date' in data.columns:
            data_dates = pd.to_datetime(data['date'])
        else:
            issues.append("No date column found")
            return self._create_invalid_quality_report(symbol, start_date, end_date, issues)

        # Check required columns
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            issues.append(f"Missing required columns: {missing_columns}")

        # Check for missing data points
        expected_days = pd.bdate_range(start=start_date, end=end_date)
        actual_days = data_dates
        missing_days = set(expected_days) - set(actual_days)
        missing_points = len(missing_days)

        if missing_points > 0:
            issues.append(f"Missing {missing_points} data points")
            if missing_points > len(expected_days) * 0.1:  # More than 10% missing
                recommendations.append("Consider using data interpolation or alternative data source")

        # Check for invalid prices (negative, zero, or extreme values)
        invalid_points = 0
        price_columns = ['open', 'high', 'low', 'close']

        for col in price_columns:
            if col in data.columns:
                invalid_mask = (data[col] <= 0) | (data[col] > 1000000)  # Extreme values
                invalid_count = invalid_mask.sum()
                invalid_points += invalid_count

                if invalid_count > 0:
                    issues.append(f"Invalid {col} prices: {invalid_count} points")

        # Check OHLC consistency
        if all(col in data.columns for col in price_columns):
            ohlc_issues = (
                (data['high'] < data['low']) |
                (data['high'] < data['open']) |
                (data['high'] < data['close']) |
                (data['low'] > data['open']) |
                (data['low'] > data['close'])
            ).sum()

            if ohlc_issues > 0:
                issues.append(f"OHLC consistency issues: {ohlc_issues} points")
                invalid_points += ohlc_issues

        # Check for outliers (using IQR method)
        outliers = 0
        if 'close' in data.columns:
            Q1 = data['close'].quantile(0.25)
            Q3 = data['close'].quantile(0.75)
            IQR = Q3 - Q1

            outlier_mask = (data['close'] < (Q1 - 3 * IQR)) | (data['close'] > (Q3 + 3 * IQR))
            outliers = outlier_mask.sum()

            if outliers > len(data) * 0.05:  # More than 5% outliers
                issues.append(f"High number of price outliers: {outliers}")
                recommendations.append("Review outlier data points for accuracy")

        # Check for data gaps (consecutive missing dates)
        gaps = []
        if len(missing_days) > 0:
            sorted_missing = sorted(missing_days)
            gap_start = None

            for i, date in enumerate(sorted_missing):
                if gap_start is None:
                    gap_start = date
                elif i == len(sorted_missing) - 1 or (sorted_missing[i + 1] - date).days > 1:
                    gaps.append((gap_start, date))
                    gap_start = None

        # Calculate quality score
        total_points = len(expected_days)
        quality_score = max(0, 1 - (missing_points + invalid_points) / total_points)

        # Determine quality level
        if quality_score >= 0.95:
            quality_level = DataQuality.EXCELLENT
        elif quality_score >= 0.85:
            quality_level = DataQuality.GOOD
        elif quality_score >= 0.70:
            quality_level = DataQuality.ACCEPTABLE
        elif quality_score >= 0.50:
            quality_level = DataQuality.POOR
        else:
            quality_level = DataQuality.INVALID

        # Add recommendations based on quality level
        if quality_level == DataQuality.POOR:
            recommendations.append("Consider data cleaning and validation")
        elif quality_level == DataQuality.INVALID:
            recommendations.append("Data quality too poor for reliable analysis")

        return DataQualityReport(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            total_points=total_points,
            missing_points=missing_points,
            invalid_points=invalid_points,
            outliers=outliers,
            gaps=gaps,
            quality_score=quality_score,
            quality_level=quality_level,
            issues=issues,
            recommendations=recommendations
        )

    def _create_invalid_quality_report(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        issues: List[str]
    ) -> DataQualityReport:
        """Create a quality report for invalid data."""
        return DataQualityReport(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            total_points=0,
            missing_points=0,
            invalid_points=0,
            outliers=0,
            gaps=[],
            quality_score=0.0,
            quality_level=DataQuality.INVALID,
            issues=issues,
            recommendations=["Fix data structure issues"]
        )

    def _clean_data(self, data: pd.DataFrame, quality_report: DataQualityReport) -> pd.DataFrame:
        """Clean data based on quality assessment."""
        cleaned_data = data.copy()

        # Remove invalid price points
        price_columns = ['open', 'high', 'low', 'close']
        for col in price_columns:
            if col in cleaned_data.columns:
                # Remove negative or zero prices
                cleaned_data = cleaned_data[cleaned_data[col] > 0]

                # Remove extreme outliers (beyond 5 standard deviations)
                mean_price = cleaned_data[col].mean()
                std_price = cleaned_data[col].std()
                upper_bound = mean_price + 5 * std_price
                lower_bound = max(0, mean_price - 5 * std_price)

                cleaned_data = cleaned_data[
                    (cleaned_data[col] >= lower_bound) &
                    (cleaned_data[col] <= upper_bound)
                ]

        # Interpolate missing values for small gaps
        if 'close' in cleaned_data.columns:
            cleaned_data['close'] = cleaned_data['close'].interpolate(method='linear', limit=3)

        # Fix OHLC consistency issues
        if all(col in cleaned_data.columns for col in price_columns):
            # Ensure high is the maximum and low is the minimum
            cleaned_data['high'] = cleaned_data[['open', 'high', 'low', 'close']].max(axis=1)
            cleaned_data['low'] = cleaned_data[['open', 'high', 'low', 'close']].min(axis=1)

        self.logger.info(f"Data cleaning completed. Original: {len(data)}, Cleaned: {len(cleaned_data)}")

        return cleaned_data

    def _initialize_database(self):
        """Initialize SQLite database for data storage."""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()

            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_data (
                    symbol TEXT,
                    date TEXT,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume INTEGER,
                    adjusted_close REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (symbol, date)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS data_quality (
                    symbol TEXT,
                    date_range TEXT,
                    quality_score REAL,
                    quality_level TEXT,
                    issues TEXT,
                    assessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (symbol, date_range)
                )
            ''')

            conn.commit()
            conn.close()

        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")

    def get_data_summary(self, symbols: List[str] = None) -> Dict[str, Any]:
        """Get summary of available data."""
        try:
            conn = sqlite3.connect(self.database_path)

            if symbols:
                symbol_list = "', '".join(symbols)
                query = f"""
                    SELECT symbol,
                           COUNT(*) as record_count,
                           MIN(date) as start_date,
                           MAX(date) as end_date
                    FROM market_data
                    WHERE symbol IN ('{symbol_list}')
                    GROUP BY symbol
                """
            else:
                query = """
                    SELECT symbol,
                           COUNT(*) as record_count,
                           MIN(date) as start_date,
                           MAX(date) as end_date
                    FROM market_data
                    GROUP BY symbol
                """

            df = pd.read_sql_query(query, conn)
            conn.close()

            return {
                'total_symbols': len(df),
                'symbols': df.to_dict('records'),
                'cache_directory': str(self.cache_dir),
                'database_path': self.database_path
            }

        except Exception as e:
            self.logger.error(f"Failed to get data summary: {e}")
            return {'error': str(e)}

    async def preload_data(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime,
        data_source: DataSource = DataSource.MOCK
    ):
        """Preload data for multiple symbols to cache."""
        self.logger.info(f"Preloading data for {len(symbols)} symbols")

        tasks = []
        for symbol in symbols:
            task = self.get_historical_data(
                [symbol], start_date, end_date, data_source, force_refresh=False
            )
            tasks.append(task)

        # Execute in batches to avoid overwhelming the system
        batch_size = 10
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            await asyncio.gather(*batch)

            # Small delay between batches
            if i + batch_size < len(tasks):
                await asyncio.sleep(0.5)

        self.logger.info("Data preloading completed")


# Utility functions
async def create_sample_data_manager(cache_dir: str = "test_cache") -> DataManager:
    """Create a sample data manager with mock data source."""
    manager = DataManager(cache_dir=cache_dir)

    # Add mock data source
    mock_config = DataSourceConfig(
        source=DataSource.MOCK,
        rate_limit=10,
        timeout=5
    )
    manager.add_data_source(mock_config)

    return manager


async def generate_backtest_dataset(
    symbols: List[str],
    start_date: str = "2023-01-01",
    end_date: str = "2024-01-01",
    include_news: bool = True
) -> Tuple[Dict[str, pd.DataFrame], Dict[str, List[Dict]]]:
    """
    Generate a complete dataset for backtesting.

    Args:
        symbols: List of symbols to include
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        include_news: Whether to include news data

    Returns:
        Tuple of (price_data, news_data)
    """
    manager = await create_sample_data_manager()

    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")

    # Get price data
    price_data = await manager.get_historical_data(
        symbols=symbols,
        start_date=start_dt,
        end_date=end_dt,
        data_source=DataSource.MOCK
    )

    # Get news data if requested
    news_data = {}
    if include_news:
        news_data = await manager.get_news_data(
            symbols=symbols,
            start_date=start_dt,
            end_date=end_dt
        )

    return price_data, news_data


if __name__ == "__main__":
    # Example usage
    async def example_usage():
        manager = await create_sample_data_manager()

        symbols = ['AAPL', 'GOOGL', 'MSFT']
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2024, 1, 1)

        # Get historical data
        data = await manager.get_historical_data(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date
        )

        print(f"Retrieved data for {len(data)} symbols")
        for symbol, df in data.items():
            print(f"{symbol}: {len(df)} records from {df['date'].min()} to {df['date'].max()}")

    # Run example
    asyncio.run(example_usage())
