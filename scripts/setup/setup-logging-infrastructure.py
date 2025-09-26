#!/usr/bin/env python3
"""
Logging and Monitoring Infrastructure Setup

This script sets up the complete logging and monitoring infrastructure for the
Agent Investment Platform, including ELK stack, Docker services, and configuration.
"""

import os
import sys
import platform
import subprocess
import json
import yaml
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class LoggingConfig:
    """Configuration for logging infrastructure"""
    enable_elk_stack: bool = True
    enable_grafana: bool = True
    enable_websocket_streaming: bool = True
    enable_health_monitoring: bool = True
    elasticsearch_version: str = "8.11.0"
    logstash_version: str = "8.11.0"
    kibana_version: str = "8.11.0"
    grafana_version: str = "latest"

class LoggingInfrastructureSetup:
    """Handles setup of logging and monitoring infrastructure"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.config_dir = project_root / "config"
        self.logs_dir = project_root / "logs"
        self.docker_compose_file = project_root / "docker-compose.yml"

        # Ensure directories exist
        self.logs_dir.mkdir(exist_ok=True)
        self.config_dir.mkdir(exist_ok=True)

    def setup_all(self, config: Optional[LoggingConfig] = None) -> bool:
        """Setup complete logging infrastructure"""
        if config is None:
            config = LoggingConfig()

        logger.info("Setting up logging and monitoring infrastructure...")

        try:
            # 1. Setup logging configuration
            self._setup_logging_config()

            # 2. Setup Docker Compose services
            if config.enable_elk_stack or config.enable_grafana:
                self._setup_docker_services(config)

            # 3. Setup Elasticsearch configuration
            if config.enable_elk_stack:
                self._setup_elasticsearch_config()
                self._setup_logstash_config()

            # 4. Setup Grafana configuration
            if config.enable_grafana:
                self._setup_grafana_config()

            # 5. Setup health monitoring
            if config.enable_health_monitoring:
                self._setup_health_monitoring()

            # 6. Validate setup
            return self._validate_logging_setup()

        except Exception as e:
            logger.error(f"Logging infrastructure setup failed: {e}")
            return False

    def _setup_logging_config(self):
        """Setup logging configuration files"""
        logger.info("Setting up logging configuration...")

        # Main logging configuration
        logging_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "structured": {
                    "class": "src.logging.core.StructuredFormatter",
                    "format": "%(message)s"
                },
                "console": {
                    "class": "src.logging.core.ConsoleFormatter",
                    "format": "%(asctime)s [%(levelname)-8s] [%(name)s] %(message)s"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "INFO",
                    "formatter": "console",
                    "stream": "ext://sys.stdout"
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "DEBUG",
                    "formatter": "structured",
                    "filename": "logs/platform.log",
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5
                },
                "elasticsearch": {
                    "class": "src.logging.aggregation.ElasticsearchLogHandler",
                    "level": "INFO",
                    "formatter": "structured"
                }
            },
            "loggers": {
                "": {  # Root logger
                    "level": "INFO",
                    "handlers": ["console", "file", "elasticsearch"],
                    "propagate": False
                },
                "src": {
                    "level": "DEBUG",
                    "handlers": ["console", "file", "elasticsearch"],
                    "propagate": False
                }
            }
        }

        config_file = self.config_dir / "logging-config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(logging_config, f, default_flow_style=False)

        logger.info(f"Logging configuration saved to {config_file}")

    def _setup_docker_services(self, config: LoggingConfig):
        """Setup Docker Compose services for logging infrastructure"""
        logger.info("Setting up Docker services for logging infrastructure...")

        # Check if docker-compose.yml already exists
        if self.docker_compose_file.exists():
            logger.info("Docker Compose file exists, updating with logging services...")
            with open(self.docker_compose_file, 'r') as f:
                docker_compose = yaml.safe_load(f) or {}
        else:
            logger.info("Creating new Docker Compose file...")
            docker_compose = {
                "version": "3.8",
                "services": {},
                "volumes": {},
                "networks": {
                    "investment-network": {
                        "driver": "bridge"
                    }
                }
            }

        # Add ELK Stack services
        if config.enable_elk_stack:
            # Elasticsearch
            docker_compose["services"]["elasticsearch"] = {
                "image": f"docker.elastic.co/elasticsearch/elasticsearch:{config.elasticsearch_version}",
                "container_name": "elasticsearch",
                "environment": [
                    "discovery.type=single-node",
                    "ES_JAVA_OPTS=-Xms512m -Xmx512m",
                    "xpack.security.enabled=false"
                ],
                "ports": ["9200:9200", "9300:9300"],
                "volumes": ["elasticsearch_data:/usr/share/elasticsearch/data"],
                "networks": ["investment-network"],
                "healthcheck": {
                    "test": ["CMD-SHELL", "curl -f http://localhost:9200/_cluster/health || exit 1"],
                    "interval": "30s",
                    "timeout": "10s",
                    "retries": 3
                }
            }

            # Logstash
            docker_compose["services"]["logstash"] = {
                "image": f"docker.elastic.co/logstash/logstash:{config.logstash_version}",
                "container_name": "logstash",
                "ports": ["5000:5000", "5044:5044"],
                "volumes": [
                    "./config/logstash:/usr/share/logstash/pipeline",
                    "./logs:/logs"
                ],
                "networks": ["investment-network"],
                "depends_on": {
                    "elasticsearch": {
                        "condition": "service_healthy"
                    }
                }
            }

            # Kibana
            docker_compose["services"]["kibana"] = {
                "image": f"docker.elastic.co/kibana/kibana:{config.kibana_version}",
                "container_name": "kibana",
                "ports": ["5601:5601"],
                "environment": [
                    "ELASTICSEARCH_HOSTS=http://elasticsearch:9200"
                ],
                "networks": ["investment-network"],
                "depends_on": {
                    "elasticsearch": {
                        "condition": "service_healthy"
                    }
                }
            }

            # Add volumes
            docker_compose["volumes"]["elasticsearch_data"] = {"driver": "local"}

        # Add Grafana service
        if config.enable_grafana:
            docker_compose["services"]["grafana"] = {
                "image": f"grafana/grafana:{config.grafana_version}",
                "container_name": "grafana",
                "ports": ["3001:3000"],  # Use 3001 to avoid conflict with MCP server
                "environment": [
                    "GF_SECURITY_ADMIN_PASSWORD=admin123",
                    "GF_USERS_ALLOW_SIGN_UP=false"
                ],
                "volumes": [
                    "grafana_data:/var/lib/grafana",
                    "./config/grafana:/etc/grafana/provisioning"
                ],
                "networks": ["investment-network"]
            }

            docker_compose["volumes"]["grafana_data"] = {"driver": "local"}

        # Save updated docker-compose.yml
        with open(self.docker_compose_file, 'w') as f:
            yaml.dump(docker_compose, f, default_flow_style=False)

        logger.info(f"Docker Compose configuration saved to {self.docker_compose_file}")

    def _setup_elasticsearch_config(self):
        """Setup Elasticsearch configuration"""
        logger.info("Setting up Elasticsearch configuration...")

        # Create index templates and mappings
        elasticsearch_config = {
            "index_patterns": ["platform-logs-*"],
            "template": {
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0,
                    "index.refresh_interval": "5s"
                },
                "mappings": {
                    "properties": {
                        "@timestamp": {"type": "date"},
                        "level": {"type": "keyword"},
                        "logger_name": {"type": "keyword"},
                        "message": {"type": "text"},
                        "module": {"type": "keyword"},
                        "function": {"type": "keyword"},
                        "component": {"type": "keyword"},
                        "trace_id": {"type": "keyword"},
                        "span_id": {"type": "keyword"},
                        "duration_ms": {"type": "float"},
                        "hostname": {"type": "keyword"},
                        "process_id": {"type": "integer"},
                        "thread_id": {"type": "integer"}
                    }
                }
            }
        }

        # Save configuration for later application
        config_file = self.config_dir / "elasticsearch-template.json"
        with open(config_file, 'w') as f:
            json.dump(elasticsearch_config, f, indent=2)

        logger.info(f"Elasticsearch template saved to {config_file}")

    def _setup_logstash_config(self):
        """Setup Logstash configuration"""
        logger.info("Setting up Logstash configuration...")

        logstash_config_dir = self.config_dir / "logstash"
        logstash_config_dir.mkdir(exist_ok=True)

        # Main logstash pipeline configuration
        logstash_conf = '''
input {
  tcp {
    port => 5000
    codec => json_lines
  }
  beats {
    port => 5044
  }
  file {
    path => "/logs/*.log"
    start_position => "beginning"
    codec => json
  }
}

filter {
  # Parse timestamp
  date {
    match => [ "timestamp", "ISO8601" ]
    target => "@timestamp"
  }

  # Add metadata
  mutate {
    add_field => { "[@metadata][index]" => "platform-logs-%{+YYYY.MM.dd}" }
  }

  # Parse component information
  if [component] {
    mutate {
      add_tag => [ "component_%{component}" ]
    }
  }

  # Performance monitoring
  if [duration_ms] {
    mutate {
      convert => { "duration_ms" => "float" }
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "%{[@metadata][index]}"
    template_name => "platform-logs"
    template_pattern => "platform-logs-*"
  }

  # Debug output
  stdout {
    codec => rubydebug
  }
}
'''

        pipeline_file = logstash_config_dir / "logstash.conf"
        with open(pipeline_file, 'w') as f:
            f.write(logstash_conf)

        logger.info(f"Logstash configuration saved to {pipeline_file}")

    def _setup_grafana_config(self):
        """Setup Grafana configuration"""
        logger.info("Setting up Grafana configuration...")

        grafana_config_dir = self.config_dir / "grafana"
        grafana_config_dir.mkdir(exist_ok=True)

        # Datasources configuration
        datasources_dir = grafana_config_dir / "datasources"
        datasources_dir.mkdir(exist_ok=True)

        datasources_config = {
            "apiVersion": 1,
            "datasources": [
                {
                    "name": "Elasticsearch",
                    "type": "elasticsearch",
                    "access": "proxy",
                    "url": "http://elasticsearch:9200",
                    "database": "platform-logs-*",
                    "isDefault": True,
                    "jsonData": {
                        "esVersion": "8.0.0",
                        "timeField": "@timestamp",
                        "logMessageField": "message",
                        "logLevelField": "level"
                    }
                }
            ]
        }

        datasources_file = datasources_dir / "elasticsearch.yml"
        with open(datasources_file, 'w') as f:
            yaml.dump(datasources_config, f, default_flow_style=False)

        # Dashboards configuration
        dashboards_dir = grafana_config_dir / "dashboards"
        dashboards_dir.mkdir(exist_ok=True)

        dashboards_config = {
            "apiVersion": 1,
            "providers": [
                {
                    "name": "default",
                    "orgId": 1,
                    "folder": "",
                    "type": "file",
                    "disableDeletion": False,
                    "updateIntervalSeconds": 10,
                    "allowUiUpdates": True,
                    "options": {
                        "path": "/etc/grafana/provisioning/dashboards"
                    }
                }
            ]
        }

        dashboard_provider_file = dashboards_dir / "dashboards.yml"
        with open(dashboard_provider_file, 'w') as f:
            yaml.dump(dashboards_config, f, default_flow_style=False)

        logger.info(f"Grafana configuration saved to {grafana_config_dir}")

    def _setup_health_monitoring(self):
        """Setup health monitoring configuration"""
        logger.info("Setting up health monitoring...")

        # Health monitoring configuration
        health_config = {
            "monitoring": {
                "enabled": True,
                "interval_seconds": 30,
                "components": [
                    "orchestrator",
                    "mcp_manager",
                    "analysis_engines",
                    "notification_system",
                    "logging_system"
                ],
                "metrics": {
                    "system": ["cpu", "memory", "disk"],
                    "application": ["response_time", "error_rate", "throughput"],
                    "custom": ["analysis_success_rate", "report_generation_time"]
                }
            },
            "alerts": {
                "enabled": True,
                "thresholds": {
                    "cpu_usage": 80,
                    "memory_usage": 85,
                    "disk_usage": 90,
                    "error_rate": 5,
                    "response_time_ms": 5000
                }
            }
        }

        health_config_file = self.config_dir / "health-monitoring.yaml"
        with open(health_config_file, 'w') as f:
            yaml.dump(health_config, f, default_flow_style=False)

        logger.info(f"Health monitoring configuration saved to {health_config_file}")

    def _validate_logging_setup(self) -> bool:
        """Validate logging infrastructure setup"""
        logger.info("Validating logging infrastructure setup...")

        required_files = [
            self.config_dir / "logging-config.yaml",
            self.docker_compose_file
        ]

        missing_files = []
        for file_path in required_files:
            if not file_path.exists():
                missing_files.append(str(file_path))

        if missing_files:
            logger.error(f"Missing required files: {missing_files}")
            return False

        # Check if Docker is available
        if not shutil.which("docker"):
            logger.warning("Docker not found - logging infrastructure will be limited")
            return False

        logger.info("Logging infrastructure validation completed successfully")
        return True

    def start_logging_services(self) -> bool:
        """Start logging and monitoring services"""
        logger.info("Starting logging and monitoring services...")

        if not self.docker_compose_file.exists():
            logger.error("Docker Compose file not found")
            return False

        try:
            # Start services
            cmd = ["docker-compose", "up", "-d", "elasticsearch", "logstash", "kibana"]
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)

            if result.returncode == 0:
                logger.info("Logging services started successfully")
                return True
            else:
                logger.error(f"Failed to start logging services: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Error starting logging services: {e}")
            return False

def main():
    """Main entry point for standalone execution"""
    project_root = Path(__file__).parent.parent.parent

    setup = LoggingInfrastructureSetup(project_root)
    config = LoggingConfig()

    if setup.setup_all(config):
        print("✅ Logging infrastructure setup completed successfully")

        # Optionally start services
        if input("\nStart logging services now? [y/N]: ").lower().startswith('y'):
            if setup.start_logging_services():
                print("✅ Logging services started")
                print("🔍 Kibana: http://localhost:5601")
                print("📊 Grafana: http://localhost:3001 (admin/admin123)")
            else:
                print("❌ Failed to start logging services")
    else:
        print("❌ Logging infrastructure setup failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
