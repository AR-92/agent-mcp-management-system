"""
Security & Monitoring Agent using Strands Agents SDK

This agent combines Firewall, Server Health, System Monitoring, and Port Scanner MCPs
to provide comprehensive security and system monitoring capabilities.
"""

from strandsagents import Agent
from typing import Dict, Any, List
import json
from datetime import datetime, timedelta


def list_firewall_rules() -> List[Dict[str, Any]]:
    """
    List current firewall rules.
    
    Returns:
        List of dictionaries containing firewall rules
    """
    # This would connect to the Firewall MCP server in a real implementation
    return [
        {
            "rule_id": i,
            "action": "allow" if i % 4 != 0 else "deny",
            "protocol": "tcp" if i % 3 == 0 else "udp" if i % 3 == 1 else "icmp",
            "port": 22 if i == 1 else 80 if i == 2 else 443 if i == 3 else 8080 if i == 4 else i * 10,
            "source": "any" if i % 2 == 0 else f"192.168.1.{i}",
            "destination": "any",
            "description": f"Rule to {action} {protocol} traffic on port {port}".replace(
                "to allow", "to allow").replace("to deny", "to deny").format(
                action="allow" if i % 4 != 0 else "deny",
                protocol="tcp" if i % 3 == 0 else "udp" if i % 3 == 1 else "icmp",
                port=22 if i == 1 else 80 if i == 2 else 443 if i == 3 else 8080 if i == 4 else i * 10
            ),
            "enabled": True
        }
        for i in range(1, 11)
    ]


def add_firewall_rule(
    action: str,  # allow or deny
    protocol: str,
    port: int,
    source: str = "any",
    destination: str = "any",
    description: str = ""
) -> Dict[str, Any]:
    """
    Add a new firewall rule.
    
    Args:
        action: Whether to 'allow' or 'deny' the traffic
        protocol: Protocol to filter ('tcp', 'udp', 'icmp')
        port: Port number to filter
        source: Source IP or range (default: 'any')
        destination: Destination IP or range (default: 'any')
        description: Description of the rule
        
    Returns:
        Dictionary containing the rule addition result
    """
    # This would connect to the Firewall MCP server in a real implementation
    rule_id = f"rule_{hash(f'{action}_{protocol}_{port}') % 10000}"
    
    return {
        "status": "added",
        "rule_id": rule_id,
        "action": action,
        "protocol": protocol,
        "port": port,
        "source": source,
        "destination": destination,
        "description": description,
        "message": f"Firewall rule {action}ing {protocol} traffic on port {port} added successfully"
    }


def get_system_health() -> Dict[str, Any]:
    """
    Get comprehensive system health information.
    
    Returns:
        Dictionary containing server health metrics
    """
    # This would connect to the Server Health MCP server in a real implementation
    return {
        "timestamp": datetime.now().isoformat(),
        "cpu_usage_percent": 28.4,
        "memory_usage_percent": 58.7,
        "disk_usage_percent": 62.3,
        "network_status": "healthy",
        "load_average": [0.25, 0.31, 0.28],
        "uptime": "12 days, 7 hours, 34 minutes",
        "service_status": {
            "ssh": "running",
            "nginx": "running",
            "postgresql": "running",
            "firewall": "active",
            "docker": "running"
        },
        "temperature": {
            "cpu": "42°C",
            "motherboard": "38°C"
        },
        "health_score": 96  # Out of 100
    }


def get_cpu_usage() -> Dict[str, float]:
    """
    Get current CPU usage metrics.
    
    Returns:
        Dictionary containing CPU usage metrics
    """
    # This would connect to the System Monitoring MCP server in a real implementation
    return {
        "cpu_percent": 28.4,
        "load_1min": 0.25,
        "load_5min": 0.31,
        "load_15min": 0.28,
        "cpu_count": 4,
        "cpu_frequency": 2.4  # GHz
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
        "available_memory_gb": 6.5,
        "used_memory_gb": 9.5,
        "memory_percent": 58.7,
        "swap_total_gb": 2.0,
        "swap_used_gb": 0.3,
        "swap_percent": 15.0,
        "processes_using_memory": [
            {"process": "systemd", "usage_gb": 1.2},
            {"process": "docker", "usage_gb": 0.8},
            {"process": "postgresql", "usage_gb": 0.6}
        ]
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
            "total_gb": 250.0,
            "used_gb": 155.8,
            "free_gb": 94.2,
            "usage_percent": 62.3,
            "file_system": "ext4",
            "inodes_used_percent": 12.4
        },
        {
            "mount_point": "/home",
            "total_gb": 500.0,
            "used_gb": 235.0,
            "free_gb": 265.0,
            "usage_percent": 47.0,
            "file_system": "ext4",
            "inodes_used_percent": 8.2
        },
        {
            "mount_point": "/var/lib/docker",
            "total_gb": 100.0,
            "used_gb": 87.5,
            "free_gb": 12.5,
            "usage_percent": 87.5,  # High usage warning
            "file_system": "ext4",
            "inodes_used_percent": 22.1
        }
    ]


