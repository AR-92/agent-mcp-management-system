#!/usr/bin/env python3
"""
Simple MCP Server Manager

Minimal control script to start, stop, and manage MCP servers with Qwen integration.
"""

import os
import sys
import subprocess
import signal
import time
import argparse
import json
from pathlib import Path
from typing import List, Dict, Any
import psutil  # Still needed for process management
import dotenv
from datetime import datetime


class SimpleMCPServerManager:
    """Simple MCP server manager with essential lifecycle management."""
    
    def __init__(self):
        # Load environment variables from .env file
        dotenv.load_dotenv()
        
        self.project_root = Path(__file__).parent.resolve()
        self.mcps_dir = self.project_root / "mcps"
        self.log_file = self.project_root / "manager.log"
        
        # Basic configuration with sensible defaults
        self.start_on_boot = os.getenv("START_ON_BOOT", "false").lower() == "true"
        self.shutdown_on_exit = os.getenv("SHUTDOWN_ON_EXIT", "true").lower() == "true"
        self.environment = os.getenv("ENVIRONMENT", "development")
        
        # Initialize basic logging
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('SimpleMCPServerManager')
        
        # Initialize servers and configuration
        self.servers = self._discover_servers()
        self.pid_file = self.project_root / "pids.json"
        
        # Register cleanup handlers
        import atexit
        atexit.register(self._cleanup_on_exit)
        
        # Handle signals for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Start services based on configuration
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize services based on configuration."""
        if self.start_on_boot:
            self.logger.info("Starting servers on boot...")
            self.start_all()
        self.logger.info(f"Simple MCP Manager initialized in {self.environment} environment")
    
    def _discover_servers(self) -> Dict[str, Dict]:
        """Dynamically discover all MCP servers in the mcps directory."""
        servers = {}
        
        if not self.mcps_dir.exists():
            self.logger.warning(f"MCPs directory does not exist: {self.mcps_dir}")
            return servers
            
        # Get all Python files in mcps directory that are MCP servers
        for item in self.mcps_dir.iterdir():
            if item.is_file() and item.suffix == ".py" and item.name != "__init__.py":
                # Use the file name without extension as the server name
                server_name = item.name[:-3]  # Remove .py extension
                
                servers[server_name] = {
                    "name": server_name,
                    "dir": item.parent,
                    "script": item.name,
                    "process": None,
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
    
    def load_pids(self) -> Dict[str, int]:
        """Load stored PIDs from file."""
        try:
            if self.pid_file.exists():
                with open(self.pid_file, 'r') as f:
                    return json.load(f)
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
    
    def start_server(self, server_name: str) -> bool:
        """Start a specific MCP server."""
        if server_name not in self.servers:
            error_msg = f"Server '{server_name}' not found"
            self.logger.error(error_msg)
            print(error_msg)
            return False
            
        server = self.servers[server_name]
        script_path = server["dir"] / server["script"]
        
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
        
        # Start the server process
        try:
            self.logger.info(f"Starting {server['name']} (stdio mode)")
            
            # Prepare environment
            env = os.environ.copy()
            
            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(server["dir"]),
                env=env,
                preexec_fn=os.setsid  # Create new process group
            )
            
            server["process"] = process
            
            # Brief wait to see if process exits immediately
            time.sleep(0.1)
            
            if process.poll() is not None:
                error_msg = f"Server {server['name']} terminated during startup (exit code: {process.returncode})"
                self.logger.error(error_msg)
                return False
            
            # Save the PID
            pids = self.load_pids()
            pids[server_name] = process.pid
            self.save_pids(pids)
            
            server["status"] = "running"
            server["startup_time"] = datetime.now().isoformat()
            
            success_msg = f"Started {server['name']} (PID: {process.pid})"
            self.logger.info(success_msg)
            print(success_msg)
            return True
            
        except Exception as e:
            error_msg = f"Error starting {server['name']}: {str(e)}"
            self.logger.error(error_msg)
            print(error_msg)
            return False
    
    def stop_server(self, server_name: str) -> bool:
        """Stop a specific MCP server."""
        if server_name not in self.servers:
            error_msg = f"Server '{server_name}' not found"
            self.logger.error(error_msg)
            print(error_msg)
            return False
            
        server = self.servers[server_name]
        
        # Try to get PID from stored file
        pids = self.load_pids()
        pid = pids.get(server_name)
        
        if not pid:
            warning_msg = f"No PID found for {server['name']}"
            self.logger.warning(warning_msg)
            print(warning_msg)
            return False
        
        try:
            self.logger.info(f"Stopping {server['name']} (PID: {pid})")
            
            # Kill the process group
            os.killpg(os.getpgid(pid), signal.SIGTERM)
            
            # Wait for graceful shutdown
            shutdown_start = time.time()
            max_wait = 30  # 30 seconds default timeout
            
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
                    force_msg = f"Force killing {server['name']} (PID: {pid}) after timeout"
                    self.logger.warning(force_msg)
                    os.killpg(os.getpgid(pid), signal.SIGKILL)
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
    
    def status(self) -> None:
        """Show status of all MCP servers."""
        print(f"MCP Server Status (Environment: {self.environment})")
        print("=" * 50)
        
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
                        running_count += 1
                    else:
                        status = "STOPPED"
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    status = "STOPPED"
                    # Clean up dead PID if needed
                    if server_name in pids:
                        del pids[server_name]
                        self.save_pids(pids)
            else:
                status = "STOPPED"
            
            print(f"{server['name']}: {status}")
            if pid and status == "RUNNING":
                print(f"  - PID: {pid}")
        
        print(f"\nSummary: {running_count}/{len(self.servers)} servers running")


class SimpleQwenMCPManager:
    """Manages Qwen MCP server configurations."""
    
    def __init__(self, mcps_dir=None):
        """Initialize the Qwen MCP Manager."""
        self.project_root = Path(__file__).parent.resolve()
        self.mcps_dir = mcps_dir or self.project_root / "mcps"
        
        # Qwen configuration paths (correct location that Qwen actually uses)
        self.qwen_config_dir = Path.home() / ".qwen"
        self.qwen_settings_file = self.qwen_config_dir / "settings.json"
        
        # Create Qwen config directory if it doesn't exist
        self.qwen_config_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize settings
        self.settings = self._load_qwen_settings()
    
    def _load_qwen_settings(self) -> Dict[str, Any]:
        """Load existing Qwen settings or create default ones."""
        if self.qwen_settings_file.exists():
            try:
                with open(self.qwen_settings_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load Qwen settings: {e}")
        
        # Return default settings with object format for mcpServers
        return {
            "mcpServers": {},
            "defaultServer": None,
            "serverDiscovery": {
                "autoDiscover": True,
                "scanDirectories": [str(self.mcps_dir)]
            }
        }
    
    def _save_qwen_settings(self) -> None:
        """Save Qwen settings to file."""
        try:
            with open(self.qwen_settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            print(f"Saved Qwen settings to {self.qwen_settings_file}")
        except Exception as e:
            print(f"Error saving Qwen settings: {e}")
    
    def discover_mcps(self) -> List[Dict[str, Any]]:
        """Discover all MCP servers in the mcps directory."""
        mcps = []
        
        if not self.mcps_dir.exists():
            print(f"Warning: MCP directory does not exist: {self.mcps_dir}")
            return mcps
        
        # Scan for MCP server files
        for item in self.mcps_dir.iterdir():
            if item.is_file() and item.suffix == ".py" and item.name != "__init__.py":
                # Extract server information
                server_name = item.name[:-3]  # Remove .py extension
                # Clean up common suffixes
                clean_name = server_name.replace('-mcp-server', '').replace('-server', '').replace('-', ' ').title()
                
                mcp_info = {
                    "id": server_name,
                    "name": f"{clean_name} Server",
                    "path": str(item.parent),
                    "entryPoint": item.name,  # Use actual file name
                    "enabled": True,
                    "description": f"Automatically discovered MCP server: {clean_name}"
                }
                mcps.append(mcp_info)
                print(f"Discovered MCP server: {server_name}")
        
        return mcps
    
    def integrate_with_qwen(self) -> None:
        """Integrate discovered MCPs with Qwen configuration."""
        # Discover MCP servers
        discovered_mcps = self.discover_mcps()
        
        if not discovered_mcps:
            print("No MCP servers found to integrate with Qwen")
            return
        
        # Handle object format for mcpServers
        current_mcps = self.settings.get("mcpServers", {})
        
        # Merge discovered MCPs with existing ones in object format
        for mcp in discovered_mcps:
            mcp_id = mcp["id"]
            if mcp_id not in current_mcps:
                # Convert to the object format expected by Qwen
                current_mcps[mcp_id] = {
                    "command": "python",
                    "args": ["-u", f"{mcp['path']}/{mcp['entryPoint']}"],
                    "cwd": mcp['path'],
                    "timeout": 30000,
                    "enabled": mcp.get("enabled", True)
                }
                print(f"Added new MCP server to Qwen: {mcp['name']}")
            else:
                # Update existing MCP info
                current_mcps[mcp_id].update({
                    "command": "python",
                    "args": ["-u", f"{mcp['path']}/{mcp['entryPoint']}"],
                    "cwd": mcp['path'],
                    "enabled": mcp.get("enabled", True)
                })
                print(f"Updated existing MCP server in Qwen: {mcp['name']}")
        
        self.settings["mcpServers"] = current_mcps
        
        # Set first server as default if none is set
        if not self.settings.get("defaultServer") and current_mcps:
            first_key = next(iter(current_mcps))
            self.settings["defaultServer"] = first_key
            print(f"Set default MCP server to: {first_key}")
        
        # Save updated settings
        self._save_qwen_settings()
        
        # Print summary
        print(f"\nSuccessfully integrated {len(discovered_mcps)} MCP servers with Qwen")
        print("Current MCP servers in Qwen configuration:")
        for server_id in self.settings["mcpServers"]:
            print(f"  - {server_id} [ENABLED]")
    
    def remove_all_mcps(self) -> None:
        """Remove all MCP servers from Qwen configuration."""
        current_mcps = self.settings.get("mcpServers", {})
        removed_count = len(current_mcps)
        self.settings["mcpServers"] = {}
        self.settings["defaultServer"] = None
        self._save_qwen_settings()
        print(f"Removed all {removed_count} MCP servers from Qwen configuration")
    
    def list_integrated_mcps(self) -> None:
        """List all MCP servers currently integrated with Qwen."""
        mcps = self.settings.get("mcpServers", {})
        
        if not mcps:
            print("No MCP servers are currently integrated with Qwen")
            return
        
        print("MCP servers integrated with Qwen:")
        for server_id, server_config in mcps.items():
            status = "ENABLED"
            default_marker = " (DEFAULT)" if server_id == self.settings.get("defaultServer") else ""
            print(f"  - {server_id} [{status}]{default_marker}")
            print(f"    ID: {server_id}")
            print(f"    Command: {server_config.get('command', 'N/A')}")
            print(f"    Args: {server_config.get('args', 'N/A')}")
            print(f"    CWD: {server_config.get('cwd', 'N/A')}")
            print()
    
    def get_qwen_config_path(self) -> str:
        """Return the path to the Qwen configuration file."""
        return str(self.qwen_settings_file)


def main():
    parser = argparse.ArgumentParser(
        description="Simple MCP Server Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s status                        # Show status of all servers
  %(prog)s start my-server              # Start a specific server
  %(prog)s stop-all                     # Stop all servers
  %(prog)s restart my-server            # Restart a specific server
  %(prog)s integrate                    # Integrate MCPs with Qwen
  %(prog)s list-qwen                    # List integrated MCPs
        """
    )
    parser.add_argument(
        "action", 
        choices=[
            "start", "stop", "restart", "status", 
            "start-all", "stop-all", "restart-all",
            "integrate", "list-qwen", "remove-all-qwen", "qwen-config-path"
        ],
        help="Action to perform"
    )
    parser.add_argument(
        "server", 
        nargs="?",
        help="Server name (directory names from mcps/, or 'all')"
    )
    
    args = parser.parse_args()
    
    manager = SimpleMCPServerManager()
    
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
            manager.stop_all()
            time.sleep(2)  # Wait for all servers to stop
            manager.start_all()
        elif args.server:
            manager.restart_server(args.server)
        else:
            print("Please specify a server name or 'all'")
            
    elif args.action == "status":
        manager.status()
    
    elif args.action == "start-all":
        manager.start_all()
        
    elif args.action == "stop-all":
        manager.stop_all()
        
    elif args.action == "restart-all":
        manager.stop_all()
        time.sleep(2)  # Wait for all servers to stop
        manager.start_all()
    
    elif args.action == "integrate":
        qwen_manager = SimpleQwenMCPManager(mcps_dir=manager.mcps_dir)
        qwen_manager.integrate_with_qwen()
    
    elif args.action == "list-qwen":
        qwen_manager = SimpleQwenMCPManager(mcps_dir=manager.mcps_dir)
        qwen_manager.list_integrated_mcps()
    
    elif args.action == "remove-all-qwen":
        qwen_manager = SimpleQwenMCPManager(mcps_dir=manager.mcps_dir)
        qwen_manager.remove_all_mcps()
    
    elif args.action == "qwen-config-path":
        qwen_manager = SimpleQwenMCPManager(mcps_dir=manager.mcps_dir)
        print(qwen_manager.get_qwen_config_path())


if __name__ == "__main__":
    main()