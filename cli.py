#!/usr/bin/env python3
"""
Improved FZF Enhanced MCP Server Manager CLI v3.0

An fzf-powered interface for managing MCP (Model Context Protocol) servers with
fuzzy selection capabilities. This improved version includes streamlined menus,
batch operations, and enhanced UX.

Features:
- Streamlined menu structure with reduced redundancy
- Dashboard view showing all server status in one place
- Batch operations for managing multiple servers at once
- Improved configuration management with quick toggles
- Enhanced error handling and performance optimizations
- Unified command-line and interactive interfaces
"""

import json
import sys
import os
import subprocess
import argparse
from pathlib import Path
import psutil
import time
from typing import List, Dict, Optional, Tuple

# Add the project root to the Python path to import our manager
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from manager import SimpleMCPServerManager, SimpleQwenMCPManager


def run_fzf(options, prompt="Select:", multi=False, preview=None):
    """Run fzf with the provided options and return the selected option(s)."""
    if not options:
        return [] if multi else None
        
    try:
        # Create unified fzf options with consistent styling
        fzf_cmd = [
            'fzf',
            '--prompt', f'{prompt}> ',
            '--layout=reverse',
            '--height=70%',
            '--border',
            '--cycle',
            '--ansi',
            '--no-bold',
            '--color=fg:#e0e0e0,bg:#1e1e2e,hl:#89b4fa',
            '--color=fg+:#cdd6f4,bg+:#313244,hl+:#89b4fa',
            '--color=info:#cba6f7,prompt:#fab387,pointer:#f38ba8',
            '--color=marker:#f9e2af,spinner:#94e2d5,header:#74c7ec'
        ]
        
        if multi:
            fzf_cmd.append('--multi')
        else:
            fzf_cmd.append('--no-multi')
            
        if preview:
            fzf_cmd.extend(['--preview', preview])
        
        result = subprocess.run(
            fzf_cmd,
            input='\n'.join(options),
            text=True,
            capture_output=True
        )
        if result.returncode == 0:
            if multi:
                # Split by newlines and filter out empty strings
                selected = [item.strip() for item in result.stdout.strip().split('\n') if item.strip()]
                return selected
            return result.stdout.strip()
        return [] if multi else None
    except FileNotFoundError:
        # Show error in fzf
        fzf_cmd = [
            'fzf',
            '--prompt', 'Error> ',
            '--layout=reverse',
            '--height=70%',
            '--border',
            '--no-multi',
            '--ansi',
            '--no-bold',
            '--cycle',
            '--color=fg:#e0e0e0,bg:#1e1e2e,hl:#89b4fa',
            '--color=fg+:#cdd6f4,bg+:#313244,hl+:#89b4fa',
            '--color=info:#cba6f7,prompt:#fab387,pointer:#f38ba8',
            '--color=marker:#f9e2af,spinner:#94e2d5,header:#74c7ec'
        ]
        
        subprocess.run(
            fzf_cmd,
            input='fzf not found. Please install fzf to use this interface.',
            text=True
        )
        sys.exit(1)


def get_available_servers():
    """Get list of available servers."""
    try:
        manager = SimpleMCPServerManager()
        return list(manager.servers.keys())
    except Exception as e:
        run_fzf([f"Error retrieving available servers: {e}"], "Error")
        return []


def get_server_status_info():
    """Get server status information for display."""
    manager = SimpleMCPServerManager()
    pids = manager.load_pids()
    server_info = []
    running_count = 0
    
    for server_name in manager.servers.keys():
        pid = pids.get(server_name)
        status = "STOPPED"
        if pid:
            try:
                process = psutil.Process(pid)
                if process.is_running():
                    status = "RUNNING"
                    running_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Format with consistent alignment
        if pid and status == "RUNNING":
            info_line = f"{server_name:<30} [{status:<7}] (PID: {pid})"
        else:
            info_line = f"{server_name:<30} [{status:<7}]"
        server_info.append(info_line)
    
    return server_info, running_count, len(manager.servers)


def dashboard_view():
    """Display a comprehensive dashboard view of all server statuses."""
    server_info, running_count, total_count = get_server_status_info()
    
    # Add summary to server_info list
    summary = f"Summary: {running_count}/{total_count} servers running"
    server_info.append("")
    server_info.append(summary)
    manager = SimpleMCPServerManager()
    server_info.append(f"Environment: {manager.environment}")
    
    # Color code the server list
    colored_server_info = []
    for info in server_info:
        if "[RUNNING]" in info:
            colored_info = f"\033[38;2;166;227;161m{info}\033[0m"  # Green for running
        elif "[STOPPED]" in info:
            colored_info = f"\033[38;2;243;139;168m{info}\033[0m"  # Pink for stopped
        else:
            colored_info = info
        colored_server_info.append(colored_info)
    
    # Add quick action options
    options = ["View Dashboard Only"] + colored_server_info + [
        "",
        "Quick Actions:",
        "  [S] Start all servers",
        "  [T] Stop all servers", 
        "  [R] Restart all servers",
        "  [C] Go to configuration",
        "  [Q] Go to Qwen integration",
        "  [M] Back to main menu"
    ]
    
    selection = run_fzf(options, "Dashboard View")
    
    if selection and selection.startswith("  [S]"):
        confirm_options = ["Yes", "No"]
        confirm = run_fzf(confirm_options, "Start all servers?")
        if confirm == "Yes":
            manager.start_all()
            run_fzf([f"Started all {total_count} servers"], "Info")
    elif selection and selection.startswith("  [T]"):
        confirm_options = ["Yes", "No"]
        confirm = run_fzf(confirm_options, "Stop all servers?")
        if confirm == "Yes":
            manager.stop_all()
            run_fzf([f"Stopped all {total_count} servers"], "Info")
    elif selection and selection.startswith("  [R]"):
        confirm_options = ["Yes", "No"]
        confirm = run_fzf(confirm_options, "Restart all servers?")
        if confirm == "Yes":
            manager.stop_all()
            time.sleep(2)  # Wait for all servers to stop
            manager.start_all()
            run_fzf([f"Restarted all {total_count} servers"], "Info")
    elif selection and selection.startswith("  [C]"):
        config_management_menu()
    elif selection and selection.startswith("  [Q]"):
        qwen_integration_menu()
    elif selection and selection.startswith("  [M]"):
        return True  # Return to main menu


