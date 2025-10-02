#!/usr/bin/env python3
"""
Port Scanner MCP Server

Provides access to port scanning functionality for LLMs through MCP protocol.
"""

from fastmcp import FastMCP
from typing import List, Dict, Any
import asyncio
import socket
import subprocess
import concurrent.futures
from datetime import datetime


# Initialize the MCP server
mcp = FastMCP(
    name="Port Scanner MCP Server",
    instructions="Provides access to port scanning functionality including host discovery, port scanning, and service detection",
    version="1.0.0"
)


# Tools
@mcp.tool
def scan_ports(
    host: str, 
    port_range: str = "1-1000",
    scan_type: str = "tcp"
) -> List[Dict[str, Any]]:
    """
    Scan ports on a target host
    """
    def is_port_open(target_host, port):
        """Check if a single port is open"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)  # 1 second timeout
                result = s.connect_ex((target_host, port))
                return result == 0
        except:
            return False

    try:
        # Parse port range
        if '-' in port_range:
            start, end = map(int, port_range.split('-'))
            ports = range(start, end + 1)
        else:
            ports = [int(port_range)]
        
        open_ports = []
        
        # Limit the number of concurrent connections to avoid overwhelming
        max_workers = 50
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(is_port_open, host, port): port for port in ports}
            
            for future in concurrent.futures.as_completed(futures):
                port = futures[future]
                try:
                    if future.result():
                        open_ports.append({
                            "port": port,
                            "state": "open",
                            "protocol": scan_type,
                            "service": get_common_service(port)  # Simplified service detection
                        })
                except Exception:
                    continue  # Skip on error
        
        return sorted(open_ports, key=lambda x: x['port'])
    
    except Exception as e:
        return [{"error": f"Port scan failed: {str(e)}"}]


def get_common_service(port: int) -> str:
    """
    Get common service name for a port (simplified mapping)
    """
    services = {
        20: "FTP-Data", 21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
        53: "DNS", 80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS",
        993: "IMAPS", 995: "POP3S", 3389: "RDP", 5432: "PostgreSQL",
        3306: "MySQL", 1433: "MSSQL", 6379: "Redis", 27017: "MongoDB"
    }
    return services.get(port, "Unknown")


@mcp.tool
def scan_host(host: str) -> Dict[str, Any]:
    """
    Perform a basic host availability check
    """
    try:
        # Use ping to check if host is up
        result = subprocess.run(['ping', '-c', '1', '-W', '5', host], 
                                capture_output=True, text=True, timeout=10)
        is_up = result.returncode == 0
        
        return {
            "host": host,
            "status": "up" if is_up else "down",
            "latency_ms": extract_ping_time(result.stdout) if is_up else None
        }
    except subprocess.TimeoutExpired:
        return {
            "host": host,
            "status": "timeout",
            "latency_ms": None
        }
    except Exception as e:
        return {
            "host": host,
            "status": "error",
            "error": str(e)
        }


def extract_ping_time(output: str) -> float:
    """
    Extract ping time from ping command output
    """
    import re
    match = re.search(r'time=(\d+\.?\d*)\s*ms', output)
    return float(match.group(1)) if match else 0.0


@mcp.tool
def scan_top_ports(host: str) -> List[Dict[str, Any]]:
    """
    Scan the top 1000 most common ports on a host
    """
    return scan_ports(host, "1-1000", "tcp")


@mcp.tool
def scan_specific_ports(host: str, ports: List[int]) -> List[Dict[str, Any]]:
    """
    Scan specific ports on a host
    """
    open_ports = []
    for port in ports:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex((host, port))
                if result == 0:
                    open_ports.append({
                        "port": port,
                        "state": "open",
                        "protocol": "tcp",
                        "service": get_common_service(port)
                    })
        except Exception:
            continue
    
    return sorted(open_ports, key=lambda x: x['port'])


@mcp.tool
def get_service_banner(host: str, port: int) -> Dict[str, str]:
    """
    Attempt to get service banner from an open port
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)  # 5 second timeout
            s.connect((host, port))
            
            # Send an empty request to get the banner
            s.send(b'\r\n')
            banner = s.recv(1024).decode('utf-8', errors='ignore')
            
            return {
                "port": port,
                "banner": banner.strip() if banner.strip() else "No banner received",
                "host": host
            }
    except Exception as e:
        return {
            "error": f"Could not get banner from {host}:{port} - {str(e)}"
        }


