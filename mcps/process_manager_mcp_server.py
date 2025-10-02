#!/usr/bin/env python3
"""
Process Manager MCP Server

Provides access to process management functionality for LLMs through MCP protocol.
"""

from fastmcp import FastMCP
from typing import List, Dict, Any
import asyncio
import psutil
import os
import subprocess


# Initialize the MCP server
mcp = FastMCP(
    name="Process Manager MCP Server",
    instructions="Provides access to process management functionality including process monitoring, control, and system resource management",
    version="1.0.0"
)


# Tools
@mcp.tool
def list_processes() -> List[Dict[str, Any]]:
    """
    List all running processes with detailed information
    """
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'username', 'status', 'cpu_percent', 'memory_percent', 'create_time', 'cmdline']):
        try:
            proc_info = proc.info
            processes.append({
                "pid": proc_info['pid'],
                "name": proc_info['name'],
                "username": proc_info['username'],
                "status": proc_info['status'],
                "cpu_percent": proc_info['cpu_percent'],
                "memory_percent": proc_info['memory_percent'],
                "create_time": proc_info['create_time'],
                "cmdline": ' '.join(proc_info['cmdline']) if proc_info['cmdline'] else ''
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    return sorted(processes, key=lambda p: p['cpu_percent'], reverse=True)


@mcp.tool
def get_process_info(pid: int) -> Dict[str, Any]:
    """
    Get detailed information about a specific process
    """
    try:
        proc = psutil.Process(pid)
        return {
            "pid": proc.pid,
            "name": proc.name(),
            "status": proc.status(),
            "username": proc.username(),
            "cpu_percent": proc.cpu_percent(),
            "memory_percent": proc.memory_percent(),
            "memory_info": proc.memory_info()._asdict(),
            "create_time": proc.create_time(),
            "num_threads": proc.num_threads(),
            "cwd": proc.cwd(),
            "cmdline": proc.cmdline()
        }
    except psutil.NoSuchProcess:
        return {"error": f"Process with PID {pid} not found"}
    except psutil.AccessDenied:
        return {"error": f"Access denied to process with PID {pid}"}


@mcp.tool
def kill_process(pid: int, force: bool = False) -> Dict[str, str]:
    """
    Kill a process by PID
    """
    try:
        proc = psutil.Process(pid)
        proc.kill() if force else proc.terminate()
        action = "killed" if force else "terminated"
        return {
            "status": "success",
            "message": f"Process {pid} {action} successfully"
        }
    except psutil.NoSuchProcess:
        return {"error": f"Process with PID {pid} not found"}
    except psutil.AccessDenied:
        return {"error": f"Access denied to kill process with PID {pid}"}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
def start_process(command: str, shell: bool = True) -> Dict[str, Any]:
    """
    Start a new process with the given command
    """
    try:
        if shell:
            result = subprocess.Popen(command, shell=True)
        else:
            result = subprocess.Popen(command.split())
        
        return {
            "status": "success",
            "message": f"Process started with PID {result.pid}",
            "pid": result.pid,
            "command": command
        }
    except Exception as e:
        return {"error": f"Failed to start process: {str(e)}"}


@mcp.tool
def get_top_cpu_processes(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get the top N processes by CPU usage
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
def get_top_memory_processes(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get the top N processes by memory usage
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
def search_processes_by_name(name: str) -> List[Dict[str, Any]]:
    """
    Search for processes by name
    """
    matching_processes = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if name.lower() in proc.info['name'].lower():
                matching_processes.append({
                    "pid": proc.info['pid'],
                    "name": proc.info['name']
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    return matching_processes


@mcp.tool
def get_process_connections(pid: int) -> List[Dict[str, Any]]:
    """
    Get network connections for a specific process
    """
    try:
        proc = psutil.Process(pid)
        connections = proc.connections()
        
        result = []
        for conn in connections:
            result.append({
                "fd": conn.fd,
                "family": conn.family.name if hasattr(conn.family, 'name') else conn.family,
                "type": conn.type.name if hasattr(conn.type, 'name') else conn.type,
                "local_address": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A",
                "remote_address": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr and conn.raddr.ip else "N/A",
                "status": conn.status
            })
        
        return result
    except psutil.NoSuchProcess:
        return [{"error": f"Process with PID {pid} not found"}]
    except psutil.AccessDenied:
        return [{"error": f"Access denied to process with PID {pid}"}]
    except Exception as e:
        return [{"error": str(e)}]


@mcp.tool
def get_process_tree(pid: int) -> Dict[str, Any]:
    """
    Get the process tree for a specific process (parent and children)
    """
    try:
        proc = psutil.Process(pid)
        
        # Get children processes
        children = proc.children(recursive=True)
        
        tree = {
            "parent": {
                "pid": proc.pid,
                "name": proc.name(),
                "status": proc.status()
            },
            "children": []
        }
        
        for child in children:
            tree["children"].append({
                "pid": child.pid,
                "name": child.name(),
                "status": child.status()
            })
        
        return tree
    except psutil.NoSuchProcess:
        return {"error": f"Process with PID {pid} not found"}
    except psutil.AccessDenied:
        return {"error": f"Access denied to process with PID {pid}"}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
def set_process_priority(pid: int, priority: int) -> Dict[str, str]:
    """
    Set the priority (niceness) of a process
    Note: On Windows, priority classes are used instead of nice values
    """
    try:
        proc = psutil.Process(pid)
        
        # Set the nice value (priority) on Unix-like systems
        if os.name == 'posix':
            proc.nice(priority)
            return {
                "status": "success",
                "message": f"Process {pid} priority set to {priority}"
            }
        else:
            return {
                "status": "error",
                "message": "Setting process priority is only supported on Unix-like systems"
            }
    except psutil.NoSuchProcess:
        return {"error": f"Process with PID {pid} not found"}
    except psutil.AccessDenied:
        return {"error": f"Access denied to modify process with PID {pid}"}
    except Exception as e:
        return {"error": str(e)}


# Resources
@mcp.resource("http://process-manager-mcp-server.local/system-processes-summary")
def get_system_processes_summary() -> Dict[str, int]:
    """
    Get a summary of system processes
    """
    processes = list_processes()
    statuses = {}
    
    for proc in processes:
        status = proc['status']
        statuses[status] = statuses.get(status, 0) + 1
    
    return {
        "total_processes": len(processes),
        "status_breakdown": statuses,
        "total_cpu_percent": sum(p['cpu_percent'] or 0 for p in processes),
        "total_memory_percent": sum(p['memory_percent'] or 0 for p in processes)
    }


@mcp.resource("http://process-manager-mcp-server.local/high-cpu-processes")
def get_high_cpu_processes() -> List[Dict[str, Any]]:
    """
    Get processes with high CPU usage (above 10%)
    """
    processes = list_processes()
    high_cpu = [p for p in processes if p['cpu_percent'] and p['cpu_percent'] > 10.0]
    
    return sorted(high_cpu, key=lambda p: p['cpu_percent'], reverse=True)[:10]


@mcp.resource("http://process-manager-mcp-server.local/high-memory-processes")
def get_high_memory_processes() -> List[Dict[str, Any]]:
    """
    Get processes with high memory usage (above 5%)
    """
    processes = list_processes()
    high_memory = [p for p in processes if p['memory_percent'] and p['memory_percent'] > 5.0]
    
    return sorted(high_memory, key=lambda p: p['memory_percent'], reverse=True)[:10]


# Prompts
@mcp.prompt("/process-troubleshooting")
def process_troubleshooting_prompt(
    pid: int, 
    symptoms: List[str],
    context: str = ""
) -> str:
    """
    Generate a prompt for troubleshooting a specific process
    """
    return f"""
Troubleshoot process with PID {pid} showing symptoms: {symptoms}
Context: {context}

Analyze the process information, resource usage, and potential issues.
"""


@mcp.prompt("/performance-optimization")
def performance_optimization_prompt(
    process_name: str,
    performance_issues: List[str],
    context: str = ""
) -> str:
    """
    Generate a prompt for optimizing process performance
    """
    return f"""
Optimize performance for process: {process_name}
Issues: {performance_issues}
Context: {context}

Suggest configuration changes, resource allocation, or optimization techniques.
"""


@mcp.prompt("/process-monitoring-setup")
def process_monitoring_setup_prompt(
    processes_to_monitor: List[str],
    alert_conditions: List[str],
    monitoring_requirements: str,
    context: str = ""
) -> str:
    """
    Generate a prompt for setting up process monitoring
    """
    return f"""
Set up monitoring for processes: {processes_to_monitor}
Alert Conditions: {alert_conditions}
Requirements: {monitoring_requirements}
Context: {context}

Configure monitoring rules, thresholds, and alert mechanisms.
"""


@mcp.prompt("/resource-allocation")
def resource_allocation_prompt(
    process_name: str,
    current_resource_usage: Dict[str, float],
    performance_requirements: str,
    context: str = ""
) -> str:
    """
    Generate a prompt for resource allocation planning
    """
    return f"""
Plan resource allocation for process: {process_name}
Current Usage: {current_resource_usage}
Requirements: {performance_requirements}
Context: {context}

Determine appropriate CPU, memory, and I/O allocation.
"""


if __name__ == "__main__":
    # Use stdio transport for MCP server (proper MCP protocol communication)
    asyncio.run(mcp.run_stdio_async())