def env_management_menu():
    """Environment (.env) management menu with create, edit, and delete functionality."""
    import os
    from pathlib import Path
    
    project_root = Path(__file__).parent
    env_file = project_root / ".env"
    
    options = [
        "Create .env file",
        "Edit .env file",
        "View .env file contents",
        "Delete .env file",
        "Validate .env file",
        "Back to Main Menu"
    ]
    
    while True:
        selection = run_fzf(options, "Environment (.env) Management")
        
        if not selection or selection == "Back to Main Menu":
            return  # Return to main menu
        elif selection == "Create .env file":
            if env_file.exists():
                run_fzf([f".env file already exists at: {env_file}"], "Info")
                choice = run_fzf(["Overwrite", "View Current", "Cancel"], "File already exists")
                if choice == "Overwrite":
                    create_env_file(env_file)
                elif choice == "View Current":
                    view_env_file(env_file)
            else:
                create_env_file(env_file)
        elif selection == "Edit .env file":
            if env_file.exists():
                editor = os.environ.get('EDITOR', os.environ.get('VISUAL', 'nano'))
                try:
                    subprocess.run([editor, str(env_file)])
                    run_fzf([f"Successfully edited .env file"], "Info")
                except FileNotFoundError:
                    try:
                        subprocess.run(['nano', str(env_file)])
                    except FileNotFoundError:
                        try:
                            subprocess.run(['vim', str(env_file)])
                        except FileNotFoundError:
                            run_fzf([f"Could not find an editor. Please install nano, vim, or set EDITOR environment variable."], "Error")
            else:
                run_fzf([f".env file does not exist. Create it first."], "Info")
        elif selection == "View .env file contents":
            if env_file.exists():
                view_env_file(env_file)
            else:
                run_fzf([f".env file does not exist. Create it first."], "Info")
        elif selection == "Delete .env file":
            if env_file.exists():
                confirm_options = [f"Yes, delete {env_file}", "No, cancel"]
                confirm = run_fzf(confirm_options, f"Delete .env file at {env_file}? This cannot be undone!")
                if confirm and confirm.startswith("Yes"):
                    env_file.unlink()
                    run_fzf([f"Successfully deleted .env file"], "Info")
                else:
                    run_fzf([f"Deletion cancelled."], "Info")
            else:
                run_fzf([f".env file does not exist."], "Info")
        elif selection == "Validate .env file":
            if env_file.exists():
                validate_env_file(env_file)
            else:
                run_fzf([f".env file does not exist."], "Info")


def create_env_file(env_file):
    """Helper function to create a new .env file with default content."""
    default_content = """# Environment variables for MCP Server Manager
# Copy this file to .env and fill in your values

# Server Configuration
START_ON_BOOT=false
SHUTDOWN_ON_EXIT=true
ENVIRONMENT=development

# Logging
MCP_LOG_LEVEL=INFO

# Qwen Integration
QWEN_CONFIG_PATH=

# Add your environment variables here
# Example:
# DATABASE_URL=postgresql://user:password@localhost:5432/mydb
# API_KEY=your_api_key_here
"""
    with open(env_file, 'w') as f:
        f.write(default_content)
    run_fzf([f"Created .env file at: {env_file}"], "Success")


def view_env_file(env_file):
    """Helper function to view .env file contents."""
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Split content into lines for display in fzf
    lines = content.split('\n')
    # Color code comments and sensitive values
    colored_lines = []
    for line in lines:
        if line.strip().startswith('#'):
            # Comment line - make it gray
            colored_line = f"\033[38;2;166;176;185m{line}\033[0m"  # Gray for comments
        elif '=' in line and any(sensitive in line.upper() for sensitive in ['KEY', 'SECRET', 'PASSWORD', 'TOKEN', 'API']):
            # Sensitive value - redacted in display
            key = line.split('=')[0]
            colored_line = f"\033[38;2;243;139;168m{key}=\033[0m\033[38;2;249;226;175m[REDACTED]\033[0m"  # Pink key, yellow redaction
        else:
            colored_line = line
        colored_lines.append(colored_line)
    
    run_fzf(colored_lines, f".env File Contents ({env_file.name})")


def validate_env_file(env_file):
    """Helper function to validate .env file content."""
    try:
        with open(env_file, 'r') as f:
            content = f.read()
        
        errors = []
        warnings = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Skip empty lines and comments
            if not stripped or stripped.startswith('#'):
                continue
                
            # Check for proper format key=value
            if '=' not in stripped:
                errors.append(f"Line {i}: Missing '=' in assignment: {stripped}")
                continue
            
            key, value = stripped.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            # Check for common issues
            if not key:
                errors.append(f"Line {i}: Missing key in assignment")
            
            # Check for unquoted special characters
            if value.startswith('"') and not value.endswith('"') and len(value) > 1:
                warnings.append(f"Line {i}: Value for '{key}' starts with quote but doesn't end with quote")
            elif value.startswith("'") and not value.endswith("'") and len(value) > 1:
                warnings.append(f"Line {i}: Value for '{key}' starts with quote but doesn't end with quote")
        
        # Display validation results
        result_lines = []
        if errors:
            result_lines.append(f"❌ Validation ERRORS found: {len(errors)}")
            for error in errors:
                result_lines.append(f"  • {error}")
        else:
            result_lines.append("✅ No errors found!")
            
        if warnings:
            result_lines.append(f"\n⚠️  WARNINGS: {len(warnings)}")
            for warning in warnings:
                result_lines.append(f"  • {warning}")
        else:
            if not errors:
                result_lines.append("\n✅ No warnings found!")
        
        result_lines.append(f"\nTotal lines processed: {len(lines)}")
        
        # Add options for next steps
        result_lines.extend([
            "",
            "Next steps:",
            "  • [E] Edit .env file",
            "  • [V] View .env file",
            "  • [B] Back to .env management"
        ])
        
        selection = run_fzf(result_lines, "Environment File Validation")
        
        if selection and "[E]" in selection:
            editor = os.environ.get('EDITOR', os.environ.get('VISUAL', 'nano'))
            try:
                subprocess.run([editor, str(env_file)])
            except FileNotFoundError:
                try:
                    subprocess.run(['nano', str(env_file)])
                except FileNotFoundError:
                    try:
                        subprocess.run(['vim', str(env_file)])
                    except FileNotFoundError:
                        run_fzf([f"Could not find an editor. Please install nano, vim, or set EDITOR environment variable."], "Error")
        elif selection and "[V]" in selection:
            view_env_file(env_file)
        # If [B] or no selection, just return to .env management menu
        
    except Exception as e:
        run_fzf([f"Error validating .env file: {e}"], "Error")


def create_env_file_cli(env_file):
    """CLI-specific function to create a new .env file with default content."""
    default_content = """# Environment variables for MCP Server Manager
# Copy this file to .env and fill in your values

# Server Configuration
START_ON_BOOT=false
SHUTDOWN_ON_EXIT=true
ENVIRONMENT=development

# Logging
MCP_LOG_LEVEL=INFO

# Qwen Integration
QWEN_CONFIG_PATH=

# Add your environment variables here
# Example:
# DATABASE_URL=postgresql://user:password@localhost:5432/mydb
# API_KEY=your_api_key_here
"""
    with open(env_file, 'w') as f:
        f.write(default_content)
    print(f"Created .env file at: {env_file}")


