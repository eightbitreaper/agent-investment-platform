"""
Log aggregation system for centralized log collection and indexing.

This module provides:
- Elasticsearch integration for log storage and search
- Log forwarding and buffering
- Index management and rotation
- Query interface for log retrieval
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, AsyncGenerator
from dataclasses import dataclass, asdict
from collections import deque
import aiohttp
import urllib.parse

from .core import LogEntry, get_logger
from .config import get_config_loader


@dataclass
class LogQuery:
    """Query parameters for log search."""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    level: Optional[str] = None
    component: Optional[str] = None
    logger_name: Optional[str] = None
    message_contains: Optional[str] = None
    limit: int = 100
    offset: int = 0
    sort_order: str = "desc"  # desc or asc


class ElasticsearchLogHandler:
    """Handler for sending logs to Elasticsearch."""

    def __init__(self, hosts: List[str], index_pattern: str = "logs-%Y.%m.%d"):
        self.hosts = hosts
        self.index_pattern = index_pattern
        self.logger = get_logger(__name__, "log_aggregation")
        self.session: Optional[aiohttp.ClientSession] = None
        self.buffer: deque = deque(maxlen=1000)
        self.flush_interval = 5.0  # seconds
        self.flush_task: Optional[asyncio.Task] = None
        self.batch_size = 100

    async def start(self):
        """Start the Elasticsearch handler."""
        if self.session is None:
            self.session = aiohttp.ClientSession()

        # Start periodic flush task
        if self.flush_task is None:
            self.flush_task = asyncio.create_task(self._flush_periodically())

        # Test connection
        await self._test_connection()

    async def stop(self):
        """Stop the Elasticsearch handler."""
        if self.flush_task:
            self.flush_task.cancel()
            try:
                await self.flush_task
            except asyncio.CancelledError:
                pass
            self.flush_task = None

        # Flush remaining logs
        await self._flush_buffer()

        if self.session:
            await self.session.close()
            self.session = None

    async def _test_connection(self):
        """Test connection to Elasticsearch."""
        if not self.session:
            return

        for host in self.hosts:
            try:
                async with self.session.get(f"http://{host}/_cluster/health", timeout=5) as response:
                    if response.status == 200:
                        health = await response.json()
                        self.logger.info(f"Connected to Elasticsearch at {host}, status: {health.get('status')}")
                        return
            except Exception as e:
                self.logger.warning(f"Failed to connect to Elasticsearch at {host}: {e}")

        self.logger.error("Failed to connect to any Elasticsearch host")

    async def send_log(self, log_entry: LogEntry):
        """Send log entry to buffer for batch processing."""
        self.buffer.append(log_entry)

        # Flush if buffer is full
        if len(self.buffer) >= self.batch_size:
            await self._flush_buffer()

    async def _flush_periodically(self):
        """Periodically flush the log buffer."""
        while True:
            try:
                await asyncio.sleep(self.flush_interval)
                await self._flush_buffer()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in periodic flush: {e}")

    async def _flush_buffer(self):
        """Flush buffered logs to Elasticsearch."""
        if not self.buffer or not self.session:
            return

        # Get batch of logs
        batch = []
        while self.buffer and len(batch) < self.batch_size:
            batch.append(self.buffer.popleft())

        if not batch:
            return

        # Group by index
        index_groups = {}
        for log_entry in batch:
            timestamp = datetime.fromisoformat(log_entry.timestamp.replace('Z', '+00:00'))
            index_name = timestamp.strftime(self.index_pattern)

            if index_name not in index_groups:
                index_groups[index_name] = []
            index_groups[index_name].append(log_entry)

        # Send to Elasticsearch
        for index_name, logs in index_groups.items():
            await self._send_bulk(index_name, logs)

    async def _send_bulk(self, index_name: str, logs: List[LogEntry]):
        """Send logs to Elasticsearch using bulk API."""
        if not self.session:
            return

        # Build bulk request body
        bulk_body = []
        for log_entry in logs:
            # Index action
            bulk_body.append(json.dumps({
                "index": {
                    "_index": index_name,
                    "_type": "_doc"
                }
            }))
            # Document
            bulk_body.append(json.dumps(asdict(log_entry), default=str))

        bulk_data = "\n".join(bulk_body) + "\n"

        # Send to first available host
        for host in self.hosts:
            try:
                url = f"http://{host}/_bulk"
                headers = {"Content-Type": "application/x-ndjson"}

                async with self.session.post(url, data=bulk_data, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("errors"):
                            self.logger.warning(f"Some logs failed to index: {result}")
                        else:
                            self.logger.debug(f"Successfully indexed {len(logs)} logs to {index_name}")
                        return
                    else:
                        self.logger.error(f"Failed to send logs to {host}: HTTP {response.status}")
            except Exception as e:
                self.logger.error(f"Error sending logs to {host}: {e}")

        # If all hosts failed, put logs back in buffer
        for log_entry in reversed(logs):
            self.buffer.appendleft(log_entry)


class LogAggregator:
    """Main log aggregation service."""

    def __init__(self):
        self.logger = get_logger(__name__, "log_aggregation")
        self.config_loader = get_config_loader()
        self.elasticsearch_handler: Optional[ElasticsearchLogHandler] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.running = False

    async def start(self):
        """Start the log aggregation service."""
        if self.running:
            return

        self.logger.info("Starting log aggregation service")

        # Initialize HTTP session
        self.session = aiohttp.ClientSession()

        # Initialize Elasticsearch handler if enabled
        config = self.config_loader.config
        if config and 'elasticsearch' in config.handlers:
            es_handler = config.handlers['elasticsearch']
            if es_handler.enabled:
                es_config = es_handler.config
                hosts = es_config.get('hosts', ['localhost:9200'])
                index_pattern = es_config.get('index_pattern', 'investment-platform-logs-%Y.%m.%d')

                self.elasticsearch_handler = ElasticsearchLogHandler(hosts, index_pattern)
                await self.elasticsearch_handler.start()

        self.running = True
        self.logger.info("Log aggregation service started")

    async def stop(self):
        """Stop the log aggregation service."""
        if not self.running:
            return

        self.logger.info("Stopping log aggregation service")

        if self.elasticsearch_handler:
            await self.elasticsearch_handler.stop()
            self.elasticsearch_handler = None

        if self.session:
            await self.session.close()
            self.session = None

        self.running = False
        self.logger.info("Log aggregation service stopped")

    async def process_log(self, log_entry: LogEntry):
        """Process a log entry through all configured handlers."""
        if not self.running:
            return

        try:
            # Send to Elasticsearch if configured
            if self.elasticsearch_handler:
                await self.elasticsearch_handler.send_log(log_entry)

        except Exception as e:
            self.logger.error(f"Error processing log entry: {e}")

    async def query_logs(self, query: LogQuery) -> List[Dict[str, Any]]:
        """Query logs from Elasticsearch."""
        if not self.elasticsearch_handler or not self.session:
            return []

        # Build Elasticsearch query
        es_query = self._build_es_query(query)

        # Determine index pattern
        if query.start_time and query.end_time:
            # Generate index names for the time range
            indices = self._generate_index_names(query.start_time, query.end_time)
        else:
            # Use wildcard to search all indices
            indices = [self.elasticsearch_handler.index_pattern.replace('%Y.%m.%d', '*')]

        # Search each host
        for host in self.elasticsearch_handler.hosts:
            try:
                index_list = ",".join(indices)
                url = f"http://{host}/{index_list}/_search"

                async with self.session.post(url, json=es_query, timeout=30) as response:
                    if response.status == 200:
                        result = await response.json()
                        hits = result.get('hits', {}).get('hits', [])
                        return [hit['_source'] for hit in hits]
                    else:
                        self.logger.error(f"Query failed on {host}: HTTP {response.status}")
            except Exception as e:
                self.logger.error(f"Error querying {host}: {e}")

        return []

    def _build_es_query(self, query: LogQuery) -> Dict[str, Any]:
        """Build Elasticsearch query from LogQuery."""
        must_clauses = []

        # Time range
        if query.start_time or query.end_time:
            time_range = {}
            if query.start_time:
                time_range['gte'] = query.start_time.isoformat()
            if query.end_time:
                time_range['lte'] = query.end_time.isoformat()

            must_clauses.append({
                "range": {
                    "timestamp": time_range
                }
            })

        # Log level
        if query.level:
            must_clauses.append({
                "term": {
                    "level": query.level
                }
            })

        # Component
        if query.component:
            must_clauses.append({
                "term": {
                    "component": query.component
                }
            })

        # Logger name
        if query.logger_name:
            must_clauses.append({
                "term": {
                    "logger_name": query.logger_name
                }
            })

        # Message contains
        if query.message_contains:
            must_clauses.append({
                "match": {
                    "message": query.message_contains
                }
            })

        # Build complete query
        es_query = {
            "query": {
                "bool": {
                    "must": must_clauses
                }
            } if must_clauses else {"match_all": {}},
            "sort": [
                {
                    "timestamp": {
                        "order": query.sort_order
                    }
                }
            ],
            "from": query.offset,
            "size": query.limit
        }

        return es_query

    def _generate_index_names(self, start_time: datetime, end_time: datetime) -> List[str]:
        """Generate list of index names for a time range."""
        if not self.elasticsearch_handler:
            return []

        indices = []
        current = start_time.replace(hour=0, minute=0, second=0, microsecond=0)

        while current <= end_time:
            index_name = current.strftime(self.elasticsearch_handler.index_pattern)
            indices.append(index_name)
            current += timedelta(days=1)

        return indices

    async def get_log_statistics(self,
                                start_time: Optional[datetime] = None,
                                end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Get log statistics from Elasticsearch."""
        if not self.elasticsearch_handler or not self.session:
            return {}

        # Build aggregation query
        agg_query = {
            "query": {
                "range": {
                    "timestamp": {
                        "gte": start_time.isoformat() if start_time else "now-1d",
                        "lte": end_time.isoformat() if end_time else "now"
                    }
                }
            },
            "aggs": {
                "levels": {
                    "terms": {
                        "field": "level",
                        "size": 10
                    }
                },
                "components": {
                    "terms": {
                        "field": "component",
                        "size": 20
                    }
                },
                "timeline": {
                    "date_histogram": {
                        "field": "timestamp",
                        "calendar_interval": "1h"
                    }
                }
            },
            "size": 0
        }

        # Query first available host
        for host in self.elasticsearch_handler.hosts:
            try:
                url = f"http://{host}/_search"
                async with self.session.post(url, json=agg_query, timeout=30) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "total": result.get('hits', {}).get('total', {}).get('value', 0),
                            "levels": result.get('aggregations', {}).get('levels', {}).get('buckets', []),
                            "components": result.get('aggregations', {}).get('components', {}).get('buckets', []),
                            "timeline": result.get('aggregations', {}).get('timeline', {}).get('buckets', [])
                        }
            except Exception as e:
                self.logger.error(f"Error getting statistics from {host}: {e}")

        return {}


