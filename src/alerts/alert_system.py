#!/usr/bin/env python3
"""
Agent Investment Platform - Intelligent Alert System

This module implements an intelligent alert system for market conditions,
portfolio risks, and system issues with configurable thresholds and
smart filtering to reduce noise and false alarms.

Key Features:
- Market condition monitoring with dynamic thresholds
- Portfolio risk assessment and breach detection
- System health monitoring and failure alerts
- Intelligent alert grouping and deduplication
- Machine learning-based anomaly detection
- Configurable alert rules and escalation policies
- Historical alert tracking and analysis
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from pathlib import Path
from dataclasses import dataclass, field, asdict
from enum import Enum
import hashlib
import statistics
from collections import defaultdict, deque
import yaml


class AlertType(Enum):
    """Types of alerts in the system."""
    MARKET_MOVEMENT = "market_movement"
    PORTFOLIO_RISK = "portfolio_risk"
    TECHNICAL_INDICATOR = "technical_indicator"
    SYSTEM_HEALTH = "system_health"
    DATA_QUALITY = "data_quality"
    PERFORMANCE = "performance"
    SECURITY = "security"
    NEWS_SENTIMENT = "news_sentiment"


class AlertSeverity(Enum):
    """Alert severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertStatus(Enum):
    """Alert processing status."""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
    EXPIRED = "expired"


@dataclass
class AlertRule:
    """Definition of an alert rule."""
    id: str
    name: str
    alert_type: AlertType
    condition: str  # Condition expression
    threshold: Union[float, int, str]
    severity: AlertSeverity
    enabled: bool = True
    cooldown_minutes: int = 60
    escalation_minutes: Optional[int] = None
    auto_resolve: bool = False
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Alert:
    """Represents an active alert."""
    id: str
    rule_id: str
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    timestamp: datetime
    status: AlertStatus = AlertStatus.ACTIVE
    context: Dict[str, Any] = field(default_factory=dict)
    affected_entity: Optional[str] = None  # Symbol, component, etc.
    threshold_value: Optional[Union[float, int]] = None
    actual_value: Optional[Union[float, int]] = None
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    escalated: bool = False
    suppression_count: int = 0

    def to_dict(self):
        """Convert to dictionary for serialization."""
        result = asdict(self)
        result['alert_type'] = self.alert_type.value
        result['severity'] = self.severity.value
        result['status'] = self.status.value
        result['timestamp'] = self.timestamp.isoformat()
        if self.resolved_at:
            result['resolved_at'] = self.resolved_at.isoformat()
        if self.acknowledged_at:
            result['acknowledged_at'] = self.acknowledged_at.isoformat()
        return result


