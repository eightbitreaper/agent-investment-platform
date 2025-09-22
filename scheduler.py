#!/usr/bin/env python3
"""
Agent Investment Platform - Scheduler System

This module provides comprehensive scheduling functionality for automated
report generation, analysis updates, and system maintenance tasks.

Features:
- Cron-like scheduling with flexible timing options
- Priority-based job queue management
- Market hours awareness for trading-related tasks
- Retry logic with exponential backoff
- Health monitoring and error recovery
- Configurable job persistence and logging
"""

import asyncio
import logging
import json
import threading
from datetime import datetime, timedelta, time as dt_time
from typing import Dict, List, Callable, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import uuid
import time
import croniter

try:
    import pytz
    TIMEZONE_SUPPORT = True
except ImportError:
    TIMEZONE_SUPPORT = False
    logging.warning("pytz not available, timezone support disabled")


class JobStatus(Enum):
    """Job execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class JobPriority(Enum):
    """Job priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


class MarketSession(Enum):
    """Market session types."""
    PRE_MARKET = "pre_market"
    REGULAR = "regular"
    AFTER_HOURS = "after_hours"
    CLOSED = "closed"


@dataclass
class ScheduledJob:
    """Represents a scheduled job with all its parameters."""
    id: str
    name: str
    function: Callable
    cron_expression: str
    priority: JobPriority = JobPriority.NORMAL
    max_retries: int = 3
    retry_delay: int = 60  # seconds
    timeout: int = 300  # seconds
    market_hours_only: bool = False
    timezone: str = "UTC"
    enabled: bool = True
    metadata: Optional[Dict[str, Any]] = None

    # Runtime state
    status: JobStatus = JobStatus.PENDING
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    retry_count: int = 0
    error_message: Optional[str] = None
    execution_time: Optional[float] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        self._calculate_next_run()

    def _calculate_next_run(self):
        """Calculate next execution time based on cron expression."""
        try:
            if TIMEZONE_SUPPORT and self.timezone != "UTC":
                tz = pytz.timezone(self.timezone)
                now = datetime.now(tz)
            else:
                now = datetime.utcnow()

            cron = croniter.croniter(self.cron_expression, now)
            self.next_run = cron.get_next(datetime)
        except Exception as e:
            logging.error(f"Failed to calculate next run for job {self.id}: {e}")
            self.next_run = datetime.utcnow() + timedelta(minutes=1)

    def should_run_now(self) -> bool:
        """Check if job should run now."""
        if not self.enabled or self.status == JobStatus.RUNNING:
            return False

        now = datetime.utcnow()
        if self.next_run and now >= self.next_run:
            if self.market_hours_only:
                return self._is_market_hours()
            return True

        return False

    def _is_market_hours(self) -> bool:
        """Check if current time is within market hours (NYSE)."""
        if not TIMEZONE_SUPPORT:
            # Fallback: assume 9:30 AM - 4:00 PM EST (14:30 - 21:00 UTC)
            now_utc = datetime.utcnow().time()
            return dt_time(14, 30) <= now_utc <= dt_time(21, 0)

        try:
            est = pytz.timezone('US/Eastern')
            now_est = datetime.now(est)

            # Check if weekday (Monday=0, Sunday=6)
            if now_est.weekday() >= 5:  # Saturday=5, Sunday=6
                return False

            # Regular market hours: 9:30 AM - 4:00 PM EST
            market_open = now_est.replace(hour=9, minute=30, second=0, microsecond=0)
            market_close = now_est.replace(hour=16, minute=0, second=0, microsecond=0)

            return market_open <= now_est <= market_close
        except Exception as e:
            logging.warning(f"Market hours check failed: {e}")
            return True  # Default to allowing execution

    def get_market_session(self) -> MarketSession:
        """Determine current market session."""
        if not TIMEZONE_SUPPORT:
            return MarketSession.REGULAR

        try:
            est = pytz.timezone('US/Eastern')
            now_est = datetime.now(est)

            if now_est.weekday() >= 5:
                return MarketSession.CLOSED

            current_time = now_est.time()
            if dt_time(4, 0) <= current_time < dt_time(9, 30):
                return MarketSession.PRE_MARKET
            elif dt_time(9, 30) <= current_time < dt_time(16, 0):
                return MarketSession.REGULAR
            elif dt_time(16, 0) <= current_time < dt_time(20, 0):
                return MarketSession.AFTER_HOURS
            else:
                return MarketSession.CLOSED
        except Exception:
            return MarketSession.REGULAR


