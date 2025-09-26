"""
Real-time log querying API with WebSocket support.

This module provides:
- RESTful API for log querying and statistics
- WebSocket server for real-time log streaming
- Filtering and search capabilities
- Live log monitoring
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
import websockets
from aiohttp import web, WSMsgType
try:
    import aiohttp_cors
    CORS_AVAILABLE = True
except ImportError:
    CORS_AVAILABLE = False
from pathlib import Path

from .core import LogEntry, get_logger, subscribe_to_logs, unsubscribe_from_logs
from .config import get_config_loader
from .aggregation import get_log_aggregator, LogQuery


@dataclass
class LogFilter:
    """Filter criteria for real-time log streaming."""
    levels: Optional[List[str]] = None
    components: Optional[List[str]] = None
    logger_names: Optional[List[str]] = None
    message_contains: Optional[str] = None
    min_timestamp: Optional[datetime] = None


class WebSocketLogClient:
    """Represents a WebSocket client connection for real-time logs."""

    def __init__(self, websocket, client_id: str):
        self.websocket = websocket
        self.client_id = client_id
        self.filters: Optional[LogFilter] = None
        self.connected = True
        self.last_ping = time.time()

    async def send_log(self, log_entry: LogEntry):
        """Send log entry to client if it matches filters."""
        if not self.connected:
            return

        # Apply filters
        if self.filters:
            if self.filters.levels and log_entry.level not in self.filters.levels:
                return
            if self.filters.components and log_entry.component not in self.filters.components:
                return
            if self.filters.logger_names and log_entry.logger_name not in self.filters.logger_names:
                return
            if self.filters.message_contains and self.filters.message_contains.lower() not in log_entry.message.lower():
                return
            if self.filters.min_timestamp:
                log_time = datetime.fromisoformat(log_entry.timestamp.replace('Z', '+00:00'))
                if log_time < self.filters.min_timestamp:
                    return

        try:
            message = {
                "type": "log_entry",
                "data": asdict(log_entry)
            }
            await self.websocket.send(json.dumps(message, default=str))
        except Exception:
            self.connected = False

    async def send_message(self, message_type: str, data: Any):
        """Send a message to the client."""
        if not self.connected:
            return

        try:
            message = {
                "type": message_type,
                "data": data
            }
            await self.websocket.send(json.dumps(message, default=str))
        except Exception:
            self.connected = False

    def set_filters(self, filters: LogFilter):
        """Set log filters for this client."""
        self.filters = filters

    def update_ping(self):
        """Update last ping time."""
        self.last_ping = time.time()


class LogStreamingServer:
    """WebSocket server for real-time log streaming."""

    def __init__(self, host: str = "0.0.0.0", port: int = 8765):
        self.host = host
        self.port = port
        self.logger = get_logger(__name__, "log_streaming")
        self.clients: Dict[str, WebSocketLogClient] = {}
        self.server = None
        self.running = False
        self.ping_task: Optional[asyncio.Task] = None

    async def start(self):
        """Start the WebSocket server."""
        if self.running:
            return

        self.logger.info(f"Starting WebSocket log streaming server on {self.host}:{self.port}")

        # Subscribe to real-time logs with a synchronous wrapper
        def sync_log_handler(log_entry: LogEntry):
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self._on_log_entry(log_entry))
            except RuntimeError:
                # No event loop running, skip this log entry
                pass

        subscribe_to_logs(sync_log_handler)
        self._sync_handler = sync_log_handler

        # Start WebSocket server
        try:
            import websockets.exceptions
            self.server = await websockets.serve(
                self._handle_client,
                self.host,
                self.port,
                ping_interval=30,
                ping_timeout=10
            )
        except ImportError:
            self.logger.error("websockets library not available")
            return

        # Start ping task for client management
        self.ping_task = asyncio.create_task(self._ping_clients())

        self.running = True
        self.logger.info(f"WebSocket server started on ws://{self.host}:{self.port}")

    async def stop(self):
        """Stop the WebSocket server."""
        if not self.running:
            return

        self.logger.info("Stopping WebSocket log streaming server")

        # Unsubscribe from logs
        if hasattr(self, '_sync_handler'):
            unsubscribe_from_logs(self._sync_handler)

        # Stop ping task
        if self.ping_task:
            self.ping_task.cancel()
            try:
                await self.ping_task
            except asyncio.CancelledError:
                pass

        # Close all client connections
        for client in list(self.clients.values()):
            try:
                await client.websocket.close()
            except Exception:
                pass
        self.clients.clear()

        # Stop server
        if self.server:
            self.server.close()
            await self.server.wait_closed()

        self.running = False
        self.logger.info("WebSocket server stopped")

    async def _handle_client(self, websocket):
        """Handle new WebSocket client connection."""
        client_id = f"client_{len(self.clients)}_{int(time.time())}"
        client = WebSocketLogClient(websocket, client_id)
        self.clients[client_id] = client

        self.logger.info(f"New WebSocket client connected: {client_id}")

        try:
            # Send welcome message
            await client.send_message("connected", {
                "client_id": client_id,
                "server_time": datetime.utcnow().isoformat()
            })

            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self._handle_client_message(client, data)
                except json.JSONDecodeError:
                    await client.send_message("error", {"message": "Invalid JSON"})
                except Exception as e:
                    self.logger.error(f"Error handling client message: {e}")
                    await client.send_message("error", {"message": str(e)})

        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            self.logger.error(f"Error handling client {client_id}: {e}")
        finally:
            # Clean up client
            if client_id in self.clients:
                del self.clients[client_id]
            self.logger.info(f"Client disconnected: {client_id}")

    async def _handle_client_message(self, client: WebSocketLogClient, data: Dict[str, Any]):
        """Handle message from WebSocket client."""
        message_type = data.get("type")
        payload = data.get("data", {})

        if message_type == "set_filters":
            # Set log filters
            filters = LogFilter(
                levels=payload.get("levels"),
                components=payload.get("components"),
                logger_names=payload.get("logger_names"),
                message_contains=payload.get("message_contains"),
                min_timestamp=datetime.fromisoformat(payload["min_timestamp"]) if payload.get("min_timestamp") else None
            )
            client.set_filters(filters)
            await client.send_message("filters_set", {"status": "ok"})

        elif message_type == "ping":
            client.update_ping()
            await client.send_message("pong", {"timestamp": datetime.utcnow().isoformat()})

        elif message_type == "get_stats":
            # Get current statistics
            aggregator = await get_log_aggregator()
            stats = await aggregator.get_log_statistics()
            await client.send_message("stats", stats)

        else:
            await client.send_message("error", {"message": f"Unknown message type: {message_type}"})

    async def _on_log_entry(self, log_entry: LogEntry):
        """Handle new log entry from the logging system."""
        # Broadcast to all connected clients
        disconnected_clients = []

        for client_id, client in self.clients.items():
            try:
                await client.send_log(log_entry)
                if not client.connected:
                    disconnected_clients.append(client_id)
            except Exception as e:
                self.logger.error(f"Error sending log to client {client_id}: {e}")
                disconnected_clients.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected_clients:
            if client_id in self.clients:
                del self.clients[client_id]

    async def _ping_clients(self):
        """Periodically ping clients to detect disconnections."""
        while self.running:
            try:
                await asyncio.sleep(30)

                current_time = time.time()
                disconnected_clients = []

                for client_id, client in self.clients.items():
                    # Check if client is still responsive
                    if current_time - client.last_ping > 60:  # 60 seconds timeout
                        disconnected_clients.append(client_id)

                # Clean up unresponsive clients
                for client_id in disconnected_clients:
                    if client_id in self.clients:
                        self.logger.info(f"Removing unresponsive client: {client_id}")
                        del self.clients[client_id]

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in client ping task: {e}")


class LogQueryAPI:
    """REST API for log querying and management."""

    def __init__(self):
        self.logger = get_logger(__name__, "log_api")
        self.app = web.Application()
        self.setup_routes()
        self.setup_cors()

    def setup_routes(self):
        """Setup API routes."""
        self.app.router.add_get('/api/logs', self.query_logs)
        self.app.router.add_get('/api/logs/stats', self.get_statistics)
        self.app.router.add_get('/api/logs/components', self.get_components)
        self.app.router.add_get('/api/health', self.health_check)

        # Static files for dashboard
        self.app.router.add_static('/', Path(__file__).parent / 'dashboard', name='dashboard')

    def setup_cors(self):
        """Setup CORS for cross-origin requests."""
        if CORS_AVAILABLE:
            cors = aiohttp_cors.setup(self.app, defaults={
                "*": aiohttp_cors.ResourceOptions(
                    allow_credentials=True,
                    expose_headers="*",
                    allow_headers="*",
                    allow_methods="*"
                )
            })

            # Add CORS to all routes
            for route in list(self.app.router.routes()):
                cors.add(route)
        else:
            # Manual CORS headers
            @web.middleware
            async def cors_middleware(request, handler):
                response = await handler(request)
                response.headers['Access-Control-Allow-Origin'] = '*'
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
                response.headers['Access-Control-Allow-Headers'] = '*'
                return response

            self.app.middlewares.append(cors_middleware)

    async def query_logs(self, request: web.Request) -> web.Response:
        """Query logs with filtering and pagination."""
        try:
            # Parse query parameters
            params = request.query

            # Build log query with error handling for datetime parsing
            start_time = None
            end_time = None

            if params.get('start_time'):
                try:
                    start_time = datetime.fromisoformat(params['start_time'])
                except ValueError:
                    return web.json_response(
                        {"error": "Invalid start_time format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"},
                        status=400
                    )

            if params.get('end_time'):
                try:
                    end_time = datetime.fromisoformat(params['end_time'])
                except ValueError:
                    return web.json_response(
                        {"error": "Invalid end_time format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"},
                        status=400
                    )

            query = LogQuery(
                start_time=start_time,
                end_time=end_time,
                level=params.get('level'),
                component=params.get('component'),
                logger_name=params.get('logger_name'),
                message_contains=params.get('message_contains'),
                limit=int(params.get('limit', 100)),
                offset=int(params.get('offset', 0)),
                sort_order=params.get('sort_order', 'desc')
            )

            # Query logs
            aggregator = await get_log_aggregator()
            logs = await aggregator.query_logs(query)

            return web.json_response({
                "logs": logs,
                "count": len(logs),
                "query": asdict(query)
            })

        except Exception as e:
            self.logger.error(f"Error querying logs: {e}")
            return web.json_response(
                {"error": str(e)},
                status=500
            )

    async def get_statistics(self, request: web.Request) -> web.Response:
        """Get log statistics and aggregations."""
        try:
            params = request.query

            start_time = None
            end_time = None

            if params.get('start_time'):
                try:
                    start_time = datetime.fromisoformat(params['start_time'])
                except ValueError:
                    return web.json_response(
                        {"error": "Invalid start_time format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"},
                        status=400
                    )

            if params.get('end_time'):
                try:
                    end_time = datetime.fromisoformat(params['end_time'])
                except ValueError:
                    return web.json_response(
                        {"error": "Invalid end_time format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"},
                        status=400
                    )

            aggregator = await get_log_aggregator()
            stats = await aggregator.get_log_statistics(start_time, end_time)

            return web.json_response(stats)

        except Exception as e:
            self.logger.error(f"Error getting statistics: {e}")
            return web.json_response(
                {"error": str(e)},
                status=500
            )

    async def get_components(self, request: web.Request) -> web.Response:
        """Get list of available components."""
        try:
            # This would typically come from a configuration or discovery service
            # For now, return a static list based on known components
            components = [
                "orchestrator",
                "mcp_servers",
                "analysis_engine",
                "financial_data",
                "report_generator",
                "health_monitor",
                "websocket_server",
                "logging_dashboard",
                "data_collector",
                "strategy_manager",
                "risk_manager",
                "notification_system"
            ]

            return web.json_response({
                "components": components
            })

        except Exception as e:
            self.logger.error(f"Error getting components: {e}")
            return web.json_response(
                {"error": str(e)},
                status=500
            )

    async def health_check(self, request: web.Request) -> web.Response:
        """Health check endpoint."""
        try:
            aggregator = await get_log_aggregator()

            health = {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "services": {
                    "log_aggregator": "running" if aggregator.running else "stopped",
                    "elasticsearch": "unknown"  # Would check ES health
                }
            }

            return web.json_response(health)

        except Exception as e:
            self.logger.error(f"Health check error: {e}")
            return web.json_response(
                {"status": "unhealthy", "error": str(e)},
                status=500
            )


async def run_log_api_server(host: str = "0.0.0.0", port: int = 8764):
    """Run the log query API server."""
    api = LogQueryAPI()

    runner = web.AppRunner(api.app)
    await runner.setup()

    site = web.TCPSite(runner, host, port)
    await site.start()

    logger = get_logger(__name__, "log_api")
    logger.info(f"Log API server started on http://{host}:{port}")

    return runner


async def main():
    """Main entry point for the log streaming and API servers."""
    config_loader = get_config_loader()
    config = config_loader.config

    # Start WebSocket server
    ws_port = config.realtime.get('websocket_port', 8765) if config else 8765
    streaming_server = LogStreamingServer(port=ws_port)
    await streaming_server.start()

    # Start API server
    api_runner = await run_log_api_server(port=8764)

    try:
        # Keep servers running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down servers...")
    finally:
        await streaming_server.stop()
        await api_runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
