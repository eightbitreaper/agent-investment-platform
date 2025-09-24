#!/usr/bin/env python3
"""
Docker Management Script for Agent Investment Platform

This script provides easy commands to manage Docker services
for the Agent Investment Platform.
"""

import subprocess
import sys
import argparse
import time
from pathlib import Path

def run_command(command, capture_output=False):
    """Run a shell command and handle errors."""
    print(f"Running: {command}")
    try:
        if capture_output:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout, result.stderr
        else:
            result = subprocess.run(command, shell=True)
            return result.returncode == 0, "", ""
    except Exception as e:
        print(f"Error running command: {e}")
        return False, "", str(e)

def check_docker():
    """Check if Docker is installed and running."""
    print("Checking Docker installation...")

    # Check if Docker is installed
    success, stdout, stderr = run_command("docker --version", capture_output=True)
    if not success:
        print("❌ Docker is not installed or not in PATH")
        print("Please install Docker Desktop from: https://docs.docker.com/desktop/install/windows-install/")
        return False

    print(f"✅ Docker installed: {stdout.strip()}")

    # Check if Docker is running
    success, _, _ = run_command("docker info", capture_output=True)
    if not success:
        print("❌ Docker is not running")
        print("Please start Docker Desktop")
        return False

    print("✅ Docker is running")
    return True

def build_images():
    """Build Docker images."""
    print("Building Docker images...")

    commands = [
        "docker-compose build --no-cache",
        "docker-compose pull"
    ]

    for cmd in commands:
        success, _, _ = run_command(cmd)
        if not success:
            print(f"❌ Failed to execute: {cmd}")
            return False

    print("✅ Docker images built successfully")
    return True

def start_services(profile="production"):
    """Start Docker services with specified profile."""
    print(f"Starting services with profile: {profile}")

    # Load environment
    env_file = ".env.docker" if Path(".env.docker").exists() else ".env"

    cmd = f"docker-compose --profile {profile} --env-file {env_file} up -d"
    success, _, _ = run_command(cmd)

    if success:
        print("✅ Services started successfully")
        print_status()
    else:
        print("❌ Failed to start services")

    return success

def stop_services():
    """Stop all Docker services."""
    print("Stopping Docker services...")

    success, _, _ = run_command("docker-compose down")
    if success:
        print("✅ Services stopped successfully")
    else:
        print("❌ Failed to stop services")

    return success

def print_status():
    """Show status of all services."""
    print("\n" + "="*60)
    print("SERVICE STATUS")
    print("="*60)

    run_command("docker-compose ps")

    print("\n" + "="*60)
    print("ACCESS URLS")
    print("="*60)
    print("🌐 Main Application:     http://localhost:8000")
    print("📊 Grafana Monitoring:   http://localhost:3000")
    print("📈 Prometheus Metrics:   http://localhost:9090")
    print("🗄️  PostgreSQL:          localhost:5432")
    print("🔴 Redis:               localhost:6379")
    print("🤖 Ollama (if enabled): http://localhost:11434")

def show_logs(service=None):
    """Show logs for services."""
    if service:
        cmd = f"docker-compose logs -f {service}"
    else:
        cmd = "docker-compose logs -f"

    run_command(cmd)

def reset_data():
    """Reset all data volumes (WARNING: This will delete all data!)."""
    print("⚠️  WARNING: This will delete ALL data including databases!")
    response = input("Are you sure? Type 'YES' to confirm: ")

    if response == "YES":
        print("Stopping services and removing volumes...")
        run_command("docker-compose down -v")
        run_command("docker volume prune -f")
        print("✅ All data reset")
    else:
        print("Operation cancelled")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Docker Management for Agent Investment Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python docker-manager.py check           # Check Docker installation
  python docker-manager.py build           # Build Docker images
  python docker-manager.py start           # Start production services
  python docker-manager.py start --dev     # Start development environment
  python docker-manager.py stop            # Stop all services
  python docker-manager.py status          # Show service status
  python docker-manager.py logs            # Show all logs
  python docker-manager.py logs redis      # Show Redis logs
  python docker-manager.py reset           # Reset all data (WARNING!)
        """
    )

    parser.add_argument("command", choices=[
        "check", "build", "start", "stop", "status", "logs", "reset"
    ], help="Docker management command")

    parser.add_argument("--dev", action="store_true",
                       help="Use development profile")

    parser.add_argument("--monitoring", action="store_true",
                       help="Include monitoring services")

    parser.add_argument("--service", type=str,
                       help="Specific service for logs command")

    args = parser.parse_args()

    if args.command == "check":
        if not check_docker():
            sys.exit(1)

    elif args.command == "build":
        if not check_docker():
            sys.exit(1)
        if not build_images():
            sys.exit(1)

    elif args.command == "start":
        if not check_docker():
            sys.exit(1)

        profile = "development" if args.dev else "production"
        if args.monitoring:
            profile += ",monitoring"

        if not start_services(profile):
            sys.exit(1)

    elif args.command == "stop":
        if not stop_services():
            sys.exit(1)

    elif args.command == "status":
        print_status()

    elif args.command == "logs":
        show_logs(args.service)

    elif args.command == "reset":
        reset_data()

if __name__ == "__main__":
    main()
