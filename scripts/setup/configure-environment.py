#!/usr/bin/env python3
"""
Environment Configuration Script for Agent Investment Platform

This script handles automated configuration of environment variables,
configuration files, and workspace settings for the platform.
"""

import os
import sys
import json
import yaml
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass, asdict
from dotenv import load_dotenv, set_key
import secrets
import string

# Setup logging
logger = logging.getLogger(__name__)

@dataclass
class LLMConfig:
    """Configuration for LLM services"""
    provider: str  # "local", "openai", "anthropic", "hybrid"
    local_endpoint: str = "http://localhost:11434"
    api_key: Optional[str] = None
    model_name: str = "llama3.1"
    max_tokens: int = 4096
    temperature: float = 0.7

@dataclass
class MCPServerConfig:
    """Configuration for MCP servers"""
    name: str
    command: str
    args: List[str]
    env: Dict[str, str]
    enabled: bool = True

@dataclass
class DataSourceConfig:
    """Configuration for data sources"""
    name: str
    api_key: Optional[str] = None
    endpoint: str = ""
    rate_limit: int = 100
    enabled: bool = True

@dataclass
class NotificationConfig:
    """Configuration for notifications"""
    email_enabled: bool = False
    email_smtp_host: str = ""
    email_smtp_port: int = 587
    email_username: str = ""
    email_password: str = ""
    discord_enabled: bool = False
    discord_webhook_url: str = ""

class EnvironmentConfigurator:
    """Handles environment configuration and setup"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.config_dir = project_root / "config"
        self.env_file = project_root / ".env"
        self.env_example = project_root / ".env.example"

        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)

    def setup_all(self):
        """Setup complete environment configuration"""
        logger.info("Configuring environment...")

        try:
            # Create configuration files
            self._create_env_example()
            self._create_env_file()
            self._create_llm_config()
            self._create_mcp_servers_config()
            self._create_data_sources_config()
            self._create_strategies_config()
            self._create_notification_config()

            # Load environment variables
            self._load_environment()

            logger.info("Environment configuration completed successfully")

        except Exception as e:
            logger.error(f"Environment configuration failed: {e}")
            raise

    def _create_env_example(self):
        """Create .env.example template file"""

        # Check if a comprehensive .env.example already exists
        if self.env_example.exists():
            content = self.env_example.read_text()
            # If file has substantial content (more than basic template), preserve it
            if len(content.splitlines()) > 50:
                logger.info(".env.example already exists with comprehensive configuration, preserving it")
                return

        logger.info("Creating .env.example template...")

        env_template = """# Agent Investment Platform Environment Variables
# Copy this file to .env and fill in your actual values

# =============================================================================
# LLM Configuration
# =============================================================================
# Choose: local, openai, anthropic, hybrid
LLM_PROVIDER=local

# For local LLM (Ollama)
LOCAL_LLM_ENDPOINT=http://localhost:11434
LOCAL_LLM_MODEL=llama3.1

# For API-based LLMs (uncomment and fill in as needed)
# OPENAI_API_KEY=your_openai_api_key_here
# ANTHROPIC_API_KEY=your_anthropic_api_key_here

# =============================================================================
# Data Source API Keys
# =============================================================================
# Stock Data APIs
# ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
# YAHOO_FINANCE_API_KEY=your_yahoo_finance_key_here
# FINNHUB_API_KEY=your_finnhub_key_here

# News APIs
# NEWS_API_KEY=your_news_api_key_here
# GOOGLE_NEWS_API_KEY=your_google_news_key_here

# Social Media APIs
# REDDIT_CLIENT_ID=your_reddit_client_id_here
# REDDIT_CLIENT_SECRET=your_reddit_client_secret_here
# TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here

# YouTube API
# YOUTUBE_API_KEY=your_youtube_api_key_here

# =============================================================================
# GitHub Integration
# =============================================================================
# GitHub token for report uploads
# GITHUB_TOKEN=your_github_token_here
GITHUB_REPO=eightbitreaper/agent-investment-platform
GITHUB_REPORTS_BRANCH=reports

# =============================================================================
# Notification Settings
# =============================================================================
# Email notifications
EMAIL_ENABLED=false
# EMAIL_SMTP_HOST=smtp.gmail.com
# EMAIL_SMTP_PORT=587
# EMAIL_USERNAME=your_email@gmail.com
# EMAIL_PASSWORD=your_app_password_here
# EMAIL_TO_ADDRESS=alerts@yourdomain.com

