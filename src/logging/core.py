"""
Core logging infrastructure for the Agent Investment Platform.

This module provides centralized, structured logging with support for:
- Multiple output handlers (console, file, remote)
- Structured JSON logging
- Log rotation and archival
- Real-time log streaming
- Context enrichment
- Performance monitoring
"""

import logging
import logging.handlers
import json
import sys
import traceback
import threading
import time
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import queue
import socket
import os

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False


@dataclass
class LogEntry:
    """Structured log entry with enriched context."""
    timestamp: str
    level: str
    logger_name: str
    message: str
    module: str
    function: str
    line_number: int
    thread_id: int
    process_id: int
    hostname: str
    component: str
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    duration_ms: Optional[float] = None
    exception: Optional[Dict[str, Any]] = None
    extra: Optional[Dict[str, Any]] = None


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging."""

    def __init__(self, component: str = "unknown"):
        super().__init__()
        self.component = component
        self.hostname = socket.gethostname()

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        # Get exception info if present
        exception_info = None
        if record.exc_info:
            exception_info = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info)
            }

        # Create structured log entry
        log_entry = LogEntry(
            timestamp=datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            level=record.levelname,
            logger_name=record.name,
            message=record.getMessage(),
            module=record.module,
            function=record.funcName,
            line_number=record.lineno,
            thread_id=record.thread or 0,
            process_id=record.process or 0,
            hostname=self.hostname,
            component=self.component,
            trace_id=getattr(record, 'trace_id', None),
            span_id=getattr(record, 'span_id', None),
            user_id=getattr(record, 'user_id', None),
            session_id=getattr(record, 'session_id', None),
            request_id=getattr(record, 'request_id', None),
            duration_ms=getattr(record, 'duration_ms', None),
            exception=exception_info,
            extra=getattr(record, 'extra_data', None)
        )

        return json.dumps(asdict(log_entry), default=str, ensure_ascii=False)


class ConsoleFormatter(logging.Formatter):
    """Human-readable console formatter with colors."""

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }

    def __init__(self, component: str = "unknown"):
        super().__init__()
        self.component = component

    def format(self, record: logging.LogRecord) -> str:
        """Format log record for console output."""
        color = self.COLORS.get(record.levelname, '')
        reset = self.COLORS['RESET']

        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')

        base = f"{timestamp} {color}[{record.levelname:8}]{reset} [{self.component}] {record.name}: {record.getMessage()}"

        if record.exc_info:
            base += f"\n{self.formatException(record.exc_info)}"

        return base


class AsyncLogHandler:
    """Async log handler for real-time log streaming."""

    def __init__(self):
        self.subscribers: List[Callable[[LogEntry], None]] = []
        self.queue = asyncio.Queue()
        self.worker_task: Optional[asyncio.Task] = None

    async def start(self):
        """Start the async log processing worker."""
        if self.worker_task is None:
            self.worker_task = asyncio.create_task(self._process_logs())

    async def stop(self):
        """Stop the async log processing worker."""
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass
            self.worker_task = None

    def subscribe(self, callback: Callable[[LogEntry], None]):
        """Subscribe to real-time log events."""
        self.subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[LogEntry], None]):
        """Unsubscribe from real-time log events."""
        if callback in self.subscribers:
            self.subscribers.remove(callback)

    async def emit(self, log_entry: LogEntry):
        """Emit log entry to subscribers."""
        await self.queue.put(log_entry)

    async def _process_logs(self):
        """Process log queue and notify subscribers."""
        while True:
            try:
                log_entry = await self.queue.get()
                for callback in self.subscribers:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            # Use asyncio.create_task to avoid cross-loop issues
                            try:
                                await callback(log_entry)
                            except Exception as cb_error:
                                print(f"Error in async log subscriber: {cb_error}", file=sys.stderr)
                        else:
                            callback(log_entry)
                    except Exception as e:
                        # Avoid infinite recursion by not logging here
                        print(f"Error in log subscriber: {e}", file=sys.stderr)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error processing log: {e}", file=sys.stderr)


class PlatformLogHandler(logging.Handler):
    """Custom log handler for the platform logging system."""

    def __init__(self, component: str, async_handler: Optional[AsyncLogHandler] = None):
        super().__init__()
        self.component = component
        self.async_handler = async_handler
        self.setFormatter(StructuredFormatter(component))

    def emit(self, record: logging.LogRecord):
        """Emit log record to async handler."""
        if self.async_handler:
            try:
                # Convert to LogEntry
                formatter = self.formatter
                if isinstance(formatter, StructuredFormatter):
                    json_str = formatter.format(record)
                    log_data = json.loads(json_str)
                    log_entry = LogEntry(**log_data)

                    # Schedule async emit
                    loop = None
                    try:
                        loop = asyncio.get_running_loop()
                    except RuntimeError:
                        pass

                    if loop:
                        asyncio.create_task(self.async_handler.emit(log_entry))

            except Exception as e:
                # Avoid infinite recursion
                print(f"Error in PlatformLogHandler: {e}", file=sys.stderr)


class LoggerManager:
    """Central manager for platform logging configuration."""

    def __init__(self):
        self.handlers: Dict[str, logging.Handler] = {}
        self.async_handler = None  # Only create when needed
        self.async_enabled = False
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        self._performance_metrics = {}
        self._setup_root_logger()

    def _setup_root_logger(self):
        """Setup root logger configuration."""
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)

        # Remove existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

    def get_logger(self, name: str, component: Optional[str] = None) -> logging.Logger:
        """Get configured logger for a component."""
        logger = logging.getLogger(name)

        if component is None:
            component = name.split('.')[0] if '.' in name else name

        # Add handlers if not already added
        handler_key = f"{name}_{component}"
        if handler_key not in self.handlers:
            self._configure_logger(logger, component)
            # Store a dummy value to track configured loggers
            self.handlers[handler_key] = logging.Handler()  # type: ignore

        return logger

    def _configure_logger(self, logger: logging.Logger, component: str):
        """Configure logger with appropriate handlers."""
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(ConsoleFormatter(component))
        console_handler.setLevel(logging.INFO)
        logger.addHandler(console_handler)

        # File handler with rotation
        log_file = self.log_dir / f"{component}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(StructuredFormatter(component))
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)

        # Platform handler for real-time streaming (only if async enabled)
        if self.async_enabled and self.async_handler:
            platform_handler = PlatformLogHandler(component, self.async_handler)
            platform_handler.setLevel(logging.DEBUG)
            logger.addHandler(platform_handler)

        # Error file handler
        error_file = self.log_dir / f"{component}_errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10,
            encoding='utf-8'
        )
        error_handler.setFormatter(StructuredFormatter(component))
        error_handler.setLevel(logging.ERROR)
        logger.addHandler(error_handler)

    async def start_async_processing(self):
        """Start async log processing."""
        if not self.async_handler:
            self.async_handler = AsyncLogHandler()
        self.async_enabled = True
        await self.async_handler.start()

    async def stop_async_processing(self):
        """Stop async log processing."""
        if self.async_handler:
            await self.async_handler.stop()
        self.async_enabled = False

    def subscribe_to_logs(self, callback: Callable[[LogEntry], None]):
        """Subscribe to real-time log events."""
        if not self.async_handler:
            self.async_handler = AsyncLogHandler()
        self.async_handler.subscribe(callback)

    def unsubscribe_from_logs(self, callback: Callable[[LogEntry], None]):
        """Unsubscribe from real-time log events."""
        if self.async_handler:
            self.async_handler.unsubscribe(callback)

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "log_handlers": len(self.handlers),
            "async_queue_size": self.async_handler.queue.qsize() if self.async_handler and self.async_handler.queue else 0,
            "subscribers": len(self.async_handler.subscribers) if self.async_handler else 0
        }

        if PSUTIL_AVAILABLE:
            process = psutil.Process()
            metrics.update({
                "memory_usage_mb": process.memory_info().rss / 1024 / 1024,
                "cpu_percent": process.cpu_percent(),
                "open_files": len(process.open_files())
            })

        return metrics


# Global logger manager instance
_logger_manager = LoggerManager()


def get_logger(name: str, component: Optional[str] = None) -> logging.Logger:
    """Get configured logger for a component."""
    return _logger_manager.get_logger(name, component)


def configure_logging(level: str = "INFO",
                     component: str = "platform",
                     enable_async: bool = False) -> logging.Logger:
    """Configure platform logging system."""
    # Set global logging level
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.getLogger().setLevel(numeric_level)

    # Set async enabled flag
    _logger_manager.async_enabled = enable_async

    # Only start async processing if explicitly enabled
    if enable_async:
        try:
            loop = asyncio.get_event_loop()
            if not loop.is_running():
                loop.run_until_complete(_logger_manager.start_async_processing())
            else:
                asyncio.create_task(_logger_manager.start_async_processing())
        except RuntimeError:
            # No event loop, will start when one is available
            pass

    return get_logger(__name__, component)


def subscribe_to_logs(callback: Callable[[LogEntry], None]):
    """Subscribe to real-time log events."""
    _logger_manager.subscribe_to_logs(callback)


def unsubscribe_from_logs(callback: Callable[[LogEntry], None]):
    """Unsubscribe from real-time log events."""
    _logger_manager.unsubscribe_from_logs(callback)


def get_performance_metrics() -> Dict[str, Any]:
    """Get logging system performance metrics."""
    return _logger_manager.get_performance_metrics()


class LogContext:
    """Context manager for enriched logging."""

    def __init__(self, **context):
        self.context = context
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = (time.time() - self.start_time) * 1000
            self.context['duration_ms'] = duration

    def log(self, logger: logging.Logger, level: str, message: str, **extra):
        """Log with enriched context."""
        # Merge context with extra data
        log_extra = {**self.context, **extra}

        # Create log record with extra context
        record = logger.makeRecord(
            logger.name, getattr(logging, level.upper()),
            "", 0, message, (), None
        )

        # Add context to record
        for key, value in log_extra.items():
            setattr(record, key, value)

        logger.handle(record)


def log_performance(func):
    """Decorator for performance logging."""
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__, func.__module__.split('.')[0])
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
            duration = (time.time() - start_time) * 1000
            # Use extra parameter for additional data
            extra = {
                'duration_ms': duration,
                'function': func.__name__,
                'module': func.__module__
            }
            logger.info(f"Function {func.__name__} completed", extra=extra)
            return result
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            # Use extra parameter for additional data
            extra = {
                'duration_ms': duration,
                'function': func.__name__,
                'module': func.__module__,
                'error': str(e)
            }
            logger.error(f"Function {func.__name__} failed: {e}", exc_info=True, extra=extra)
            raise

    return wrapper


if __name__ == "__main__":
    # Example usage
    logger = configure_logging("DEBUG", "test-component")

    logger.info("Testing structured logging")
    logger.warning("This is a warning message")

    try:
        raise ValueError("Test exception")
    except Exception:
        logger.error("Caught exception", exc_info=True)

    # Test context logging
    with LogContext(user_id="123", request_id="req-456") as ctx:
        ctx.log(logger, "info", "Processing request")

    # Test performance decorator
    @log_performance
    def test_function():
        time.sleep(0.1)
        return "done"

    test_function()

    print("Performance metrics:", get_performance_metrics())
