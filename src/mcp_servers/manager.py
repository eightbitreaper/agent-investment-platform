"""
MCP Server Manager for the Agent Investment Platform.

This module provides orchestration, health monitoring, and lifecycle management
for all MCP servers in the platform.
"""

import asyncio
import json
import logging
import os
import signal
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
# import yaml  # Will be added to requirements
# import psutil  # Will be added to requirements


@dataclass
class ServerProcess:
    """Represents a running MCP server process."""
    name: str
    process: subprocess.Popen
    config: Dict[str, Any]
    start_time: float
    restart_count: int = 0
    last_health_check: Optional[float] = None
    health_status: str = "unknown"  # unknown, healthy, unhealthy, stopped


@dataclass
class ServerMetrics:
    """Metrics for a running MCP server."""
    name: str
    pid: Optional[int]
    memory_usage_mb: float
    cpu_percent: float
    response_time_ms: Optional[float]
    error_count: int
    request_count: int
    uptime_seconds: float
    restart_count: int
    last_health_check: Optional[float]
    health_status: str


class MCPServerManager:
    """
    Manages the lifecycle of all MCP servers in the Agent Investment Platform.

    This class handles:
    - Starting and stopping MCP servers
    - Health monitoring and auto-restart
    - Configuration management
    - Metrics collection
    - Logging and monitoring
    """

    def __init__(self, config_path: str = "config/mcp-servers.json"):
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.servers: Dict[str, ServerProcess] = {}
        self.logger = logging.getLogger(self.__class__.__name__)
        self.shutdown_event = asyncio.Event()
        self.health_check_task: Optional[asyncio.Task] = None

        # Setup logging
        self._setup_logging()

        # Load configuration
        self._load_config()

        # Setup signal handlers
        self._setup_signal_handlers()

    def _setup_logging(self):
        """Setup logging configuration."""
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stderr)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def _load_config(self):
        """Load MCP servers configuration."""
        try:
            if not self.config_path.exists():
                raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)

            self.logger.info(f"Loaded configuration for {len(self.config.get('mcpServers', {}))} servers")

        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            raise

    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating shutdown...")
            asyncio.create_task(self.shutdown())

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def _expand_env_vars(self, value: Any) -> Any:
        """Recursively expand environment variables in configuration values."""
        if isinstance(value, str):
            # Expand ${VAR_NAME} format
            import re
            pattern = r'\$\{([^}]+)\}'
            matches = re.findall(pattern, value)
            for match in matches:
                env_value = os.environ.get(match, f"${{{match}}}")
                value = value.replace(f"${{{match}}}", env_value)
            return value
        elif isinstance(value, dict):
            return {k: self._expand_env_vars(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._expand_env_vars(item) for item in value]
        else:
            return value

    async def start_server(self, server_name: str) -> bool:
        """
        Start a specific MCP server.

        Args:
            server_name: Name of the server to start

        Returns:
            True if server started successfully, False otherwise
        """
        try:
            server_config = self.config.get("mcpServers", {}).get(server_name)
            if not server_config:
                self.logger.error(f"No configuration found for server: {server_name}")
                return False

            if not server_config.get("enabled", True):
                self.logger.info(f"Server {server_name} is disabled, skipping")
                return False

            if server_name in self.servers:
                self.logger.warning(f"Server {server_name} is already running")
                return True

            # Expand environment variables in configuration
            expanded_config = self._expand_env_vars(server_config)

            # Prepare command and environment
            command = [expanded_config["command"]] + expanded_config.get("args", [])
            env = os.environ.copy()
            env.update(expanded_config.get("env", {}))

            # Start the process
            self.logger.info(f"Starting server {server_name} with command: {' '.join(command)}")

            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True,
                bufsize=0
            )

            # Store server process information
            server_process = ServerProcess(
                name=server_name,
                process=process,
                config=expanded_config,
                start_time=time.time()
            )

            self.servers[server_name] = server_process

            # Wait a bit to check if process started successfully
            await asyncio.sleep(0.5)

            if process.poll() is not None:
                # Process exited immediately
                stdout, stderr = process.communicate()
                self.logger.error(f"Server {server_name} failed to start:")
                self.logger.error(f"STDOUT: {stdout}")
                self.logger.error(f"STDERR: {stderr}")
                del self.servers[server_name]
                return False

            self.logger.info(f"Server {server_name} started successfully (PID: {process.pid})")
            return True

        except Exception as e:
            self.logger.error(f"Error starting server {server_name}: {e}")
            return False

    async def stop_server(self, server_name: str, timeout: float = 10.0) -> bool:
        """
        Stop a specific MCP server.

        Args:
            server_name: Name of the server to stop
            timeout: Timeout in seconds for graceful shutdown

        Returns:
            True if server stopped successfully, False otherwise
        """
        try:
            server_process = self.servers.get(server_name)
            if not server_process:
                self.logger.warning(f"Server {server_name} is not running")
                return True

            process = server_process.process

            self.logger.info(f"Stopping server {server_name} (PID: {process.pid})")

            # Try graceful shutdown first
            process.terminate()

            try:
                await asyncio.wait_for(
                    asyncio.create_task(self._wait_for_process(process)),
                    timeout=timeout
                )
                self.logger.info(f"Server {server_name} stopped gracefully")
            except asyncio.TimeoutError:
                # Force kill if graceful shutdown failed
                self.logger.warning(f"Server {server_name} did not stop gracefully, force killing")
                process.kill()
                await asyncio.create_task(self._wait_for_process(process))

            del self.servers[server_name]
            return True

        except Exception as e:
            self.logger.error(f"Error stopping server {server_name}: {e}")
            return False

    async def _wait_for_process(self, process: subprocess.Popen):
        """Wait for a process to terminate."""
        while process.poll() is None:
            await asyncio.sleep(0.1)

    async def restart_server(self, server_name: str) -> bool:
        """
        Restart a specific MCP server.

        Args:
            server_name: Name of the server to restart

        Returns:
            True if server restarted successfully, False otherwise
        """
        self.logger.info(f"Restarting server {server_name}")

        # Stop the server
        await self.stop_server(server_name)

        # Wait a bit before restarting
        restart_delay = self.config.get("global_settings", {}).get("restart_delay", 5000) / 1000
        await asyncio.sleep(restart_delay)

        # Start the server
        success = await self.start_server(server_name)

        if success and server_name in self.servers:
            self.servers[server_name].restart_count += 1

        return success

    async def start_all_servers(self) -> Dict[str, bool]:
        """
        Start all enabled MCP servers.

        Returns:
            Dictionary mapping server names to their start success status
        """
        self.logger.info("Starting all MCP servers...")

        results = {}
        server_configs = self.config.get("mcpServers", {})

        for server_name in server_configs:
            results[server_name] = await self.start_server(server_name)

        successful = sum(1 for success in results.values() if success)
        total = len(results)

        self.logger.info(f"Started {successful}/{total} servers successfully")
        return results

    async def stop_all_servers(self) -> Dict[str, bool]:
        """
        Stop all running MCP servers.

        Returns:
            Dictionary mapping server names to their stop success status
        """
        self.logger.info("Stopping all MCP servers...")

        results = {}
        server_names = list(self.servers.keys())

        # Stop servers in parallel
        tasks = []
        for server_name in server_names:
            task = asyncio.create_task(self.stop_server(server_name))
            tasks.append((server_name, task))

        for server_name, task in tasks:
            results[server_name] = await task

        successful = sum(1 for success in results.values() if success)
        total = len(results)

        self.logger.info(f"Stopped {successful}/{total} servers successfully")
        return results

    async def get_server_status(self, server_name: str) -> Optional[Dict[str, Any]]:
        """
        Get status information for a specific server.

        Args:
            server_name: Name of the server

        Returns:
            Dictionary containing server status information
        """
        server_process = self.servers.get(server_name)
        if not server_process:
            return {
                "name": server_name,
                "status": "stopped",
                "pid": None,
                "uptime": 0,
                "restart_count": 0
            }

        process = server_process.process
        uptime = time.time() - server_process.start_time

        status = {
            "name": server_name,
            "status": "running" if process.poll() is None else "stopped",
            "pid": process.pid,
            "uptime": uptime,
            "restart_count": server_process.restart_count,
            "health_status": server_process.health_status,
            "last_health_check": server_process.last_health_check
        }

        # Add process metrics if available
        try:
            if process.poll() is None:
                # TODO: Add psutil dependency for process monitoring
                # psutil_process = psutil.Process(process.pid)
                # memory_info = psutil_process.memory_info()
                # status.update({
                #     "memory_usage_mb": memory_info.rss / 1024 / 1024,
                #     "cpu_percent": psutil_process.cpu_percent()
                # })
                pass
        except Exception:
            pass

        return status

    async def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status information for all servers.

        Returns:
            Dictionary mapping server names to their status information
        """
        status = {}
        server_configs = self.config.get("mcpServers", {})

        for server_name in server_configs:
            status[server_name] = await self.get_server_status(server_name)

        return status

    async def health_check_server(self, server_name: str) -> bool:
        """
        Perform health check on a specific server.

        Args:
            server_name: Name of the server to check

        Returns:
            True if server is healthy, False otherwise
        """
        try:
            server_process = self.servers.get(server_name)
            if not server_process:
                return False

            process = server_process.process

            # Check if process is still running
            if process.poll() is not None:
                server_process.health_status = "stopped"
                return False

            # Try to send a ping message
            ping_message = {
                "jsonrpc": "2.0",
                "id": f"health_check_{time.time()}",
                "method": "ping",
                "params": {}
            }

            # Send ping and wait for response (with timeout)
            if process.stdin:
                process.stdin.write(json.dumps(ping_message) + "\n")
                process.stdin.flush()

            # For now, assume healthy if process is running
            # TODO: Implement actual ping response handling
            server_process.health_status = "healthy"
            server_process.last_health_check = time.time()

            return True

        except Exception as e:
            self.logger.error(f"Health check failed for server {server_name}: {e}")
            if server_name in self.servers:
                self.servers[server_name].health_status = "unhealthy"
            return False

    async def health_check_loop(self):
        """Main health check loop."""
        health_check_interval = self.config.get("global_settings", {}).get("health_check_interval", 60000) / 1000
        auto_restart = self.config.get("global_settings", {}).get("auto_restart", True)
        max_restart_attempts = self.config.get("global_settings", {}).get("max_restart_attempts", 3)

        self.logger.info(f"Starting health check loop (interval: {health_check_interval}s)")

        while not self.shutdown_event.is_set():
            try:
                for server_name in list(self.servers.keys()):
                    healthy = await self.health_check_server(server_name)

                    server_process = self.servers.get(server_name)
                    if not healthy and server_process and auto_restart:
                        if server_process.restart_count < max_restart_attempts:
                            self.logger.warning(f"Server {server_name} is unhealthy, restarting...")
                            await self.restart_server(server_name)
                        else:
                            self.logger.error(f"Server {server_name} exceeded max restart attempts ({max_restart_attempts})")

                await asyncio.sleep(health_check_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(5)  # Short delay before retrying

    async def run(self):
        """
        Main entry point for the MCP Server Manager.

        This starts all enabled servers and runs the health check loop.
        """
        try:
            self.logger.info("Starting MCP Server Manager...")

            # Start all servers
            await self.start_all_servers()

            # Start health check loop
            self.health_check_task = asyncio.create_task(self.health_check_loop())

            # Wait for shutdown signal
            await self.shutdown_event.wait()

        except Exception as e:
            self.logger.error(f"Error in main run loop: {e}")
        finally:
            await self.cleanup()

    async def shutdown(self):
        """Gracefully shutdown all servers and manager."""
        self.logger.info("Shutting down MCP Server Manager...")

        # Signal shutdown
        self.shutdown_event.set()

        # Cancel health check task
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass

        # Stop all servers
        await self.stop_all_servers()

    async def cleanup(self):
        """Cleanup resources."""
        self.logger.info("Cleaning up MCP Server Manager...")


async def main():
    """Main entry point for running the MCP Server Manager."""
    import argparse

    parser = argparse.ArgumentParser(description="MCP Server Manager for Agent Investment Platform")
    parser.add_argument(
        "--config",
        default="config/mcp-servers.json",
        help="Path to MCP servers configuration file"
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level"
    )

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create and run manager
    manager = MCPServerManager(config_path=args.config)

    try:
        await manager.run()
    except KeyboardInterrupt:
        logging.info("Received interrupt signal")
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
