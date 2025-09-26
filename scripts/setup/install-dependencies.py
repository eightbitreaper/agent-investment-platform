#!/usr/bin/env python3
"""
Dependency Installation Script for Agent Investment Platform

This script handles automated installation of platform-specific dependencies
including Docker, Python packages, and system requirements across Windows, Linux, and macOS.
"""

import os
import sys
import platform
import subprocess
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass

# Setup logging
logger = logging.getLogger(__name__)

@dataclass
class SystemInfo:
    """System information for platform-specific setup"""
    os_name: str
    architecture: str
    python_version: str
    has_docker: bool
    has_git: bool
    is_admin: bool

class DependencyError(Exception):
    """Custom exception for dependency installation failures"""
    pass

class DependencyInstaller:
    """Handles platform-specific dependency installation"""

    def __init__(self, system_info: SystemInfo):
        self.system_info = system_info
        self.project_root = Path(__file__).parent.parent.parent
        self.requirements_file = self.project_root / "requirements.txt"

    def install_all(self):
        """Install all required dependencies based on platform"""
        logger.info(f"Installing dependencies for {self.system_info.os_name}")

        try:
            # Install system dependencies
            self._install_system_dependencies()

            # Install Python dependencies
            self._install_python_dependencies()

            # Install Docker if needed
            self._install_docker()

            # Verify installations
            self._verify_installations()

            logger.info("All dependencies installed successfully")

        except Exception as e:
            logger.error(f"Dependency installation failed: {e}")
            raise DependencyError(f"Failed to install dependencies: {e}")

    def _install_system_dependencies(self):
        """Install platform-specific system dependencies"""
        if self.system_info.os_name == "windows":
            self._install_windows_dependencies()
        elif self.system_info.os_name == "linux":
            self._install_linux_dependencies()
        elif self.system_info.os_name == "darwin":  # macOS
            self._install_macos_dependencies()
        else:
            raise DependencyError(f"Unsupported operating system: {self.system_info.os_name}")

    def _install_windows_dependencies(self):
        """Install Windows-specific dependencies"""
        logger.info("Installing Windows dependencies...")

        # Check if running in WSL
        is_wsl = self._is_wsl()

        if is_wsl:
            logger.info("Detected WSL environment, using Linux installation method")
            self._install_linux_dependencies()
            return

        # For development environment, skip complex system package installation
        # Focus on Python packages and essential tools that are likely already present
        logger.info("Checking essential tools...")

        essential_tools = ["git", "python", "pip"]
        missing_tools = []

        for tool in essential_tools:
            if not self._check_command_exists(tool):
                missing_tools.append(tool)

        if missing_tools:
            logger.warning(f"Some essential tools are missing: {missing_tools}")
            logger.info("Please install missing tools manually or run as administrator")
        else:
            logger.info("Essential tools are available")

    def _install_linux_dependencies(self):
        """Install Linux-specific dependencies"""
        logger.info("Installing Linux dependencies...")

        # Detect package manager
        if self._check_command_exists("apt-get"):
            self._install_debian_dependencies()
        elif self._check_command_exists("yum"):
            self._install_redhat_dependencies()
        elif self._check_command_exists("pacman"):
            self._install_arch_dependencies()
        else:
            logger.warning("Unknown package manager, attempting generic installation")
            self._install_generic_linux_dependencies()

    def _install_debian_dependencies(self):
        """Install dependencies on Debian/Ubuntu systems"""
        logger.info("Installing Debian/Ubuntu dependencies...")

        # Update package list
        self._run_command(["sudo", "apt-get", "update"])

        # Install essential packages
        packages = [
            "python3", "python3-pip", "python3-venv", "python3-dev",
            "curl", "wget", "git", "build-essential", "software-properties-common",
            "apt-transport-https", "ca-certificates", "gnupg", "lsb-release"
        ]

        cmd = ["sudo", "apt-get", "install", "-y"] + packages
        self._run_command(cmd)

    def _install_redhat_dependencies(self):
        """Install dependencies on RedHat/CentOS systems"""
        logger.info("Installing RedHat/CentOS dependencies...")

        packages = [
            "python3", "python3-pip", "python3-devel",
            "curl", "wget", "git", "gcc", "gcc-c++", "make"
        ]

        cmd = ["sudo", "yum", "install", "-y"] + packages
        self._run_command(cmd)

    def _install_arch_dependencies(self):
        """Install dependencies on Arch Linux systems"""
        logger.info("Installing Arch Linux dependencies...")

        packages = [
            "python", "python-pip", "curl", "wget", "git", "base-devel"
        ]

        cmd = ["sudo", "pacman", "-S", "--noconfirm"] + packages
        self._run_command(cmd)

    def _install_generic_linux_dependencies(self):
        """Fallback installation for unknown Linux distributions"""
        logger.info("Attempting generic Linux dependency installation...")

        # Try to install Python if not present
        if not self._check_command_exists("python3"):
            logger.warning("Python3 not found. Please install Python 3.9+ manually.")

        # Try to install pip if not present
        if not self._check_command_exists("pip3"):
            logger.info("Attempting to install pip...")
            try:
                # Download get-pip.py
                import urllib.request
                urllib.request.urlretrieve("https://bootstrap.pypa.io/get-pip.py", "get-pip.py")
                self._run_command(["python3", "get-pip.py"])
                os.remove("get-pip.py")
            except Exception as e:
                logger.warning(f"Failed to install pip: {e}")

    def _install_macos_dependencies(self):
        """Install macOS-specific dependencies"""
        logger.info("Installing macOS dependencies...")

        # Install Homebrew if not present
        if not self._check_command_exists("brew"):
            logger.info("Installing Homebrew...")
            brew_install_cmd = [
                "/bin/bash", "-c",
                "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            ]
            self._run_command(brew_install_cmd)

        # Install essential packages via Homebrew
        packages = ["python@3.9", "git", "curl", "wget"]
        for package in packages:
            logger.info(f"Installing {package}...")
            self._run_command(["brew", "install", package])

    def _install_docker(self):
        """Install Docker if not present"""
        if self.system_info.has_docker:
            logger.info("Docker already installed")
            return

        logger.info("Installing Docker...")

        if self.system_info.os_name == "windows":
            self._install_docker_windows()
        elif self.system_info.os_name == "linux":
            self._install_docker_linux()
        elif self.system_info.os_name == "darwin":
            self._install_docker_macos()

    def _install_docker_windows(self):
        """Install Docker Desktop on Windows"""
        if self._is_wsl():
            logger.info("In WSL, Docker Desktop should be installed on Windows host")
            return

        logger.info("Installing Docker Desktop for Windows...")
        # Use Chocolatey if available
        if self._check_command_exists("choco"):
            self._run_command(["choco", "install", "docker-desktop", "-y"], admin_required=True)
        else:
            logger.warning("Please install Docker Desktop manually from https://docker.com/products/docker-desktop")

    def _install_docker_linux(self):
        """Install Docker on Linux"""
        logger.info("Installing Docker on Linux...")

        if self._check_command_exists("apt-get"):
            # Docker installation for Debian/Ubuntu
            commands = [
                ["curl", "-fsSL", "https://download.docker.com/linux/ubuntu/gpg", "|", "sudo", "gpg", "--dearmor", "-o", "/usr/share/keyrings/docker-archive-keyring.gpg"],
                ["echo", "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable", "|", "sudo", "tee", "/etc/apt/sources.list.d/docker.list"],
                ["sudo", "apt-get", "update"],
                ["sudo", "apt-get", "install", "-y", "docker-ce", "docker-ce-cli", "containerd.io", "docker-compose-plugin"]
            ]

            for cmd in commands:
                self._run_command(cmd)

            # Add user to docker group
            try:
                import getpass
                username = getpass.getuser()
                self._run_command(["sudo", "usermod", "-aG", "docker", username])
                logger.info("Added user to docker group. Please log out and back in for changes to take effect.")
            except Exception as e:
                logger.warning(f"Failed to add user to docker group: {e}")

        else:
            logger.warning("Please install Docker manually for your Linux distribution")

    def _install_docker_macos(self):
        """Install Docker Desktop on macOS"""
        logger.info("Installing Docker Desktop for macOS...")

        if self._check_command_exists("brew"):
            self._run_command(["brew", "install", "--cask", "docker"])
        else:
            logger.warning("Please install Docker Desktop manually from https://docker.com/products/docker-desktop")

    def _install_python_dependencies(self):
        """Install Python package dependencies"""
        logger.info("Installing Python dependencies...")

        # Ensure pip is up to date (minimum version 25.2 for security updates)
        self._run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip>=25.2"])

        # Install from requirements.txt if it exists
        if self.requirements_file.exists():
            logger.info(f"Installing from {self.requirements_file}")
            self._run_command([sys.executable, "-m", "pip", "install", "-r", str(self.requirements_file)])
        else:
            # Install essential packages directly
            essential_packages = [
                "requests>=2.31.0",
                "pyyaml>=6.0",
                "docker>=6.1.0",
                "python-dotenv>=1.0.0",
                "click>=8.1.0",
                "rich>=13.0.0",
                "httpx>=0.24.0",
                "asyncio",
                "aiofiles>=23.0.0",
                # Logging and monitoring dependencies
                "elasticsearch>=8.11.0",
                "websockets>=12.0",
                "aiohttp-cors>=0.7.0",
                "fastapi>=0.104.0",
                "uvicorn[standard]>=0.24.0"
            ]

            logger.info("Installing essential Python packages...")
            for package in essential_packages:
                self._run_command([sys.executable, "-m", "pip", "install", package])

    def _verify_installations(self):
        """Verify all required dependencies are properly installed"""
        logger.info("Verifying installations...")

        # Check Python
        if sys.version_info < (3, 9):
            raise DependencyError("Python 3.9+ is required")

        # Check essential commands
        required_commands = ["git", "python3" if self.system_info.os_name != "windows" else "python"]

        for cmd in required_commands:
            if not self._check_command_exists(cmd):
                raise DependencyError(f"Required command not found: {cmd}")

        # Check Python packages
        required_packages = ["requests", "yaml", "docker", "click"]

        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                raise DependencyError(f"Required Python package not found: {package}")

        logger.info("All dependencies verified successfully")

    def _is_wsl(self) -> bool:
        """Check if running in Windows Subsystem for Linux"""
        try:
            with open('/proc/version', 'r') as f:
                return 'microsoft' in f.read().lower()
        except FileNotFoundError:
            return False

    def _check_command_exists(self, command: str) -> bool:
        """Check if a command exists in the system PATH"""
        return shutil.which(command) is not None

    def _run_command(self, cmd: List[str], admin_required: bool = False) -> subprocess.CompletedProcess:
        """Run a system command with proper error handling"""
        logger.debug(f"Running command: {' '.join(cmd)}")

        try:
            if admin_required and self.system_info.os_name == "windows" and not self.system_info.is_admin:
                logger.warning("Administrator privileges required for some operations.")
                logger.info("Attempting to proceed without elevation (some features may not work)")
                # Skip admin elevation for development environment
                # The command will run as current user

            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.stdout:
                logger.debug(f"Command output: {result.stdout}")

            return result

        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {' '.join(cmd)}")
            logger.error(f"Error: {e.stderr if e.stderr else e}")
            raise DependencyError(f"Command failed: {e}")

        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {' '.join(cmd)}")
            raise DependencyError("Command execution timed out")

def main():
    """Main entry point for standalone execution"""
    # This would typically be called from the main initialize.py script
    # But can also be run standalone for testing

    print("Dependency Installer - Test Mode")
    print("This script is typically called from initialize.py")

    # Basic system detection for testing
    system_info = SystemInfo(
        os_name=platform.system().lower(),
        architecture=platform.machine(),
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        has_docker=shutil.which("docker") is not None,
        has_git=shutil.which("git") is not None,
        is_admin=False  # Simplified for testing
    )

    installer = DependencyInstaller(system_info)

    try:
        installer.install_all()
        print("✅ Dependencies installed successfully")
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