def validate_env_file_cli(env_file):
    """CLI-specific function to validate .env file content."""
    try:
        with open(env_file, 'r') as f:
            content = f.read()
        
        errors = []
        warnings = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Skip empty lines and comments
            if not stripped or stripped.startswith('#'):
                continue
                
            # Check for proper format key=value
            if '=' not in stripped:
                errors.append(f"Line {i}: Missing '=' in assignment: {stripped}")
                continue
            
            key, value = stripped.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            # Check for common issues
            if not key:
                errors.append(f"Line {i}: Missing key in assignment")
            
            # Check for unquoted special characters
            if value.startswith('"') and not value.endswith('"') and len(value) > 1:
                warnings.append(f"Line {i}: Value for '{key}' starts with quote but doesn't end with quote")
            elif value.startswith("'") and not value.endswith("'") and len(value) > 1:
                warnings.append(f"Line {i}: Value for '{key}' starts with quote but doesn't end with quote")
        
        # Display validation results
        if errors:
            print(f"❌ Validation ERRORS found: {len(errors)}")
            for error in errors:
                print(f"  • {error}")
        else:
            print("✅ No errors found!")
            
        if warnings:
            print(f"\n⚠️  WARNINGS: {len(warnings)}")
            for warning in warnings:
                print(f"  • {warning}")
        else:
            if not errors:
                print("\n✅ No warnings found!")
        
        print(f"\nTotal lines processed: {len(lines)}")
        
    except Exception as e:
        print(f"Error validating .env file: {e}")


def batch_server_operations():
    """Perform batch operations on multiple servers using fzf multi-select."""
    manager = SimpleMCPServerManager()
    servers = get_available_servers()
    
    if not servers:
        run_fzf(["No servers available."], "Info")
        return
    
    # Multi-select servers
    selected_servers = run_fzf(servers, "Select servers (TAB to select multiple)", multi=True)
    
    if not selected_servers:
        run_fzf(["No servers selected."], "Info")
        return
    
    # Choose operation
    operations = [
        "Start Selected Servers",
        "Stop Selected Servers", 
        "Restart Selected Servers",
        "Cancel"
    ]
    
    operation = run_fzf(operations, f"Operation for {len(selected_servers)} servers")
    
    if operation == "Start Selected Servers":
        for server in selected_servers:
            manager.start_server(server)
        run_fzf([f"Started {len(selected_servers)} servers"], "Info")
    elif operation == "Stop Selected Servers":
        for server in selected_servers:
            manager.stop_server(server)
        run_fzf([f"Stopped {len(selected_servers)} servers"], "Info")
    elif operation == "Restart Selected Servers":
        for server in selected_servers:
            manager.stop_server(server)
        time.sleep(1)  # Brief pause
        for server in selected_servers:
            manager.start_server(server)
        run_fzf([f"Restarted {len(selected_servers)} servers"], "Info")


def server_management_menu():
    """Improved server management menu with batch operations."""
    manager = SimpleMCPServerManager()
    options = [
        "Start Server",
        "Stop Server", 
        "Restart Server",
        "Batch Operations (Select Multiple Servers)",
        "Start All Servers",
        "Stop All Servers",
        "Restart All Servers",
        "Dashboard View",
        "Back to Main Menu"
    ]
    
    while True:
        selection = run_fzf(options, "Server Management")
        
        if not selection or selection == "Back to Main Menu":
            return  # Return to main menu
        elif selection == "Start Server":
            servers = get_available_servers()
            if not servers:
                run_fzf(["No servers available."], "Info")
                continue
                
            server = run_fzf(servers, "Select server to start")
            if server:
                # Direct operation without confirmation for single server
                manager.start_server(server)
                run_fzf([f"Started {server}"], "Info")
            else:
                run_fzf(["No server selected."], "Info")
        elif selection == "Stop Server":
            servers = get_available_servers()
            if not servers:
                run_fzf(["No servers available."], "Info")
                continue
                
            server = run_fzf(servers, "Select server to stop")
            if server:
                # Direct operation without confirmation for single server
                manager.stop_server(server)
                run_fzf([f"Stopped {server}"], "Info")
            else:
                run_fzf(["No server selected."], "Info")
        elif selection == "Restart Server":
            servers = get_available_servers()
            if not servers:
                run_fzf(["No servers available."], "Info")
                continue
                
            server = run_fzf(servers, "Select server to restart")
            if server:
                # Direct operation without confirmation for single server
                manager.restart_server(server)
                run_fzf([f"Restarted {server}"], "Info")
            else:
                run_fzf(["No server selected."], "Info")
        elif selection == "Batch Operations (Select Multiple Servers)":
            batch_server_operations()
        elif selection == "Start All Servers":
            confirm_options = ["Yes", "No"]
            confirm = run_fzf(confirm_options, "Start all servers?")
            if confirm == "Yes":
                manager.start_all()
                run_fzf(["Started all servers"], "Info")
            else:
                run_fzf(["Start all operation cancelled."], "Info")
        elif selection == "Stop All Servers":
            confirm_options = ["Yes", "No"]
            confirm = run_fzf(confirm_options, "Stop all servers?")
            if confirm == "Yes":
                manager.stop_all()
                run_fzf(["Stopped all servers"], "Info")
            else:
                run_fzf(["Stop all operation cancelled."], "Info")
        elif selection == "Restart All Servers":
            confirm_options = ["Yes", "No"]
            confirm = run_fzf(confirm_options, "Restart all servers?")
            if confirm == "Yes":
                manager.stop_all()
                time.sleep(2)  # Wait for all servers to stop
                manager.start_all()
                run_fzf(["Restarted all servers"], "Info")
            else:
                run_fzf(["Restart all operation cancelled."], "Info")
        elif selection == "Dashboard View":
            dashboard_view()


