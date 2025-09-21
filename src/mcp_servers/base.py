"""
Base classes and utilities for MCP servers in the Agent Investment Platform.

This module provides the foundational components for implementing Model Context Protocol
servers, including base classes, error handling, and communication protocols.
"""

import asyncio
import json
import logging
import sys
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Union, Callable, AsyncGenerator
from enum import Enum
import traceback


class MCPMessageType(Enum):
    """MCP message types according to specification."""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"


class MCPMethodType(Enum):
    """Standard MCP method types."""
    INITIALIZE = "initialize"
    PING = "ping"
    CALL_TOOL = "tools/call"
    LIST_TOOLS = "tools/list"
    GET_PROMPT = "prompts/get"
    LIST_PROMPTS = "prompts/list"
    LIST_RESOURCES = "resources/list"
    READ_RESOURCE = "resources/read"
    SUBSCRIBE = "resources/subscribe"
    UNSUBSCRIBE = "resources/unsubscribe"


@dataclass
class MCPMessage:
    """Base MCP message structure."""
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None
    method: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        data = asdict(self)
        return {k: v for k, v in data.items() if v is not None}

    def to_json(self) -> str:
        """Convert message to JSON string."""
        return json.dumps(self.to_dict())


@dataclass
class MCPTool:
    """MCP tool definition."""
    name: str
    description: str
    inputSchema: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to dictionary."""
        return asdict(self)


@dataclass
class MCPPrompt:
    """MCP prompt definition."""
    name: str
    description: str
    arguments: Optional[List[Dict[str, Any]]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert prompt to dictionary."""
        return asdict(self)