def scan_network_ports(
    target: str,
    port_range: str = "1-1000",
    scan_type: str = "tcp"  # tcp, udp, both
) -> List[Dict[str, Any]]:
    """
    Scan network ports on a target system.
    
    Args:
        target: Target host or IP to scan
        port_range: Range of ports to scan (e.g., "1-1000", "22,80,443")
        scan_type: Type of scan ('tcp', 'udp', 'both')
        
    Returns:
        List of dictionaries containing port scan results
    """
    # This would connect to the Port Scanner MCP server in a real implementation
    return [
        {
            "port": port,
            "status": "open" if port in [22, 80, 443, 3000, 5432, 6379] else "closed",
            "service": "ssh" if port == 22 else "http" if port == 80 else "https" if port == 443 else 
                      "app" if port == 3000 else "database" if port == 5432 else "redis" if port == 6379 else "unknown",
            "protocol": "tcp",
            "description": f"Service running on port {port}"
        }
        for port in [22, 25, 53, 80, 110, 143, 443, 993, 995, 3000, 5432, 6379, 8080, 9000, 9418]
        if f"{port}" in port_range or (port_range == "1-1000" and port <= 1000)
    ]


def get_network_connections() -> List[Dict[str, Any]]:
    """
    Get current network connections.
    
    Returns:
        List of dictionaries containing network connection information
    """
    # This would connect to the System Monitoring MCP server in a real implementation
    return [
        {
            "protocol": "tcp",
            "local_address": f"0.0.0.0:{port}",
            "remote_address": "0.0.0.0:0" if port in [22, 80, 443] else f"192.168.1.100:{remote_port}",
            "state": "LISTEN" if port in [22, 80, 443] else "ESTABLISHED",
            "process": "sshd" if port == 22 else "nginx" if port in [80, 443] else "app" if port == 3000 else "postgres"
        }
        for port, remote_port in [(22, 54321), (80, 12345), (443, 23456), (3000, 34567), (5432, 45678)]
    ]


def check_security_logs(
    log_type: str = "auth",  # auth, kern, syslog, etc.
    hours_back: int = 24,
    filter_level: str = "all"  # all, info, warning, error
) -> List[Dict[str, Any]]:
    """
    Check security-related logs.
    
    Args:
        log_type: Type of log to check ('auth', 'kern', 'syslog', etc.)
        hours_back: Number of hours back to look
        filter_level: Log level to filter ('all', 'info', 'warning', 'error')
        
    Returns:
        List of dictionaries containing log entries
    """
    # This would connect to the Log Viewer MCP server in a real implementation
    return [
        {
            "timestamp": (datetime.now() - timedelta(hours=i, minutes=i*2)).isoformat(),
            "level": "INFO" if i % 3 != 0 else "WARNING" if i % 3 == 1 else "ERROR",
            "source": f"systemd" if i % 4 == 0 else f"sshd" if i % 4 == 1 else f"kernel" if i % 4 == 2 else "app",
            "message": f"Security event log entry #{i} for {log_type} monitoring",
            "details": f"Details about the security event #{i}"
        }
        for i in range(1, 11)
        if filter_level == "all" or 
           (filter_level == "INFO" and "INFO" in (f"{'INFO' if i % 3 != 0 else 'WARNING' if i % 3 == 1 else 'ERROR'}")) or
           (filter_level == "WARNING" and "WARNING" in (f"{'INFO' if i % 3 != 0 else 'WARNING' if i % 3 == 1 else 'ERROR'}")) or
           (filter_level == "ERROR" and "ERROR" in (f"{'INFO' if i % 3 != 0 else 'WARNING' if i % 3 == 1 else 'ERROR'}"))
    ]


def get_process_list() -> List[Dict[str, Any]]:
    """
    Get list of running processes.
    
    Returns:
        List of dictionaries containing process information
    """
    # This would connect to the Process Manager MCP server in a real implementation
    import psutil
    
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
        "service_name": service_name,
        "timestamp": datetime.now().isoformat()
    }


