"""
Logging configuration loader and manager.

This module handles loading and applying logging configuration from YAML files
and environment variables, providing a centralized way to manage logging settings.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import logging

from .core import get_logger


@dataclass
class HandlerConfig:
    """Configuration for a log handler."""
    enabled: bool = True
    level: str = "INFO"
    format: str = "simple"
    rotation: Optional[Dict[str, Any]] = None
    # Handler-specific configuration
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LoggingConfig:
    """Complete logging configuration."""
    log_level: str = "INFO"
    structured_logging: bool = True
    colored_console: bool = True
    max_log_file_size_mb: int = 50
    log_backup_count: int = 10

    component_levels: Dict[str, str] = field(default_factory=dict)
    handlers: Dict[str, HandlerConfig] = field(default_factory=dict)
    formats: Dict[str, str] = field(default_factory=dict)

    performance: Dict[str, Any] = field(default_factory=dict)
    realtime: Dict[str, Any] = field(default_factory=dict)
    alerting: Dict[str, Any] = field(default_factory=dict)
    retention: Dict[str, Any] = field(default_factory=dict)
    security: Dict[str, Any] = field(default_factory=dict)
    development: Dict[str, Any] = field(default_factory=dict)
    integrations: Dict[str, Any] = field(default_factory=dict)


class LoggingConfigLoader:
    """Load and manage logging configuration."""

    def __init__(self, config_path: Optional[str] = None):
        self.logger = get_logger(__name__, "logging_config")
        self.config_path = config_path or self._find_config_file()
        self.config: Optional[LoggingConfig] = None

    def _find_config_file(self) -> str:
        """Find the logging configuration file."""
        possible_paths = [
            Path("config/logging-config.yaml"),
            Path("logging-config.yaml"),
            Path("config/logging.yaml"),
            Path("logging.yaml")
        ]

        for path in possible_paths:
            if path.exists():
                return str(path)

        # Return default path even if it doesn't exist
        return "config/logging-config.yaml"

    def load_config(self) -> LoggingConfig:
        """Load configuration from YAML file and environment variables."""
        config_data = {}

        # Load from YAML file if it exists
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f) or {}
                self.logger.info(f"Loaded logging configuration from {self.config_path}")
            except Exception as e:
                self.logger.error(f"Failed to load configuration from {self.config_path}: {e}")
        else:
            self.logger.warning(f"Configuration file not found: {self.config_path}, using defaults")

        # Override with environment variables
        config_data = self._apply_env_overrides(config_data)

        # Convert to LoggingConfig object
        self.config = self._convert_to_dataclass(config_data)

        return self.config

    def _apply_env_overrides(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides to configuration."""
        # Global settings
        if 'LOG_LEVEL' in os.environ:
            config_data['LOG_LEVEL'] = os.environ['LOG_LEVEL']

        if 'STRUCTURED_LOGGING' in os.environ:
            config_data['STRUCTURED_LOGGING'] = os.environ['STRUCTURED_LOGGING'].lower() == 'true'

        if 'COLORED_CONSOLE' in os.environ:
            config_data['COLORED_CONSOLE'] = os.environ['COLORED_CONSOLE'].lower() == 'true'

        # Component-specific levels
        component_levels = config_data.get('component_levels', {})
        for key, value in os.environ.items():
            if key.startswith('LOG_LEVEL_'):
                component = key[10:].lower()  # Remove 'LOG_LEVEL_' prefix
                component_levels[component] = value

        if component_levels:
            config_data['component_levels'] = component_levels

        # Handler settings
        handlers = config_data.get('handlers', {})

        # Console handler
        if 'CONSOLE_LOG_ENABLED' in os.environ:
            handlers.setdefault('console', {})['enabled'] = os.environ['CONSOLE_LOG_ENABLED'].lower() == 'true'

        if 'CONSOLE_LOG_LEVEL' in os.environ:
            handlers.setdefault('console', {})['level'] = os.environ['CONSOLE_LOG_LEVEL']

        # File handler
        if 'FILE_LOG_ENABLED' in os.environ:
            handlers.setdefault('file', {})['enabled'] = os.environ['FILE_LOG_ENABLED'].lower() == 'true'

        if 'FILE_LOG_LEVEL' in os.environ:
            handlers.setdefault('file', {})['level'] = os.environ['FILE_LOG_LEVEL']

        # Remote logging
        if 'ELASTICSEARCH_ENABLED' in os.environ:
            handlers.setdefault('elasticsearch', {})['enabled'] = os.environ['ELASTICSEARCH_ENABLED'].lower() == 'true'

        if 'ELASTICSEARCH_HOSTS' in os.environ:
            hosts = os.environ['ELASTICSEARCH_HOSTS'].split(',')
            handlers.setdefault('elasticsearch', {})['hosts'] = hosts

        if handlers:
            config_data['handlers'] = handlers

        # Performance settings
        performance = config_data.get('performance', {})

        if 'PERFORMANCE_LOGGING' in os.environ:
            performance['function_timing'] = os.environ['PERFORMANCE_LOGGING'].lower() == 'true'

        if 'SLOW_OPERATION_THRESHOLD' in os.environ:
            performance['slow_operation_threshold_ms'] = int(os.environ['SLOW_OPERATION_THRESHOLD'])

        if performance:
            config_data['performance'] = performance

        # Real-time settings
        realtime = config_data.get('realtime', {})

        if 'WEBSOCKET_LOGGING' in os.environ:
            realtime['websocket_enabled'] = os.environ['WEBSOCKET_LOGGING'].lower() == 'true'

        if 'WEBSOCKET_PORT' in os.environ:
            realtime['websocket_port'] = int(os.environ['WEBSOCKET_PORT'])

        if realtime:
            config_data['realtime'] = realtime

        return config_data

    def _convert_to_dataclass(self, config_data: Dict[str, Any]) -> LoggingConfig:
        """Convert configuration dictionary to LoggingConfig dataclass."""
        # Convert handler configs
        handlers = {}
        for name, handler_data in config_data.get('handlers', {}).items():
            handlers[name] = HandlerConfig(
                enabled=handler_data.get('enabled', True),
                level=handler_data.get('level', 'INFO'),
                format=handler_data.get('format', 'simple'),
                rotation=handler_data.get('rotation'),
                config=handler_data
            )

        return LoggingConfig(
            log_level=config_data.get('LOG_LEVEL', 'INFO'),
            structured_logging=config_data.get('STRUCTURED_LOGGING', True),
            colored_console=config_data.get('COLORED_CONSOLE', True),
            max_log_file_size_mb=config_data.get('MAX_LOG_FILE_SIZE_MB', 50),
            log_backup_count=config_data.get('LOG_BACKUP_COUNT', 10),

            component_levels=config_data.get('component_levels', {}),
            handlers=handlers,
            formats=config_data.get('formats', {}),

            performance=config_data.get('performance', {}),
            realtime=config_data.get('realtime', {}),
            alerting=config_data.get('alerting', {}),
            retention=config_data.get('retention', {}),
            security=config_data.get('security', {}),
            development=config_data.get('development', {}),
            integrations=config_data.get('integrations', {})
        )

    def get_component_level(self, component: str) -> str:
        """Get logging level for a specific component."""
        if not self.config:
            return "INFO"

        return self.config.component_levels.get(component, self.config.log_level)

    def is_handler_enabled(self, handler_name: str) -> bool:
        """Check if a handler is enabled."""
        if not self.config:
            return True

        handler = self.config.handlers.get(handler_name)
        return handler.enabled if handler else False

    def get_handler_config(self, handler_name: str) -> Optional[HandlerConfig]:
        """Get configuration for a specific handler."""
        if not self.config:
            return None

        return self.config.handlers.get(handler_name)

    def should_mask_sensitive_data(self) -> bool:
        """Check if sensitive data should be masked."""
        if not self.config:
            return True

        return self.config.security.get('mask_sensitive_data', True)

    def get_sensitive_patterns(self) -> List[str]:
        """Get patterns for sensitive data masking."""
        if not self.config:
            return []

        return self.config.security.get('sensitive_patterns', [])

    def get_mask_placeholder(self) -> str:
        """Get placeholder for masked sensitive data."""
        if not self.config:
            return "[REDACTED]"

        return self.config.security.get('mask_placeholder', '[REDACTED]')

    def is_performance_logging_enabled(self) -> bool:
        """Check if performance logging is enabled."""
        if not self.config:
            return False

        return self.config.performance.get('function_timing', False)

    def get_slow_operation_threshold(self) -> int:
        """Get threshold for slow operation logging in milliseconds."""
        if not self.config:
            return 1000

        return self.config.performance.get('slow_operation_threshold_ms', 1000)

    def is_realtime_enabled(self) -> bool:
        """Check if real-time logging is enabled."""
        if not self.config:
            return False

        return self.config.realtime.get('websocket_enabled', False)

    def get_websocket_port(self) -> int:
        """Get WebSocket port for real-time logging."""
        if not self.config:
            return 8765

        return self.config.realtime.get('websocket_port', 8765)

    def export_config(self, output_path: str):
        """Export current configuration to a YAML file."""
        if not self.config:
            raise ValueError("No configuration loaded")

        # Convert dataclass to dictionary
        config_dict = self._dataclass_to_dict(self.config)

        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)

        self.logger.info(f"Configuration exported to {output_path}")

    def _dataclass_to_dict(self, config: LoggingConfig) -> Dict[str, Any]:
        """Convert LoggingConfig dataclass to dictionary."""
        result = {
            'LOG_LEVEL': config.log_level,
            'STRUCTURED_LOGGING': config.structured_logging,
            'COLORED_CONSOLE': config.colored_console,
            'MAX_LOG_FILE_SIZE_MB': config.max_log_file_size_mb,
            'LOG_BACKUP_COUNT': config.log_backup_count,
            'component_levels': config.component_levels,
            'formats': config.formats,
            'performance': config.performance,
            'realtime': config.realtime,
            'alerting': config.alerting,
            'retention': config.retention,
            'security': config.security,
            'development': config.development,
            'integrations': config.integrations
        }

        # Convert handlers
        handlers = {}
        for name, handler in config.handlers.items():
            handlers[name] = handler.config
        result['handlers'] = handlers

        return result


# Global configuration loader instance
_config_loader = None


def get_config_loader(config_path: Optional[str] = None) -> LoggingConfigLoader:
    """Get global configuration loader instance."""
    global _config_loader
    if _config_loader is None:
        _config_loader = LoggingConfigLoader(config_path)
        _config_loader.load_config()
    return _config_loader


def reload_config(config_path: Optional[str] = None):
    """Reload logging configuration."""
    global _config_loader
    _config_loader = LoggingConfigLoader(config_path)
    _config_loader.load_config()


if __name__ == "__main__":
    # Test configuration loading
    loader = LoggingConfigLoader()
    config = loader.load_config()

    print(f"Log level: {config.log_level}")
    print(f"Structured logging: {config.structured_logging}")
    print(f"Component levels: {config.component_levels}")
    print(f"Handlers: {list(config.handlers.keys())}")

    # Test component level lookup
    print(f"Orchestrator level: {loader.get_component_level('orchestrator')}")
    print(f"Unknown component level: {loader.get_component_level('unknown')}")

    # Test handler checks
    print(f"Console handler enabled: {loader.is_handler_enabled('console')}")
    print(f"File handler enabled: {loader.is_handler_enabled('file')}")

    # Export configuration
    loader.export_config("exported-logging-config.yaml")
