"""
Analysis Engine Test Configuration and Runner

This module provides configuration and utilities for running the analysis engine test suite.
"""

import pytest
import sys
import os
from pathlib import Path

# Ensure src is in path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))

def run_sentiment_tests():
    """Run sentiment analyzer tests only."""
    return pytest.main([
        str(Path(__file__).parent / 'test_sentiment_analyzer.py'),
        "-v",
        "--tb=short",
        "--color=yes"
    ])

def run_chart_tests():
    """Run chart analyzer tests only."""
    return pytest.main([
        str(Path(__file__).parent / 'test_chart_analyzer.py'),
        "-v",
        "--tb=short",
        "--color=yes"
    ])

def run_recommendation_tests():
    """Run recommendation engine tests only."""
    return pytest.main([
        str(Path(__file__).parent / 'test_recommendation_engine.py'),
        "-v",
        "--tb=short",
        "--color=yes"
    ])

def run_integration_tests():
    """Run integration tests only."""
    return pytest.main([
        str(Path(__file__).parent / 'test_integration.py'),
        "-v",
        "--tb=short",
        "--color=yes"
    ])

def run_all_analysis_tests():
    """Run all analysis engine tests."""
    return pytest.main([
        str(Path(__file__).parent),
        "-v",
        "--tb=short",
        "--color=yes",
        "--durations=10"  # Show 10 slowest tests
    ])

def run_quick_tests():
    """Run a subset of quick tests for rapid feedback."""
    return pytest.main([
        str(Path(__file__).parent),
        "-v",
        "--tb=short",
        "--color=yes",
        "-k", "not integration and not performance"  # Skip slow tests
    ])

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run Analysis Engine Tests")
    parser.add_argument(
        "test_type",
        choices=["all", "quick", "sentiment", "chart", "recommendation", "integration"],
        help="Type of tests to run"
    )

    args = parser.parse_args()

    test_runners = {
        "all": run_all_analysis_tests,
        "quick": run_quick_tests,
        "sentiment": run_sentiment_tests,
        "chart": run_chart_tests,
        "recommendation": run_recommendation_tests,
        "integration": run_integration_tests
    }

    exit_code = test_runners[args.test_type]()
    sys.exit(exit_code)
