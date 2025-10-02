#!/usr/bin/env python3
"""
System Monitoring MCP Server

Provides access to system monitoring functionality for LLMs through MCP protocol.
"""

from fastmcp import FastMCP
from typing import List, Dict, Any
import asyncio
import subprocess
import psutil
import time


# Initialize the MCP server
mcp = FastMCP(
    name="System Monitoring MCP Server",
    instructions="Provides access to system monitoring functionality including CPU, memory, disk, and network usage metrics",
    version="1.0.0"
)


# Tools
@mcp.tool
def get_cpu_usage() -> Dict[str, float]:
    """
    Get current CPU usage metrics
    """
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count()
    cpu_freq = psutil.cpu_freq()
    
    result = {
        "cpu_percent": cpu_percent,
        "cpu_count": cpu_count,
        "cpu_freq_current": cpu_freq.current if cpu_freq else None,
        "cpu_freq_max": cpu_freq.max if cpu_freq else None
    }
    
    return result


@mcp.tool
def get_memory_usage() -> Dict[str, Any]:
    """
    Get current memory usage metrics
    """
    memory = psutil.virtual_memory()
    
    return {
        "total": memory.total,
        "available": memory.available,
        "percent": memory.percent,
        "used": memory.used,
        "free": memory.free,
        "buffers": memory.buffers,
        "cached": memory.cached
    }


@mcp.tool
def get_disk_usage(path: str = "/") -> Dict[str, Any]:
    """
    Get disk usage metrics for a specific path
    """
    disk = psutil.disk_usage(path)
    
    return {
        "path": path,
        "total": disk.total,
        "used": disk.used,
        "free": disk.free,
        "percent": (disk.used / disk.total) * 100
    }


@mcp.tool
def get_network_usage() -> Dict[str, Any]:
    """
    Get network I/O statistics
    """
    net_io = psutil.net_io_counters()
    
    return {
        "bytes_sent": net_io.bytes_sent,
        "bytes_recv": net_io.bytes_recv,
        "packets_sent": net_io.packets_sent,
        "packets_recv": net_io.packets_recv,
        "errin": net_io.errin,
        "errout": net_io.errout,
        "dropin": net_io.dropin,
        "dropout": net_io.dropout
    }


