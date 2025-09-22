#!/usr/bin/env python3
"""
Agent Investment Platform - Component Integration Framework

This module provides the integration framework to connect all platform
components for end-to-end automated workflows including MCP servers,
analysis engines, report generators, notifications, and monitoring.

Key Features:
- Component discovery and auto-registration
- Service lifecycle management and health checks
- Inter-component communication and data flow
- Workflow orchestration and task coordination
- Error propagation and recovery mechanisms
- Performance monitoring and metrics collection
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from pathlib import Path
import json
from dataclasses import dataclass, field
from enum import Enum
import importlib
import inspect


class ComponentStatus(Enum):
    """Component status enumeration."""
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    ERROR = "error"
    STOPPING = "stopping"
    STOPPED = "stopped"


class ComponentType(Enum):
    """Component type enumeration."""
    MCP_SERVER = "mcp_server"
    ANALYSIS_ENGINE = "analysis_engine"
    REPORT_GENERATOR = "report_generator"
    NOTIFICATION_SYSTEM = "notification_system"
    ALERT_SYSTEM = "alert_system"
    MONITORING_SYSTEM = "monitoring_system"
    SCHEDULER = "scheduler"
    RISK_MANAGEMENT = "risk_management"


@dataclass
class ComponentInfo:
    """Information about a registered component."""
    name: str
    component_type: ComponentType
    instance: Any
    status: ComponentStatus = ComponentStatus.INITIALIZING
    dependencies: List[str] = field(default_factory=list)
    provides: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)
    health_check_method: Optional[str] = None
    startup_method: Optional[str] = None
    shutdown_method: Optional[str] = None
    last_health_check: Optional[datetime] = None
    error_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class IntegrationFramework:
    """
    Main integration framework for connecting all platform components.

    Manages component lifecycle, dependencies, health monitoring, and
    provides unified interface for inter-component communication.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.components: Dict[str, ComponentInfo] = {}
        self.component_graph: Dict[str, List[str]] = {}
        self.running = False
        self.health_check_task: Optional[asyncio.Task] = None

        # Event system for component communication
        self.event_handlers: Dict[str, List[Callable]] = {}

        # Statistics
        self.stats = {
            'components_registered': 0,
            'components_started': 0,
            'health_checks_performed': 0,
            'errors_handled': 0,
            'events_processed': 0
        }

    def register_component(
        self,
        name: str,
        instance: Any,
        component_type: ComponentType,
        dependencies: Optional[List[str]] = None,
        provides: Optional[List[str]] = None,
        config: Optional[Dict[str, Any]] = None,
        health_check_method: Optional[str] = None,
        startup_method: Optional[str] = None,
        shutdown_method: Optional[str] = None
    ) -> bool:
        """
        Register a component with the integration framework.

        Args:
            name: Unique component name
            instance: Component instance
            component_type: Type of component
            dependencies: List of component names this depends on
            provides: List of services this component provides
            config: Component configuration
            health_check_method: Method name for health checks
            startup_method: Method name for startup
            shutdown_method: Method name for shutdown

        Returns:
            True if registration successful
        """
        try:
            if name in self.components:
                self.logger.warning(f"Component {name} already registered, updating...")

            component_info = ComponentInfo(
                name=name,
                component_type=component_type,
                instance=instance,
                dependencies=dependencies or [],
                provides=provides or [],
                config=config or {},
                health_check_method=health_check_method,
                startup_method=startup_method,
                shutdown_method=shutdown_method
            )

            self.components[name] = component_info
            self.stats['components_registered'] += 1

            # Validate component has required methods
            self._validate_component_methods(component_info)

            self.logger.info(f"Registered component: {name} ({component_type.value})")
            return True

        except Exception as e:
            self.logger.error(f"Failed to register component {name}: {e}")
            return False

    def get_component(self, name: str) -> Optional[Any]:
        """Get a component instance by name."""
        if name in self.components:
            return self.components[name].instance
        return None

    def get_components_by_type(self, component_type: ComponentType) -> List[Any]:
        """Get all components of a specific type."""
        return [
            info.instance for info in self.components.values()
            if info.component_type == component_type
        ]

    async def start_all_components(self) -> bool:
        """Start all registered components in dependency order."""
        try:
            self.logger.info("Starting all components...")

            # Build dependency graph
            self._build_dependency_graph()

            # Get startup order based on dependencies
            startup_order = self._get_startup_order()

            # Start components in order
            for component_name in startup_order:
                success = await self._start_component(component_name)
                if not success:
                    self.logger.error(f"Failed to start component: {component_name}")
                    return False

            self.running = True

            # Start health monitoring
            self.health_check_task = asyncio.create_task(self._health_check_loop())

            self.logger.info(f"Successfully started {len(startup_order)} components")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start components: {e}")
            return False

    async def stop_all_components(self) -> bool:
        """Stop all components in reverse dependency order."""
        try:
            self.logger.info("Stopping all components...")
            self.running = False

            # Stop health monitoring
            if self.health_check_task:
                self.health_check_task.cancel()
                try:
                    await self.health_check_task
                except asyncio.CancelledError:
                    pass

            # Get shutdown order (reverse of startup)
            startup_order = self._get_startup_order()
            shutdown_order = list(reversed(startup_order))

            # Stop components in order
            for component_name in shutdown_order:
                await self._stop_component(component_name)

            self.logger.info("All components stopped")
            return True

        except Exception as e:
            self.logger.error(f"Failed to stop components: {e}")
            return False

    async def emit_event(self, event_name: str, data: Dict[str, Any], source: str = "unknown"):
        """Emit an event to all registered handlers."""
        try:
            if event_name not in self.event_handlers:
                return

            self.logger.debug(f"Emitting event: {event_name} from {source}")

            # Call all handlers for this event
            for handler in self.event_handlers[event_name]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(data, source)
                    else:
                        handler(data, source)
                except Exception as e:
                    self.logger.error(f"Event handler error for {event_name}: {e}")

            self.stats['events_processed'] += 1

        except Exception as e:
            self.logger.error(f"Failed to emit event {event_name}: {e}")

    def subscribe_to_event(self, event_name: str, handler: Callable):
        """Subscribe to an event."""
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []

        self.event_handlers[event_name].append(handler)
        self.logger.debug(f"Subscribed to event: {event_name}")

    async def execute_workflow(self, workflow_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a predefined workflow using registered components."""
        try:
            self.logger.info(f"Executing workflow: {workflow_name}")

            if workflow_name == "full_analysis":
                return await self._execute_full_analysis_workflow(**kwargs)
            elif workflow_name == "health_check":
                return await self._execute_health_check_workflow()
            elif workflow_name == "emergency_stop":
                return await self._execute_emergency_stop_workflow()
            else:
                raise ValueError(f"Unknown workflow: {workflow_name}")

        except Exception as e:
            self.logger.error(f"Workflow execution failed: {workflow_name} - {e}")
            return {"success": False, "error": str(e)}

    async def _execute_full_analysis_workflow(self, symbols: List[str], **kwargs) -> Dict[str, Any]:
        """Execute full investment analysis workflow."""
        try:
            workflow_results = {
                "workflow": "full_analysis",
                "symbols": symbols,
                "start_time": datetime.utcnow().isoformat(),
                "results": {},
                "success": True
            }

            # Step 1: Get MCP server manager
            mcp_manager = self.get_component("mcp_manager")
            if not mcp_manager:
                raise RuntimeError("MCP Manager not available")

            # Step 2: Fetch market data
            self.logger.info("Fetching market data...")
            market_data = {}
            for symbol in symbols:
                try:
                    # This would use the actual MCP server methods
                    data = await self._fetch_symbol_data(symbol)
                    market_data[symbol] = data
                except Exception as e:
                    self.logger.error(f"Failed to fetch data for {symbol}: {e}")
                    market_data[symbol] = {"error": str(e)}

            workflow_results["results"]["market_data"] = market_data

            # Step 3: Perform analysis
            self.logger.info("Performing analysis...")
            analysis_results = await self._perform_comprehensive_analysis(market_data)
            workflow_results["results"]["analysis"] = analysis_results

            # Step 4: Generate recommendations
            self.logger.info("Generating recommendations...")
            recommendations = await self._generate_investment_recommendations(analysis_results)
            workflow_results["results"]["recommendations"] = recommendations

            # Step 5: Generate report
            self.logger.info("Generating report...")
            report_path = await self._generate_analysis_report(workflow_results)
            workflow_results["results"]["report_path"] = report_path

            # Step 6: Send notifications
            self.logger.info("Sending notifications...")
            notification_results = await self._send_workflow_notifications(workflow_results)
            workflow_results["results"]["notifications"] = notification_results

            # Step 7: Update alerts
            self.logger.info("Processing alerts...")
            alert_results = await self._process_workflow_alerts(workflow_results)
            workflow_results["results"]["alerts"] = alert_results

            workflow_results["end_time"] = datetime.utcnow().isoformat()
            workflow_results["duration_seconds"] = (
                datetime.fromisoformat(workflow_results["end_time"]) -
                datetime.fromisoformat(workflow_results["start_time"])
            ).total_seconds()

            # Emit workflow completion event
            await self.emit_event("workflow_completed", workflow_results, "integration_framework")

            return workflow_results

        except Exception as e:
            self.logger.error(f"Full analysis workflow failed: {e}")
            return {
                "workflow": "full_analysis",
                "success": False,
                "error": str(e),
                "end_time": datetime.utcnow().isoformat()
            }

    async def _fetch_symbol_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch data for a specific symbol using MCP servers."""
        # This would integrate with actual MCP servers
        # For now, return mock data structure
        return {
            "symbol": symbol,
            "price": 100.0,
            "volume": 1000000,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success"
        }

    async def _perform_comprehensive_analysis(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive analysis using analysis engines."""
        analysis_results = {}

        # Get analysis components
        sentiment_analyzer = self.get_component("sentiment_analyzer")
        chart_analyzer = self.get_component("chart_analyzer")
        recommendation_engine = self.get_component("recommendation_engine")

        try:
            # Sentiment analysis
            if sentiment_analyzer:
                sentiment_results = {}
                for symbol, data in market_data.items():
                    if "error" not in data:
                        # Mock sentiment analysis
                        sentiment_results[symbol] = {
                            "sentiment_score": 0.2,
                            "confidence": 0.8,
                            "analysis_time": datetime.utcnow().isoformat()
                        }
                analysis_results["sentiment"] = sentiment_results

            # Technical analysis
            if chart_analyzer:
                technical_results = {}
                for symbol, data in market_data.items():
                    if "error" not in data:
                        # Mock technical analysis
                        technical_results[symbol] = {
                            "trend": "bullish",
                            "rsi": 45.0,
                            "macd": 0.5,
                            "analysis_time": datetime.utcnow().isoformat()
                        }
                analysis_results["technical"] = technical_results

            return analysis_results

        except Exception as e:
            self.logger.error(f"Analysis failed: {e}")
            return {"error": str(e)}

    async def _generate_investment_recommendations(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate investment recommendations."""
        recommendation_engine = self.get_component("recommendation_engine")

        if not recommendation_engine:
            return {"error": "Recommendation engine not available"}

        try:
            # Mock recommendation generation
            recommendations = {}

            if "sentiment" in analysis_results:
                for symbol in analysis_results["sentiment"].keys():
                    recommendations[symbol] = {
                        "action": "HOLD",
                        "confidence": 0.7,
                        "reasoning": "Neutral market conditions",
                        "timestamp": datetime.utcnow().isoformat()
                    }

            return recommendations

        except Exception as e:
            self.logger.error(f"Recommendation generation failed: {e}")
            return {"error": str(e)}

    async def _generate_analysis_report(self, workflow_results: Dict[str, Any]) -> Optional[str]:
        """Generate analysis report."""
        report_generator = self.get_component("report_generator")

        if not report_generator:
            self.logger.error("Report generator not available")
            return None

        try:
            # Mock report generation
            report_filename = f"analysis_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.md"
            report_path = f"reports/{report_filename}"

            # This would use the actual report generator
            self.logger.info(f"Generated report: {report_path}")
            return report_path

        except Exception as e:
            self.logger.error(f"Report generation failed: {e}")
            return None

    async def _send_workflow_notifications(self, workflow_results: Dict[str, Any]) -> Dict[str, Any]:
        """Send notifications for workflow completion."""
        notification_system = self.get_component("notification_system")

        if not notification_system:
            return {"error": "Notification system not available"}

        try:
            # Mock notification sending
            notification_results = {
                "notifications_sent": 1,
                "channels": ["email"],
                "timestamp": datetime.utcnow().isoformat()
            }

            return notification_results

        except Exception as e:
            self.logger.error(f"Notification sending failed: {e}")
            return {"error": str(e)}

    async def _process_workflow_alerts(self, workflow_results: Dict[str, Any]) -> Dict[str, Any]:
        """Process alerts based on workflow results."""
        alert_system = self.get_component("alert_system")

        if not alert_system:
            return {"error": "Alert system not available"}

        try:
            # Mock alert processing
            alert_results = {
                "alerts_triggered": 0,
                "alerts_resolved": 0,
                "timestamp": datetime.utcnow().isoformat()
            }

            return alert_results

        except Exception as e:
            self.logger.error(f"Alert processing failed: {e}")
            return {"error": str(e)}

    async def _execute_health_check_workflow(self) -> Dict[str, Any]:
        """Execute comprehensive health check workflow."""
        try:
            health_results = {
                "workflow": "health_check",
                "timestamp": datetime.utcnow().isoformat(),
                "components": {},
                "overall_status": "healthy"
            }

            unhealthy_components = 0

            for name, component_info in self.components.items():
                try:
                    component_health = await self._check_component_health(component_info)
                    health_results["components"][name] = component_health

                    if component_health["status"] != "healthy":
                        unhealthy_components += 1

                except Exception as e:
                    health_results["components"][name] = {
                        "status": "error",
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    unhealthy_components += 1

            # Determine overall status
            if unhealthy_components == 0:
                health_results["overall_status"] = "healthy"
            elif unhealthy_components < len(self.components) / 2:
                health_results["overall_status"] = "degraded"
            else:
                health_results["overall_status"] = "unhealthy"

            return health_results

        except Exception as e:
            self.logger.error(f"Health check workflow failed: {e}")
            return {
                "workflow": "health_check",
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def _execute_emergency_stop_workflow(self) -> Dict[str, Any]:
        """Execute emergency stop workflow."""
        try:
            self.logger.warning("Executing emergency stop workflow")

            stop_results = {
                "workflow": "emergency_stop",
                "timestamp": datetime.utcnow().isoformat(),
                "components_stopped": [],
                "errors": []
            }

            # Stop all components immediately
            for name, component_info in self.components.items():
                try:
                    await self._stop_component(name)
                    stop_results["components_stopped"].append(name)
                except Exception as e:
                    error_msg = f"Failed to stop {name}: {e}"
                    stop_results["errors"].append(error_msg)
                    self.logger.error(error_msg)

            self.running = False

            return stop_results

        except Exception as e:
            self.logger.error(f"Emergency stop workflow failed: {e}")
            return {
                "workflow": "emergency_stop",
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def _validate_component_methods(self, component_info: ComponentInfo):
        """Validate that component has required methods."""
        instance = component_info.instance

        # Check health check method
        if component_info.health_check_method:
            if not hasattr(instance, component_info.health_check_method):
                self.logger.warning(
                    f"Component {component_info.name} missing health check method: "
                    f"{component_info.health_check_method}"
                )

        # Check startup method
        if component_info.startup_method:
            if not hasattr(instance, component_info.startup_method):
                self.logger.warning(
                    f"Component {component_info.name} missing startup method: "
                    f"{component_info.startup_method}"
                )

        # Check shutdown method
        if component_info.shutdown_method:
            if not hasattr(instance, component_info.shutdown_method):
                self.logger.warning(
                    f"Component {component_info.name} missing shutdown method: "
                    f"{component_info.shutdown_method}"
                )

    def _build_dependency_graph(self):
        """Build component dependency graph."""
        self.component_graph = {}

        for name, component_info in self.components.items():
            self.component_graph[name] = component_info.dependencies

    def _get_startup_order(self) -> List[str]:
        """Get component startup order based on dependencies."""
        # Simple topological sort
        visited = set()
        temp_visited = set()
        order = []

        def visit(node):
            if node in temp_visited:
                raise RuntimeError(f"Circular dependency detected involving {node}")
            if node in visited:
                return

            temp_visited.add(node)

            for dependency in self.component_graph.get(node, []):
                if dependency in self.components:
                    visit(dependency)

            temp_visited.remove(node)
            visited.add(node)
            order.append(node)

        for component_name in self.components.keys():
            if component_name not in visited:
                visit(component_name)

        return order

    async def _start_component(self, component_name: str) -> bool:
        """Start a specific component."""
        try:
            component_info = self.components[component_name]

            if component_info.startup_method:
                method = getattr(component_info.instance, component_info.startup_method)
                if asyncio.iscoroutinefunction(method):
                    await method()
                else:
                    method()

            component_info.status = ComponentStatus.RUNNING
            self.stats['components_started'] += 1

            self.logger.info(f"Started component: {component_name}")
            return True

        except Exception as e:
            self.components[component_name].status = ComponentStatus.ERROR
            self.components[component_name].error_count += 1
            self.logger.error(f"Failed to start component {component_name}: {e}")
            return False

    async def _stop_component(self, component_name: str) -> bool:
        """Stop a specific component."""
        try:
            component_info = self.components[component_name]
            component_info.status = ComponentStatus.STOPPING

            if component_info.shutdown_method:
                method = getattr(component_info.instance, component_info.shutdown_method)
                if asyncio.iscoroutinefunction(method):
                    await method()
                else:
                    method()

            component_info.status = ComponentStatus.STOPPED

            self.logger.info(f"Stopped component: {component_name}")
            return True

        except Exception as e:
            self.components[component_name].status = ComponentStatus.ERROR
            self.logger.error(f"Failed to stop component {component_name}: {e}")
            return False

    async def _health_check_loop(self):
        """Continuous health monitoring loop."""
        while self.running:
            try:
                for component_info in self.components.values():
                    await self._check_component_health(component_info)

                self.stats['health_checks_performed'] += 1
                await asyncio.sleep(60)  # Check every minute

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(30)  # Back off on error

    async def _check_component_health(self, component_info: ComponentInfo) -> Dict[str, Any]:
        """Check health of a specific component."""
        try:
            health_result = {
                "component": component_info.name,
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "response_time_ms": 0
            }

            start_time = datetime.utcnow()

            if component_info.health_check_method:
                method = getattr(component_info.instance, component_info.health_check_method)

                if asyncio.iscoroutinefunction(method):
                    result = await method()
                else:
                    result = method()

                # Interpret health check result
                if isinstance(result, bool):
                    health_result["status"] = "healthy" if result else "unhealthy"
                elif isinstance(result, dict):
                    health_result.update(result)

            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            health_result["response_time_ms"] = response_time

            component_info.last_health_check = datetime.utcnow()

            return health_result

        except Exception as e:
            component_info.error_count += 1
            return {
                "component": component_info.name,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def get_integration_status(self) -> Dict[str, Any]:
        """Get current integration framework status."""
        return {
            "running": self.running,
            "components_registered": len(self.components),
            "component_status": {
                name: {
                    "type": info.component_type.value,
                    "status": info.status.value,
                    "error_count": info.error_count,
                    "last_health_check": info.last_health_check.isoformat() if info.last_health_check else None
                }
                for name, info in self.components.items()
            },
            "statistics": self.stats.copy(),
            "event_handlers": {
                event: len(handlers) for event, handlers in self.event_handlers.items()
            }
        }


# Helper function to create and configure integration framework
def create_integration_framework() -> IntegrationFramework:
    """Create and configure the integration framework with auto-discovery."""
    framework = IntegrationFramework()

    # Auto-register components would be implemented here
    # For now, this is a placeholder for manual registration

    return framework


if __name__ == "__main__":
    """Test the integration framework."""
    import asyncio

    async def test_integration():
        """Test integration framework functionality."""
        # Create framework
        framework = create_integration_framework()

        # Mock component for testing
        class MockComponent:
            def __init__(self, name):
                self.name = name
                self.running = False

            async def start(self):
                self.running = True
                print(f"Started {self.name}")

            async def stop(self):
                self.running = False
                print(f"Stopped {self.name}")

            def health_check(self):
                return {"status": "healthy", "running": self.running}

        # Register test components
        framework.register_component(
            "test_component",
            MockComponent("TestComponent"),
            ComponentType.ANALYSIS_ENGINE,
            startup_method="start",
            shutdown_method="stop",
            health_check_method="health_check"
        )

        # Test workflow
        try:
            # Start components
            await framework.start_all_components()

            # Execute test workflow
            result = await framework.execute_workflow("health_check")
            print(f"Health check result: {json.dumps(result, indent=2)}")

            # Get status
            status = framework.get_integration_status()
            print(f"Framework status: {json.dumps(status, indent=2)}")

        finally:
            # Stop components
            await framework.stop_all_components()

    # Run test
    asyncio.run(test_integration())
