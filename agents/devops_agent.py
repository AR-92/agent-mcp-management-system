"""
DevOps Operations Agent using Strands Agents SDK

This agent combines Dokploy, Linux administration, and system monitoring MCPs
to provide comprehensive DevOps operations support.
"""

from strandsagents import Agent
from typing import Dict, Any, List
import json
from datetime import datetime, timedelta
import psutil


def list_dokploy_applications() -> List[Dict[str, Any]]:
    """
    List applications managed by Dokploy.
    
    Returns:
        List of dictionaries containing application information
    """
    # This would connect to the Dokploy MCP server in a real implementation
    return [
        {
            "id": "app_1",
            "name": "Web Application",
            "status": "running",
            "containers": 3,
            "memory_usage": "2.4GB",
            "cpu_usage": "45%",
            "last_deployed": "2023-10-01T14:30:00Z",
            "health_status": "healthy"
        },
        {
            "id": "app_2", 
            "name": "API Service",
            "status": "running",
            "containers": 2,
            "memory_usage": "1.2GB",
            "cpu_usage": "30%",
            "last_deployed": "2023-09-28T10:15:00Z",
            "health_status": "healthy"
        },
        {
            "id": "app_3",
            "name": "Database",
            "status": "running",
            "containers": 1,
            "memory_usage": "3.8GB",
            "cpu_usage": "65%",
            "last_deployed": "2023-09-15T16:45:00Z",
            "health_status": "warning"  # High CPU usage
        }
    ]


def deploy_application(
    app_id: str,
    new_image: str,
    environment: str = "production"
) -> Dict[str, Any]:
    """
    Deploy a new version of an application.
    
    Args:
        app_id: ID of the application to deploy
        new_image: New Docker image to deploy
        environment: Environment to deploy to (staging/production)
        
    Returns:
        Dictionary containing the deployment result
    """
    # This would connect to the Dokploy MCP server in a real implementation
    return {
        "status": "initiated",
        "deployment_id": f"deploy_{app_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "app_id": app_id,
        "new_image": new_image,
        "environment": environment,
        "estimated_completion": "5-10 minutes",
        "message": f"Deployment of {new_image} to {environment} initiated for {app_id}"
    }


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