@mcp.tool
def get_process_list() -> List[Dict[str, Any]]:
    """
    Get a list of running processes with their resource usage
    """
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'status']):
        try:
            proc_info = proc.info
            processes.append({
                "pid": proc_info['pid'],
                "name": proc_info['name'],
                "username": proc_info['username'],
                "cpu_percent": proc_info['cpu_percent'],
                "memory_percent": proc_info['memory_percent'],
                "status": proc_info['status']
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # Process may have terminated during iteration
            continue
    
    return processes


@mcp.tool
def get_system_load() -> Dict[str, float]:
    """
    Get system load averages
    """
    load1, load5, load15 = psutil.getloadavg()
    
    return {
        "load_1min": load1,
        "load_5min": load5,
        "load_15min": load15
    }


@mcp.tool
def get_uptime() -> Dict[str, float]:
    """
    Get system uptime in seconds
    """
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time
    
    return {
        "uptime_seconds": uptime_seconds,
        "uptime_formatted": f"{uptime_seconds / 86400:.2f} days"
    }


@mcp.tool
def get_top_processes_by_cpu(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get the top processes by CPU usage
    """
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    # Sort by CPU usage in descending order and take the top 'limit' processes
    top_processes = sorted(processes, key=lambda p: p['cpu_percent'] or 0, reverse=True)[:limit]
    
    return top_processes


@mcp.tool
def get_top_processes_by_memory(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get the top processes by memory usage
    """
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    # Sort by memory usage in descending order and take the top 'limit' processes
    top_processes = sorted(processes, key=lambda p: p['memory_percent'] or 0, reverse=True)[:limit]
    
    return top_processes


@mcp.tool
def get_filesystem_info() -> List[Dict[str, str]]:
    """
    Get information about mounted filesystems
    """
    partitions = psutil.disk_partitions()
    filesystems = []
    
    for partition in partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            filesystems.append({
                "device": partition.device,
                "mountpoint": partition.mountpoint,
                "file_system_type": partition.fstype,
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
                "percentage": (usage.used / usage.total) * 100
            })
        except PermissionError:
            # This can happen for system-protected partitions
            continue
    
    return filesystems


@mcp.tool
def get_system_temperatures() -> Dict[str, List[Dict[str, float]]]:
    """
    Get system temperature sensors (may return empty if not available on system)
    """
    try:
        temps = psutil.sensors_temperatures()
        result = {}
        for name, entries in temps.items():
            result[name] = []
            for entry in entries:
                result[name].append({
                    "label": entry.label or "",
                    "current": entry.current,
                    "high": entry.high,
                    "critical": entry.critical
                })
        return result
    except AttributeError:
        # sensors_temperatures() not available on this platform
        return {"error": "Temperature sensors not available on this system"}


# Resources
@mcp.resource("http://system-monitoring-mcp-server.local/current-status")
def get_current_system_status() -> Dict[str, Any]:
    """
    Get overall system status with key metrics
    """
    return {
        "timestamp": time.time(),
        "cpu_usage_percent": psutil.cpu_percent(interval=1),
        "memory_usage_percent": psutil.virtual_memory().percent,
        "disk_usage_percent": psutil.disk_usage("/").percent,
        "status": "normal"  # This could be determined from thresholds
    }


@mcp.resource("http://system-monitoring-mcp-server.local/historical-metrics")
def get_historical_metrics() -> Dict[str, List[Dict[str, float]]]:
    """
    Get historical system metrics (simulated for this example)
    """
    # In a real implementation, this would retrieve from a time-series database
    # For now, we'll return simulated historical data
    import random
    from datetime import datetime, timedelta
    
    now = datetime.now()
    historical_data = []
    
    for i in range(24):  # Last 24 hours
        historical_data.append({
            "timestamp": (now - timedelta(hours=i)).isoformat(),
            "cpu_usage_percent": round(random.uniform(10, 80), 2),
            "memory_usage_percent": round(random.uniform(20, 90), 2),
            "disk_usage_percent": round(random.uniform(50, 90), 2)
        })
    
    return {"hourly": historical_data}


@mcp.resource("http://system-monitoring-mcp-server.local/alerts")
def get_system_alerts() -> List[Dict[str, str]]:
    """
    Get current system alerts (simulated for this example)
    """
    # In a real implementation, this would check for actual system alerts
    # For now, we'll return simulated alerts based on thresholds
    cpu_percent = psutil.cpu_percent(interval=1)
    memory_percent = psutil.virtual_memory().percent
    disk_percent = psutil.disk_usage("/").percent
    
    alerts = []
    
    if cpu_percent > 90:
        alerts.append({
            "type": "high_cpu",
            "severity": "high",
            "message": f"CPU usage is high: {cpu_percent}%"
        })
    
    if memory_percent > 85:
        alerts.append({
            "type": "high_memory",
            "severity": "high",
            "message": f"Memory usage is high: {memory_percent}%"
        })
    
    if disk_percent > 90:
        alerts.append({
            "type": "high_disk",
            "severity": "high",
            "message": f"Disk usage is high: {disk_percent}%"
        })
    
    return alerts


# Prompts
@mcp.prompt("/system-performance-analysis")
def performance_analysis_prompt(
    metrics: List[str], 
    time_period: str,
    critical_thresholds: Dict[str, float],
    context: str = ""
) -> str:
    """
    Generate a prompt for analyzing system performance
    """
    return f"""
Analyze system performance based on these metrics: {metrics}
Time Period: {time_period}
Critical Thresholds: {critical_thresholds}
Context: {context}

Identify bottlenecks, trends, and recommendations for optimization.
"""


@mcp.prompt("/system-alert-response")
def alert_response_prompt(alert_type: str, severity: str, current_metrics: Dict[str, float], context: str = "") -> str:
    """
    Generate a prompt for responding to system alerts
    """
    return f"""
Respond to system alert:
- Type: {alert_type}
- Severity: {severity}
- Current Metrics: {current_metrics}
- Context: {context}

Provide immediate actions and long-term remediation steps.
"""


@mcp.prompt("/capacity-planning")
def capacity_planning_prompt(current_usage: Dict[str, float], growth_rate: float, planning_horizon: str, context: str = "") -> str:
    """
    Generate a prompt for system capacity planning
    """
    return f"""
Plan system capacity based on:
- Current Usage: {current_usage}
- Expected Growth Rate: {growth_rate} per month
- Planning Horizon: {planning_horizon}
- Context: {context}

Determine when upgrades will be needed and what resources to provision.
"""


@mcp.prompt("/monitoring-dashboard-setup")
def monitoring_dashboard_setup_prompt(metrics_to_track: List[str], alert_conditions: List[str], dashboard_requirements: str, context: str = "") -> str:
    """
    Generate a prompt for setting up a monitoring dashboard
    """
    return f"""
Set up a monitoring dashboard to track: {metrics_to_track}
Alert Conditions: {alert_conditions}
Requirements: {dashboard_requirements}
Context: {context}

Design the dashboard layout, visualization types, and alert configurations.
"""


if __name__ == "__main__":
    # Use stdio transport for MCP server (proper MCP protocol communication)
    asyncio.run(mcp.run_stdio_async())