#!/usr/bin/env python3
"""
MCP Server Monitoring Service

This service monitors the health, performance, and availability of all MCP servers.
"""

import os
import time
import threading
import requests
import psutil
from datetime import datetime
from pathlib import Path
import json
import smtplib
from email.mime.text import MIMEText
from typing import Dict, List, Optional
import dotenv
import logging

dotenv.load_dotenv()


class MCPServerMonitor:
    """Monitors MCP servers for health, performance, and availability."""
    
    def __init__(self, manager):
        # Load monitoring configuration
        self.monitoring_enabled = os.getenv("MONITORING_ENABLED", "true").lower() == "true"
        self.monitoring_interval = int(os.getenv("MONITORING_INTERVAL", "10"))
        self.health_check_timeout = int(os.getenv("HEALTH_CHECK_TIMEOUT", "5"))
        self.cpu_threshold = int(os.getenv("CPU_THRESHOLD", "80"))
        self.memory_threshold = int(os.getenv("MEMORY_THRESHOLD", "85"))
        self.response_time_threshold = int(os.getenv("RESPONSE_TIME_THRESHOLD", "5000"))
        self.alert_on_failure = os.getenv("ALERT_ON_FAILURE", "true").lower() == "true"
        
        self.manager = manager
        self.monitoring_thread = None
        self.is_monitoring = False
        self.metrics_history = {}
        
        # Get logger from the centralized logging system
        from logs.log_manager import get_log_manager
        self.log_manager = get_log_manager()
        self.logger = self.log_manager.get_monitoring_logger()
        
        # Create monitoring data directory
        self.data_dir = Path("monitoring") / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def start_monitoring(self):
        """Start the monitoring service."""
        if not self.monitoring_enabled:
            self.logger.info("Monitoring is disabled by configuration")
            return
            
        if self.is_monitoring:
            self.logger.info("Monitoring is already running")
            return
            
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        self.logger.info("Monitoring service started")

    def stop_monitoring(self):
        """Stop the monitoring service."""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2)
        self.logger.info("Monitoring service stopped")

    def _monitoring_loop(self):
        """Main monitoring loop that runs continuously."""
        while self.is_monitoring:
            try:
                self._check_all_servers()
                time.sleep(self.monitoring_interval)
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {str(e)}")
                time.sleep(self.monitoring_interval)

    def _check_all_servers(self):
        """Check the status of all servers."""
        for server_name, server_config in self.manager.servers.items():
            try:
                self._check_single_server(server_name, server_config)
            except Exception as e:
                self.logger.error(f"Error checking server {server_name}: {str(e)}")

    def _check_single_server(self, server_name: str, server_config: Dict):
        """Check the health and performance of a single server."""
        # Check if the server is running
        pids = self.manager.load_pids()
        pid = pids.get(server_name)
        
        server_status = {
            'timestamp': datetime.now().isoformat(),
            'server_name': server_name,
            'port': server_config['port'],
            'host': server_config['host'],
            'is_running': False,
            'cpu_percent': 0,
            'memory_percent': 0,
            'response_time': None,
            'health_status': 'unknown',
            'alerts': []
        }
        
        if pid:
            try:
                process = psutil.Process(pid)
                if process.is_running():
                    server_status['is_running'] = True
                    server_status['cpu_percent'] = process.cpu_percent()
                    server_status['memory_percent'] = process.memory_percent()
                    
                    # Check CPU usage threshold
                    if server_status['cpu_percent'] > self.cpu_threshold:
                        alert_msg = f"High CPU usage: {server_status['cpu_percent']:.1f}% > {self.cpu_threshold}%"
                        server_status['alerts'].append(alert_msg)
                        self.logger.warning(f"Server {server_name}: {alert_msg}")
                    
                    # Check memory usage threshold
                    if server_status['memory_percent'] > self.memory_threshold:
                        alert_msg = f"High memory usage: {server_status['memory_percent']:.1f}% > {self.memory_threshold}%"
                        server_status['alerts'].append(alert_msg)
                        self.logger.warning(f"Server {server_name}: {alert_msg}")
                    
                    # Check server health endpoint if available
                    health_status, response_time = self._check_server_health(
                        server_config['host'], 
                        server_config['port']
                    )
                    server_status['health_status'] = health_status
                    server_status['response_time'] = response_time
                    
                    if health_status != 'healthy':
                        alert_msg = f"Health check failed: {health_status}"
                        server_status['alerts'].append(alert_msg)
                        self.logger.warning(f"Server {server_name}: {alert_msg}")
                    
                    if response_time and response_time > self.response_time_threshold:
                        alert_msg = f"High response time: {response_time}ms > {self.response_time_threshold}ms"
                        server_status['alerts'].append(alert_msg)
                        self.logger.warning(f"Server {server_name}: {alert_msg}")
                        
                else:
                    server_status['health_status'] = 'stopped'
                    alert_msg = f"Process is not running (PID: {pid})"
                    server_status['alerts'].append(alert_msg)
                    self.logger.warning(f"Server {server_name}: {alert_msg}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                server_status['health_status'] = 'process_missing'
                alert_msg = f"Process not found (PID: {pid})"
                server_status['alerts'].append(alert_msg)
                self.logger.warning(f"Server {server_name}: {alert_msg}")
        else:
            server_status['health_status'] = 'no_pid'
            alert_msg = f"No PID found for server"
            server_status['alerts'].append(alert_msg)
            self.logger.warning(f"Server {server_name}: {alert_msg}")
        
        # Store metrics
        if server_name not in self.metrics_history:
            self.metrics_history[server_name] = []
        self.metrics_history[server_name].append(server_status)
        
        # Keep only last 1000 entries per server to prevent memory issues
        if len(self.metrics_history[server_name]) > 1000:
            self.metrics_history[server_name] = self.metrics_history[server_name][-1000:]
        
        # Save metrics to file
        self._save_metrics(server_name, server_status)
        
        # Send alerts if needed
        if server_status['alerts'] and self.alert_on_failure:
            self._send_alerts(server_name, server_status['alerts'])

    def _check_server_health(self, host: str, port: int) -> tuple:
        """Check the health of a server via its health endpoint."""
        try:
            start_time = time.time()
            response = requests.get(f"http://{host}:{port}/health", timeout=self.health_check_timeout)
            response_time = int((time.time() - start_time) * 1000)  # Convert to milliseconds
            
            if response.status_code == 200:
                return 'healthy', response_time
            else:
                return f'unhealthy (status: {response.status_code})', response_time
        except requests.exceptions.Timeout:
            return 'timeout', self.health_check_timeout * 1000
        except requests.exceptions.ConnectionError:
            return 'connection_error', None
        except Exception as e:
            return f'error: {str(e)}', None

    def _save_metrics(self, server_name: str, metrics: Dict):
        """Save metrics to a JSON file."""
        metrics_file = self.data_dir / f"{server_name}_metrics.json"
        
        # Load existing metrics
        existing_metrics = []
        if metrics_file.exists():
            try:
                with open(metrics_file, 'r') as f:
                    existing_metrics = json.load(f)
            except:
                existing_metrics = []
        
        # Append new metrics
        existing_metrics.append(metrics)
        
        # Keep only last 1000 entries to prevent file bloat
        if len(existing_metrics) > 1000:
            existing_metrics = existing_metrics[-1000:]
        
        # Save back to file
        with open(metrics_file, 'w') as f:
            json.dump(existing_metrics, f, indent=2)

    def _send_alerts(self, server_name: str, alerts: List[str]):
        """Send alerts for issues found."""
        alert_msg = f"Alerts for server {server_name}:\n" + "\n".join(f"- {alert}" for alert in alerts)
        self.logger.warning(alert_msg)
        
        # In a full implementation, you would send emails, webhooks, etc.
        # For now, just log the alerts
        # TODO: Implement email and webhook notifications

    def get_server_metrics(self, server_name: str) -> List[Dict]:
        """Get metrics history for a specific server."""
        return self.metrics_history.get(server_name, [])

    def get_all_metrics(self) -> Dict[str, List[Dict]]:
        """Get metrics history for all servers."""
        return self.metrics_history

    def get_current_status(self) -> Dict[str, Dict]:
        """Get current status of all servers."""
        current_status = {}
        for server_name in self.manager.servers.keys():
            if self.metrics_history.get(server_name):
                current_status[server_name] = self.metrics_history[server_name][-1]
            else:
                current_status[server_name] = {
                    'server_name': server_name,
                    'status': 'unknown',
                    'timestamp': datetime.now().isoformat()
                }
        return current_status

    def export_metrics(self, format_type: str = "json") -> str:
        """Export metrics in the specified format."""
        if format_type == "json":
            export_file = self.data_dir / f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(export_file, 'w') as f:
                json.dump(self.metrics_history, f, indent=2)
            return str(export_file)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")