#!/usr/bin/env python3
"""
Professional MCP Server Manager

Centralized control script to start, stop, monitor, and manage all MCP servers
in the agent-mcp-management-system project with comprehensive features.
"""

import os
import sys
import subprocess
import signal
import time
import argparse
import json
import atexit
from pathlib import Path
from typing import List, Dict, Optional, Any
import psutil  # type: ignore
import dotenv
import socket
import threading
from datetime import datetime
from contextlib import contextmanager

from monitoring.monitor_service import MCPServerMonitor


class MCPServerManager:
    """Professional MCP server manager with comprehensive lifecycle management."""
    
    def __init__(self):
        # Load environment variables from .env file
        dotenv.load_dotenv()
        
        self.project_root = Path(__file__).parent.resolve()
        self.mcps_dir = self.project_root / "mcps"
        self.logs_dir = self.project_root / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        # Load configuration from environment variables
        self.host = os.getenv("FASTMCP_HOST", "127.0.0.1")
        self.base_port = int(os.getenv("FASTMCP_BASE_PORT", "8000"))
        self.debug = os.getenv("FASTMCP_DEBUG", "false").lower() == "true"
        self.start_on_boot = os.getenv("START_ON_BOOT", "false").lower() == "true"
        self.shutdown_on_exit = os.getenv("SHUTDOWN_ON_EXIT", "true").lower() == "true"
        self.health_check_enabled = os.getenv("HEALTH_CHECK_ENABLED", "true").lower() == "true"
        self.health_check_interval = int(os.getenv("HEALTH_CHECK_INTERVAL", "30"))
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.log_to_file = os.getenv("LOG_TO_FILE", "true").lower() == "true"
        self.server_startup_timeout = int(os.getenv("SERVER_STARTUP_TIMEOUT", "60"))
        self.server_shutdown_timeout = int(os.getenv("SERVER_SHUTDOWN_TIMEOUT", "30"))
        self.monitor_interval = int(os.getenv("SERVER_MONITOR_INTERVAL", "10"))
        
        # Docker-specific settings
        self.docker_mode = os.getenv("DOCKER_MODE", "false").lower() == "true"
        self.container_prefix = os.getenv("CONTAINER_PREFIX", "agent-mcp")
        self.network_name = os.getenv("NETWORK_NAME", "agent-mcp-net")
        self.compose_file = os.getenv("COMPOSE_FILE", "docker-compose.yml")
        self.container_memory_limit = os.getenv("CONTAINER_MEMORY_LIMIT", "1g")
        self.container_cpu_limit = os.getenv("CONTAINER_CPU_LIMIT", "1.0")
        
        # Initialize logging
        from logs.log_manager import get_log_manager
        self.log_manager = get_log_manager()
        self.logger = self.log_manager.get_manager_logger()
        
        # Initialize monitoring
        self.monitor = MCPServerMonitor(self)
        
        # Initialize servers and configuration
        self.servers = self._discover_servers()
        self.pid_file = self.logs_dir / "mcp_manager_pids.json"
        
        # Register cleanup handlers
        atexit.register(self._cleanup_on_exit)
        
        # Handle signals for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Start services based on configuration
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize all services based on configuration."""
        # Start servers on boot if configured
        if self.start_on_boot and not self.docker_mode:
            self.logger.info("Starting servers on boot...")
            self.start_all()
            
        # Start monitoring if enabled
        if os.getenv("MONITORING_ENABLED", "true").lower() == "true":
            self.monitor.start_monitoring()
            self.logger.info("Monitoring service started")
        
        # Start log cleanup daemon
        self.log_manager.start_log_cleanup_daemon()
        self.logger.info("Log cleanup daemon started")
        
        self.logger.info(f"MCP Manager initialized in {self.environment} environment")
    
    def _discover_servers(self) -> Dict[str, Dict]:
        """Dynamically discover all MCP servers in the mcps directory."""
        servers = {}
        
        # Default port to start from
        base_port = int(os.getenv("FASTMCP_BASE_PORT", "8000"))
        
        if not self.mcps_dir.exists():
            self.logger.warning(f"MCPs directory does not exist: {self.mcps_dir}")
            return servers
            
        # Get all subdirectories in mcps directory
        for item in self.mcps_dir.iterdir():
            if item.is_dir():
                # Use the directory name as the server name
                server_name = item.name
                
                # Skip if it's not an MCP server directory (basic check)
                server_script = item / "server.py"
                if not server_script.exists():
                    self.logger.debug(f"Skipping {server_name} - no server.py found")
                    continue  # Not an MCP server directory
                
                # Create server configuration
                port = base_port + len(servers)  # Assign ports sequentially starting from base_port
                # Format server name more cleanly by handling common suffixes
                clean_name = server_name.replace('-mcp-server', '').replace('-', ' ').title()
                servers[server_name] = {
                    "name": f"{clean_name} Server",
                    "dir": item,
                    "script": "server.py",
                    "port": port,
                    "host": os.getenv("FASTMCP_HOST", "127.0.0.1"),
                    "process": None,
                    "log_file": self.logs_dir / f"{server_name}.log",
                    "status": "stopped",
                    "startup_time": None
                }
        
        self.logger.info(f"Discovered {len(servers)} MCP servers")
        return servers
    
    def _signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown."""
        self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self._cleanup_on_exit()
        sys.exit(0)
    
    def _cleanup_on_exit(self):
        """Clean up resources on exit if configured."""
        if self.shutdown_on_exit:
            self.logger.info("Shutting down all servers...")
            self.stop_all()
            self.logger.info("All servers stopped")
        
        # Stop monitoring
        try:
            self.monitor.stop_monitoring()
            self.logger.info("Monitoring service stopped")
        except Exception as e:
            self.logger.error(f"Error stopping monitoring: {e}")
        
    def load_pids(self) -> Dict[str, int]:
        """Load stored PIDs from file."""
        try:
            if self.pid_file.exists():
                with open(self.pid_file, 'r') as f:
                    content = json.load(f)
                    # Ensure all values are integers
                    return {k: int(v) for k, v in content.items()}
        except (json.JSONDecodeError, ValueError, IOError) as e:
            self.logger.error(f"Error loading PIDs from file: {e}")
        return {}
    
    def save_pids(self, pids: Dict[str, int]) -> None:
        """Save PIDs to file."""
        try:
            with open(self.pid_file, 'w') as f:
                json.dump(pids, f, indent=2)
        except IOError as e:
            self.logger.error(f"Error saving PIDs to file: {e}")
    
    def is_port_in_use(self, port: int) -> bool:
        """Check if a port is currently in use."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                return False
            except OSError:
                return True
    
    def check_server_health(self, server_name: str) -> Dict[str, Any]:
        """Check the health of a specific server."""
        if server_name not in self.servers:
            return {"status": "unknown", "message": f"Server {server_name} not found"}
        
        server = self.servers[server_name]
        pids = self.load_pids()
        pid = pids.get(server_name)
        
        if not pid:
            return {"status": "stopped", "message": "No PID found"}
        
        try:
            process = psutil.Process(pid)
            if process.is_running():
                return {
                    "status": "running",
                    "pid": pid,
                    "cpu_percent": process.cpu_percent(),
                    "memory_percent": process.memory_percent(),
                    "uptime_seconds": (datetime.now() - process.create_time()).total_seconds()
                }
            else:
                return {"status": "stopped", "message": "Process is not running"}
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return {"status": "unknown", "message": "Process access denied or not found"}
    
    def start_server(self, server_name: str) -> bool:
        """Start a specific MCP server."""
        if server_name not in self.servers:
            error_msg = f"Server '{server_name}' not found"
            self.logger.error(error_msg)
            print(error_msg)
            return False
            
        server = self.servers[server_name]
        server_dir = server["dir"]
        script = server["script"]
        
        # Check if server directory exists
        if not server_dir.exists():
            error_msg = f"Server directory '{server_dir}' does not exist"
            self.logger.error(error_msg)
            print(error_msg)
            return False
            
        # Check if script exists
        script_path = server_dir / script
        if not script_path.exists():
            error_msg = f"Server script '{script_path}' does not exist"
            self.logger.error(error_msg)
            print(error_msg)
            return False
        
        # Check if server is already running
        pids = self.load_pids()
        existing_pid = pids.get(server_name)
        if existing_pid:
            try:
                existing_process = psutil.Process(existing_pid)
                if existing_process.is_running():
                    warning_msg = f"Server {server_name} is already running with PID {existing_pid}"
                    self.logger.warning(warning_msg)
                    print(warning_msg)
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass  # Process doesn't exist, continue with start
        
        # Check if port is available
        if self.is_port_in_use(server["port"]):
            warning_msg = f"Port {server['port']} is already in use"
            self.logger.warning(warning_msg)
            print(warning_msg)
            
        # If in Docker mode, handle differently
        if self.docker_mode:
            return self._start_server_docker(server_name)
            
        # Prepare environment with server-specific configurations
        env = os.environ.copy()
        env["FASTMCP_HOST"] = server["host"]
        env["FASTMCP_PORT"] = str(server["port"])
        
        # Start the server process
        try:
            # Get a dedicated logger for this server
            server_logger = self.log_manager.get_server_logger(server_name)
            start_time = datetime.now()
            server_logger.info(f"Starting {server['name']} on {server['host']}:{server['port']}")
            
            # Only open log file if logging to file is enabled
            if self.log_to_file:
                log_file = open(server["log_file"], "a")
                stdout_target = log_file
                stderr_target = log_file
            else:
                stdout_target = subprocess.PIPE
                stderr_target = subprocess.PIPE
            
            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                stdout=stdout_target,
                stderr=stderr_target,
                cwd=str(server_dir),
                env=env,
                preexec_fn=os.setsid  # Create new process group
            )
            
            server["process"] = process
            
            # Wait for the process to start properly
            max_wait = self.server_startup_timeout
            waited = 0
            while waited < max_wait and process.poll() is None:
                # Check if the process is actually listening on the expected port
                if self._is_port_listening(server["host"], server["port"]):
                    break
                time.sleep(0.5)
                waited += 0.5
            
            # Check if process terminated early
            if process.poll() is not None:
                error_msg = f"Server {server['name']} terminated during startup (exit code: {process.returncode})"
                self.logger.error(error_msg)
                server_logger.error(error_msg)
                if self.log_to_file and 'log_file' in locals():
                    log_file.close()
                return False
            
            # Verify the port is actually listening
            if not self._is_port_listening(server["host"], server["port"]):
                warning_msg = f"Server {server['name']} started but port {server['port']} may not be accessible"
                self.logger.warning(warning_msg)
                server_logger.warning(warning_msg)
            
            # Save the PID
            pids = self.load_pids()
            pids[server_name] = process.pid
            self.save_pids(pids)
            
            server["status"] = "running"
            server["startup_time"] = start_time.isoformat()
            
            success_msg = f"Started {server['name']} on {server['host']}:{server['port']} (PID: {process.pid})"
            self.logger.info(success_msg)
            server_logger.info(success_msg)
            print(success_msg)
            return True
            
        except Exception as e:
            error_msg = f"Error starting {server['name']}: {str(e)}"
            self.logger.error(error_msg)
            if 'server_logger' in locals():
                server_logger.error(error_msg)
            print(error_msg)
            return False
    
    def _is_port_listening(self, host: str, port: int) -> bool:
        """Check if a specific port is actively listening."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex((host, port))
                return result == 0
        except:
            return False
    
    def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """Perform health check on all servers."""
        results = {}
        for server_name in self.servers:
            results[server_name] = self.check_server_health(server_name)
        return results
    
    def restart_server_graceful(self, server_name: str) -> bool:
        """Perform graceful restart of a server."""
        if server_name not in self.servers:
            error_msg = f"Server '{server_name}' not found"
            self.logger.error(error_msg)
            print(error_msg)
            return False
        
        # Check current health before restart
        health_before = self.check_server_health(server_name)
        self.logger.info(f"Health before restart of {server_name}: {health_before}")
        
        # Stop the server
        if not self.stop_server(server_name):
            self.logger.error(f"Failed to stop {server_name} before restart")
            return False
        
        # Wait before starting again
        time.sleep(2)
        
        # Start the server
        success = self.start_server(server_name)
        
        if success:
            health_after = self.check_server_health(server_name)
            self.logger.info(f"Health after restart of {server_name}: {health_after}")
        
        return success
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        try:
            import platform
            return {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "cpu_count": os.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available,
                "disk_usage": psutil.disk_usage('/').percent,
                "manager_uptime": getattr(self, '_start_time', datetime.now()).timestamp(),
                "running_servers": len([s for s in self.servers.values() if s.get('status') == 'running'])
            }
        except Exception as e:
            self.logger.error(f"Error getting system info: {e}")
            return {"error": str(e)}
    
    def export_config(self) -> Dict[str, Any]:
        """Export current configuration."""
        return {
            "host": self.host,
            "base_port": self.base_port,
            "debug": self.debug,
            "start_on_boot": self.start_on_boot,
            "shutdown_on_exit": self.shutdown_on_exit,
            "environment": self.environment,
            "log_to_file": self.log_to_file,
            "server_startup_timeout": self.server_startup_timeout,
            "server_shutdown_timeout": self.server_shutdown_timeout,
            "docker_mode": self.docker_mode,
            "container_prefix": self.container_prefix,
            "servers_count": len(self.servers)
        }
    
    def _start_server_docker(self, server_name: str) -> bool:
        """Start a server using Docker if in Docker mode."""
        # This would implement Docker-specific logic
        # For now, we'll just show a message
        print(f"Docker mode enabled - would start {server_name} in container")
        print(f"Configuration: memory={self.container_memory_limit}, cpu={self.container_cpu_limit}")
        # In a real implementation, this would start Docker containers
        return True
    
    def stop_server(self, server_name: str) -> bool:
        """Stop a specific MCP server."""
        if server_name not in self.servers:
            error_msg = f"Server '{server_name}' not found"
            self.logger.error(error_msg)
            print(error_msg)
            return False
            
        server = self.servers[server_name]
        
        # If in Docker mode, handle differently
        if self.docker_mode:
            return self._stop_server_docker(server_name)
        
        # Try to get PID from stored file
        pids = self.load_pids()
        pid = pids.get(server_name)
        
        if not pid:
            warning_msg = f"No PID found for {server['name']}"
            self.logger.warning(warning_msg)
            print(warning_msg)
            return False
        
        try:
            # Get server logger for this specific server
            server_logger = self.log_manager.get_server_logger(server_name)
            
            # Log the stop action
            self.logger.info(f"Stopping {server['name']} (PID: {pid})")
            server_logger.info(f"Stopping {server['name']} (PID: {pid})")
            
            # Kill the process group with the configured timeout
            os.killpg(os.getpgid(pid), signal.SIGTERM)
            
            # Wait for graceful shutdown with configured timeout
            shutdown_start = time.time()
            max_wait = self.server_shutdown_timeout
            
            # Check if process is still running
            while time.time() - shutdown_start < max_wait:
                try:
                    process = psutil.Process(pid)
                    if not process.is_running():
                        break
                    time.sleep(0.1)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    break  # Process is gone
            
            # Check if process is still running and force kill if necessary
            try:
                process = psutil.Process(pid)
                if process.is_running():
                    force_msg = f"Force killing {server['name']} (PID: {pid}) after {max_wait}s timeout"
                    self.logger.warning(force_msg)
                    server_logger.warning(force_msg)
                    os.killpg(os.getpgid(pid), signal.SIGKILL)
                    
                    # Wait a bit more to ensure process is killed
                    time.sleep(1)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass  # Process already terminated
            
            # Remove from stored PIDs
            if server_name in pids:
                del pids[server_name]
                self.save_pids(pids)
            
            server["status"] = "stopped"
            server["startup_time"] = None
            
            stopped_msg = f"Stopped {server['name']} (PID: {pid})"
            self.logger.info(stopped_msg)
            server_logger.info(stopped_msg)
            print(stopped_msg)
            return True
        except ProcessLookupError:
            not_found_msg = f"Process with PID {pid} not found for {server['name']}"
            self.logger.warning(not_found_msg)
            # Remove from stored PIDs anyway
            if server_name in pids:
                del pids[server_name]
                self.save_pids(pids)
            return True  # Consider it stopped
        except PermissionError:
            perm_error_msg = f"Permission denied stopping {server['name']} (PID: {pid})"
            self.logger.error(perm_error_msg)
            print(perm_error_msg)
            return False
        except Exception as e:
            error_msg = f"Error stopping {server['name']}: {str(e)}"
            self.logger.error(error_msg)
            print(error_msg)
            return False
    
    def _stop_server_docker(self, server_name: str) -> bool:
        """Stop a server running in Docker if in Docker mode."""
        print(f"Docker mode enabled - would stop {server_name} container")
        return True
    
    def start_all(self) -> None:
        """Start all MCP servers."""
        print("Starting all MCP servers...")
        for server_name in self.servers:
            self.start_server(server_name)
    
    def stop_all(self) -> None:
        """Stop all MCP servers."""
        print("Stopping all MCP servers...")
        for server_name in self.servers:
            self.stop_server(server_name)
    
    def restart_server(self, server_name: str) -> bool:
        """Restart a specific MCP server."""
        if self.stop_server(server_name):
            time.sleep(1)  # Brief pause before restart
            return self.start_server(server_name)
        else:
            return self.start_server(server_name)
    
    def restart_all(self) -> None:
        """Restart all MCP servers."""
        print("Restarting all MCP servers...")
        self.stop_all()
        time.sleep(2)  # Wait for all servers to stop
        self.start_all()
    
    def status(self) -> None:
        """Show status of all MCP servers."""
        print(f"MCP Server Status (Environment: {self.environment})")
        print("=" * 80)
        
        if not self.servers:
            print("No MCP servers found.")
            return
        
        pids = self.load_pids()
        running_count = 0
        
        for server_name, server in self.servers.items():
            pid = pids.get(server_name)
            
            if pid:
                try:
                    # Check if process is still running
                    process = psutil.Process(pid)
                    if process.is_running():
                        status = "RUNNING"
                        cpu_percent = process.cpu_percent()
                        memory_percent = process.memory_percent()
                        running_count += 1
                        uptime = (datetime.now() - datetime.fromtimestamp(process.create_time())).total_seconds()
                        uptime_str = self._format_uptime(uptime)
                    else:
                        status = "STOPPED"
                        cpu_percent = 0
                        memory_percent = 0
                        uptime_str = "N/A"
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    status = "STOPPED"
                    cpu_percent = 0
                    memory_percent = 0
                    uptime_str = "N/A"
                    # Clean up dead PID if needed
                    if server_name in pids:
                        del pids[server_name]
                        self.save_pids(pids)
            else:
                status = "STOPPED"
                cpu_percent = 0
                memory_percent = 0
                uptime_str = "N/A"
            
            print(f"{server['name']}")
            print(f"  ├── Status: {status}")
            print(f"  ├── Port: {server['port']}")
            print(f"  ├── Host: {server['host']}")
            if pid:
                print(f"  ├── PID: {pid}")
            print(f"  ├── Uptime: {uptime_str}")
            if status == "RUNNING":
                print(f"  ├── CPU: {cpu_percent:.2f}%")
                print(f"  └── Memory: {memory_percent:.2f}%")
            else:
                print(f"  └── Details: Process not running")
            print()
        
        print(f"Summary: {running_count}/{len(self.servers)} servers running")
        
        # Print configuration summary if in debug mode
        if self.debug:
            print("\nConfiguration:")
            print(f"  ├── Docker Mode: {self.docker_mode}")
            print(f"  ├── Base Port: {self.base_port}")
            print(f"  ├── Auto-start on boot: {self.start_on_boot}")
            print(f"  ├── Log to file: {self.log_to_file}")
            print(f"  ├── Health Check: {self.health_check_enabled}")
            print(f"  └── Environment: {self.environment}")
    
    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in seconds to a human-readable format."""
        if seconds < 0:
            return "N/A"
        
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if secs > 0 or not parts:
            parts.append(f"{secs}s")
        
        return " ".join(parts)
    
    def logs(self, server_name: str, lines: int = 20) -> None:
        """Display logs for a specific server."""
        if server_name not in self.servers:
            error_msg = f"Server '{server_name}' not found"
            print(error_msg)
            self.logger.warning(error_msg)
            return
            
        log_file = self.servers[server_name]["log_file"]
        
        if not log_file.exists():
            no_logs_msg = f"No logs found for {server_name}"
            print(no_logs_msg)
            self.logger.info(no_logs_msg)
            return
            
        # Read the last N lines from the log file
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines_list = f.readlines()
                
            # Get the last 'lines' lines
            last_lines = lines_list[-lines:] if len(lines_list) >= lines else lines_list
            
            print(f"Last {len(last_lines)} lines of {server_name} logs:")
            print("-" * 50)
            for line in last_lines:
                print(line.rstrip())
            
            self.logger.info(f"Displayed {len(last_lines)} log lines for {server_name}")
        except Exception as e:
            error_msg = f"Error reading logs for {server_name}: {str(e)}"
            print(error_msg)
            self.logger.error(error_msg)


def main():
    parser = argparse.ArgumentParser(
        description="Professional MCP Server Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s status                                   # Show status of all servers
  %(prog)s start meta-fastmcp-mcp-server           # Start a specific server
  %(prog)s stop-all                                # Stop all servers
  %(prog)s restart meta-fastmcp-mcp-server         # Restart a specific server
  %(prog)s logs meta-fastmcp-mcp-server -l 50      # View last 50 lines of server logs
  %(prog)s health-check meta-fastmcp-mcp-server    # Check health of specific server
  %(prog)s system-info                             # Show system information
        """
    )
    parser.add_argument(
        "action", 
        choices=[
            "start", "stop", "restart", "status", "logs", 
            "start-all", "stop-all", "restart-all",
            "monitor", "metrics", "health-check",
            "system-info", "export-config", "health-all"
        ],
        help="Action to perform"
    )
    parser.add_argument(
        "server", 
        nargs="?",
        help="Server name (directory names from mcps/, or 'all')"
    )
    parser.add_argument(
        "-l", "--lines",
        type=int,
        default=20,
        help="Number of log lines to display (default: 20)"
    )
    parser.add_argument(
        "--graceful",
        action="store_true",
        help="Perform graceful restart (wait for graceful shutdown)"
    )
    
    args = parser.parse_args()
    
    manager = MCPServerManager()
    
    if args.action == "start":
        if args.server == "all":
            manager.start_all()
        elif args.server:
            manager.start_server(args.server)
        else:
            print("Please specify a server name or 'all'")
    
    elif args.action == "stop":
        if args.server == "all":
            manager.stop_all()
        elif args.server:
            manager.stop_server(args.server)
        else:
            print("Please specify a server name or 'all'")
            
    elif args.action == "restart":
        if args.server == "all":
            manager.restart_all()
        elif args.server:
            if args.graceful:
                manager.restart_server_graceful(args.server)
            else:
                manager.restart_server(args.server)
        else:
            print("Please specify a server name or 'all'")
            
    elif args.action == "status":
        manager.status()
        
    elif args.action == "logs":
        if args.server:
            manager.logs(args.server, args.lines)
        else:
            print("Please specify a server name")
    
    elif args.action == "monitor":
        print("Starting monitoring console...")
        manager.monitor.start_monitoring()
        try:
            # Keep the monitoring running until interrupted
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping monitoring...")
            manager.monitor.stop_monitoring()
    
    elif args.action == "metrics":
        if args.server:
            metrics = manager.monitor.get_server_metrics(args.server)
            print(f"Metrics for {args.server}:")
            if metrics:
                for metric in metrics[-5:]:  # Show last 5 metrics
                    print(f"  {metric['timestamp']}: CPU={metric['cpu_percent']:.1f}%, "
                          f"Mem={metric['memory_percent']:.1f}%, Status={metric['health_status']}")
            else:
                print("  No metrics available")
        else:
            print("Current server status:")
            current_status = manager.monitor.get_current_status()
            for server_name, status in current_status.items():
                if 'health_status' in status:
                    print(f"  {server_name}: {status['health_status']} "
                          f"(CPU: {status['cpu_percent']:.1f}%, "
                          f"Mem: {status['memory_percent']:.1f}%)")
                else:
                    print(f"  {server_name}: {status['status']}")
    
    elif args.action == "health-check":
        if args.server:
            health = manager.check_server_health(args.server)
            print(f"Health of {args.server}: {health}")
        else:
            print("Please specify a server name")
    
    elif args.action == "health-all":
        all_health = manager.health_check_all()
        print("Health of all servers:")
        for server, health in all_health.items():
            print(f"  {server}: {health}")
    
    elif args.action == "system-info":
        sys_info = manager.get_system_info()
        print("System Information:")
        for key, value in sys_info.items():
            print(f"  {key}: {value}")
    
    elif args.action == "export-config":
        config = manager.export_config()
        print("Current Configuration:")
        for key, value in config.items():
            print(f"  {key}: {value}")
    
    elif args.action == "start-all":
        manager.start_all()
        
    elif args.action == "stop-all":
        manager.stop_all()
        
    elif args.action == "restart-all":
        manager.restart_all()


if __name__ == "__main__":
    main()