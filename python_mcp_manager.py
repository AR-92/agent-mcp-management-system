#!/usr/bin/env python3
"""
MCP Server Manager

Python script to manage MCP server processes (start, stop, status) without shell scripts.
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path
import json
import psutil
from typing import Dict, List, Optional


class MCPServerManager:
    """Manages MCP server processes using Python instead of shell scripts."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.mcps_dir = self.project_root / "mcps"
        self.logs_dir = self.project_root / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        # Store PIDs in a JSON file
        self.pid_file = self.logs_dir / "mcp_servers.json"
        self.pids = self.load_pids()
        
    def load_pids(self) -> Dict[str, int]:
        """Load stored PIDs from file."""
        if self.pid_file.exists():
            try:
                with open(self.pid_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading PIDs: {e}")
        return {}
    
    def save_pids(self) -> None:
        """Save PIDs to file."""
        try:
            with open(self.pid_file, 'w') as f:
                json.dump(self.pids, f, indent=2)
        except Exception as e:
            print(f"Error saving PIDs: {e}")
    
    def discover_servers(self) -> List[str]:
        """Discover all server directories that contain server.py"""
        servers = []
        for item in self.mcps_dir.iterdir():
            if item.is_dir():
                server_script = item / "server.py"
                if server_script.exists():
                    servers.append(item.name)
        return servers
    
    def start_server(self, server_name: str) -> bool:
        """Start a specific MCP server."""
        server_dir = self.mcps_dir / server_name
        server_script = server_dir / "server.py"
        
        if not server_script.exists():
            print(f"Error: server.py not found for {server_name}")
            return False
        
        # Check if already running
        if server_name in self.pids:
            pid = self.pids[server_name]
            try:
                process = psutil.Process(pid)
                if process.is_running():
                    print(f"Server {server_name} is already running with PID {pid}")
                    return True
                else:
                    # Remove dead PID
                    del self.pids[server_name]
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Remove dead PID
                del self.pids[server_name]
        
        # Start the server process with proper stdio handling
        try:
            log_file = self.logs_dir / f"{server_name}.log"
            with open(log_file, 'a') as log:
                # For stdio-based servers, we need to start them as background processes
                process = subprocess.Popen(
                    [sys.executable, str(server_script)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,  # Redirect stderr to stdout
                    stdin=subprocess.PIPE,     # Provide stdin so process can communicate
                    cwd=str(server_dir)
                )
            
            # Store the PID
            self.pids[server_name] = process.pid
            self.save_pids()
            print(f"Started {server_name} with PID {process.pid}")
            return True
            
        except Exception as e:
            print(f"Error starting {server_name}: {e}")
            return False
    
    def stop_server(self, server_name: str) -> bool:
        """Stop a specific MCP server."""
        if server_name not in self.pids:
            print(f"Server {server_name} is not running (no PID found)")
            return False
        
        pid = self.pids[server_name]
        try:
            process = psutil.Process(pid)
            process.terminate()
            
            # Wait for process to terminate
            try:
                process.wait(timeout=10)
            except psutil.TimeoutExpired:
                print(f"Process {pid} didn't terminate gracefully, killing...")
                process.kill()
            
            # Remove from PIDs
            del self.pids[server_name]
            self.save_pids()
            print(f"Stopped {server_name} (PID: {pid})")
            return True
            
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            print(f"Process with PID {pid} not found or access denied")
            # Remove from PIDs anyway
            if server_name in self.pids:
                del self.pids[server_name]
                self.save_pids()
            return True
        except Exception as e:
            print(f"Error stopping {server_name}: {e}")
            return False
    
    def start_all(self) -> None:
        """Start all discovered MCP servers."""
        servers = self.discover_servers()
        print(f"Discovered {len(servers)} servers: {', '.join(servers)}")
        
        for server_name in servers:
            print(f"Starting {server_name}...")
            self.start_server(server_name)
    
    def stop_all(self) -> None:
        """Stop all running MCP servers."""
        if not self.pids:
            print("No servers are currently running")
            return
        
        for server_name in list(self.pids.keys()):
            print(f"Stopping {server_name}...")
            self.stop_server(server_name)
    
    def status(self) -> None:
        """Show status of all servers."""
        servers = self.discover_servers()
        
        if not servers:
            print("No servers found")
            return
        
        print("Server Status:")
        print("-" * 60)
        
        for server_name in servers:
            if server_name in self.pids:
                pid = self.pids[server_name]
                try:
                    process = psutil.Process(pid)
                    if process.is_running():
                        status = "RUNNING"
                        cpu_percent = process.cpu_percent()
                        memory_mb = process.memory_info().rss / 1024 / 1024
                        print(f"{server_name:30} | PID: {pid:6} | {status:10} | CPU: {cpu_percent:5.1f}% | MEM: {memory_mb:6.1f}MB")
                    else:
                        print(f"{server_name:30} | PID: {pid:6} | STOPPED")
                        # Remove dead PID
                        del self.pids[server_name]
                        self.save_pids()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    print(f"{server_name:30} | PID: {pid:6} | ZOMBIE")
                    # Remove dead PID
                    del self.pids[server_name]
                    self.save_pids()
            else:
                print(f"{server_name:30} | PID:   -- | STOPPED")


def main():
    if len(sys.argv) < 2:
        print("Usage: python mcp_manager.py [start-all|stop-all|status|start <server>|stop <server>]")
        sys.exit(1)
    
    manager = MCPServerManager()
    command = sys.argv[1]
    
    if command == "start-all":
        manager.start_all()
    elif command == "stop-all":
        manager.stop_all()
    elif command == "status":
        manager.status()
    elif command == "start" and len(sys.argv) > 2:
        server_name = sys.argv[2]
        manager.start_server(server_name)
    elif command == "stop" and len(sys.argv) > 2:
        server_name = sys.argv[2]
        manager.stop_server(server_name)
    else:
        print(f"Unknown command: {command}")
        print("Usage: python mcp_manager.py [start-all|stop-all|status|start <server>|stop <server>]")
        sys.exit(1)


if __name__ == "__main__":
    main()