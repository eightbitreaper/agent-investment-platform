#!/usr/bin/env python3
"""
Docker Container Health Monitoring Script
Monitors all Docker containers for health, status, and resource usage.
"""

import json
import subprocess
import time
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import requests


class DockerHealthMonitor:
    """Monitor Docker container health and status."""

    def __init__(self):
        self.required_containers = {
            # Core Platform Services
            'agent-investment-platform': {'port': 8000, 'health_endpoint': '/health'},

            # Data Layer
            'postgres-investment': {'port': 5432, 'health_check': 'pg_isready'},
            'redis-investment': {'port': 6379, 'health_check': 'redis-cli ping'},
            'elasticsearch': {'port': 9200, 'health_endpoint': '/_cluster/health'},

            # MCP Servers
            'mcp-financial-server': {'port': 3000, 'health_endpoint': '/health'},
            'mcp-report-server': {'port': 3002, 'health_endpoint': '/health'},
            'mcp-stock-data-server': {'port': 3003, 'health_endpoint': '/health'},
            'mcp-analysis-server': {'port': 3004, 'health_endpoint': '/health'},

            # Monitoring Stack
            'logstash': {'port': 5000, 'service_type': 'logstash'},
            'kibana': {'port': 5601, 'health_endpoint': '/status'},
            'grafana': {'port': 3001, 'health_endpoint': '/api/health'},

            # AI Services
            'ollama-investment': {'port': 11434, 'health_endpoint': '/api/tags'},
            'ollama-webui': {'port': 8080, 'health_endpoint': '/health'},
        }

        self.alert_history = []
        self.container_status_history = {}

    def run_docker_command(self, command: List[str]) -> Tuple[bool, str]:
        """Run a docker command and return success status and output."""
        try:
            result = subprocess.run(
                ['docker'] + command,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout.strip()
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)

    def get_container_status(self) -> Dict[str, Dict]:
        """Get status of all containers."""
        success, output = self.run_docker_command(['ps', '-a', '--format', 'json'])
        if not success:
            return {}

        containers = {}
        for line in output.split('\n'):
            if line.strip():
                try:
                    container = json.loads(line)
                    containers[container['Names']] = {
                        'id': container['ID'],
                        'image': container['Image'],
                        'status': container['Status'],
                        'state': container['State'],
                        'ports': container.get('Ports', ''),
                        'created': container['CreatedAt']
                    }
                except json.JSONDecodeError:
                    continue

        return containers

    def check_container_health(self, container_name: str, config: Dict) -> Dict:
        """Check health of a specific container."""
        containers = self.get_container_status()

        health_result = {
            'container': container_name,
            'timestamp': datetime.now().isoformat(),
            'status': 'unknown',
            'issues': [],
            'healthy': False
        }

        # Check if container exists and is running
        if container_name not in containers:
            health_result['status'] = 'missing'
            health_result['issues'].append('Container does not exist')
            return health_result

        container = containers[container_name]
        health_result['container_state'] = container['state']
        health_result['container_status'] = container['status']

        # Check if container is running
        if container['state'] != 'running':
            health_result['status'] = 'stopped'
            health_result['issues'].append(f'Container is {container["state"]}')
            return health_result

        # Check port availability if specified
        if 'port' in config:
            port_healthy = self.check_port_health(config['port'])
            if not port_healthy:
                health_result['issues'].append(f'Port {config["port"]} not accessible')

        # Check health endpoint if specified
        if 'health_endpoint' in config:
            endpoint_healthy = self.check_health_endpoint(
                config['port'], config['health_endpoint']
            )
            if not endpoint_healthy:
                health_result['issues'].append(f'Health endpoint {config["health_endpoint"]} failed')
            else:
                health_result['healthy'] = True
                health_result['status'] = 'healthy'

        # If no specific health check, assume healthy if running
        if not health_result['issues'] and 'health_endpoint' not in config:
            health_result['healthy'] = True
            health_result['status'] = 'running'

        return health_result

    def check_port_health(self, port: int) -> bool:
        """Check if a port is accessible."""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return result == 0
        except Exception:
            return False

    def check_health_endpoint(self, port: int, endpoint: str) -> bool:
        """Check if a health endpoint responds correctly."""
        try:
            url = f"http://localhost:{port}{endpoint}"
            response = requests.get(url, timeout=10)
            return response.status_code == 200
        except Exception:
            return False

    def detect_port_conflicts(self) -> List[Dict]:
        """Detect port conflicts between containers."""
        conflicts = []
        port_usage = {}

        # Get actual port conflicts by checking netstat-like information
        try:
            success, output = self.run_docker_command(['ps', '--format', 'table {{.Names}}\t{{.Ports}}'])
            if not success:
                return conflicts

            lines = output.split('\n')[1:]  # Skip header
            for line in lines:
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        name = parts[0].strip()
                        ports_str = parts[1].strip()

                        if ports_str and '->' in ports_str:
                            # Parse port mappings like "0.0.0.0:3000->3000/tcp, 0.0.0.0:3001->3001/tcp"
                            port_mappings = [p.strip() for p in ports_str.split(',')]
                            for mapping in port_mappings:
                                if '->' in mapping:
                                    # Extract external port (before ->)
                                    external_part = mapping.split('->')[0]
                                    if ':' in external_part:
                                        external_port = external_part.split(':')[-1]

                                        if external_port in port_usage and port_usage[external_port] != name:
                                            conflicts.append({
                                                'port': external_port,
                                                'containers': [port_usage[external_port], name],
                                                'issue': 'Port conflict detected'
                                            })
                                        else:
                                            port_usage[external_port] = name
        except Exception as e:
            # If port conflict detection fails, don't crash the monitoring
            pass

        return conflicts

    def get_resource_usage(self) -> Dict[str, Dict]:
        """Get resource usage for all containers."""
        success, output = self.run_docker_command(['stats', '--no-stream', '--format', 'json'])
        if not success:
            return {}

        resources = {}
        for line in output.split('\n'):
            if line.strip():
                try:
                    stats = json.loads(line)
                    resources[stats['Name']] = {
                        'cpu_percent': stats['CPUPerc'].rstrip('%'),
                        'memory_usage': stats['MemUsage'],
                        'memory_percent': stats['MemPerc'].rstrip('%'),
                        'network_io': stats['NetIO'],
                        'block_io': stats['BlockIO']
                    }
                except json.JSONDecodeError:
                    continue

        return resources

    def generate_alert(self, alert_type: str, message: str, severity: str = 'warning'):
        """Generate an alert for container issues."""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'type': alert_type,
            'message': message,
            'severity': severity
        }

        self.alert_history.append(alert)

        # Print alert to console
        severity_symbol = {
            'info': '[INFO]',
            'warning': '[WARN]',
            'error': '[ERROR]',
            'critical': '[CRITICAL]'
        }.get(severity, '[ALERT]')

        print(f"{severity_symbol} {alert['timestamp']}: {message}")

    def monitor_all_containers(self) -> Dict:
        """Monitor all required containers and return health report."""
        print(f"\n=== Docker Container Health Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")

        health_report = {
            'timestamp': datetime.now().isoformat(),
            'total_containers': len(self.required_containers),
            'healthy_containers': 0,
            'unhealthy_containers': 0,
            'missing_containers': 0,
            'container_health': {},
            'port_conflicts': [],
            'resource_usage': {},
            'alerts': []
        }

        # Check individual container health
        for container_name, config in self.required_containers.items():
            health_result = self.check_container_health(container_name, config)
            health_report['container_health'][container_name] = health_result

            if health_result['healthy']:
                health_report['healthy_containers'] += 1
                print(f"  [PASS] {container_name}: {health_result['status']}")
            elif health_result['status'] == 'missing':
                health_report['missing_containers'] += 1
                print(f"  [MISS] {container_name}: {health_result['status']}")
                self.generate_alert(
                    'container_missing',
                    f"Required container '{container_name}' is missing",
                    'error'
                )
            else:
                health_report['unhealthy_containers'] += 1
                print(f"  [FAIL] {container_name}: {health_result['status']} - {', '.join(health_result['issues'])}")
                self.generate_alert(
                    'container_unhealthy',
                    f"Container '{container_name}' is unhealthy: {', '.join(health_result['issues'])}",
                    'warning'
                )

        # Check for port conflicts
        port_conflicts = self.detect_port_conflicts()
        health_report['port_conflicts'] = port_conflicts

        if port_conflicts:
            print(f"\n  [WARN] Port conflicts detected:")
            for conflict in port_conflicts:
                print(f"    Port {conflict['port']}: {', '.join(conflict['containers'])}")
                self.generate_alert(
                    'port_conflict',
                    f"Port conflict on {conflict['port']}: {', '.join(conflict['containers'])}",
                    'warning'
                )

        # Get resource usage
        resource_usage = self.get_resource_usage()
        health_report['resource_usage'] = resource_usage

        # Check for high resource usage
        for container, resources in resource_usage.items():
            try:
                cpu_percent = float(resources['cpu_percent'])
                mem_percent = float(resources['memory_percent'])

                if cpu_percent > 80:
                    self.generate_alert(
                        'high_cpu',
                        f"Container '{container}' CPU usage is {cpu_percent}%",
                        'warning'
                    )

                if mem_percent > 80:
                    self.generate_alert(
                        'high_memory',
                        f"Container '{container}' memory usage is {mem_percent}%",
                        'warning'
                    )
            except (ValueError, KeyError):
                continue

        health_report['alerts'] = self.alert_history.copy()

        # Print summary
        print(f"\n=== Summary ===")
        print(f"Total Containers: {health_report['total_containers']}")
        print(f"Healthy: {health_report['healthy_containers']}")
        print(f"Unhealthy: {health_report['unhealthy_containers']}")
        print(f"Missing: {health_report['missing_containers']}")
        print(f"Alerts Generated: {len(self.alert_history)}")

        success_rate = (health_report['healthy_containers'] / health_report['total_containers']) * 100
        print(f"Health Success Rate: {success_rate:.1f}%")

        if success_rate < 100:
            print(f"\n[WARNING] Not all containers are healthy! Manual intervention may be required.")
            return health_report

        print(f"\n[SUCCESS] All containers are healthy!")
        return health_report

    def save_health_report(self, report: Dict, filename: Optional[str] = None):
        """Save health report to JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"docker_health_report_{timestamp}.json"

        try:
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\nHealth report saved to: {filename}")
        except Exception as e:
            print(f"\nFailed to save health report: {e}")


def main():
    """Main monitoring function."""
    monitor = DockerHealthMonitor()

    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Monitor Docker container health')
    parser.add_argument('--continuous', '-c', action='store_true',
                       help='Run continuous monitoring (every 60 seconds)')
    parser.add_argument('--interval', '-i', type=int, default=60,
                       help='Monitoring interval in seconds (default: 60)')
    parser.add_argument('--save-report', '-s', action='store_true',
                       help='Save health report to JSON file')

    args = parser.parse_args()

    try:
        if args.continuous:
            print(f"Starting continuous Docker health monitoring (interval: {args.interval}s)")
            print("Press Ctrl+C to stop monitoring")

            while True:
                report = monitor.monitor_all_containers()

                if args.save_report:
                    monitor.save_health_report(report)

                # Wait for next check
                time.sleep(args.interval)
        else:
            # Single health check
            report = monitor.monitor_all_containers()

            if args.save_report:
                monitor.save_health_report(report)

            # Exit with appropriate code
            if report['unhealthy_containers'] > 0 or report['missing_containers'] > 0:
                sys.exit(1)
            else:
                sys.exit(0)

    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nMonitoring failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
