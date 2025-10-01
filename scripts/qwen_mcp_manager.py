#!/usr/bin/env python3
"""
Qwen MCP Configuration Manager

This script manages the Qwen Model Context Protocol server configurations
by dynamically discovering MCP servers and integrating them with Qwen's
global configuration system.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any


class QwenMCPManager:
    """Manages Qwen MCP server configurations."""
    
    def __init__(self):
        """Initialize the Qwen MCP Manager."""
        # Find the agent MCP management system directory
        self.project_root = Path("/home/rana/Documents/agent-mcp-managnet-system")
        self.mcps_dir = self.project_root / "mcps"
        
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
        
        # Scan for MCP server directories
        for item in self.mcps_dir.iterdir():
            if item.is_dir():
                # Look for server.py or similar entry point
                server_script = item / "server.py"
                if server_script.exists():
                    # Extract server information
                    server_name = item.name
                    # Clean up common suffixes
                    clean_name = server_name.replace('-mcp-server', '').replace('-server', '').replace('-', ' ').title()
                    
                    mcp_info = {
                        "id": server_name,
                        "name": f"{clean_name} Server",
                        "path": str(item),
                        "entryPoint": "server.py",
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
        
        # Handle both list and object formats for mcpServers
        current_mcps = self.settings.get("mcpServers", {})
        
        if isinstance(current_mcps, dict):  # Object format
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
        else:  # List format
            # Update Qwen settings with discovered MCPs
            existing_mcps = {mcp["id"]: mcp for mcp in current_mcps}
            
            # Merge discovered MCPs with existing ones
            for mcp in discovered_mcps:
                mcp_id = mcp["id"]
                if mcp_id not in existing_mcps:
                    existing_mcps[mcp_id] = mcp
                    print(f"Added new MCP server to Qwen: {mcp['name']}")
                else:
                    # Update existing MCP info
                    existing_mcps[mcp_id].update(mcp)
                    print(f"Updated existing MCP server in Qwen: {mcp['name']}")
            
            # Convert back to list
            self.settings["mcpServers"] = list(existing_mcps.values())
        
        # Set first server as default if none is set
        if not self.settings.get("defaultServer"):
            if isinstance(self.settings["mcpServers"], dict) and self.settings["mcpServers"]:
                first_key = next(iter(self.settings["mcpServers"]))
                self.settings["defaultServer"] = first_key
                print(f"Set default MCP server to: {first_key}")
            elif isinstance(self.settings["mcpServers"], list) and self.settings["mcpServers"]:
                self.settings["defaultServer"] = self.settings["mcpServers"][0]["id"]
                print(f"Set default MCP server to: {self.settings['mcpServers'][0]['name']}")
        
        # Save updated settings
        self._save_qwen_settings()
        
        # Print summary
        print(f"\nSuccessfully integrated {len(discovered_mcps)} MCP servers with Qwen")
        print("Current MCP servers in Qwen configuration:")
        if isinstance(self.settings["mcpServers"], dict):
            for server_id in self.settings["mcpServers"]:
                print(f"  - {server_id} [ENABLED]")
        else:
            for mcp in self.settings["mcpServers"]:
                status = "ENABLED" if mcp.get("enabled", True) else "DISABLED"
                print(f"  - {mcp['name']} [{status}]")
    
    def remove_all_mcps(self) -> None:
        """Remove all MCP servers from Qwen configuration."""
        current_mcps = self.settings.get("mcpServers", {})
        if isinstance(current_mcps, dict):
            removed_count = len(current_mcps)
            self.settings["mcpServers"] = {}
        else:
            removed_count = len(current_mcps)
            self.settings["mcpServers"] = []
        self.settings["defaultServer"] = None
        self._save_qwen_settings()
        print(f"Removed all {removed_count} MCP servers from Qwen configuration")
    
    def list_integrated_mcps(self) -> None:
        """List all MCP servers currently integrated with Qwen."""
        mcps = self.settings.get("mcpServers", [])
        
        # Handle both list format and object format for mcpServers
        if isinstance(mcps, dict):  # Object format
            if not mcps:
                print("No MCP servers are currently integrated with Qwen")
                return
            
            print("MCP servers integrated with Qwen:")
            for server_id, server_config in mcps.items():
                # For object format, use the key as ID and add display name
                status = "ENABLED"  # Objects format doesn't have enabled flag in this example
                default_marker = " (DEFAULT)" if server_id == self.settings.get("defaultServer") else ""
                print(f"  - {server_id} [{status}]{default_marker}")
                print(f"    ID: {server_id}")
                print(f"    Command: {server_config.get('command', 'N/A')}")
                print(f"    Args: {server_config.get('args', 'N/A')}")
                print(f"    CWD: {server_config.get('cwd', 'N/A')}")
                print()
        else:  # List format
            if not mcps:
                print("No MCP servers are currently integrated with Qwen")
                return
            
            print("MCP servers integrated with Qwen:")
            for mcp in mcps:
                status = "ENABLED" if mcp.get("enabled", True) else "DISABLED"
                default_marker = " (DEFAULT)" if mcp.get("id") == self.settings.get("defaultServer") else ""
                print(f"  - {mcp['name']} [{status}]{default_marker}")
                print(f"    ID: {mcp['id']}")
                print(f"    Path: {mcp['path']}")
                print(f"    Description: {mcp.get('description', 'No description')}")
                print()
    
    def get_qwen_config_path(self) -> str:
        """Return the path to the Qwen configuration file."""
        return str(self.qwen_settings_file)


def main():
    """Main entry point for the Qwen MCP Manager."""
    manager = QwenMCPManager()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python qwen_mcp_manager.py integrate     - Integrate all MCPs with Qwen")
        print("  python qwen_mcp_manager.py remove-all     - Remove all MCPs from Qwen")
        print("  python qwen_mcp_manager.py list            - List integrated MCPs")
        print("  python qwen_mcp_manager.py config-path    - Show Qwen config file path")
        return
    
    command = sys.argv[1]
    
    if command == "integrate":
        manager.integrate_with_qwen()
    elif command == "remove-all":
        manager.remove_all_mcps()
    elif command == "list":
        manager.list_integrated_mcps()
    elif command == "config-path":
        print(manager.get_qwen_config_path())
    else:
        print(f"Unknown command: {command}")
        print("Available commands: integrate, remove-all, list, config-path")


if __name__ == "__main__":
    main()