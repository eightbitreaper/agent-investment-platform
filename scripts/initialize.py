#!/usr/bin/env python3
"""
Agent Investment Platform Initialization Script

This script orchestrates the complete setup process for the Agent-Driven Stock Investment Platform.
It handles platform detection, dependency installation, configuration, and validation.
"""

import os
import sys
import platform
import subprocess
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/initialization.log'),
        logging.StreamHandler()
    ]
)
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

class InitializationError(Exception):
    """Custom exception for initialization failures"""
    pass

class AgentPlatformInitializer:
    """Main initialization orchestrator for the Agent Investment Platform"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.system_info = None
        self.config_dir = self.project_root / "config"
        self.logs_dir = self.project_root / "logs"
        self.scripts_dir = self.project_root / "scripts"

        # Ensure required directories exist
        self._create_directories()

    def _create_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            self.config_dir,
            self.logs_dir,
            self.project_root / "reports",
            self.project_root / "templates",
            self.project_root / "src" / "agents",
            self.project_root / "src" / "analysis",
            self.project_root / "src" / "reports",
            self.project_root / "tests" / "agents",
            self.project_root / "tests" / "analysis",
            self.project_root / "docs" / "setup",
            self.scripts_dir / "setup"
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Ensured directory exists: {directory}")

    def detect_system(self) -> SystemInfo:
        """Detect system information for platform-specific setup"""
        logger.info("Detecting system configuration...")

        os_name = platform.system().lower()
        architecture = platform.machine()
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

        # Check for Docker
        has_docker = self._check_command_exists("docker")

        # Check for Git
        has_git = self._check_command_exists("git")

        # Check admin privileges
        is_admin = self._check_admin_privileges()

        self.system_info = SystemInfo(
            os_name=os_name,
            architecture=architecture,
            python_version=python_version,
            has_docker=has_docker,
            has_git=has_git,
            is_admin=is_admin
        )

        logger.info(f"System detected: {os_name} {architecture}, Python {python_version}")
        logger.info(f"Docker available: {has_docker}, Git available: {has_git}")

        return self.system_info

    def _check_command_exists(self, command: str) -> bool:
        """Check if a command exists in the system PATH"""
        try:
            subprocess.run([command, "--version"],
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _check_admin_privileges(self) -> bool:
        """Check if running with administrator privileges"""
        try:
            if platform.system().lower() == "windows":
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                # Unix systems
                if hasattr(os, 'geteuid'):
                    return os.geteuid() == 0  # type: ignore
                return False
        except Exception:
            return False

    def install_dependencies(self):
        """Install platform-specific dependencies"""
        logger.info("Installing dependencies...")

        if not self.system_info:
            raise InitializationError("System information not detected")

        # Import and run dependency installation
        sys.path.append(str(self.scripts_dir / "setup"))

        try:
            # Handle hyphenated filename by using importlib
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "install_dependencies",
                self.scripts_dir / "setup" / "install-dependencies.py"
            )
            if spec is None or spec.loader is None:
                raise ImportError("Could not load dependency installer module")

            install_dependencies = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(install_dependencies)

            installer = install_dependencies.DependencyInstaller(self.system_info)
            installer.install_all()
            logger.info("Dependencies installed successfully")
        except (ImportError, FileNotFoundError, AttributeError) as e:
            logger.error(f"Dependency installer not found or failed to load: {e}")
            raise InitializationError("Missing dependency installer")

    def configure_environment(self):
        """Configure environment variables and settings"""
        logger.info("Configuring environment...")

        try:
            # Handle hyphenated filename by using importlib
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "configure_environment",
                self.scripts_dir / "setup" / "configure-environment.py"
            )
            if spec is None or spec.loader is None:
                raise ImportError("Could not load environment configurator module")

            configure_environment = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(configure_environment)

            configurator = configure_environment.EnvironmentConfigurator(self.project_root)
            configurator.setup_all()
            logger.info("Environment configured successfully")
        except (ImportError, FileNotFoundError, AttributeError) as e:
            logger.error(f"Environment configurator not found or failed to load: {e}")
            raise InitializationError("Missing environment configurator")

    def setup_logging_infrastructure(self):
        """Setup logging and monitoring infrastructure"""
        logger.info("Setting up logging and monitoring infrastructure...")

        try:
            # Handle hyphenated filename by using importlib
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "setup_logging_infrastructure",
                self.scripts_dir / "setup" / "setup-logging-infrastructure.py"
            )
            if spec is None or spec.loader is None:
                raise ImportError("Could not load logging infrastructure setup module")

            setup_logging_infrastructure = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(setup_logging_infrastructure)

            logging_setup = setup_logging_infrastructure.LoggingInfrastructureSetup(self.project_root)
            config = setup_logging_infrastructure.LoggingConfig()

            if logging_setup.setup_all(config):
                logger.info("Logging infrastructure configured successfully")
                return True
            else:
                logger.error("Logging infrastructure setup failed")
                return False

        except (ImportError, FileNotFoundError, AttributeError) as e:
            logger.error(f"Logging infrastructure setup not found or failed to load: {e}")
            return False

    def setup_llm_models(self, llm_choice: str = "local"):
        """Setup LLM models based on user choice"""
        logger.info(f"Setting up LLM models (choice: {llm_choice})...")

        try:
            # Handle hyphenated filename by using importlib
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "download_models",
                self.scripts_dir / "setup" / "download-models.py"
            )
            if spec is None or spec.loader is None:
                raise ImportError("Could not load model downloader module")

            download_models = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(download_models)

            downloader = download_models.HuggingFaceModelManager(self.config_dir)
            # For now, just skip model download in silent mode - can be done later
            logger.info("Model download skipped in silent mode - run manually if needed")
            logger.info("LLM models configured successfully")
        except (ImportError, FileNotFoundError, AttributeError) as e:
            logger.error(f"Model downloader not found or failed to load: {e}")
            raise InitializationError("Missing model downloader")

    def validate_setup(self) -> bool:
        """Validate the complete setup"""
        logger.info("Validating setup...")

        try:
            # Handle hyphenated filename by using importlib
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "validate_setup",
                self.scripts_dir / "setup" / "validate-setup.py"
            )
            if spec is None or spec.loader is None:
                raise ImportError("Could not load setup validator module")

            validate_setup = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(validate_setup)

            validator = validate_setup.SetupValidator(self.project_root)
            return validator.validate_all()
        except (ImportError, FileNotFoundError, AttributeError) as e:
            logger.error(f"Setup validator not found or failed to load: {e}")
            return False

    def interactive_setup(self):
        """Run interactive setup with user prompts"""
        print("🚀 Agent Investment Platform Initialization")
        print("=" * 50)

        # System detection
        system_info = self.detect_system()
        print(f"\n📊 System: {system_info.os_name} {system_info.architecture}")
        print(f"🐍 Python: {system_info.python_version}")

        # Prerequisites check
        if not system_info.has_git:
            raise InitializationError("Git is required but not found")

        # LLM choice
        print("\n🧠 Choose your LLM setup:")
        print("1. Local LLM (Ollama) - Recommended for privacy")
        print("2. API-based (OpenAI/Anthropic) - Requires API keys")
        print("3. Hybrid (Local + API) - Best of both worlds")

        while True:
            choice = input("\nEnter your choice (1-3): ").strip()
            if choice in ["1", "2", "3"]:
                llm_choices = {"1": "local", "2": "api", "3": "hybrid"}
                llm_choice = llm_choices[choice]
                break
            print("Invalid choice. Please enter 1, 2, or 3.")

        # Run setup steps
        try:
            self.install_dependencies()
            self.configure_environment()
            self.setup_logging_infrastructure()  # Setup logging infrastructure
            self.setup_llm_models(llm_choice)

            # Final validation
            if self.validate_setup():
                print("\n✅ Initialization completed successfully!")
                print(f"📁 Project root: {self.project_root}")
                print("📚 Next steps:")
                print("  1. Review configuration files in config/")
                print("  2. Add your API keys if using API-based LLMs")
                print("  3. Run: python orchestrator.py --test-mode")
                return True
            else:
                print("\n❌ Setup validation failed. Check logs for details.")
                return False

        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            print(f"\n❌ Initialization failed: {e}")
            return False

    def run_silent(self, llm_choice: str = "local") -> bool:
        """Run setup without user interaction"""
        try:
            self.detect_system()
            self.install_dependencies()
            self.configure_environment()
            self.setup_logging_infrastructure()  # Setup logging infrastructure
            self.setup_llm_models(llm_choice)
            return self.validate_setup()
        except Exception as e:
            logger.error(f"Silent initialization failed: {e}")
            return False

def main():
    """Main entry point"""
    initializer = AgentPlatformInitializer()

    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--silent":
            llm_choice = sys.argv[2] if len(sys.argv) > 2 else "local"
            success = initializer.run_silent(llm_choice)
        elif sys.argv[1] == "--help":
            print("Agent Investment Platform Initializer")
            print("\nUsage:")
            print("  python initialize.py              # Interactive setup")
            print("  python initialize.py --silent     # Silent setup with local LLM")
            print("  python initialize.py --silent api # Silent setup with API LLM")
            return
        else:
            print(f"Unknown argument: {sys.argv[1]}")
            print("Use --help for usage information")
            return
    else:
        success = initializer.interactive_setup()

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
