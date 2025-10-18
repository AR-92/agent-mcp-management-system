#!/usr/bin/env python3
"""
Simple MCP Server Manager - Non-Interactive Version

Minimal control script to start, stop, and manage MCP servers with Qwen integration.
This version removes all interactive modes and features.
"""

import os
import sys
import subprocess
import signal
import time
import argparse
import json

# Disable bytecode file generation
sys.dont_write_bytecode = True

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
        self.config_file = self.project_root / "config.json"
        
        # Load configuration from config file if it exists, otherwise use defaults
        self._load_config()
        
        # Initialize basic logging with no output by default
        import logging
        # Set logging level to suppress all logs by default
        logging.basicConfig(
            level=999,  # A high number to suppress all logs (CRITICAL = 50, so 999 suppresses everything)
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
    
    def _load_config(self):
        """Load configuration from config.json file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                
                server_config = config.get("server_config", {})
                self.start_on_boot = server_config.get("start_on_boot", False)
                self.shutdown_on_exit = server_config.get("shutdown_on_exit", True)
                self.environment = server_config.get("environment", "development")
            else:
                # Use defaults if config file doesn't exist
                self.start_on_boot = os.getenv("START_ON_BOOT", "false").lower() == "true"
                self.shutdown_on_exit = os.getenv("SHUTDOWN_ON_EXIT", "true").lower() == "true"
                self.environment = os.getenv("ENVIRONMENT", "development")
        except Exception as e:
            self.logger.error(f"Error loading config file: {e}")
            # Use defaults if there's an error loading the config
            self.start_on_boot = os.getenv("START_ON_BOOT", "false").lower() == "true"
            self.shutdown_on_exit = os.getenv("SHUTDOWN_ON_EXIT", "true").lower() == "true"
            self.environment = os.getenv("ENVIRONMENT", "development")
    
    def _initialize_services(self):
        """Initialize services based on configuration."""
        if self.start_on_boot:
            self.logger.info("Starting servers on boot based on individual configurations...")
            for server_name, server_config in self.servers.items():
                if server_config.get("start_on_boot", False):
                    self.logger.info(f"Starting {server_name} on boot based on server config")
                    self.start_server(server_name)
        self.logger.info(f"Simple MCP Manager initialized in {self.environment} environment")
    
    def _generate_default_config(self):
        """Generate a default config.json file based on discovered MCP files."""
        if not self.mcps_dir.exists():
            self.logger.warning(f"MCPs directory does not exist: {self.mcps_dir}")
            return

        # Discover all MCP files in the directory
        mcp_servers = {}
        for item in self.mcps_dir.iterdir():
            if item.is_file() and item.suffix == ".py" and item.name != "__init__.py":
                server_name = item.name[:-3]  # Remove .py extension
                # Set all defaults to false as requested
                mcp_servers[server_name] = {
                    "enabled": False,
                    "start_on_boot": False,
                    "add_to_qwen": False
                }

        # Create the default config structure
        default_config = {
            "server_config": {
                "start_on_boot": False,
                "shutdown_on_exit": False,
                "environment": "development",
                "servers": mcp_servers
            }
        }

        # Write the default config to file
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        self.logger.info(f"Generated default config.json with {len(mcp_servers)} discovered servers")
    
    def _discover_servers(self) -> Dict[str, Dict]:
        """Dynamically discover all MCP servers in the mcps directory."""
        # If config file doesn't exist, automatically generate it
        if not self.config_file.exists():
            self._generate_default_config()
        
        servers = {}
        
        if not self.mcps_dir.exists():
            self.logger.warning(f"MCPs directory does not exist: {self.mcps_dir}")
            return servers
        
        # Load server configuration if it exists
        enabled_servers = None
        config_servers = {}
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                config_servers = config.get("server_config", {}).get("servers", {})
            except Exception as e:
                self.logger.error(f"Error loading server config: {e}")
                # If there's an error loading config, generate a default one
                self._generate_default_config()
                # Reload the config after generating
                try:
                    with open(self.config_file, 'r') as f:
                        config = json.load(f)
                    config_servers = config.get("server_config", {}).get("servers", {})
                except Exception as e2:
                    self.logger.error(f"Error loading generated config: {e2}")
                    config_servers = {}

        # Get all Python files in mcps directory that are MCP servers
        for item in self.mcps_dir.iterdir():
            if item.is_file() and item.suffix == ".py" and item.name != "__init__.py":
                # Use the file name without extension as the server name
                server_name = item.name[:-3]  # Remove .py extension
                
                # If this server is not in the config, add it with default false values
                if server_name not in config_servers:
                    config_servers[server_name] = {
                        "enabled": False,
                        "start_on_boot": False,
                        "add_to_qwen": False
                    }
                    # Update the main config file with the new server
                    self._update_config_with_new_server(server_name, config_servers[server_name])
                
                # Check if this server is enabled in config
                server_config = config_servers.get(server_name, {})
                is_enabled = server_config.get("enabled", False)  # Now defaults to False
                
                if is_enabled:
                    servers[server_name] = {
                        "name": server_name,
                        "dir": item.parent,
                        "script": item.name,
                        "process": None,
                        "status": "stopped",
                        "startup_time": None,
                        "start_on_boot": server_config.get("start_on_boot", False)
                    }
        
        self.logger.info(f"Discovered {len(servers)} MCP servers (enabled)")
        return servers
    
    def _update_config_with_new_server(self, server_name, server_config):
        """Update the config file with a newly discovered server."""
        try:
            # Load current config
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
            else:
                config = {"server_config": {"servers": {}}}
            
            # Ensure the servers section exists
            if "server_config" not in config:
                config["server_config"] = {"servers": {}}
            if "servers" not in config["server_config"]:
                config["server_config"]["servers"] = {}
            
            # Add the new server config
            config["server_config"]["servers"][server_name] = server_config
            
            # Write updated config back to file
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error updating config with new server {server_name}: {e}")
    
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
        
        # Load server configuration to check which servers to add to Qwen
        config_file = self.project_root / "config.json"
        qwen_servers = {}
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                qwen_servers = config.get("server_config", {}).get("servers", {})
            except Exception as e:
                print(f"Warning: Could not load server config: {e}")
        
        # Scan for MCP server files
        for item in self.mcps_dir.iterdir():
            if item.is_file() and item.suffix == ".py" and item.name != "__init__.py":
                # Extract server information
                server_name = item.name[:-3]  # Remove .py extension
                # Clean up common suffixes
                clean_name = server_name.replace('-mcp-server', '').replace('-server', '').replace('-', ' ').title()
                
                # Check if this server should be added to Qwen
                server_config = qwen_servers.get(server_name, {})
                add_to_qwen = server_config.get("add_to_qwen", True)  # Add to Qwen by default
                
                if add_to_qwen:
                    mcp_info = {
                        "id": server_name,
                        "name": f"{clean_name} Server",
                        "path": str(item.parent),
                        "entryPoint": item.name,  # Use actual file name
                        "enabled": True,
                        "description": f"Automatically discovered MCP server: {clean_name}"
                    }
                    mcps.append(mcp_info)
                    print(f"Discovered MCP server: {server_name} (adding to Qwen)")
                else:
                    print(f"Discovered MCP server: {server_name} (skipping - not adding to Qwen)")
        
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
        description="Simple MCP Server Manager - Non-Interactive Version",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s status                        # Show status of all servers
  %(prog)s start my-server              # Start a specific server
  %(prog)s stop-all                     # Stop all servers
  %(prog)s restart my-server            # Restart a specific server
  %(prog)s integrate                    # Integrate MCPs with Qwen
  %(prog)s list-qwen                    # List integrated MCPs
  %(prog)s config-show                  # Show current configuration
        """
    )
    parser.add_argument(
        "action", 
        choices=[
            "start", "s", "stop", "sp", "restart", "r", "status", "st", 
            "start-all", "sa", "stop-all", "spa", "restart-all", "ra",
            "integrate", "int", "list-qwen", "lq", "remove-all-qwen", "qwen-config-path", "qcp",
            "config-show", "cfg", "config-list", "clist", "config-edit", "cedit", "list", "ls"
        ],
        help="Action to perform"
    )
    parser.add_argument(
        "server", 
        nargs="?",
        help="Server name (directory names from mcps/, or 'all')"
    )
    
    args = parser.parse_args()
    
    # Handle command aliases
    action = args.action
    if action in ['s']:
        action = 'start'
    elif action in ['sp']:
        action = 'stop'
    elif action in ['r']:
        action = 'restart'
    elif action in ['st']:
        action = 'status'
    elif action in ['sa']:
        action = 'start-all'
    elif action in ['spa']:
        action = 'stop-all'
    elif action in ['ra']:
        action = 'restart-all'
    elif action in ['ls']:
        action = 'list'
    elif action in ['cfg']:
        action = 'config-show'
    elif action in ['clist']:
        action = 'config-list'
    elif action in ['cedit']:
        action = 'config-edit'
    elif action in ['int']:
        action = 'integrate'
    elif action in ['lq']:
        action = 'list-qwen'
    elif action in ['qcp']:
        action = 'qwen-config-path'
    
    manager = SimpleMCPServerManager()
    
    if action == "start":
        if args.server == "all":
            manager.start_all()
        elif args.server:
            manager.start_server(args.server)
        else:
            print("Please specify a server name or 'all'")
    
    elif action == "stop":
        if args.server == "all":
            manager.stop_all()
        elif args.server:
            manager.stop_server(args.server)
        else:
            print("Please specify a server name or 'all'")
            
    elif action == "restart":
        if args.server == "all":
            manager.stop_all()
            time.sleep(2)  # Wait for all servers to stop
            manager.start_all()
        elif args.server:
            manager.restart_server(args.server)
        else:
            print("Please specify a server name or 'all'")
            
    elif action == "status":
        manager.status()
    
    elif action == "start-all":
        manager.start_all()
        
    elif action == "stop-all":
        manager.stop_all()
        
    elif action == "restart-all":
        manager.stop_all()
        time.sleep(2)  # Wait for all servers to stop
        manager.start_all()
    
    elif action == "integrate":
        qwen_manager = SimpleQwenMCPManager(mcps_dir=manager.mcps_dir)
        qwen_manager.integrate_with_qwen()
    
    elif action == "list-qwen":
        qwen_manager = SimpleQwenMCPManager(mcps_dir=manager.mcps_dir)
        qwen_manager.list_integrated_mcps()
    
    elif action == "remove-all-qwen":
        qwen_manager = SimpleQwenMCPManager(mcps_dir=manager.mcps_dir)
        qwen_manager.remove_all_mcps()
    
    elif action == "qwen-config-path":
        qwen_manager = SimpleQwenMCPManager(mcps_dir=manager.mcps_dir)
        print(qwen_manager.get_qwen_config_path())
    
    elif action == "config-show":
        import pprint
        config_file = manager.project_root / "config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
            print("Current configuration:")
            pprint.pprint(config)
        else:
            print("Configuration file not found. Using defaults.")
    
    elif action == "config-list":
        config_file = manager.project_root / "config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            print("MCP Server Configuration List:")
            print("=" * 60)
            
            server_config = config.get("server_config", {})
            servers = server_config.get("servers", {})
            
            if not servers:
                print("No servers configured.")
                return
            
            # Print header
            print(f"{'Server Name':<30} {'Enabled':<10} {'Boot':<10} {'Qwen':<10}")
            print("-" * 60)
            
            # Print each server's configuration
            for server_name, settings in servers.items():
                enabled = "YES" if settings.get("enabled", False) else "NO"
                start_on_boot = "YES" if settings.get("start_on_boot", False) else "NO"
                add_to_qwen = "YES" if settings.get("add_to_qwen", False) else "NO"
                
                print(f"{server_name:<30} {enabled:<10} {start_on_boot:<10} {add_to_qwen:<10}")
            
            print()
            print("Legend:")
            print("  Enabled: Whether the server is enabled in the manager")
            print("  Boot: Whether the server starts automatically on boot")
            print("  Qwen: Whether the server is integrated with Qwen")
        else:
            print("Configuration file not found. Using defaults.")
    
    elif action == "config-edit":
        config_file = manager.project_root / "config.json"
        if not config_file.exists():
            print("Configuration file not found. Nothing to modify.")
            return
        
        if not args.server:
            print("Please specify a server name to edit.")
            print("Usage: manager.py config-edit <server-name>")
            return
        
        server_name = args.server
        
        # Load current config
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Check if server exists in config
        servers = config.get("server_config", {}).get("servers", {})
        if server_name not in servers:
            print(f"Server '{server_name}' not found in configuration.")
            print("Available servers:")
            for name in servers.keys():
                print(f"  - {name}")
            return
        
        # Get current settings
        current_settings = servers[server_name]
        enabled = current_settings.get("enabled", False)
        start_on_boot = current_settings.get("start_on_boot", False)
        add_to_qwen = current_settings.get("add_to_qwen", False)
        
        print(f"Current configuration for {server_name}:")
        print(f"  Enabled: {enabled}")
        print(f"  Start on boot: {start_on_boot}")
        print(f"  Add to Qwen: {add_to_qwen}")
        print()
        
        # Ask user what to modify
        print("Which setting would you like to modify?")
        print("1. Enabled")
        print("2. Start on boot")
        print("3. Add to Qwen")
        print("4. All settings")
        choice = input("Enter your choice (1-4, or 'q' to quit): ").strip()
        
        if choice.lower() == 'q':
            print("No changes made.")
            return
        
        changes_made = False
        
        if choice == '1':
            current_value = enabled
            new_value = input(f"Set 'enabled' to (true/false) [current: {current_value}]: ").strip().lower()
            if new_value in ['true', '1', 'yes', 'y']:
                servers[server_name]['enabled'] = True
                changes_made = True
            elif new_value in ['false', '0', 'no', 'n']:
                servers[server_name]['enabled'] = False
                changes_made = True
            else:
                print("Invalid input. No changes made.")
        elif choice == '2':
            current_value = start_on_boot
            new_value = input(f"Set 'start_on_boot' to (true/false) [current: {current_value}]: ").strip().lower()
            if new_value in ['true', '1', 'yes', 'y']:
                servers[server_name]['start_on_boot'] = True
                changes_made = True
            elif new_value in ['false', '0', 'no', 'n']:
                servers[server_name]['start_on_boot'] = False
                changes_made = True
            else:
                print("Invalid input. No changes made.")
        elif choice == '3':
            current_value = add_to_qwen
            new_value = input(f"Set 'add_to_qwen' to (true/false) [current: {current_value}]: ").strip().lower()
            if new_value in ['true', '1', 'yes', 'y']:
                servers[server_name]['add_to_qwen'] = True
                changes_made = True
            elif new_value in ['false', '0', 'no', 'n']:
                servers[server_name]['add_to_qwen'] = False
                changes_made = True
            else:
                print("Invalid input. No changes made.")
        elif choice == '4':
            # Modify all settings
            current_value = enabled
            new_value = input(f"Set 'enabled' to (true/false) [current: {current_value}]: ").strip().lower()
            if new_value in ['true', '1', 'yes', 'y']:
                servers[server_name]['enabled'] = True
                changes_made = True
            elif new_value in ['false', '0', 'no', 'n']:
                servers[server_name]['enabled'] = False
                changes_made = True
            else:
                print("Invalid input for 'enabled'. Skipping.")
            
            current_value = start_on_boot
            new_value = input(f"Set 'start_on_boot' to (true/false) [current: {current_value}]: ").strip().lower()
            if new_value in ['true', '1', 'yes', 'y']:
                servers[server_name]['start_on_boot'] = True
                changes_made = True
            elif new_value in ['false', '0', 'no', 'n']:
                servers[server_name]['start_on_boot'] = False
                changes_made = True
            else:
                print("Invalid input for 'start_on_boot'. Skipping.")
            
            current_value = add_to_qwen
            new_value = input(f"Set 'add_to_qwen' to (true/false) [current: {current_value}]: ").strip().lower()
            if new_value in ['true', '1', 'yes', 'y']:
                servers[server_name]['add_to_qwen'] = True
                changes_made = True
            elif new_value in ['false', '0', 'no', 'n']:
                servers[server_name]['add_to_qwen'] = False
                changes_made = True
            else:
                print("Invalid input for 'add_to_qwen'. Skipping.")
        else:
            print("Invalid choice. No changes made.")
        
        if changes_made:
            # Save the updated config
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"Configuration for {server_name} updated successfully.")
        else:
            print("No changes were made.")
    
    elif action == "list":
        print("Discovered servers:")
        for server_name in manager.servers.keys():
            print(f"  - {server_name}")
        if not manager.servers:
            print("  No servers found (all servers are disabled in config)")


if __name__ == "__main__":
    main()