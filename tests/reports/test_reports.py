"""
Unit tests for report generation package.

This module contains comprehensive tests for all report generation components:
- Markdown report generation
- Report validation
- Report history tracking
"""

import unittest
import tempfile
import shutil
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import the modules to test
import sys
sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

try:
    from reports.markdown_generator import MarkdownReportGenerator, generate_stock_report
    from reports.report_validator import ReportValidator, validate_report_content, ValidationLevel
    from reports.report_history import ReportHistoryTracker, track_report, PredictionType
except ImportError as e:
    # Skip tests if dependencies are not available
    print(f"Skipping tests due to missing dependencies: {e}")
    sys.exit(0)


class TestMarkdownReportGenerator(unittest.TestCase):
    """Test cases for MarkdownReportGenerator."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.template_dir = Path(self.temp_dir) / "templates"
        self.output_dir = Path(self.temp_dir) / "output"

        # Create template directory structure
        self.template_dir.mkdir(parents=True, exist_ok=True)
        (self.template_dir / "reports").mkdir(exist_ok=True)

        # Create a simple test template
        test_template = """# {{title}}

## Summary
**Date:** {{data.date}}
**Recommendation:** {{data.recommendation}}

## Details
{{data.content | default('No content provided')}}

---
Generated on {{data.date}}
"""

        with open(self.template_dir / "test_template.md", 'w') as f:
            f.write(test_template)

        # Initialize generator
        self.generator = MarkdownReportGenerator(
            template_dir=str(self.template_dir),
            output_dir=str(self.output_dir)
        )

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """Test generator initialization."""
        self.assertEqual(self.generator.template_dir, self.template_dir)
        self.assertEqual(self.generator.output_dir, self.output_dir)
        self.assertIsNotNone(self.generator.jinja_env)

    def test_generate_report_basic(self):
        """Test basic report generation."""
        test_data = {
            'date': '2025-09-22',
            'recommendation': 'BUY',
            'content': 'This is test content for the report.'
        }

        report_path = self.generator.generate_report(
            'test_template.md',
            test_data,
            'test_output.md',
            'Test Report'
        )

        # Check that file was created
        self.assertTrue(Path(report_path).exists())

        # Check content
        with open(report_path, 'r') as f:
            content = f.read()

        self.assertIn('# Test Report', content)
        self.assertIn('**Date:** 2025-09-22', content)
        self.assertIn('**Recommendation:** BUY', content)
        self.assertIn('This is test content', content)

    def test_generate_report_with_filters(self):
        """Test report generation with Jinja2 filters."""
        # Create template with filters
        filter_template = """# {{title}}

Price: {{data.price | currency}}
Change: {{data.change | percentage}}
Date: {{data.date | format_date('%B %d, %Y')}}
"""

        with open(self.template_dir / "filter_template.md", 'w') as f:
            f.write(filter_template)

        test_data = {
            'price': 150.75,
            'change': 0.0325,
            'date': '2025-09-22'
        }

        report_path = self.generator.generate_report(
            'filter_template.md',
            test_data,
            'filter_test.md',
            'Filter Test'
        )

        with open(report_path, 'r') as f:
            content = f.read()

        # Check that filters were applied (basic check)
        self.assertIn('$150.75', content)
        self.assertIn('3.25%', content)

    def test_stock_analysis_report(self):
        """Test specific stock analysis report generation."""
        analysis_data = {
            'current_price': 150.25,
            'target_price': 165.00,
            'recommendation': 'BUY',
            'technical_analysis': {
                'indicators': [
                    {'name': 'RSI', 'value': '65.2', 'signal': 'Neutral'},
                    {'name': 'MACD', 'value': '1.2', 'signal': 'Bullish'}
                ],
                'summary': 'Technical indicators show bullish momentum.'
            },
            'investment_thesis': 'Strong fundamentals and growth prospects.',
            'risks': ['Market volatility', 'Competition'],
            'conclusion': 'Recommended buy with upside potential.'
        }

        # Create stock analysis template
        stock_template = """# {{title}}

**Current Price:** {{data.current_price | currency}}
**Target Price:** {{data.target_price | currency}}
**Recommendation:** {{data.recommendation}}

## Technical Analysis
{% if data.technical_analysis %}
{{data.technical_analysis.summary}}
{% endif %}

## Investment Thesis
{{data.investment_thesis}}

## Risks
{% for risk in data.risks %}
- {{risk}}
{% endfor %}

