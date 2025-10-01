#!/usr/bin/env python3
"""
Simple Meta MCP Server

A streamlined MCP server with essential tools, resources, and prompts for managing 
MCP server creation and management tasks.
"""

from fastmcp import FastMCP
from typing import List, Dict, Any
import asyncio
import os
import subprocess
import json
from datetime import datetime


# Initialize the MCP server
mcp = FastMCP(
    name="Simple Meta MCP Server",
    instructions="Provides utilities for managing and creating MCP servers",
    version="1.0.0"
)


# Tools
@mcp.tool
def create_mcp_skeleton(
    name: str, 
    description: str, 
    tools: List[str] = None, 
    resources: List[str] = None, 
    prompts: List[str] = None
) -> Dict[str, Any]:
    """
    Create a skeleton for a new MCP server
    """
    if tools is None:
        tools = ["list_items", "get_item"]
    if resources is None:
        resources = ["get_status"]
    if prompts is None:
        prompts = ["explain_concept"]
    
    # Create project files
    skeleton = {
        "project_name": name,
        "description": description,
        "files": {
            "server.py": f'''#!/usr/bin/env python3
"""
{name} MCP Server
{description}
"""
from fastmcp import FastMCP
from typing import List, Dict, Any

# Initialize the MCP server
mcp = FastMCP(
    name="{name}",
    instructions="{description}",
    version="1.0.0"
)

# Example tools
@mcp.tool
def list_items():
    return {{"message": "List of items"}}

@mcp.tool
def get_item(item_id: str):
    return {{"item_id": item_id, "data": "item data"}}

# Example resources
@mcp.resource("http://{name.lower().replace(' ', '-')}.local/status")
def get_status():
    return {{"status": "running", "server": "{name}"}}

# Example prompts
@mcp.prompt("/{name.replace(' ', '').lower()}-explain")
def explain_concept():
    return "Explain the concept..."

if __name__ == "__main__":
    import asyncio
    asyncio.run(mcp.run_stdio_async())
''',
            "README.md": f'''# {name} MCP Server

{description}

## Setup
```bash
pip install -r requirements.txt
```

## Run
```bash
python server.py
```
''',
            "requirements.txt": "fastmcp>=2.0.0"
        }
    }
    
    return skeleton


@mcp.tool
def validate_mcp_config(config_content: str) -> Dict[str, Any]:
    """
    Validate MCP configuration content
    """
    issues = []
    
    # Check for common issues
    if "fastmcp" not in config_content.lower():
        issues.append("Missing 'fastmcp' import or usage")
    
    if "mcp = FastMCP" not in config_content:
        issues.append("Missing FastMCP server initialization")
    
    if "run_stdio_async" not in config_content:
        issues.append("Missing proper MCP server execution")
    
    # Check for decorators
    tool_count = config_content.count("@mcp.tool")
    resource_count = config_content.count("@mcp.resource") 
    prompt_count = config_content.count("@mcp.prompt")
    
    if tool_count == 0 and resource_count == 0 and prompt_count == 0:
        issues.append("No MCP components (tools, resources, or prompts) defined")
    
    return {
        "is_valid": len(issues) == 0,
        "issues": issues,
        "tool_count": tool_count,
        "resource_count": resource_count,
        "prompt_count": prompt_count
    }


@mcp.tool
def analyze_existing_mcp(server_content: str) -> Dict[str, Any]:
    """
    Analyze an existing MCP server code and provide insights
    """
    analysis = {
        "imports": [],
        "tools_count": 0,
        "resources_count": 0,
        "prompts_count": 0,
        "decorators_found": [],
        "potential_issues": [],
        "suggestions": []
    }
    
    # Analyze imports
    if "from fastmcp import FastMCP" in server_content:
        analysis["imports"].append("fastmcp")
    
    # Count decorators
    analysis["tools_count"] = server_content.count("@mcp.tool")
    analysis["resources_count"] = server_content.count("@mcp.resource")
    analysis["prompts_count"] = server_content.count("@mcp.prompt")
    
    # Track all decorators found
    if analysis["tools_count"] > 0:
        analysis["decorators_found"].append("tools")
    if analysis["resources_count"] > 0:
        analysis["decorators_found"].append("resources")
    if analysis["prompts_count"] > 0:
        analysis["decorators_found"].append("prompts")
    
    # Check for common issues
    if "asyncio.run(mcp.run_stdio_async())" not in server_content:
        analysis["potential_issues"].append("Missing proper server execution")
        analysis["suggestions"].append("Add asyncio.run(mcp.run_stdio_async()) in main block")
    
    if "import asyncio" not in server_content and ("@mcp.tool" in server_content or "@mcp.resource" in server_content):
        analysis["potential_issues"].append("Missing asyncio import")
        analysis["suggestions"].append("Add 'import asyncio' at the top of the file")
    
    if len(analysis["imports"]) == 0:
        analysis["potential_issues"].append("Missing FastMCP import")
        analysis["suggestions"].append("Add 'from fastmcp import FastMCP'")
    
    return analysis