def list_system_users() -> List[Dict[str, Any]]:
    """
    List all system users.
    
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
            "username": "deploy",
            "uid": 1001,
            "gid": 1001,
            "home": "/home/deploy",
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


def get_system_health() -> Dict[str, Any]:
    """
    Get comprehensive system health information.
    
    Returns:
        Dictionary containing server health metrics
    """
    # This would connect to the Server Health MCP server in a real implementation
    return {
        "timestamp": "2023-10-02T10:30:00Z",
        "cpu_usage_percent": 25.3,
        "memory_usage_percent": 52.7,
        "disk_usage_percent": 75.2,
        "network_status": "healthy",
        "load_average": [0.12, 0.08, 0.05],
        "uptime": "8 days, 5 hours, 22 minutes",
        "service_status": {
            "ssh": "running",
            "nginx": "running",
            "postgresql": "running",
            "docker": "running",
            "firewall": "active"
        }
    }


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
    return processes[:15]  # Return first 15 processes


def get_cpu_usage() -> Dict[str, float]:
    """
    Get current CPU usage metrics.
    
    Returns:
        Dictionary containing CPU usage metrics
    """
    # This would connect to the System Monitoring MCP server in a real implementation
    return {
        "cpu_percent": 25.3,
        "load_1min": 0.12,
        "load_5min": 0.08,
        "load_15min": 0.05
    }


def get_memory_usage() -> Dict[str, Any]:
    """
    Get current memory usage metrics.
    
    Returns:
        Dictionary containing memory usage metrics
    """
    # This would connect to the System Monitoring MCP server in a real implementation
    return {
        "total_memory_gb": 16.0,
        "available_memory_gb": 7.5,
        "used_memory_gb": 8.5,
        "memory_percent": 52.7,
        "swap_total_gb": 4.0,
        "swap_used_gb": 0.5,
        "swap_percent": 12.5
    }


def get_disk_usage() -> List[Dict[str, Any]]:
    """
    Get disk usage metrics for mounted filesystems.
    
    Returns:
        List of dictionaries containing disk usage metrics
    """
    # This would connect to the System Monitoring MCP server in a real implementation
    return [
        {
            "mount_point": "/",
            "total_gb": 200.0,
            "used_gb": 150.4,
            "free_gb": 49.6,
            "usage_percent": 75.2,
            "file_system": "ext4"
        },
        {
            "mount_point": "/home",
            "total_gb": 500.0,
            "used_gb": 125.0,
            "free_gb": 375.0,
            "usage_percent": 25.0,
            "file_system": "ext4"
        },
        {
            "mount_point": "/var/lib/docker",
            "total_gb": 300.0,
            "used_gb": 285.0,
            "free_gb": 15.0,
            "usage_percent": 95.0,  # High usage warning
            "file_system": "ext4"
        }
    ]


def create_backup(
    backup_type: str,
    destination: str,
    include_databases: bool = False,
    encryption: bool = True
) -> Dict[str, Any]:
    """
    Create a system or application backup.
    
    Args:
        backup_type: Type of backup ('full', 'incremental', 'application')
        destination: Destination for the backup
        include_databases: Whether to include database backups
        encryption: Whether to encrypt the backup
        
    Returns:
        Dictionary containing the backup creation result
    """
    # This would connect to the Backup & Restore MCP server in a real implementation
    return {
        "status": "initiated",
        "backup_id": f"backup_{backup_type}_{datetime.now().strftime('%Y%m%d')}",
        "type": backup_type,
        "destination": destination,
        "encryption_enabled": encryption,
        "estimated_completion": "30-60 minutes",
        "message": f"{backup_type.capitalize()} backup initiated to {destination}"
    }


def scan_network_ports(target: str, port_range: str = "1-1000") -> List[Dict[str, Any]]:
    """
    Scan network ports on a target system.
    
    Args:
        target: Target host or IP to scan
        port_range: Range of ports to scan (e.g., "1-1000", "22,80,443")
        
    Returns:
        List of dictionaries containing port scan results
    """
    # This would connect to the Port Scanner MCP server in a real implementation
    return [
        {
            "port": 22,
            "status": "open",
            "service": "ssh",
            "protocol": "tcp",
            "description": "SSH service"
        },
        {
            "port": 80,
            "status": "open",
            "service": "http",
            "protocol": "tcp",
            "description": "HTTP web server"
        },
        {
            "port": 443,
            "status": "open",
            "service": "https",
            "protocol": "tcp",
            "description": "HTTPS web server"
        },
        {
            "port": 3000,
            "status": "open",
            "service": "application",
            "protocol": "tcp",
            "description": "Application server"
        },
        {
            "port": 5432,
            "status": "filtered",
            "service": "postgresql",
            "protocol": "tcp",
            "description": "PostgreSQL database"
        }
    ]


# Create a DevOps operations agent
agent = Agent(
    system_prompt="You are a DevOps operations assistant. You can manage applications with Dokploy, perform Linux system administration tasks, monitor system health and performance, create backups, and scan network ports. When asked about deployment or system operations, provide detailed information about the process and potential impact. Always follow DevOps best practices and ensure system stability and security."
)


def setup_devops_agent():
    """Set up the DevOps operations agent with tools."""
    try:
        agent.add_tool(list_dokploy_applications)
        agent.add_tool(deploy_application)
        agent.add_tool(restart_service)
        agent.add_tool(list_system_users)
        agent.add_tool(get_system_health)
        agent.add_tool(list_running_processes)
        agent.add_tool(get_cpu_usage)
        agent.add_tool(get_memory_usage)
        agent.add_tool(get_disk_usage)
        agent.add_tool(create_backup)
        agent.add_tool(scan_network_ports)
        print("DevOps operations tools successfully registered with the agent.")
        return True
    except AttributeError as e:
        print(f"Note: Tool registration API may vary depending on the specific Strands implementation. Error: {e}")
        return False


def run_devops_agent(user_input: str):
    """
    Run the DevOps operations agent with the given user input.
    
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
        return f"Simulated response: DevOps operations agent. You requested: '{user_input}'"
    except Exception as e:
        return f"Error processing your request: {str(e)}"


def main():
    """Main function to run the DevOps operations agent."""
    # Set up tools
    tools_setup = setup_devops_agent()
    
    print("DevOps Operations Agent")
    print("This agent can:")
    print("- List Dokploy applications (e.g., 'list applications')")
    print("- Deploy new application versions (e.g., 'deploy app_1 with new image')")
    print("- Restart system services (e.g., 'restart nginx')")
    print("- List system users (e.g., 'show system users')")
    print("- Check system health (e.g., 'check server health')")
    print("- Monitor system performance (e.g., 'show CPU usage')")
    print("- Create backups (e.g., 'create full backup')")
    print("- Scan network ports (e.g., 'scan ports on 192.168.1.10')")
    print("Type 'quit' to exit.\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Agent: Goodbye! DevOps operations assistant signing off.")
            break
            
        response = run_devops_agent(user_input)
        print(f"Agent: {response}\n")


if __name__ == "__main__":
    main()