@mcp.tool
def nmap_scan(host: str, scan_type: str = "-sV") -> List[Dict[str, Any]]:
    """
    Perform an nmap scan (if nmap is installed)
    """
    try:
        # Common nmap scan types: -sS (SYN), -sT (TCP), -sV (version detection), -O (OS detection)
        result = subprocess.run(['nmap', scan_type, host], 
                                capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            # This is a simplified parsing. A real implementation would have more robust parsing.
            lines = result.stdout.split('\n')
            open_ports = []
            
            for line in lines:
                if '/tcp' in line and 'open' in line:
                    parts = line.strip().split()
                    if len(parts) >= 3:
                        port_protocol = parts[0].split('/')
                        if len(port_protocol) == 2:
                            port = int(port_protocol[0])
                            protocol = port_protocol[1]
                            service = parts[2] if len(parts) > 2 else "unknown"
                            
                            open_ports.append({
                                "port": port,
                                "state": "open",
                                "protocol": protocol,
                                "service": service
                            })
            
            return sorted(open_ports, key=lambda x: x['port'])
        else:
            return [{"error": f"nmap scan failed: {result.stderr}"}]
    except subprocess.TimeoutExpired:
        return [{"error": "nmap scan timed out"}]
    except FileNotFoundError:
        return [{"error": "nmap not found on system"}]
    except Exception as e:
        return [{"error": f"nmap scan failed: {str(e)}"}]


@mcp.tool
def scan_subnet(subnet: str) -> List[Dict[str, str]]:
    """
    Scan a subnet for active hosts (simplified)
    """
    import ipaddress
    
    try:
        network = ipaddress.IPv4Network(subnet, strict=False)
        alive_hosts = []
        
        # For each IP in the subnet, check if it's alive (simplified)
        # Note: This is a very simplified subnet scan - real implementations would be more efficient
        for ip in network:
            host = str(ip)
            # Skip network and broadcast addresses in /24 or similar subnets
            if str(ip).endswith('.0') or host.split('.')[-1] in ['255']:
                continue

            # Limit subnet scanning to prevent overwhelming the network
            if len(alive_hosts) >= 20:  # Limit to 20 hosts in the result
                break

            result = scan_host(host)
            if result.get('status') == 'up':
                alive_hosts.append({
                    "host": host,
                    "status": "up"
                })
        
        return alive_hosts
    except Exception as e:
        return [{"error": f"Subnet scan failed: {str(e)}"}]


@mcp.tool
def check_common_services(host: str) -> List[Dict[str, Any]]:
    """
    Check for common services on a host
    """
    common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3389, 3306, 5432]
    return scan_specific_ports(host, common_ports)


