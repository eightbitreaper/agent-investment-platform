"""
Risk Configuration Manager

This module provides configuration management for the risk management system,
including loading YAML configurations, strategy-specific settings, market regime
adjustments, and dynamic risk parameter management.

Key Features:
- YAML configuration loading and validation
- Strategy-specific risk parameter management
- Market regime-based parameter adjustment
- Risk profile templates
- Dynamic configuration updates
- Configuration validation and error handling
"""

import yaml
import os
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from enum import Enum
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketRegime(Enum):
    """Market regime classifications"""
    BULL_MARKET = "bull_market"
    BEAR_MARKET = "bear_market"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"
    NORMAL = "normal"

class RiskProfile(Enum):
    """Risk profile classifications"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"

@dataclass
class StrategyRiskConfig:
    """Risk configuration for a specific strategy"""
    strategy_name: str
    max_portfolio_risk: float = 0.02
    max_position_size: float = 0.05
    position_sizing_method: str = "volatility_based"
    stop_loss_method: str = "atr_based"
    take_profit_method: str = "risk_reward_ratio"
    target_risk_reward: float = 2.0
    max_correlation: float = 0.70
    custom_params: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'strategy_name': self.strategy_name,
            'max_portfolio_risk': self.max_portfolio_risk,
            'max_position_size': self.max_position_size,
            'position_sizing_method': self.position_sizing_method,
            'stop_loss_method': self.stop_loss_method,
            'take_profit_method': self.take_profit_method,
            'target_risk_reward': self.target_risk_reward,
            'max_correlation': self.max_correlation,
            'custom_params': self.custom_params
        }

@dataclass
class GlobalRiskConfig:
    """Global risk configuration settings"""
    max_portfolio_risk: float = 0.02
    max_position_size: float = 0.05
    max_sector_concentration: float = 0.20
    max_correlation: float = 0.70
    max_leverage: float = 1.0
    max_daily_loss: float = 0.03
    max_drawdown: float = 0.15
    min_liquidity_ratio: float = 0.05

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'max_portfolio_risk': self.max_portfolio_risk,
            'max_position_size': self.max_position_size,
            'max_sector_concentration': self.max_sector_concentration,
            'max_correlation': self.max_correlation,
            'max_leverage': self.max_leverage,
            'max_daily_loss': self.max_daily_loss,
            'max_drawdown': self.max_drawdown,
            'min_liquidity_ratio': self.min_liquidity_ratio
        }

class RiskConfigManager:
    """
    Comprehensive risk configuration management system.

    This class handles loading, validating, and managing risk configuration
    settings from YAML files, including strategy-specific parameters,
    market regime adjustments, and dynamic configuration updates.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Risk Configuration Manager

        Args:
            config_path: Path to the risk management YAML configuration file
        """
        self.config_path = config_path or self._find_config_file()
        self.config_data: Dict[str, Any] = {}
        self.global_config: Optional[GlobalRiskConfig] = None
        self.strategy_configs: Dict[str, StrategyRiskConfig] = {}
        self.current_regime: MarketRegime = MarketRegime.NORMAL
        self.current_profile: RiskProfile = RiskProfile.MODERATE

        # Load configuration
        self.load_configuration()
        logger.info(f"RiskConfigManager initialized with config: {self.config_path}")

    def _find_config_file(self) -> str:
        """Find the risk management configuration file"""
        possible_paths = [
            "config/risk_management.yaml",
            "../config/risk_management.yaml",
            "../../config/risk_management.yaml",
            os.path.join(os.path.dirname(__file__), "../../config/risk_management.yaml")
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        # If no config file found, create default
        logger.warning("No risk management config file found, using defaults")
        return self._create_default_config()

    def _create_default_config(self) -> str:
        """Create a default configuration file"""
        default_config = {
            'global_risk': {
                'max_portfolio_risk': 0.02,
                'max_position_size': 0.05,
                'max_sector_concentration': 0.20,
                'max_correlation': 0.70,
                'max_leverage': 1.0,
                'max_daily_loss': 0.03,
                'max_drawdown': 0.15,
                'min_liquidity_ratio': 0.05
            },
            'position_sizing': {
                'default_method': 'volatility_based'
            },
            'stop_loss': {
                'default_method': 'atr_based',
                'max_stop_loss': 0.10,
                'min_stop_loss': 0.01
            },
            'take_profit': {
                'default_method': 'risk_reward_ratio'
            }
        }

        config_path = "default_risk_config.yaml"
        try:
            with open(config_path, 'w') as f:
                yaml.dump(default_config, f, default_flow_style=False)
            logger.info(f"Created default config file: {config_path}")
        except Exception as e:
            logger.error(f"Error creating default config: {str(e)}")

        return config_path

    def load_configuration(self) -> bool:
        """
        Load configuration from YAML file

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.config_path, 'r') as f:
                self.config_data = yaml.safe_load(f)

            # Parse global configuration
            self._parse_global_config()

            # Parse strategy configurations
            self._parse_strategy_configs()

            logger.info("Risk configuration loaded successfully")
            return True

        except FileNotFoundError:
            logger.error(f"Configuration file not found: {self.config_path}")
            return False
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML configuration: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            return False

    def _parse_global_config(self):
        """Parse global risk configuration"""
        global_risk = self.config_data.get('global_risk', {})

        self.global_config = GlobalRiskConfig(
            max_portfolio_risk=global_risk.get('max_portfolio_risk', 0.02),
            max_position_size=global_risk.get('max_position_size', 0.05),
            max_sector_concentration=global_risk.get('max_sector_concentration', 0.20),
            max_correlation=global_risk.get('max_correlation', 0.70),
            max_leverage=global_risk.get('max_leverage', 1.0),
            max_daily_loss=global_risk.get('max_daily_loss', 0.03),
            max_drawdown=global_risk.get('max_drawdown', 0.15),
            min_liquidity_ratio=global_risk.get('min_liquidity_ratio', 0.05)
        )

    def _parse_strategy_configs(self):
        """Parse strategy-specific configurations"""
        strategies = self.config_data.get('strategies', {})

        for strategy_name, strategy_config in strategies.items():
            self.strategy_configs[strategy_name] = StrategyRiskConfig(
                strategy_name=strategy_name,
                max_portfolio_risk=strategy_config.get('max_portfolio_risk', 0.02),
                max_position_size=strategy_config.get('max_position_size', 0.05),
                position_sizing_method=strategy_config.get('position_sizing_method', 'volatility_based'),
                stop_loss_method=strategy_config.get('stop_loss_method', 'atr_based'),
                take_profit_method=strategy_config.get('take_profit_method', 'risk_reward_ratio'),
                target_risk_reward=strategy_config.get('target_risk_reward', 2.0),
                max_correlation=strategy_config.get('max_correlation', 0.70),
                custom_params={k: v for k, v in strategy_config.items()
                             if k not in ['max_portfolio_risk', 'max_position_size',
                                        'position_sizing_method', 'stop_loss_method',
                                        'take_profit_method', 'target_risk_reward', 'max_correlation']}
            )

    def get_global_config(self) -> GlobalRiskConfig:
        """Get global risk configuration"""
        if self.global_config is None:
            return GlobalRiskConfig()  # Return default if not loaded
        return self.global_config

    def get_strategy_config(self, strategy_name: str) -> StrategyRiskConfig:
        """
        Get risk configuration for a specific strategy

        Args:
            strategy_name: Name of the strategy

        Returns:
            StrategyRiskConfig for the strategy
        """
        if strategy_name in self.strategy_configs:
            return self.strategy_configs[strategy_name]

        # Return default strategy config if not found
        logger.warning(f"Strategy config not found for {strategy_name}, using default")
        return StrategyRiskConfig(strategy_name=strategy_name)

    def get_position_sizing_config(self, method: str = None) -> Dict[str, Any]:
        """
        Get position sizing configuration

        Args:
            method: Specific method to get config for

        Returns:
            Position sizing configuration dict
        """
        position_sizing = self.config_data.get('position_sizing', {})

        if method is None:
            return position_sizing

        # Get specific method configuration
        method_config = position_sizing.get(method, {})

        # Add default method if not specified
        if not method_config and method == position_sizing.get('default_method'):
            method_config = {'method': method}

        return method_config

    def get_stop_loss_config(self, method: str = None) -> Dict[str, Any]:
        """
        Get stop-loss configuration

        Args:
            method: Specific method to get config for

        Returns:
            Stop-loss configuration dict
        """
        stop_loss = self.config_data.get('stop_loss', {})

        if method is None:
            return stop_loss

        # Get specific method configuration
        method_config = stop_loss.get(method, {})

        # Add global stop-loss limits
        method_config.update({
            'max_stop_loss': stop_loss.get('max_stop_loss', 0.10),
            'min_stop_loss': stop_loss.get('min_stop_loss', 0.01)
        })

        return method_config

    def get_take_profit_config(self, method: str = None) -> Dict[str, Any]:
        """
        Get take-profit configuration

        Args:
            method: Specific method to get config for

        Returns:
            Take-profit configuration dict
        """
        take_profit = self.config_data.get('take_profit', {})

        if method is None:
            return take_profit

        # Get specific method configuration
        return take_profit.get(method, {})

    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get portfolio monitoring configuration"""
        return self.config_data.get('monitoring', {
            'check_interval_minutes': 15,
            'alert_cooldown_minutes': 60,
            'thresholds': {}
        })

    def apply_market_regime(self, regime: MarketRegime) -> bool:
        """
        Apply market regime adjustments to risk parameters

        Args:
            regime: Market regime to apply

        Returns:
            True if successful, False otherwise
        """
        try:
            self.current_regime = regime

            regime_config = self.config_data.get('market_regimes', {}).get(regime.value, {})

            if not regime_config:
                logger.warning(f"No regime configuration found for {regime.value}")
                return False

            # Apply regime multipliers to global config
            if self.global_config:
                self.global_config.max_portfolio_risk *= regime_config.get('risk_multiplier', 1.0)
                self.global_config.max_position_size *= regime_config.get('position_size_multiplier', 1.0)

            # Apply regime multipliers to strategy configs
            for strategy_config in self.strategy_configs.values():
                strategy_config.max_portfolio_risk *= regime_config.get('risk_multiplier', 1.0)
                strategy_config.max_position_size *= regime_config.get('position_size_multiplier', 1.0)
                strategy_config.target_risk_reward *= regime_config.get('take_profit_multiplier', 1.0)

            logger.info(f"Applied market regime adjustments for {regime.value}")
            return True

        except Exception as e:
            logger.error(f"Error applying market regime {regime.value}: {str(e)}")
            return False

    def apply_risk_profile(self, profile: RiskProfile) -> bool:
        """
        Apply risk profile template

        Args:
            profile: Risk profile to apply

        Returns:
            True if successful, False otherwise
        """
        try:
            self.current_profile = profile

            profile_config = self.config_data.get('risk_profiles', {}).get(profile.value, {})

            if not profile_config:
                logger.warning(f"No profile configuration found for {profile.value}")
                return False

            # Update global config with profile settings
            if self.global_config:
                for key, value in profile_config.items():
                    if hasattr(self.global_config, key):
                        setattr(self.global_config, key, value)

            logger.info(f"Applied risk profile: {profile.value}")
            return True

        except Exception as e:
            logger.error(f"Error applying risk profile {profile.value}: {str(e)}")
            return False

    def get_emergency_controls(self) -> Dict[str, Any]:
        """Get emergency control settings"""
        return self.config_data.get('emergency_controls', {
            'daily_loss_limit': 0.05,
            'flash_crash_protection': 0.10,
            'correlation_breakdown': 0.95
        })

    def validate_configuration(self) -> Dict[str, List[str]]:
        """
        Validate configuration parameters

        Returns:
            Dict with validation results {'errors': [], 'warnings': []}
        """
        errors = []
        warnings = []

        try:
            # Validate global config
            if self.global_config:
                if self.global_config.max_portfolio_risk <= 0 or self.global_config.max_portfolio_risk > 0.5:
                    errors.append("Invalid max_portfolio_risk: must be between 0 and 0.5")

                if self.global_config.max_position_size <= 0 or self.global_config.max_position_size > 1.0:
                    errors.append("Invalid max_position_size: must be between 0 and 1.0")

                if self.global_config.max_drawdown <= 0 or self.global_config.max_drawdown > 1.0:
                    errors.append("Invalid max_drawdown: must be between 0 and 1.0")

            # Validate strategy configs
            for strategy_name, config in self.strategy_configs.items():
                if config.max_portfolio_risk <= 0:
                    errors.append(f"Invalid max_portfolio_risk for {strategy_name}")

                if config.target_risk_reward <= 0:
                    errors.append(f"Invalid target_risk_reward for {strategy_name}")

                if config.max_position_size > 0.5:
                    warnings.append(f"Large max_position_size for {strategy_name}: {config.max_position_size}")

            # Validate method configurations
            position_sizing = self.config_data.get('position_sizing', {})
            if 'default_method' not in position_sizing:
                warnings.append("No default position sizing method specified")

            stop_loss = self.config_data.get('stop_loss', {})
            if 'default_method' not in stop_loss:
                warnings.append("No default stop-loss method specified")

        except Exception as e:
            errors.append(f"Configuration validation error: {str(e)}")

        return {'errors': errors, 'warnings': warnings}

    def update_strategy_config(self, strategy_name: str, updates: Dict[str, Any]) -> bool:
        """
        Update strategy configuration dynamically

        Args:
            strategy_name: Name of the strategy to update
            updates: Dictionary of parameter updates

        Returns:
            True if successful, False otherwise
        """
        try:
            if strategy_name not in self.strategy_configs:
                # Create new strategy config
                self.strategy_configs[strategy_name] = StrategyRiskConfig(strategy_name=strategy_name)

            strategy_config = self.strategy_configs[strategy_name]

            # Update parameters
            for key, value in updates.items():
                if hasattr(strategy_config, key):
                    setattr(strategy_config, key, value)
                else:
                    strategy_config.custom_params[key] = value

            logger.info(f"Updated strategy config for {strategy_name}")
            return True

        except Exception as e:
            logger.error(f"Error updating strategy config for {strategy_name}: {str(e)}")
            return False

    def save_configuration(self, output_path: Optional[str] = None) -> bool:
        """
        Save current configuration to YAML file

        Args:
            output_path: Optional output path, defaults to current config path

        Returns:
            True if successful, False otherwise
        """
        try:
            output_path = output_path or self.config_path

            # Rebuild config data from current objects
            updated_config = self.config_data.copy()

            # Update global config
            if self.global_config:
                updated_config['global_risk'] = self.global_config.to_dict()

            # Update strategy configs
            strategies_dict = {}
            for strategy_name, config in self.strategy_configs.items():
                strategies_dict[strategy_name] = config.to_dict()
            updated_config['strategies'] = strategies_dict

            # Save to file
            with open(output_path, 'w') as f:
                yaml.dump(updated_config, f, default_flow_style=False, indent=2)

            logger.info(f"Configuration saved to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
            return False

    def get_current_settings_summary(self) -> Dict[str, Any]:
        """Get summary of current settings"""
        return {
            'config_path': self.config_path,
            'current_regime': self.current_regime.value,
            'current_profile': self.current_profile.value,
            'global_config': self.global_config.to_dict() if self.global_config else {},
            'strategy_count': len(self.strategy_configs),
            'strategies': list(self.strategy_configs.keys())
        }

    def reset_to_defaults(self) -> bool:
        """Reset configuration to default values"""
        try:
            # Reset market regime and profile
            self.current_regime = MarketRegime.NORMAL
            self.current_profile = RiskProfile.MODERATE

            # Reload original configuration
            self.load_configuration()

            logger.info("Configuration reset to defaults")
            return True

        except Exception as e:
            logger.error(f"Error resetting configuration: {str(e)}")
            return False