def config_management_menu():
    """Improved configuration management menu with direct server toggles."""
    manager = SimpleMCPServerManager()
    config_file = manager.project_root / "config.json"
    
    while True:
        # Read config to show current settings
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
        except:
            config = {"server_config": {"servers": {}}}
        
        # Create options based on config
        options = [
            "Show Current Configuration",
            "List All Discovered Servers",
            "Modify Server Configuration",
            "Direct Server Config Toggles",
            "Back to Main Menu"
        ]
        
        selection = run_fzf(options, "Configuration Management")
        
        if not selection or selection == "Back to Main Menu":
            return  # Return to main menu
        elif selection == "Show Current Configuration":
            # Offer to edit the configuration file directly with an editor
            options = [
                "View Configuration in FZF",
                "Edit Configuration with Editor",
                "Back to Configuration Management"
            ]
            choice = run_fzf(options, "Configuration View/Editing Options")
            
            if choice == "View Configuration in FZF":
                config_data = []
                
                if config_file.exists():
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                    
                    # Format the configuration as a user-friendly list
                    def flatten_config(config_obj, prefix=""):
                        items = []
                        for key, value in config_obj.items():
                            if isinstance(value, dict):
                                # Add section header
                                items.append(f"[{key}]")
                                # Recursively add nested items with improved indentation
                                items.extend(flatten_config(value, prefix + "  "))
                            else:
                                # Add key-value pairs with consistent formatting
                                items.append(f"{prefix}{key:<20}: {value}")
                        return items
                    
                    config_data = flatten_config(config)
                else:
                    config_data = ["Configuration file not found. Using defaults."]
                    config_data.append("")
                    config_data.append("Default configuration would include:")
                    config_data.append("- start_on_boot: false")
                    config_data.append("- shutdown_on_exit: false") 
                    config_data.append("- environment: development")
                
                run_fzf(config_data, "Current Configuration")
            elif choice == "Edit Configuration with Editor":
                if config_file.exists():
                    # Determine the appropriate editor to use
                    editor = os.environ.get('EDITOR', os.environ.get('VISUAL', 'nano'))
                    try:
                        subprocess.run([editor, str(config_file)])
                    except FileNotFoundError:
                        # If the preferred editor is not found, try alternatives
                        try:
                            subprocess.run(['nano', str(config_file)])
                        except FileNotFoundError:
                            try:
                                subprocess.run(['vim', str(config_file)])
                            except FileNotFoundError:
                                run_fzf([f"Could not find an editor. Please install nano, vim, or set EDITOR environment variable."], "Error")
                else:
                    # Create a default config file if it doesn't exist
                    default_config = {
                        "server_config": {
                            "start_on_boot": False,
                            "shutdown_on_exit": True,
                            "environment": "development",
                            "servers": {}
                        }
                    }
                    with open(config_file, 'w') as f:
                        json.dump(default_config, f, indent=2)
                    
                    editor = os.environ.get('EDITOR', os.environ.get('VISUAL', 'nano'))
                    try:
                        subprocess.run([editor, str(config_file)])
                    except FileNotFoundError:
                        try:
                            subprocess.run(['nano', str(config_file)])
                        except FileNotFoundError:
                            try:
                                subprocess.run(['vim', str(config_file)])
                            except FileNotFoundError:
                                run_fzf([f"Could not find an editor. Please install nano, vim, or set EDITOR environment variable."], "Error")
        elif selection == "List All Discovered Servers":
            servers = get_available_servers()
            if servers:
                # Get status for each server to display in fzf
                manager = SimpleMCPServerManager()
                pids = manager.load_pids()
                
                server_status_list = []
                
                for server_name in servers:
                    pid = pids.get(server_name)
                    status = "STOPPED"
                    if pid:
                        try:
                            process = psutil.Process(pid)
                            if process.is_running():
                                status = "RUNNING"
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                    # Format with consistent alignment
                    if pid and status == "RUNNING":
                        info_line = f"{server_name:<30} [{status:<7}] (PID: {pid})"
                    else:
                        info_line = f"{server_name:<30} [{status:<7}]"
                    server_status_list.append(info_line)
                
                # Color code the server list
                colored_server_status_list = []
                for info in server_status_list:
                    if "[RUNNING]" in info:
                        colored_info = f"\033[38;2;166;227;161m{info}\033[0m"  # Green for running
                    elif "[STOPPED]" in info:
                        colored_info = f"\033[38;2;243;139;168m{info}\033[0m"  # Pink for stopped
                    else:
                        colored_info = info
                    colored_server_status_list.append(colored_info)
                
                run_fzf(colored_server_status_list, f'Discovered Servers ({len(servers)} servers)')
            else:
                run_fzf(["No servers found (all servers are disabled in config)"], "Info")
        elif selection == "Modify Server Configuration":
            modify_server_config_menu(manager, config_file)
        elif selection == "Direct Server Config Toggles":
            direct_server_config_toggles(manager, config_file)


def direct_server_config_toggles(manager, config_file):
    """Quick configuration toggles for servers."""
    # Read current config
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
    except:
        run_fzf(["Configuration file not found. Using defaults."], "Info")
        return
    
    servers = config.get("server_config", {}).get("servers", {})
    
    if not servers:
        run_fzf(["No servers configured."], "Info")
        return
    
    # Create a list of servers with their current settings
    server_options = []
    for server_name, settings in servers.items():
        enabled = "YES" if settings.get("enabled", False) else "NO"
        start_on_boot = "YES" if settings.get("start_on_boot", False) else "NO"
        add_to_qwen = "YES" if settings.get("add_to_qwen", False) else "NO"
        
        option = f"{server_name} | Enabled: {enabled} | Boot: {start_on_boot} | Qwen: {add_to_qwen}"
        server_options.append(option)
    
    # Allow user to select servers for direct config changes
    selected = run_fzf(server_options, "Select server to modify (shows current config)", multi=True)
    
    if not selected:
        return
    
    # Parse the selected server names
    for selection in selected:
        server_name = selection.split(" | ")[0]
        
        # Get current config for this server
        server_config = servers.get(server_name, {})
        
        # Configuration options menu for this server
        config_options = [
            f"Toggle Enabled: {'Yes' if server_config.get('enabled', False) else 'No'}",
            f"Toggle Start on Boot: {'Yes' if server_config.get('start_on_boot', False) else 'No'}",
            f"Toggle Add to Qwen: {'Yes' if server_config.get('add_to_qwen', False) else 'No'}",
            f"Edit {server_name} individually",
            "Back to Configuration Menu"
        ]
        
        while True:
            config_selection = run_fzf(config_options, f"Configure '{server_name}'")
            
            if not config_selection or config_selection == "Back to Configuration Menu":
                return  # Return to parent menu
            elif config_selection.startswith("Toggle Enabled:"):
                # Toggle enabled status
                current_value = server_config.get('enabled', False)
                new_value = not current_value
                _update_server_config(config_file, server_name, "enabled", new_value)
                # Update local config
                server_config['enabled'] = new_value
                # Update our options list to reflect the change
                config_options[0] = f"Toggle Enabled: {'Yes' if new_value else 'No'}"
            elif config_selection.startswith("Toggle Start on Boot:"):
                # Toggle start on boot
                current_value = server_config.get('start_on_boot', False)
                new_value = not current_value
                _update_server_config(config_file, server_name, "start_on_boot", new_value)
                # Update local config
                server_config['start_on_boot'] = new_value
                # Update our options list to reflect the change
                config_options[1] = f"Toggle Start on Boot: {'Yes' if new_value else 'No'}"
            elif config_selection.startswith("Toggle Add to Qwen:"):
                # Toggle add to qwen
                current_value = server_config.get('add_to_qwen', False)
                new_value = not current_value
                _update_server_config(config_file, server_name, "add_to_qwen", new_value)
                # Update local config
                server_config['add_to_qwen'] = new_value
                # Update our options list to reflect the change
                config_options[2] = f"Toggle Add to Qwen: {'Yes' if new_value else 'No'}"
            elif config_selection == f"Edit {server_name} individually":
                modify_server_config_menu_single(manager, config_file, server_name)
                # After editing individually, break from this server's config loop to continue with next selected server
                break


def modify_server_config_menu(manager, config_file):
    """Menu for modifying server configuration with fzf."""
    # Read current config
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
    except:
        run_fzf(["Configuration file not found. Using defaults."], "Info")
        return
    
    servers = config.get("server_config", {}).get("servers", {})
    
    if not servers:
        run_fzf(["No servers configured."], "Info")
        return
    
    # Get the list of servers
    server_names = list(servers.keys())
    server_selection = run_fzf(server_names, "Select server to modify:")
    
    if not server_selection:
        return
    
    modify_server_config_menu_single(manager, config_file, server_selection)


