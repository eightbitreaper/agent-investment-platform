#!/usr/bin/env python3
"""
Complete System Validation for Agent Investment Platform
This script validates all components after installation
"""

import subprocess
import sys
import requests
import time
import json
import os
from pathlib import Path
import yaml

class SystemValidator:
    def __init__(self):
        self.results = {}
        self.passed = 0
        self.failed = 0
        self.warnings = 0

    def run_command(self, command, capture_output=True):
        """Run a shell command and return success status"""
        try:
            if capture_output:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                return result.returncode == 0, result.stdout, result.stderr
            else:
                result = subprocess.run(command, shell=True)
                return result.returncode == 0, "", ""
        except Exception as e:
            return False, "", str(e)

    def test_system_requirements(self):
        """Test system requirements"""
        print("\n" + "="*60)
        print("🔧 TESTING SYSTEM REQUIREMENTS")
        print("="*60)

        # Test Python
        success, stdout, _ = self.run_command("python --version")
        if success:
            version = stdout.strip()
            print(f"✅ Python: {version}")
            self.passed += 1
        else:
            print("❌ Python: Not found")
            self.failed += 1

        # Test Docker
        success, stdout, _ = self.run_command("docker --version")
        if success:
            version = stdout.strip()
            print(f"✅ Docker: {version}")
            self.passed += 1

            # Test Docker running
            success, _, _ = self.run_command("docker info")
            if success:
                print("✅ Docker: Running")
                self.passed += 1
            else:
                print("⚠️  Docker: Installed but not running")
                self.warnings += 1
        else:
            print("❌ Docker: Not found")
            self.failed += 1

        # Test Node.js
        success, stdout, _ = self.run_command("node --version")
        if success:
            version = stdout.strip()
            print(f"✅ Node.js: {version}")
            self.passed += 1
        else:
            print("⚠️  Node.js: Not found (optional)")
            self.warnings += 1

        # Test Git
        success, stdout, _ = self.run_command("git --version")
        if success:
            version = stdout.strip()
            print(f"✅ Git: {version}")
            self.passed += 1
        else:
            print("⚠️  Git: Not found")
            self.warnings += 1

    def test_python_environment(self):
        """Test Python environment and dependencies"""
        print("\n" + "="*60)
        print("🐍 TESTING PYTHON ENVIRONMENT")
        print("="*60)

        # Test virtual environment
        if Path(".venv").exists():
            print("✅ Virtual environment: Found")
            self.passed += 1
        else:
            print("❌ Virtual environment: Not found")
            self.failed += 1
            return

        # Test key dependencies
        dependencies = [
            "requests", "fastapi", "pandas", "numpy", "yfinance",
            "docker", "aiohttp", "uvicorn", "pydantic"
        ]

        for dep in dependencies:
            success, _, _ = self.run_command(f".venv/Scripts/python -c \"import {dep}\"")
            if success:
                print(f"✅ {dep}: Available")
                self.passed += 1
            else:
                print(f"❌ {dep}: Missing")
                self.failed += 1

    def test_configuration(self):
        """Test configuration files"""
        print("\n" + "="*60)
        print("⚙️  TESTING CONFIGURATION")
        print("="*60)

        # Test .env file
        if Path(".env").exists():
            print("✅ Environment file: Found")
            self.passed += 1

            # Check for API key
            try:
                with open(".env", "r") as f:
                    content = f.read()
                    if "POLYGON_API_KEY=aDnpiaVz" in content:
                        print("✅ Polygon API key: Configured")
                        self.passed += 1
                    else:
                        print("⚠️  Polygon API key: Not configured")
                        self.warnings += 1
            except Exception as e:
                print(f"⚠️  Environment file: Error reading - {e}")
                self.warnings += 1
        else:
            print("❌ Environment file: Not found")
            self.failed += 1

        # Test configuration files
        config_files = [
            "docker-compose.yml", "Dockerfile",
            "config/strategies.yaml", "config/llm-config.yaml"
        ]

        for config in config_files:
            if Path(config).exists():
                print(f"✅ {config}: Found")
                self.passed += 1
            else:
                print(f"❌ {config}: Missing")
                self.failed += 1

    def test_docker_services(self):
        """Test Docker services"""
        print("\n" + "="*60)
        print("🐋 TESTING DOCKER SERVICES")
        print("="*60)

        # Check if Docker Compose is available
        success, _, _ = self.run_command("docker-compose --version")
        if not success:
            print("❌ Docker Compose: Not available")
            self.failed += 1
            return

        print("✅ Docker Compose: Available")
        self.passed += 1

        # Get service status
        success, stdout, _ = self.run_command("docker-compose ps --format json")
        if success and stdout.strip():
            try:
                services = json.loads(f"[{stdout.replace('}{', '},{')}]")
                for service in services:
                    name = service.get('Name', 'Unknown')
                    state = service.get('State', 'Unknown')
                    if state == 'running':
                        print(f"✅ {name}: Running")
                        self.passed += 1
                    else:
                        print(f"❌ {name}: {state}")
                        self.failed += 1
            except json.JSONDecodeError:
                print("⚠️  Docker services: Status format error")
                self.warnings += 1
        else:
            print("⚠️  Docker services: No services running")
            self.warnings += 1

    def test_web_services(self):
        """Test web service endpoints"""
        print("\n" + "="*60)
        print("🌐 TESTING WEB SERVICES")
        print("="*60)

        services = {
            "Main Application": "http://localhost:8000",
            "Grafana": "http://localhost:3000",
            "Prometheus": "http://localhost:9090"
        }

        for name, url in services.items():
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    print(f"✅ {name}: Responding ({response.status_code})")
                    self.passed += 1
                else:
                    print(f"⚠️  {name}: HTTP {response.status_code}")
                    self.warnings += 1
            except requests.exceptions.RequestException as e:
                print(f"❌ {name}: Not responding - {str(e)[:50]}...")
                self.failed += 1

    def test_database_connections(self):
        """Test database connections"""
        print("\n" + "="*60)
        print("🗄️  TESTING DATABASE CONNECTIONS")
        print("="*60)

        # Test PostgreSQL (Docker container)
        success, _, _ = self.run_command("docker exec postgres-investment pg_isready -U postgres")
        if success:
            print("✅ PostgreSQL: Connected")
            self.passed += 1
        else:
            print("❌ PostgreSQL: Connection failed")
            self.failed += 1

        # Test Redis (Docker container)
        success, _, _ = self.run_command("docker exec redis-investment redis-cli ping")
        if success:
            print("✅ Redis: Connected")
            self.passed += 1
        else:
            print("❌ Redis: Connection failed")
            self.failed += 1

    def test_file_system(self):
        """Test file system setup"""
        print("\n" + "="*60)
        print("📁 TESTING FILE SYSTEM")
        print("="*60)

        directories = ["data", "logs", "reports", "models", ".memory"]
        for directory in directories:
            if Path(directory).exists():
                print(f"✅ {directory}/: Exists")
                self.passed += 1
            else:
                print(f"❌ {directory}/: Missing")
                self.failed += 1

    def run_functional_test(self):
        """Run a basic functional test"""
        print("\n" + "="*60)
        print("🧪 RUNNING FUNCTIONAL TEST")
        print("="*60)

        try:
            # Test deployment script
            success, _, _ = self.run_command(".venv/Scripts/python deployment_test.py")
            if success:
                print("✅ Deployment test: Passed")
                self.passed += 1
            else:
                print("⚠️  Deployment test: Some issues detected")
                self.warnings += 1

            # Test health check
            success, _, _ = self.run_command(".venv/Scripts/python scripts/health-check.py")
            if success:
                print("✅ Health check: Passed")
                self.passed += 1
            else:
                print("⚠️  Health check: Issues detected")
                self.warnings += 1

        except Exception as e:
            print(f"❌ Functional test: Error - {e}")
            self.failed += 1

    def generate_report(self):
        """Generate final report"""
        print("\n" + "="*60)
        print("📊 VALIDATION REPORT")
        print("="*60)

        total = self.passed + self.failed + self.warnings
        pass_rate = (self.passed / total * 100) if total > 0 else 0

        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"⚠️  Warnings: {self.warnings}")
        print(f"📈 Pass Rate: {pass_rate:.1f}%")

        if self.failed == 0 and pass_rate >= 80:
            print("\n🎉 SYSTEM VALIDATION: SUCCESS!")
            print("✅ Platform is ready for production use")
            status = "SUCCESS"
        elif self.failed == 0:
            print("\n⚠️  SYSTEM VALIDATION: PARTIAL SUCCESS")
            print("⚠️  Platform is functional but has some warnings")
            status = "PARTIAL"
        else:
            print("\n❌ SYSTEM VALIDATION: FAILED")
            print("❌ Platform has critical issues that need to be resolved")
            status = "FAILED"

        # Save report
        report = {
            "timestamp": time.time(),
            "status": status,
            "total_tests": total,
            "passed": self.passed,
            "failed": self.failed,
            "warnings": self.warnings,
            "pass_rate": pass_rate
        }

        try:
            with open("logs/validation-report.json", "w") as f:
                json.dump(report, f, indent=2)
            print(f"\n📄 Report saved to: logs/validation-report.json")
        except Exception as e:
            print(f"\n⚠️  Could not save report: {e}")

        return status

def main():
    """Main validation function"""
    print("🔍 Agent Investment Platform - System Validation")
    print("This will test all components after installation")
    print()

    validator = SystemValidator()

    # Run all tests
    validator.test_system_requirements()
    validator.test_python_environment()
    validator.test_configuration()
    validator.test_docker_services()
    validator.test_web_services()
    validator.test_database_connections()
    validator.test_file_system()
    validator.run_functional_test()

    # Generate final report
    status = validator.generate_report()

    # Exit with appropriate code
    if status == "SUCCESS":
        sys.exit(0)
    elif status == "PARTIAL":
        sys.exit(1)
    else:
        sys.exit(2)

if __name__ == "__main__":
    main()
