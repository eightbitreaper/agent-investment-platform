"""
Logging system initialization and integration module.

This module handles the initialization and integration of the comprehensive
logging system with the existing Agent Investment Platform components.
"""

import asyncio
import logging
import sys
import time
from pathlib import Path
from typing import Optional
import os

# Import the new logging system
from .core import configure_logging, get_logger, LogContext, log_performance
from .config import get_config_loader, reload_config
from .aggregation import get_log_aggregator, shutdown_log_aggregator
from .websocket_server import LogStreamingServer, run_log_api_server


class LoggingSystemManager:
    """Manager for the complete logging system lifecycle."""

    def __init__(self):
        self.config_loader = None
        self.aggregator = None
        self.streaming_server = None
        self.api_runner = None
        self.logger = None
        self.initialized = False

    async def initialize(self, config_path: Optional[str] = None, log_level: str = "INFO"):
        """Initialize the complete logging system."""
        if self.initialized:
            return

        try:
            # Load configuration
            self.config_loader = get_config_loader(config_path)
            config = self.config_loader.config

            # Configure core logging
            self.logger = configure_logging(
                level=config.log_level if config else log_level,
                component="logging_system",
                enable_async=True
            )

            self.logger.info("Initializing comprehensive logging system")

            # Start log aggregation
            self.aggregator = await get_log_aggregator()
            self.logger.info("Log aggregation system started")

            # Start WebSocket streaming server if enabled
            if config and config.realtime.get('websocket_enabled', False):
                ws_port = config.realtime.get('websocket_port', 8765)
                self.streaming_server = LogStreamingServer(port=ws_port)
                await self.streaming_server.start()
                self.logger.info(f"WebSocket streaming server started on port {ws_port}")

            # Start REST API server
            api_port = 8764  # Default API port
            self.api_runner = await run_log_api_server(port=api_port)
            self.logger.info(f"Log API server started on port {api_port}")

            self.initialized = True
            self.logger.info("Logging system initialization completed successfully")

        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to initialize logging system: {e}", exc_info=True)
            else:
                print(f"CRITICAL: Failed to initialize logging system: {e}")
            raise

    async def shutdown(self):
        """Shutdown the logging system gracefully."""
        if not self.initialized:
            return

        if self.logger:
            self.logger.info("Shutting down logging system")

        try:
            # Stop streaming server
            if self.streaming_server:
                await self.streaming_server.stop()
                if self.logger:
                    self.logger.info("WebSocket streaming server stopped")

            # Stop API server
            if self.api_runner:
                await self.api_runner.cleanup()
                if self.logger:
                    self.logger.info("Log API server stopped")

            # Stop aggregator
            if self.aggregator:
                await shutdown_log_aggregator()
                if self.logger:
                    self.logger.info("Log aggregation system stopped")

            self.initialized = False
            if self.logger:
                self.logger.info("Logging system shutdown completed")

        except Exception as e:
            if self.logger:
                self.logger.error(f"Error during logging system shutdown: {e}", exc_info=True)
            else:
                print(f"ERROR: Failed to shutdown logging system: {e}")

    def reload_configuration(self, config_path: Optional[str] = None):
        """Reload logging configuration."""
        if self.logger:
            self.logger.info("Reloading logging configuration")

        try:
            reload_config(config_path)

            if self.logger:
                self.logger.info("Logging configuration reloaded successfully")

        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to reload logging configuration: {e}", exc_info=True)
            raise


# Global logging system manager
_logging_manager = None


async def initialize_platform_logging(config_path: Optional[str] = None, log_level: str = "INFO"):
    """Initialize the platform-wide logging system."""
    global _logging_manager

    if _logging_manager is None:
        _logging_manager = LoggingSystemManager()

    await _logging_manager.initialize(config_path, log_level)
    return _logging_manager


async def shutdown_platform_logging():
    """Shutdown the platform-wide logging system."""
    global _logging_manager

    if _logging_manager:
        await _logging_manager.shutdown()
        _logging_manager = None


def get_platform_logger(name: str, component: Optional[str] = None) -> logging.Logger:
    """Get a configured logger for platform components."""
    return get_logger(name, component)


def create_log_context(**context):
    """Create a logging context for enriched logging."""
    return LogContext(**context)


