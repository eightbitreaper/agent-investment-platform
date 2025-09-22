#!/usr/bin/env python3
"""
Agent Investment Platform - Integration Example

This script demonstrates the complete integration of all platform components
including scheduler, orchestrator, notifications, alerts, and monitoring.

This serves as both a demonstration and validation of the integration framework.
"""

import asyncio
import logging
import sys
import os
from datetime import datetime
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def demonstrate_integration():
    """Demonstrate the complete integration framework."""
    logger.info("=" * 60)
    logger.info("Agent Investment Platform - Integration Demonstration")
    logger.info("=" * 60)

    try:
        # Step 1: Import and create integration framework
        logger.info("Step 1: Creating Integration Framework...")
        from src.integration.framework import IntegrationFramework, ComponentType

        framework = IntegrationFramework()
        logger.info("Integration framework created successfully")

        # Step 2: Create and register components
        logger.info("\nStep 2: Creating and registering components...")

        # Create scheduler
        from scheduler import JobScheduler, JobPriority
        scheduler = JobScheduler()

        framework.register_component(
            "scheduler",
            scheduler,
            ComponentType.SCHEDULER,
            startup_method="start",
            shutdown_method="stop",
            health_check_method="get_statistics"
        )
        logger.info("Scheduler registered")

        # Create notification system
        from src.notifications.notification_system import NotificationSystem
        notification_system = NotificationSystem()

        framework.register_component(
            "notification_system",
            notification_system,
            ComponentType.NOTIFICATION_SYSTEM,
            startup_method="start",
            shutdown_method="stop",
            health_check_method="get_statistics"
        )
        logger.info("Notification system registered")

        # Create alert system
        from src.alerts.alert_system import IntelligentAlertSystem
        alert_system = IntelligentAlertSystem()
        alert_system.set_external_systems(notification_system=notification_system)

        framework.register_component(
            "alert_system",
            alert_system,
            ComponentType.ALERT_SYSTEM,
            dependencies=["notification_system"]
        )
        logger.info("Alert system registered")

        # Create monitoring dashboard
        from src.monitoring.dashboard import MonitoringDashboard
        monitoring_dashboard = MonitoringDashboard(port=8081)  # Use different port

        framework.register_component(
            "monitoring_dashboard",
            monitoring_dashboard,
            ComponentType.MONITORING_SYSTEM,
            dependencies=["notification_system", "alert_system"]
        )
        logger.info("Monitoring dashboard registered")

        # Step 3: Start all components
        logger.info("\nStep 3: Starting all components...")
        success = await framework.start_all_components()

        if success:
            logger.info("All components started successfully!")
        else:
            logger.error("Failed to start some components")
            return

        # Step 4: Get system status
        logger.info("\nStep 4: Getting system status...")
        status = framework.get_integration_status()

        logger.info(f"Components registered: {status['components_registered']}")
        logger.info(f"Framework running: {status['running']}")

        for name, comp_status in status['component_status'].items():
            logger.info(f"  {name}: {comp_status['status']} (type: {comp_status['type']})")

        # Step 5: Execute test workflow
        logger.info("\nStep 5: Executing health check workflow...")
        health_result = await framework.execute_workflow("health_check")

        if health_result.get("success", False):
            logger.info(f"Health check completed: {health_result.get('overall_status', 'unknown')}")
        else:
            logger.warning(f"Health check failed: {health_result.get('error', 'unknown error')}")

        # Step 6: Test event system
        logger.info("\nStep 6: Testing event system...")

        # Subscribe to events
        def event_handler(data, source):
            logger.info(f"Event received from {source}: {data.get('message', 'no message')}")

        framework.subscribe_to_event("test_event", event_handler)

        # Emit test event
        await framework.emit_event("test_event", {"message": "Integration test successful"}, "demo")

        # Step 7: Wait briefly to see events
        logger.info("\nStep 7: Running for 10 seconds to demonstrate operation...")
        await asyncio.sleep(10)

        # Step 8: Generate final statistics
        logger.info("\nStep 8: Final statistics...")
        final_status = framework.get_integration_status()
        statistics = final_status['statistics']

        logger.info(f"Events processed: {statistics.get('events_processed', 0)}")
        logger.info(f"Health checks performed: {statistics.get('health_checks_performed', 0)}")

        # Step 9: Clean shutdown
        logger.info("\nStep 9: Shutting down all components...")
        await framework.stop_all_components()
        logger.info("All components shut down successfully")

        logger.info("\n" + "=" * 60)
        logger.info("Integration demonstration completed successfully!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Integration demonstration failed: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Main function."""
    try:
        await demonstrate_integration()
        print("\nIntegration demonstration completed successfully!")

    except KeyboardInterrupt:
        print("\nIntegration demonstration interrupted by user")
    except Exception as e:
        print(f"\nIntegration demonstration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