## Conclusion
{{data.conclusion}}
"""

        with open(self.template_dir / "reports" / "stock_analysis.md", 'w') as f:
            f.write(stock_template)

        report_path = self.generator.generate_stock_analysis_report('AAPL', analysis_data)

        self.assertTrue(Path(report_path).exists())

        with open(report_path, 'r') as f:
            content = f.read()

        self.assertIn('AAPL Stock Analysis', content)
        self.assertIn('$150.25', content)
        self.assertIn('$165.00', content)
        self.assertIn('BUY', content)
        self.assertIn('Market volatility', content)

    def test_error_handling(self):
        """Test error handling for invalid templates."""
        with self.assertRaises(Exception):
            self.generator.generate_report(
                'nonexistent_template.md',
                {},
                'output.md',
                'Test'
            )


class TestReportValidator(unittest.TestCase):
    """Test cases for ReportValidator."""

    def setUp(self):
        """Set up test fixtures."""
        self.validator = ReportValidator()

    def test_valid_report(self):
        """Test validation of a valid report."""
        valid_report = """# Investment Analysis Report

## Executive Summary

This report provides a comprehensive analysis of AAPL stock.

## Analysis

Technical indicators show positive momentum with RSI at 65.

## Recommendations

We recommend a BUY rating with a target price of $175.

## Risk Assessment

Market volatility and competition present moderate risks.

## Disclaimer

This is not financial advice. Past performance does not guarantee future results.
All investments carry risk of loss.
"""

        result = self.validator.validate_report(valid_report)

        self.assertTrue(result.score > 70)  # Should pass minimum score
        self.assertEqual(len([i for i in result.issues if i.level == ValidationLevel.ERROR]), 0)

    def test_invalid_report_missing_sections(self):
        """Test validation of report missing required sections."""
        invalid_report = """# Short Report

This is a very short report without proper sections.
"""

        result = self.validator.validate_report(invalid_report)

        self.assertFalse(result.is_valid)
        self.assertTrue(len(result.issues) > 0)

        # Check for missing sections
        error_messages = [issue.message for issue in result.issues if issue.level == ValidationLevel.ERROR]
        self.assertTrue(any('Missing required section' in msg for msg in error_messages))

    def test_report_with_placeholder_text(self):
        """Test validation of report with placeholder text."""
        placeholder_report = """# Test Report

## Executive Summary

TODO: Add summary here

## Analysis

This section contains {{placeholder}} text that should be flagged.

## Recommendations

TBD - need to complete analysis first.

## Disclaimer

This is not financial advice.
"""

        result = self.validator.validate_report(placeholder_report)

        # Should find placeholder issues
        error_messages = [issue.message for issue in result.issues if issue.level == ValidationLevel.ERROR]
        self.assertTrue(any('Placeholder text found' in msg for msg in error_messages))

    def test_report_with_data_issues(self):
        """Test validation of report with data quality issues."""
        data_issue_report = """# Test Report

## Executive Summary

The stock price is $999,999,999.99 with a 5000% return.

## Analysis

This analysis covers the period from 1900-01-01 to 2050-12-31.

## Disclaimer

This is not financial advice.
"""

        result = self.validator.validate_report(data_issue_report)

        # Should find data quality issues
        warning_messages = [issue.message for issue in result.issues if issue.level == ValidationLevel.WARNING]
        self.assertTrue(any('Unusually large number' in msg or 'Unusually high percentage' in msg
                          for msg in warning_messages))

    def test_convenience_function(self):
        """Test convenience function for validation."""
        test_report = """# Test Report

## Summary
Basic report content.

