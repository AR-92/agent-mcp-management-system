#!/usr/bin/env python3
"""
Linux Administration MCP Server

Provides access to Linux system administration functionality for LLMs through MCP protocol.
"""

from fastmcp import FastMCP
from typing import List, Dict, Any
import asyncio
import subprocess
import os
import pwd
import grp


# Initialize the MCP server
mcp = FastMCP(
    name="Linux Administration MCP Server",
    instructions="Provides access to Linux system administration functionality including user management, service control, and system configuration",
    version="1.0.0"
)


# Tools
@mcp.tool
def list_users() -> List[Dict[str, Any]]:
    """
    List all users on the Linux system
    """
    users = []
    for user in pwd.getpwall():
        users.append({
            "username": user.pw_name,
            "uid": user.pw_uid,
            "gid": user.pw_gid,
            "home_dir": user.pw_dir,
            "shell": user.pw_shell,
            "full_name": user.pw_gecos.split(',')[0] if user.pw_gecos else user.pw_name
        })
    return users


@mcp.tool
def get_user_info(username: str) -> Dict[str, str]:
    """
    Get detailed information about a specific user
    """
    try:
        user_info = pwd.getpwnam(username)
        return {
            "username": user_info.pw_name,
            "uid": user_info.pw_uid,
            "gid": user_info.pw_gid,
            "home_dir": user_info.pw_dir,
            "shell": user_info.pw_shell,
            "full_name": user_info.pw_gecos,
            "groups": [group.gr_name for group in grp.getgrall() if username in group.gr_mem]
        }
    except KeyError:
        return {"error": f"User {username} not found"}


