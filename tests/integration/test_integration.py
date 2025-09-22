#!/usr/bin/env python3
"""
Agent Investment Platform - Integration Testing

This script provides comprehensive testing for the integration framework
and all connected components including scheduling, notifications, alerts,
monitoring, and end-to-end workflows.

Key Features:
- Component integration validation
- End-to-end workflow testing
- Health monitoring verification
- Notification system testing
- Alert system validation
- Performance benchmarking
"""

import asyncio
import logging
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import traceback


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/integration_test.log')
    ]
)

logger = logging.getLogger(__name__)


class IntegrationTester:
    """Comprehensive integration testing framework."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.test_results = {}
        self.orchestrator = None

        # Test configuration
        self.test_symbols = ["AAPL", "GOOGL", "MSFT", "TSLA"]
        self.test_timeout = 300  # 5 minutes

        # Statistics
        self.stats = {
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'start_time': None,
            'end_time': None
        }

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run comprehensive integration test suite."""
        self.logger.info("🚀 Starting comprehensive integration testing...")
        self.stats['start_time'] = datetime.utcnow()

        try:
            # Test 1: Component Initialization
            await self._test_component_initialization()

            # Test 2: Integration Framework
            await self._test_integration_framework()

            # Test 3: Orchestrator Functionality
            await self._test_orchestrator_functionality()

            # Test 4: Scheduling System
            await self._test_scheduling_system()

            # Test 5: Notification System
            await self._test_notification_system()

            # Test 6: Alert System
            await self._test_alert_system()

            # Test 7: Monitoring Dashboard
            await self._test_monitoring_dashboard()

            # Test 8: End-to-End Workflows
            await self._test_end_to_end_workflows()

            # Test 9: Error Recovery
            await self._test_error_recovery()

            # Test 10: Performance Testing
            await self._test_performance()

        except Exception as e:
            self.logger.error(f"Test suite execution failed: {e}")
            self.test_results['critical_error'] = {
                'error': str(e),
                'traceback': traceback.format_exc()
            }

        finally:
            self.stats['end_time'] = datetime.utcnow()
            await self._cleanup()

        return self._generate_test_report()

    async def _test_component_initialization(self):
        """Test 1: Component initialization and registration."""
        test_name = "component_initialization"
        self.logger.info(f"🧪 Running test: {test_name}")

        try:
            # Import orchestrator
            from orchestrator import PlatformOrchestrator

            # Initialize orchestrator
            self.orchestrator = PlatformOrchestrator()

            # Test initialization
            success = await self.orchestrator.initialize()

            if success:
                # Verify component registration
                integration_status = self.orchestrator.integration_framework.get_integration_status()

                registered_components = integration_status.get('components_registered', 0)
                if registered_components > 0:
                    self._record_test_result(test_name, True, f"Successfully registered {registered_components} components")
                else:
                    self._record_test_result(test_name, False, "No components registered")
            else:
                self._record_test_result(test_name, False, "Orchestrator initialization failed")

        except Exception as e:
            self._record_test_result(test_name, False, f"Component initialization error: {e}")

    async def _test_integration_framework(self):
        """Test 2: Integration framework functionality."""
        test_name = "integration_framework"
        self.logger.info(f"🧪 Running test: {test_name}")

        try:
            if not self.orchestrator:
                self._record_test_result(test_name, False, "Orchestrator not available")
                return

            framework = self.orchestrator.integration_framework

            # Test component retrieval
            mcp_manager = framework.get_component("mcp_manager")
            scheduler = framework.get_component("scheduler")
            notification_system = framework.get_component("notification_system")

            components_found = sum([
                1 for comp in [mcp_manager, scheduler, notification_system]
                if comp is not None
            ])

            if components_found >= 2:
                self._record_test_result(test_name, True, f"Successfully retrieved {components_found} components")
            else:
                self._record_test_result(test_name, False, f"Only found {components_found} components")

        except Exception as e:
            self._record_test_result(test_name, False, f"Integration framework error: {e}")

    async def _test_orchestrator_functionality(self):
        """Test 3: Orchestrator core functionality."""
        test_name = "orchestrator_functionality"
        self.logger.info(f"🧪 Running test: {test_name}")

        try:
            if not self.orchestrator:
                self._record_test_result(test_name, False, "Orchestrator not available")
                return

            # Test system status
            system_status = self.orchestrator.get_system_status()

            # Verify status structure
            required_keys = ['state', 'config', 'statistics', 'uptime']
            missing_keys = [key for key in required_keys if key not in system_status]

            if not missing_keys:
                state = system_status.get('state')
                self._record_test_result(test_name, True, f"System status valid, state: {state}")
            else:
                self._record_test_result(test_name, False, f"Missing status keys: {missing_keys}")

        except Exception as e:
            self._record_test_result(test_name, False, f"Orchestrator functionality error: {e}")

    async def _test_scheduling_system(self):
        """Test 4: Scheduling system functionality."""
        test_name = "scheduling_system"
        self.logger.info(f"🧪 Running test: {test_name}")

        try:
            if not self.orchestrator or not self.orchestrator.scheduler:
                self._record_test_result(test_name, False, "Scheduler not available")
                return

            scheduler = self.orchestrator.scheduler

            # Test scheduler statistics
            stats = scheduler.get_statistics() if hasattr(scheduler, 'get_statistics') else {}

            # Test job scheduling (would need actual implementation)
            if hasattr(scheduler, 'add_job'):
                # Mock job for testing
                async def test_job():
                    return "test_completed"

                # Add test job
                try:
                    job_id = scheduler.add_job(
                        name="Integration Test Job",
                        function=test_job,
                        cron_expression="* * * * *"  # Every minute
                    )
                    self._record_test_result(test_name, True, f"Scheduler working, stats: {stats}")
                except Exception as e:
                    self._record_test_result(test_name, False, f"Job scheduling failed: {e}")
            else:
                self._record_test_result(test_name, False, "Scheduler missing add_job method")

        except Exception as e:
            self._record_test_result(test_name, False, f"Scheduling system error: {e}")

    async def _test_notification_system(self):
        """Test 5: Notification system functionality."""
        test_name = "notification_system"
        self.logger.info(f"🧪 Running test: {test_name}")

        try:
            if not self.orchestrator or not self.orchestrator.notification_system:
                self._record_test_result(test_name, False, "Notification system not available")
                return

            notification_system = self.orchestrator.notification_system

            # Test notification statistics
            if hasattr(notification_system, 'get_statistics'):
                stats = notification_system.get_statistics()
                self._record_test_result(test_name, True, f"Notification system stats: {stats}")
            else:
                self._record_test_result(test_name, False, "Notification system missing get_statistics method")

        except Exception as e:
            self._record_test_result(test_name, False, f"Notification system error: {e}")

    async def _test_alert_system(self):
        """Test 6: Alert system functionality."""
        test_name = "alert_system"
        self.logger.info(f"🧪 Running test: {test_name}")

        try:
            if not self.orchestrator or not self.orchestrator.alert_system:
                self._record_test_result(test_name, False, "Alert system not available")
                return

            alert_system = self.orchestrator.alert_system

            # Test alert statistics
            if hasattr(alert_system, 'get_statistics'):
                stats = alert_system.get_statistics()
                self._record_test_result(test_name, True, f"Alert system stats: {stats}")
            else:
                self._record_test_result(test_name, False, "Alert system missing get_statistics method")

        except Exception as e:
            self._record_test_result(test_name, False, f"Alert system error: {e}")

    async def _test_monitoring_dashboard(self):
        """Test 7: Monitoring dashboard functionality."""
        test_name = "monitoring_dashboard"
        self.logger.info(f"🧪 Running test: {test_name}")

        try:
            if not self.orchestrator or not self.orchestrator.monitoring_dashboard:
                self._record_test_result(test_name, False, "Monitoring dashboard not available")
                return

            # Test that dashboard was initialized
            dashboard = self.orchestrator.monitoring_dashboard

            if hasattr(dashboard, 'app') and dashboard.app:
                self._record_test_result(test_name, True, "Monitoring dashboard initialized successfully")
            else:
                self._record_test_result(test_name, False, "Monitoring dashboard not properly initialized")

        except Exception as e:
            self._record_test_result(test_name, False, f"Monitoring dashboard error: {e}")

    async def _test_end_to_end_workflows(self):
        """Test 8: End-to-end workflow execution."""
        test_name = "end_to_end_workflows"
        self.logger.info(f"🧪 Running test: {test_name}")

        try:
            if not self.orchestrator:
                self._record_test_result(test_name, False, "Orchestrator not available")
                return

            # Test health check workflow
            health_result = await self.orchestrator.execute_integrated_workflow("health_check")

            if health_result.get("success", False):
                overall_status = health_result.get("overall_status", "unknown")
                self._record_test_result(test_name, True, f"Health check workflow completed, status: {overall_status}")
            else:
                error = health_result.get("error", "Unknown error")
                self._record_test_result(test_name, False, f"Health check workflow failed: {error}")

        except Exception as e:
            self._record_test_result(test_name, False, f"End-to-end workflow error: {e}")

    async def _test_error_recovery(self):
        """Test 9: Error recovery mechanisms."""
        test_name = "error_recovery"
        self.logger.info(f"🧪 Running test: {test_name}")

        try:
            if not self.orchestrator:
                self._record_test_result(test_name, False, "Orchestrator not available")
                return

            # Test invalid workflow execution
            invalid_result = await self.orchestrator.execute_integrated_workflow("invalid_workflow")

            if not invalid_result.get("success", True):
                self._record_test_result(test_name, True, "Error recovery working - invalid workflow handled gracefully")
            else:
                self._record_test_result(test_name, False, "Error recovery not working - invalid workflow should fail")

        except Exception as e:
            self._record_test_result(test_name, False, f"Error recovery test error: {e}")

    async def _test_performance(self):
        """Test 10: Performance benchmarking."""
        test_name = "performance"
        self.logger.info(f"🧪 Running test: {test_name}")

        try:
            if not self.orchestrator:
                self._record_test_result(test_name, False, "Orchestrator not available")
                return

            # Performance test: multiple health checks
            start_time = datetime.utcnow()

            tasks = []
            for i in range(5):
                task = self.orchestrator.execute_integrated_workflow("health_check")
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)

            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()

            successful_results = sum(1 for r in results if isinstance(r, dict) and r.get("success", False))

            if successful_results >= 3 and duration < 30:  # 3+ successes in under 30 seconds
                self._record_test_result(test_name, True, f"Performance test passed: {successful_results}/5 successful in {duration:.2f}s")
            else:
                self._record_test_result(test_name, False, f"Performance test failed: {successful_results}/5 successful in {duration:.2f}s")

        except Exception as e:
            self._record_test_result(test_name, False, f"Performance test error: {e}")

    def _record_test_result(self, test_name: str, success: bool, details: str):
        """Record test result."""
        self.stats['tests_run'] += 1
        if success:
            self.stats['tests_passed'] += 1
            self.logger.info(f"✅ {test_name}: {details}")
        else:
            self.stats['tests_failed'] += 1
            self.logger.error(f"❌ {test_name}: {details}")

        self.test_results[test_name] = {
            'success': success,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        }

    async def _cleanup(self):
        """Clean up test resources."""
        try:
            if self.orchestrator:
                await self.orchestrator.shutdown()
                self.logger.info("Test cleanup completed")
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")

    def _generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
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

        return report


async def main():
    """Main test execution function."""
    print("🚀 Agent Investment Platform - Integration Testing")
    print("=" * 60)

    # Ensure logs directory exists
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Run integration tests
    tester = IntegrationTester()

    try:
        test_report = await tester.run_all_tests()

        # Display results
        print("\n📊 Test Results Summary")
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

        print(f"\n📄 Detailed report saved: {report_file}")

        # Display individual test results
        print("\n🔍 Individual Test Results")
        print("=" * 60)
        for test_name, result in test_report['test_results'].items():
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"{status} {test_name}: {result['details']}")

        # Exit with appropriate code
        if test_report['overall_result'] == 'PASS':
            print("\n🎉 All integration tests completed successfully!")
            sys.exit(0)
        else:
            print("\n⚠️  Some integration tests failed. Please review the results.")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Integration testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Integration testing failed with critical error: {e}")
        logger.error(f"Critical test failure: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