## Disclaimer
This is not financial advice.
"""

        result = validate_report_content(test_report)
        self.assertIsNotNone(result)
        self.assertIsInstance(result.score, float)


class TestReportHistoryTracker(unittest.TestCase):
    """Test cases for ReportHistoryTracker."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        self.tracker = ReportHistoryTracker(self.temp_db.name)

    def tearDown(self):
        """Clean up test fixtures."""
        os.unlink(self.temp_db.name)

    def test_add_report(self):
        """Test adding a report to the tracker."""
        predictions = [
            {
                'prediction_type': 'stock_price',
                'symbol': 'AAPL',
                'predicted_value': 175.50,
                'confidence': 0.85,
                'time_horizon': '3M'
            }
        ]

        report_id = self.tracker.add_report(
            report_id="test_001",
            title="Test Analysis",
            report_type="stock_analysis",
            content="Test content",
            predictions=predictions,
            model_used="test_model",
            symbols=["AAPL"]
        )

        self.assertEqual(report_id, "test_001")

        # Verify report was stored
        metrics = self.tracker.get_report_metrics(report_id)
        self.assertIsNotNone(metrics)
        self.assertEqual(metrics.total_predictions, 1)

    def test_update_prediction_outcome(self):
        """Test updating prediction outcomes."""
        # First add a report with predictions
        predictions = [
            {
                'prediction_type': 'stock_price',
                'symbol': 'AAPL',
                'predicted_value': 175.50,
                'confidence': 0.85,
                'time_horizon': '1M'
            }
        ]

        report_id = self.tracker.add_report(
            report_id="test_002",
            title="Prediction Test",
            report_type="stock_analysis",
            content="Test content",
            predictions=predictions
        )

        # Get the prediction ID (we'll need to query the database for this)
        import sqlite3
        with sqlite3.connect(self.tracker.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM predictions WHERE report_id = ?', (report_id,))
            pred_id = cursor.fetchone()[0]

        # Update the prediction outcome
        success = self.tracker.update_prediction_outcome(pred_id, 180.25, 0.85)
        self.assertTrue(success)

        # Verify the update
        with sqlite3.connect(self.tracker.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT actual_value, accuracy_score FROM predictions WHERE id = ?', (pred_id,))
            actual_value, accuracy_score = cursor.fetchone()

        self.assertEqual(actual_value, '180.25')
        self.assertEqual(accuracy_score, 0.85)

    def test_get_overall_performance(self):
        """Test getting overall performance metrics."""
        # Add multiple reports
        for i in range(3):
            predictions = [
                {
                    'prediction_type': 'stock_price',
                    'symbol': 'AAPL',
                    'predicted_value': 175.50 + i,
                    'confidence': 0.8,
                    'time_horizon': '1M'
                }
            ]

            self.tracker.add_report(
                report_id=f"perf_test_{i}",
                title=f"Performance Test {i}",
                report_type="stock_analysis",
                content="Test content",
                predictions=predictions
            )

        performance = self.tracker.get_overall_performance()

        self.assertEqual(performance['summary']['total_reports'], 3)
        self.assertEqual(performance['summary']['total_predictions'], 3)
        self.assertEqual(performance['summary']['pending_predictions'], 3)

    def test_get_pending_predictions(self):
        """Test getting pending predictions."""
        predictions = [
            {
                'prediction_type': 'stock_price',
                'symbol': 'AAPL',
                'predicted_value': 175.50,
                'confidence': 0.85,
                'time_horizon': '1W'  # Should be due soon
            }
        ]

        self.tracker.add_report(
            report_id="pending_test",
            title="Pending Test",
            report_type="stock_analysis",
            content="Test content",
            predictions=predictions
        )

        pending = self.tracker.get_pending_predictions(days_ahead=30)
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]['symbol'], 'AAPL')

    def test_convenience_function(self):
        """Test convenience function for tracking reports."""
        report_id = track_report(
            report_id="convenience_test",
            title="Convenience Test",
            report_type="test",
            content="Test content",
            predictions=[],
            db_path=self.temp_db.name
        )

        self.assertEqual(report_id, "convenience_test")


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete report system."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.template_dir = Path(self.temp_dir) / "templates"
        self.output_dir = Path(self.temp_dir) / "output"
        self.db_path = Path(self.temp_dir) / "test.db"

        # Create template directory
        self.template_dir.mkdir(parents=True, exist_ok=True)

        # Create comprehensive template
        comprehensive_template = """# {{title}}

## Executive Summary
**Date:** {{data.analysis_date}}
**Recommendation:** {{data.recommendation}}

{% if data.stock_analysis %}
## Stock Analysis
{% for stock in data.stock_analysis %}
### {{stock.symbol}}
**Price:** ${{stock.current_price}}
**Target:** ${{stock.target_price}}
**Recommendation:** {{stock.recommendation}}
{% endfor %}
{% endif %}

## Disclaimer
This is not financial advice. Past performance does not guarantee future results.
"""

        with open(self.template_dir / "comprehensive.md", 'w') as f:
            f.write(comprehensive_template)

        # Initialize components
        self.generator = MarkdownReportGenerator(
            template_dir=str(self.template_dir),
            output_dir=str(self.output_dir)
        )
        self.validator = ReportValidator()
        self.tracker = ReportHistoryTracker(str(self.db_path))

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_complete_workflow(self):
        """Test complete report generation, validation, and tracking workflow."""
        # 1. Generate report
        report_data = {
            'recommendation': 'BUY',
            'stock_analysis': [
                {
                    'symbol': 'AAPL',
                    'current_price': 150.25,
                    'target_price': 175.50,
                    'recommendation': 'BUY'
                }
            ]
        }

        report_path = self.generator.generate_report(
            'comprehensive.md',
            report_data,
            'integration_test.md',
            'Integration Test Report'
        )

        # 2. Validate report
        validation_result = self.validator.validate_report_file(report_path)

        # 3. Track report
        predictions = [
            {
                'prediction_type': 'stock_price',
                'symbol': 'AAPL',
                'predicted_value': 175.50,
                'confidence': 0.85,
                'time_horizon': '3M'
            }
        ]

        with open(report_path, 'r') as f:
            content = f.read()

        report_id = self.tracker.add_report(
            report_id="integration_001",
            title="Integration Test Report",
            report_type="comprehensive",
            content=content,
            predictions=predictions,
            file_path=str(report_path)
        )

        # Verify complete workflow
        self.assertTrue(Path(report_path).exists())
        self.assertIsNotNone(validation_result)
        self.assertEqual(report_id, "integration_001")

        # Check tracking metrics
        metrics = self.tracker.get_report_metrics(report_id)
        self.assertIsNotNone(metrics)
        self.assertEqual(metrics.total_predictions, 1)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