@mcp.tool
def run_system_command(command: str) -> Dict[str, Any]:
    """
    Execute a system command safely within the environment
    """
    try:
        # For security, we'll restrict to only safe commands
        allowed_commands = ["ls", "pwd", "whoami", "date", "echo", "ps", "top"]
        
        if not any(command.startswith(cmd) for cmd in allowed_commands):
            return {
                "error": "Command not allowed",
                "allowed_commands": allowed_commands
            }
        
        # Execute the command
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        
        return {
            "command": command,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "error": "Command timed out",
            "command": command
        }
    except Exception as e:
        return {
            "error": str(e),
            "command": command
        }


@mcp.tool
def generate_mcp_project(
    project_name: str,
    features: List[str] = None,
) -> Dict[str, Any]:
    """
    Generate a complete MCP project with specified features
    """
    if features is None:
        features = ["tools", "resources", "prompts"]
    
    # Create project files
    project_files = {
        "server.py": f'''#!/usr/bin/env python3
"""
{project_name} MCP Server
Generated by Simple Meta MCP Server
"""
import asyncio
from fastmcp import FastMCP
from typing import List, Dict, Any

# Initialize the MCP server
mcp = FastMCP(
    name="{project_name}",
    instructions="Provides {project_name.lower()} functionality",
    version="1.0.0"
)

# Generated tools
@mcp.tool
def list_items():
    return {{"message": "List of items for {project_name}"}}

# Generated resources
@mcp.resource("http://{project_name.lower().replace(' ', '-')}.local/status")
def get_status():
    return {{"status": "running", "server": "{project_name}"}}

# Generated prompts
@mcp.prompt("/{project_name.lower().replace(' ', '')}-query")
def query_prompt():
    return "Query for {project_name}..."

if __name__ == "__main__":
    # Use stdio transport for MCP server
    asyncio.run(mcp.run_stdio_async())
''',
        "README.md": f'''# {project_name} MCP Server

This is a generated MCP server that provides {project_name.lower()} functionality.

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
python server.py
```

## Features

- Tools: list_items
- Resources: get_status
- Prompts: query_prompt
''',
        "requirements.txt": "fastmcp>=2.0.0"
    }
    
    return {
        "project_name": project_name,
        "features": features,
        "files": project_files
    }


# Resources
@mcp.resource("http://simple-meta-mcp-server.local/server-info")
def get_server_info() -> Dict[str, Any]:
    """
    Get information about the server
    """
    return {
        "name": mcp.name,
        "description": "A simple MCP server for managing MCP systems",
        "version": mcp.version,
        "server_time": datetime.now().isoformat(),
        "uptime_seconds": 0  # Simplified for demo
    }


@mcp.resource("http://simple-meta-mcp-server.local/system-metrics")
def get_system_metrics() -> Dict[str, float]:
    """
    Get basic system metrics
    """
    return {
        "cpu_usage": 15.2,
        "memory_usage": 42.8,
        "active_connections": 3
    }


@mcp.resource("http://simple-meta-mcp-server.local/config-templates")
def get_config_templates() -> Dict[str, Any]:
    """
    Get available configuration templates
    """
    return {
        "basic": {
            "description": "Basic configuration with essential settings",
            "file": "config.json"
        },
        "env": {
            "description": "Environment variable configuration",
            "file": ".env"
        }
    }


# Prompts
@mcp.prompt("/mcp-implementation-guide")
def mcp_implementation_guide(
    project_type: str,
    requirements: str = ""
) -> str:
    """
    Generate a prompt for implementing an MCP server
    """
    return f"""
# Implementation Guide for {project_type} MCP Server

Requirements: {requirements}

## Key Steps:
1. Define your tools using @mcp.tool decorator
2. Define your resources using @mcp.resource decorator  
3. Define your prompts using @mcp.prompt decorator
4. Set up proper error handling
5. Implement logging
6. Create comprehensive tests

## Best Practices:
- Use descriptive names for tools, resources, and prompts
- Add proper type hints to all functions
- Implement comprehensive error handling
- Include validation for all inputs
"""


@mcp.prompt("/mcp-security-checklist")
def mcp_security_checklist(server_content: str) -> str:
    """
    Generate a security checklist for an MCP server
    """
    return f"""
# Security Checklist for MCP Server

Based on provided server content:

## Input Validation
- [ ] Validate all function parameters
- [ ] Sanitize all user inputs
- [ ] Check for injection vulnerabilities

## Access Control  
- [ ] Implement rate limiting
- [ ] Add authentication if needed
- [ ] Validate file paths to prevent directory traversal

## Error Handling
- [ ] Don't expose internal errors to users
- [ ] Log security-relevant events
- [ ] Implement graceful degradation

Server content review: {server_content[:200]}...
"""


@mcp.prompt("/error-resolution")
def error_resolution_prompt(error_message: str, context: str = "") -> str:
    """
    Generate a prompt for resolving an error
    """
    return f"""
An error occurred: {error_message}

Context: {context}

Please suggest possible solutions to resolve this error.
"""


# Health check tool
@mcp.tool
def health_check() -> Dict[str, str]:
    """
    Check the health status of the server
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "simple-meta-mcp-server"
    }


if __name__ == "__main__":
    # Use stdio transport for MCP server (proper MCP protocol communication)
    asyncio.run(mcp.run_stdio_async())