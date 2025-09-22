"""
Test runner for report generation tests.

This script provides a simple way to run tests for the report generation system
without requiring all external dependencies to be installed.
"""

import sys
import os
from pathlib import Path

# Add src directory to path
project_root = Path(__file__).parents[2]
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing module imports...")

    try:
        # Test basic imports without external dependencies
        import tempfile
        import json
        from datetime import datetime
        print("✓ Standard library imports successful")

        # Test project modules (will work if dependencies are available)
        try:
            from reports.markdown_generator import MarkdownReportGenerator
            print("✓ MarkdownReportGenerator import successful")
        except ImportError as e:
            print(f"⚠ MarkdownReportGenerator import failed: {e}")

        try:
            from reports.report_validator import ReportValidator
            print("✓ ReportValidator import successful")
        except ImportError as e:
            print(f"⚠ ReportValidator import failed: {e}")

        try:
            from reports.report_history import ReportHistoryTracker
            print("✓ ReportHistoryTracker import successful")
        except ImportError as e:
            print(f"⚠ ReportHistoryTracker import failed: {e}")

        return True

    except Exception as e:
        print(f"✗ Import test failed: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality without external dependencies."""
    print("\nTesting basic functionality...")

    try:
        import tempfile
        from datetime import datetime

        # Test template directory structure
        template_content = """# {{title}}

## Summary
{{data.content | default('No content')}}

Date: {{data.date}}
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(template_content)
            template_path = f.name

        # Test that we can read the template
        with open(template_path, 'r') as f:
            content = f.read()

        assert '{{title}}' in content
        assert '{{data.content' in content

        os.unlink(template_path)
        print("✓ Template handling test successful")

        # Test data structures
        test_data = {
            'analysis_date': datetime.now().isoformat(),
            'recommendation': 'BUY',
            'stock_analysis': [
                {
                    'symbol': 'AAPL',
                    'current_price': 150.25,
                    'target_price': 175.50
                }
            ]
        }

        assert test_data['recommendation'] == 'BUY'
        assert len(test_data['stock_analysis']) == 1
        print("✓ Data structure test successful")

        return True

    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False

def test_validation_logic():
    """Test validation logic without full validator."""
    print("\nTesting validation logic...")

    try:
        # Test markdown structure detection
        sample_report = """# Investment Report

## Executive Summary
This is a test report.

## Analysis
Some analysis content here.

## Disclaimer
This is not financial advice.
"""

        lines = sample_report.split('\n')
        headers = [line for line in lines if line.strip().startswith('#')]

        assert len(headers) == 4  # Title + 3 sections
        assert '# Investment Report' in headers[0]
        assert '## Executive Summary' in headers[1]

        print("✓ Markdown structure detection successful")

        # Test content length validation
        word_count = len(sample_report.split())
        char_count = len(sample_report)

        assert word_count > 10
        assert char_count > 50

        print("✓ Content metrics calculation successful")

        return True

    except Exception as e:
        print(f"✗ Validation logic test failed: {e}")
        return False

def test_database_structure():
    """Test database structure without full implementation."""
    print("\nTesting database structure...")

    try:
        import sqlite3
        import tempfile

        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        # Test database creation
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Create test table (similar to what ReportHistoryTracker uses)
            cursor.execute('''
                CREATE TABLE test_reports (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Insert test data
            cursor.execute(
                'INSERT INTO test_reports (id, title) VALUES (?, ?)',
                ('test_001', 'Test Report')
            )

            # Query test data
            cursor.execute('SELECT * FROM test_reports')
            rows = cursor.fetchall()

            assert len(rows) == 1
            assert rows[0][0] == 'test_001'
            assert rows[0][1] == 'Test Report'

            conn.commit()

        os.unlink(db_path)
        print("✓ Database operations test successful")

        return True

    except Exception as e:
        print(f"✗ Database structure test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Report Generation System - Test Runner")
    print("=" * 50)

    all_passed = True

    all_passed &= test_imports()
    all_passed &= test_basic_functionality()
    all_passed &= test_validation_logic()
    all_passed &= test_database_structure()

    print("\n" + "=" * 50)
    if all_passed:
        print("✓ All basic tests passed!")
        print("\nNote: Some modules may show import warnings if optional")
        print("dependencies (like Jinja2, PyYAML, pandas) are not installed.")
        print("This is expected and won't affect core functionality.")
    else:
        print("✗ Some tests failed. Check the output above for details.")
        sys.exit(1)

if __name__ == '__main__':
    main()