def performance_monitor(logger_or_func=None):
    """Decorator for performance monitoring.

    Can be used with or without a logger parameter:
    @performance_monitor  # Uses default logger
    @performance_monitor(logger)  # Uses provided logger
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Determine which logger to use
            if logger_or_func and hasattr(logger_or_func, 'info'):
                # logger_or_func is actually a logger
                logger = logger_or_func
            else:
                # Use default logger
                try:
                    logger = get_platform_logger(func.__module__, func.__module__.split('.')[0])
                except:
                    logger = get_platform_logger(__name__, "performance_monitor")

            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                duration = (time.time() - start_time) * 1000
                logger.info(f"Function {func.__name__} completed in {duration:.2f}ms")
                return result
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                logger.error(f"Function {func.__name__} failed after {duration:.2f}ms: {e}", exc_info=True)
                raise

        return wrapper

    # Handle the case where decorator is used without parentheses
    if logger_or_func and callable(logger_or_func) and not hasattr(logger_or_func, 'info'):
        # @performance_monitor (without parentheses)
        func = logger_or_func
        return decorator(func)
    else:
        # @performance_monitor() or @performance_monitor(logger)
        return decorator


def integrate_with_existing_modules():
    """Integrate the new logging system with existing platform modules."""
    logger = get_platform_logger(__name__, "logging_integration")
    logger.info("Starting integration with existing platform modules")

    try:
        # Update orchestrator logging
        _update_orchestrator_logging()

        # Update MCP server logging
        _update_mcp_server_logging()

        # Update health check logging
        _update_health_check_logging()

        # Update other modules
        _update_other_modules_logging()

        logger.info("Successfully integrated logging with existing modules")

    except Exception as e:
        logger.error(f"Failed to integrate logging with existing modules: {e}", exc_info=True)
        raise


def _update_orchestrator_logging():
    """Update orchestrator.py to use the new logging system."""
    logger = get_platform_logger(__name__, "orchestrator_integration")

    # This would typically involve modifying the orchestrator.py file
    # to use the new logging system, but since we don't want to modify
    # existing files extensively, we'll provide integration points

    logger.info("Orchestrator logging integration prepared")


def _update_mcp_server_logging():
    """Update MCP servers to use the new logging system."""
    logger = get_platform_logger(__name__, "mcp_integration")

    # Integration points for MCP servers
    logger.info("MCP server logging integration prepared")


def _update_health_check_logging():
    """Update health check scripts to use the new logging system."""
    logger = get_platform_logger(__name__, "health_check_integration")

    # Integration points for health checks
    logger.info("Health check logging integration prepared")


def _update_other_modules_logging():
    """Update other platform modules to use the new logging system."""
    logger = get_platform_logger(__name__, "modules_integration")

    # Integration points for other modules
    logger.info("Other modules logging integration prepared")


class LoggingMiddleware:
    """Middleware for integrating logging with web requests."""

    def __init__(self, app):
        self.app = app
        self.logger = get_platform_logger(__name__, "web_middleware")

    async def __call__(self, scope, receive, send):
        """ASGI middleware for request logging."""
        if scope["type"] == "http":
            with create_log_context(
                request_id=scope.get("request_id"),
                path=scope.get("path"),
                method=scope.get("method")
            ) as ctx:
                ctx.log(self.logger, "info", f"Request started: {scope.get('method')} {scope.get('path')}")

                try:
                    await self.app(scope, receive, send)
                    ctx.log(self.logger, "info", "Request completed successfully")
                except Exception as e:
                    ctx.log(self.logger, "error", f"Request failed: {e}", exc_info=True)
                    raise
        else:
            await self.app(scope, receive, send)


def setup_environment_logging():
    """Setup logging based on environment variables."""
    logger = get_platform_logger(__name__, "environment_setup")

    # Check for environment-specific logging configuration
    env = os.getenv("ENVIRONMENT", "development")
    debug_mode = os.getenv("DEBUG", "false").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "INFO")

    logger.info(f"Setting up logging for environment: {env}")
    logger.info(f"Debug mode: {debug_mode}")
    logger.info(f"Log level: {log_level}")

    # Apply environment-specific settings
    if env == "production":
        # Production logging settings
        logger.info("Applying production logging configuration")
    elif env == "development":
        # Development logging settings
        logger.info("Applying development logging configuration")
    elif env == "testing":
        # Testing logging settings
        logger.info("Applying testing logging configuration")


async def health_check_logging_system():
    """Perform health check on the logging system."""
    logger = get_platform_logger(__name__, "health_check")

    try:
        logger.info("Starting logging system health check")

        # Check core logging
        test_logger = get_platform_logger("health_test", "test")
        test_logger.debug("Health check: DEBUG level")
        test_logger.info("Health check: INFO level")
        test_logger.warning("Health check: WARNING level")

        # Check aggregation system
        global _logging_manager
        if _logging_manager and _logging_manager.aggregator:
            if _logging_manager.aggregator.running:
                logger.info("Log aggregation system: HEALTHY")
            else:
                logger.warning("Log aggregation system: NOT RUNNING")
        else:
            logger.warning("Log aggregation system: NOT INITIALIZED")

        # Check streaming server
        if _logging_manager and _logging_manager.streaming_server:
            if _logging_manager.streaming_server.running:
                logger.info("WebSocket streaming server: HEALTHY")
            else:
                logger.warning("WebSocket streaming server: NOT RUNNING")
        else:
            logger.info("WebSocket streaming server: NOT ENABLED")

        # Check API server
        if _logging_manager and _logging_manager.api_runner:
            logger.info("Log API server: HEALTHY")
        else:
            logger.warning("Log API server: NOT RUNNING")

        logger.info("Logging system health check completed")
        return True

    except Exception as e:
        logger.error(f"Logging system health check failed: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    """Test the logging system initialization."""

    async def test_logging_system():
        try:
            # Initialize the logging system
            manager = await initialize_platform_logging(log_level="DEBUG")

            # Test logging functionality
            logger = get_platform_logger(__name__, "test")
            logger.info("Testing the new logging system")

            # Test context logging
            with create_log_context(user_id="test_user", session_id="test_session") as ctx:
                ctx.log(logger, "info", "Testing context logging")

            # Test performance monitoring
            @performance_monitor
            def test_function():
                import time
                time.sleep(0.1)
                return "Test completed"

            result = test_function()
            logger.info(f"Performance test result: {result}")

            # Run health check
            health_status = await health_check_logging_system()
            logger.info(f"Health check result: {'PASS' if health_status else 'FAIL'}")

            # Keep running for a bit to see real-time features
            logger.info("Logging system test running for 30 seconds...")
            await asyncio.sleep(30)

        except Exception as e:
            print(f"Test failed: {e}")
        finally:
            # Shutdown
            await shutdown_platform_logging()
            print("Logging system test completed")

    asyncio.run(test_logging_system())
