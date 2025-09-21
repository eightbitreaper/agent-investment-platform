"""
Model Context Protocol (MCP) Servers for Agent Investment Platform

This package contains MCP server implementations for various financial data sources
and analysis capabilities.
"""

__version__ = "1.0.0"
__author__ = "Agent Investment Platform"

from .base import MCPServerBase, MCPHandler, MCPError
from .manager import MCPServerManager

__all__ = [
    "MCPServerBase",
    "MCPHandler",
    "MCPError",
    "MCPServerManager",
]