@mcp.tool
def create_scan_report(hosts: List[str], scan_results: List[List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Create a formatted scan report combining hosts and their scan results
    """
    report = {
        "generated_at": datetime.now().isoformat(),
        "hosts_scanned": len(hosts),
        "total_open_ports": 0,
        "hosts": []
    }
    
    for i, host in enumerate(hosts):
        if i < len(scan_results):
            host_report = {
                "host": host,
                "open_ports_count": len(scan_results[i]),
                "open_ports": scan_results[i],
                "vulnerability_estimate": estimate_vulnerabilities(scan_results[i])
            }
            report["hosts"].append(host_report)
            report["total_open_ports"] += len(scan_results[i])
    
    return report


def estimate_vulnerabilities(open_ports: List[Dict[str, Any]]) -> str:
    """
    Estimate vulnerability level based on open ports
    """
    high_risk_ports = [21, 23, 135, 139, 445, 1433, 3306, 5432]  # FTP, Telnet, SMB, Databases, etc.
    medium_risk_ports = [22, 25, 110, 143]  # SSH, SMTP, POP3, IMAP
    
    high_risk_count = sum(1 for port_info in open_ports if port_info['port'] in high_risk_ports)
    medium_risk_count = sum(1 for port_info in open_ports if port_info['port'] in medium_risk_ports)
    
    if high_risk_count > 0:
        return "high"
    elif medium_risk_count > 0:
        return "medium"
    else:
        return "low"


# Resources
@mcp.resource("http://port-scanner-mcp-server.local/scanning-guidelines")
def get_scanning_guidelines() -> Dict[str, str]:
    """
    Get guidelines for responsible port scanning
    """
    return {
        "title": "Port Scanning Guidelines",
        "purpose": "Provide guidance for responsible security scanning",
        "best_practices": [
            "Only scan systems you own or have explicit permission to scan",
            "Avoid scanning production systems during business hours",
            "Respect rate limits to avoid impacting system performance",
            "Document and report findings responsibly"
        ],
        "legal_considerations": [
            "Unauthorized scanning may violate laws and terms of service",
            "Always obtain proper authorization before scanning",
            "Follow responsible disclosure practices"
        ]
    }


@mcp.resource("http://port-scanner-mcp-server.local/common-ports")
def get_common_ports() -> List[Dict[str, str]]:
    """
    Get a list of common ports and their associated services
    """
    return [
        {"port": 22, "service": "SSH", "description": "Secure Shell - remote administration"},
        {"port": 80, "service": "HTTP", "description": "Web server"},
        {"port": 443, "service": "HTTPS", "description": "Secure web server"},
        {"port": 3306, "service": "MySQL", "description": "Database service"},
        {"port": 5432, "service": "PostgreSQL", "description": "Database service"},
        {"port": 6379, "service": "Redis", "description": "In-memory data structure store"},
        {"port": 27017, "service": "MongoDB", "description": "NoSQL database"},
        {"port": 5900, "service": "VNC", "description": "Remote desktop service"},
        {"port": 3389, "service": "RDP", "description": "Remote Desktop Protocol"}
    ]


@mcp.resource("http://port-scanner-mcp-server.local/suggested-scans")
def get_suggested_scans() -> List[Dict[str, str]]:
    """
    Get suggested scanning profiles
    """
    return [
        {"name": "Quick Scan", "description": "Scan top 100 ports", "command": "scan_top_ports"},
        {"name": "Full Scan", "description": "Scan all 65535 ports", "command": "scan_ports(1-65535)"},
        {"name": "Service Scan", "description": "Scan for common services", "command": "check_common_services"},
        {"name": "Stealth Scan", "description": "Slow scan to avoid detection", "command": "nmap_scan(-sS)"}
    ]


# Prompts
@mcp.prompt("/vulnerability-assessment")
def vulnerability_assessment_prompt(
    scan_results: List[Dict[str, Any]],
    asset_criticality: str,
    compliance_requirements: List[str],
    context: str = ""
) -> str:
    """
    Generate a prompt for conducting a vulnerability assessment
    """
    return f"""
Conduct a vulnerability assessment based on these scan results: {scan_results}
Asset Criticality: {asset_criticality}
Compliance Requirements: {compliance_requirements}
Context: {context}

Analyze open ports, services, and potential vulnerabilities.
"""


@mcp.prompt("/penetration-testing-plan")
def penetration_testing_prompt(
    target_host: str,
    testing_scope: str,
    authorization: str,
    context: str = ""
) -> str:
    """
    Generate a prompt for planning penetration testing
    """
    return f"""
Plan a penetration testing engagement for: {target_host}
Testing Scope: {testing_scope}
Authorization: {authorization}
Context: {context}

Outline testing methodology, tools, and reporting requirements.
"""


@mcp.prompt("/network-security-review")
def network_security_prompt(
    network_topology: str,
    open_ports: List[Dict[str, Any]],
    security_policy: str,
    context: str = ""
) -> str:
    """
    Generate a prompt for reviewing network security
    """
    return f"""
Review network security for topology: {network_topology}
Open Ports: {open_ports}
Security Policy: {security_policy}
Context: {context}

Identify security gaps and recommend improvements.
"""


@mcp.prompt("/compliance-validation")
def compliance_validation_prompt(
    compliance_framework: str,
    port_scan_results: List[Dict[str, Any]],
    allowed_services: List[str],
    context: str = ""
) -> str:
    """
    Generate a prompt for validating compliance with port restrictions
    """
    return f"""
Validate compliance with framework: {compliance_framework}
Port scan results: {port_scan_results}
Allowed services: {allowed_services}
Context: {context}

Check for unauthorized services and compliance gaps.
"""


if __name__ == "__main__":
    # Use stdio transport for MCP server (proper MCP protocol communication)
    asyncio.run(mcp.run_stdio_async())