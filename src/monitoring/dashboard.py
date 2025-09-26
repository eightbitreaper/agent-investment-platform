#!/usr/bin/env python3
"""
Agent Investment Platform - System Monitoring Dashboard

This module provides a comprehensive web-based monitoring interface for tracking
component health, performance metrics, analysis success rates, and system status.

Key Features:
- Real-time system health monitoring and alerts
- Performance metrics visualization and tracking
- Component status dashboard with detailed diagnostics
- Analysis success rate monitoring and trending
- Interactive web interface with live updates
- Historical data tracking and reporting
- Alert system integration and notification status
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import time
from dataclasses import dataclass, asdict
from enum import Enum

# Web framework imports
try:
    from fastapi import FastAPI, WebSocket, HTTPException, BackgroundTasks
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import HTMLResponse, JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    WEB_AVAILABLE = True
except ImportError:
    WEB_AVAILABLE = False
    FastAPI = WebSocket = HTTPException = BackgroundTasks = None
    StaticFiles = HTMLResponse = JSONResponse = CORSMiddleware = None
    uvicorn = None


class ComponentStatus(Enum):
    """Component status enumeration."""
    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


@dataclass
class SystemMetrics:
    """System performance metrics."""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    active_connections: int
    uptime_seconds: float

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result


@dataclass
class ComponentHealth:
    """Individual component health status."""
    name: str
    status: ComponentStatus
    last_check: datetime
    response_time_ms: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        from enum import Enum

        def serialize_value(value):
            """Recursively serialize values, handling enums."""
            if isinstance(value, Enum):
                return value.value
            elif isinstance(value, list):
                return [serialize_value(item) for item in value]
            elif isinstance(value, dict):
                return {k: serialize_value(v) for k, v in value.items()}
            elif hasattr(value, '__dict__'):
                # Handle objects with __dict__ (like dataclasses)
                return {k: serialize_value(v) for k, v in value.__dict__.items()}
            else:
                return value

        result = asdict(self)
        result['status'] = self.status.value
        result['last_check'] = self.last_check.isoformat()
        result['metadata'] = serialize_value(self.metadata or {})
        return result


@dataclass
class AnalysisMetrics:
    """Analysis performance metrics."""
    timestamp: datetime
    reports_generated: int
    analyses_completed: int
    success_rate: float
    average_execution_time: float
    failed_analyses: int
    queue_size: int

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result


class MonitoringDataCollector:
    """Collects monitoring data from various system components."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics_history: List[SystemMetrics] = []
        self.component_health: Dict[str, ComponentHealth] = {}
        self.analysis_metrics: List[AnalysisMetrics] = []
        self.max_history_size = 1000

        # Component references (set by external systems)
        self.orchestrator = None
        self.scheduler = None
        self.notification_system = None
        self.mcp_manager = None

    def set_components(self, **components):
        """Set references to system components for monitoring."""
        for name, component in components.items():
            setattr(self, name, component)
            self.logger.info(f"Monitoring component registered: {name}")

    async def collect_system_metrics(self) -> SystemMetrics:
        """Collect current system performance metrics."""
        try:
            import psutil

            # Get system metrics
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()

            metrics = SystemMetrics(
                timestamp=datetime.utcnow(),
                cpu_usage=cpu_usage,
                memory_usage=memory.percent,
                disk_usage=(disk.used / disk.total) * 100,
                network_io={
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },
                active_connections=len(psutil.net_connections()),
                uptime_seconds=time.time() - psutil.boot_time()
            )

            # Store in history
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > self.max_history_size:
                self.metrics_history = self.metrics_history[-self.max_history_size:]

            return metrics

        except ImportError:
            # Fallback if psutil not available
            return SystemMetrics(
                timestamp=datetime.utcnow(),
                cpu_usage=0.0,
                memory_usage=0.0,
                disk_usage=0.0,
                network_io={},
                active_connections=0,
                uptime_seconds=0.0
            )
        except Exception as e:
            self.logger.error(f"Failed to collect system metrics: {e}")
            return SystemMetrics(
                timestamp=datetime.utcnow(),
                cpu_usage=-1.0,  # Indicates error
                memory_usage=-1.0,
                disk_usage=-1.0,
                network_io={},
                active_connections=0,
                uptime_seconds=0.0
            )

    async def check_component_health(self) -> Dict[str, ComponentHealth]:
        """Check health of all monitored components."""
        health_results = {}

        # Check orchestrator
        if self.orchestrator:
            health_results['orchestrator'] = await self._check_orchestrator_health()

        # Check scheduler
        if self.scheduler:
            health_results['scheduler'] = await self._check_scheduler_health()

        # Check notification system
        if self.notification_system:
            health_results['notification_system'] = await self._check_notification_health()

        # Check MCP manager
        if self.mcp_manager:
            health_results['mcp_manager'] = await self._check_mcp_health()

        # Update stored health status
        self.component_health.update(health_results)

        return health_results

    async def collect_analysis_metrics(self) -> AnalysisMetrics:
        """Collect analysis performance metrics."""
        try:
            # Get metrics from orchestrator if available
            if self.orchestrator:
                stats = self.orchestrator.get_statistics() if hasattr(self.orchestrator, 'get_statistics') else {}

                metrics = AnalysisMetrics(
                    timestamp=datetime.utcnow(),
                    reports_generated=stats.get('reports_generated', 0),
                    analyses_completed=stats.get('analyses_completed', 0),
                    success_rate=self._calculate_success_rate(stats),
                    average_execution_time=self._calculate_avg_execution_time(stats),
                    failed_analyses=stats.get('errors_encountered', 0),
                    queue_size=self._get_queue_size()
                )
            else:
                metrics = AnalysisMetrics(
                    timestamp=datetime.utcnow(),
                    reports_generated=0,
                    analyses_completed=0,
                    success_rate=0.0,
                    average_execution_time=0.0,
                    failed_analyses=0,
                    queue_size=0
                )

            # Store in history
            self.analysis_metrics.append(metrics)
            if len(self.analysis_metrics) > self.max_history_size:
                self.analysis_metrics = self.analysis_metrics[-self.max_history_size:]

            return metrics

        except Exception as e:
            self.logger.error(f"Failed to collect analysis metrics: {e}")
            return AnalysisMetrics(
                timestamp=datetime.utcnow(),
                reports_generated=0,
                analyses_completed=0,
                success_rate=0.0,
                average_execution_time=0.0,
                failed_analyses=0,
                queue_size=0
            )

    async def _check_orchestrator_health(self) -> ComponentHealth:
        """Check orchestrator component health."""
        start_time = time.time()

        try:
            # Try to get orchestrator status
            if self.orchestrator and hasattr(self.orchestrator, 'get_system_status'):
                status_info = self.orchestrator.get_system_status()
                response_time = (time.time() - start_time) * 1000

                # Determine status based on orchestrator state
                if status_info and status_info.get('state') == 'running':
                    status = ComponentStatus.HEALTHY
                elif status_info and status_info.get('state') in ['error', 'stopped']:
                    status = ComponentStatus.ERROR
                else:
                    status = ComponentStatus.WARNING

                return ComponentHealth(
                    name='orchestrator',
                    status=status,
                    last_check=datetime.utcnow(),
                    response_time_ms=response_time,
                    metadata=status_info or {}
                )
            else:
                return ComponentHealth(
                    name='orchestrator',
                    status=ComponentStatus.UNKNOWN,
                    last_check=datetime.utcnow(),
                    error_message="No status method available"
                )

        except Exception as e:
            return ComponentHealth(
                name='orchestrator',
                status=ComponentStatus.ERROR,
                last_check=datetime.utcnow(),
                error_message=str(e)
            )

    async def _check_scheduler_health(self) -> ComponentHealth:
        """Check scheduler component health."""
        start_time = time.time()

        try:
            if self.scheduler and hasattr(self.scheduler, 'is_running') and hasattr(self.scheduler, 'get_statistics'):
                is_running = self.scheduler.is_running()
                stats = self.scheduler.get_statistics()
                response_time = (time.time() - start_time) * 1000

                status = ComponentStatus.HEALTHY if is_running else ComponentStatus.ERROR

                return ComponentHealth(
                    name='scheduler',
                    status=status,
                    last_check=datetime.utcnow(),
                    response_time_ms=response_time,
                    metadata=stats or {}
                )
            else:
                return ComponentHealth(
                    name='scheduler',
                    status=ComponentStatus.UNKNOWN,
                    last_check=datetime.utcnow(),
                    error_message="Scheduler methods not available"
                )

        except Exception as e:
            return ComponentHealth(
                name='scheduler',
                status=ComponentStatus.ERROR,
                last_check=datetime.utcnow(),
                error_message=str(e)
            )

    async def _check_notification_health(self) -> ComponentHealth:
        """Check notification system health."""
        start_time = time.time()

        try:
            if self.notification_system and hasattr(self.notification_system, 'get_statistics'):
                stats = self.notification_system.get_statistics()
                response_time = (time.time() - start_time) * 1000

                # Check if there are recent failures
                stats = stats or {}
                failure_rate = stats.get('messages_failed', 0) / max(stats.get('messages_sent', 1), 1)

                if failure_rate > 0.5:
                    status = ComponentStatus.ERROR
                elif failure_rate > 0.1:
                    status = ComponentStatus.WARNING
                else:
                    status = ComponentStatus.HEALTHY

                return ComponentHealth(
                    name='notification_system',
                    status=status,
                    last_check=datetime.utcnow(),
                    response_time_ms=response_time,
                    metadata=stats
                )
            else:
                return ComponentHealth(
                    name='notification_system',
                    status=ComponentStatus.UNKNOWN,
                    last_check=datetime.utcnow(),
                    error_message="Statistics method not available"
                )

        except Exception as e:
            return ComponentHealth(
                name='notification_system',
                status=ComponentStatus.ERROR,
                last_check=datetime.utcnow(),
                error_message=str(e)
            )

    async def _check_mcp_health(self) -> ComponentHealth:
        """Check MCP manager health."""
        start_time = time.time()

        try:
            if self.mcp_manager and hasattr(self.mcp_manager, 'get_server_status'):
                server_status = self.mcp_manager.get_server_status()
                response_time = (time.time() - start_time) * 1000

                # Check if all servers are running
                if server_status is None:
                    server_status = {}

                try:
                    if not server_status:
                        all_healthy = True  # No servers configured
                    else:
                        all_healthy = True
                        for status in server_status.values():
                            if isinstance(status, dict) and status.get('status') != 'running':
                                all_healthy = False
                                break
                except (AttributeError, TypeError):
                    all_healthy = False

                status = ComponentStatus.HEALTHY if all_healthy else ComponentStatus.WARNING

                return ComponentHealth(
                    name='mcp_manager',
                    status=status,
                    last_check=datetime.utcnow(),
                    response_time_ms=response_time,
                    metadata={'servers': server_status}
                )
            else:
                return ComponentHealth(
                    name='mcp_manager',
                    status=ComponentStatus.UNKNOWN,
                    last_check=datetime.utcnow(),
                    error_message="Server status method not available"
                )

        except Exception as e:
            return ComponentHealth(
                name='mcp_manager',
                status=ComponentStatus.ERROR,
                last_check=datetime.utcnow(),
                error_message=str(e)
            )

    def _calculate_success_rate(self, stats: Dict[str, Any]) -> float:
        """Calculate analysis success rate."""
        completed = stats.get('analyses_completed', 0)
        failed = stats.get('errors_encountered', 0)
        total = completed + failed

        if total == 0:
            return 100.0

        return (completed / total) * 100.0

    def _calculate_avg_execution_time(self, stats: Dict[str, Any]) -> float:
        """Calculate average execution time."""
        # This would need to be implemented based on actual timing data
        return 0.0  # Placeholder

    def _get_queue_size(self) -> int:
        """Get current analysis queue size."""
        if self.scheduler and hasattr(self.scheduler, 'queue_size'):
            return self.scheduler.queue_size()
        return 0

    def get_historical_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """Get historical metrics for the specified time period."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        # Filter metrics by time
        recent_system_metrics = [
            m.to_dict() for m in self.metrics_history
            if m.timestamp > cutoff_time
        ]

        recent_analysis_metrics = [
            m.to_dict() for m in self.analysis_metrics
            if m.timestamp > cutoff_time
        ]

        return {
            'system_metrics': recent_system_metrics,
            'analysis_metrics': recent_analysis_metrics,
            'component_health': {k: v.to_dict() for k, v in self.component_health.items()}
        }


class MonitoringDashboard:
    """Web-based monitoring dashboard."""

    def __init__(self, port: int = 8080, host: str = "0.0.0.0"):
        self.port = port
        self.host = host
        self.logger = logging.getLogger(__name__)
        self.data_collector = MonitoringDataCollector()
        self.connected_clients = []  # List[WebSocket] - avoid type annotation issues

        if not WEB_AVAILABLE:
            self.logger.error("Web framework not available - monitoring dashboard disabled")
            self.app = None
            return

        # Initialize FastAPI app
        if FastAPI is None:
            self.logger.error("FastAPI not available")
            self.app = None
            return

        self.app = FastAPI(title="Agent Investment Platform Monitor", version="1.0.0")

        # Add CORS middleware
        if CORSMiddleware is not None:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

        self._setup_routes()

    def set_components(self, **components):
        """Set system components for monitoring."""
        self.data_collector.set_components(**components)

    def _json_encoder(self, obj):
        """Custom JSON encoder to handle enums and other non-serializable objects."""
        if isinstance(obj, Enum):
            return obj.value
        elif hasattr(obj, 'isoformat'):  # datetime objects
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):  # objects with __dict__
            return obj.__dict__
        else:
            return str(obj)

    def _safe_json_response(self, data, status_code=200):
        """Create safe JSON response handling missing FastAPI components."""
        if JSONResponse:
            return JSONResponse(content=data, status_code=status_code)
        else:
            return data

    def _safe_http_exception(self, status_code, detail):
        """Create safe HTTP exception handling missing FastAPI components."""
        if HTTPException:
            raise HTTPException(status_code=status_code, detail=detail)
        else:
            return {"error": detail, "status_code": status_code}

    def _setup_routes(self):
        """Setup API routes."""
        if not self.app or not WEB_AVAILABLE:
            return

        @self.app.get("/")
        async def dashboard():
            """Serve the main dashboard HTML."""
            return self._get_dashboard_html()

        @self.app.get("/api/status")
        async def get_system_status():
            """Get overall system status."""
            try:
                # Collect current metrics
                system_metrics = await self.data_collector.collect_system_metrics()
                component_health = await self.data_collector.check_component_health()
                analysis_metrics = await self.data_collector.collect_analysis_metrics()

                # Calculate overall health
                overall_status = self._calculate_overall_status(component_health)

                # Create response data with proper serialization
                response_data = {
                    'status': 'success',
                    'data': {
                        'overall_status': overall_status,
                        'system_metrics': system_metrics.to_dict(),
                        'component_health': {k: v.to_dict() for k, v in component_health.items()},
                        'analysis_metrics': analysis_metrics.to_dict(),
                        'timestamp': datetime.utcnow().isoformat()
                    }
                }

                # Use custom JSON encoder to handle enums
                json_str = json.dumps(response_data, default=self._json_encoder)
                if JSONResponse:
                    return JSONResponse(content=json.loads(json_str))
                else:
                    return json.loads(json_str)

            except Exception as e:
                self.logger.error(f"Status endpoint error: {e}")
                if HTTPException:
                    raise HTTPException(status_code=500, detail=str(e))
                else:
                    return {"error": str(e)}

        @self.app.get("/api/metrics/history")
        async def get_metrics_history(hours: int = 24):
            """Get historical metrics."""
            try:
                data = self.data_collector.get_historical_metrics(hours)
                return self._safe_json_response({
                    'status': 'success',
                    'data': data
                })
            except Exception as e:
                self.logger.error(f"Metrics history endpoint error: {e}")
                return self._safe_http_exception(500, str(e))

        @self.app.get("/api/components/{component_name}")
        async def get_component_details(component_name: str):
            """Get detailed information about a specific component."""
            try:
                if component_name in self.data_collector.component_health:
                    component = self.data_collector.component_health[component_name]
                    return self._safe_json_response({
                        'status': 'success',
                        'data': component.to_dict()
                    })
                else:
                    return self._safe_http_exception(404, "Component not found")
            except Exception as e:
                self.logger.error(f"Component details endpoint error: {e}")
                return self._safe_http_exception(500, str(e))

        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket):
            """WebSocket endpoint for real-time updates."""
            await websocket.accept()
            self.connected_clients.append(websocket)

            try:
                while True:
                    # Keep connection alive
                    await websocket.receive_text()
            except Exception as e:
                self.logger.info(f"WebSocket client disconnected: {e}")
            finally:
                if websocket in self.connected_clients:
                    self.connected_clients.remove(websocket)

    async def start(self):
        """Start the monitoring dashboard."""
        if not self.app:
            self.logger.error("Cannot start dashboard - web framework not available")
            return

        # Start background monitoring task
        asyncio.create_task(self._monitoring_loop())

        # Start web server
        if uvicorn is None:
            self.logger.error("uvicorn not available - cannot start web server")
            return

        config = uvicorn.Config(
            app=self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )
        server = uvicorn.Server(config)

        self.logger.info(f"Starting monitoring dashboard on http://{self.host}:{self.port}")
        await server.serve()

    async def _monitoring_loop(self):
        """Background monitoring loop."""
        while True:
            try:
                # Collect all metrics
                system_metrics = await self.data_collector.collect_system_metrics()
                component_health = await self.data_collector.check_component_health()
                analysis_metrics = await self.data_collector.collect_analysis_metrics()

                # Send updates to connected WebSocket clients
                if self.connected_clients:
                    update_data = {
                        'type': 'update',
                        'system_metrics': system_metrics.to_dict(),
                        'component_health': {k: v.to_dict() for k, v in component_health.items()},
                        'analysis_metrics': analysis_metrics.to_dict(),
                        'timestamp': datetime.utcnow().isoformat()
                    }

                    # Send to all connected clients
                    disconnected_clients = []
                    for client in self.connected_clients:
                        try:
                            await client.send_json(update_data)
                        except Exception as e:
                            self.logger.warning(f"Failed to send update to client: {e}")
                            disconnected_clients.append(client)

                    # Remove disconnected clients
                    for client in disconnected_clients:
                        if client in self.connected_clients:
                            self.connected_clients.remove(client)

                # Wait before next update
                await asyncio.sleep(30)  # Update every 30 seconds

            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(60)  # Back off on error

    def _calculate_overall_status(self, component_health: Dict[str, ComponentHealth]) -> str:
        """Calculate overall system status."""
        if not component_health:
            return 'unknown'

        statuses = [health.status for health in component_health.values()]

        if ComponentStatus.ERROR in statuses:
            return 'error'
        elif ComponentStatus.WARNING in statuses:
            return 'warning'
        elif all(status == ComponentStatus.HEALTHY for status in statuses):
            return 'healthy'
        else:
            return 'warning'

    def _get_dashboard_html(self) -> str:
        """Generate the dashboard HTML."""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent Investment Platform - System Monitor</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        .card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .card h3 {
            margin-top: 0;
            color: #333;
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-healthy { background-color: #4CAF50; }
        .status-warning { background-color: #FF9800; }
        .status-error { background-color: #F44336; }
        .status-unknown { background-color: #9E9E9E; }
        .metric {
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            padding: 5px 0;
            border-bottom: 1px solid #eee;
        }
        .metric:last-child {
            border-bottom: none;
        }
        .metric-value {
            font-weight: bold;
            color: #667eea;
        }
        #lastUpdate {
            text-align: center;
            color: #666;
            margin-top: 20px;
        }
        .connection-status {
            position: fixed;
            top: 10px;
            right: 10px;
            padding: 10px;
            border-radius: 5px;
            color: white;
            font-size: 14px;
        }
        .connected { background-color: #4CAF50; }
        .disconnected { background-color: #F44336; }
    </style>
</head>
<body>
    <div class="connection-status" id="connectionStatus">Connecting...</div>

    <div class="header">
        <h1>🚀 Agent Investment Platform</h1>
        <h2>System Monitoring Dashboard</h2>
    </div>

    <div class="dashboard-grid">
        <div class="card">
            <h3>Overall System Status</h3>
            <div id="overallStatus">
                <span class="status-indicator status-unknown"></span>
                Loading...
            </div>
        </div>

        <div class="card">
            <h3>System Performance</h3>
            <div id="systemMetrics">
                <div class="metric">
                    <span>CPU Usage:</span>
                    <span class="metric-value" id="cpuUsage">-</span>
                </div>
                <div class="metric">
                    <span>Memory Usage:</span>
                    <span class="metric-value" id="memoryUsage">-</span>
                </div>
                <div class="metric">
                    <span>Disk Usage:</span>
                    <span class="metric-value" id="diskUsage">-</span>
                </div>
                <div class="metric">
                    <span>Active Connections:</span>
                    <span class="metric-value" id="activeConnections">-</span>
                </div>
            </div>
        </div>

        <div class="card">
            <h3>Component Health</h3>
            <div id="componentHealth">
                Loading component status...
            </div>
        </div>

        <div class="card">
            <h3>Analysis Metrics</h3>
            <div id="analysisMetrics">
                <div class="metric">
                    <span>Reports Generated:</span>
                    <span class="metric-value" id="reportsGenerated">-</span>
                </div>
                <div class="metric">
                    <span>Analyses Completed:</span>
                    <span class="metric-value" id="analysesCompleted">-</span>
                </div>
                <div class="metric">
                    <span>Success Rate:</span>
                    <span class="metric-value" id="successRate">-</span>
                </div>
                <div class="metric">
                    <span>Queue Size:</span>
                    <span class="metric-value" id="queueSize">-</span>
                </div>
            </div>
        </div>
    </div>

    <div id="lastUpdate">Last updated: Never</div>

    <script>
        let ws;
        let reconnectInterval;

        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;

            ws = new WebSocket(wsUrl);

            ws.onopen = function() {
                console.log('WebSocket connected');
                document.getElementById('connectionStatus').textContent = 'Connected';
                document.getElementById('connectionStatus').className = 'connection-status connected';

                if (reconnectInterval) {
                    clearInterval(reconnectInterval);
                    reconnectInterval = null;
                }
            };

            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                updateDashboard(data);
            };

            ws.onclose = function() {
                console.log('WebSocket disconnected');
                document.getElementById('connectionStatus').textContent = 'Disconnected';
                document.getElementById('connectionStatus').className = 'connection-status disconnected';

                // Try to reconnect
                if (!reconnectInterval) {
                    reconnectInterval = setInterval(connectWebSocket, 5000);
                }
            };

            ws.onerror = function(error) {
                console.error('WebSocket error:', error);
            };
        }

        function updateDashboard(data) {
            if (data.type === 'update') {
                // Update overall status
                const overallStatus = calculateOverallStatus(data.component_health);
                document.getElementById('overallStatus').innerHTML =
                    `<span class="status-indicator status-${overallStatus}"></span>${overallStatus.toUpperCase()}`;

                // Update system metrics
                const sm = data.system_metrics;
                document.getElementById('cpuUsage').textContent = `${sm.cpu_usage.toFixed(1)}%`;
                document.getElementById('memoryUsage').textContent = `${sm.memory_usage.toFixed(1)}%`;
                document.getElementById('diskUsage').textContent = `${sm.disk_usage.toFixed(1)}%`;
                document.getElementById('activeConnections').textContent = sm.active_connections;

                // Update component health
                updateComponentHealth(data.component_health);

                // Update analysis metrics
                const am = data.analysis_metrics;
                document.getElementById('reportsGenerated').textContent = am.reports_generated;
                document.getElementById('analysesCompleted').textContent = am.analyses_completed;
                document.getElementById('successRate').textContent = `${am.success_rate.toFixed(1)}%`;
                document.getElementById('queueSize').textContent = am.queue_size;

                // Update timestamp
                const timestamp = new Date(data.timestamp).toLocaleString();
                document.getElementById('lastUpdate').textContent = `Last updated: ${timestamp}`;
            }
        }

        function calculateOverallStatus(componentHealth) {
            const statuses = Object.values(componentHealth).map(c => c.status);

            if (statuses.includes('error')) return 'error';
            if (statuses.includes('warning')) return 'warning';
            if (statuses.every(s => s === 'healthy')) return 'healthy';
            return 'warning';
        }

        function updateComponentHealth(componentHealth) {
            const container = document.getElementById('componentHealth');
            container.innerHTML = '';

            for (const [name, health] of Object.entries(componentHealth)) {
                const div = document.createElement('div');
                div.className = 'metric';
                div.innerHTML = `
                    <span>${name.replace('_', ' ').toUpperCase()}:</span>
                    <span class="metric-value">
                        <span class="status-indicator status-${health.status}"></span>
                        ${health.status.toUpperCase()}
                    </span>
                `;
                container.appendChild(div);
            }
        }

        // Initial connection
        connectWebSocket();

        // Also fetch initial data via REST API
        fetch('/api/status')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    updateDashboard({type: 'update', ...data.data});
                }
            })
            .catch(error => console.error('Failed to fetch initial data:', error));
    </script>
</body>
</html>
        """


async def main():
    """Main function to run the monitoring dashboard."""
    logging.basicConfig(level=logging.INFO)

    # Create and start monitoring dashboard
    dashboard = MonitoringDashboard(port=8080)

    if dashboard.app:
        await dashboard.start()
    else:
        print("Monitoring dashboard not available - missing web framework dependencies")
        print("Install with: pip install fastapi uvicorn[standard]")


if __name__ == "__main__":
    asyncio.run(main())
