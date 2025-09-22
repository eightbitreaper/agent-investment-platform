#!/usr/bin/env python3
"""
Agent Investment Platform - System Orchestrator

This module coordinates all platform components to provide unified
investment analysis and reporting capabilities. The orchestrator manages
MCP servers, analysis engines, report generation, and notifications.

Key Features:
- Unified system coordination and lifecycle management
- Automated analysis workflows and report generation
- Real-time market data processing and alert systems
- Comprehensive error handling and recovery mechanisms
- Health monitoring and performance metrics
- Configuration-driven operation modes
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
import json
import yaml
import argparse
from dataclasses import dataclass
from enum import Enum

# Import platform components
try:
    from scheduler import JobScheduler, JobPriority
    from src.mcp_servers.manager import MCPServerManager
    from src.analysis.recommendation_engine import RecommendationEngine
    from src.analysis.sentiment_analyzer import FinancialSentimentAnalyzer
    from src.analysis.chart_analyzer import TechnicalAnalysis
    from src.risk_management.risk_engine import RiskEngine
    from src.reports.markdown_generator import MarkdownReportGenerator
    from src.reports.report_validator import ReportValidator
    from src.reports.report_history import ReportHistoryTracker
    from src.github.report_uploader import GitHubReportUploader
    from src.integration.framework import IntegrationFramework, ComponentType
    from src.notifications.notification_system import NotificationSystem
    from src.alerts.alert_system import IntelligentAlertSystem
    from src.monitoring.dashboard import MonitoringDashboard
    COMPONENTS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Some platform components not available: {e}")
    COMPONENTS_AVAILABLE = False


class OperationMode(Enum):
    """System operation modes."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"
    DEMO = "demo"


class SystemState(Enum):
    """System operational states."""
    INITIALIZING = "initializing"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class SystemConfig:
    """System configuration parameters."""
    mode: OperationMode = OperationMode.DEVELOPMENT
    enable_scheduling: bool = True
    enable_notifications: bool = True
    enable_live_data: bool = False
    report_frequency: str = "daily"  # daily, hourly, on-demand
    max_concurrent_analysis: int = 3
    data_retention_days: int = 90
    log_level: str = "INFO"
    auto_recovery: bool = True
    health_check_interval: int = 300  # seconds