@dataclass
class MCPResource:
    """MCP resource definition."""
    uri: str
    name: str
    description: Optional[str] = None
    mimeType: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert resource to dictionary."""
        return asdict(self)


class MCPError(Exception):
    """Base exception for MCP server errors."""

    def __init__(self, code: int, message: str, data: Optional[Any] = None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(f"MCP Error {code}: {message}")


class MCPValidationError(MCPError):
    """Error for invalid requests or parameters."""

    def __init__(self, message: str, data: Optional[Any] = None):
        super().__init__(-32602, message, data)


class MCPMethodNotFoundError(MCPError):
    """Error for unknown methods."""

    def __init__(self, method: str):
        super().__init__(-32601, f"Method not found: {method}")


class MCPInternalError(MCPError):
    """Error for internal server errors."""

    def __init__(self, message: str, data: Optional[Any] = None):
        super().__init__(-32603, message, data)


class MCPHandler:
    """Base handler for MCP method implementations."""

    def __init__(self, server: 'MCPServerBase'):
        self.server = server
        self.logger = logging.getLogger(f"{server.__class__.__name__}.{self.__class__.__name__}")

    async def handle_method(self, method: str, params: Optional[Dict[str, Any]]) -> Any:
        """Handle a specific MCP method."""
        handler_name = f"handle_{method.replace('/', '_').replace('-', '_')}"
        handler = getattr(self, handler_name, None)

        if not handler:
            raise MCPMethodNotFoundError(method)

        try:
            return await handler(params or {})
        except MCPError:
            raise
        except Exception as e:
            self.logger.error(f"Error in {method}: {str(e)}", exc_info=True)
            raise MCPInternalError(f"Internal error in {method}: {str(e)}")

    async def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialize method."""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": self.server.get_capabilities(),
            "serverInfo": {
                "name": self.server.name,
                "version": self.server.version
            }
        }

    async def handle_ping(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ping method."""
        return {"pong": True, "timestamp": time.time()}


class MCPServerBase(ABC):
    """
    Base class for MCP servers in the Agent Investment Platform.

    This class provides the foundational structure for implementing MCP servers,
    including message handling, error management, and protocol compliance.
    """

    def __init__(self, name: str, version: str = "1.0.0", description: str = ""):
        self.name = name
        self.version = version
        self.description = description
        self.logger = logging.getLogger(self.__class__.__name__)
        self.handlers: Dict[str, MCPHandler] = {}
        self.tools: Dict[str, MCPTool] = {}
        self.prompts: Dict[str, MCPPrompt] = {}
        self.resources: Dict[str, MCPResource] = {}
        self.initialized = False

        # Setup logging
        self._setup_logging()

        # Register default handlers
        self._register_default_handlers()

        # Register server-specific tools, prompts, and resources
        self._register_capabilities()

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

    def _register_default_handlers(self):
        """Register default MCP handlers."""
        default_handler = MCPHandler(self)
        self.handlers["default"] = default_handler

    @abstractmethod
    def _register_capabilities(self):
        """Register server-specific tools, prompts, and resources."""
        pass

    def register_tool(self, tool: MCPTool, handler: Callable):
        """Register a tool with its handler."""
        self.tools[tool.name] = tool
        setattr(self.handlers.get("default"), f"handle_tools_call_{tool.name}", handler)

    def register_prompt(self, prompt: MCPPrompt, handler: Callable):
        """Register a prompt with its handler."""
        self.prompts[prompt.name] = prompt
        setattr(self.handlers.get("default"), f"handle_prompts_get_{prompt.name}", handler)

    def register_resource(self, resource: MCPResource, handler: Callable):
        """Register a resource with its handler."""
        self.resources[resource.uri] = resource
        setattr(self.handlers.get("default"), f"handle_resources_read_{resource.name}", handler)

    def get_capabilities(self) -> Dict[str, Any]:
        """Get server capabilities."""
        capabilities = {}

        if self.tools:
            capabilities["tools"] = {"listChanged": False}

        if self.prompts:
            capabilities["prompts"] = {"listChanged": False}

        if self.resources:
            capabilities["resources"] = {"subscribe": True, "listChanged": False}

        return capabilities

    async def handle_message(self, message_data: str) -> Optional[str]:
        """
        Handle incoming MCP message.

        Args:
            message_data: JSON string containing the MCP message

        Returns:
            JSON response string or None for notifications
        """
        try:
            data = json.loads(message_data)
            message = MCPMessage(**data)

            # Handle different message types
            if message.method:
                return await self._handle_request(message)
            elif message.result is not None or message.error is not None:
                return await self._handle_response(message)
            else:
                await self._handle_notification(message)
                return None

        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON received: {e}")
            error_response = MCPMessage(
                id=None,
                error={"code": -32700, "message": "Parse error"}
            )
            return error_response.to_json()
        except Exception as e:
            self.logger.error(f"Error handling message: {e}", exc_info=True)
            error_response = MCPMessage(
                id=getattr(message, 'id', None) if 'message' in locals() else None,
                error={"code": -32603, "message": f"Internal error: {str(e)}"}
            )
            return error_response.to_json()

    async def _handle_request(self, message: MCPMessage) -> str:
        """Handle request messages."""
        try:
            if not message.method:
                raise MCPValidationError("Method is required for requests")

            # Route to appropriate handler
            handler = self._get_handler_for_method(message.method)
            result = await handler.handle_method(message.method, message.params)

            response = MCPMessage(
                id=message.id,
                result=result
            )
            return response.to_json()

        except MCPError as e:
            error_response = MCPMessage(
                id=message.id,
                error={"code": e.code, "message": e.message, "data": e.data}
            )
            return error_response.to_json()
        except Exception as e:
            self.logger.error(f"Unexpected error in request handler: {e}", exc_info=True)
            error_response = MCPMessage(
                id=message.id,
                error={"code": -32603, "message": f"Internal error: {str(e)}"}
            )
            return error_response.to_json()

    async def _handle_response(self, message: MCPMessage) -> str:
        """Handle response messages."""
        # Responses are typically handled by clients, not servers
        self.logger.debug(f"Received response: {message}")
        return ""

    async def _handle_notification(self, message: MCPMessage):
        """Handle notification messages."""
        self.logger.debug(f"Received notification: {message}")

    def _get_handler_for_method(self, method: str) -> MCPHandler:
        """Get the appropriate handler for a method."""
        # For now, use default handler for all methods
        # Can be extended to support specialized handlers
        return self.handlers["default"]

    async def run_stdio(self):
        """
        Run the MCP server using stdio transport.

        This is the main entry point for MCP servers using standard input/output
        for communication with the client.
        """
        self.logger.info(f"Starting {self.name} MCP server...")

        try:
            while True:
                try:
                    # Read message from stdin
                    line = await asyncio.get_event_loop().run_in_executor(
                        None, sys.stdin.readline
                    )

                    if not line:
                        break

                    line = line.strip()
                    if not line:
                        continue

                    # Process message
                    response = await self.handle_message(line)

                    # Send response if any
                    if response:
                        print(response, flush=True)

                except KeyboardInterrupt:
                    self.logger.info("Received interrupt signal, shutting down...")
                    break
                except EOFError:
                    self.logger.info("EOF received, shutting down...")
                    break
                except Exception as e:
                    self.logger.error(f"Error in main loop: {e}", exc_info=True)

        except Exception as e:
            self.logger.error(f"Fatal error in server: {e}", exc_info=True)
        finally:
            await self.cleanup()

    async def cleanup(self):
        """Cleanup resources when shutting down."""
        self.logger.info(f"Shutting down {self.name} MCP server...")

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check and return status."""
        pass


def create_tool_schema(name: str, description: str, properties: Dict[str, Any],
                      required: Optional[List[str]] = None) -> Dict[str, Any]:
    """Helper function to create tool input schema."""
    return {
        "type": "object",
        "properties": properties,
        "required": required or []
    }


def create_error_response(code: int, message: str, request_id: Optional[Union[str, int]] = None) -> str:
    """Helper function to create error response."""
    response = MCPMessage(
        id=request_id,
        error={"code": code, "message": message}
    )
    return response.to_json()
