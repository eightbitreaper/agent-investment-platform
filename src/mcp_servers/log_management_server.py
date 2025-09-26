"""
MCP Server for Log Querying and Management.

This server provides MCP tools for:
- Querying logs with advanced filtering
- Real-time log monitoring
- Log statistics and analytics
- System health monitoring through logs
- Log export and management
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import asdict

from ..mcp_servers.base import MCPServerBase, MCPTool, MCPHandler
from ..logging.core import get_logger
from ..logging.aggregation import get_log_aggregator, LogQuery
from ..logging.config import get_config_loader
from ..logging import health_check_logging_system


class LogQueryHandler(MCPHandler):
    """Handler for log query operations."""

    async def handle_tools_call_query_logs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query logs with filtering and pagination."""
        try:
            # Parse query parameters
            start_time = None
            end_time = None

            if params.get('start_time'):
                start_time = datetime.fromisoformat(params['start_time'])
            if params.get('end_time'):
                end_time = datetime.fromisoformat(params['end_time'])

            # Create log query
            query = LogQuery(
                start_time=start_time,
                end_time=end_time,
                level=params.get('level'),
                component=params.get('component'),
                logger_name=params.get('logger_name'),
                message_contains=params.get('message_contains'),
                limit=params.get('limit', 100),
                offset=params.get('offset', 0),
                sort_order=params.get('sort_order', 'desc')
            )

            # Query logs
            aggregator = await get_log_aggregator()
            logs = await aggregator.query_logs(query)

            return {
                "success": True,
                "logs": logs,
                "count": len(logs),
                "query_params": asdict(query)
            }

        except Exception as e:
            self.logger.error(f"Error querying logs: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    async def handle_tools_call_get_log_statistics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get log statistics and aggregations."""
        try:
            start_time = None
            end_time = None

            if params.get('start_time'):
                start_time = datetime.fromisoformat(params['start_time'])
            if params.get('end_time'):
                end_time = datetime.fromisoformat(params['end_time'])

            aggregator = await get_log_aggregator()
            stats = await aggregator.get_log_statistics(start_time, end_time)

            return {
                "success": True,
                "statistics": stats
            }

        except Exception as e:
            self.logger.error(f"Error getting log statistics: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    async def handle_tools_call_get_recent_errors(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get recent error and critical logs."""
        try:
            hours = params.get('hours', 1)
            limit = params.get('limit', 50)

            # Query for recent errors
            start_time = datetime.utcnow() - timedelta(hours=hours)

            query = LogQuery(
                start_time=start_time,
                level='ERROR',
                limit=limit,
                sort_order='desc'
            )

            aggregator = await get_log_aggregator()
            error_logs = await aggregator.query_logs(query)

            # Also get critical logs
            critical_query = LogQuery(
                start_time=start_time,
                level='CRITICAL',
                limit=limit,
                sort_order='desc'
            )

            critical_logs = await aggregator.query_logs(critical_query)

            return {
                "success": True,
                "error_logs": error_logs,
                "critical_logs": critical_logs,
                "total_errors": len(error_logs),
                "total_critical": len(critical_logs),
                "time_range_hours": hours
            }

        except Exception as e:
            self.logger.error(f"Error getting recent errors: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    async def handle_tools_call_analyze_log_patterns(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze log patterns and trends."""
        try:
            hours = params.get('hours', 24)
            start_time = datetime.utcnow() - timedelta(hours=hours)

            aggregator = await get_log_aggregator()
            stats = await aggregator.get_log_statistics(start_time)

            # Analyze patterns
            analysis = {
                "time_range_hours": hours,
                "total_logs": stats.get('total', 0),
                "level_distribution": {},
                "component_activity": {},
                "error_rate": 0,
                "top_components": [],
                "timeline_analysis": {}
            }

            # Process level distribution
            levels = stats.get('levels', [])
            total_logs = sum(level['doc_count'] for level in levels)

            for level in levels:
                level_name = level['key']
                count = level['doc_count']
                percentage = (count / total_logs * 100) if total_logs > 0 else 0

                analysis['level_distribution'][level_name] = {
                    'count': count,
                    'percentage': round(percentage, 2)
                }

                if level_name in ['ERROR', 'CRITICAL']:
                    analysis['error_rate'] += percentage

            analysis['error_rate'] = round(analysis['error_rate'], 2)

            # Process component activity
            components = stats.get('components', [])
            analysis['top_components'] = sorted(components, key=lambda x: x['doc_count'], reverse=True)[:10]

            # Process timeline
            timeline = stats.get('timeline', [])
            if timeline:
                # Calculate activity trends
                recent_activity = sum(bucket['doc_count'] for bucket in timeline[-6:])  # Last 6 hours
                earlier_activity = sum(bucket['doc_count'] for bucket in timeline[-12:-6])  # Previous 6 hours

                if earlier_activity > 0:
                    trend_percentage = ((recent_activity - earlier_activity) / earlier_activity) * 100
                    analysis['timeline_analysis'] = {
                        'recent_activity': recent_activity,
                        'earlier_activity': earlier_activity,
                        'trend_percentage': round(trend_percentage, 2),
                        'trend_direction': 'increasing' if trend_percentage > 0 else 'decreasing'
                    }

            return {
                "success": True,
                "analysis": analysis
            }

        except Exception as e:
            self.logger.error(f"Error analyzing log patterns: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    async def handle_tools_call_search_logs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search logs with text-based queries."""
        try:
            search_term = params.get('search_term', '')
            if not search_term:
                return {
                    "success": False,
                    "error": "search_term parameter is required"
                }

            hours = params.get('hours', 24)
            limit = params.get('limit', 100)
            level = params.get('level')
            component = params.get('component')

            start_time = datetime.utcnow() - timedelta(hours=hours)

            query = LogQuery(
                start_time=start_time,
                level=level,
                component=component,
                message_contains=search_term,
                limit=limit,
                sort_order='desc'
            )

            aggregator = await get_log_aggregator()
            logs = await aggregator.query_logs(query)

            # Highlight search terms in results
            highlighted_logs = []
            for log in logs:
                highlighted_log = dict(log)
                if search_term.lower() in log['message'].lower():
                    # Simple highlighting (in production, you'd use proper text highlighting)
                    highlighted_log['highlighted_message'] = log['message'].replace(
                        search_term, f"**{search_term}**"
                    )
                highlighted_logs.append(highlighted_log)

            return {
                "success": True,
                "search_term": search_term,
                "logs": highlighted_logs,
                "count": len(highlighted_logs),
                "time_range_hours": hours
            }

        except Exception as e:
            self.logger.error(f"Error searching logs: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    async def handle_tools_call_get_system_health(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get system health information based on logs."""
        try:
            # Run logging system health check
            health_status = await health_check_logging_system()

            # Get recent error counts
            hours = params.get('hours', 1)
            start_time = datetime.utcnow() - timedelta(hours=hours)

            aggregator = await get_log_aggregator()
            stats = await aggregator.get_log_statistics(start_time)

            # Calculate health metrics
            levels = stats.get('levels', [])
            error_count = 0
            critical_count = 0
            warning_count = 0
            total_logs = 0

            for level in levels:
                count = level['doc_count']
                total_logs += count

                if level['key'] == 'ERROR':
                    error_count = count
                elif level['key'] == 'CRITICAL':
                    critical_count = count
                elif level['key'] == 'WARNING':
                    warning_count = count

            # Determine overall health
            overall_health = "healthy"
            if critical_count > 0:
                overall_health = "critical"
            elif error_count > 10:  # Threshold for errors
                overall_health = "unhealthy"
            elif warning_count > 50:  # Threshold for warnings
                overall_health = "warning"

            health_info = {
                "overall_health": overall_health,
                "logging_system_status": "healthy" if health_status else "unhealthy",
                "metrics": {
                    "total_logs": total_logs,
                    "error_count": error_count,
                    "critical_count": critical_count,
                    "warning_count": warning_count,
                    "error_rate": round((error_count / total_logs * 100) if total_logs > 0 else 0, 2)
                },
                "time_range_hours": hours,
                "timestamp": datetime.utcnow().isoformat()
            }

            return {
                "success": True,
                "health": health_info
            }

        except Exception as e:
            self.logger.error(f"Error getting system health: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    async def handle_tools_call_get_log_config(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get current logging configuration."""
        try:
            config_loader = get_config_loader()
            config = config_loader.config

            if not config:
                return {
                    "success": False,
                    "error": "No logging configuration loaded"
                }

            config_info = {
                "log_level": config.log_level,
                "structured_logging": config.structured_logging,
                "colored_console": config.colored_console,
                "component_levels": config.component_levels,
                "enabled_handlers": {
                    name: handler.enabled
                    for name, handler in config.handlers.items()
                },
                "realtime_enabled": config.realtime.get('websocket_enabled', False),
                "websocket_port": config.realtime.get('websocket_port', 8765),
                "performance_logging": config.performance.get('function_timing', False)
            }

            return {
                "success": True,
                "configuration": config_info
            }

        except Exception as e:
            self.logger.error(f"Error getting log configuration: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }


class LogManagementServer(MCPServerBase):
    """MCP Server for log querying and management."""

    def __init__(self):
        super().__init__(
            name="log-management",
            version="1.0.0",
            description="MCP Server for comprehensive log querying, analysis, and management"
        )

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check and return status."""
        try:
            # Check if logging system is running
            health_status = await health_check_logging_system()

            # Check if aggregator is available
            aggregator = await get_log_aggregator()
            aggregator_running = aggregator.running if aggregator else False

            status = "healthy" if health_status and aggregator_running else "unhealthy"

            return {
                "status": status,
                "timestamp": datetime.utcnow().isoformat(),
                "components": {
                    "logging_system": "healthy" if health_status else "unhealthy",
                    "log_aggregator": "running" if aggregator_running else "stopped"
                }
            }
        except Exception as e:
            self.logger.error(f"Health check failed: {e}", exc_info=True)
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def _register_capabilities(self):
        """Register MCP tools for log management."""
        # Register handler
        self.handlers["log_query"] = LogQueryHandler(self)

        # Query logs tool
        query_logs_tool = MCPTool(
            name="query_logs",
            description="Query logs with advanced filtering and pagination",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_time": {
                        "type": "string",
                        "description": "Start time in ISO format (optional)"
                    },
                    "end_time": {
                        "type": "string",
                        "description": "End time in ISO format (optional)"
                    },
                    "level": {
                        "type": "string",
                        "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        "description": "Log level filter (optional)"
                    },
                    "component": {
                        "type": "string",
                        "description": "Component name filter (optional)"
                    },
                    "logger_name": {
                        "type": "string",
                        "description": "Logger name filter (optional)"
                    },
                    "message_contains": {
                        "type": "string",
                        "description": "Search text in log messages (optional)"
                    },
                    "limit": {
                        "type": "integer",
                        "default": 100,
                        "description": "Maximum number of logs to return"
                    },
                    "offset": {
                        "type": "integer",
                        "default": 0,
                        "description": "Offset for pagination"
                    },
                    "sort_order": {
                        "type": "string",
                        "enum": ["asc", "desc"],
                        "default": "desc",
                        "description": "Sort order by timestamp"
                    }
                }
            }
        )
        self.register_tool(query_logs_tool, self.handlers["log_query"].handle_tools_call_query_logs)

        # Get log statistics tool
        stats_tool = MCPTool(
            name="get_log_statistics",
            description="Get log statistics and aggregations",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_time": {
                        "type": "string",
                        "description": "Start time in ISO format (optional)"
                    },
                    "end_time": {
                        "type": "string",
                        "description": "End time in ISO format (optional)"
                    }
                }
            }
        )
        self.register_tool(stats_tool, self.handlers["log_query"].handle_tools_call_get_log_statistics)

        # Get recent errors tool
        errors_tool = MCPTool(
            name="get_recent_errors",
            description="Get recent error and critical logs",
            inputSchema={
                "type": "object",
                "properties": {
                    "hours": {
                        "type": "integer",
                        "default": 1,
                        "description": "Number of hours to look back"
                    },
                    "limit": {
                        "type": "integer",
                        "default": 50,
                        "description": "Maximum number of logs per level"
                    }
                }
            }
        )
        self.register_tool(errors_tool, self.handlers["log_query"].handle_tools_call_get_recent_errors)

        # Analyze log patterns tool
        patterns_tool = MCPTool(
            name="analyze_log_patterns",
            description="Analyze log patterns and trends",
            inputSchema={
                "type": "object",
                "properties": {
                    "hours": {
                        "type": "integer",
                        "default": 24,
                        "description": "Number of hours to analyze"
                    }
                }
            }
        )
        self.register_tool(patterns_tool, self.handlers["log_query"].handle_tools_call_analyze_log_patterns)

        # Search logs tool
        search_tool = MCPTool(
            name="search_logs",
            description="Search logs with text-based queries",
            inputSchema={
                "type": "object",
                "properties": {
                    "search_term": {
                        "type": "string",
                        "description": "Text to search for in log messages"
                    },
                    "hours": {
                        "type": "integer",
                        "default": 24,
                        "description": "Number of hours to search back"
                    },
                    "limit": {
                        "type": "integer",
                        "default": 100,
                        "description": "Maximum number of logs to return"
                    },
                    "level": {
                        "type": "string",
                        "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        "description": "Log level filter (optional)"
                    },
                    "component": {
                        "type": "string",
                        "description": "Component name filter (optional)"
                    }
                },
                "required": ["search_term"]
            }
        )
        self.register_tool(search_tool, self.handlers["log_query"].handle_tools_call_search_logs)

        # Get system health tool
        health_tool = MCPTool(
            name="get_system_health",
            description="Get system health information based on logs",
            inputSchema={
                "type": "object",
                "properties": {
                    "hours": {
                        "type": "integer",
                        "default": 1,
                        "description": "Number of hours to analyze for health metrics"
                    }
                }
            }
        )
        self.register_tool(health_tool, self.handlers["log_query"].handle_tools_call_get_system_health)

        # Get log configuration tool
        config_tool = MCPTool(
            name="get_log_config",
            description="Get current logging system configuration",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
        self.register_tool(config_tool, self.handlers["log_query"].handle_tools_call_get_log_config)


async def main():
    """Main entry point for the Log Management MCP Server."""
    import sys

    # Initialize logging
    from ..logging import initialize_platform_logging
    await initialize_platform_logging(log_level="INFO")

    logger = get_logger(__name__)
    logger.info("Starting Log Management MCP Server")

    # Create and start server
    server = LogManagementServer()

    try:
        # Set port from environment or command line
        import os
        port = int(sys.argv[1]) if len(sys.argv) > 1 else 3005
        os.environ['PORT'] = str(port)

        # Start the MCP server
        await server.run_http_server()
    except KeyboardInterrupt:
        logger.info("Shutting down Log Management MCP Server")
    except Exception as e:
        logger.error(f"Error running server: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
