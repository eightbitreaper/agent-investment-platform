#!/usr/bin/env python3
"""
Health Check Script for the Agent Investment Platform.

This script provides comprehensive health monitoring for all system components
including MCP servers, databases, APIs, and dependencies.
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import subprocess
import requests
import sqlite3

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class SystemHealthChecker:
    """Comprehensive system health monitoring."""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.health_results = {}
        self.overall_status = "healthy"

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    async def run_health_check(self) -> Dict[str, Any]:
        """Run comprehensive health check."""
        self.logger.info("Starting system health check...")

        # Check all system components
        await self.check_python_environment()
        await self.check_dependencies()
        await self.check_configuration()
        await self.check_database()
        await self.check_api_keys()
        await self.check_external_apis()
        await self.check_file_system()
        await self.check_mcp_servers()

        # Generate health report
        return self.generate_health_report()

    async def check_python_environment(self):
        """Check Python environment and version."""
        try:
            python_version = sys.version_info

            self.health_results["python_environment"] = {
                "status": "healthy",
                "version": f"{python_version.major}.{python_version.minor}.{python_version.micro}",
                "executable": sys.executable,
                "platform": sys.platform,
                "check_time": datetime.now().isoformat()
            }

            # Check minimum Python version (3.9+)
            if python_version < (3, 9):
                self.health_results["python_environment"]["status"] = "warning"
                self.health_results["python_environment"]["warning"] = "Python 3.9+ recommended"

        except Exception as e:
            self.health_results["python_environment"] = {
                "status": "error",
                "error": str(e),
                "check_time": datetime.now().isoformat()
            }
            self.overall_status = "unhealthy"

    async def check_dependencies(self):
        """Check installed Python dependencies."""
        try:
            # Check critical dependencies
            critical_deps = [
                "requests", "yaml", "click", "rich",
                "aiohttp", "jinja2", "markdown"
            ]

            missing_deps = []
            installed_deps = {}

            for dep in critical_deps:
                try:
                    __import__(dep)
                    # Try to get version
                    try:
                        module = __import__(dep)
                        version = getattr(module, '__version__', 'unknown')
                        installed_deps[dep] = version
                    except:
                        installed_deps[dep] = 'installed'
                except ImportError:
                    missing_deps.append(dep)

            status = "healthy" if not missing_deps else "error"
            if status == "error":
                self.overall_status = "unhealthy"

            self.health_results["dependencies"] = {
                "status": status,
                "installed": installed_deps,
                "missing": missing_deps,
                "check_time": datetime.now().isoformat()
            }

        except Exception as e:
            self.health_results["dependencies"] = {
                "status": "error",
                "error": str(e),
                "check_time": datetime.now().isoformat()
            }
            self.overall_status = "unhealthy"

    async def check_configuration(self):
        """Check configuration files."""
        try:
            config_files = [
                "config/mcp-servers.json",
                "config/llm-config.yaml",
                "config/data-sources.yaml",
                "config/strategies.yaml",
                "config/notification-config.yaml"
            ]

            missing_configs = []
            valid_configs = []
            invalid_configs = []

            for config_file in config_files:
                config_path = Path(config_file)

                if not config_path.exists():
                    missing_configs.append(config_file)
                    continue

                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        if config_file.endswith('.json'):
                            json.load(f)
                        # Note: yaml check would require PyYAML import
                        valid_configs.append(config_file)
                except Exception as e:
                    invalid_configs.append({"file": config_file, "error": str(e)})

            status = "healthy"
            if missing_configs or invalid_configs:
                status = "warning" if not missing_configs else "error"

            if status == "error":
                self.overall_status = "unhealthy"

            self.health_results["configuration"] = {
                "status": status,
                "valid_configs": valid_configs,
                "missing_configs": missing_configs,
                "invalid_configs": invalid_configs,
                "check_time": datetime.now().isoformat()
            }

        except Exception as e:
            self.health_results["configuration"] = {
                "status": "error",
                "error": str(e),
                "check_time": datetime.now().isoformat()
            }
            self.overall_status = "unhealthy"

    async def check_database(self):
        """Check database connectivity and structure."""
        try:
            db_path = Path("data/analysis.db")

            if not db_path.exists():
                self.health_results["database"] = {
                    "status": "warning",
                    "message": "Database not initialized - will be created on first use",
                    "check_time": datetime.now().isoformat()
                }
                return

            # Test database connection
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()

                self.health_results["database"] = {
                    "status": "healthy",
                    "path": str(db_path),
                    "tables": [table[0] for table in tables],
                    "size_mb": round(db_path.stat().st_size / 1024 / 1024, 2),
                    "check_time": datetime.now().isoformat()
                }

        except Exception as e:
            self.health_results["database"] = {
                "status": "error",
                "error": str(e),
                "check_time": datetime.now().isoformat()
            }
            self.overall_status = "unhealthy"

    async def check_api_keys(self):
        """Check API key configuration."""
        try:
            api_keys = {
                "ALPHA_VANTAGE_API_KEY": os.environ.get("ALPHA_VANTAGE_API_KEY"),
                "POLYGON_API_KEY": os.environ.get("POLYGON_API_KEY"),
                "NEWS_API_KEY": os.environ.get("NEWS_API_KEY"),
                "YOUTUBE_API_KEY": os.environ.get("YOUTUBE_API_KEY"),
                "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY"),
                "ANTHROPIC_API_KEY": os.environ.get("ANTHROPIC_API_KEY"),
                "GITHUB_TOKEN": os.environ.get("GITHUB_TOKEN")
            }

            configured_keys = {k: bool(v) for k, v in api_keys.items()}
            configured_count = sum(configured_keys.values())

            status = "healthy" if configured_count > 0 else "warning"

            self.health_results["api_keys"] = {
                "status": status,
                "configured_keys": configured_keys,
                "total_configured": configured_count,
                "total_available": len(api_keys),
                "message": "At least one API key should be configured for full functionality",
                "check_time": datetime.now().isoformat()
            }

        except Exception as e:
            self.health_results["api_keys"] = {
                "status": "error",
                "error": str(e),
                "check_time": datetime.now().isoformat()
            }

    async def check_external_apis(self):
        """Check external API connectivity."""
        try:
            api_tests = []

            # Test Alpha Vantage if key is available
            alpha_key = os.environ.get("ALPHA_VANTAGE_API_KEY")
            if alpha_key:
                try:
                    response = requests.get(
                        "https://www.alphavantage.co/query",
                        params={
                            "function": "GLOBAL_QUOTE",
                            "symbol": "AAPL",
                            "apikey": alpha_key
                        },
                        timeout=10
                    )
                    if response.status_code == 200:
                        api_tests.append({"api": "Alpha Vantage", "status": "healthy"})
                    else:
                        api_tests.append({"api": "Alpha Vantage", "status": "error", "code": response.status_code})
                except Exception as e:
                    api_tests.append({"api": "Alpha Vantage", "status": "error", "error": str(e)})

            # Test NewsAPI if key is available
            news_key = os.environ.get("NEWS_API_KEY")
            if news_key:
                try:
                    response = requests.get(
                        "https://newsapi.org/v2/top-headlines",
                        params={
                            "country": "us",
                            "category": "business",
                            "pageSize": 1,
                            "apiKey": news_key
                        },
                        timeout=10
                    )
                    if response.status_code == 200:
                        api_tests.append({"api": "NewsAPI", "status": "healthy"})
                    else:
                        api_tests.append({"api": "NewsAPI", "status": "error", "code": response.status_code})
                except Exception as e:
                    api_tests.append({"api": "NewsAPI", "status": "error", "error": str(e)})

            # Test general internet connectivity
            try:
                response = requests.get("https://httpbin.org/status/200", timeout=5)
                if response.status_code == 200:
                    api_tests.append({"api": "Internet Connectivity", "status": "healthy"})
                else:
                    api_tests.append({"api": "Internet Connectivity", "status": "warning"})
            except Exception as e:
                api_tests.append({"api": "Internet Connectivity", "status": "error", "error": str(e)})

            healthy_apis = sum(1 for test in api_tests if test["status"] == "healthy")
            status = "healthy" if healthy_apis > 0 else "warning"

            self.health_results["external_apis"] = {
                "status": status,
                "tests": api_tests,
                "healthy_apis": healthy_apis,
                "total_tested": len(api_tests),
                "check_time": datetime.now().isoformat()
            }

        except Exception as e:
            self.health_results["external_apis"] = {
                "status": "error",
                "error": str(e),
                "check_time": datetime.now().isoformat()
            }

    async def check_file_system(self):
        """Check file system permissions and directories."""
        try:
            required_dirs = [
                "data", "reports", "logs", "config",
                "src", "scripts", ".vscode", "templates"
            ]

            missing_dirs = []
            accessible_dirs = []
            permission_errors = []

            for dir_name in required_dirs:
                dir_path = Path(dir_name)

                if not dir_path.exists():
                    missing_dirs.append(dir_name)
                    continue

                try:
                    # Test read/write permissions
                    if dir_path.is_dir():
                        test_file = dir_path / ".health_check_test"
                        test_file.write_text("test")
                        test_file.unlink()
                        accessible_dirs.append(dir_name)
                    else:
                        permission_errors.append({"dir": dir_name, "error": "Not a directory"})
                except Exception as e:
                    permission_errors.append({"dir": dir_name, "error": str(e)})

            # Check disk space
            try:
                disk_usage = os.statvfs('.') if hasattr(os, 'statvfs') else None
                if disk_usage:
                    free_space_gb = (disk_usage.f_bavail * disk_usage.f_frsize) / (1024**3)
                else:
                    free_space_gb = None
            except:
                free_space_gb = None

            status = "healthy"
            if missing_dirs:
                status = "warning"
            if permission_errors:
                status = "error"
                self.overall_status = "unhealthy"

            self.health_results["file_system"] = {
                "status": status,
                "accessible_dirs": accessible_dirs,
                "missing_dirs": missing_dirs,
                "permission_errors": permission_errors,
                "free_space_gb": free_space_gb,
                "check_time": datetime.now().isoformat()
            }

        except Exception as e:
            self.health_results["file_system"] = {
                "status": "error",
                "error": str(e),
                "check_time": datetime.now().isoformat()
            }
            self.overall_status = "unhealthy"

    async def check_mcp_servers(self):
        """Check MCP server availability."""
        try:
            # For now, just check if server files exist
            server_files = [
                "src/mcp_servers/stock_data_server.py",
                "src/mcp_servers/analysis_engine_server.py",
                "src/mcp_servers/report_generator_server.py",
                "src/mcp-servers/news-analysis-server.js",
                "src/mcp_servers/manager.py",
                "scripts/run_mcp_server.py"
            ]

            available_servers = []
            missing_servers = []

            for server_file in server_files:
                if Path(server_file).exists():
                    available_servers.append(server_file)
                else:
                    missing_servers.append(server_file)

            status = "healthy" if len(available_servers) > 0 else "error"
            if status == "error":
                self.overall_status = "unhealthy"

            self.health_results["mcp_servers"] = {
                "status": status,
                "available_servers": available_servers,
                "missing_servers": missing_servers,
                "total_available": len(available_servers),
                "total_expected": len(server_files),
                "check_time": datetime.now().isoformat()
            }

        except Exception as e:
            self.health_results["mcp_servers"] = {
                "status": "error",
                "error": str(e),
                "check_time": datetime.now().isoformat()
            }
            self.overall_status = "unhealthy"

    def generate_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report."""

        # Count component status
        healthy_count = sum(1 for result in self.health_results.values()
                          if result.get("status") == "healthy")
        warning_count = sum(1 for result in self.health_results.values()
                          if result.get("status") == "warning")
        error_count = sum(1 for result in self.health_results.values()
                        if result.get("status") == "error")

        total_components = len(self.health_results)

        # Generate summary
        summary = {
            "overall_status": self.overall_status,
            "check_timestamp": datetime.now().isoformat(),
            "total_components": total_components,
            "healthy_components": healthy_count,
            "warning_components": warning_count,
            "error_components": error_count,
            "health_score": round((healthy_count / total_components * 100), 1) if total_components > 0 else 0
        }

        # Recommendations
        recommendations = []

        if error_count > 0:
            recommendations.append("Address critical errors before running the platform")

        if warning_count > 0:
            recommendations.append("Review warnings for optimal performance")

        if not os.environ.get("ALPHA_VANTAGE_API_KEY"):
            recommendations.append("Configure API keys for full functionality")

        if not Path("data").exists():
            recommendations.append("Run initialization script to create required directories")

        return {
            "summary": summary,
            "components": self.health_results,
            "recommendations": recommendations,
            "report_generated": datetime.now().isoformat()
        }

    def print_health_report(self, report: Dict[str, Any]):
        """Print formatted health report."""
        summary = report["summary"]

        print(f"\n{'='*60}")
        print(f"SYSTEM HEALTH REPORT")
        print(f"{'='*60}")
        print(f"Overall Status: {summary['overall_status'].upper()}")
        print(f"Health Score: {summary['health_score']}%")
        print(f"Components: {summary['healthy_components']} healthy, {summary['warning_components']} warnings, {summary['error_components']} errors")
        print(f"Generated: {summary['check_timestamp']}")
        print(f"{'='*60}")

        # Component details
        for component, details in report["components"].items():
            status_icon = "✅" if details["status"] == "healthy" else "⚠️" if details["status"] == "warning" else "❌"
            print(f"{status_icon} {component.replace('_', ' ').title()}: {details['status'].upper()}")

            if "error" in details:
                print(f"   Error: {details['error']}")
            elif "warning" in details:
                print(f"   Warning: {details['warning']}")
            elif "message" in details:
                print(f"   Info: {details['message']}")

        print(f"\n{'='*60}")

        # Recommendations
        if report["recommendations"]:
            print("RECOMMENDATIONS:")
            for i, rec in enumerate(report["recommendations"], 1):
                print(f"{i}. {rec}")
            print(f"{'='*60}")


async def main():
    """Main entry point for health check."""
    checker = SystemHealthChecker()
    report = await checker.run_health_check()

    # Print report to console
    checker.print_health_report(report)

    # Save report to file
    report_path = Path("logs/health-check-report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"\nDetailed report saved to: {report_path}")

    # Exit with appropriate code
    if report["summary"]["overall_status"] == "unhealthy":
        sys.exit(1)
    elif report["summary"]["error_components"] > 0:
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