class PlatformOrchestrator:
    """
    Main orchestrator for the Agent Investment Platform.

    Coordinates all system components to provide seamless investment
    analysis and reporting capabilities with comprehensive monitoring
    and error recovery.
    """

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the platform orchestrator.

        Args:
            config_file: Path to configuration file
        """
        self.logger = logging.getLogger(__name__)
        self.config = SystemConfig()
        self.state = SystemState.INITIALIZING
        self.config_file = config_file

        # Integration framework for component management
        self.integration_framework = IntegrationFramework()

        # Component managers (accessed through integration framework)
        self.scheduler: Optional[JobScheduler] = None
        self.mcp_manager: Optional[MCPServerManager] = None
        self.recommendation_engine: Optional[RecommendationEngine] = None
        self.sentiment_analyzer: Optional[FinancialSentimentAnalyzer] = None
        self.chart_analyzer: Optional[TechnicalAnalysis] = None
        self.risk_engine: Optional[RiskEngine] = None
        self.report_generator: Optional[MarkdownReportGenerator] = None
        self.report_validator: Optional[ReportValidator] = None
        self.report_history: Optional[ReportHistoryTracker] = None
        self.github_uploader: Optional[GitHubReportUploader] = None
        self.notification_system: Optional[NotificationSystem] = None
        self.alert_system: Optional[IntelligentAlertSystem] = None
        self.monitoring_dashboard: Optional[MonitoringDashboard] = None        # System state
        self.start_time: Optional[datetime] = None
        self.shutdown_requested = False
        self.health_check_task: Optional[asyncio.Task] = None

        # Statistics and monitoring
        self.stats = {
            'reports_generated': 0,
            'analyses_completed': 0,
            'errors_encountered': 0,
            'uptime_seconds': 0,
            'last_successful_analysis': None,
            'component_status': {}
        }

        # Load configuration
        self._load_configuration()

        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()

        self.logger.info(f"Platform Orchestrator initialized in {self.config.mode.value} mode")

    async def initialize(self) -> bool:
        """
        Initialize all platform components.

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self.logger.info("Initializing platform components...")

            if not COMPONENTS_AVAILABLE:
                self.logger.error("Platform components not available")
                return False

            # Initialize core components
            await self._initialize_components()

            # Setup automated workflows
            if self.config.enable_scheduling:
                await self._setup_scheduled_jobs()

            # Start health monitoring
            self.health_check_task = asyncio.create_task(self._health_check_loop())

            self.state = SystemState.RUNNING
            self.start_time = datetime.utcnow()

            self.logger.info("Platform initialization completed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Platform initialization failed: {e}")
            self.state = SystemState.ERROR
            return False

    async def run(self):
        """
        Main execution loop for the platform.

        Keeps the platform running and handles coordination between components.
        """
        if self.state != SystemState.RUNNING:
            if not await self.initialize():
                return

        self.logger.info("Platform is now running")

        try:
            # Main operation loop
            while not self.shutdown_requested and self.state == SystemState.RUNNING:
                await self._process_system_tasks()
                await asyncio.sleep(10)  # Main loop interval

        except KeyboardInterrupt:
            self.logger.info("Shutdown requested via keyboard interrupt")
        except Exception as e:
            self.logger.error(f"Unexpected error in main loop: {e}")
            self.state = SystemState.ERROR
        finally:
            await self.shutdown()

    async def shutdown(self):
        """Gracefully shutdown all platform components."""
        if self.state == SystemState.STOPPING:
            return

        self.logger.info("Initiating platform shutdown...")
        self.state = SystemState.STOPPING

        try:
            # Cancel health check task
            if self.health_check_task:
                self.health_check_task.cancel()
                try:
                    await self.health_check_task
                except asyncio.CancelledError:
                    pass

            # Shutdown scheduler
            if self.scheduler:
                await self.scheduler.stop()

            # Shutdown MCP servers
            if self.mcp_manager:
                await self.mcp_manager.shutdown()

            # Generate final statistics report
            await self._generate_shutdown_report()

            self.state = SystemState.STOPPED
            self.logger.info("Platform shutdown completed")

        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")

    async def generate_analysis_report(
        self,
        symbols: List[str],
        report_type: str = "comprehensive",
        priority: JobPriority = JobPriority.NORMAL
    ) -> Optional[str]:
        """
        Generate investment analysis report for specified symbols using integration framework.

        Args:
            symbols: List of stock symbols to analyze
            report_type: Type of report to generate
            priority: Analysis priority level

        Returns:
            Path to generated report or None if failed
        """
        try:
            self.logger.info(f"Starting analysis workflow for symbols: {symbols}")

            # Execute full analysis workflow through integration framework
            workflow_result = await self.integration_framework.execute_workflow(
                "full_analysis",
                symbols=symbols,
                report_type=report_type,
                priority=priority
            )

            if workflow_result.get("success", False):
                report_path = workflow_result.get("results", {}).get("report_path")
                if report_path:
                    self.stats['reports_generated'] += 1
                    self.stats['last_successful_analysis'] = datetime.utcnow()
                    self.logger.info(f"Analysis workflow completed successfully: {report_path}")
                    return report_path
                else:
                    self.logger.warning("Workflow succeeded but no report path returned")
            else:
                error = workflow_result.get("error", "Unknown error")
                self.logger.error(f"Analysis workflow failed: {error}")

            return None

        except Exception as e:
            self.logger.error(f"Analysis workflow execution failed: {e}")
            self.stats['errors_encountered'] += 1
            return None

    async def execute_integrated_workflow(self, workflow_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a workflow using the integration framework.

        Args:
            workflow_name: Name of workflow to execute
            **kwargs: Workflow parameters

        Returns:
            Workflow execution results
        """
        try:
            self.logger.info(f"Executing integrated workflow: {workflow_name}")

            result = await self.integration_framework.execute_workflow(workflow_name, **kwargs)

            # Update statistics based on result
            if result.get("success", False):
                self.stats['analyses_completed'] += 1
            else:
                self.stats['errors_encountered'] += 1

            return result

        except Exception as e:
            self.logger.error(f"Integrated workflow execution failed: {workflow_name} - {e}")
            self.stats['errors_encountered'] += 1
            return {
                "success": False,
                "error": str(e),
                "workflow": workflow_name,
                "timestamp": datetime.utcnow().isoformat()
            }

    async def _initialize_components(self):
        """Initialize all platform components using integration framework."""
        self.logger.info("Initializing components through integration framework...")

        # Initialize and register MCP Server Manager
        try:
            self.mcp_manager = MCPServerManager()
            self.integration_framework.register_component(
                "mcp_manager",
                self.mcp_manager,
                ComponentType.MCP_SERVER,
                startup_method="start" if hasattr(self.mcp_manager, "start") else None,
                shutdown_method="shutdown" if hasattr(self.mcp_manager, "shutdown") else None,
                health_check_method="get_server_status" if hasattr(self.mcp_manager, "get_server_status") else None
            )
            self.stats['component_status']['mcp_manager'] = 'initialized'
            self.logger.info("MCP Server Manager registered")
        except Exception as e:
            self.logger.error(f"Failed to initialize MCP Manager: {e}")
            self.stats['component_status']['mcp_manager'] = 'failed'

        # Initialize and register Analysis Engines
        try:
            self.recommendation_engine = RecommendationEngine()
            self.integration_framework.register_component(
                "recommendation_engine",
                self.recommendation_engine,
                ComponentType.ANALYSIS_ENGINE,
                dependencies=["mcp_manager"]
            )

            self.sentiment_analyzer = FinancialSentimentAnalyzer()
            self.integration_framework.register_component(
                "sentiment_analyzer",
                self.sentiment_analyzer,
                ComponentType.ANALYSIS_ENGINE,
                dependencies=["mcp_manager"]
            )

            self.stats['component_status']['analysis_engines'] = 'initialized'
            self.logger.info("Analysis engines registered")
        except Exception as e:
            self.logger.error(f"Failed to initialize analysis engines: {e}")
            self.stats['component_status']['analysis_engines'] = 'failed'

        # Initialize and register Report System
        try:
            self.report_generator = MarkdownReportGenerator()
            self.integration_framework.register_component(
                "report_generator",
                self.report_generator,
                ComponentType.REPORT_GENERATOR,
                dependencies=["recommendation_engine", "sentiment_analyzer"]
            )

            self.report_validator = ReportValidator()
            self.integration_framework.register_component(
                "report_validator",
                self.report_validator,
                ComponentType.REPORT_GENERATOR
            )

            self.report_history = ReportHistoryTracker()
            self.integration_framework.register_component(
                "report_history",
                self.report_history,
                ComponentType.REPORT_GENERATOR
            )

            self.stats['component_status']['report_system'] = 'initialized'
            self.logger.info("Report system registered")
        except Exception as e:
            self.logger.error(f"Failed to initialize report system: {e}")
            self.stats['component_status']['report_system'] = 'failed'

        # Initialize and register GitHub integration (optional)
        try:
            self.github_uploader = GitHubReportUploader()
            self.integration_framework.register_component(
                "github_uploader",
                self.github_uploader,
                ComponentType.REPORT_GENERATOR,
                dependencies=["report_generator"]
            )
            self.stats['component_status']['github_uploader'] = 'initialized'
            self.logger.info("GitHub uploader registered")
        except Exception as e:
            self.logger.warning(f"GitHub uploader initialization failed (optional): {e}")
            self.stats['component_status']['github_uploader'] = 'failed'

        # Initialize and register Notification System
        try:
            self.notification_system = NotificationSystem()
            self.integration_framework.register_component(
                "notification_system",
                self.notification_system,
                ComponentType.NOTIFICATION_SYSTEM,
                startup_method="start",
                shutdown_method="stop",
                health_check_method="get_statistics"
            )
            self.stats['component_status']['notification_system'] = 'initialized'
            self.logger.info("Notification system registered")
        except Exception as e:
            self.logger.error(f"Failed to initialize notification system: {e}")
            self.stats['component_status']['notification_system'] = 'failed'

        # Initialize and register Alert System
        try:
            self.alert_system = IntelligentAlertSystem()
            self.alert_system.set_external_systems(
                notification_system=self.notification_system
            )
            self.integration_framework.register_component(
                "alert_system",
                self.alert_system,
                ComponentType.ALERT_SYSTEM,
                dependencies=["notification_system"]
            )
            self.stats['component_status']['alert_system'] = 'initialized'
            self.logger.info("Alert system registered")
        except Exception as e:
            self.logger.error(f"Failed to initialize alert system: {e}")
            self.stats['component_status']['alert_system'] = 'failed'

        # Initialize and register Monitoring Dashboard
        try:
            self.monitoring_dashboard = MonitoringDashboard()
            self.monitoring_dashboard.set_components(
                orchestrator=self,
                scheduler=self.scheduler,
                notification_system=self.notification_system,
                mcp_manager=self.mcp_manager
            )
            self.integration_framework.register_component(
                "monitoring_dashboard",
                self.monitoring_dashboard,
                ComponentType.MONITORING_SYSTEM,
                startup_method="start",
                dependencies=["notification_system", "alert_system"]
            )
            self.stats['component_status']['monitoring_dashboard'] = 'initialized'
            self.logger.info("Monitoring dashboard registered")
        except Exception as e:
            self.logger.error(f"Failed to initialize monitoring dashboard: {e}")
            self.stats['component_status']['monitoring_dashboard'] = 'failed'

        # Initialize and register Job Scheduler
        if self.config.enable_scheduling:
            try:
                self.scheduler = JobScheduler()
                self.integration_framework.register_component(
                    "scheduler",
                    self.scheduler,
                    ComponentType.SCHEDULER,
                    startup_method="start",
                    shutdown_method="stop",
                    health_check_method="get_statistics"
                )
                self.stats['component_status']['scheduler'] = 'initialized'
                self.logger.info("Job scheduler registered")
            except Exception as e:
                self.logger.error(f"Failed to initialize scheduler: {e}")
                self.stats['component_status']['scheduler'] = 'failed'

        # Start all components through integration framework
        success = await self.integration_framework.start_all_components()
        if not success:
            raise RuntimeError("Failed to start all components through integration framework")

        self.logger.info("All components initialized and started through integration framework")

    async def _setup_scheduled_jobs(self):
        """Setup automated scheduled jobs."""
        if not self.scheduler:
            return

        try:
            # Daily market analysis (9:30 AM EST, weekdays)
            self.scheduler.add_job(
                name="Daily Market Analysis",
                function=self._daily_market_analysis,
                cron_expression="30 9 * * 1-5",
                priority=JobPriority.HIGH,
                market_hours_only=True,
                timezone="US/Eastern"
            )

            # End of day report (4:30 PM EST, weekdays)
            self.scheduler.add_job(
                name="End of Day Report",
                function=self._end_of_day_report,
                cron_expression="30 16 * * 1-5",
                priority=JobPriority.HIGH,
                timezone="US/Eastern"
            )

            # Weekly portfolio review (Sunday 6 PM EST)
            self.scheduler.add_job(
                name="Weekly Portfolio Review",
                function=self._weekly_portfolio_review,
                cron_expression="0 18 * * 0",
                priority=JobPriority.NORMAL,
                timezone="US/Eastern"
            )

            # System health check (every hour)
            self.scheduler.add_job(
                name="System Health Check",
                function=self._system_health_check,
                cron_expression="0 * * * *",
                priority=JobPriority.LOW
            )

            # Data cleanup (daily at 2 AM EST)
            self.scheduler.add_job(
                name="Data Cleanup",
                function=self._cleanup_old_data,
                cron_expression="0 2 * * *",
                priority=JobPriority.LOW,
                timezone="US/Eastern"
            )

            self.logger.info("Scheduled jobs configured successfully")

        except Exception as e:
            self.logger.error(f"Failed to setup scheduled jobs: {e}")

    async def _perform_comprehensive_analysis(self, symbols: List[str]) -> Dict[str, Any]:
        """Perform comprehensive analysis using all available engines."""
        analysis_data = {
            'symbols': symbols,
            'timestamp': datetime.utcnow().isoformat(),
            'market_data': {},
            'technical_analysis': {},
            'sentiment_analysis': {},
            'recommendations': {},
            'risk_assessment': {}
        }

        try:
            # Get market data through MCP servers
            if self.mcp_manager:
                for symbol in symbols:
                    try:
                        # This would call actual MCP server methods
                        market_data = await self._get_market_data(symbol)
                        analysis_data['market_data'][symbol] = market_data
                    except Exception as e:
                        self.logger.warning(f"Failed to get market data for {symbol}: {e}")

            # Perform technical analysis
            if self.chart_analyzer:
                for symbol in symbols:
                    try:
                        technical_data = await self._perform_technical_analysis(symbol)
                        analysis_data['technical_analysis'][symbol] = technical_data
                    except Exception as e:
                        self.logger.warning(f"Technical analysis failed for {symbol}: {e}")

            # Perform sentiment analysis
            if self.sentiment_analyzer:
                try:
                    sentiment_data = await self._perform_sentiment_analysis(symbols)
                    analysis_data['sentiment_analysis'] = sentiment_data
                except Exception as e:
                    self.logger.warning(f"Sentiment analysis failed: {e}")

            # Generate investment recommendations
            if self.recommendation_engine:
                try:
                    recommendations = await self._generate_recommendations(symbols, analysis_data)
                    analysis_data['recommendations'] = recommendations
                except Exception as e:
                    self.logger.warning(f"Recommendation generation failed: {e}")

            # Perform risk assessment
            if self.risk_engine:
                try:
                    risk_data = await self._assess_portfolio_risk(symbols, analysis_data)
                    analysis_data['risk_assessment'] = risk_data
                except Exception as e:
                    self.logger.warning(f"Risk assessment failed: {e}")

            self.stats['analyses_completed'] += 1
            return analysis_data

        except Exception as e:
            self.logger.error(f"Comprehensive analysis failed: {e}")
            return {}

    async def _generate_report(self, analysis_data: Dict[str, Any], report_type: str) -> Optional[str]:
        """Generate formatted report from analysis data."""
        if not self.report_generator:
            return None

        try:
            # Format data for report template
            report_data = self._format_analysis_for_report(analysis_data)

            # Generate report using appropriate template
            if report_type == "comprehensive":
                return self.report_generator.generate_comprehensive_report(
                    analysis_data['symbols'],
                    {
                        'recommendation_engine': self.recommendation_engine,
                        'sentiment_analyzer': self.sentiment_analyzer,
                        'chart_analyzer': self.chart_analyzer,
                        'risk_engine': self.risk_engine
                    }
                )
            elif report_type == "daily":
                return self.report_generator.generate_market_summary_report(report_data)
            else:
                return self.report_generator.generate_report("report-template.md", report_data)

        except Exception as e:
            self.logger.error(f"Report generation failed: {e}")
            return None

    async def _process_system_tasks(self):
        """Process periodic system tasks."""
        try:
            # Update system statistics
            if self.start_time:
                self.stats['uptime_seconds'] = (datetime.utcnow() - self.start_time).total_seconds()

            # Check component health
            await self._check_component_health()

            # Handle any pending notifications
            await self._process_pending_notifications()

        except Exception as e:
            self.logger.error(f"System task processing error: {e}")

    async def _health_check_loop(self):
        """Continuous health monitoring loop."""
        while not self.shutdown_requested:
            try:
                await self._comprehensive_health_check()
                await asyncio.sleep(self.config.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Health check error: {e}")
                await asyncio.sleep(60)  # Back off on error

    # Scheduled job implementations
    async def _daily_market_analysis(self):
        """Perform daily market analysis."""
        self.logger.info("Running daily market analysis")

        # Default symbols for daily analysis
        symbols = ["SPY", "QQQ", "DIA", "IWM"]  # Major ETFs

        report_path = await self.generate_analysis_report(
            symbols,
            "daily",
            JobPriority.HIGH
        )

        if report_path:
            self.logger.info(f"Daily market analysis completed: {report_path}")
        else:
            self.logger.error("Daily market analysis failed")

    async def _end_of_day_report(self):
        """Generate end of day summary report."""
        self.logger.info("Generating end of day report")
        # Implementation would generate EOD summary
        pass

    async def _weekly_portfolio_review(self):
        """Generate weekly portfolio review."""
        self.logger.info("Running weekly portfolio review")
        # Implementation would analyze portfolio performance
        pass

    async def _system_health_check(self):
        """Perform system health check."""
        self.logger.debug("Running system health check")
        await self._comprehensive_health_check()

    async def _cleanup_old_data(self):
        """Clean up old data files."""
        self.logger.info("Running data cleanup")

        try:
            # Clean up old reports
            reports_dir = Path("reports")
            if reports_dir.exists():
                cutoff_date = datetime.utcnow() - timedelta(days=self.config.data_retention_days)

                for report_file in reports_dir.glob("*.md"):
                    if report_file.stat().st_mtime < cutoff_date.timestamp():
                        report_file.unlink()
                        self.logger.debug(f"Cleaned up old report: {report_file}")

            # Clean up old logs
            logs_dir = Path("logs")
            if logs_dir.exists():
                for log_file in logs_dir.glob("*.log*"):
                    if log_file.stat().st_mtime < cutoff_date.timestamp():
                        log_file.unlink()
                        self.logger.debug(f"Cleaned up old log: {log_file}")

        except Exception as e:
            self.logger.error(f"Data cleanup failed: {e}")

    # Helper methods (these would be implemented with actual logic)
    async def _get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get market data for symbol."""
        # Placeholder - would use MCP servers
        return {"symbol": symbol, "price": 100.0, "volume": 1000000}

    async def _perform_technical_analysis(self, symbol: str) -> Dict[str, Any]:
        """Perform technical analysis for symbol."""
        # Placeholder - would use chart analyzer
        return {"symbol": symbol, "trend": "bullish", "rsi": 45.0}

    async def _perform_sentiment_analysis(self, symbols: List[str]) -> Dict[str, Any]:
        """Perform sentiment analysis."""
        # Placeholder - would use sentiment analyzer
        return {"overall_sentiment": "neutral", "confidence": 0.7}

    async def _generate_recommendations(self, symbols: List[str], analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate investment recommendations."""
        # Placeholder - would use recommendation engine
        return {"recommendations": [{"symbol": s, "action": "HOLD"} for s in symbols]}

    async def _assess_portfolio_risk(self, symbols: List[str], analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess portfolio risk."""
        # Placeholder - would use risk engine
        return {"risk_score": 5, "max_drawdown": 0.15}

    def _format_analysis_for_report(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format analysis data for report template."""
        return {
            "analysis_date": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "symbols": analysis_data.get("symbols", []),
            "market_summary": analysis_data.get("market_data", {}),
            "recommendations": analysis_data.get("recommendations", {})
        }

    async def _track_report(self, report_path: str, analysis_data: Dict[str, Any]):
        """Track report in history system."""
        if not self.report_history:
            return

        try:
            with open(report_path, 'r') as f:
                content = f.read()

            report_id = f"auto_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

            self.report_history.add_report(
                report_id=report_id,
                title="Automated Analysis Report",
                report_type="comprehensive",
                content=content,
                predictions=[],  # Would extract predictions from analysis_data
                file_path=report_path
            )

        except Exception as e:
            self.logger.error(f"Report tracking failed: {e}")

    async def _upload_report_to_github(self, report_path: str):
        """Upload report to GitHub."""
        if self.github_uploader:
            try:
                result = self.github_uploader.upload_report(report_path)
                self.logger.info(f"Report uploaded to GitHub: {result.get('html_url', 'unknown')}")
            except Exception as e:
                self.logger.error(f"GitHub upload failed: {e}")

    async def _check_component_health(self):
        """Check health of all components."""
        # Update component status
        for component_name in self.stats['component_status']:
            # Placeholder - would actually check component health
            pass

    async def _process_pending_notifications(self):
        """Process any pending notifications."""
        # Placeholder - would handle notification queue
        pass

    async def _comprehensive_health_check(self):
        """Perform comprehensive system health check."""
        try:
            health_status = {
                'timestamp': datetime.utcnow().isoformat(),
                'system_state': self.state.value,
                'uptime_seconds': self.stats['uptime_seconds'],
                'components': self.stats['component_status'].copy(),
                'performance': {
                    'reports_generated': self.stats['reports_generated'],
                    'analyses_completed': self.stats['analyses_completed'],
                    'errors_encountered': self.stats['errors_encountered']
                }
            }

            # Check scheduler health
            if self.scheduler:
                scheduler_stats = self.scheduler.get_statistics()
                health_status['scheduler'] = scheduler_stats

            # Log health status
            self.logger.debug(f"System health: {health_status}")

        except Exception as e:
            self.logger.error(f"Comprehensive health check failed: {e}")

    async def _generate_shutdown_report(self):
        """Generate final system report before shutdown."""
        try:
            uptime = datetime.utcnow() - self.start_time if self.start_time else timedelta(0)

            shutdown_report = {
                'shutdown_time': datetime.utcnow().isoformat(),
                'total_uptime': str(uptime),
                'final_statistics': self.stats.copy(),
                'component_status': self.stats['component_status'].copy()
            }

            # Save shutdown report
            shutdown_dir = Path("logs")
            shutdown_dir.mkdir(exist_ok=True)

            shutdown_file = shutdown_dir / f"shutdown_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"

            with open(shutdown_file, 'w') as f:
                json.dump(shutdown_report, f, indent=2)

            self.logger.info(f"Shutdown report saved: {shutdown_file}")

        except Exception as e:
            self.logger.error(f"Failed to generate shutdown report: {e}")

    def _load_configuration(self):
        """Load system configuration from file."""
        if not self.config_file or not Path(self.config_file).exists():
            self.logger.info("Using default configuration")
            return

        try:
            with open(self.config_file, 'r') as f:
                if self.config_file.endswith('.yaml') or self.config_file.endswith('.yml'):
                    config_data = yaml.safe_load(f)
                else:
                    config_data = json.load(f)

            # Update configuration
            for key, value in config_data.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)

            self.logger.info(f"Configuration loaded from {self.config_file}")

        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")

    def _load_risk_config(self) -> Dict[str, Any]:
        """Load risk management configuration."""
        config_path = Path("config/risk_management.yaml")

        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                self.logger.error(f"Failed to load risk config: {e}")

        # Return default configuration
        return {
            'max_position_size': 0.1,
            'max_portfolio_risk': 0.02,
            'stop_loss_threshold': 0.05,
            'risk_free_rate': 0.02
        }

    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating shutdown")
            self.shutdown_requested = True

        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, signal_handler)
        if hasattr(signal, 'SIGINT'):
            signal.signal(signal.SIGINT, signal_handler)

    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status."""
        return {
            'state': self.state.value,
            'config': {
                'mode': self.config.mode.value,
                'scheduling_enabled': self.config.enable_scheduling,
                'live_data_enabled': self.config.enable_live_data
            },
            'statistics': self.stats.copy(),
            'uptime': str(datetime.utcnow() - self.start_time) if self.start_time else "0:00:00"
        }


def main():
    """Main entry point for the orchestrator."""
    parser = argparse.ArgumentParser(description="Agent Investment Platform Orchestrator")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--mode", choices=["development", "testing", "production", "demo"],
                      default="development", help="Operation mode")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                      default="INFO", help="Logging level")
    parser.add_argument("--test-mode", action="store_true",
                      help="Run in test mode (generate sample report)")
    parser.add_argument("--live", action="store_true",
                      help="Enable live data feeds")

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger = logging.getLogger(__name__)

    async def run_orchestrator():
        """Run the orchestrator."""
        orchestrator = PlatformOrchestrator(args.config)

        # Configure based on arguments
        orchestrator.config.mode = OperationMode(args.mode)
        orchestrator.config.enable_live_data = args.live

        if args.test_mode:
            logger.info("Running in test mode")
            # Generate a test report
            test_symbols = ["AAPL", "GOOGL", "MSFT"]
            report_path = await orchestrator.generate_analysis_report(
                test_symbols, "comprehensive"
            )
            if report_path:
                logger.info(f"Test report generated: {report_path}")
            else:
                logger.error("Test report generation failed")
            return

        try:
            await orchestrator.run()
        except KeyboardInterrupt:
            logger.info("Orchestrator stopped by user")
        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            sys.exit(1)

    # Run the orchestrator
    try:
        asyncio.run(run_orchestrator())
    except KeyboardInterrupt:
        logger.info("Orchestrator interrupted")
        sys.exit(0)


if __name__ == "__main__":
    main()
