"""
Reports package for Agent Investment Platform

This package provides comprehensive report generation capabilities including:
- Markdown report generation with Jinja2 templates
- Report validation and quality checks
- Report history tracking and performance analysis
- GitHub report publishing and version control
"""

from .markdown_generator import (
    MarkdownReportGenerator,
    generate_stock_report,
    generate_portfolio_report,
    generate_market_report,
    generate_comprehensive_report
)

from .report_validator import (
    ReportValidator,
    ValidationResult,
    ValidationIssue,
    ValidationLevel,
    ValidationCategory,
    validate_report_content,
    validate_report_file
)

from .report_history import (
    ReportHistoryTracker,
    Prediction,
    ReportMetrics,
    PredictionType,
    PredictionStatus,
    track_report,
    get_performance_summary
)

__all__ = [
    # Markdown Generation
    'MarkdownReportGenerator',
    'generate_stock_report',
    'generate_portfolio_report',
    'generate_market_report',
    'generate_comprehensive_report',

    # Report Validation
    'ReportValidator',
    'ValidationResult',
    'ValidationIssue',
    'ValidationLevel',
    'ValidationCategory',
    'validate_report_content',
    'validate_report_file',

    # Report History
    'ReportHistoryTracker',
    'Prediction',
    'ReportMetrics',
    'PredictionType',
    'PredictionStatus',
    'track_report',
    'get_performance_summary'
]