def modify_server_config_menu_single(manager, config_file, server_selection):
    """Menu for modifying a single server's configuration."""
    # Read current config
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
    except:
        run_fzf(["Configuration file not found. Using defaults."], "Info")
        return
    
    servers = config.get("server_config", {}).get("servers", {})
    if server_selection not in servers:
        run_fzf([f"Server '{server_selection}' not found."], "Error")
        return
    
    # Get current config for this server
    server_config = servers.get(server_selection, {})
    
    # Configuration options menu
    config_options = [
        f"Enabled: {'Yes' if server_config.get('enabled', False) else 'No'}",
        f"Start on Boot: {'Yes' if server_config.get('start_on_boot', False) else 'No'}",
        f"Add to Qwen: {'Yes' if server_config.get('add_to_qwen', False) else 'No'}",
        "Back to Configuration Menu"
    ]
    
    while True:
        config_selection = run_fzf(config_options, f"Configure '{server_selection}'")
        
        if not config_selection or config_selection == "Back to Configuration Menu":
            return  # Return to parent menu
        elif config_selection.startswith("Enabled:"):
            # Toggle enabled status
            current_value = server_config.get('enabled', False)
            new_value = not current_value
            _update_server_config(config_file, server_selection, "enabled", new_value)
            # Update local config
            server_config['enabled'] = new_value
            # Update our options list to reflect the change
            config_options[0] = f"Enabled: {'Yes' if new_value else 'No'}"
        elif config_selection.startswith("Start on Boot:"):
            # Toggle start on boot
            current_value = server_config.get('start_on_boot', False)
            new_value = not current_value
            _update_server_config(config_file, server_selection, "start_on_boot", new_value)
            # Update local config
            server_config['start_on_boot'] = new_value
            # Update our options list to reflect the change
            config_options[1] = f"Start on Boot: {'Yes' if new_value else 'No'}"
        elif config_selection.startswith("Add to Qwen:"):
            # Toggle add to qwen
            current_value = server_config.get('add_to_qwen', False)
            new_value = not current_value
            _update_server_config(config_file, server_selection, "add_to_qwen", new_value)
            # Update local config
            server_config['add_to_qwen'] = new_value
            # Update our options list to reflect the change
            config_options[2] = f"Add to Qwen: {'Yes' if new_value else 'No'}"


def _update_server_config(config_file, server_name, property_name, value):
    """Helper function to update a server configuration property."""
    try:
        # Load current config
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
        else:
            config = {"server_config": {"servers": {}}}
        
        # Ensure the servers section exists
        if "server_config" not in config:
            config["server_config"] = {"servers": {}}
        if "servers" not in config["server_config"]:
            config["server_config"]["servers"] = {}
        
        # Get the server config, creating it if it doesn't exist
        server_configs = config["server_config"]["servers"]
        if server_name not in server_configs:
            server_configs[server_name] = {
                "enabled": False,
                "start_on_boot": False,
                "add_to_qwen": False
            }
        
        # Update the specific property
        server_configs[server_name][property_name] = value
        
        # Write updated config back to file
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        run_fzf([f"Error updating config for {server_name}: {e}"], "Error")


def qwen_integration_menu():
    """Qwen integration menu with fzf selection."""
    manager = SimpleMCPServerManager()
    qwen_manager = SimpleQwenMCPManager(mcps_dir=manager.mcps_dir)
    
    options = [
        "Integrate MCPs with Qwen",
        "List Integrated MCPs",
        "Remove All MCPs from Qwen",
        "Show Qwen Config Path",
        "Back to Main Menu"
    ]
    
    while True:
        selection = run_fzf(options, "Qwen Integration")
        
        if not selection or selection == "Back to Main Menu":
            return  # Return to main menu
        elif selection == "Integrate MCPs with Qwen":
            confirm_options = ["Yes", "No"]
            confirm = run_fzf(confirm_options, "Integrate MCPs with Qwen?")
            if confirm == "Yes":
                qwen_manager.integrate_with_qwen()
                run_fzf(["MCPs integrated with Qwen"], "Info")
            else:
                run_fzf(["Integration cancelled."], "Info")
        elif selection == "List Integrated MCPs":
            mcps = qwen_manager.settings.get("mcpServers", {})
            if mcps:
                mcp_list = []
                default_server = qwen_manager.settings.get("defaultServer")
                
                for server_id in mcps:
                    status = "ENABLED" if mcps[server_id].get('enabled', True) else "DISABLED"
                    default_marker = " (DEFAULT)" if server_id == default_server else ""
                    mcp_list.append(f"{server_id:<30} [{status:<8}]{default_marker}")
                
                # Color code the MCP list
                colored_mcp_list = []
                for info in mcp_list:
                    if "[ENABLED]" in info:
                        colored_info = f"\033[38;2;166;227;161m{info}\033[0m"  # Green for enabled
                    elif "[DISABLED]" in info:
                        colored_info = f"\033[38;2;243;139;168m{info}\033[0m"  # Pink for disabled
                    else:
                        colored_info = info
                    colored_mcp_list.append(colored_info)
                
                run_fzf(colored_mcp_list, f'Integrated MCPs ({len(mcps)} servers)')
            else:
                run_fzf(["No MCP servers are currently integrated with Qwen"], "Info")
        elif selection == "Remove All MCPs from Qwen":
            confirm_options = ["Yes", "No"]
            confirm = run_fzf(confirm_options, "Remove ALL MCPs from Qwen? This cannot be undone!")
            if confirm == "Yes":
                qwen_manager.remove_all_mcps()
                run_fzf(["All MCPs removed from Qwen"], "Info")
            else:
                run_fzf(["Removal cancelled."], "Info")
        elif selection == "Show Qwen Config Path":
            path = qwen_manager.get_qwen_config_path()
            run_fzf([path], "Qwen Config Path")


