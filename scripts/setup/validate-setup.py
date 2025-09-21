#!/usr/bin/env python3
"""
Setup Validation Script for Agent Investment Platform

This script provides comprehensive validation of the complete setup including
dependencies, configuration, LLM availability, and system readiness.
"""

import os
import sys
import json
import yaml
import subprocess
import requests
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging
from dataclasses import dataclass
import time
import platform
from enum import Enum

# Setup logging
logger = logging.getLogger(__name__)

class ValidationResult(Enum):
    """Validation result status"""
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    SKIP = "SKIP"

@dataclass
class ValidationCheck:
    """Individual validation check"""
    name: str
    description: str
    result: ValidationResult
    message: str
    remediation: Optional[str] = None

class SetupValidator:
    """Comprehensive setup validation system"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.config_dir = project_root / "config"
        self.scripts_dir = project_root / "scripts"
        self.docs_dir = project_root / "docs"
        self.memory_dir = project_root / ".memory"
        self.vscode_dir = project_root / ".vscode"

        self.validation_results: List[ValidationCheck] = []
        self.overall_status = ValidationResult.PASS

    def validate_all(self) -> bool:
        """Run complete validation suite"""
        logger.info("Starting comprehensive setup validation...")

        try:
            # Core validation categories
            self._validate_directory_structure()
            self._validate_dependencies()
            self._validate_configuration_files()
            self._validate_llm_setup()
            self._validate_mcp_readiness()
            self._validate_docker_environment()
            self._validate_documentation()
            self._validate_vscode_integration()
            self._validate_memory_bank()

            # Generate validation report
            self._generate_validation_report()

            # Determine overall status
            has_failures = any(check.result == ValidationResult.FAIL for check in self.validation_results)

            if has_failures:
                self.overall_status = ValidationResult.FAIL
                logger.error("Setup validation failed - see validation report")
                return False
            else:
                self.overall_status = ValidationResult.PASS
                logger.info("Setup validation passed successfully")
                return True

        except Exception as e:
            logger.error(f"Validation process failed: {e}")
            self._add_check("validation_process", "Validation Process",
                          ValidationResult.FAIL, f"Validation failed: {e}")
            return False

    def _validate_directory_structure(self):
        """Validate project directory structure"""
        logger.info("Validating directory structure...")

        required_dirs = [
            ("config", "Configuration files directory"),
            ("scripts", "Setup and utility scripts"),
            ("scripts/setup", "Setup automation scripts"),
            ("docs", "Documentation directory"),
            ("docs/setup", "Setup documentation"),
            ("logs", "Logging directory"),
            ("reports", "Generated reports directory"),
            ("src", "Source code directory"),
            ("src/agents", "MCP agent implementations"),
            ("src/analysis", "Analysis engine components"),
            ("src/reports", "Report generation components"),
            (".vscode", "VS Code workspace configuration"),
            (".memory", "AI memory bank system")
        ]

        for dir_path, description in required_dirs:
            full_path = self.project_root / dir_path
            if full_path.exists():
                self._add_check(f"dir_{dir_path.replace('/', '_')}",
                              f"Directory: {dir_path}",
                              ValidationResult.PASS,
                              f"{description} exists")
            else:
                self._add_check(f"dir_{dir_path.replace('/', '_')}",
                              f"Directory: {dir_path}",
                              ValidationResult.FAIL,
                              f"Missing required directory: {dir_path}",
                              f"Create directory: mkdir -p {dir_path}")

    def _validate_dependencies(self):
        """Validate system dependencies"""
        logger.info("Validating system dependencies...")

        # Python version
        python_version = sys.version_info
        if python_version >= (3, 11):
            self._add_check("python_version", "Python Version",
                          ValidationResult.PASS,
                          f"Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        else:
            self._add_check("python_version", "Python Version",
                          ValidationResult.FAIL,
                          f"Python {python_version.major}.{python_version.minor} < 3.11",
                          "Install Python 3.11 or higher")

        # Required system commands
        required_commands = {
            "git": "Git version control",
            "docker": "Docker containerization",
            "python3": "Python 3 interpreter"
        }

        for cmd, description in required_commands.items():
            if self._check_command_exists(cmd):
                try:
                    result = subprocess.run([cmd, "--version"],
                                          capture_output=True, text=True, timeout=10)
                    version = result.stdout.split('\n')[0] if result.stdout else "Unknown"
                    self._add_check(f"cmd_{cmd}", f"Command: {cmd}",
                                  ValidationResult.PASS,
                                  f"{description} - {version}")
                except Exception:
                    self._add_check(f"cmd_{cmd}", f"Command: {cmd}",
                                  ValidationResult.WARNING,
                                  f"{description} exists but version check failed")
            else:
                remediation = {
                    "git": "Install Git: https://git-scm.com/downloads",
                    "docker": "Install Docker: https://docs.docker.com/get-docker/",
                    "python3": "Install Python 3.11+: https://python.org/downloads"
                }.get(cmd, f"Install {cmd}")

                self._add_check(f"cmd_{cmd}", f"Command: {cmd}",
                              ValidationResult.FAIL,
                              f"Missing required command: {cmd}",
                              remediation)

        # Python packages
        required_packages = [
            "requests", "yaml", "click", "pathlib", "json", "subprocess"
        ]

        for package in required_packages:
            try:
                __import__(package)
                self._add_check(f"pkg_{package}", f"Python Package: {package}",
                              ValidationResult.PASS, f"Package {package} available")
            except ImportError:
                self._add_check(f"pkg_{package}", f"Python Package: {package}",
                              ValidationResult.WARNING,
                              f"Package {package} not available",
                              f"Install with: pip install {package}")

    def _validate_configuration_files(self):
        """Validate configuration files"""
        logger.info("Validating configuration files...")

        required_configs = {
            ".env.example": "Environment variables template",
            "config/llm-config.yaml": "LLM configuration",
            "config/mcp-servers.json": "MCP server definitions",
            "config/data-sources.yaml": "Data source configuration",
            "config/strategies.yaml": "Investment strategies",
            "config/notification-config.yaml": "Notification settings"
        }

        for config_file, description in required_configs.items():
            file_path = self.project_root / config_file
            if file_path.exists():
                # Validate file content
                try:
                    if config_file.endswith('.json'):
                        with open(file_path) as f:
                            json.load(f)
                    elif config_file.endswith('.yaml') or config_file.endswith('.yml'):
                        with open(file_path) as f:
                            yaml.safe_load(f)

                    self._add_check(f"config_{config_file.replace('/', '_').replace('.', '_')}",
                                  f"Config: {config_file}",
                                  ValidationResult.PASS,
                                  f"{description} - valid format")

                except Exception as e:
                    self._add_check(f"config_{config_file.replace('/', '_').replace('.', '_')}",
                                  f"Config: {config_file}",
                                  ValidationResult.FAIL,
                                  f"{description} - invalid format: {e}",
                                  f"Fix configuration file syntax in {config_file}")
            else:
                self._add_check(f"config_{config_file.replace('/', '_').replace('.', '_')}",
                              f"Config: {config_file}",
                              ValidationResult.FAIL,
                              f"Missing configuration: {config_file}",
                              f"Run environment configuration: python scripts/setup/configure-environment.py")

        # Check .env file
        env_file = self.project_root / ".env"
        if env_file.exists():
            self._add_check("env_file", ".env File",
                          ValidationResult.PASS, "Environment file exists")

            # Check for critical environment variables
            with open(env_file) as f:
                env_content = f.read()

            critical_vars = ["LLM_PROVIDER", "SECRET_KEY"]
            for var in critical_vars:
                if f"{var}=" in env_content and not f"{var}=" in env_content.split(f"{var}=")[1].split('\n')[0]:
                    self._add_check(f"env_{var.lower()}", f"Environment Variable: {var}",
                                  ValidationResult.WARNING,
                                  f"{var} is set but may be empty",
                                  f"Configure {var} in .env file")
                elif f"{var}=" in env_content:
                    self._add_check(f"env_{var.lower()}", f"Environment Variable: {var}",
                                  ValidationResult.PASS, f"{var} is configured")
                else:
                    self._add_check(f"env_{var.lower()}", f"Environment Variable: {var}",
                                  ValidationResult.WARNING,
                                  f"{var} not found in .env",
                                  f"Add {var} to .env file")
        else:
            self._add_check("env_file", ".env File",
                          ValidationResult.WARNING,
                          "No .env file found - using defaults",
                          "Copy .env.example to .env and configure")

    def _validate_llm_setup(self):
        """Validate LLM setup and availability"""
        logger.info("Validating LLM setup...")

        # Check Ollama availability
        if self._check_command_exists("ollama"):
            try:
                result = subprocess.run(["ollama", "list"],
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    models = []
                    for line in result.stdout.split('\n')[1:]:  # Skip header
                        if line.strip():
                            model_name = line.split()[0]
                            models.append(model_name)

                    if models:
                        self._add_check("ollama_models", "Ollama Models",
                                      ValidationResult.PASS,
                                      f"Available models: {', '.join(models[:3])}")
                    else:
                        self._add_check("ollama_models", "Ollama Models",
                                      ValidationResult.WARNING,
                                      "Ollama running but no models available",
                                      "Download models: python scripts/setup/download-models.py")
                else:
                    self._add_check("ollama_service", "Ollama Service",
                                  ValidationResult.WARNING,
                                  "Ollama installed but not responding",
                                  "Start Ollama service: ollama serve")

            except subprocess.TimeoutExpired:
                self._add_check("ollama_service", "Ollama Service",
                              ValidationResult.WARNING,
                              "Ollama command timeout",
                              "Check Ollama service status")
            except Exception as e:
                self._add_check("ollama_service", "Ollama Service",
                              ValidationResult.WARNING,
                              f"Ollama check failed: {e}")
        else:
            self._add_check("ollama_install", "Ollama Installation",
                          ValidationResult.WARNING,
                          "Ollama not installed",
                          "Install Ollama: https://ollama.com/download")

        # Check local model configuration
        model_config_file = self.config_dir / "local-models.json"
        if model_config_file.exists():
            try:
                with open(model_config_file) as f:
                    config = json.load(f)

                local_models = config.get("local_models", {})
                model_assignments = config.get("model_assignments", {})

                if local_models:
                    self._add_check("local_model_config", "Local Model Configuration",
                                  ValidationResult.PASS,
                                  f"Configured with {len(local_models)} models")
                else:
                    self._add_check("local_model_config", "Local Model Configuration",
                                  ValidationResult.WARNING,
                                  "Model configuration exists but no models configured")

            except Exception as e:
                self._add_check("local_model_config", "Local Model Configuration",
                              ValidationResult.FAIL,
                              f"Invalid model configuration: {e}",
                              "Regenerate config: python scripts/setup/download-models.py")
        else:
            self._add_check("local_model_config", "Local Model Configuration",
                          ValidationResult.WARNING,
                          "No local model configuration found",
                          "Configure models: python scripts/setup/download-models.py")

    def _validate_mcp_readiness(self):
        """Validate MCP server readiness"""
        logger.info("Validating MCP server readiness...")

        # Check MCP server configuration
        mcp_config_file = self.config_dir / "mcp-servers.json"
        if mcp_config_file.exists():
            try:
                with open(mcp_config_file) as f:
                    mcp_config = json.load(f)

                servers = mcp_config.get("mcpServers", {})
                enabled_servers = [name for name, config in servers.items()
                                 if config.get("enabled", True)]

                if enabled_servers:
                    self._add_check("mcp_config", "MCP Server Configuration",
                                  ValidationResult.PASS,
                                  f"Configured servers: {', '.join(enabled_servers[:3])}")
                else:
                    self._add_check("mcp_config", "MCP Server Configuration",
                                  ValidationResult.WARNING,
                                  "MCP configuration exists but no servers enabled")

            except Exception as e:
                self._add_check("mcp_config", "MCP Server Configuration",
                              ValidationResult.FAIL,
                              f"Invalid MCP configuration: {e}",
                              "Fix MCP configuration in config/mcp-servers.json")
        else:
            self._add_check("mcp_config", "MCP Server Configuration",
                          ValidationResult.FAIL,
                          "Missing MCP server configuration",
                          "Run: python scripts/setup/configure-environment.py")

        # Check for MCP agent implementations
        agent_files = [
            "src/agents/stock_data_agent.py",
            "src/agents/news_agent.py",
            "src/agents/youtube_agent.py"
        ]

        existing_agents = []
        for agent_file in agent_files:
            if (self.project_root / agent_file).exists():
                existing_agents.append(agent_file.split('/')[-1])

        if existing_agents:
            self._add_check("mcp_agents", "MCP Agent Implementations",
                          ValidationResult.PASS,
                          f"Found agents: {', '.join(existing_agents)}")
        else:
            self._add_check("mcp_agents", "MCP Agent Implementations",
                          ValidationResult.WARNING,
                          "No MCP agent implementations found",
                          "MCP agents will be created in Task 2.0")

    def _validate_docker_environment(self):
        """Validate Docker environment"""
        logger.info("Validating Docker environment...")

        if self._check_command_exists("docker"):
            try:
                # Check Docker daemon
                result = subprocess.run(["docker", "info"],
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    self._add_check("docker_daemon", "Docker Daemon",
                                  ValidationResult.PASS, "Docker daemon running")

                    # Check Docker Compose
                    if self._check_command_exists("docker-compose") or "compose" in result.stdout:
                        self._add_check("docker_compose", "Docker Compose",
                                      ValidationResult.PASS, "Docker Compose available")
                    else:
                        self._add_check("docker_compose", "Docker Compose",
                                      ValidationResult.WARNING,
                                      "Docker Compose not available",
                                      "Install Docker Compose or use 'docker compose'")
                else:
                    self._add_check("docker_daemon", "Docker Daemon",
                                  ValidationResult.FAIL,
                                  "Docker installed but daemon not running",
                                  "Start Docker service/daemon")

            except subprocess.TimeoutExpired:
                self._add_check("docker_daemon", "Docker Daemon",
                              ValidationResult.FAIL,
                              "Docker command timeout",
                              "Check Docker daemon status")
            except Exception as e:
                self._add_check("docker_daemon", "Docker Daemon",
                              ValidationResult.WARNING,
                              f"Docker check failed: {e}")
        else:
            self._add_check("docker_install", "Docker Installation",
                          ValidationResult.WARNING,
                          "Docker not installed",
                          "Install Docker: https://docs.docker.com/get-docker/")

        # Check for Docker configuration files
        docker_files = ["docker-compose.yml", "Dockerfile"]
        for docker_file in docker_files:
            if (self.project_root / docker_file).exists():
                self._add_check(f"docker_{docker_file.replace('.', '_').replace('-', '_')}",
                              f"Docker File: {docker_file}",
                              ValidationResult.PASS, f"{docker_file} exists")
            else:
                self._add_check(f"docker_{docker_file.replace('.', '_').replace('-', '_')}",
                              f"Docker File: {docker_file}",
                              ValidationResult.WARNING,
                              f"Missing {docker_file}",
                              f"{docker_file} will be created in Task 1.0")

    def _validate_documentation(self):
        """Validate documentation structure"""
        logger.info("Validating documentation structure...")

        # Check main documentation files
        doc_files = {
            "README.md": "Main project README",
            "docs/README.md": "Documentation index",
            "docs/setup/initialize.prompt.md": "VS Code initialization prompt",
            ".vscode/guidelines.prompt.md": "Development guidelines"
        }

        for doc_file, description in doc_files.items():
            file_path = self.project_root / doc_file
            if file_path.exists():
                # Check file is not empty
                if file_path.stat().st_size > 0:
                    self._add_check(f"doc_{doc_file.replace('/', '_').replace('.', '_')}",
                                  f"Documentation: {doc_file}",
                                  ValidationResult.PASS, f"{description} exists")
                else:
                    self._add_check(f"doc_{doc_file.replace('/', '_').replace('.', '_')}",
                                  f"Documentation: {doc_file}",
                                  ValidationResult.WARNING,
                                  f"{description} exists but is empty")
            else:
                self._add_check(f"doc_{doc_file.replace('/', '_').replace('.', '_')}",
                              f"Documentation: {doc_file}",
                              ValidationResult.FAIL,
                              f"Missing {description}",
                              f"Create {doc_file}")

        # Check documentation structure consistency
        docs_structure = [
            "docs/setup", "docs/api", "docs/development",
            "docs/deployment", "docs/troubleshooting"
        ]

        existing_sections = []
        for section in docs_structure:
            if (self.project_root / section).exists():
                existing_sections.append(section.split('/')[-1])

        if len(existing_sections) >= 3:
            self._add_check("docs_structure", "Documentation Structure",
                          ValidationResult.PASS,
                          f"Documentation sections: {', '.join(existing_sections)}")
        else:
            self._add_check("docs_structure", "Documentation Structure",
                          ValidationResult.WARNING,
                          f"Limited documentation sections: {', '.join(existing_sections)}",
                          "Complete documentation structure in Task 6.0")

    def _validate_vscode_integration(self):
        """Validate VS Code integration"""
        logger.info("Validating VS Code integration...")

        # Check VS Code configuration
        vscode_files = {
            ".vscode/guidelines.prompt.md": "Development guidelines prompt",
        }

        planned_vscode_files = {
            ".vscode/tasks.json": "VS Code tasks configuration",
            ".vscode/settings.json": "VS Code workspace settings"
        }

        for vscode_file, description in vscode_files.items():
            file_path = self.project_root / vscode_file
            if file_path.exists():
                self._add_check(f"vscode_{vscode_file.replace('/', '_').replace('.', '_')}",
                              f"VS Code: {vscode_file}",
                              ValidationResult.PASS, f"{description} configured")
            else:
                self._add_check(f"vscode_{vscode_file.replace('/', '_').replace('.', '_')}",
                              f"VS Code: {vscode_file}",
                              ValidationResult.FAIL,
                              f"Missing {description}",
                              f"Create {vscode_file}")

        for vscode_file, description in planned_vscode_files.items():
            file_path = self.project_root / vscode_file
            if file_path.exists():
                self._add_check(f"vscode_{vscode_file.replace('/', '_').replace('.', '_')}",
                              f"VS Code: {vscode_file}",
                              ValidationResult.PASS, f"{description} configured")
            else:
                self._add_check(f"vscode_{vscode_file.replace('/', '_').replace('.', '_')}",
                              f"VS Code: {vscode_file}",
                              ValidationResult.WARNING,
                              f"Missing {description}",
                              f"{vscode_file} will be created in Tasks 0.7-0.8")

    def _validate_memory_bank(self):
        """Validate AI memory bank system"""
        logger.info("Validating memory bank system...")

        memory_files = {
            ".memory/project-context.md": "Project context and history",
            ".memory/user-preferences.json": "User preferences and patterns",
            ".memory/architecture-decisions.md": "Architecture decisions log",
            ".memory/patterns-knowledge.json": "Implementation patterns",
            ".memory/knowledge-graph.json": "Knowledge relationships",
            ".memory/memory_bank.py": "Memory bank API"
        }

        memory_score = 0
        for memory_file, description in memory_files.items():
            file_path = self.project_root / memory_file
            if file_path.exists():
                memory_score += 1
                self._add_check(f"memory_{memory_file.replace('/', '_').replace('.', '_')}",
                              f"Memory: {memory_file}",
                              ValidationResult.PASS, f"{description} exists")
            else:
                self._add_check(f"memory_{memory_file.replace('/', '_').replace('.', '_')}",
                              f"Memory: {memory_file}",
                              ValidationResult.WARNING,
                              f"Missing {description}")

        if memory_score >= 4:
            self._add_check("memory_system", "Memory Bank System",
                          ValidationResult.PASS,
                          f"Memory bank functional ({memory_score}/{len(memory_files)} files)")
        else:
            self._add_check("memory_system", "Memory Bank System",
                          ValidationResult.WARNING,
                          f"Memory bank incomplete ({memory_score}/{len(memory_files)} files)")

    def _generate_validation_report(self):
        """Generate comprehensive validation report"""
        logger.info("Generating validation report...")

        # Count results by status
        status_counts = {
            ValidationResult.PASS: 0,
            ValidationResult.FAIL: 0,
            ValidationResult.WARNING: 0,
            ValidationResult.SKIP: 0
        }

        for check in self.validation_results:
            status_counts[check.result] += 1

        # Create report
        report_lines = []
        report_lines.append("# Agent Investment Platform - Setup Validation Report")
        report_lines.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")

        # Summary
        total_checks = len(self.validation_results)
        report_lines.append("## Summary")
        report_lines.append(f"- **Total Checks**: {total_checks}")
        report_lines.append(f"- **Passed**: {status_counts[ValidationResult.PASS]} [PASS]")
        report_lines.append(f"- **Failed**: {status_counts[ValidationResult.FAIL]} [FAIL]")
        report_lines.append(f"- **Warnings**: {status_counts[ValidationResult.WARNING]} [WARN]")
        report_lines.append(f"- **Skipped**: {status_counts[ValidationResult.SKIP]} [SKIP]")
        report_lines.append("")

        # Overall status
        if status_counts[ValidationResult.FAIL] > 0:
            report_lines.append("## Overall Status: [FAIL] VALIDATION FAILED")
        elif status_counts[ValidationResult.WARNING] > 0:
            report_lines.append("## Overall Status: [WARN] VALIDATION PASSED WITH WARNINGS")
        else:
            report_lines.append("## Overall Status: [PASS] VALIDATION PASSED")
        report_lines.append("")

        # Detailed results
        report_lines.append("## Detailed Results")
        report_lines.append("")

        # Group by status
        for status in [ValidationResult.FAIL, ValidationResult.WARNING, ValidationResult.PASS, ValidationResult.SKIP]:
            status_checks = [check for check in self.validation_results if check.result == status]
            if not status_checks:
                continue

            status_icon = {
                ValidationResult.PASS: "[PASS]",
                ValidationResult.FAIL: "[FAIL]",
                ValidationResult.WARNING: "[WARN]",
                ValidationResult.SKIP: "[SKIP]"
            }[status]

            report_lines.append(f"### {status_icon} {status.value} ({len(status_checks)})")
            report_lines.append("")

            for check in status_checks:
                report_lines.append(f"**{check.name}**: {check.description}")
                report_lines.append(f"- Status: {check.message}")
                if check.remediation:
                    report_lines.append(f"- Remediation: {check.remediation}")
                report_lines.append("")

        # Next steps
        if status_counts[ValidationResult.FAIL] > 0:
            report_lines.append("## Next Steps")
            report_lines.append("1. Address all FAILED validations before proceeding")
            report_lines.append("2. Review and resolve WARNING items as needed")
            report_lines.append("3. Re-run validation: `python scripts/setup/validate-setup.py`")
            report_lines.append("")

        # Save report
        report_file = self.project_root / "logs" / "validation-report.md"
        report_file.parent.mkdir(exist_ok=True)

        with open(report_file, 'w') as f:
            f.write('\n'.join(report_lines))

        logger.info(f"Validation report saved: {report_file}")

        # Also print summary to console
        print("\n" + "="*60)
        print("SETUP VALIDATION SUMMARY")
        print("="*60)
        print(f"[PASS] Passed: {status_counts[ValidationResult.PASS]}")
        print(f"[FAIL] Failed: {status_counts[ValidationResult.FAIL]}")
        print(f"[WARN] Warnings: {status_counts[ValidationResult.WARNING]}")
        print(f"Full report: {report_file}")
        print("="*60)

    def _add_check(self, check_id: str, name: str, result: ValidationResult,
                   message: str, remediation: str = None):
        """Add a validation check result"""
        check = ValidationCheck(name, check_id, result, message, remediation)
        self.validation_results.append(check)

        # Log the result
        level = {
            ValidationResult.PASS: logging.INFO,
            ValidationResult.FAIL: logging.ERROR,
            ValidationResult.WARNING: logging.WARNING,
            ValidationResult.SKIP: logging.INFO
        }[result]

        logger.log(level, f"{result.value}: {name} - {message}")

    def _check_command_exists(self, command: str) -> bool:
        """Check if a command exists in the system PATH"""
        return shutil.which(command) is not None

    def quick_validation(self) -> Dict[str, Any]:
        """Quick validation for basic readiness"""
        logger.info("Running quick validation...")

        quick_checks = {
            "python_version": sys.version_info >= (3, 11),
            "git_available": self._check_command_exists("git"),
            "docker_available": self._check_command_exists("docker"),
            "config_dir": self.config_dir.exists(),
            "env_example": (self.project_root / ".env.example").exists(),
            "guidelines": (self.vscode_dir / "guidelines.prompt.md").exists(),
            "memory_bank": self.memory_dir.exists()
        }

        passed = sum(quick_checks.values())
        total = len(quick_checks)

        return {
            "ready": passed >= (total * 0.8),  # 80% pass rate
            "score": f"{passed}/{total}",
            "percentage": (passed / total) * 100,
            "details": quick_checks
        }

def main():
    """Main entry point for standalone execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Agent Investment Platform Setup Validator")
    parser.add_argument("--quick", action="store_true", help="Quick validation only")
    parser.add_argument("--report", action="store_true", help="Generate detailed report")

    args = parser.parse_args()

    # Setup paths
    project_root = Path(__file__).parent.parent.parent
    validator = SetupValidator(project_root)

    try:
        if args.quick:
            result = validator.quick_validation()
            print(f"Quick Validation: {result['score']} ({result['percentage']:.1f}%)")
            print(f"Ready: {'[PASS]' if result['ready'] else '[FAIL]'}")

            if not result['ready']:
                print("\nFailed Checks:")
                for check, passed in result['details'].items():
                    if not passed:
                        print(f"  [FAIL] {check}")
        else:
            success = validator.validate_all()
            sys.exit(0 if success else 1)

    except Exception as e:
        logger.error(f"Validation failed: {e}")
        print(f"[ERROR] Validation error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