def get_system_users() -> List[Dict[str, Any]]:
    """
    Get list of system users.
    
    Returns:
        List of dictionaries containing user information
    """
    # This would connect to the Linux Admin MCP server in a real implementation
    return [
        {
            "username": user,
            "uid": uid,
            "gid": gid,
            "home": home,
            "shell": shell,
            "last_login": (datetime.now() - timedelta(days=days)).isoformat() if days != 0 else "Never",
            "is_active": is_active
        }
        for user, uid, gid, home, shell, days, is_active in [
            ("root", 0, 0, "/root", "/bin/bash", 0, True),
            ("admin", 1000, 1000, "/home/admin", "/bin/bash", 1, True),
            ("www-data", 33, 33, "/var/www", "/usr/sbin/nologin", 0, True),
            ("backup", 1001, 1001, "/home/backup", "/bin/false", 15, False),
            ("testuser", 1002, 1002, "/home/testuser", "/bin/bash", 2, True)
        ]
    ]


def get_security_recommendations() -> List[Dict[str, str]]:
    """
    Get security recommendations based on system analysis.
    
    Returns:
        List of dictionaries containing security recommendations
    """
    # This would combine insights from all security-related MCPs
    return [
        {
            "id": 1,
            "category": "firewall",
            "recommendation": "Consider restricting SSH access to specific IPs",
            "severity": "medium",
            "status": "pending"
        },
        {
            "id": 2,
            "category": "monitoring",
            "recommendation": "Enable disk usage alerts for /var/lib/docker",
            "severity": "high",
            "status": "pending" 
        },
        {
            "id": 3,
            "category": "access",
            "recommendation": "Disable inactive user account 'backup'",
            "severity": "low",
            "status": "pending"
        },
        {
            "id": 4,
            "category": "services",
            "recommendation": "Review and potentially disable unnecessary network services",
            "severity": "medium",
            "status": "pending"
        }
    ]


# Create a Security & Monitoring agent
agent = Agent(
    system_prompt="You are a Security & System Monitoring assistant. You can manage firewall rules, check system health, monitor network connections, scan ports, view security logs, manage processes, restart services, and provide security recommendations. When asked about security or system operations, provide detailed information about system status, security posture, and recommended actions."
)


def setup_security_agent():
    """Set up the Security & Monitoring agent with tools."""
    try:
        agent.add_tool(list_firewall_rules)
        agent.add_tool(add_firewall_rule)
        agent.add_tool(get_system_health)
        agent.add_tool(get_cpu_usage)
        agent.add_tool(get_memory_usage)
        agent.add_tool(get_disk_usage)
        agent.add_tool(scan_network_ports)
        agent.add_tool(get_network_connections)
        agent.add_tool(check_security_logs)
        agent.add_tool(get_process_list)
        agent.add_tool(restart_service)
        agent.add_tool(get_system_users)
        agent.add_tool(get_security_recommendations)
        print("Security & Monitoring tools successfully registered with the agent.")
        return True
    except AttributeError as e:
        print(f"Note: Tool registration API may vary depending on the specific Strands implementation. Error: {e}")
        return False


def run_security_agent(user_input: str):
    """
    Run the Security & Monitoring agent with the given user input.
    
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
        return f"Simulated response: Security & Monitoring agent. You requested: '{user_input}'"
    except Exception as e:
        return f"Error processing your request: {str(e)}"


def main():
    """Main function to run the Security & Monitoring agent."""
    # Set up tools
    tools_setup = setup_security_agent()
    
    print("Security & Monitoring Agent")
    print("This agent can:")
    print("- List firewall rules (e.g., 'show firewall rules')")
    print("- Add firewall rules (e.g., 'add rule to allow port 8080')")
    print("- Check system health (e.g., 'check system health')")
    print("- Monitor CPU usage (e.g., 'show CPU usage')")
    print("- Monitor memory usage (e.g., 'show memory usage')")
    print("- Check disk usage (e.g., 'show disk usage')")
    print("- Scan network ports (e.g., 'scan ports on 192.168.1.100')")
    print("- Get network connections (e.g., 'show network connections')")
    print("- Check security logs (e.g., 'show auth logs')")
    print("- List processes (e.g., 'show running processes')")
    print("- Restart services (e.g., 'restart nginx')")
    print("- Show system users (e.g., 'list users')")
    print("- Get security recommendations (e.g., 'show security recommendations')")
    print("Type 'quit' to exit.\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Agent: Goodbye! Security & Monitoring assistant signing off.")
            break
            
        response = run_security_agent(user_input)
        print(f"Agent: {response}\n")


if __name__ == "__main__":
    main()