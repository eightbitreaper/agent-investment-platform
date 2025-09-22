#!/usr/bin/env python3
"""
Agent Investment Platform - Integration Testing (Simple Version)

This script provides basic integration testing for the components
without Unicode characters that cause issues on Windows.
"""

import asyncio
import logging
import json
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import traceback

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class SimpleIntegrationTester:
    """Simple integration testing framework."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.test_results = {}

        # Statistics
        self.stats = {
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'start_time': None,
            'end_time': None
        }

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run simple integration test suite."""
        self.logger.info("Starting integration testing...")
        self.stats['start_time'] = datetime.utcnow()

        try:
            # Test 1: Import Integration Framework
            await self._test_import_integration_framework()

            # Test 2: Import Scheduler
            await self._test_import_scheduler()

            # Test 3: Import Notification System
            await self._test_import_notification_system()

            # Test 4: Import Alert System
            await self._test_import_alert_system()

            # Test 5: Import Monitoring Dashboard
            await self._test_import_monitoring_dashboard()

            # Test 6: Test Integration Framework Creation
            await self._test_integration_framework_creation()

        except Exception as e:
            self.logger.error(f"Test suite execution failed: {e}")
            self.test_results['critical_error'] = {
                'error': str(e),
                'traceback': traceback.format_exc()
            }

        finally:
            self.stats['end_time'] = datetime.utcnow()

        return self._generate_test_report()

    async def _test_import_integration_framework(self):
        """Test 1: Import integration framework."""
        test_name = "import_integration_framework"
        self.logger.info(f"Running test: {test_name}")

        try:
            from src.integration.framework import IntegrationFramework, ComponentType
            self._record_test_result(test_name, True, "Integration framework imported successfully")
        except Exception as e:
            self._record_test_result(test_name, False, f"Import error: {e}")

    async def _test_import_scheduler(self):
        """Test 2: Import scheduler."""
        test_name = "import_scheduler"
        self.logger.info(f"Running test: {test_name}")

        try:
            from scheduler import JobScheduler, JobPriority
            self._record_test_result(test_name, True, "Scheduler imported successfully")
        except Exception as e:
            self._record_test_result(test_name, False, f"Import error: {e}")

    async def _test_import_notification_system(self):
        """Test 3: Import notification system."""
        test_name = "import_notification_system"
        self.logger.info(f"Running test: {test_name}")

        try:
            from src.notifications.notification_system import NotificationSystem
            self._record_test_result(test_name, True, "Notification system imported successfully")
        except Exception as e:
            self._record_test_result(test_name, False, f"Import error: {e}")

    async def _test_import_alert_system(self):
        """Test 4: Import alert system."""
        test_name = "import_alert_system"
        self.logger.info(f"Running test: {test_name}")

        try:
            from src.alerts.alert_system import IntelligentAlertSystem
            self._record_test_result(test_name, True, "Alert system imported successfully")
        except Exception as e:
            self._record_test_result(test_name, False, f"Import error: {e}")

    async def _test_import_monitoring_dashboard(self):
        """Test 5: Import monitoring dashboard."""
        test_name = "import_monitoring_dashboard"
        self.logger.info(f"Running test: {test_name}")

        try:
            from src.monitoring.dashboard import MonitoringDashboard
            self._record_test_result(test_name, True, "Monitoring dashboard imported successfully")
        except Exception as e:
            self._record_test_result(test_name, False, f"Import error: {e}")

    async def _test_integration_framework_creation(self):
        """Test 6: Create integration framework."""
        test_name = "integration_framework_creation"
        self.logger.info(f"Running test: {test_name}")

        try:
            from src.integration.framework import IntegrationFramework, ComponentType

            # Create framework
            framework = IntegrationFramework()

            # Test basic functionality
            status = framework.get_integration_status()

            if isinstance(status, dict) and 'running' in status:
                self._record_test_result(test_name, True, f"Framework created, status: {status['running']}")
            else:
                self._record_test_result(test_name, False, "Framework status invalid")

        except Exception as e:
            self._record_test_result(test_name, False, f"Creation error: {e}")

    def _record_test_result(self, test_name: str, success: bool, details: str):
        """Record test result."""
        self.stats['tests_run'] += 1
        if success:
            self.stats['tests_passed'] += 1
            self.logger.info(f"PASS {test_name}: {details}")
        else:
            self.stats['tests_failed'] += 1
            self.logger.error(f"FAIL {test_name}: {details}")

        self.test_results[test_name] = {
            'success': success,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        }

    def _generate_test_report(self) -> Dict[str, Any]:
        """Generate test report."""
        duration = None
        if self.stats['start_time'] and self.stats['end_time']:
            duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()

        success_rate = (self.stats['tests_passed'] / max(self.stats['tests_run'], 1)) * 100

        report = {
            'test_suite': 'Agent Investment Platform Integration Tests',
            'timestamp': datetime.utcnow().isoformat(),
            'duration_seconds': duration,
            'statistics': self.stats.copy(),
            'success_rate': success_rate,
            'overall_result': 'PASS' if success_rate >= 80 else 'FAIL',
            'test_results': self.test_results.copy()
        }

        # Convert datetime objects to strings
        if report['statistics']['start_time']:
            report['statistics']['start_time'] = report['statistics']['start_time'].isoformat()
        if report['statistics']['end_time']:
            report['statistics']['end_time'] = report['statistics']['end_time'].isoformat()

        return report


async def main():
    """Main test execution function."""
    print("Agent Investment Platform - Integration Testing")
    print("=" * 60)

    # Ensure logs directory exists
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Run integration tests
    tester = SimpleIntegrationTester()

    try:
        test_report = await tester.run_all_tests()

        # Display results
        print("\nTest Results Summary")
        print("=" * 60)
        print(f"Tests Run: {test_report['statistics']['tests_run']}")
        print(f"Tests Passed: {test_report['statistics']['tests_passed']}")
        print(f"Tests Failed: {test_report['statistics']['tests_failed']}")
        print(f"Success Rate: {test_report['success_rate']:.1f}%")
        print(f"Overall Result: {test_report['overall_result']}")

        if test_report['duration_seconds']:
            print(f"Duration: {test_report['duration_seconds']:.2f} seconds")

        # Save detailed report
        report_file = f"logs/integration_test_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(test_report, f, indent=2)

        print(f"\nDetailed report saved: {report_file}")

        # Display individual test results
        print("\nIndividual Test Results")
        print("=" * 60)
        for test_name, result in test_report['test_results'].items():
            status = "PASS" if result['success'] else "FAIL"
            print(f"{status} {test_name}: {result['details']}")

        # Exit with appropriate code
        if test_report['overall_result'] == 'PASS':
            print("\nAll integration tests completed successfully!")
            sys.exit(0)
        else:
            print("\nSome integration tests failed. Please review the results.")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\nIntegration testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nIntegration testing failed with critical error: {e}")
        logger.error(f"Critical test failure: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
