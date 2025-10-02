#!/usr/bin/env python3
"""
Firewall MCP Server

Provides access to firewall management functionality for LLMs through MCP protocol.
"""

from fastmcp import FastMCP
from typing import List, Dict, Any
import asyncio
import subprocess
import json
from datetime import datetime


# Initialize the MCP server
mcp = FastMCP(
    name="Firewall MCP Server",
    instructions="Provides access to firewall management functionality including rule management, port configuration, and security policy enforcement",
    version="1.0.0"
)


# Tools
@mcp.tool
def list_firewall_rules() -> List[Dict[str, Any]]:
    """
    List current firewall rules (assumes iptables)
    """
    try:
        # Get iptables rules
        result = subprocess.run(['sudo', 'iptables', '-L', '-n', '-v'], 
                                capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            rules = []
            lines = result.stdout.strip().split('\n')
            
            current_chain = None
            for line in lines:
                if line.startswith('Chain'):
                    current_chain = line.split()[1]
                elif line.startswith('num') or line.startswith('target') or not line.strip():
                    continue  # Skip header lines
                elif len(line.strip()) > 0 and not line.startswith(' '):
                    # Parse rule line (simplified)
                    parts = line.split()
                    if len(parts) >= 4:
                        rules.append({
                            "chain": current_chain,
                            "target": parts[0],
                            "prot": parts[1],
                            "opt": parts[2] if len(parts) > 2 else "",
                            "source": parts[3] if len(parts) > 3 else "",
                            "destination": parts[4] if len(parts) > 4 else "",
                            "raw": line.strip()
                        })
            return rules
        else:
            return [{"error": "Failed to list firewall rules", "details": result.stderr}]
    except subprocess.TimeoutExpired:
        return [{"error": "Timeout while listing firewall rules"}]
    except Exception as e:
        return [{"error": str(e)}]


@mcp.tool
def add_firewall_rule(
    chain: str, 
    protocol: str, 
    port: str, 
    action: str, 
    source: str = "0.0.0.0/0",
    destination: str = "0.0.0.0/0"
) -> Dict[str, str]:
    """
    Add a new firewall rule
    """
    try:
        # Construct iptables command
        cmd = ['sudo', 'iptables', '-A', chain, '-p', protocol, '--dport', str(port), '-j', action]
        if source != "0.0.0.0/0":
            cmd.extend(['-s', source])
        if destination != "0.0.0.0/0":
            cmd.extend(['-d', destination])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return {
                "status": "success",
                "message": f"Rule added to {chain} chain: {action} {protocol} port {port}"
            }
        else:
            return {
                "status": "error",
                "message": result.stderr
            }
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": "Timeout while adding firewall rule"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@mcp.tool
def remove_firewall_rule(chain: str, rule_number: int) -> Dict[str, str]:
    """
    Remove a firewall rule by chain and rule number
    """
    try:
        result = subprocess.run(['sudo', 'iptables', '-D', chain, str(rule_number)], 
                                capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return {
                "status": "success",
                "message": f"Rule {rule_number} removed from {chain} chain"
            }
        else:
            return {
                "status": "error",
                "message": result.stderr
            }
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": "Timeout while removing firewall rule"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@mcp.tool
def get_firewall_status() -> Dict[str, str]:
    """
    Get the status of the firewall service
    """
    try:
        result = subprocess.run(['sudo', 'ufw', 'status'], 
                                capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            status = result.stdout.strip()
            return {
                "status": "success",
                "message": status
            }
        else:
            # If ufw is not available, try iptables
            try:
                result = subprocess.run(['sudo', 'systemctl', 'is-active', 'iptables'], 
                                        capture_output=True, text=True, timeout=10)
                return {
                    "status": "success",
                    "message": f"iptables status: {result.stdout.strip()}"
                }
            except:
                return {
                    "status": "error",
                    "message": "Unable to determine firewall service status"
                }
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": "Timeout while checking firewall status"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@mcp.tool
def enable_firewall() -> Dict[str, str]:
    """
    Enable the firewall service
    """
    try:
        result = subprocess.run(['sudo', 'ufw', 'enable'], 
                                capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return {
                "status": "success",
                "message": "Firewall enabled successfully"
            }
        else:
            return {
                "status": "error",
                "message": result.stderr
            }
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": "Timeout while enabling firewall"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@mcp.tool
def disable_firewall() -> Dict[str, str]:
    """
    Disable the firewall service
    """
    try:
        result = subprocess.run(['sudo', 'ufw', 'disable'], 
                                capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return {
                "status": "success",
                "message": "Firewall disabled successfully"
            }
        else:
            return {
                "status": "error",
                "message": result.stderr
            }
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": "Timeout while disabling firewall"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@mcp.tool
def allow_port(port: str, protocol: str = "tcp") -> Dict[str, str]:
    """
    Allow traffic on a specific port
    """
    try:
        result = subprocess.run(['sudo', 'ufw', 'allow', f'{port}/{protocol}'], 
                                capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return {
                "status": "success",
                "message": f"Port {port}/{protocol} allowed successfully"
            }
        else:
            return {
                "status": "error",
                "message": result.stderr
            }
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": f"Timeout while allowing port {port}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@mcp.tool
def deny_port(port: str, protocol: str = "tcp") -> Dict[str, str]:
    """
    Deny traffic on a specific port
    """
    try:
        result = subprocess.run(['sudo', 'ufw', 'deny', f'{port}/{protocol}'], 
                                capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return {
                "status": "success",
                "message": f"Port {port}/{protocol} denied successfully"
            }
        else:
            return {
                "status": "error",
                "message": result.stderr
            }
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": f"Timeout while denying port {port}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@mcp.tool
def allow_ip(ip_address: str) -> Dict[str, str]:
    """
    Allow traffic from a specific IP address
    """
    try:
        result = subprocess.run(['sudo', 'ufw', 'allow', 'from', ip_address], 
                                capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return {
                "status": "success",
                "message": f"IP {ip_address} allowed successfully"
            }
        else:
            return {
                "status": "error",
                "message": result.stderr
            }
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": f"Timeout while allowing IP {ip_address}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@mcp.tool
def block_ip(ip_address: str) -> Dict[str, str]:
    """
    Block traffic from a specific IP address
    """
    try:
        result = subprocess.run(['sudo', 'ufw', 'deny', 'from', ip_address], 
                                capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return {
                "status": "success",
                "message": f"IP {ip_address} blocked successfully"
            }
        else:
            return {
                "status": "error",
                "message": result.stderr
            }
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": f"Timeout while blocking IP {ip_address}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


# Resources
@mcp.resource("http://firewall-mcp-server.local/active-rules")
def get_active_rules() -> List[Dict[str, str]]:
    """
    Get currently active firewall rules
    """
    # This would return the currently active rules
    return [
        {"rule": "allow 22/tcp", "description": "SSH access"},
        {"rule": "allow 80/tcp", "description": "HTTP traffic"},
        {"rule": "allow 443/tcp", "description": "HTTPS traffic"},
        {"rule": "deny 1433/tcp", "description": "Block SQL Server"}
    ]


@mcp.resource("http://firewall-mcp-server.local/security-policy")
def get_security_policy() -> Dict[str, Any]:
    """
    Get the current security policy
    """
    return {
        "default_policy": {
            "input": "DROP",
            "output": "ACCEPT",
            "forward": "DROP"
        },
        "logging": {
            "enabled": True,
            "level": "medium"
        },
        "rate_limiting": {
            "enabled": True,
            "threshold": "100 connections per minute"
        }
    }


@mcp.resource("http://firewall-mcp-server.local/ports-status")
def get_open_ports() -> List[Dict[str, str]]:
    """
    Get information about open ports (assumes netstat or ss)
    """
    try:
        result = subprocess.run(['ss', '-tuln'], 
                                capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            ports = []
            for line in result.stdout.strip().split('\n'):
                if line.startswith('LISTEN'):
                    parts = line.split()
                    if len(parts) >= 5:
                        ports.append({
                            "protocol": parts[0],
                            "state": "LISTENING",
                            "port": parts[4]  # Address:Port format
                        })
            return ports
        else:
            return [{"error": "Failed to get open ports", "details": result.stderr}]
    except Exception as e:
        return [{"error": str(e)}]


# Prompts
@mcp.prompt("/firewall-security-assessment")
def security_assessment_prompt(
    network_topology: str,
    security_requirements: List[str],
    compliance_standards: List[str],
    context: str = ""
) -> str:
    """
    Generate a prompt for conducting a firewall security assessment
    """
    return f"""
Conduct a firewall security assessment for network topology: {network_topology}
Security Requirements: {security_requirements}
Compliance Standards: {compliance_standards}
Context: {context}

Review rules, identify vulnerabilities, and recommend improvements.
"""


@mcp.prompt("/firewall-rule-optimization")
def rule_optimization_prompt(
    current_rules: List[str],
    performance_issues: List[str],
    business_requirements: List[str],
    context: str = ""
) -> str:
    """
    Generate a prompt for optimizing firewall rules
    """
    return f"""
Optimize firewall rules: {current_rules}
Addressing performance issues: {performance_issues}
Business requirements: {business_requirements}
Context: {context}

Suggest rule consolidation, ordering, and performance improvements.
"""


@mcp.prompt("/threat-response-plan")
def threat_response_prompt(
    threat_type: str,
    affected_systems: List[str],
    ioa_indicators: List[str],
    context: str = ""
) -> str:
    """
    Generate a prompt for creating a threat response plan
    """
    return f"""
Create a threat response plan for: {threat_type}
Affected Systems: {affected_systems}
Indicators of Attack: {ioa_indicators}
Context: {context}

Outline immediate actions including firewall rule changes.
"""


@mcp.prompt("/compliance-audit")
def compliance_audit_prompt(
    compliance_framework: str,
    firewall_rules: List[str],
    audit_requirements: List[str],
    context: str = ""
) -> str:
    """
    Generate a prompt for firewall compliance auditing
    """
    return f"""
Perform a compliance audit for framework: {compliance_framework}
Current firewall rules: {firewall_rules}
Audit requirements: {audit_requirements}
Context: {context}

Ensure rules meet compliance standards and document findings.
"""


if __name__ == "__main__":
    # Use stdio transport for MCP server (proper MCP protocol communication)
    asyncio.run(mcp.run_stdio_async())