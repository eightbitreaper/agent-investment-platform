"""
Comprehensive health monitoring system for the Agent Investment Platform.

This module provides:
- Health checks for all platform components
- Metrics collection and aggregation
- Alerting based on health status
- Real-time health monitoring dashboard
"""

import asyncio
import json
import time
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import aiohttp
import socket

from ..logging.core import get_logger
from ..logging.aggregation import get_log_aggregator
from ..logging.config import get_config_loader


@dataclass
class HealthStatus:
    """Health status for a component."""
    name: str
    status: str  # healthy, warning, critical, unknown
    message: str
    details: Dict[str, Any]
    last_check: datetime
    response_time_ms: Optional[float] = None


@dataclass
class SystemMetrics:
    """System-level metrics."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_total_mb: float
    disk_usage_percent: float
    disk_free_gb: float
    network_connections: int
    process_count: int


class HealthChecker:
    """Health checker for platform components."""

    def __init__(self):
        self.logger = get_logger(__name__, "health_monitor")
        self.session: Optional[aiohttp.ClientSession] = None
        self.checks: Dict[str, HealthStatus] = {}
        self.metrics_history: List[SystemMetrics] = []
        self.max_history = 1000  # Keep last 1000 metrics

    async def start(self):
        """Start the health checker."""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        self.logger.info("Health checker started")

    async def stop(self):
        """Stop the health checker."""
        if self.session:
            await self.session.close()
            self.session = None
        self.logger.info("Health checker stopped")

    async def check_all_components(self) -> Dict[str, HealthStatus]:
        """Check health of all platform components."""
        if not self.session:
            await self.start()

        # Define components to check
        components = {
            "elasticsearch": self.check_elasticsearch,
            "logstash": self.check_logstash,
            "kibana": self.check_kibana,
            "log_aggregator": self.check_log_aggregator,
            "websocket_server": self.check_websocket_server,
            "mcp_log_server": self.check_mcp_log_server,
            "orchestrator": self.check_orchestrator,
            "mcp_financial_server": self.check_mcp_server("mcp-financial-server", 3000),
            "mcp_analysis_server": self.check_mcp_server("mcp-analysis-server", 3004),
            "mcp_report_server": self.check_mcp_server("mcp-report-server", 3002),
            "postgres": self.check_postgres,
            "redis": self.check_redis,
        }

        # Run all checks concurrently
        tasks = []
        for name, check_func in components.items():
            tasks.append(self.run_health_check(name, check_func))

        await asyncio.gather(*tasks, return_exceptions=True)

        return self.checks

    async def run_health_check(self, name: str, check_func):
        """Run a single health check with timing."""
        start_time = time.time()

        try:
            status = await check_func()
            response_time = (time.time() - start_time) * 1000

            if isinstance(status, HealthStatus):
                status.response_time_ms = response_time
                self.checks[name] = status
            else:
                # Handle legacy return format
                self.checks[name] = HealthStatus(
                    name=name,
                    status=status.get("status", "unknown"),
                    message=status.get("message", ""),
                    details=status.get("details", {}),
                    last_check=datetime.utcnow(),
                    response_time_ms=response_time
                )

        except Exception as e:
            self.logger.error(f"Health check failed for {name}: {e}")
            self.checks[name] = HealthStatus(
                name=name,
                status="critical",
                message=f"Health check failed: {str(e)}",
                details={"error": str(e)},
                last_check=datetime.utcnow(),
                response_time_ms=(time.time() - start_time) * 1000
            )

    async def check_elasticsearch(self) -> HealthStatus:
        """Check Elasticsearch health."""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            async with self.session.get("http://elasticsearch:9200/_cluster/health", timeout=5) as response:
                if response.status == 200:
                    health = await response.json()
                    status = health.get("status", "unknown")

                    health_status = "healthy" if status == "green" else "warning" if status == "yellow" else "critical"

                    return HealthStatus(
                        name="elasticsearch",
                        status=health_status,
                        message=f"Cluster status: {status}",
                        details=health,
                        last_check=datetime.utcnow()
                    )
                else:
                    return HealthStatus(
                        name="elasticsearch",
                        status="critical",
                        message=f"HTTP {response.status}",
                        details={"status_code": response.status},
                        last_check=datetime.utcnow()
                    )

        except Exception as e:
            return HealthStatus(
                name="elasticsearch",
                status="critical",
                message=f"Connection failed: {str(e)}",
                details={"error": str(e)},
                last_check=datetime.utcnow()
            )

    async def check_logstash(self) -> HealthStatus:
        """Check Logstash health."""
        try:
            # Logstash doesn't have a standard health endpoint, so we check if it's listening
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection("logstash", 5000),
                timeout=5
            )
            writer.close()
            await writer.wait_closed()

            return HealthStatus(
                name="logstash",
                status="healthy",
                message="Service is responsive",
                details={"port": 5000},
                last_check=datetime.utcnow()
            )

        except Exception as e:
            return HealthStatus(
                name="logstash",
                status="critical",
                message=f"Connection failed: {str(e)}",
                details={"error": str(e)},
                last_check=datetime.utcnow()
            )

    async def check_kibana(self) -> HealthStatus:
        """Check Kibana health."""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            async with self.session.get("http://kibana:5601/api/status", timeout=10) as response:
                if response.status == 200:
                    status = await response.json()
                    overall_status = status.get("status", {}).get("overall", {}).get("state", "unknown")

                    health_status = "healthy" if overall_status == "green" else "warning" if overall_status == "yellow" else "critical"

                    return HealthStatus(
                        name="kibana",
                        status=health_status,
                        message=f"Overall status: {overall_status}",
                        details=status,
                        last_check=datetime.utcnow()
                    )
                else:
                    return HealthStatus(
                        name="kibana",
                        status="critical",
                        message=f"HTTP {response.status}",
                        details={"status_code": response.status},
                        last_check=datetime.utcnow()
                    )

        except Exception as e:
            return HealthStatus(
                name="kibana",
                status="critical",
                message=f"Connection failed: {str(e)}",
                details={"error": str(e)},
                last_check=datetime.utcnow()
            )

    async def check_log_aggregator(self) -> HealthStatus:
        """Check log aggregator health."""
        try:
            aggregator = await get_log_aggregator()

            if aggregator and aggregator.running:
                # Try to get recent statistics
                stats = await aggregator.get_log_statistics()

                return HealthStatus(
                    name="log_aggregator",
                    status="healthy",
                    message="Aggregator is running and responsive",
                    details={
                        "running": True,
                        "total_logs": stats.get("total", 0)
                    },
                    last_check=datetime.utcnow()
                )
            else:
                return HealthStatus(
                    name="log_aggregator",
                    status="critical",
                    message="Aggregator is not running",
                    details={"running": False},
                    last_check=datetime.utcnow()
                )

        except Exception as e:
            return HealthStatus(
                name="log_aggregator",
                status="critical",
                message=f"Check failed: {str(e)}",
                details={"error": str(e)},
                last_check=datetime.utcnow()
            )

    async def check_websocket_server(self) -> HealthStatus:
        """Check WebSocket server health."""
        try:
            # Try to connect to WebSocket server
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection("log-streaming-server", 8765),
                timeout=5
            )
            writer.close()
            await writer.wait_closed()

            return HealthStatus(
                name="websocket_server",
                status="healthy",
                message="WebSocket server is responsive",
                details={"port": 8765},
                last_check=datetime.utcnow()
            )

        except Exception as e:
            return HealthStatus(
                name="websocket_server",
                status="critical",
                message=f"Connection failed: {str(e)}",
                details={"error": str(e)},
                last_check=datetime.utcnow()
            )

    async def check_mcp_log_server(self) -> HealthStatus:
        """Check MCP log server health."""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            async with self.session.get("http://mcp-log-server:3005/health", timeout=5) as response:
                if response.status == 200:
                    health = await response.json()

                    return HealthStatus(
                        name="mcp_log_server",
                        status="healthy" if health.get("status") == "healthy" else "warning",
                        message=health.get("message", "Service is responsive"),
                        details=health,
                        last_check=datetime.utcnow()
                    )
                else:
                    return HealthStatus(
                        name="mcp_log_server",
                        status="critical",
                        message=f"HTTP {response.status}",
                        details={"status_code": response.status},
                        last_check=datetime.utcnow()
                    )

        except Exception as e:
            return HealthStatus(
                name="mcp_log_server",
                status="critical",
                message=f"Connection failed: {str(e)}",
                details={"error": str(e)},
                last_check=datetime.utcnow()
            )

    def check_mcp_server(self, container_name: str, port: int):
        """Create a health check function for an MCP server."""
        async def check():
            try:
                if not self.session:
                    self.session = aiohttp.ClientSession()
                async with self.session.get(f"http://{container_name}:{port}/health", timeout=5) as response:
                    if response.status == 200:
                        health = await response.json()

                        return HealthStatus(
                            name=container_name,
                            status="healthy",
                            message="Service is responsive",
                            details=health,
                            last_check=datetime.utcnow()
                        )
                    else:
                        return HealthStatus(
                            name=container_name,
                            status="critical",
                            message=f"HTTP {response.status}",
                            details={"status_code": response.status},
                            last_check=datetime.utcnow()
                        )

            except Exception as e:
                return HealthStatus(
                    name=container_name,
                    status="critical",
                    message=f"Connection failed: {str(e)}",
                    details={"error": str(e)},
                    last_check=datetime.utcnow()
                )

        return check

    async def check_orchestrator(self) -> HealthStatus:
        """Check orchestrator health."""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            async with self.session.get("http://agent-investment-platform:8080/health", timeout=5) as response:
                if response.status == 200:
                    return HealthStatus(
                        name="orchestrator",
                        status="healthy",
                        message="Orchestrator is responsive",
                        details={"status_code": response.status},
                        last_check=datetime.utcnow()
                    )
                else:
                    return HealthStatus(
                        name="orchestrator",
                        status="critical",
                        message=f"HTTP {response.status}",
                        details={"status_code": response.status},
                        last_check=datetime.utcnow()
                    )

        except Exception as e:
            return HealthStatus(
                name="orchestrator",
                status="critical",
                message=f"Connection failed: {str(e)}",
                details={"error": str(e)},
                last_check=datetime.utcnow()
            )

    async def check_postgres(self) -> HealthStatus:
        """Check PostgreSQL health."""
        try:
            # Simple connection test
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection("postgres", 5432),
                timeout=5
            )
            writer.close()
            await writer.wait_closed()

            return HealthStatus(
                name="postgres",
                status="healthy",
                message="Database is responsive",
                details={"port": 5432},
                last_check=datetime.utcnow()
            )

        except Exception as e:
            return HealthStatus(
                name="postgres",
                status="critical",
                message=f"Connection failed: {str(e)}",
                details={"error": str(e)},
                last_check=datetime.utcnow()
            )

    async def check_redis(self) -> HealthStatus:
        """Check Redis health."""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection("redis", 6379),
                timeout=5
            )

            # Send PING command
            writer.write(b"PING\r\n")
            await writer.drain()

            response = await reader.read(100)
            writer.close()
            await writer.wait_closed()

            if b"PONG" in response:
                return HealthStatus(
                    name="redis",
                    status="healthy",
                    message="Redis is responsive",
                    details={"port": 6379},
                    last_check=datetime.utcnow()
                )
            else:
                return HealthStatus(
                    name="redis",
                    status="warning",
                    message="Unexpected response from Redis",
                    details={"response": response.decode()},
                    last_check=datetime.utcnow()
                )

        except Exception as e:
            return HealthStatus(
                name="redis",
                status="critical",
                message=f"Connection failed: {str(e)}",
                details={"error": str(e)},
                last_check=datetime.utcnow()
            )

    def collect_system_metrics(self) -> SystemMetrics:
        """Collect system-level metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_mb = memory.used / 1024 / 1024
            memory_total_mb = memory.total / 1024 / 1024

            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_usage_percent = disk.used / disk.total * 100
            disk_free_gb = disk.free / 1024 / 1024 / 1024

            # Network metrics
            network_connections = len(psutil.net_connections())

            # Process metrics
            process_count = len(psutil.pids())

            metrics = SystemMetrics(
                timestamp=datetime.utcnow(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_used_mb=memory_used_mb,
                memory_total_mb=memory_total_mb,
                disk_usage_percent=disk_usage_percent,
                disk_free_gb=disk_free_gb,
                network_connections=network_connections,
                process_count=process_count
            )

            # Add to history
            self.metrics_history.append(metrics)

            # Keep only recent history
            if len(self.metrics_history) > self.max_history:
                self.metrics_history = self.metrics_history[-self.max_history:]

            return metrics

        except Exception as e:
            self.logger.error(f"Failed to collect system metrics: {e}")
            return SystemMetrics(
                timestamp=datetime.utcnow(),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_used_mb=0.0,
                memory_total_mb=0.0,
                disk_usage_percent=0.0,
                disk_free_gb=0.0,
                network_connections=0,
                process_count=0
            )

    def get_overall_health(self) -> str:
        """Get overall platform health status."""
        if not self.checks:
            return "unknown"

        statuses = [check.status for check in self.checks.values()]

        if "critical" in statuses:
            return "critical"
        elif "warning" in statuses:
            return "warning"
        elif all(status == "healthy" for status in statuses):
            return "healthy"
        else:
            return "unknown"

    def get_health_summary(self) -> Dict[str, Any]:
        """Get a summary of platform health."""
        overall_status = self.get_overall_health()

        status_counts = {}
        for status in ["healthy", "warning", "critical", "unknown"]:
            status_counts[status] = sum(1 for check in self.checks.values() if check.status == status)

        # Get latest metrics
        latest_metrics = self.metrics_history[-1] if self.metrics_history else None

        return {
            "overall_status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "component_count": len(self.checks),
            "status_distribution": status_counts,
            "components": {name: asdict(check) for name, check in self.checks.items()},
            "system_metrics": asdict(latest_metrics) if latest_metrics else None
        }


class HealthMonitoringService:
    """Service for continuous health monitoring."""

    def __init__(self, check_interval: int = 60):
        self.logger = get_logger(__name__, "health_service")
        self.checker = HealthChecker()
        self.check_interval = check_interval
        self.running = False
        self.monitor_task: Optional[asyncio.Task] = None

    async def start(self):
        """Start the health monitoring service."""
        if self.running:
            return

        await self.checker.start()
        self.running = True
        self.monitor_task = asyncio.create_task(self._monitor_loop())

        self.logger.info(f"Health monitoring service started (check interval: {self.check_interval}s)")

    async def stop(self):
        """Stop the health monitoring service."""
        if not self.running:
            return

        self.running = False

        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass

        await self.checker.stop()
        self.logger.info("Health monitoring service stopped")

    async def _monitor_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                # Run health checks
                await self.checker.check_all_components()

                # Collect system metrics
                self.checker.collect_system_metrics()

                # Log overall health status
                summary = self.checker.get_health_summary()
                self.logger.info(f"Health check completed - Overall status: {summary['overall_status']}")

                # Check for critical issues
                critical_components = [
                    name for name, check in self.checker.checks.items()
                    if check.status == "critical"
                ]

                if critical_components:
                    self.logger.error(f"Critical health issues detected in: {', '.join(critical_components)}")

                # Wait for next check
                await asyncio.sleep(self.check_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in health monitoring loop: {e}", exc_info=True)
                await asyncio.sleep(self.check_interval)

    def get_current_health(self) -> Dict[str, Any]:
        """Get current health status."""
        return self.checker.get_health_summary()

    def get_metrics_history(self, hours: int = 24) -> List[SystemMetrics]:
        """Get system metrics history."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return [
            metrics for metrics in self.checker.metrics_history
            if metrics.timestamp >= cutoff_time
        ]


# Global health monitoring service
_health_service = None


async def get_health_service() -> HealthMonitoringService:
    """Get global health monitoring service."""
    global _health_service
    if _health_service is None:
        _health_service = HealthMonitoringService()
        await _health_service.start()
    return _health_service


async def shutdown_health_service():
    """Shutdown global health monitoring service."""
    global _health_service
    if _health_service:
        await _health_service.stop()
        _health_service = None


if __name__ == "__main__":
    """Test the health monitoring system."""

    async def test_health_monitoring():
        try:
            service = await get_health_service()

            # Wait for a few health checks
            for i in range(3):
                await asyncio.sleep(10)
                health = service.get_current_health()
                print(f"\nHealth Check {i+1}:")
                print(f"Overall Status: {health['overall_status']}")
                print(f"Components: {health['status_distribution']}")

                if health['system_metrics']:
                    metrics = health['system_metrics']
                    print(f"CPU: {metrics['cpu_percent']:.1f}%")
                    print(f"Memory: {metrics['memory_percent']:.1f}%")
                    print(f"Disk: {metrics['disk_usage_percent']:.1f}%")

        finally:
            await shutdown_health_service()

    asyncio.run(test_health_monitoring())