class AlertConditionEvaluator:
    """Evaluates alert conditions against incoming data."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_cache = {}
        self.historical_data = defaultdict(lambda: deque(maxlen=1000))

    def evaluate_condition(
        self,
        rule: AlertRule,
        data: Dict[str, Any],
        symbol: Optional[str] = None
    ) -> bool:
        """
        Evaluate if an alert condition is met.

        Args:
            rule: Alert rule to evaluate
            data: Current data to check against
            symbol: Optional symbol context

        Returns:
            True if condition is met, False otherwise
        """
        try:
            # Store data for historical analysis
            if symbol:
                self.historical_data[symbol].append({
                    'timestamp': datetime.utcnow(),
                    'data': data.copy()
                })

            # Evaluate based on alert type
            if rule.alert_type == AlertType.MARKET_MOVEMENT:
                return self._evaluate_market_movement(rule, data, symbol)
            elif rule.alert_type == AlertType.PORTFOLIO_RISK:
                return self._evaluate_portfolio_risk(rule, data)
            elif rule.alert_type == AlertType.TECHNICAL_INDICATOR:
                return self._evaluate_technical_indicator(rule, data, symbol)
            elif rule.alert_type == AlertType.SYSTEM_HEALTH:
                return self._evaluate_system_health(rule, data)
            elif rule.alert_type == AlertType.DATA_QUALITY:
                return self._evaluate_data_quality(rule, data)
            elif rule.alert_type == AlertType.PERFORMANCE:
                return self._evaluate_performance(rule, data)
            elif rule.alert_type == AlertType.NEWS_SENTIMENT:
                return self._evaluate_news_sentiment(rule, data, symbol)
            else:
                self.logger.warning(f"Unknown alert type: {rule.alert_type}")
                return False

        except Exception as e:
            self.logger.error(f"Error evaluating condition for rule {rule.id}: {e}")
            return False

    def _evaluate_market_movement(self, rule: AlertRule, data: Dict[str, Any], symbol: Optional[str]) -> bool:
        """Evaluate market movement conditions."""
        condition = rule.condition.lower()
        threshold = float(rule.threshold)

        if condition == "price_change_percent":
            current_price = data.get('current_price', 0)
            previous_price = data.get('previous_price', current_price)

            if previous_price == 0:
                return False

            change_percent = abs((current_price - previous_price) / previous_price * 100)
            return change_percent >= threshold

        elif condition == "volume_spike":
            current_volume = data.get('volume', 0)
            avg_volume = self._get_average_volume(symbol) if symbol else 0

            if avg_volume == 0:
                return False

            volume_ratio = current_volume / avg_volume
            return volume_ratio >= threshold

        elif condition == "volatility_spike":
            volatility = data.get('volatility', 0)
            return volatility >= threshold

        return False

    def _evaluate_portfolio_risk(self, rule: AlertRule, data: Dict[str, Any]) -> bool:
        """Evaluate portfolio risk conditions."""
        condition = rule.condition.lower()
        threshold = float(rule.threshold)

        if condition == "portfolio_drawdown":
            drawdown = data.get('max_drawdown', 0)
            return abs(drawdown) >= threshold

        elif condition == "position_concentration":
            max_position = data.get('max_position_size', 0)
            return max_position >= threshold

        elif condition == "var_breach":
            var_estimate = data.get('value_at_risk', 0)
            portfolio_value = data.get('portfolio_value', 1)
            var_percent = abs(var_estimate) / portfolio_value * 100 if portfolio_value > 0 else 0
            return var_percent >= threshold

        elif condition == "beta_drift":
            current_beta = data.get('portfolio_beta', 1.0)
            target_beta = data.get('target_beta', 1.0)
            beta_drift = abs(current_beta - target_beta)
            return beta_drift >= threshold

        return False

    def _evaluate_technical_indicator(self, rule: AlertRule, data: Dict[str, Any], symbol: Optional[str]) -> bool:
        """Evaluate technical indicator conditions."""
        condition = rule.condition.lower()
        threshold = float(rule.threshold) if isinstance(rule.threshold, (int, float)) else rule.threshold

        if condition == "rsi_overbought":
            rsi = data.get('rsi', 50)
            return rsi >= float(threshold)

        elif condition == "rsi_oversold":
            rsi = data.get('rsi', 50)
            return rsi <= float(threshold)

        elif condition == "macd_signal":
            macd = data.get('macd', 0)
            macd_signal = data.get('macd_signal', 0)
            if threshold == "bullish_crossover":
                return macd > macd_signal and (symbol is not None and self._was_below_signal(symbol, 'macd'))
            elif threshold == "bearish_crossover":
                return macd < macd_signal and (symbol is not None and self._was_above_signal(symbol, 'macd'))

        elif condition == "bollinger_squeeze":
            bb_upper = data.get('bollinger_upper', 0)
            bb_lower = data.get('bollinger_lower', 0)
            bb_width = bb_upper - bb_lower if bb_upper > bb_lower else 0
            avg_width = self._get_average_bollinger_width(symbol) if symbol else 0

            if avg_width > 0:
                width_ratio = bb_width / avg_width
                return width_ratio <= float(threshold)  # Squeeze when width is narrow

        elif condition == "moving_average_cross":
            ma_short = data.get('ma_short', 0)
            ma_long = data.get('ma_long', 0)
            if threshold == "golden_cross":
                return ma_short > ma_long and (symbol is not None and self._was_ma_below(symbol))
            elif threshold == "death_cross":
                return ma_short < ma_long and (symbol is not None and self._was_ma_above(symbol))

        return False

    def _evaluate_system_health(self, rule: AlertRule, data: Dict[str, Any]) -> bool:
        """Evaluate system health conditions."""
        condition = rule.condition.lower()
        threshold = float(rule.threshold)

        if condition == "cpu_usage":
            cpu_usage = data.get('cpu_usage', 0)
            return cpu_usage >= threshold

        elif condition == "memory_usage":
            memory_usage = data.get('memory_usage', 0)
            return memory_usage >= threshold

        elif condition == "disk_usage":
            disk_usage = data.get('disk_usage', 0)
            return disk_usage >= threshold

        elif condition == "response_time":
            response_time = data.get('response_time_ms', 0)
            return response_time >= threshold

        elif condition == "error_rate":
            errors = data.get('errors', 0)
            total_requests = data.get('total_requests', 1)
            error_rate = (errors / total_requests) * 100 if total_requests > 0 else 0
            return error_rate >= threshold

        elif condition == "component_failure":
            failed_components = data.get('failed_components', [])
            return len(failed_components) > 0

        return False

    def _evaluate_data_quality(self, rule: AlertRule, data: Dict[str, Any]) -> bool:
        """Evaluate data quality conditions."""
        condition = rule.condition.lower()
        threshold = float(rule.threshold) if isinstance(rule.threshold, (int, float)) else rule.threshold

        if condition == "missing_data_percent":
            missing_count = data.get('missing_data_points', 0)
            total_count = data.get('total_data_points', 1)
            missing_percent = (missing_count / total_count) * 100 if total_count > 0 else 0
            return missing_percent >= float(threshold)

        elif condition == "stale_data":
            last_update = data.get('last_update')
            if last_update:
                if isinstance(last_update, str):
                    last_update = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
                staleness_minutes = (datetime.utcnow() - last_update).total_seconds() / 60
                return staleness_minutes >= float(threshold)

        elif condition == "data_anomaly":
            anomaly_score = data.get('anomaly_score', 0)
            return anomaly_score >= float(threshold)

        return False

    def _evaluate_performance(self, rule: AlertRule, data: Dict[str, Any]) -> bool:
        """Evaluate performance conditions."""
        condition = rule.condition.lower()
        threshold = float(rule.threshold)

        if condition == "analysis_failure_rate":
            failed_analyses = data.get('failed_analyses', 0)
            total_analyses = data.get('total_analyses', 1)
            failure_rate = (failed_analyses / total_analyses) * 100 if total_analyses > 0 else 0
            return failure_rate >= threshold

        elif condition == "queue_size":
            queue_size = data.get('queue_size', 0)
            return queue_size >= threshold

        elif condition == "processing_latency":
            avg_latency = data.get('average_processing_time', 0)
            return avg_latency >= threshold

        return False

    def _evaluate_news_sentiment(self, rule: AlertRule, data: Dict[str, Any], symbol: Optional[str]) -> bool:
        """Evaluate news sentiment conditions."""
        condition = rule.condition.lower()
        threshold = float(rule.threshold) if isinstance(rule.threshold, (int, float)) else rule.threshold

        if condition == "sentiment_extreme":
            sentiment_score = data.get('sentiment_score', 0)
            return abs(sentiment_score) >= float(threshold)

        elif condition == "sentiment_shift":
            current_sentiment = data.get('sentiment_score', 0)
            previous_sentiment = self._get_previous_sentiment(symbol) if symbol else 0
            sentiment_change = abs(current_sentiment - previous_sentiment)
            return sentiment_change >= float(threshold)

        elif condition == "negative_news_volume":
            negative_count = data.get('negative_news_count', 0)
            return negative_count >= float(threshold)

        return False

    # Helper methods for historical data analysis
    def _get_average_volume(self, symbol: str) -> float:
        """Get average volume for a symbol."""
        if symbol not in self.historical_data:
            return 0

        history_entries = list(self.historical_data[symbol])[-20:]
        volumes = [entry['data'].get('volume', 0) for entry in history_entries]
        return statistics.mean(volumes) if volumes else 0

    def _was_below_signal(self, symbol: str, indicator: str) -> bool:
        """Check if indicator was below signal in previous period."""
        if not symbol or symbol not in self.historical_data:
            return False

        history = list(self.historical_data[symbol])
        if len(history) < 2:
            return False

        prev_data = history[-2]['data']
        prev_macd = prev_data.get('macd', 0)
        prev_signal = prev_data.get('macd_signal', 0)

        return prev_macd <= prev_signal

    def _was_above_signal(self, symbol: str, indicator: str) -> bool:
        """Check if indicator was above signal in previous period."""
        if not symbol or symbol not in self.historical_data:
            return False

        history = list(self.historical_data[symbol])
        if len(history) < 2:
            return False

        prev_data = history[-2]['data']
        prev_macd = prev_data.get('macd', 0)
        prev_signal = prev_data.get('macd_signal', 0)

        return prev_macd >= prev_signal

    def _get_average_bollinger_width(self, symbol: str) -> float:
        """Get average Bollinger Band width."""
        if not symbol or symbol not in self.historical_data:
            return 0

        widths = []
        history_entries = list(self.historical_data[symbol])[-20:]
        for entry in history_entries:
            data = entry['data']
            upper = data.get('bollinger_upper', 0)
            lower = data.get('bollinger_lower', 0)
            if upper > lower:
                widths.append(upper - lower)

        return statistics.mean(widths) if widths else 0

    def _was_ma_below(self, symbol: str) -> bool:
        """Check if short MA was below long MA in previous period."""
        if not symbol or symbol not in self.historical_data:
            return False

        history = list(self.historical_data[symbol])
        if len(history) < 2:
            return False

        prev_data = history[-2]['data']
        prev_short = prev_data.get('ma_short', 0)
        prev_long = prev_data.get('ma_long', 0)

        return prev_short <= prev_long

    def _was_ma_above(self, symbol: str) -> bool:
        """Check if short MA was above long MA in previous period."""
        if not symbol or symbol not in self.historical_data:
            return False

        history = list(self.historical_data[symbol])
        if len(history) < 2:
            return False

        prev_data = history[-2]['data']
        prev_short = prev_data.get('ma_short', 0)
        prev_long = prev_data.get('ma_long', 0)

        return prev_short >= prev_long

    def _get_previous_sentiment(self, symbol: str) -> float:
        """Get previous sentiment score for symbol."""
        if not symbol or symbol not in self.historical_data:
            return 0

        history = list(self.historical_data[symbol])
        if len(history) < 2:
            return 0

        return history[-2]['data'].get('sentiment_score', 0)


class AlertDeduplicator:
    """Handles alert deduplication and grouping."""

    def __init__(self):
        self.recent_alerts = deque(maxlen=1000)
        self.suppression_cache = {}
        self.logger = logging.getLogger(__name__)

    def should_suppress_alert(self, alert: Alert, cooldown_minutes: int = 60) -> bool:
        """Check if an alert should be suppressed due to recent similar alerts."""
        alert_key = self._generate_alert_key(alert)
        current_time = datetime.utcnow()

        # Check suppression cache
        if alert_key in self.suppression_cache:
            last_alert_time = self.suppression_cache[alert_key]
            time_diff = (current_time - last_alert_time).total_seconds() / 60

            if time_diff < cooldown_minutes:
                self.logger.debug(f"Alert suppressed due to cooldown: {alert.title}")
                return True

        # Update suppression cache
        self.suppression_cache[alert_key] = current_time

        # Clean old entries from cache
        cutoff_time = current_time - timedelta(hours=24)
        self.suppression_cache = {
            k: v for k, v in self.suppression_cache.items()
            if v > cutoff_time
        }

        return False

    def _generate_alert_key(self, alert: Alert) -> str:
        """Generate a unique key for alert deduplication."""
        # Create hash based on rule, entity, and alert type
        key_components = [
            alert.rule_id,
            alert.affected_entity or "global",
            alert.alert_type.value
        ]

        key_string = "|".join(key_components)
        return hashlib.md5(key_string.encode()).hexdigest()


class IntelligentAlertSystem:
    """Main intelligent alert system."""

    def __init__(self, config_file: str = "config/alert-config.yaml"):
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config(config_file)

        # Core components
        self.condition_evaluator = AlertConditionEvaluator()
        self.deduplicator = AlertDeduplicator()

        # Alert storage and management
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []

        # External system references
        self.notification_system = None
        self.monitoring_dashboard = None

        # Load alert rules
        self._load_alert_rules()

        # Statistics
        self.stats = {
            'alerts_generated': 0,
            'alerts_suppressed': 0,
            'alerts_resolved': 0,
            'alerts_escalated': 0
        }

    def set_external_systems(self, notification_system=None, monitoring_dashboard=None):
        """Set references to external systems."""
        self.notification_system = notification_system
        self.monitoring_dashboard = monitoring_dashboard

    async def process_data(self, data: Dict[str, Any], symbol: Optional[str] = None):
        """Process incoming data and evaluate alert conditions."""
        try:
            triggered_rules = []

            # Evaluate all enabled alert rules
            for rule in self.alert_rules.values():
                if not rule.enabled:
                    continue

                try:
                    if self.condition_evaluator.evaluate_condition(rule, data, symbol):
                        triggered_rules.append(rule)
                        self.logger.debug(f"Alert rule triggered: {rule.name}")

                except Exception as e:
                    self.logger.error(f"Error evaluating rule {rule.id}: {e}")

            # Generate alerts for triggered rules
            for rule in triggered_rules:
                await self._generate_alert(rule, data, symbol)

        except Exception as e:
            self.logger.error(f"Error processing alert data: {e}")

    async def _generate_alert(self, rule: AlertRule, data: Dict[str, Any], symbol: Optional[str]):
        """Generate an alert from a triggered rule."""
        try:
            # Create alert
            alert_id = self._generate_alert_id(rule, symbol)

            alert = Alert(
                id=alert_id,
                rule_id=rule.id,
                alert_type=rule.alert_type,
                severity=rule.severity,
                title=self._generate_alert_title(rule, data, symbol),
                message=self._generate_alert_message(rule, data, symbol),
                timestamp=datetime.utcnow(),
                context=data.copy(),
                affected_entity=symbol,
                threshold_value=rule.threshold if isinstance(rule.threshold, (int, float)) else None,
                actual_value=self._extract_actual_value(rule, data)
            )

            # Check for suppression
            if self.deduplicator.should_suppress_alert(alert, rule.cooldown_minutes):
                alert.status = AlertStatus.SUPPRESSED
                alert.suppression_count += 1
                self.stats['alerts_suppressed'] += 1
                self.logger.debug(f"Alert suppressed: {alert.title}")
                return

            # Store active alert
            self.active_alerts[alert_id] = alert
            self.alert_history.append(alert)
            self.stats['alerts_generated'] += 1

            # Send notification
            if self.notification_system:
                await self._send_alert_notification(alert)

            # Schedule auto-resolution if configured
            if rule.auto_resolve:
                asyncio.create_task(self._schedule_auto_resolution(alert, rule))

            # Schedule escalation if configured
            if rule.escalation_minutes:
                asyncio.create_task(self._schedule_escalation(alert, rule))

            self.logger.info(f"Alert generated: {alert.title}")

        except Exception as e:
            self.logger.error(f"Error generating alert: {e}")

    async def _send_alert_notification(self, alert: Alert):
        """Send alert notification."""
        try:
            if not self.notification_system:
                return

            # Map alert severity to notification severity
            from src.notifications.notification_system import NotificationSeverity

            severity_map = {
                AlertSeverity.CRITICAL: NotificationSeverity.CRITICAL,
                AlertSeverity.HIGH: NotificationSeverity.HIGH,
                AlertSeverity.MEDIUM: NotificationSeverity.MEDIUM,
                AlertSeverity.LOW: NotificationSeverity.LOW,
                AlertSeverity.INFO: NotificationSeverity.INFO
            }

            await self.notification_system.send_notification(
                title=alert.title,
                content=alert.message,
                severity=severity_map.get(alert.severity, NotificationSeverity.MEDIUM),
                tags=['alert', alert.alert_type.value, alert.severity.value],
                template='alert_notification',
                template_data={
                    'alert_id': alert.id,
                    'alert_type': alert.alert_type.value,
                    'severity': alert.severity.value,
                    'affected_entity': alert.affected_entity or 'System',
                    'threshold': alert.threshold_value,
                    'actual_value': alert.actual_value,
                    'timestamp': alert.timestamp.isoformat()
                }
            )

        except Exception as e:
            self.logger.error(f"Failed to send alert notification: {e}")

    def _generate_alert_id(self, rule: AlertRule, symbol: Optional[str]) -> str:
        """Generate unique alert ID."""
        components = [rule.id, symbol or "global", str(int(datetime.utcnow().timestamp()))]
        return hashlib.md5("|".join(components).encode()).hexdigest()[:16]

    def _generate_alert_title(self, rule: AlertRule, data: Dict[str, Any], symbol: Optional[str]) -> str:
        """Generate alert title."""
        entity = symbol or "System"
        return f"{rule.name} - {entity}"

    def _generate_alert_message(self, rule: AlertRule, data: Dict[str, Any], symbol: Optional[str]) -> str:
        """Generate detailed alert message."""
        entity = symbol or "System"
        actual_value = self._extract_actual_value(rule, data)

        message = f"Alert: {rule.name}\n"
        message += f"Entity: {entity}\n"
        message += f"Condition: {rule.condition}\n"
        message += f"Threshold: {rule.threshold}\n"

        if actual_value is not None:
            message += f"Actual Value: {actual_value}\n"

        message += f"Severity: {rule.severity.value.upper()}\n"
        message += f"Timestamp: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"

        if rule.description:
            message += f"\nDescription: {rule.description}"

        return message

    def _extract_actual_value(self, rule: AlertRule, data: Dict[str, Any]) -> Optional[Union[float, int]]:
        """Extract the actual value that triggered the alert."""
        condition = rule.condition.lower()

        # Map conditions to data fields
        field_map = {
            'price_change_percent': 'price_change_percent',
            'volume_spike': 'volume',
            'volatility_spike': 'volatility',
            'portfolio_drawdown': 'max_drawdown',
            'position_concentration': 'max_position_size',
            'rsi_overbought': 'rsi',
            'rsi_oversold': 'rsi',
            'cpu_usage': 'cpu_usage',
            'memory_usage': 'memory_usage',
            'disk_usage': 'disk_usage',
            'response_time': 'response_time_ms',
            'error_rate': 'error_rate',
            'queue_size': 'queue_size'
        }

        field = field_map.get(condition)
        if field and field in data:
            return data[field]

        return None

    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str = "system") -> bool:
        """Acknowledge an active alert."""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_at = datetime.utcnow()
            alert.acknowledged_by = acknowledged_by

            self.logger.info(f"Alert acknowledged: {alert.title} by {acknowledged_by}")
            return True

        return False

    async def resolve_alert(self, alert_id: str, resolved_by: str = "system") -> bool:
        """Resolve an active alert."""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.utcnow()

            # Remove from active alerts
            del self.active_alerts[alert_id]
            self.stats['alerts_resolved'] += 1

            self.logger.info(f"Alert resolved: {alert.title}")
            return True

        return False

    async def _schedule_auto_resolution(self, alert: Alert, rule: AlertRule):
        """Schedule automatic alert resolution."""
        # Wait for auto-resolution timeout (default 1 hour)
        timeout_minutes = rule.metadata.get('auto_resolve_minutes', 60)
        await asyncio.sleep(timeout_minutes * 60)

        # Check if alert is still active
        if alert.id in self.active_alerts and alert.status == AlertStatus.ACTIVE:
            await self.resolve_alert(alert.id, "auto-resolution")

    async def _schedule_escalation(self, alert: Alert, rule: AlertRule):
        """Schedule alert escalation."""
        if rule.escalation_minutes is None:
            return
        await asyncio.sleep(rule.escalation_minutes * 60)

        # Check if alert still needs escalation
        if (alert.id in self.active_alerts and
            alert.status == AlertStatus.ACTIVE and
            not alert.escalated):

            alert.escalated = True
            alert.severity = AlertSeverity.CRITICAL  # Escalate to critical
            self.stats['alerts_escalated'] += 1

            # Send escalation notification
            if self.notification_system:
                await self.notification_system.send_notification(
                    title=f"ESCALATED: {alert.title}",
                    content=f"Alert has been escalated due to no resolution.\n\n{alert.message}",
                    severity=self.notification_system.NotificationSeverity.CRITICAL,
                    tags=['alert', 'escalated', alert.alert_type.value]
                )

            self.logger.warning(f"Alert escalated: {alert.title}")

    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load alert system configuration."""
        try:
            config_path = Path(config_file)
            if config_path.exists():
                with open(config_path, 'r') as f:
                    return yaml.safe_load(f)
            else:
                self.logger.warning(f"Alert config file not found: {config_file}")
                return {}
        except Exception as e:
            self.logger.error(f"Failed to load alert config: {e}")
            return {}

    def _load_alert_rules(self):
        """Load alert rules from configuration."""
        rules_config = self.config.get('alert_rules', [])

        for rule_config in rules_config:
            try:
                rule = AlertRule(
                    id=rule_config['id'],
                    name=rule_config['name'],
                    alert_type=AlertType(rule_config['alert_type']),
                    condition=rule_config['condition'],
                    threshold=rule_config['threshold'],
                    severity=AlertSeverity(rule_config['severity']),
                    enabled=rule_config.get('enabled', True),
                    cooldown_minutes=rule_config.get('cooldown_minutes', 60),
                    escalation_minutes=rule_config.get('escalation_minutes'),
                    auto_resolve=rule_config.get('auto_resolve', False),
                    description=rule_config.get('description', ''),
                    metadata=rule_config.get('metadata', {})
                )

                self.alert_rules[rule.id] = rule
                self.logger.info(f"Loaded alert rule: {rule.name}")

            except Exception as e:
                self.logger.error(f"Failed to load alert rule: {e}")

        self.logger.info(f"Loaded {len(self.alert_rules)} alert rules")

    def get_statistics(self) -> Dict[str, Any]:
        """Get alert system statistics."""
        return {
            'total_rules': len(self.alert_rules),
            'active_alerts': len(self.active_alerts),
            'alerts_generated': self.stats['alerts_generated'],
            'alerts_suppressed': self.stats['alerts_suppressed'],
            'alerts_resolved': self.stats['alerts_resolved'],
            'alerts_escalated': self.stats['alerts_escalated'],
            'alert_history_size': len(self.alert_history)
        }

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get list of active alerts."""
        return [alert.to_dict() for alert in self.active_alerts.values()]

    def get_alert_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get alert history for specified time period."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        recent_alerts = [
            alert.to_dict() for alert in self.alert_history
            if alert.timestamp > cutoff_time
        ]

        return recent_alerts


# Helper functions for easy integration
async def create_market_alert_rule(
    alert_system: IntelligentAlertSystem,
    symbol: str,
    condition: str,
    threshold: float,
    severity: AlertSeverity = AlertSeverity.MEDIUM
) -> str:
    """Create a market-specific alert rule."""
    rule_id = f"market_{symbol}_{condition}_{int(datetime.utcnow().timestamp())}"

    rule = AlertRule(
        id=rule_id,
        name=f"Market Alert - {symbol} {condition}",
        alert_type=AlertType.MARKET_MOVEMENT,
        condition=condition,
        threshold=threshold,
        severity=severity,
        description=f"Alert for {symbol} when {condition} exceeds {threshold}"
    )

    alert_system.alert_rules[rule_id] = rule
    return rule_id


async def create_system_alert_rule(
    alert_system: IntelligentAlertSystem,
    component: str,
    condition: str,
    threshold: Union[float, str],
    severity: AlertSeverity = AlertSeverity.HIGH
) -> str:
    """Create a system health alert rule."""
    rule_id = f"system_{component}_{condition}_{int(datetime.utcnow().timestamp())}"

    rule = AlertRule(
        id=rule_id,
        name=f"System Alert - {component} {condition}",
        alert_type=AlertType.SYSTEM_HEALTH,
        condition=condition,
        threshold=threshold,
        severity=severity,
        description=f"Alert for {component} when {condition} condition is met"
    )

    alert_system.alert_rules[rule_id] = rule
    return rule_id


if __name__ == "__main__":
    """Test the alert system."""
    import asyncio

    async def test_alerts():
        """Test alert generation and processing."""
        # Initialize alert system
        alert_system = IntelligentAlertSystem()

        # Create test rules
        await create_market_alert_rule(
            alert_system,
            "AAPL",
            "price_change_percent",
            5.0,
            AlertSeverity.HIGH
        )

        await create_system_alert_rule(
            alert_system,
            "orchestrator",
            "cpu_usage",
            80.0,
            AlertSeverity.MEDIUM
        )

        # Test data that should trigger alerts
        test_market_data = {
            'symbol': 'AAPL',
            'current_price': 150.0,
            'previous_price': 140.0,  # 7.14% increase
            'volume': 50000000
        }

        test_system_data = {
            'cpu_usage': 85.0,  # Above 80% threshold
            'memory_usage': 65.0,
            'response_time_ms': 200
        }

        # Process test data
        await alert_system.process_data(test_market_data, "AAPL")
        await alert_system.process_data(test_system_data)

        # Print results
        stats = alert_system.get_statistics()
        active_alerts = alert_system.get_active_alerts()

        print(f"Alert System Statistics: {json.dumps(stats, indent=2)}")
        print(f"Active Alerts: {json.dumps(active_alerts, indent=2)}")

    # Run test
    asyncio.run(test_alerts())
