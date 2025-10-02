#!/usr/bin/env python3
"""
Server Health MCP Server

Provides access to server health monitoring functionality for LLMs through MCP protocol.
"""

from fastmcp import FastMCP
from typing import List, Dict, Any
import asyncio
import psutil
import subprocess
import socket
from datetime import datetime


# Initialize the MCP server
mcp = FastMCP(
    name="Server Health MCP Server",
    instructions="Provides access to server health monitoring functionality including performance metrics, service status, and system diagnostics",
    version="1.0.0"
)


# Tools
@mcp.tool
def get_system_health() -> Dict[str, Any]:
    """
    Get overall system health metrics
    """
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Determine health status based on thresholds
    cpu_status = "critical" if cpu_percent > 90 else "warning" if cpu_percent > 75 else "healthy"
    memory_status = "critical" if memory.percent > 90 else "warning" if memory.percent > 75 else "healthy"
    disk_status = "critical" if disk.percent > 90 else "warning" if disk.percent > 80 else "healthy"
    
    return {
        "timestamp": datetime.now().isoformat(),
        "cpu": {
            "usage_percent": cpu_percent,
            "status": cpu_status
        },
        "memory": {
            "total_gb": round(memory.total / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2),
            "used_percent": memory.percent,
            "status": memory_status
        },
        "disk": {
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "usage_percent": disk.percent,
            "status": disk_status
        },
        "system_status": "critical" if "critical" in [cpu_status, memory_status, disk_status] else 
                         "warning" if "warning" in [cpu_status, memory_status, disk_status] else "healthy"
    }


@mcp.tool
def get_service_status(service_name: str) -> Dict[str, str]:
    """
    Get the status of a specific system service
    """
    try:
        # This assumes a systemd-based system
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
def check_port_status(host: str, port: int) -> Dict[str, str]:
    """
    Check if a specific port is open on a host
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(3)  # 3 second timeout
            result = s.connect_ex((host, port))
            if result == 0:
                return {
                    "host": host,
                    "port": port,
                    "status": "open",
                    "message": f"Port {port} on {host} is open"
                }
            else:
                return {
                    "host": host,
                    "port": port,
                    "status": "closed",
                    "message": f"Port {port} on {host} is closed or filtered"
                }
    except Exception as e:
        return {
            "host": host,
            "port": port,
            "status": "error",
            "message": str(e)
        }


@mcp.tool
def get_running_processes() -> List[Dict[str, Any]]:
    """
    Get information about currently running processes
    """
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
        try:
            proc_info = proc.info
            processes.append({
                "pid": proc_info['pid'],
                "name": proc_info['name'],
                "cpu_percent": proc_info['cpu_percent'],
                "memory_percent": proc_info['memory_percent'],
                "status": proc_info['status']
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    # Sort by CPU usage in descending order
    return sorted(processes, key=lambda p: p['cpu_percent'] or 0, reverse=True)[:20]  # Top 20 processes


@mcp.tool
def get_network_io() -> Dict[str, Any]:
    """
    Get network I/O statistics
    """
    net_io = psutil.net_io_counters()
    
    return {
        "bytes_sent": net_io.bytes_sent,
        "bytes_recv": net_io.bytes_recv,
        "packets_sent": net_io.packets_sent,
        "packets_recv": net_io.packets_recv,
        "timestamp": datetime.now().isoformat()
    }


@mcp.tool
def get_disk_io() -> Dict[str, Any]:
    """
    Get disk I/O statistics
    """
    disk_io = psutil.disk_io_counters()
    
    if disk_io is not None:
        return {
            "read_count": disk_io.read_count,
            "write_count": disk_io.write_count,
            "read_bytes": disk_io.read_bytes,
            "write_bytes": disk_io.write_bytes,
            "read_time": disk_io.read_time,
            "write_time": disk_io.write_time,
            "timestamp": datetime.now().isoformat()
        }
    else:
        return {"error": "Disk I/O counters not available on this system"}


@mcp.tool
def check_system_load() -> Dict[str, float]:
    """
    Get system load averages
    """
    try:
        load1, load5, load15 = psutil.getloadavg()
        return {
            "load_1min": load1,
            "load_5min": load5,
            "load_15min": load15,
            "timestamp": datetime.now().isoformat()
        }
    except AttributeError:
        # getloadavg() is not available on all platforms (e.g., Windows)
        return {"error": "Load average not available on this platform"}


@mcp.tool
def get_system_uptime() -> Dict[str, str]:
    """
    Get system uptime
    """
    try:
        boot_time = psutil.boot_time()
        uptime_seconds = datetime.now().timestamp() - boot_time
        uptime_str = str(datetime.timedelta(seconds=int(uptime_seconds)))
        
        return {
            "uptime": uptime_str,
            "uptime_seconds": int(uptime_seconds),
            "boot_time": datetime.fromtimestamp(boot_time).isoformat()
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
def run_system_diagnostics() -> Dict[str, Any]:
    """
    Run a comprehensive system diagnostic check
    """
    # Collect various system metrics
    system_health = get_system_health()
    system_load = check_system_load()
    network_io = get_network_io()
    disk_io = get_disk_io()
    uptime = get_system_uptime()
    
    # Check for critical issues
    issues = []
    if system_health.get("cpu", {}).get("usage_percent", 0) > 95:
        issues.append("High CPU usage detected")
    if system_health.get("memory", {}).get("used_percent", 0) > 95:
        issues.append("High memory usage detected")
    if system_health.get("disk", {}).get("usage_percent", 0) > 95:
        issues.append("High disk usage detected")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "system_health": system_health,
        "system_load": system_load,
        "network_io": network_io,
        "disk_io": disk_io,
        "uptime": uptime,
        "diagnostic_issues": issues,
        "overall_status": "critical" if issues else system_health.get("system_status", "unknown")
    }


@mcp.tool
def get_top_cpu_processes(limit: int = 5) -> List[Dict[str, Any]]:
    """
    Get the top CPU consuming processes
    """
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try:
            proc_info = proc.info
            processes.append(proc_info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    # Sort by CPU usage in descending order and take the top 'limit' processes
    top_processes = sorted(processes, key=lambda p: p['cpu_percent'] or 0, reverse=True)[:limit]
    
    return top_processes


# Resources
@mcp.resource("http://server-health-mcp-server.local/health-indicators")
def get_health_indicators() -> Dict[str, Any]:
    """
    Get key system health indicators
    """
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "cpu_usage": f"{cpu_percent}%",
        "memory_usage": f"{memory.percent}%",
        "disk_usage": f"{disk.percent}%",
        "healthy_cpu": cpu_percent < 80,
        "healthy_memory": memory.percent < 85,
        "healthy_disk": disk.percent < 90,
        "timestamp": datetime.now().isoformat()
    }


@mcp.resource("http://server-health-mcp-server.local/service-availability")
def get_service_availability() -> List[Dict[str, str]]:
    """
    Get availability status for critical services
    """
    # Common services to check
    services = ["ssh", "nginx", "apache2", "mysql", "postgresql", "docker"]
    service_status = []
    
    for service in services:
        try:
            result = subprocess.run(['systemctl', 'is-active', service], 
                                    capture_output=True, text=True, timeout=5)
            status = result.stdout.strip()
            service_status.append({
                "service": service,
                "status": status,
                "available": status == "active"
            })
        except:
            # If systemctl fails, mark as unavailable
            service_status.append({
                "service": service,
                "status": "unavailable",
                "available": False
            })
    
    return service_status


@mcp.resource("http://server-health-mcp-server.local/performance-baselines")
def get_performance_baselines() -> Dict[str, float]:
    """
    Get established performance baselines for the system
    """
    return {
        "baseline_cpu_usage": 35.0,  # percentage
        "baseline_memory_usage": 55.0,  # percentage
        "baseline_disk_usage": 45.0,  # percentage
        "baseline_network_in": 1024000,  # bytes per second
        "baseline_network_out": 512000,  # bytes per second
        "calculation_period": "last_30_days"
    }


# Prompts
@mcp.prompt("/server-troubleshooting")
def server_troubleshooting_prompt(
    symptoms: List[str],
    system_metrics: Dict[str, Any],
    error_logs: List[str],
    context: str = ""
) -> str:
    """
    Generate a prompt for troubleshooting server issues
    """
    return f"""
