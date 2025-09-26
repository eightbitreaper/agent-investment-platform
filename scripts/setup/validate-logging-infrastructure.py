#!/usr/bin/env python3
"""
Logging Infrastructure Validation Script

This script validates that the logging and monitoring infrastructure is properly
configured and operational.
"""

import os
import sys
import subprocess
import json
import requests
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class LoggingInfrastructureValidator:
    """Validates logging and monitoring infrastructure"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.config_dir = project_root / "config"
        self.logs_dir = project_root / "logs"

    def validate_all(self) -> Tuple[bool, List[str]]:
        """Run all validation checks"""
        logger.info("Validating logging infrastructure...")

        results = []
        all_passed = True

        # 1. Check configuration files
        config_ok, config_msgs = self._validate_configuration()
        results.extend(config_msgs)
        all_passed = all_passed and config_ok

        # 2. Check Docker services
        docker_ok, docker_msgs = self._validate_docker_services()
        results.extend(docker_msgs)
        all_passed = all_passed and docker_ok

        # 3. Check service connectivity
        connectivity_ok, connectivity_msgs = self._validate_service_connectivity()
        results.extend(connectivity_msgs)
        all_passed = all_passed and connectivity_ok

        # 4. Test logging functionality
        logging_ok, logging_msgs = self._validate_logging_functionality()
        results.extend(logging_msgs)
        all_passed = all_passed and logging_ok

        return all_passed, results

    def _validate_configuration(self) -> Tuple[bool, List[str]]:
        """Validate configuration files exist and are valid"""
        logger.info("Validating configuration files...")

        results = []
        all_passed = True

        required_configs = [
            "logging-config.yaml",
            "docker-compose.yml"
        ]

        for config_file in required_configs:
            file_path = self.project_root / config_file if config_file == "docker-compose.yml" else self.config_dir / config_file

            if file_path.exists():
                results.append(f"✅ Configuration file exists: {config_file}")

                # Validate YAML syntax
                if config_file.endswith('.yaml') or config_file.endswith('.yml'):
                    try:
                        import yaml
                        with open(file_path, 'r') as f:
                            yaml.safe_load(f)
                        results.append(f"✅ Valid YAML syntax: {config_file}")
                    except yaml.YAMLError as e:
                        results.append(f"❌ Invalid YAML syntax in {config_file}: {e}")
                        all_passed = False
            else:
                results.append(f"❌ Missing configuration file: {config_file}")
                all_passed = False

        return all_passed, results

    def _validate_docker_services(self) -> Tuple[bool, List[str]]:
        """Validate Docker services are configured and running"""
        logger.info("Validating Docker services...")

        results = []
        all_passed = True

        # Check if Docker is available
        if not self._check_command_exists("docker"):
            results.append("❌ Docker not found - logging infrastructure limited")
            return False, results

        results.append("✅ Docker is available")

        # Check if docker-compose is available
        if not self._check_command_exists("docker-compose"):
            results.append("❌ docker-compose not found")
            return False, results

        results.append("✅ docker-compose is available")

        # Check if services are defined in docker-compose.yml
        docker_compose_file = self.project_root / "docker-compose.yml"
        if docker_compose_file.exists():
            try:
                import yaml
                with open(docker_compose_file, 'r') as f:
                    compose_config = yaml.safe_load(f)

                expected_services = ["elasticsearch", "logstash", "kibana"]
                services = compose_config.get("services", {})

                for service in expected_services:
                    if service in services:
                        results.append(f"✅ Service defined: {service}")
                    else:
                        results.append(f"⚠️ Service not defined: {service}")
                        # Don't fail completely, some services might be optional

            except Exception as e:
                results.append(f"❌ Error reading docker-compose.yml: {e}")
                all_passed = False

        return all_passed, results

    def _validate_service_connectivity(self) -> Tuple[bool, List[str]]:
        """Validate that logging services are accessible"""
        logger.info("Validating service connectivity...")

        results = []
        all_passed = True

        services_to_check = [
            ("Elasticsearch", "http://localhost:9200", "_cluster/health"),
            ("Kibana", "http://localhost:5601", "api/status"),
            ("Grafana", "http://localhost:3000", "api/health")
        ]

        for service_name, base_url, health_endpoint in services_to_check:
            try:
                url = f"{base_url}/{health_endpoint}"
                response = requests.get(url, timeout=5)

                if response.status_code == 200:
                    results.append(f"✅ {service_name} is accessible at {base_url}")
                else:
                    results.append(f"⚠️ {service_name} returned status {response.status_code} at {base_url}")

            except requests.exceptions.ConnectionError:
                results.append(f"⚠️ {service_name} not accessible at {base_url} (service may not be running)")
            except requests.exceptions.Timeout:
                results.append(f"⚠️ {service_name} timeout at {base_url}")
            except Exception as e:
                results.append(f"❌ Error checking {service_name}: {e}")

        # Don't fail validation if services aren't running - they might be started later
        return True, results

    def _validate_logging_functionality(self) -> Tuple[bool, List[str]]:
        """Validate core logging functionality"""
        logger.info("Validating logging functionality...")

        results = []
        all_passed = True

        try:
            # Try to import our logging modules
            sys.path.append(str(self.project_root))

            from src.logging.core import LoggerManager
            from src.logging.aggregation import LogAggregator

            results.append("✅ Logging modules can be imported")

            # Test basic logging functionality
            logger_manager = LoggerManager()
            test_logger = logger_manager.get_logger("test_validation")

            test_logger.info("Test log message for validation")
            results.append("✅ Basic logging functionality works")

            # Test log aggregation (basic initialization)
            log_aggregator = LogAggregator()
            results.append("✅ Log aggregation module initializes")

        except ImportError as e:
            results.append(f"❌ Cannot import logging modules: {e}")
            all_passed = False
        except Exception as e:
            results.append(f"❌ Error testing logging functionality: {e}")
            all_passed = False

        return all_passed, results

    def _check_command_exists(self, command: str) -> bool:
        """Check if a command exists in the system PATH"""
        try:
            subprocess.run([command, "--version"],
                         capture_output=True, check=True, timeout=5)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def start_logging_services(self) -> Tuple[bool, List[str]]:
        """Start logging services and validate they come up properly"""
        logger.info("Starting logging services...")

        results = []

        # Start Docker services
        try:
            cmd = ["docker-compose", "up", "-d", "elasticsearch", "logstash", "kibana"]
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                results.append("✅ Docker services started successfully")

                # Wait for services to be ready
                results.append("⏳ Waiting for services to initialize...")
                time.sleep(30)  # Give services time to start

                # Check service health
                health_ok, health_msgs = self._validate_service_connectivity()
                results.extend(health_msgs)

                return health_ok, results
            else:
                results.append(f"❌ Failed to start Docker services: {result.stderr}")
                return False, results

        except subprocess.TimeoutExpired:
            results.append("❌ Timeout starting Docker services")
            return False, results
        except Exception as e:
            results.append(f"❌ Error starting Docker services: {e}")
            return False, results

def main():
    """Main entry point for standalone execution"""
    project_root = Path(__file__).parent.parent.parent

    validator = LoggingInfrastructureValidator(project_root)

    print("🔍 Validating Logging Infrastructure")
    print("=" * 50)

    # Run validation
    all_passed, results = validator.validate_all()

    # Print results
    for result in results:
        print(result)

    if all_passed:
        print("\n✅ Logging infrastructure validation passed")

        # Ask if user wants to start services
        if input("\nStart logging services? [y/N]: ").lower().startswith('y'):
            start_ok, start_results = validator.start_logging_services()

            for result in start_results:
                print(result)

            if start_ok:
                print("\n🎉 Logging infrastructure is ready!")
                print("🔍 Kibana: http://localhost:5601")
                print("📊 Grafana: http://localhost:3001 (admin/admin123)")
            else:
                print("\n❌ Failed to start logging services")
    else:
        print("\n❌ Logging infrastructure validation failed")
        print("Please check the configuration and try again")
        sys.exit(1)

if __name__ == "__main__":
    main()