class JobScheduler:
    """
    Comprehensive job scheduler for the Agent Investment Platform.

    Provides cron-like scheduling with advanced features for financial
    market applications including market hours awareness, priority queuing,
    and robust error handling.
    """

    def __init__(
        self,
        config_file: Optional[str] = None,
        max_concurrent_jobs: int = 5,
        persistence_file: Optional[str] = None
    ):
        """
        Initialize the job scheduler.

        Args:
            config_file: Path to scheduler configuration file
            max_concurrent_jobs: Maximum number of jobs running concurrently
            persistence_file: File to persist job state across restarts
        """
        self.logger = logging.getLogger(__name__)
        self.jobs: Dict[str, ScheduledJob] = {}
        self.running_jobs: Dict[str, asyncio.Task] = {}
        self.max_concurrent_jobs = max_concurrent_jobs
        self.running = False
        self.scheduler_task: Optional[asyncio.Task] = None

        # Configuration
        self.config_file = config_file
        self.persistence_file = persistence_file or "data/scheduler_state.json"
        self.check_interval = 10  # seconds

        # Statistics
        self.stats = {
            'jobs_completed': 0,
            'jobs_failed': 0,
            'total_execution_time': 0.0,
            'started_at': datetime.utcnow(),
            'last_health_check': None
        }

        # Load configuration and state
        self._load_config()
        self._load_state()

        self.logger.info(f"JobScheduler initialized with {len(self.jobs)} jobs")

    def add_job(
        self,
        name: str,
        function: Callable,
        cron_expression: str,
        priority: JobPriority = JobPriority.NORMAL,
        **kwargs
    ) -> str:
        """
        Add a new scheduled job.

        Args:
            name: Human-readable job name
            function: Function to execute
            cron_expression: Cron-style scheduling expression
            priority: Job priority level
            **kwargs: Additional job parameters

        Returns:
            Job ID string
        """
        job_id = str(uuid.uuid4())

        try:
            job = ScheduledJob(
                id=job_id,
                name=name,
                function=function,
                cron_expression=cron_expression,
                priority=priority,
                **kwargs
            )

            self.jobs[job_id] = job
            self.logger.info(f"Added job '{name}' (ID: {job_id}) with schedule: {cron_expression}")

            # Persist state
            self._save_state()

            return job_id

        except Exception as e:
            self.logger.error(f"Failed to add job '{name}': {e}")
            raise

    def remove_job(self, job_id: str) -> bool:
        """
        Remove a scheduled job.

        Args:
            job_id: Job ID to remove

        Returns:
            True if job was removed, False if not found
        """
        if job_id in self.jobs:
            # Cancel if currently running
            if job_id in self.running_jobs:
                self.running_jobs[job_id].cancel()
                del self.running_jobs[job_id]

            job_name = self.jobs[job_id].name
            del self.jobs[job_id]

            self.logger.info(f"Removed job '{job_name}' (ID: {job_id})")
            self._save_state()
            return True

        return False

    def get_job(self, job_id: str) -> Optional[ScheduledJob]:
        """Get job by ID."""
        return self.jobs.get(job_id)

    def list_jobs(self, status_filter: Optional[JobStatus] = None) -> List[ScheduledJob]:
        """
        List all jobs, optionally filtered by status.

        Args:
            status_filter: Only return jobs with this status

        Returns:
            List of ScheduledJob objects
        """
        jobs = list(self.jobs.values())

        if status_filter:
            jobs = [job for job in jobs if job.status == status_filter]

        # Sort by priority (highest first), then by next run time
        jobs.sort(key=lambda j: (-j.priority.value, j.next_run or datetime.max))

        return jobs

    def enable_job(self, job_id: str) -> bool:
        """Enable a job."""
        if job_id in self.jobs:
            self.jobs[job_id].enabled = True
            self.jobs[job_id]._calculate_next_run()
            self._save_state()
            return True
        return False

    def disable_job(self, job_id: str) -> bool:
        """Disable a job."""
        if job_id in self.jobs:
            self.jobs[job_id].enabled = False
            # Cancel if running
            if job_id in self.running_jobs:
                self.running_jobs[job_id].cancel()
                del self.running_jobs[job_id]
            self._save_state()
            return True
        return False

    async def start(self):
        """Start the scheduler."""
        if self.running:
            self.logger.warning("Scheduler is already running")
            return

        self.running = True
        self.stats['started_at'] = datetime.utcnow()

        self.logger.info("Starting job scheduler")
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())

    async def stop(self):
        """Stop the scheduler gracefully."""
        if not self.running:
            return

        self.logger.info("Stopping job scheduler")
        self.running = False

        # Cancel scheduler task
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass

        # Cancel all running jobs
        for job_id, task in list(self.running_jobs.items()):
            self.logger.info(f"Cancelling running job: {self.jobs[job_id].name}")
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        self.running_jobs.clear()
        self.logger.info("Job scheduler stopped")

    async def _scheduler_loop(self):
        """Main scheduler loop."""
        while self.running:
            try:
                await self._check_and_run_jobs()
                await self._cleanup_completed_jobs()
                await self._health_check()

                await asyncio.sleep(self.check_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Scheduler loop error: {e}")
                await asyncio.sleep(self.check_interval)

    async def _check_and_run_jobs(self):
        """Check for jobs that need to run and execute them."""
        # Don't start new jobs if at capacity
        if len(self.running_jobs) >= self.max_concurrent_jobs:
            return

        # Get jobs that should run, sorted by priority
        ready_jobs = [
            job for job in self.jobs.values()
            if job.should_run_now() and job.id not in self.running_jobs
        ]

        ready_jobs.sort(key=lambda j: (-j.priority.value, j.next_run))

        # Start jobs up to capacity limit
        slots_available = self.max_concurrent_jobs - len(self.running_jobs)
        for job in ready_jobs[:slots_available]:
            await self._execute_job(job)

    async def _execute_job(self, job: ScheduledJob):
        """Execute a single job."""
        job.status = JobStatus.RUNNING
        job.last_run = datetime.utcnow()

        self.logger.info(f"Starting job '{job.name}' (ID: {job.id})")

        # Create and track the job task
        task = asyncio.create_task(self._run_job_with_timeout(job))
        self.running_jobs[job.id] = task

    async def _run_job_with_timeout(self, job: ScheduledJob):
        """Run job with timeout and error handling."""
        start_time = time.time()

        try:
            # Run job with timeout
            await asyncio.wait_for(
                self._run_job_function(job),
                timeout=job.timeout
            )

            # Job completed successfully
            job.status = JobStatus.COMPLETED
            job.retry_count = 0
            job.error_message = None
            job.execution_time = time.time() - start_time

            self.stats['jobs_completed'] += 1
            self.stats['total_execution_time'] += job.execution_time

            self.logger.info(f"Job '{job.name}' completed in {job.execution_time:.2f}s")

        except asyncio.TimeoutError:
            job.status = JobStatus.FAILED
            job.error_message = f"Job timed out after {job.timeout} seconds"
            self.logger.error(f"Job '{job.name}' timed out")
            await self._handle_job_failure(job)

        except asyncio.CancelledError:
            job.status = JobStatus.CANCELLED
            self.logger.info(f"Job '{job.name}' was cancelled")

        except Exception as e:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            job.execution_time = time.time() - start_time

            self.logger.error(f"Job '{job.name}' failed: {e}")
            await self._handle_job_failure(job)

        finally:
            # Calculate next run time
            job._calculate_next_run()

            # Remove from running jobs
            if job.id in self.running_jobs:
                del self.running_jobs[job.id]

            # Persist state
            self._save_state()

    async def _run_job_function(self, job: ScheduledJob):
        """Run the job function, handling both sync and async functions."""
        try:
            if asyncio.iscoroutinefunction(job.function):
                await job.function()
            else:
                # Run sync function in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, job.function)

        except Exception as e:
            # Add job context to exception
            raise Exception(f"Job '{job.name}' execution failed: {e}") from e

    async def _handle_job_failure(self, job: ScheduledJob):
        """Handle job failure with retry logic."""
        self.stats['jobs_failed'] += 1

        if job.retry_count < job.max_retries:
            job.retry_count += 1
            job.status = JobStatus.RETRYING

            # Calculate retry delay with exponential backoff
            retry_delay = job.retry_delay * (2 ** (job.retry_count - 1))
            retry_time = datetime.utcnow() + timedelta(seconds=retry_delay)
            job.next_run = retry_time

            self.logger.info(
                f"Job '{job.name}' will retry in {retry_delay}s "
                f"(attempt {job.retry_count}/{job.max_retries})"
            )
        else:
            self.logger.error(
                f"Job '{job.name}' failed permanently after {job.max_retries} retries"
            )

    async def _cleanup_completed_jobs(self):
        """Clean up completed job tasks."""
        # This is handled in _run_job_with_timeout, but we can add
        # additional cleanup logic here if needed
        pass

    async def _health_check(self):
        """Perform scheduler health check."""
        self.stats['last_health_check'] = datetime.utcnow()

        # Check for stuck jobs (running too long)
        stuck_threshold = timedelta(minutes=30)
        current_time = datetime.utcnow()

        for job_id, task in list(self.running_jobs.items()):
            job = self.jobs[job_id]
            if job.last_run and (current_time - job.last_run) > stuck_threshold:
                self.logger.warning(f"Job '{job.name}' appears stuck, cancelling")
                task.cancel()

        # Log scheduler statistics
        uptime = current_time - self.stats['started_at']
        self.logger.debug(
            f"Scheduler health: {len(self.running_jobs)} running, "
            f"{len(self.jobs)} total jobs, uptime: {uptime}"
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Get scheduler statistics."""
        uptime = datetime.utcnow() - self.stats['started_at']

        return {
            **self.stats,
            'uptime_seconds': uptime.total_seconds(),
            'running_jobs': len(self.running_jobs),
            'total_jobs': len(self.jobs),
            'enabled_jobs': len([j for j in self.jobs.values() if j.enabled]),
            'average_execution_time': (
                self.stats['total_execution_time'] / max(self.stats['jobs_completed'], 1)
            )
        }

    def get_job_summary(self) -> Dict[str, Any]:
        """Get summary of all jobs."""
        summary = {
            'total': len(self.jobs),
            'by_status': {},
            'by_priority': {},
            'next_runs': []
        }

        for job in self.jobs.values():
            # Count by status
            status_name = job.status.value
            summary['by_status'][status_name] = summary['by_status'].get(status_name, 0) + 1

            # Count by priority
            priority_name = job.priority.name
            summary['by_priority'][priority_name] = summary['by_priority'].get(priority_name, 0) + 1

            # Collect next run times
            if job.enabled and job.next_run:
                summary['next_runs'].append({
                    'job_name': job.name,
                    'next_run': job.next_run.isoformat(),
                    'priority': job.priority.name
                })

        # Sort next runs by time
        summary['next_runs'].sort(key=lambda x: x['next_run'])

        return summary

    def _load_config(self):
        """Load scheduler configuration from file."""
        if not self.config_file or not Path(self.config_file).exists():
            return

        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)

            self.check_interval = config.get('check_interval', self.check_interval)
            self.max_concurrent_jobs = config.get('max_concurrent_jobs', self.max_concurrent_jobs)

            self.logger.info(f"Loaded scheduler configuration from {self.config_file}")

        except Exception as e:
            self.logger.error(f"Failed to load config from {self.config_file}: {e}")

    def _save_state(self):
        """Save scheduler state to persistence file."""
        if not self.persistence_file:
            return

        try:
            # Create directory if it doesn't exist
            Path(self.persistence_file).parent.mkdir(parents=True, exist_ok=True)

            # Prepare state data (exclude function objects)
            state_data = {
                'jobs': {},
                'stats': self.stats.copy(),
                'last_saved': datetime.utcnow().isoformat()
            }

            for job_id, job in self.jobs.items():
                job_data = asdict(job)
                # Remove function object as it's not serializable
                del job_data['function']
                state_data['jobs'][job_id] = job_data

            with open(self.persistence_file, 'w') as f:
                json.dump(state_data, f, indent=2, default=str)

        except Exception as e:
            self.logger.error(f"Failed to save scheduler state: {e}")

    def _load_state(self):
        """Load scheduler state from persistence file."""
        if not self.persistence_file or not Path(self.persistence_file).exists():
            return

        try:
            with open(self.persistence_file, 'r') as f:
                state_data = json.load(f)

            # Load statistics
            if 'stats' in state_data:
                saved_stats = state_data['stats']
                # Convert string dates back to datetime objects
                if 'started_at' in saved_stats:
                    saved_stats['started_at'] = datetime.fromisoformat(saved_stats['started_at'])
                if 'last_health_check' in saved_stats and saved_stats['last_health_check']:
                    saved_stats['last_health_check'] = datetime.fromisoformat(saved_stats['last_health_check'])

                self.stats.update(saved_stats)

            self.logger.info(f"Loaded scheduler state from {self.persistence_file}")

        except Exception as e:
            self.logger.error(f"Failed to load scheduler state: {e}")


# Convenience functions for common scheduling patterns
def create_daily_job(name: str, function: Callable, hour: int, minute: int = 0) -> str:
    """Create a job that runs daily at specified time."""
    cron_expr = f"{minute} {hour} * * *"
    return JobScheduler().add_job(name, function, cron_expr)


def create_market_hours_job(name: str, function: Callable, cron_expression: str) -> str:
    """Create a job that only runs during market hours."""
    return JobScheduler().add_job(
        name, function, cron_expression,
        market_hours_only=True
    )


def create_high_priority_job(name: str, function: Callable, cron_expression: str) -> str:
    """Create a high-priority job."""
    return JobScheduler().add_job(
        name, function, cron_expression,
        priority=JobPriority.HIGH
    )


if __name__ == "__main__":
    # Example usage and testing
    import asyncio

    async def sample_job():
        """Sample job function."""
        print(f"Sample job executed at {datetime.now()}")
        await asyncio.sleep(2)  # Simulate work

    def sync_sample_job():
        """Sample synchronous job."""
        print(f"Sync job executed at {datetime.now()}")
        time.sleep(1)

    async def main():
        """Example usage."""
        logging.basicConfig(level=logging.INFO)

        scheduler = JobScheduler()

        # Add some sample jobs
        scheduler.add_job(
            "Daily Report",
            sample_job,
            "0 9 * * *",  # Daily at 9 AM
            priority=JobPriority.HIGH
        )

        scheduler.add_job(
            "Hourly Check",
            sync_sample_job,
            "0 * * * *",  # Every hour
            priority=JobPriority.NORMAL
        )

        scheduler.add_job(
            "Market Open Analysis",
            sample_job,
            "30 9 * * 1-5",  # 9:30 AM, weekdays only
            market_hours_only=True,
            priority=JobPriority.HIGH
        )

        # Start scheduler
        await scheduler.start()

        try:
            # Run for a while
            await asyncio.sleep(30)

            # Print statistics
            print("\nScheduler Statistics:")
            stats = scheduler.get_statistics()
            for key, value in stats.items():
                print(f"  {key}: {value}")

            print("\nJob Summary:")
            summary = scheduler.get_job_summary()
            for key, value in summary.items():
                print(f"  {key}: {value}")

        finally:
            await scheduler.stop()

    # Run example
    asyncio.run(main())
