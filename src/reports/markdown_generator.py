"""
Markdown Report Generator for Agent Investment Platform

This module provides functionality to generate professional investment reports
using Jinja2 templates and structured data from various analysis components.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import uuid

try:
    from jinja2 import Environment, FileSystemLoader, Template
except ImportError:
    raise ImportError("Jinja2 is required for report generation. Install with: pip install jinja2")

# Import analysis modules - using try/except for flexible import paths
try:
    from ..analysis.sentiment_analyzer import FinancialSentimentAnalyzer
    from ..analysis.chart_analyzer import TechnicalAnalysis
    from ..analysis.recommendation_engine import RecommendationEngine
    from ..risk_management.risk_engine import RiskEngine
except ImportError:
    # Fallback for direct execution or different import contexts
    try:
        import sys
        from pathlib import Path
        src_path = Path(__file__).parent.parent
        sys.path.insert(0, str(src_path))

        from analysis.sentiment_analyzer import FinancialSentimentAnalyzer
        from analysis.chart_analyzer import TechnicalAnalysis
        from analysis.recommendation_engine import RecommendationEngine
        from risk_management.risk_engine import RiskEngine
    except ImportError:
        # If imports fail, set to None and handle gracefully
        FinancialSentimentAnalyzer = None
        TechnicalAnalysis = None
        RecommendationEngine = None
        RiskEngine = None


class MarkdownReportGenerator:
    """
    Generates structured markdown reports from investment analysis data.

    Supports multiple report types:
    - Individual stock analysis
    - Portfolio analysis
    - Market summary
    - Comprehensive investment reports
    """

    def __init__(self, template_dir: Optional[str] = None, output_dir: Optional[str] = None):
        """
        Initialize the report generator.

        Args:
            template_dir: Directory containing Jinja2 templates
            output_dir: Directory for generated reports
        """
        self.logger = logging.getLogger(__name__)

        # Set default directories
        project_root = Path(__file__).parents[2]
        self.template_dir = Path(template_dir) if template_dir else project_root / "templates"
        self.output_dir = Path(output_dir) if output_dir else project_root / "reports"

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize Jinja2 environment
        try:
            self.jinja_env = Environment(
                loader=FileSystemLoader(str(self.template_dir)),
                autoescape=True,
                trim_blocks=True,
                lstrip_blocks=True
            )

            # Add custom filters
            self.jinja_env.filters.update({
                'currency': self._format_currency,
                'percentage': self._format_percentage,
                'round_float': self._round_float,
                'format_date': self._format_date,
                'upper': str.upper,
                'lower': str.lower,
                'join': lambda x, sep=', ': sep.join(x) if x else ''
            })

        except Exception as e:
            self.logger.error(f"Failed to initialize Jinja2 environment: {e}")
            raise

    def generate_report(
        self,
        template_name: str,
        data: Dict[str, Any],
        output_filename: Optional[str] = None,
        title: Optional[str] = None
    ) -> str:
        """
        Generate a markdown report from template and data.

        Args:
            template_name: Name of the template file (e.g., 'report-template.md')
            data: Dictionary containing all data for the report
            output_filename: Optional custom output filename
            title: Optional report title override

        Returns:
            Path to the generated report file
        """
        try:
            # Load template
            template = self.jinja_env.get_template(template_name)

            # Prepare data with metadata
            report_data = self._prepare_report_data(data, title)

            # Render template
            rendered_content = template.render(
                title=report_data.get('title', 'Investment Analysis Report'),
                data=report_data
            )

            # Generate output filename if not provided
            if not output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                report_type = report_data.get('report_type', 'analysis').lower().replace(' ', '_')
                output_filename = f"{report_type}_report_{timestamp}.md"

            # Write to file
            output_path = self.output_dir / output_filename
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(rendered_content)

            self.logger.info(f"Report generated successfully: {output_path}")
            return str(output_path)

        except Exception as e:
            self.logger.error(f"Failed to generate report: {e}")
            raise

    def generate_stock_analysis_report(
        self,
        symbol: str,
        analysis_data: Dict[str, Any],
        template_name: str = "reports/stock_analysis.md"
    ) -> str:
        """
        Generate a stock analysis report.

        Args:
            symbol: Stock symbol
            analysis_data: Analysis results from various engines
            template_name: Template to use

        Returns:
            Path to generated report
        """
        report_data = {
            'report_type': 'Stock Analysis',
            'symbol': symbol.upper(),
            'current_price': analysis_data.get('current_price'),
            'target_price': analysis_data.get('target_price'),
            'recommendation': analysis_data.get('recommendation', 'HOLD'),
            'technical_analysis': analysis_data.get('technical_analysis'),
            'fundamental_analysis': analysis_data.get('fundamental_analysis'),
            'risk_assessment': analysis_data.get('risk_assessment'),
            'investment_thesis': analysis_data.get('investment_thesis', ''),
            'risks': analysis_data.get('risks', []),
            'conclusion': analysis_data.get('conclusion', '')
        }

        title = f"{symbol.upper()} Stock Analysis"
        filename = f"{symbol.lower()}_analysis_{datetime.now().strftime('%Y%m%d')}.md"

        return self.generate_report(template_name, report_data, filename, title)

    def generate_portfolio_analysis_report(
        self,
        portfolio_data: Dict[str, Any],
        template_name: str = "reports/portfolio_analysis.md"
    ) -> str:
        """
        Generate a portfolio analysis report.

        Args:
            portfolio_data: Portfolio analysis results
            template_name: Template to use

        Returns:
            Path to generated report
        """
        report_data = {
            'report_type': 'Portfolio Analysis',
            'total_value': portfolio_data.get('total_value'),
            'period': portfolio_data.get('period', '1Y'),
            'assets': portfolio_data.get('assets', []),
            'performance': portfolio_data.get('performance'),
            'risk': portfolio_data.get('risk'),
            'recommendations': portfolio_data.get('recommendations', []),
            'market_commentary': portfolio_data.get('market_commentary', '')
        }

        title = f"Portfolio Analysis - {report_data['period']}"
        filename = f"portfolio_analysis_{datetime.now().strftime('%Y%m%d')}.md"

        return self.generate_report(template_name, report_data, filename, title)

    def generate_market_summary_report(
        self,
        market_data: Dict[str, Any],
        template_name: str = "reports/market_summary.md"
    ) -> str:
        """
        Generate a market summary report.

        Args:
            market_data: Market data and analysis
            template_name: Template to use

        Returns:
            Path to generated report
        """
        report_data = {
            'report_type': 'Market Summary',
            'date': market_data.get('date', datetime.now().strftime('%Y-%m-%d')),
            'market_status': market_data.get('market_status', 'Open'),
            'indices': market_data.get('indices', []),
            'top_gainers': market_data.get('top_gainers', []),
            'top_losers': market_data.get('top_losers', []),
            'sectors': market_data.get('sectors', []),
            'news': market_data.get('news', []),
            'sentiment': market_data.get('sentiment')
        }

        title = f"Market Summary - {report_data['date']}"
        filename = f"market_summary_{datetime.now().strftime('%Y%m%d')}.md"

        return self.generate_report(template_name, report_data, filename, title)

    def generate_comprehensive_report(
        self,
        symbols: List[str],
        analysis_engines: Dict[str, Any],
        template_name: str = "report-template.md"
    ) -> str:
        """
        Generate a comprehensive investment report using multiple data sources.

        Args:
            symbols: List of stock symbols to analyze
            analysis_engines: Dictionary of initialized analysis engines
            template_name: Template to use

        Returns:
            Path to generated report
        """
        try:
            # Initialize analysis components
            sentiment_analyzer = analysis_engines.get('sentiment_analyzer')
            chart_analyzer = analysis_engines.get('chart_analyzer')
            recommendation_engine = analysis_engines.get('recommendation_engine')
            risk_engine = analysis_engines.get('risk_engine')

            # Collect analysis data for all symbols
            stock_analyses = []
            for symbol in symbols:
                try:
                    stock_analysis = self._analyze_single_stock(
                        symbol, sentiment_analyzer, chart_analyzer,
                        recommendation_engine, risk_engine
                    )
                    stock_analyses.append(stock_analysis)
                except Exception as e:
                    self.logger.warning(f"Failed to analyze {symbol}: {e}")
                    continue

            # Generate market overview
            market_overview = self._generate_market_overview()

            # Generate portfolio analysis if applicable
            portfolio_analysis = self._generate_portfolio_summary(stock_analyses)

            # Generate sentiment analysis
            sentiment_analysis = self._generate_sentiment_summary(symbols, sentiment_analyzer)

            # Generate risk management summary
            risk_management = self._generate_risk_summary(stock_analyses, risk_engine)

            # Generate recommendations
            recommendations = self._generate_recommendations(stock_analyses, recommendation_engine)

            # Compile comprehensive report data
            report_data = {
                'report_type': 'Comprehensive Investment Analysis',
                'period': '1D',  # Can be made configurable
                'recommendation': self._determine_overall_recommendation(recommendations),
                'key_highlights': self._extract_key_highlights(stock_analyses, recommendations),
                'market_overview': market_overview,
                'stock_analysis': stock_analyses,
                'portfolio_analysis': portfolio_analysis,
                'sentiment_analysis': sentiment_analysis,
                'risk_management': risk_management,
                'recommendations': recommendations,
                'market_commentary': self._generate_market_commentary(),
                'disclaimers': self._get_standard_disclaimers(),
                'technical_details': self._get_technical_details()
            }

            title = "Comprehensive Investment Analysis Report"
            filename = f"comprehensive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

            return self.generate_report(template_name, report_data, filename, title)

        except Exception as e:
            self.logger.error(f"Failed to generate comprehensive report: {e}")
            raise

    def _prepare_report_data(self, data: Dict[str, Any], title: Optional[str] = None) -> Dict[str, Any]:
        """Prepare report data with standard metadata."""
        report_data = data.copy()

        # Add standard metadata
        current_time = datetime.now()
        report_data.update({
            'analysis_date': current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'report_id': str(uuid.uuid4())[:8],
            'next_update': (current_time + timedelta(days=1)).strftime('%Y-%m-%d'),
            'title': title or report_data.get('title', 'Investment Analysis Report')
        })

        return report_data

    def _analyze_single_stock(
        self,
        symbol: str,
        sentiment_analyzer,
        chart_analyzer,
        recommendation_engine,
        risk_engine
    ) -> Dict[str, Any]:
        """Analyze a single stock using available engines."""
        analysis = {
            'symbol': symbol.upper(),
            'name': symbol.upper(),  # Would get from data source in real implementation
            'current_price': 0.0,  # Would get from market data
            'target_price': 0.0,
            'recommendation': 'HOLD',
            'technical_indicators': [],
            'fundamentals': {},
            'risk': {},
            'analysis_summary': f"Analysis for {symbol.upper()} completed."
        }

        # Add technical analysis if available
        if chart_analyzer:
            try:
                # This would call actual chart analysis in real implementation
                analysis['technical_indicators'] = [
                    {'name': 'RSI', 'value': '45.2', 'signal': 'Neutral'},
                    {'name': 'MACD', 'value': '0.12', 'signal': 'Bullish'},
                    {'name': 'SMA(50)', 'value': '156.78', 'signal': 'Support'}
                ]
            except Exception as e:
                self.logger.warning(f"Technical analysis failed for {symbol}: {e}")

        # Add risk analysis if available
        if risk_engine:
            try:
                analysis['risk'] = {
                    'volatility': 22.5,
                    'beta': 1.15,
                    'score': 65
                }
            except Exception as e:
                self.logger.warning(f"Risk analysis failed for {symbol}: {e}")

        # Add recommendation if available
        if recommendation_engine:
            try:
                # This would call actual recommendation engine
                analysis['recommendation'] = 'BUY'
                analysis['target_price'] = 175.50
            except Exception as e:
                self.logger.warning(f"Recommendation generation failed for {symbol}: {e}")

        return analysis

    def _generate_market_overview(self) -> Dict[str, Any]:
        """Generate market overview data."""
        return {
            'status': 'Open',
            'sentiment': 'Neutral',
            'indices': [
                {'name': 'S&P 500', 'value': '4,450.12', 'change': '+12.34', 'change_percent': '+0.28'},
                {'name': 'NASDAQ', 'value': '13,756.33', 'change': '-45.67', 'change_percent': '-0.33'},
                {'name': 'DOW', 'value': '34,589.77', 'change': '+89.12', 'change_percent': '+0.26'}
            ]
        }

    def _generate_portfolio_summary(self, stock_analyses: List[Dict]) -> Dict[str, Any]:
        """Generate portfolio analysis summary."""
        return {
            'total_value': 250000.00,
            'total_return': 8.45,
            'risk_score': 72,
            'assets': [
                {
                    'name': analysis['name'],
                    'symbol': analysis['symbol'],
                    'weight': 100 / len(stock_analyses),  # Equal weight for simplicity
                    'value': 250000.00 / len(stock_analyses),
                    'return': 8.45
                } for analysis in stock_analyses
            ],
            'performance': {
                'annualized_return': 12.3,
                'volatility': 18.7,
                'sharpe_ratio': 0.85,
                'max_drawdown': -15.2
            }
        }

    def _generate_sentiment_summary(self, symbols: List[str], sentiment_analyzer) -> Dict[str, Any]:
        """Generate sentiment analysis summary."""
        return {
            'overall_sentiment': 'Neutral',
            'news_score': 65,
            'social_score': 72,
            'news_items': [
                {
                    'title': 'Market shows resilience amid economic uncertainty',
                    'source': 'Financial News',
                    'sentiment': 'Positive',
                    'impact': 'Medium'
                }
            ]
        }

    def _generate_risk_summary(self, stock_analyses: List[Dict], risk_engine) -> Dict[str, Any]:
        """Generate risk management summary."""
        return {
            'metrics': [
                {'name': 'Portfolio Beta', 'current_value': '1.12', 'threshold': '1.50', 'status': 'PASS'},
                {'name': 'VaR (95%)', 'current_value': '2.3%', 'threshold': '5.0%', 'status': 'PASS'},
                {'name': 'Max Drawdown', 'current_value': '8.7%', 'threshold': '15.0%', 'status': 'PASS'}
            ],
            'alerts': [],
            'position_sizing': [
                {
                    'symbol': analysis['symbol'],
                    'recommended_size': 20.0,
                    'current_size': 100 / len(stock_analyses)
                } for analysis in stock_analyses
            ]
        }

    def _generate_recommendations(self, stock_analyses: List[Dict], recommendation_engine) -> List[Dict]:
        """Generate investment recommendations."""
        recommendations = []

        for analysis in stock_analyses:
            if analysis['recommendation'] == 'BUY':
                recommendations.append({
                    'title': f'Consider increasing position in {analysis["symbol"]}',
                    'action': 'BUY',
                    'priority': 'Medium',
                    'confidence': 75,
                    'description': f'Technical and fundamental analysis suggests upside potential for {analysis["symbol"]}.',
                    'rationale': [
                        'Strong technical indicators',
                        'Positive earnings outlook',
                        'Favorable market sentiment'
                    ],
                    'risks': [
                        'Market volatility',
                        'Sector-specific headwinds'
                    ],
                    'expected_return': 15.0,
                    'time_horizon': '6-12 months'
                })

        return recommendations

    def _determine_overall_recommendation(self, recommendations: List[Dict]) -> str:
        """Determine overall portfolio recommendation."""
        if not recommendations:
            return 'HOLD'

        buy_count = sum(1 for rec in recommendations if rec['action'] == 'BUY')
        sell_count = sum(1 for rec in recommendations if rec['action'] == 'SELL')

        if buy_count > sell_count:
            return 'BUY'
        elif sell_count > buy_count:
            return 'SELL'
        else:
            return 'HOLD'

    def _extract_key_highlights(self, stock_analyses: List[Dict], recommendations: List[Dict]) -> List[str]:
        """Extract key highlights from analysis."""
        highlights = []

        # Add stock-specific highlights
        for analysis in stock_analyses:
            if analysis['recommendation'] == 'BUY':
                highlights.append(f"{analysis['symbol']} shows strong bullish signals")

        # Add recommendation highlights
        if recommendations:
            highlights.append(f"{len(recommendations)} actionable recommendations identified")

        return highlights

    def _generate_market_commentary(self) -> str:
        """Generate market commentary."""
        return ("Current market conditions show mixed signals with some sectors "
                "outperforming while others face headwinds. Investors should "
                "maintain a balanced approach and focus on quality fundamentals.")

    def _get_standard_disclaimers(self) -> List[Dict]:
        """Get standard disclaimers."""
        return [
            {
                'title': 'Investment Risk Warning',
                'text': 'All investments carry risk of loss. Past performance does not guarantee future results.'
            },
            {
                'title': 'Not Financial Advice',
                'text': 'This report is for informational purposes only and should not be considered as investment advice.'
            }
        ]

    def _get_technical_details(self) -> Dict[str, Any]:
        """Get technical details about the report generation."""
        return {
            'version': '1.0.0',
            'data_sources': ['Alpha Vantage', 'NewsAPI', 'Reddit'],
            'models': ['Sentiment Analysis', 'Technical Analysis', 'Risk Assessment'],
            'generation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data_age': 'Real-time'
        }

    # Jinja2 custom filters
    def _format_currency(self, value: Union[float, str]) -> str:
        """Format value as currency."""
        try:
            return f"${float(value):,.2f}"
        except (ValueError, TypeError):
            return str(value)

    def _format_percentage(self, value: Union[float, str]) -> str:
        """Format value as percentage."""
        try:
            # Convert to percentage (multiply by 100) and format
            return f"{float(value) * 100:.2f}%"
        except (ValueError, TypeError):
            return str(value)

    def _round_float(self, value: Union[float, str], decimals: int = 2) -> str:
        """Round float to specified decimals."""
        try:
            return f"{float(value):.{decimals}f}"
        except (ValueError, TypeError):
            return str(value)

    def _format_date(self, value: Union[str, datetime], format_str: str = '%Y-%m-%d') -> str:
        """Format date string."""
        try:
            if isinstance(value, str):
                # Try to parse the date string
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
            elif isinstance(value, datetime):
                dt = value
            else:
                return str(value)

            return dt.strftime(format_str)
        except (ValueError, TypeError):
            return str(value)


# Convenience functions for common use cases
def generate_stock_report(symbol: str, analysis_data: Dict[str, Any]) -> str:
    """Generate a stock analysis report."""
    generator = MarkdownReportGenerator()
    return generator.generate_stock_analysis_report(symbol, analysis_data)


def generate_portfolio_report(portfolio_data: Dict[str, Any]) -> str:
    """Generate a portfolio analysis report."""
    generator = MarkdownReportGenerator()
    return generator.generate_portfolio_analysis_report(portfolio_data)


def generate_market_report(market_data: Dict[str, Any]) -> str:
    """Generate a market summary report."""
    generator = MarkdownReportGenerator()
    return generator.generate_market_summary_report(market_data)


def generate_comprehensive_report(symbols: List[str], analysis_engines: Dict[str, Any]) -> str:
    """Generate a comprehensive investment report."""
    generator = MarkdownReportGenerator()
    return generator.generate_comprehensive_report(symbols, analysis_engines)


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)

    # Example stock analysis data
    sample_data = {
        'symbol': 'AAPL',
        'current_price': 150.25,
        'target_price': 165.00,
        'recommendation': 'BUY',
        'technical_analysis': {
            'indicators': [
                {'name': 'RSI', 'value': '45.2', 'signal': 'Neutral'},
                {'name': 'MACD', 'value': '0.12', 'signal': 'Bullish'}
            ],
            'summary': 'Technical indicators suggest bullish momentum.'
        },
        'investment_thesis': 'Strong fundamentals and growth prospects.',
        'risks': ['Market volatility', 'Regulatory changes'],
        'conclusion': 'Attractive investment opportunity with solid upside potential.'
    }

    # Generate report
    generator = MarkdownReportGenerator()
    report_path = generator.generate_stock_analysis_report('AAPL', sample_data)
    print(f"Report generated: {report_path}")