# Discord notifications
DISCORD_ENABLED=false
# DISCORD_WEBHOOK_URL=your_discord_webhook_url_here

# =============================================================================
# System Configuration
# =============================================================================
# Report generation schedule (cron format)
REPORT_SCHEDULE_HOURLY=0 * * * *
REPORT_SCHEDULE_DAILY=0 9 * * *
REPORT_SCHEDULE_WEEKLY=0 9 * * 1

# Logging level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# Data retention (days)
DATA_RETENTION_DAYS=30

# System timezone
TIMEZONE=UTC

# =============================================================================
# Security
# =============================================================================
# Secret key for internal operations (auto-generated)
SECRET_KEY=

# API rate limiting
API_RATE_LIMIT_PER_HOUR=1000
"""

        with open(self.env_example, 'w') as f:
            f.write(env_template)

        logger.info(f"Created {self.env_example}")

    def _create_env_file(self):
        """Create .env file from template if it doesn't exist"""
        if self.env_file.exists():
            logger.info(".env file already exists, skipping creation")
            return

        logger.info("Creating .env file from template...")

        # Copy from example
        shutil.copy2(self.env_example, self.env_file)

        # Generate secret key
        secret_key = self._generate_secret_key()
        set_key(str(self.env_file), "SECRET_KEY", secret_key)

        logger.info(f"Created {self.env_file}")
        logger.warning("Please edit .env file and add your API keys and configuration")

    def _create_llm_config(self):
        """Create LLM configuration file"""

        config_file = self.config_dir / "llm-config.yaml"

        # Check if comprehensive config already exists
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    existing_config = yaml.safe_load(f)
                # If config has substantial content, preserve it
                if existing_config and len(str(existing_config)) > 1000:
                    logger.info("LLM config already exists with comprehensive configuration, preserving it")
                    return
            except Exception:
                pass  # If we can't read it, create new one

        logger.info("Creating LLM configuration...")

        llm_config = {
            "providers": {
                "local": {
                    "type": "ollama",
                    "endpoint": "${LOCAL_LLM_ENDPOINT:-http://localhost:11434}",
                    "models": {
                        "default": "${LOCAL_LLM_MODEL:-llama3.1}",
                        "analysis": "llama3.1",
                        "reporting": "llama3.1:70b",
                        "coding": "codellama"
                    },
                    "parameters": {
                        "temperature": 0.7,
                        "max_tokens": 4096,
                        "top_p": 0.9
                    }
                },
                "openai": {
                    "type": "openai",
                    "api_key": "${OPENAI_API_KEY}",
                    "models": {
                        "default": "gpt-4o",
                        "analysis": "gpt-4o",
                        "reporting": "gpt-4o",
                        "coding": "gpt-4o"
                    },
                    "parameters": {
                        "temperature": 0.7,
                        "max_tokens": 4096,
                        "top_p": 1.0
                    }
                },
                "anthropic": {
                    "type": "anthropic",
                    "api_key": "${ANTHROPIC_API_KEY}",
                    "models": {
                        "default": "claude-3-5-sonnet-20241022",
                        "analysis": "claude-3-5-sonnet-20241022",
                        "reporting": "claude-3-5-sonnet-20241022",
                        "coding": "claude-3-5-sonnet-20241022"
                    },
                    "parameters": {
                        "temperature": 0.7,
                        "max_tokens": 4096,
                        "top_p": 1.0
                    }
                }
            },
            "default_provider": "${LLM_PROVIDER:-local}",
            "fallback_order": ["local", "openai", "anthropic"],
            "retry_config": {
                "max_retries": 3,
                "backoff_factor": 2,
                "timeout_seconds": 30
            }
        }

        with open(config_file, 'w') as f:
            yaml.dump(llm_config, f, default_flow_style=False, indent=2)

        logger.info(f"Created {config_file}")

    def _create_mcp_servers_config(self):
        """Create MCP servers configuration"""

        config_file = self.config_dir / "mcp-servers.json"

        # Check if comprehensive config already exists
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    existing_config = json.load(f)
                # If config has substantial content, preserve it
                if existing_config and len(str(existing_config)) > 1000:
                    logger.info("MCP servers config already exists with comprehensive configuration, preserving it")
                    return
            except Exception:
                pass  # If we can't read it, create new one

        logger.info("Creating MCP servers configuration...")

        mcp_config = {
            "mcpServers": {
                "stock-data": {
                    "command": "python",
                    "args": ["-m", "src.agents.stock_data_agent"],
                    "env": {
                        "ALPHA_VANTAGE_API_KEY": "${ALPHA_VANTAGE_API_KEY}",
                        "YAHOO_FINANCE_API_KEY": "${YAHOO_FINANCE_API_KEY}",
                        "FINNHUB_API_KEY": "${FINNHUB_API_KEY}"
                    },
                    "enabled": True
                },
                "news-agent": {
                    "command": "python",
                    "args": ["-m", "src.agents.news_agent"],
                    "env": {
                        "NEWS_API_KEY": "${NEWS_API_KEY}",
                        "GOOGLE_NEWS_API_KEY": "${GOOGLE_NEWS_API_KEY}"
                    },
                    "enabled": True
                },
                "youtube-agent": {
                    "command": "python",
                    "args": ["-m", "src.agents.youtube_agent"],
                    "env": {
                        "YOUTUBE_API_KEY": "${YOUTUBE_API_KEY}"
                    },
                    "enabled": True
                },
                "reddit-agent": {
                    "command": "python",
                    "args": ["-m", "src.agents.reddit_agent"],
                    "env": {
                        "REDDIT_CLIENT_ID": "${REDDIT_CLIENT_ID}",
                        "REDDIT_CLIENT_SECRET": "${REDDIT_CLIENT_SECRET}"
                    },
                    "enabled": False
                },
                "twitter-agent": {
                    "command": "python",
                    "args": ["-m", "src.agents.twitter_agent"],
                    "env": {
                        "TWITTER_BEARER_TOKEN": "${TWITTER_BEARER_TOKEN}"
                    },
                    "enabled": False
                }
            }
        }

        with open(config_file, 'w') as f:
            json.dump(mcp_config, f, indent=2)

        logger.info(f"Created {config_file}")

    def _create_data_sources_config(self):
        """Create data sources configuration"""

        config_file = self.config_dir / "data-sources.yaml"

        # Check if comprehensive config already exists
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    existing_config = yaml.safe_load(f)
                # If config has substantial content, preserve it
                if existing_config and len(str(existing_config)) > 1000:
                    logger.info("Data sources config already exists with comprehensive configuration, preserving it")
                    return
            except Exception:
                pass  # If we can't read it, create new one

        logger.info("Creating data sources configuration...")

        data_sources_config = {
            "stock_apis": {
                "alpha_vantage": {
                    "enabled": True,
                    "api_key": "${ALPHA_VANTAGE_API_KEY}",
                    "base_url": "https://www.alphavantage.co/query",
                    "rate_limit": 5,  # requests per minute
                    "endpoints": {
                        "quote": "GLOBAL_QUOTE",
                        "intraday": "TIME_SERIES_INTRADAY",
                        "daily": "TIME_SERIES_DAILY"
                    }
                },
                "yahoo_finance": {
                    "enabled": True,
                    "api_key": "${YAHOO_FINANCE_API_KEY}",
                    "base_url": "https://query1.finance.yahoo.com/v8/finance/chart",
                    "rate_limit": 100
                },
                "finnhub": {
                    "enabled": False,
                    "api_key": "${FINNHUB_API_KEY}",
                    "base_url": "https://finnhub.io/api/v1",
                    "rate_limit": 60
                }
            },
            "news_apis": {
                "news_api": {
                    "enabled": True,
                    "api_key": "${NEWS_API_KEY}",
                    "base_url": "https://newsapi.org/v2",
                    "rate_limit": 1000
                },
                "google_news": {
                    "enabled": False,
                    "api_key": "${GOOGLE_NEWS_API_KEY}",
                    "base_url": "https://news.google.com/rss",
                    "rate_limit": 100
                }
            },
            "social_apis": {
                "reddit": {
                    "enabled": False,
                    "client_id": "${REDDIT_CLIENT_ID}",
                    "client_secret": "${REDDIT_CLIENT_SECRET}",
                    "user_agent": "Agent Investment Platform v1.0",
                    "subreddits": ["investing", "stocks", "SecurityAnalysis", "ValueInvesting"]
                },
                "twitter": {
                    "enabled": False,
                    "bearer_token": "${TWITTER_BEARER_TOKEN}",
                    "rate_limit": 300
                }
            },
            "youtube": {
                "enabled": True,
                "api_key": "${YOUTUBE_API_KEY}",
                "channels": [
                    "UC_-8FbSHSCNR-8WhKk0Fw8w",  # Example finance channel
                    "UCXuqSBlHAE6Xw-yeJA0Tunw"   # Example investing channel
                ],
                "rate_limit": 100
            }
        }

        with open(config_file, 'w') as f:
            yaml.dump(data_sources_config, f, default_flow_style=False, indent=2)

        logger.info(f"Created {config_file}")

    def _create_strategies_config(self):
        """Create investment strategies configuration"""

        config_file = self.config_dir / "strategies.yaml"

        # Check if comprehensive config already exists
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    existing_config = yaml.safe_load(f)
                # If config has substantial content, preserve it
                if existing_config and len(str(existing_config)) > 1000:
                    logger.info("Strategies config already exists with comprehensive configuration, preserving it")
                    return
            except Exception:
                pass  # If we can't read it, create new one

        logger.info("Creating strategies configuration...")

        strategies_config = {
            "strategies": {
                "value_investing": {
                    "name": "Value Investing",
                    "description": "Focus on undervalued companies with strong fundamentals",
                    "enabled": True,
                    "parameters": {
                        "pe_ratio_max": 15,
                        "debt_to_equity_max": 0.5,
                        "roe_min": 0.15,
                        "revenue_growth_min": 0.05
                    },
                    "prompt_template": "templates/strategy-prompts/value-investing.md",
                    "weight": 0.4
                },
                "momentum": {
                    "name": "Momentum Strategy",
                    "description": "Follow trending stocks with strong price momentum",
                    "enabled": True,
                    "parameters": {
                        "rsi_min": 50,
                        "rsi_max": 70,
                        "moving_average_period": 20,
                        "volume_increase_threshold": 1.5
                    },
                    "prompt_template": "templates/strategy-prompts/momentum.md",
                    "weight": 0.3
                },
                "meme_stocks": {
                    "name": "Meme Stock Tracker",
                    "description": "Monitor social sentiment for viral stock movements",
                    "enabled": False,
                    "parameters": {
                        "social_mention_threshold": 100,
                        "sentiment_score_min": 0.6,
                        "volume_spike_threshold": 3.0
                    },
                    "prompt_template": "templates/strategy-prompts/meme-stocks.md",
                    "weight": 0.2
                },
                "dividend_growth": {
                    "name": "Dividend Growth",
                    "description": "Focus on companies with consistent dividend growth",
                    "enabled": True,
                    "parameters": {
                        "dividend_yield_min": 0.02,
                        "dividend_growth_years": 5,
                        "payout_ratio_max": 0.6
                    },
                    "prompt_template": "templates/strategy-prompts/dividend-growth.md",
                    "weight": 0.1
                }
            },
            "risk_management": {
                "max_position_size": 0.05,
                "stop_loss_percentage": 0.1,
                "portfolio_diversification_min": 10,
                "sector_concentration_max": 0.3
            },
            "reporting": {
                "confidence_threshold": 0.7,
                "recommendation_categories": ["STRONG_BUY", "BUY", "HOLD", "SELL", "STRONG_SELL"],
                "include_uncertainty": True
            }
        }

        with open(config_file, 'w') as f:
            yaml.dump(strategies_config, f, default_flow_style=False, indent=2)

        logger.info(f"Created {config_file}")

    def _create_notification_config(self):
        """Create notification configuration"""

        config_file = self.config_dir / "notification-config.yaml"

        # Check if comprehensive config already exists
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    existing_config = yaml.safe_load(f)
                # If config has substantial content, preserve it
                if existing_config and len(str(existing_config)) > 1000:
                    logger.info("Notification config already exists with comprehensive configuration, preserving it")
                    return
            except Exception:
                pass  # If we can't read it, create new one

        logger.info("Creating notification configuration...")

        notification_config = {
            "email": {
                "enabled": "${EMAIL_ENABLED:-false}",
                "smtp_host": "${EMAIL_SMTP_HOST:-smtp.gmail.com}",
                "smtp_port": "${EMAIL_SMTP_PORT:-587}",
                "username": "${EMAIL_USERNAME}",
                "password": "${EMAIL_PASSWORD}",
                "to_address": "${EMAIL_TO_ADDRESS}",
                "from_address": "${EMAIL_USERNAME}",
                "use_tls": True,
                "triggers": {
                    "strong_buy": True,
                    "strong_sell": True,
                    "high_volatility": True,
                    "system_error": True
                }
            },
            "discord": {
                "enabled": "${DISCORD_ENABLED:-false}",
                "webhook_url": "${DISCORD_WEBHOOK_URL}",
                "triggers": {
                    "daily_summary": True,
                    "strong_signals": True,
                    "system_status": False
                }
            },
            "urgency_levels": {
                "low": {
                    "threshold": 0.3,
                    "methods": []
                },
                "medium": {
                    "threshold": 0.6,
                    "methods": ["discord"]
                },
                "high": {
                    "threshold": 0.8,
                    "methods": ["email", "discord"]
                },
                "critical": {
                    "threshold": 0.95,
                    "methods": ["email", "discord"]
                }
            }
        }

        with open(config_file, 'w') as f:
            yaml.dump(notification_config, f, default_flow_style=False, indent=2)

        logger.info(f"Created {config_file}")

    def _load_environment(self):
        """Load environment variables from .env file"""
        if self.env_file.exists():
            load_dotenv(self.env_file)
            logger.info("Loaded environment variables from .env")
        else:
            logger.warning("No .env file found")

    def _generate_secret_key(self, length: int = 32) -> str:
        """Generate a random secret key"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def interactive_setup(self):
        """Interactive configuration setup with user prompts"""
        print("\n🔧 Environment Configuration")
        print("=" * 40)

        # LLM Provider choice
        print("\n🧠 Choose your LLM provider:")
        print("1. Local (Ollama) - Free, private, requires local installation")
        print("2. OpenAI - Paid API, high quality, cloud-based")
        print("3. Anthropic (Claude) - Paid API, excellent analysis, cloud-based")
        print("4. Hybrid - Local for processing, API for complex analysis")

        while True:
            choice = input("\nEnter your choice (1-4): ").strip()
            if choice in ["1", "2", "3", "4"]:
                providers = {"1": "local", "2": "openai", "3": "anthropic", "4": "hybrid"}
                llm_provider = providers[choice]
                break
            print("Invalid choice. Please enter 1, 2, 3, or 4.")

        # Update .env with provider choice
        set_key(str(self.env_file), "LLM_PROVIDER", llm_provider)

        # API key setup for non-local providers
        if llm_provider in ["openai", "hybrid"]:
            api_key = input("\n🔑 Enter your OpenAI API key (or press Enter to skip): ").strip()
            if api_key:
                set_key(str(self.env_file), "OPENAI_API_KEY", api_key)

        if llm_provider in ["anthropic", "hybrid"]:
            api_key = input("\n🔑 Enter your Anthropic API key (or press Enter to skip): ").strip()
            if api_key:
                set_key(str(self.env_file), "ANTHROPIC_API_KEY", api_key)

        # Notification setup
        print("\n📧 Setup notifications (optional):")

        email_setup = input("Enable email notifications? (y/N): ").strip().lower()
        if email_setup == 'y':
            set_key(str(self.env_file), "EMAIL_ENABLED", "true")

            email = input("Email address: ").strip()
            if email:
                set_key(str(self.env_file), "EMAIL_USERNAME", email)
                set_key(str(self.env_file), "EMAIL_TO_ADDRESS", email)

            password = input("Email app password (for Gmail use app-specific password): ").strip()
            if password:
                set_key(str(self.env_file), "EMAIL_PASSWORD", password)

        discord_setup = input("Enable Discord notifications? (y/N): ").strip().lower()
        if discord_setup == 'y':
            set_key(str(self.env_file), "DISCORD_ENABLED", "true")

            webhook = input("Discord webhook URL: ").strip()
            if webhook:
                set_key(str(self.env_file), "DISCORD_WEBHOOK_URL", webhook)

        print("\n✅ Basic configuration completed!")
        print("📝 You can add API keys for data sources by editing the .env file")
        print(f"📄 Configuration files created in: {self.config_dir}")

def main():
    """Main entry point for standalone execution"""
    project_root = Path(__file__).parent.parent.parent
    configurator = EnvironmentConfigurator(project_root)

    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        configurator.setup_all()
        configurator.interactive_setup()
    else:
        configurator.setup_all()
        print("✅ Environment configuration completed")
        print("💡 Run with --interactive for guided setup")

if __name__ == "__main__":
    main()