def main_menu():
    """Improved main menu with streamlined options."""
    main_options = [
        "🚀 Quick Actions",
        "🔧 Server Management", 
        "⚙️  Configuration",
        "🌐 Qwen Integration",
        "📝 Environment (.env) Management",
        "📊 Dashboard View",
        "🚪 Exit"
    ]
    
    while True:
        selection = run_fzf(main_options, "MCP Server Manager - Main Menu")
        
        if not selection or selection == "🚪 Exit":
            print("Goodbye!")
            break
        elif selection == "🚀 Quick Actions":
            # Provide common operations in a single menu
            quick_actions = [
                "Start All Servers",
                "Stop All Servers", 
                "Restart All Servers",
                "Show Dashboard",
                "Integrate All with Qwen",
                "Back to Main Menu"
            ]
            action = run_fzf(quick_actions, "Quick Actions")
            
            if action == "Start All Servers":
                manager = SimpleMCPServerManager()
                confirm_options = ["Yes", "No"]
                confirm = run_fzf(confirm_options, "Start all servers?")
                if confirm == "Yes":
                    manager.start_all()
                    run_fzf(["Started all servers"], "Info")
                else:
                    run_fzf(["Start all operation cancelled."], "Info")
            elif action == "Stop All Servers":
                manager = SimpleMCPServerManager()
                confirm_options = ["Yes", "No"]
                confirm = run_fzf(confirm_options, "Stop all servers?")
                if confirm == "Yes":
                    manager.stop_all()
                    run_fzf(["Stopped all servers"], "Info")
                else:
                    run_fzf(["Stop all operation cancelled."], "Info")
            elif action == "Restart All Servers":
                manager = SimpleMCPServerManager()
                confirm_options = ["Yes", "No"]
                confirm = run_fzf(confirm_options, "Restart all servers?")
                if confirm == "Yes":
                    manager.stop_all()
                    time.sleep(2)  # Wait for all servers to stop
                    manager.start_all()
                    run_fzf(["Restarted all servers"], "Info")
                else:
                    run_fzf(["Restart all operation cancelled."], "Info")
            elif action == "Show Dashboard":
                dashboard_view()
            elif action == "Integrate All with Qwen":
                manager = SimpleMCPServerManager()
                qwen_manager = SimpleQwenMCPManager(mcps_dir=manager.mcps_dir)
                confirm_options = ["Yes", "No"]
                confirm = run_fzf(confirm_options, "Integrate MCPs with Qwen?")
                if confirm == "Yes":
                    qwen_manager.integrate_with_qwen()
                    run_fzf(["MCPs integrated with Qwen"], "Info")
                else:
                    run_fzf(["Integration cancelled."], "Info")
            elif not action or action == "Back to Main Menu":
                return  # Return to main menu
        elif selection == "🔧 Server Management":
            server_management_menu()
        elif selection == "⚙️  Configuration":
            config_management_menu()
        elif selection == "🌐 Qwen Integration":
            qwen_integration_menu()
        elif selection == "📝 Environment (.env) Management":
            env_management_menu()
        elif selection == "📊 Dashboard View":
            dashboard_view()