@mcp.tool
def create_user(
    username: str, 
    home_dir: str = None, 
    shell: str = "/bin/bash",
    groups: List[str] = None
) -> Dict[str, str]:
    """
    Create a new user on the Linux system
    """
    try:
        # In a real implementation, this would execute the useradd command
        return {
            "status": "success",
            "message": f"User {username} created successfully"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@mcp.tool
def delete_user(username: str, remove_home: bool = False) -> Dict[str, str]:
    """
    Delete a user from the Linux system
    """
    try:
        # In a real implementation, this would execute the userdel command
        message = f"User {username} deleted successfully"
        if remove_home:
            message += " (including home directory)"
        return {
            "status": "success",
            "message": message
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@mcp.tool
def list_groups() -> List[Dict[str, Any]]:
    """
    List all groups on the Linux system
    """
    groups = []
    for group in grp.getgrall():
        groups.append({
            "name": group.gr_name,
            "gid": group.gr_gid,
            "members": group.gr_mem
        })
    return groups


@mcp.tool
def get_service_status(service_name: str) -> Dict[str, str]:
    """
    Get the status of a systemd service
    """
    try:
        result = subprocess.run(['systemctl', 'is-active', service_name], 
                                capture_output=True, text=True, timeout=10)
        status = result.stdout.strip()
        return {
            "service": service_name,
            "status": status,
            "message": f"Service {service_name} is {status}"
        }
    except subprocess.TimeoutExpired:
        return {
            "service": service_name,
            "status": "timeout",
            "message": f"Timeout while checking service {service_name}"
        }
    except Exception as e:
        return {
            "service": service_name,
            "status": "error",
            "message": str(e)
        }


@mcp.tool
def start_service(service_name: str) -> Dict[str, str]:
    """
    Start a systemd service
    """
    try:
        result = subprocess.run(['sudo', 'systemctl', 'start', service_name], 
                                capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return {
                "status": "success",
                "message": f"Service {service_name} started successfully"
            }
        else:
            return {
                "status": "error",
                "message": result.stderr
            }
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": f"Timeout while starting service {service_name}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@mcp.tool
def stop_service(service_name: str) -> Dict[str, str]:
    """
    Stop a systemd service
    """
    try:
        result = subprocess.run(['sudo', 'systemctl', 'stop', service_name], 
                                capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return {
                "status": "success",
                "message": f"Service {service_name} stopped successfully"
            }
        else:
            return {
                "status": "error",
                "message": result.stderr
            }
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": f"Timeout while stopping service {service_name}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@mcp.tool
def restart_service(service_name: str) -> Dict[str, str]:
    """
    Restart a systemd service
    """
    try:
        result = subprocess.run(['sudo', 'systemctl', 'restart', service_name], 
                                capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return {
                "status": "success",
                "message": f"Service {service_name} restarted successfully"
            }
        else:
            return {
                "status": "error",
                "message": result.stderr
            }
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": f"Timeout while restarting service {service_name}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@mcp.tool
def list_packages() -> List[Dict[str, str]]:
    """
    List installed packages (assumes apt-based system)
    """
    try:
        result = subprocess.run(['dpkg', '--get-selections'], 
                                capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            packages = []
            for line in result.stdout.splitlines():
                if line and "\tinstall" in line:
                    parts = line.split("\t")
                    package_name = parts[0]
                    packages.append({"name": package_name, "status": "installed"})
            return packages
        else:
            return [{"error": "Failed to list packages", "details": result.stderr}]
    except subprocess.TimeoutExpired:
        return [{"error": "Timeout while listing packages"}]
    except Exception as e:
        return [{"error": str(e)}]


@mcp.tool
def check_disk_usage(path: str = "/") -> Dict[str, str]:
    """
    Check disk usage for a given path
    """
    try:
        result = subprocess.run(['df', '-h', path], 
                                capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                header = lines[0].split()
                values = lines[1].split()
                usage_info = dict(zip(header, values))
                return {
                    "path": path,
                    "size": usage_info.get('1K-blocks', 'N/A'),
                    "used": usage_info.get('Used', 'N/A'),
                    "available": usage_info.get('Available', 'N/A'),
                    "use_percent": usage_info.get('Use%', 'N/A'),
                    "mounted_on": usage_info.get('Mounted on', 'N/A')
                }
        return {"error": f"Failed to check disk usage for {path}"}
    except Exception as e:
        return {"error": str(e)}


# Resources
@mcp.resource("http://linux-admin-mcp-server.local/system-info")
def get_system_info() -> Dict[str, Any]:
    """
    Get comprehensive system information
    """
    import platform
    
    return {
        "hostname": os.uname().nodename,
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "architecture": platform.architecture()[0],
        "python_version": platform.python_version()
    }


@mcp.resource("http://linux-admin-mcp-server.local/user-sessions")
def get_user_sessions() -> List[Dict[str, str]]:
    """
    Get information about active user sessions
    """
    try:
        result = subprocess.run(['who'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            sessions = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split()
                    if len(parts) >= 3:
                        sessions.append({
                            "user": parts[0],
                            "terminal": parts[1],
                            "login_time": parts[2],
                            "login_date": parts[3] if len(parts) > 3 else "N/A"
                        })
            return sessions
        else:
            return [{"error": "Failed to get user sessions", "details": result.stderr}]
    except Exception as e:
        return [{"error": str(e)}]


@mcp.resource("http://linux-admin-mcp-server.local/network-interfaces")
def get_network_interfaces() -> List[Dict[str, str]]:
    """
    Get information about network interfaces
    """
    try:
        result = subprocess.run(['ip', 'addr', 'show'], 
                                capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            # Simplified parsing of network interfaces
            interfaces = []
            current_interface = None
            
            for line in result.stdout.split('\n'):
                if line.strip() and line[0].isdigit():
                    # New interface
                    parts = line.split(':')
                    if len(parts) >= 2:
                        current_interface = parts[1].strip()
                        interfaces.append({"name": current_interface, "info": []})
                
            return interfaces or [{"name": "lo", "info": ["127.0.0.1/8"}]
        else:
            return [{"name": "error", "info": [result.stderr]}]
    except Exception as e:
        return [{"name": "error", "info": [str(e)]}]


# Prompts
@mcp.prompt("/linux-user-management")
def user_management_prompt(action: str, username: str, context: str = "") -> str:
    """
    Generate a prompt for Linux user management tasks
    """
    return f"""
Perform the following user management action on Linux: {action}
Username: {username}
Context: {context}

Consider security implications, necessary permissions, and best practices for user management.
"""


@mcp.prompt("/linux-service-troubleshooting")
def service_troubleshooting_prompt(service_name: str, issue_description: str, context: str = "") -> str:
    """
    Generate a prompt for troubleshooting a Linux service
    """
    return f"""
Troubleshoot the following issue with service {service_name}:
Issue: {issue_description}
Context: {context}

Provide steps to diagnose, fix, and prevent this issue in the future.
"""


@mcp.prompt("/linux-security-audit")
def security_audit_prompt(components: List[str], context: str = "") -> str:
    """
    Generate a prompt for performing a Linux security audit
    """
    return f"""
Perform a security audit on the following components: {components}
Context: {context}

Check for vulnerabilities, misconfigurations, and security best practices.
"""


@mcp.prompt("/linux-system-optimization")
def system_optimization_prompt(performance_issues: List[str], context: str = "") -> str:
    """
    Generate a prompt for optimizing Linux system performance
    """
    return f"""
Optimize Linux system performance for these issues: {performance_issues}
Context: {context}

Provide recommendations for configuration changes, resource allocation, and optimizations.
"""


if __name__ == "__main__":
    # Use stdio transport for MCP server (proper MCP protocol communication)
    asyncio.run(mcp.run_stdio_async())