Troubleshoot server issues with symptoms: {symptoms}
Current system metrics: {system_metrics}
Error logs: {error_logs}
Context: {context}

Identify root cause and provide remediation steps.
"""


@mcp.prompt("/capacity-planning")
def capacity_planning_prompt(
    current_usage: Dict[str, float],
    growth_projection: float,
    infrastructure_limits: Dict[str, float],
    context: str = ""
) -> str:
    """
    Generate a prompt for server capacity planning
    """
    return f"""
Plan server capacity based on:
Current usage: {current_usage}
Expected growth: {growth_projection} over the next 6 months
Infrastructure limits: {infrastructure_limits}
Context: {context}

Determine when scaling will be required and recommend solutions.
"""


@mcp.prompt("/monitoring-setup")
def monitoring_setup_prompt(
    system_components: List[str],
    alert_thresholds: Dict[str, float],
    notification_channels: List[str],
    context: str = ""
) -> str:
    """
    Generate a prompt for setting up server monitoring
    """
    return f"""
Set up monitoring for system components: {system_components}
Alert thresholds: {alert_thresholds}
Notification channels: {notification_channels}
Context: {context}

Configure appropriate monitoring tools and alerting mechanisms.
"""


@mcp.prompt("/performance-optimization")
def performance_optimization_prompt(
    performance_bottlenecks: List[str],
    system_specs: Dict[str, Any],
    usage_patterns: List[str],
    context: str = ""
) -> str:
    """
    Generate a prompt for optimizing server performance
    """
    return f"""
Optimize server performance addressing bottlenecks: {performance_bottlenecks}
System specifications: {system_specs}
Usage patterns: {usage_patterns}
Context: {context}

Suggest configuration changes and optimization strategies.
"""


if __name__ == "__main__":
    # Use stdio transport for MCP server (proper MCP protocol communication)
    asyncio.run(mcp.run_stdio_async())