def main():
    parser = argparse.ArgumentParser(
        description="Improved FZF Enhanced MCP Server Manager - Enhanced command-line interface for managing MCP servers with fuzzy selection capabilities",
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
  %(prog)s config-list                  # List server configurations
  %(prog)s config-edit server-name      # Edit server configuration
  %(prog)s env                          # Manage environment (.env) files
  %(prog)s env-create                   # Create .env file
  %(prog)s env-edit                     # Edit .env file
  %(prog)s env-view                     # View .env file contents
  %(prog)s env-delete                   # Delete .env file
  %(prog)s env-validate                 # Validate .env file format
  %(prog)s list                         # List discovered servers
  %(prog)s --fzf                        # Start interactive fzf mode
  %(prog)s --verbose                    # Show detailed logs

Command Aliases:
  start (s), stop (sp), restart (r), status (st)
  start-all (sa), stop-all (spa), restart-all (ra)
  integrate (int), list-qwen (lq), qwen-config-path (qcp)
  config-show (cfg), config-list (clist), config-edit (cedit)
  env-create, env-edit, env-view, env-delete, env-validate
  list (ls)

Environment Variables:
  START_ON_BOOT, SHUTDOWN_ON_EXIT, ENVIRONMENT, MCP_LOG_LEVEL
        """
    )
    parser.add_argument(
        "action", 
        nargs="?",
        choices=[
            "start", "s", "stop", "sp", "restart", "r", "status", "st", 
            "start-all", "sa", "stop-all", "spa", "restart-all", "ra",
            "integrate", "int", "list-qwen", "lq", "remove-all-qwen", "qwen-config-path", "qcp",
            "config-show", "cfg", "config-list", "clist", "config-edit", "cedit", "list", "ls", 
            "env", "env-create", "env-edit", "env-view", "env-delete", "env-validate",
            "interactive", "fzf", "dashboard"
        ],
        help="Action to perform (use 'interactive' or 'fzf' for fzf interface, or omit for fzf by default)"
    )
    parser.add_argument(
        "--fzf", 
        action="store_true",
        help="Start interactive fzf mode"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Show detailed logs (sets logging level to INFO)"
    )
    parser.add_argument(
        "server", 
        nargs="?",
        help="Server name (directory names from mcps/, or 'all')"
    )
    
    args = parser.parse_args()
    
    # Set logging level based on verbose flag
    if args.verbose:
        os.environ['MCP_LOG_LEVEL'] = 'INFO'
    else:
        os.environ['MCP_LOG_LEVEL'] = 'WARNING'
    
    # Check if we should enter fzf mode based on flag or action
    if args.fzf or args.action in ['interactive', 'fzf'] or (args.action is None and os.isatty(0)):
        main_menu()
        return 0  # Success exit code
    
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
    elif action in ['int']:
        action = 'integrate'
    elif action in ['lq']:
        action = 'list-qwen'
    elif action in ['qcp']:
        action = 'qwen-config-path'
    elif action in ['cfg']:
        action = 'config-show'
    elif action in ['clist']:
        action = 'config-list'
    elif action in ['cedit']:
        action = 'config-edit'
    elif action in ['ls']:
        action = 'list'
    elif action in ['env-create']:
        action = 'env'
        # Set a flag to create env file
        os.environ['_CLI_ENV_ACTION'] = 'create'
    elif action in ['env-edit']:
        action = 'env'
        os.environ['_CLI_ENV_ACTION'] = 'edit'
    elif action in ['env-view']:
        action = 'env'
        os.environ['_CLI_ENV_ACTION'] = 'view'
    elif action in ['env-delete']:
        action = 'env'
        os.environ['_CLI_ENV_ACTION'] = 'delete'
    elif action in ['env-validate']:
        action = 'env'
        os.environ['_CLI_ENV_ACTION'] = 'validate'
    
    try:
        manager = SimpleMCPServerManager()
    except Exception as e:
        run_fzf([f"Error initializing server manager: {e}"], "Error")
        return 1  # Error exit code
    
    if action == "start":
        if args.server == "all":
            # Direct operation without confirmation for CLI
            manager.start_all()
            print("Started all servers")
        elif args.server:
            # Direct operation for specific server
            all_servers = get_available_servers()
            if args.server.lower() in [s.lower() for s in all_servers]:
                # Direct match
                matching_server = next(s for s in all_servers if s.lower() == args.server.lower())
                manager.start_server(matching_server)
                print(f"Started {matching_server}")
            else:
                # Find partial matches
                partial_matches = [s for s in all_servers if args.server.lower() in s.lower()]
                if len(partial_matches) == 1:
                    manager.start_server(partial_matches[0])
                    print(f"Started {partial_matches[0]}")
                elif len(partial_matches) > 1:
                    print(f"Multiple matches for '{args.server}': {', '.join(partial_matches)}")
                else:
                    print(f"Server '{args.server}' not found. Available servers: {', '.join(all_servers)}")
        else:
            print("Please specify a server name or 'all'")
    
    elif action == "stop":
        if args.server == "all":
            # Direct operation without confirmation for CLI
            manager.stop_all()
            print("Stopped all servers")
        elif args.server:
            # Direct operation for specific server
            all_servers = get_available_servers()
            if args.server.lower() in [s.lower() for s in all_servers]:
                # Direct match
                matching_server = next(s for s in all_servers if s.lower() == args.server.lower())
                manager.stop_server(matching_server)
                print(f"Stopped {matching_server}")
            else:
                # Find partial matches
                partial_matches = [s for s in all_servers if args.server.lower() in s.lower()]
                if len(partial_matches) == 1:
                    manager.stop_server(partial_matches[0])
                    print(f"Stopped {partial_matches[0]}")
                elif len(partial_matches) > 1:
                    print(f"Multiple matches for '{args.server}': {', '.join(partial_matches)}")
                else:
                    print(f"Server '{args.server}' not found. Available servers: {', '.join(all_servers)}")
        else:
            print("Please specify a server name or 'all'")
            
    elif action == "restart":
        if args.server == "all":
            # Direct operation without confirmation for CLI
            manager.stop_all()
            time.sleep(2)  # Wait for all servers to stop
            manager.start_all()
            print("Restarted all servers")
        elif args.server:
            # Direct operation for specific server
            all_servers = get_available_servers()
            if args.server.lower() in [s.lower() for s in all_servers]:
                # Direct match
                matching_server = next(s for s in all_servers if s.lower() == args.server.lower())
                manager.restart_server(matching_server)
                print(f"Restarted {matching_server}")
            else:
                # Find partial matches
                partial_matches = [s for s in all_servers if args.server.lower() in s.lower()]
                if len(partial_matches) == 1:
                    manager.restart_server(partial_matches[0])
                    print(f"Restarted {partial_matches[0]}")
                elif len(partial_matches) > 1:
                    print(f"Multiple matches for '{args.server}': {', '.join(partial_matches)}")
                else:
                    print(f"Server '{args.server}' not found. Available servers: {', '.join(all_servers)}")
        else:
            print("Please specify a server name or 'all'")
            
    elif action == "status":
        # Create status info for display
        pids = manager.load_pids()
        server_info = []
        running_count = 0
        
        for server_name in manager.servers.keys():
            pid = pids.get(server_name)
            status = "STOPPED"
            if pid:
                try:
                    process = psutil.Process(pid)
                    if process.is_running():
                        status = "RUNNING"
                        running_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Format with consistent alignment
            if pid and status == "RUNNING":
                info_line = f"{server_name:<30} [{status:<7}] (PID: {pid})"
            else:
                info_line = f"{server_name:<30} [{status:<7}]"
            server_info.append(info_line)
        
        # Add summary to server_info list
        summary = f"Summary: {running_count}/{len(manager.servers)} servers running"
        server_info.append("")
        server_info.append(summary)
        server_info.append(f"Environment: {manager.environment}")
        
        for info in server_info:
            print(info)
    
    elif action == "dashboard":
        # Show dashboard view in CLI format
        server_info, running_count, total_count = get_server_status_info()
        print(f"Dashboard View:")
        print("="*50)
        for info in server_info[:-3]:  # exclude summary items
            print(info)
        print(f"\nSummary: {running_count}/{total_count} servers running")
        print(f"Environment: {manager.environment}")
        
    elif action == "env":
        # Handle .env file management through CLI
        from pathlib import Path
        env_file = Path(__file__).parent / ".env"
        env_action = os.environ.get('_CLI_ENV_ACTION', 'menu')  # Default to menu if no specific action
        
        if env_action == 'create':
            if env_file.exists():
                print(f".env file already exists at: {env_file}")
                overwrite = input("File exists. Overwrite? (y/N): ")
                if overwrite.lower() == 'y':
                    create_env_file_cli(env_file)
                else:
                    print("Operation cancelled.")
            else:
                create_env_file_cli(env_file)
        elif env_action == 'edit':
            if env_file.exists():
                editor = os.environ.get('EDITOR', os.environ.get('VISUAL', 'nano'))
                try:
                    subprocess.run([editor, str(env_file)])
                    print(f"Successfully edited .env file")
                except FileNotFoundError:
                    try:
                        subprocess.run(['nano', str(env_file)])
                    except FileNotFoundError:
                        try:
                            subprocess.run(['vim', str(env_file)])
                        except FileNotFoundError:
                            print(f"Could not find an editor. Please install nano, vim, or set EDITOR environment variable.")
            else:
                print(f".env file does not exist. Create it first with 'env-create'.")
        elif env_action == 'view':
            if env_file.exists():
                with open(env_file, 'r') as f:
                    content = f.read()
                print("=== .env File Contents ===")
                print(content)
            else:
                print(f".env file does not exist.")
        elif env_action == 'delete':
            if env_file.exists():
                confirm = input(f"Delete .env file at {env_file}? This cannot be undone! (y/N): ")
                if confirm.lower() == 'y':
                    env_file.unlink()
                    print(f"Successfully deleted .env file")
                else:
                    print("Deletion cancelled.")
            else:
                print(f".env file does not exist.")
        elif env_action == 'validate':
            if env_file.exists():
                validate_env_file_cli(env_file)
            else:
                print(f".env file does not exist.")
        else:
            # Default to interactive menu
            env_management_menu()
        
        # Clean up the environment variable
        if '_CLI_ENV_ACTION' in os.environ:
            del os.environ['_CLI_ENV_ACTION']
        
    elif action == "start-all":
        manager.start_all()
        print("Started all servers")
        
    elif action == "stop-all":
        manager.stop_all()
        print("Stopped all servers")
        
    elif action == "restart-all":
        manager.stop_all()
        time.sleep(2)  # Wait for all servers to stop
        manager.start_all()
        print("Restarted all servers")
    
    elif action == "integrate":
        qwen_manager = SimpleQwenMCPManager(mcps_dir=manager.mcps_dir)
        qwen_manager.integrate_with_qwen()
        print("MCPs integrated with Qwen")
    
    elif action == "list-qwen":
        qwen_manager = SimpleQwenMCPManager(mcps_dir=manager.mcps_dir)
        mcps = qwen_manager.settings.get("mcpServers", {})
        if mcps:
            for server_id in mcps:
                status = "ENABLED" if mcps[server_id].get('enabled', True) else "DISABLED"
                default_marker = " (DEFAULT)" if server_id == qwen_manager.settings.get("defaultServer") else ""
                print(f"{server_id} [{status}]{default_marker}")
        else:
            print("No MCP servers are currently integrated with Qwen")
    
    elif action == "remove-all-qwen":
        qwen_manager = SimpleQwenMCPManager(mcps_dir=manager.mcps_dir)
        qwen_manager.remove_all_mcps()
        print("All MCPs removed from Qwen")
    
    elif action == "qwen-config-path":
        qwen_manager = SimpleQwenMCPManager(mcps_dir=manager.mcps_dir)
        config_path = qwen_manager.get_qwen_config_path()
        print(f"Qwen Configuration Path: {config_path}")
    
    elif action == "config-show":
        config_file = manager.project_root / "config.json"
        
        # Determine if we're running in interactive mode or just showing config
        if args.server == "edit":  # Special flag to edit
            if config_file.exists():
                # Determine the appropriate editor to use
                editor = os.environ.get('EDITOR', os.environ.get('VISUAL', 'nano'))
                try:
                    subprocess.run([editor, str(config_file)])
                except FileNotFoundError:
                    # If the preferred editor is not found, try alternatives
                    try:
                        subprocess.run(['nano', str(config_file)])
                    except FileNotFoundError:
                        try:
                            subprocess.run(['vim', str(config_file)])
                        except FileNotFoundError:
                            print(f"Could not find an editor. Please install nano, vim, or set EDITOR environment variable.")
            else:
                # Create a default config file if it doesn't exist
                default_config = {
                    "server_config": {
                        "start_on_boot": False,
                        "shutdown_on_exit": True,
                        "environment": "development",
                        "servers": {}
                    }
                }
                with open(config_file, 'w') as f:
                    json.dump(default_config, f, indent=2)
                
                editor = os.environ.get('EDITOR', os.environ.get('VISUAL', 'nano'))
                try:
                    subprocess.run([editor, str(config_file)])
                except FileNotFoundError:
                    try:
                        subprocess.run(['nano', str(config_file)])
                    except FileNotFoundError:
                        try:
                            subprocess.run(['vim', str(config_file)])
                        except FileNotFoundError:
                            print(f"Could not find an editor. Please install nano, vim, or set EDITOR environment variable.")
        else:
            # Just show the configuration in CLI
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                # Format the configuration as a user-friendly list
                def print_config(config_obj, prefix=""):
                    for key, value in config_obj.items():
                        if isinstance(value, dict):
                            # Add section header
                            print(f"[{key}]")
                            # Recursively add nested items with indentation
                            print_config(value, prefix + "  ")
                        else:
                            # Add key-value pairs
                            print(f"{prefix}{key}: {value}")
                
                print_config(config)
            else:
                print("Configuration file not found. Using defaults.")
                print("")
                print("Default configuration would include:")
                print("- start_on_boot: false")
                print("- shutdown_on_exit: false") 
                print("- environment: development")
    
    elif action == "list":
        servers = get_available_servers()
        if servers:
            # Get status for each server to display
            pids = manager.load_pids()
            
            for server_name in servers:
                pid = pids.get(server_name)
                status = "STOPPED"
                if pid:
                    try:
                        process = psutil.Process(pid)
                        if process.is_running():
                            status = "RUNNING"
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                # Format with consistent alignment
                if pid and status == "RUNNING":
                    info_line = f"{server_name:<30} [{status:<7}] (PID: {pid})"
                else:
                    info_line = f"{server_name:<30} [{status:<7}]"
                print(info_line)
        else:
            print("No servers found (all servers are disabled in config)")
    
    elif action == "config-list":
        config_file = manager.project_root / "config.json"
        if not config_file.exists():
            print("Configuration file not found. Using defaults.")
            return 1
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        print("MCP Server Configuration List:")
        print("=" * 60)
        
        server_config = config.get("server_config", {})
        servers = server_config.get("servers", {})
        
        if not servers:
            print("No servers configured.")
            return 0
        
        # Add header
        print(f"{'Server Name':<30} {'Enabled':<8} {'Boot':<8} {'Qwen':<8}")
        print("-" * 54)
        
        # Add each server's configuration
        for server_name, settings in servers.items():
            enabled = "YES" if settings.get("enabled", False) else "NO"
            start_on_boot = "YES" if settings.get("start_on_boot", False) else "NO"
            add_to_qwen = "YES" if settings.get("add_to_qwen", False) else "NO"
            
            # Ensure clean formatting by using proper spacing
            print(f"{server_name:<30} {enabled:<8} {start_on_boot:<8} {add_to_qwen:<8}")
        
        print("")
        print("Legend:")
        print("  Enabled: Whether the server is enabled in the manager")
        print("  Boot: Whether the server starts automatically on boot")
        print("  Qwen: Whether the server is integrated with Qwen")
        
        return 0  # Success exit code
    
    elif action == "config-edit":
        config_file = manager.project_root / "config.json"
        if not config_file.exists():
            print("Configuration file not found. Nothing to modify.")
            return 1
        
        if not args.server:
            print("Please specify a server name to edit.")
            print("Usage: cli.py config-edit <server-name>")
            return 1
        
        server_name = args.server
        
        # Load current config
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Check if server exists in config
        servers = config.get("server_config", {}).get("servers", {})
        if server_name not in servers:
            available_servers = list(servers.keys())
            print(f"Server '{server_name}' not found in configuration.")
            if available_servers:
                print("Available servers:")
                for name in available_servers:
                    print(f"  - {name}")
            return 1
        
        # Get current settings
        current_settings = servers[server_name]
        enabled = current_settings.get("enabled", False)
        start_on_boot = current_settings.get("start_on_boot", False)
        add_to_qwen = current_settings.get("add_to_qwen", False)
        
        print(f"Current configuration for {server_name}:")
        print(f"  Enabled: {enabled}")
        print(f"  Start on boot: {start_on_boot}")
        print(f"  Add to Qwen: {add_to_qwen}")
        
        changes_made = False
        
        # For CLI, we'll provide a simple method to update settings
        print("\nWhich setting would you like to modify?")
        print("1. Enabled")
        print("2. Start on boot") 
        print("3. Add to Qwen")
        print("4. All settings")
        print("5. Cancel")
        
        choice = input("Enter your choice (1-5): ")
        
        if choice == '5':
            print("No changes made.")
            return 0
        
        if choice in ['1', '4']:
            enabled_input = input(f"Set 'enabled' for {server_name} (current: {enabled}, enter true/false): ")
            if enabled_input.lower() in ['true', '1', 'yes']:
                servers[server_name]['enabled'] = True
                changes_made = True
            elif enabled_input.lower() in ['false', '0', 'no']:
                servers[server_name]['enabled'] = False
                changes_made = True
        
        if choice in ['2', '4']:
            boot_input = input(f"Set 'start_on_boot' for {server_name} (current: {start_on_boot}, enter true/false): ")
            if boot_input.lower() in ['true', '1', 'yes']:
                servers[server_name]['start_on_boot'] = True
                changes_made = True
            elif boot_input.lower() in ['false', '0', 'no']:
                servers[server_name]['start_on_boot'] = False
                changes_made = True
        
        if choice in ['3', '4']:
            qwen_input = input(f"Set 'add_to_qwen' for {server_name} (current: {add_to_qwen}, enter true/false): ")
            if qwen_input.lower() in ['true', '1', 'yes']:
                servers[server_name]['add_to_qwen'] = True
                changes_made = True
            elif qwen_input.lower() in ['false', '0', 'no']:
                servers[server_name]['add_to_qwen'] = False
                changes_made = True
        
        if choice not in ['1', '2', '3', '4']:
            print("Invalid choice. No changes made.")
            return 1
        
        if changes_made:
            # Save the updated config
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"Configuration for {server_name} updated successfully.")
            return 0
        else:
            print("No changes were made.")
        return 0  # Success exit code
    
    return 0  # Success exit code for all other cases


if __name__ == "__main__":
    sys.exit(main())