# Global aggregator instance
_log_aggregator = None


async def get_log_aggregator() -> LogAggregator:
    """Get global log aggregator instance."""
    global _log_aggregator
    if _log_aggregator is None:
        _log_aggregator = LogAggregator()
        await _log_aggregator.start()
    return _log_aggregator


async def shutdown_log_aggregator():
    """Shutdown global log aggregator."""
    global _log_aggregator
    if _log_aggregator:
        await _log_aggregator.stop()
        _log_aggregator = None


if __name__ == "__main__":
    import asyncio
    from datetime import datetime, timezone

    async def test_aggregation():
        """Test log aggregation functionality."""
        aggregator = await get_log_aggregator()

        # Create test log entry
        test_log = LogEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            level="INFO",
            logger_name="test",
            message="Test log message",
            module="test_module",
            function="test_function",
            line_number=1,
            thread_id=12345,
            process_id=67890,
            hostname="test-host",
            component="test-component"
        )

        # Process log
        await aggregator.process_log(test_log)

        # Wait for processing
        await asyncio.sleep(2)

        # Query logs
        query = LogQuery(
            component="test-component",
            limit=10
        )

        results = await aggregator.query_logs(query)
        print(f"Found {len(results)} log entries")

        # Get statistics
        stats = await aggregator.get_log_statistics()
        print(f"Statistics: {stats}")

        await shutdown_log_aggregator()

    asyncio.run(test_aggregation())
