"""
System Administration Agent using Strands Agents SDK

This agent uses multiple MCPs to provide comprehensive system administration capabilities,
including Linux administration, process management, server health monitoring, and log viewing.
"""

from strandsagents import Agent
from typing import Dict, Any, List
import json
import psutil


def list_system_users() -> List[Dict[str, Any]]:
    """
    List all system users using Linux administration MCP.
    
    Returns:
        List of dictionaries containing user information
    """
    # This would connect to the Linux Admin MCP server in a real implementation
    return [
        {
            "username": "root",
            "uid": 0,
            "gid": 0,
            "home": "/root",
            "shell": "/bin/bash",
            "is_admin": True
        },
        {
            "username": "rana",
            "uid": 1000,
            "gid": 1000,
            "home": "/home/rana",
            "shell": "/bin/bash",
            "is_admin": True
        },
        {
            "username": "www-data",
            "uid": 33,
            "gid": 33,
            "home": "/var/www",
            "shell": "/usr/sbin/nologin",
            "is_admin": False
        }
    ]


def list_running_processes() -> List[Dict[str, Any]]:
    """
    List all running processes on the system.
    
    Returns:
        List of dictionaries containing process information
    """
    # This would connect to the Process Manager MCP server in a real implementation
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'username', 'status', 'cpu_percent', 'memory_percent']):
        try:
            proc_info = proc.info
            processes.append({
                "pid": proc_info['pid'],
                "name": proc_info['name'],
                "username": proc_info['username'],
                "status": proc_info['status'],
                "cpu_percent": proc_info['cpu_percent'],
                "memory_percent": proc_info['memory_percent']
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass  # Skip processes that are no longer available
    return processes[:20]  # Return first 20 processes


def get_server_health() -> Dict[str, Any]:
    """
    Get comprehensive server health information.
    
    Returns:
        Dictionary containing server health metrics
    """
    # This would connect to the Server Health MCP server in a real implementation
    return {
        "timestamp": "2023-10-02T10:30:00Z",
        "cpu_usage_percent": 15.3,
        "memory_usage_percent": 42.7,
        "disk_usage_percent": 65.2,
        "network_status": "healthy",
        "load_average": [0.12, 0.08, 0.05],
        "uptime": "5 days, 3 hours, 42 minutes",
        "service_status": {
            "ssh": "running",
            "nginx": "running",
            "postgresql": "running",
            "firewall": "active"
        }
    }


def read_system_logs(file_path: str = "/var/log/syslog", lines: int = 20) -> List[str]:
    """
    Read system log file.
    
    Args:
        file_path: Path to the log file to read
        lines: Number of lines to read from the end of the file
        
    Returns:
        List of log entries
    """
    # This would connect to the Log Viewer MCP server in a real implementation
    sample_logs = [
        "Oct 2 08:15:22 server systemd[1]: Started Daily apt download activities.",
        "Oct 2 09:22:15 server sshd[12345]: Accepted password for admin from 192.168.1.100 port 54321 ssh2",
        "Oct 2 10:05:33 server kernel: [12345.678901] CPU0 is up",
        "Oct 2 10:15:44 server nginx[6789]: 2023/10/02 10:15:44 [info] Starting nginx",
        "Oct 2 10:20:12 server cron[1001]: (root) CMD (/usr/local/bin/backup_script.sh)"
    ]
    return sample_logs[:lines]


def restart_service(service_name: str) -> Dict[str, str]:
    """
    Restart a system service.
    
    Args:
        service_name: Name of the service to restart
        
    Returns:
        Dictionary containing the result of the service restart operation
    """
    # This would connect to the Linux Admin MCP server in a real implementation
    return {
        "status": "success",
        "message": f"Service '{service_name}' restarted successfully",
        "service_name": service_name
    }


def check_firewall_rules() -> List[Dict[str, Any]]:
    """
    Check current firewall rules.
    
    Returns:
        List of dictionaries containing firewall rules
    """
    # This would connect to the Firewall MCP server in a real implementation
    return [
        {
            "rule_id": 1,
            "action": "allow",
            "protocol": "tcp",
            "port": 22,
            "source": "any",
            "description": "SSH access"
        },
        {
            "rule_id": 2,
            "action": "allow",
            "protocol": "tcp",
            "port": 80,
            "source": "any",
            "description": "HTTP access"
        },
        {
            "rule_id": 3,
            "action": "allow",
            "protocol": "tcp",
            "port": 443,
            "source": "any",
            "description": "HTTPS access"
        },
        {
            "rule_id": 4,
            "action": "deny",
            "protocol": "all",
            "port": "any",
            "source": "any",
            "description": "Default deny"
        }
    ]


# Create a comprehensive system administration agent
agent = Agent(
    system_prompt="You are a system administration assistant. You can list users, monitor system processes, check server health, read system logs, restart services, and check firewall rules. When asked about system status, provide detailed information about CPU, memory, disk usage, and running services. Be helpful but cautious with system operations and always explain the implications of administrative actions."
)


def setup_system_admin_agent():
    """Set up the system administration agent with tools."""
    try:
        agent.add_tool(list_system_users)
        agent.add_tool(list_running_processes)
        agent.add_tool(get_server_health)
        agent.add_tool(read_system_logs)
        agent.add_tool(restart_service)
        agent.add_tool(check_firewall_rules)
        print("System administration tools successfully registered with the agent.")
        return True
    except AttributeError as e:
        print(f"Note: Tool registration API may vary depending on the specific Strands implementation. Error: {e}")
        return False


def run_system_agent(user_input: str):
    """
    Run the system administration agent with the given user input.
    
    Args:
        user_input: The input from the user
        
    Returns:
        The agent's response
    """
    try:
        response = agent.run(user_input)
        return response
    except ImportError:
        # If strandsagents is not available, return a simulated response
        return f"Simulated response: System administration agent. You requested: '{user_input}'"
    except Exception as e:
        return f"Error processing your request: {str(e)}"


def main():
    """Main function to run the system administration agent."""
    # Set up tools
    tools_setup = setup_system_admin_agent()
    
    print("System Administration Agent")
    print("This agent can:")
    print("- List system users (e.g., 'list all users')")
    print("- Show running processes (e.g., 'show running processes')")
    print("- Check server health (e.g., 'check server health')")
    print("- Read system logs (e.g., 'read last 10 lines from syslog')")
    print("- Restart services (e.g., 'restart nginx service')")
    print("- Check firewall rules (e.g., 'show firewall rules')")
    print("Type 'quit' to exit.\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Agent: Goodbye! System administration assistant signing off.")
            break
            
        response = run_system_agent(user_input)
        print(f"Agent: {response}\n")


if __name__ == "__main__":
    main()