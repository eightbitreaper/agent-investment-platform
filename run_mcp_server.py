#!/usr/bin/env python3
"""
MCP Server Runner for the Agent Investment Platform.

This script provides a command-line interface to run individual MCP servers
or manage all servers through the MCP Server Manager.
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.mcp_servers.manager import MCPServerManager
from src.mcp_servers.stock_data_server import StockDataServer
from src.mcp_servers.analysis_engine_server import AnalysisEngineServer
from src.mcp_servers.report_generator_server import ReportGeneratorServer


def setup_logging(level: str = "INFO"):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stderr),
            logging.FileHandler('logs/mcp-servers.log', mode='a')
        ]
    )


async def run_individual_server(server_name: str):
    """Run an individual MCP server."""
    servers = {
        "stock-data": StockDataServer,
        "analysis-engine": AnalysisEngineServer,
        "report-generator": ReportGeneratorServer,
    }

    server_class = servers.get(server_name)
    if not server_class:
        available = ", ".join(servers.keys())
        print(f"Error: Unknown server '{server_name}'. Available servers: {available}", file=sys.stderr)
        return 1

    try:
        server = server_class()
        await server.run_stdio()
        return 0
    except KeyboardInterrupt:
        logging.info(f"Server {server_name} interrupted by user")
        return 0
    except Exception as e:
        logging.error(f"Error running server {server_name}: {e}")
        return 1


async def run_manager(config_path: str):
    """Run the MCP Server Manager."""
    try:
        manager = MCPServerManager(config_path)
        await manager.run()
        return 0
    except KeyboardInterrupt:
        logging.info("MCP Server Manager interrupted by user")
        return 0
    except Exception as e:
        logging.error(f"Error running MCP Server Manager: {e}")
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="MCP Server Runner for Agent Investment Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --server stock-data                    # Run stock data server
  %(prog)s --server analysis-engine               # Run analysis engine server
  %(prog)s --server report-generator              # Run report generator server
  %(prog)s --manager                              # Run server manager (all servers)
  %(prog)s --manager --config custom-config.json # Run with custom config
        """
    )

    # Server selection
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--server",
        choices=["stock-data", "analysis-engine", "report-generator"],
        help="Run a specific MCP server"
    )
    group.add_argument(
        "--manager",
        action="store_true",
        help="Run the MCP Server Manager (manages all servers)"
    )

    # Configuration
    parser.add_argument(
        "--config",
        default="config/mcp-servers.json",
        help="Path to MCP servers configuration file (for manager mode)"
    )

    # Logging
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level"
    )

    # List available servers
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available servers and exit"
    )

    args = parser.parse_args()

    if args.list:
        print("Available MCP Servers:")
        print("  stock-data        - Real-time stock data, prices, and financial metrics")
        print("  analysis-engine   - Core financial analysis and strategy engine")
        print("  report-generator  - Automated investment report generation")
        print("\nServer Manager:")
        print("  --manager         - Run all servers with orchestration and monitoring")
        return 0

    # Setup logging
    setup_logging(args.log_level)

    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)

    try:
        if args.server:
            return asyncio.run(run_individual_server(args.server))
        elif args.manager:
            return asyncio.run(run_manager(args.config))
    except KeyboardInterrupt:
        logging.info("Received interrupt signal")
        return 0
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
