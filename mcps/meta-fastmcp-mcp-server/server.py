#!/usr/bin/env python3
"""
Professional MCP Server using FastMCP with Advanced Features

This server provides a comprehensive set of tools, resources, and prompts
for managing agent-based systems and general utility functions.
Incorporates advanced features from the docs server including caching,
rate limiting, configuration management, and enhanced logging.
"""

import pathlib  # Import at the top to use in config
from fastmcp import FastMCP
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import asyncio
import datetime
import os
import subprocess
import json
import glob
from pathlib import Path
import re
import logging
import hashlib
from datetime import datetime, timedelta
import time
import yaml


# Set up logging
logging.basicConfig(
    level=os.getenv("FASTMCP_LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Configuration class for server settings
class ServerConfig:
    """Configuration class to manage server settings"""
    
    def __init__(self):
        # Server settings
        self.name = os.getenv("FASTMCP_SERVER_NAME", "Meta FastMCP Server")
        self.version = os.getenv("FASTMCP_VERSION", "2.0.0")
        self.instructions = os.getenv("FASTMCP_INSTRUCTIONS", "A professional MCP server for managing agent systems and providing utility functions")
        
        # Cache settings
        self.cache_max_size = int(os.getenv("CACHE_MAX_SIZE", "100"))
        self.cache_ttl = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes in seconds
        
        # Rate limiting settings
        self.rate_limit_max_requests = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "100"))
        self.rate_limit_window = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # 1 hour in seconds
        
        # Server settings
        self.host = os.getenv("FASTMCP_HOST", "127.0.0.1")
        self.port = int(os.getenv("FASTMCP_PORT", "8000"))
        self.log_level = os.getenv("FASTMCP_LOG_LEVEL", "INFO")
        
        # Security settings
        self.allow_directory_traversal = os.getenv("ALLOW_DIRECTORY_TRAVERSAL", "false").lower() == "true"
        
        # Load from config file if it exists
        self.load_from_config_file()
    
    def load_from_config_file(self):
        """Load configuration from config.json file if it exists"""
        config_file_paths = [
            os.path.join(os.path.dirname(__file__), "config.json"),
            os.path.join(os.path.dirname(__file__), "config.yaml"),
            os.path.join(os.path.dirname(__file__), "config.yml")
        ]
        
        for config_path in config_file_paths:
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        if config_path.endswith('.json'):
                            config_data = json.load(f)
                        else:  # YAML file
                            config_data = yaml.safe_load(f)
                    
                    # Update configuration from file
                    for key, value in config_data.items():
                        if hasattr(self, key):
                            setattr(self, key, value)
                    
                    logger.info(f"Configuration loaded from {config_path}")
                    return
                except Exception as e:
                    logger.error(f"Error loading configuration from {config_path}: {e}")
    
    def to_dict(self):
        """Convert configuration to dictionary for debugging/inspection"""
        return {
            'name': self.name,
            'version': self.version,
            'cache_max_size': self.cache_max_size,
            'cache_ttl': self.cache_ttl,
            'rate_limit_max_requests': self.rate_limit_max_requests,
            'rate_limit_window': self.rate_limit_window,
            'host': self.host,
            'port': self.port,
            'log_level': self.log_level,
            'allow_directory_traversal': self.allow_directory_traversal
        }


# Load configuration
config = ServerConfig()


class AgentConfig(BaseModel):
    """Configuration for an agent"""
    name: str
    type: str
    enabled: bool = True
    parameters: Dict[str, Any] = {}


class TaskRequest(BaseModel):
    """Request for a task execution"""
    task_id: str
    description: str
    priority: int = 1
    timeout: Optional[int] = None


# Initialize the MCP server with configuration
mcp = FastMCP(
    name=config.name,
    instructions=config.instructions,
    version=config.version
)


# Cache for storing search results and file contents
class DocumentCache:
    def __init__(self, max_size: int = None, ttl: int = None):
        # Use config values if available, otherwise defaults
        self.max_size = max_size if max_size is not None else config.cache_max_size
        self.ttl = ttl if ttl is not None else config.cache_ttl
        self.cache = {}
        self.access_times = {}
    
    def _is_expired(self, key: str) -> bool:
        if key not in self.access_times:
            return True
        return time.time() - self.access_times[key] > self.ttl
    
    def get(self, key: str):
        if key in self.cache and not self._is_expired(key):
            self.access_times[key] = time.time()
            return self.cache[key]
        elif key in self.cache:
            # Remove expired entry
            del self.cache[key]
            del self.access_times[key]
        return None
    
    def set(self, key: str, value):
        # Remove oldest entries if cache is full
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
            del self.cache[oldest_key]
            del self.access_times[oldest_key]
        
        self.cache[key] = value
        self.access_times[key] = time.time()
    
    def clear(self):
        self.cache.clear()
        self.access_times.clear()

# Initialize cache
doc_cache = DocumentCache()

# Rate limiting
class RateLimiter:
    def __init__(self, max_requests: int = None, window_seconds: int = None):
        self.max_requests = max_requests if max_requests is not None else config.rate_limit_max_requests
        self.window_seconds = window_seconds if window_seconds is not None else config.rate_limit_window
        self.requests = {}
    
    def is_allowed(self, identifier: str = "default") -> bool:
        now = time.time()
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        # Remove old requests outside the window
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if now - req_time < self.window_seconds
        ]
        
        if len(self.requests[identifier]) >= self.max_requests:
            return False
        
        # Add current request
        self.requests[identifier].append(now)
        return True

rate_limiter = RateLimiter()

def get_cache_key(*args, **kwargs) -> str:
    """Generate a cache key from function arguments"""
    key_data = str(args) + str(sorted(kwargs.items()))
    return hashlib.md5(key_data.encode()).hexdigest()

def rate_limit_check(identifier: str = "default"):
    """Decorator to check rate limiting"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not rate_limiter.is_allowed(identifier):
                raise Exception(f"Rate limit exceeded for {identifier}")
            return func(*args, **kwargs)
        return wrapper
    return decorator


def _create_agent_impl(config: AgentConfig) -> Dict[str, Any]:
    """
    Create a new agent with the specified configuration - core implementation
    """
    try:
        logger.info(f"Creating agent with config: {config}")
        
        # Rate limit check
        if not rate_limiter.is_allowed("create_agent"):
            logger.warning("Rate limit exceeded for create_agent operation")
            raise Exception("Rate limit exceeded. Please try again later.")
        
        agent_id = f"agent_{len(str(datetime.datetime.now().timestamp()))}"
        agent_info = {
            "id": agent_id,
            "config": config.model_dump(),
            "created_at": datetime.datetime.now().isoformat(),
            "status": "created"
        }
        
        # In a real implementation, this would create the actual agent
        logger.info(f"Created agent: {agent_id} with config: {config}")
        
        # Cache the agent
        cache_key = get_cache_key("_create_agent_impl", agent_id)
        doc_cache.set(cache_key, agent_info)
        
        return agent_info
    except Exception as e:
        logger.error(f"Error creating agent: {str(e)}")
        raise


@mcp.tool
def create_agent(config: AgentConfig) -> Dict[str, Any]:
    """
    Create a new agent with the specified configuration
    """
    return _create_agent_impl(config)


def _delete_agent_impl(agent_id: str) -> Dict[str, str]:
    """
    Delete an existing agent by ID - core implementation
    """
    try:
        logger.info(f"Deleting agent: {agent_id}")
        
        # Rate limit check
        if not rate_limiter.is_allowed("delete_agent"):
            logger.warning(f"Rate limit exceeded for deleting agent: {agent_id}")
            raise Exception("Rate limit exceeded. Please try again later.")
        
        # Remove from cache if exists
        cache_key = get_cache_key("_create_agent_impl", agent_id)
        if doc_cache.get(cache_key):
            doc_cache.cache.pop(cache_key, None)
            doc_cache.access_times.pop(cache_key, None)
        
        # In a real implementation, this would delete the actual agent
        logger.info(f"Deleted agent: {agent_id}")
        
        return {
            "message": f"Agent {agent_id} deleted successfully",
            "status": "deleted",
            "agent_id": agent_id
        }
    except Exception as e:
        logger.error(f"Error deleting agent {agent_id}: {str(e)}")
        raise


@mcp.tool
def delete_agent(agent_id: str) -> Dict[str, str]:
    """
    Delete an existing agent by ID
    """
    return _delete_agent_impl(agent_id)


def _list_agents_impl() -> List[Dict[str, Any]]:
    """
    List all available agents - core implementation
    """
    try:
        logger.info("Listing all agents")
        
        # Rate limit check
        if not rate_limiter.is_allowed("list_agents"):
            logger.warning("Rate limit exceeded for list_agents operation")
            raise Exception("Rate limit exceeded. Please try again later.")
        
        cache_key = get_cache_key("_list_agents_impl")
        cached_result = doc_cache.get(cache_key)
        if cached_result is not None:
            logger.info("Returning cached result for list_agents")
            return cached_result
        
        # Simulated list of agents
        agents = [
            {
                "id": "agent_12345",
                "name": "DataProcessor",
                "type": "processing",
                "status": "running",
                "created_at": "2025-10-01T10:00:00Z"
            },
            {
                "id": "agent_67890",
                "name": "NotificationHandler",
                "type": "notification",
                "status": "idle",
                "created_at": "2025-10-01T10:05:00Z"
            }
        ]
        
        doc_cache.set(cache_key, agents)
        logger.info(f"Listed {len(agents)} agents")
        return agents
    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
        raise


@mcp.tool
def list_agents() -> List[Dict[str, Any]]:
    """
    List all available agents
    """
    return _list_agents_impl()


def _execute_task_impl(task: TaskRequest) -> Dict[str, Any]:
    """
    Execute a task with the given parameters - core implementation
    """
    try:
        logger.info(f"Executing task: {task.task_id}")
        
        # Rate limit check
        if not rate_limiter.is_allowed("execute_task"):
            logger.warning(f"Rate limit exceeded for executing task: {task.task_id}")
            raise Exception("Rate limit exceeded. Please try again later.")
        
        result = {
            "task_id": task.task_id,
            "status": "completed",
            "executed_at": datetime.datetime.now().isoformat(),
            "result": f"Task {task.task_id} completed successfully",
            "description": task.description
        }
        
        # In a real implementation, this would execute the actual task
        logger.info(f"Executing task: {task.task_id} - {task.description}")
        
        # Cache the task result
        cache_key = get_cache_key("_execute_task_impl", task.task_id)
        doc_cache.set(cache_key, result)
        
        return result
    except Exception as e:
        logger.error(f"Error executing task {task.task_id}: {str(e)}")
        raise


@mcp.tool
def execute_task(task: TaskRequest) -> Dict[str, Any]:
    """
    Execute a task with the given parameters
    """
    return _execute_task_impl(task)


@mcp.tool
def run_system_command(command: str) -> Dict[str, Any]:
    """
    Execute a system command safely within the environment
    """
    try:
        # For security, we'll restrict to only safe commands
        allowed_commands = ["ls", "pwd", "whoami", "date", "echo"]
        
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
async def async_operation_simulation(data: str, delay: float = 1.0) -> str:
    """
    Simulate an asynchronous operation with a delay
    """
    await asyncio.sleep(delay)
    return f"Async operation completed with data: {data}"


@mcp.resource("http://meta-fastmcp-server.local/server-info")
def get_server_info() -> Dict[str, Any]:
    """
    Get information about the server
    """
    return {
        "name": mcp.name,
        "description": "A professional MCP server for managing agent systems and providing utility functions",
        "version": mcp.version,
        "server_time": datetime.datetime.now().isoformat(),
        "uptime_seconds": 0  # Simplified for demo
    }


@mcp.resource("http://meta-fastmcp-server.local/agent-types")
def get_agent_types() -> List[Dict[str, str]]:
    """
    Get available agent types
    """
    return [
        {"name": "DataProcessor", "description": "Processes data streams"},
        {"name": "NotificationHandler", "description": "Handles notifications"},
        {"name": "Scheduler", "description": "Manages scheduled tasks"},
        {"name": "Monitor", "description": "Monitors system health"}
    ]


@mcp.resource("http://meta-fastmcp-server.local/system-metrics")
def get_system_metrics() -> Dict[str, float]:
    """
    Get basic system metrics
    """
    # In a real implementation, this would gather actual system metrics
    return {
        "cpu_usage": 15.2,
        "memory_usage": 42.8,
        "disk_usage": 65.3,
        "active_connections": 3
    }


@mcp.prompt("/agent-selection")
def agent_selection_prompt(agent_types: List[str], task_description: str) -> str:
    """
    Generate a prompt for selecting the appropriate agent for a task
    """
    return f"""
    Given the following agent types: {', '.join(agent_types)}
    
    And the following task: {task_description}
    
    Please select the most appropriate agent type to handle this task and explain your reasoning.
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


@mcp.prompt("/task-breakdown")
def task_breakdown_prompt(task_description: str, steps: int = 5) -> str:
    """
    Generate a prompt for breaking down a complex task
    """
    return f"""
    Break down the following task into {steps} detailed steps:
    
    Task: {task_description}
    
    Provide a clear, sequential breakdown of how to accomplish this task.
    """


def _get_server_health_impl() -> Dict[str, Any]:
    """
    Get the health status of the server - core implementation
    """
    try:
        logger.info("Getting server health")
        
        cache_key = get_cache_key("_get_server_health_impl")
        cached_result = doc_cache.get(cache_key)
        if cached_result is not None:
            logger.info("Returning cached result for server health")
            return cached_result
        
        health = {
            "status": "healthy",
            "timestamp": datetime.datetime.now().isoformat(),
            "service": "meta-fastmcp-server",
            "server_config": {
                "name": config.name,
                "version": config.version,
                "host": config.host,
                "port": config.port
            },
            "cache_stats": {
                "cache_size": len(doc_cache.cache),
                "max_size": doc_cache.max_size,
                "ttl_seconds": doc_cache.ttl
            }
        }
        
        doc_cache.set(cache_key, health)
        logger.info("Server health check completed")
        return health
    except Exception as e:
        logger.error(f"Error getting server health: {str(e)}")
        raise


@mcp.tool
def health_check() -> Dict[str, str]:
    """
    Check the health status of the server
    """
    return _get_server_health_impl()


# Additional utility tools
@mcp.tool
def calculate_expression(expression: str) -> float:
    """
    Safely calculate a mathematical expression
    """
    # For security, we'll only allow safe mathematical operations
    allowed_chars = set('0123456789+-*/.() ')
    
    if not all(c in allowed_chars for c in expression):
        raise ValueError("Invalid characters in expression")
    
    try:
        # Evaluate the expression (in a real implementation, use a safer method)
        result = eval(expression)  # NOQA: S307 This is a controlled environment
        return float(result)
    except Exception as e:
        raise ValueError(f"Invalid expression: {str(e)}")


def _create_mcp_skeleton_impl(
    name: str, 
    description: str, 
    tools: List[str] = None, 
    resources: List[str] = None, 
    prompts: List[str] = None
) -> Dict[str, Any]:
    """
    Create a skeleton for a new MCP server - core implementation
    """
    try:
        logger.info(f"Creating MCP skeleton for: {name}")
        
        if not name or not isinstance(name, str):
            raise ValueError("Name must be a non-empty string")
        
        if tools is None:
            tools = ["list_items", "get_item", "search_items"]
        if resources is None:
            resources = ["get_status", "get_config"]
        if prompts is None:
            prompts = ["explain_concept", "implementation_guide"]
        
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
{chr(10).join([f"@mcp.tool{chr(10)}def {tool}():{chr(10)}    return \\\"\\\"\\\"Tool implementation for {tool}\\\"\\\"\\\"{chr(10)}" for tool in tools])}

# Example resources
{chr(10).join([f"@mcp.resource(\\\"http://{name.replace(' ', '-').lower()}.local/{resource}\\\"){chr(10)}def get_{resource}():{chr(10)}    return {{\\\"message\\\": \\\"Resource implementation for {resource}\\\"}}{chr(10)}" for resource in resources])}

# Example prompts
{chr(10).join([f"@mcp.prompt(\\\"/{name.replace(' ', '').lower()}-{prompt}\\\"){chr(10)}def {prompt}_prompt():{chr(10)}    return \\\"\\\"\\\"Prompt for {name} {prompt}\\\"\\\"\\\"{chr(10)}" for prompt in prompts])}

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

## Features
- Tools: {", ".join(tools)}
- Resources: {", ".join(resources)}
- Prompts: {", ".join(prompts)}
''',
                "requirements.txt": "fastmcp>=2.0.0\npydantic>=2.0.0\nanyio>=4.0.0",
                "Dockerfile": f'''# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \\
    PYTHONUNBUFFERED=1 \\
    FASTMCP_HOST=0.0.0.0 \\
    FASTMCP_PORT=8001

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \\
    && apt-get install -y --no-install-recommends \\
        build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8001

# Run the application
CMD ["python", "server.py"]
''',
                "docker-compose.yml": f'''version: '3.8'

services:
  {name.replace(" ", "-").lower()}:
    build: .
    ports:
      - "8001:8001"
    environment:
      - FASTMCP_HOST=0.0.0.0
      - FASTMCP_PORT=8001
    restart: unless-stopped
'''
            }
        }
        
        return skeleton
    except Exception as e:
        logger.error(f"Error creating MCP skeleton for {name}: {str(e)}")
        raise


def _validate_mcp_config_impl(config_content: str) -> Dict[str, Any]:
    """
    Validate MCP configuration content - core implementation
    """
    try:
        logger.info("Validating MCP configuration")
        
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
    except Exception as e:
        logger.error(f"Error validating MCP configuration: {str(e)}")
        raise


def _analyze_existing_mcp_impl(server_content: str) -> Dict[str, Any]:
    """
    Analyze an existing MCP server code and provide insights - core implementation
    """
    try:
        logger.info("Analyzing existing MCP server code")
        
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
        
        # Check for error handling
        if "try:" not in server_content and ("@mcp.tool" in server_content or "@mcp.resource" in server_content):
            analysis["suggestions"].append("Consider adding error handling to your functions")
        
        return analysis
    except Exception as e:
        logger.error(f"Error analyzing existing MCP code: {str(e)}")
        raise


# Enhanced tools from the docs server
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
    return _create_mcp_skeleton_impl(name, description, tools, resources, prompts)


@mcp.tool
def validate_mcp_config(config_content: str) -> Dict[str, Any]:
    """
    Validate MCP configuration content
    """
    return _validate_mcp_config_impl(config_content)


@mcp.tool
def analyze_existing_mcp(server_content: str) -> Dict[str, Any]:
    """
    Analyze an existing MCP server code and provide insights
    """
    return _analyze_existing_mcp_impl(server_content)


@mcp.resource("http://meta-fastmcp-server.local/documentation-links")
def get_documentation_links() -> Dict[str, str]:
    """
    Get useful documentation links
    """
    return {
        "fastmcp_docs": "https://gofastmcp.com",
        "mcp_specification": "https://modelcontextprotocol.ai",
        "python_sdk": "https://github.com/modelcontextprotocol/python-sdk"
    }


@mcp.resource("http://meta-fastmcp-server.local/server-stats")
def get_server_stats() -> Dict[str, Any]:
    """
    Get server statistics including cache and rate limiting info
    """
    return {
        "server_info": {
            "name": config.name,
            "version": config.version,
            "host": config.host,
            "port": config.port,
        },
        "cache_stats": {
            "cache_size": len(doc_cache.cache),
            "cache_keys": list(doc_cache.cache.keys())[:10],  # First 10 keys
            "max_size": doc_cache.max_size,
            "ttl_seconds": doc_cache.ttl
        },
        "rate_limiting_stats": {
            "requests_tracking": {k: len(v) for k, v in rate_limiter.requests.items()},
            "max_requests": rate_limiter.max_requests,
            "window_seconds": rate_limiter.window_seconds
        },
        "server_uptime": datetime.datetime.now().isoformat()
    }


@mcp.tool
def clear_cache() -> Dict[str, str]:
    """
    Clear the server cache
    """
    doc_cache.clear()
    logger.info("Document cache cleared")
    return {"message": "Cache cleared successfully"}


# MCP Creation Tools for 100% Coverage

def _generate_mcp_project_impl(
    project_name: str,
    project_type: str = "basic", 
    features: List[str] = None,
    include_examples: bool = True,
    include_tests: bool = True,
    include_docs: bool = True
) -> Dict[str, Any]:
    """
    Generate a complete MCP project with specified features - core implementation
    """
    try:
        logger.info(f"Generating MCP project: {project_name} (type: {project_type})")
        
        if not project_name or not isinstance(project_name, str):
            raise ValueError("Project name must be a non-empty string")
        
        if features is None:
            features = ["tools", "resources", "prompts"]
        
        # Define templates for different project types
        project_templates = {
            "basic": {
                "tools": ["list_items", "get_item", "search_items"],
                "resources": ["get_status", "get_config"],
                "prompts": ["query_handler", "task_planner"]
            },
            "documentation": {
                "tools": ["search_docs", "read_file", "list_sections"],
                "resources": ["get_toc", "get_stats"],
                "prompts": ["documentation_query", "explanation_generator"]
            },
            "agent": {
                "tools": ["create_agent", "list_agents", "execute_task"],
                "resources": ["get_agent_types", "get_system_metrics"],
                "prompts": ["agent_selection", "task_breakdown"]
            },
            "utility": {
                "tools": ["run_command", "calculate", "process_data"],
                "resources": ["get_system_info", "get_server_metrics"],
                "prompts": ["command_helper", "data_processor"]
            }
        }
        
        # Get template based on project type, default to basic
        template = project_templates.get(project_type, project_templates["basic"])
        
        # Create project files
        project_files = {
            "server.py": f'''#!/usr/bin/env python3
"""
{project_name} MCP Server
Generated by Meta FastMCP Server
"""
import os
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
{chr(10).join([f"@mcp.tool{chr(10)}def {tool}():{chr(10)}    return {{\\\"message\\\": \\\"{tool.replace('_', ' ').title()} implementation\\\"}}{chr(10)}" for tool in template["tools"]])}

# Generated resources
{chr(10).join([f"@mcp.resource(\\\"http://{project_name.lower().replace(' ', '-')}.local/{resource}\\\"){chr(10)}def get_{resource}():{chr(10)}    return {{\\\"data\\\": \\\"Resource implementation for {resource}\\\"}}{chr(10)}" for resource in template["resources"]])}

# Generated prompts
{chr(10).join([f"@mcp.prompt(\\\"/{project_name.lower().replace(' ', '')}-{prompt}\\\"){chr(10)}def {prompt}_prompt():{chr(10)}    return \\\"\\\"\\\"Prompt for {project_name} {prompt}\\\"\\\"\\\"{chr(10)}" for prompt in template["prompts"]])}

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

- Tools: {", ".join(template["tools"])}
- Resources: {", ".join(template["resources"])}
- Prompts: {", ".join(template["prompts"])}

## Configuration

The server can be configured using environment variables:
- `FASTMCP_HOST`: Host to bind to (default: 127.0.0.1)
- `FASTMCP_PORT`: Port to bind to (default: 8000)
''',
            "requirements.txt": "fastmcp>=2.0.0\npydantic>=2.0.0\nanyio>=4.0.0\n",
            "Dockerfile": f'''# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \\
    PYTHONUNBUFFERED=1 \\
    FASTMCP_HOST=0.0.0.0 \\
    FASTMCP_PORT=8000

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \\
    && apt-get install -y --no-install-recommends \\
        build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "server.py"]
''',
            "docker-compose.yml": f'''version: '3.8'

services:
  {project_name.lower().replace(" ", "-")}:
    build: .
    ports:
      - "8000:8000"
    environment:
      - FASTMCP_HOST=0.0.0.0
      - FASTMCP_PORT=8000
    restart: unless-stopped
    volumes:
      - .:/app
      - /app/__pycache__
'''
        }
        
        # Add example files if requested
        if include_examples:
            project_files["examples/basic_usage.py"] = f'''#!/usr/bin/env python3
"""
Basic usage example for {project_name} MCP Server
"""
import asyncio
from fastmcp import Client

async def example_usage():
    # Connect to the MCP server
    async with Client("stdio") as client:  # Or use http transport
        # Example of calling tools, resources, prompts
        tools = await client.list_tools()
        print(f"Available tools: {[t.name for t in tools]}")
        
        resources = await client.list_resources()
        print(f"Available resources: {[r.name for r in resources]}")

if __name__ == "__main__":
    asyncio.run(example_usage())
'''
        
        # Add test files if requested
        if include_tests:
            project_files["tests/test_server.py"] = f'''#!/usr/bin/env python3
"""
Tests for {project_name} MCP Server
"""
import pytest
from fastmcp import FastMCP

def test_server_initialization():
    """Test that the server initializes correctly"""
    mcp = FastMCP(
        name="{project_name}",
        instructions="Provides {project_name.lower()} functionality",
        version="1.0.0"
    )
    assert mcp.name == "{project_name}"
    assert mcp.instructions == "Provides {project_name.lower()} functionality"
    assert mcp.version == "1.0.0"

def test_server_has_components():
    """Test that server has expected components"""
    # This would test actual server components
    pass

if __name__ == "__main__":
    test_server_initialization()
    test_server_has_components()
    print("All tests passed!")
'''
        
        # Add documentation if requested
        if include_docs:
            project_files["docs/README.md"] = f'''# {project_name} Documentation

This documents the {project_name} MCP Server.

## Architecture

The server is built with FastMCP and provides:
- Tools for specific operations
- Resources for data retrieval
- Prompts for AI interactions

## API Reference

### Tools
{chr(10).join([f"- `{tool}`: Functionality for {tool.replace('_', ' ')}" for tool in template["tools"]])}

### Resources
{chr(10).join([f"- `{resource}`: Data resource for {resource.replace('_', ' ')}" for resource in template["resources"]])}

### Prompts
{chr(10).join([f"- `{prompt}_prompt`: Prompt for {prompt.replace('_', ' ')} operations" for prompt in template["prompts"]])}
'''
        
        return {
            "project_name": project_name,
            "project_type": project_type,
            "features": features,
            "files": project_files
        }
    except Exception as e:
        logger.error(f"Error generating MCP project {project_name}: {str(e)}")
        raise


def _generate_mcp_with_template_impl(
    name: str,
    template_type: str,
    template_options: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Generate an MCP using a predefined template - core implementation
    """
    try:
        logger.info(f"Generating MCP with template: {template_type} for {name}")
        
        if template_options is None:
            template_options = {}
        
        # Define various templates for common MCP patterns
        templates = {
            "api-wrapper": {
                "description": "An MCP server that wraps an existing API",
                "instructions": f"Provides access to external services through the {name} API",
                "tools": ["call_api", "get_status", "list_endpoints"],
                "resources": ["get_api_schema", "get_rate_limits"],
                "prompts": ["api_query", "endpoint_suggestion"]
            },
            "file-processor": {
                "description": "An MCP server for processing files and documents",
                "instructions": f"Provides file processing capabilities for {name} documents",
                "tools": ["read_file", "write_file", "process_document"],
                "resources": ["get_file_stats", "get_supported_formats"],
                "prompts": ["document_query", "format_suggestion"]
            },
            "data-analyzer": {
                "description": "An MCP server for analyzing data",
                "instructions": f"Provides data analysis and visualization tools for {name} datasets",
                "tools": ["analyze_data", "generate_report", "filter_data"],
                "resources": ["get_data_schema", "get_analysis_stats"],
                "prompts": ["data_query", "visualization_suggestion"]
            },
            "task-orchestrator": {
                "description": "An MCP server for orchestrating tasks",
                "instructions": f"Manages and orchestrates tasks for {name} systems",
                "tools": ["create_task", "execute_task", "monitor_task"],
                "resources": ["get_task_queue", "get_system_metrics"],
                "prompts": ["task_breakdown", "workflow_suggestion"]
            }
        }
        
        template = templates.get(template_type)
        if not template:
            raise ValueError(f"Unknown template type: {template_type}. Available: {', '.join(templates.keys())}")
        
        # Generate server code using the template
        server_code = f'''#!/usr/bin/env python3
"""
{name} MCP Server
Template: {template_type}
Generated by Meta FastMCP Server
"""
import os
import asyncio
from fastmcp import FastMCP
from typing import List, Dict, Any

# Initialize the MCP server
mcp = FastMCP(
    name="{name}",
    instructions="{template["instructions"]}",
    version="1.0.0"
)

# Tools
{chr(10).join([f"@mcp.tool{chr(10)}def {tool}():{chr(10)}    return {{\\\"message\\\": \\\"{tool.replace('_', ' ').title()} implementation\\\"}}{chr(10)}" for tool in template["tools"]])}

# Resources
{chr(10).join([f"@mcp.resource(\\\"http://{name.lower().replace(' ', '-')}.local/{resource}\\\"){chr(10)}def get_{resource}():{chr(10)}    return {{\\\"data\\\": \\\"Resource implementation for {resource}\\\"}}{chr(10)}" for resource in template["resources"]])}

# Prompts
{chr(10).join([f"@mcp.prompt(\\\"/{name.lower().replace(' ', '')}-{prompt}\\\"){chr(10)}def {prompt}_prompt():{chr(10)}    return \\\"\\\"\\\"Prompt for {name} {prompt}\\\"\\\"\\\"{chr(10)}" for prompt in template["prompts"]])}

if __name__ == "__main__":
    # Use stdio transport for MCP server
    asyncio.run(mcp.run_stdio_async())
'''
        
        return {
            "name": name,
            "template_type": template_type,
            "description": template["description"],
            "server_code": server_code,
            "tools": template["tools"],
            "resources": template["resources"],
            "prompts": template["prompts"]
        }
    except Exception as e:
        logger.error(f"Error generating MCP with template {template_type}: {str(e)}")
        raise


def _deploy_mcp_impl(
    server_content: str,
    deployment_type: str = "local",
    config: Dict[str, Any] = None
) -> Dict[str, str]:
    """
    Deploy an MCP server to various environments - core implementation
    """
    try:
        logger.info(f"Deploying MCP server to {deployment_type}")
        
        if config is None:
            config = {}
        
        deployment_methods = {
            "local": f"Local deployment: Save server.py with content and run with 'python server.py'",
            "docker": f"Create Docker image with the server code",
            "kubernetes": f"Create Kubernetes deployment manifests",
            "cloud": f"Deploy to cloud platform (configuration needed)"
        }
        
        if deployment_type not in deployment_methods:
            raise ValueError(f"Unknown deployment type: {deployment_type}. Available: {', '.join(deployment_methods.keys())}")
        
        # Return deployment instructions
        instructions = deployment_methods[deployment_type]
        
        return {
            "deployment_type": deployment_type,
            "instructions": instructions,
            "status": "ready for deployment",
            "next_steps": [
                "Save the server code to a file (e.g., server.py)",
                "Install dependencies: pip install -r requirements.txt",
                f"Follow the {deployment_type} deployment instructions"
            ]
        }
    except Exception as e:
        logger.error(f"Error deploying MCP: {str(e)}")
        raise


def _test_mcp_impl(
    server_content: str,
    test_type: str = "basic",
    target_host: str = "localhost",
    target_port: int = 8000
) -> Dict[str, Any]:
    """
    Test an MCP server implementation - core implementation
    """
    try:
        logger.info(f"Testing MCP server at {target_host}:{target_port}")
        
        # Create test content based on the test type
        test_types = {
            "basic": "Basic functionality tests",
            "integration": "Integration tests with other systems",
            "performance": "Performance and load tests",
            "security": "Security and validation tests"
        }
        
        if test_type not in test_types:
            raise ValueError(f"Unknown test type: {test_type}. Available: {', '.join(test_types.keys())}")
        
        # Generate test code
        test_code = f'''#!/usr/bin/env python3
"""
Test suite for MCP Server
Test Type: {test_type}
"""
import asyncio
import pytest
from fastmcp import Client

async def test_mcp_connection():
    """Test basic connection to MCP server"""
    try:
        async with Client("stdio") as client:  # or http connection
            tools = await client.list_tools()
            resources = await client.list_resources()
            prompts = await client.list_prompts()
            
            print(f"Found {{len(tools)}} tools, {{len(resources)}} resources, {{len(prompts)}} prompts")
            return True
    except Exception as e:
        print(f"Connection test failed: {{e}}")
        return False

async def test_{test_type}_functionality():
    """Test {test_type} functionality"""
    # Implementation depends on actual server
    pass

if __name__ == "__main__":
    # Run tests
    asyncio.run(test_mcp_connection())
    print("Tests completed")
'''
        
        return {
            "test_type": test_type,
            "test_code": test_code,
            "description": test_types[test_type],
            "status": "test generated"
        }
    except Exception as e:
        logger.error(f"Error testing MCP: {str(e)}")
        raise


def _generate_mcp_documentation_impl(
    server_content: str,
    doc_type: str = "api",
    output_format: str = "markdown"
) -> Dict[str, str]:
    """
    Generate documentation for an MCP server - core implementation
    """
    try:
        logger.info(f"Generating {doc_type} documentation in {output_format} format")
        
        # Analyze the server content to extract tools, resources, and prompts
        import re
        
        tools = re.findall(r'@mcp\.tool\s+def\s+(\w+)', server_content)
        resources = re.findall(r'@mcp\.resource\([^)]+\)\s+def\s+(\w+)', server_content)
        prompts = re.findall(r'@mcp\.prompt\([^)]+\)\s+def\s+(\w+)', server_content)
        
        # Generate documentation based on the format
        if output_format == "markdown":
            doc_content = f"""# MCP Server Documentation

## Overview
This document provides information about the MCP server functionality.

## Tools
Tools are functions that perform actions.

{chr(10).join([f"- `{tool}`: Performs an action" for tool in tools])}

## Resources
Resources are functions that return data.

{chr(10).join([f"- `{resource}`: Provides data" for resource in resources])}

## Prompts
Prompts are functions that return AI prompt templates.

{chr(10).join([f"- `{prompt}`: AI prompt template" for prompt in prompts])}

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Run the server: `python server.py`
"""
        elif output_format == "json":
            doc_content = json.dumps({
                "tools": [{"name": tool, "description": "Performs an action"} for tool in tools],
                "resources": [{"name": resource, "description": "Provides data"} for resource in resources],
                "prompts": [{"name": prompt, "description": "AI prompt template"} for prompt in prompts]
            }, indent=2)
        else:
            doc_content = f"Documentation for tools: {', '.join(tools)}, resources: {', '.join(resources)}, prompts: {', '.join(prompts)}"
        
        return {
            "doc_type": doc_type,
            "output_format": output_format,
            "content": doc_content
        }
    except Exception as e:
        logger.error(f"Error generating documentation: {str(e)}")
        raise


# MCP Creation Tools for 100% Coverage

@mcp.tool
def generate_mcp_project(
    project_name: str,
    project_type: str = "basic", 
    features: List[str] = None,
    include_examples: bool = True,
    include_tests: bool = True,
    include_docs: bool = True
) -> Dict[str, Any]:
    """
    Generate a complete MCP project with specified features
    """
    return _generate_mcp_project_impl(
        project_name, project_type, features, 
        include_examples, include_tests, include_docs
    )


@mcp.tool
def generate_mcp_with_template(
    name: str,
    template_type: str,
    template_options: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Generate an MCP using a predefined template
    """
    return _generate_mcp_with_template_impl(name, template_type, template_options)


@mcp.tool
def deploy_mcp(
    server_content: str,
    deployment_type: str = "local",
    config: Dict[str, Any] = None
) -> Dict[str, str]:
    """
    Deploy an MCP server to various environments
    """
    return _deploy_mcp_impl(server_content, deployment_type, config)


@mcp.tool
def test_mcp(
    server_content: str,
    test_type: str = "basic",
    target_host: str = "localhost",
    target_port: int = 8000
) -> Dict[str, Any]:
    """
    Test an MCP server implementation
    """
    return _test_mcp_impl(server_content, test_type, target_host, target_port)


@mcp.tool
def generate_mcp_documentation(
    server_content: str,
    doc_type: str = "api",
    output_format: str = "markdown"
) -> Dict[str, str]:
    """
    Generate documentation for an MCP server
    """
    return _generate_mcp_documentation_impl(server_content, doc_type, output_format)


@mcp.resource("http://meta-fastmcp-server.local/mcp-templates")
def get_mcp_templates() -> Dict[str, Any]:
    """
    Get available MCP templates for project generation
    """
    return {
        "api-wrapper": {
            "description": "An MCP server that wraps an existing API",
            "use_case": "Connect to external services"
        },
        "file-processor": {
            "description": "An MCP server for processing files and documents",
            "use_case": "Handle file-based operations"
        },
        "data-analyzer": {
            "description": "An MCP server for analyzing data",
            "use_case": "Process and analyze datasets"
        },
        "task-orchestrator": {
            "description": "An MCP server for orchestrating tasks",
            "use_case": "Manage complex workflows"
        },
        "basic": {
            "description": "A basic MCP server with essential components",
            "use_case": "General purpose MCP"
        }
    }


@mcp.resource("http://meta-fastmcp-server.local/deployment-options")
def get_deployment_options() -> Dict[str, str]:
    """
    Get available deployment options for MCP servers
    """
    return {
        "local": "Run the MCP server locally on your machine",
        "docker": "Containerize the MCP server with Docker",
        "kubernetes": "Deploy to a Kubernetes cluster",
        "cloud": "Deploy to cloud platforms (AWS, GCP, Azure)"
    }


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
6. Add rate limiting if needed
7. Create comprehensive tests
8. Document your API

## Best Practices:

- Use descriptive names for tools, resources, and prompts
- Add proper type hints to all functions
- Implement comprehensive error handling
- Include validation for all inputs
- Use configuration management for flexibility
- Follow security best practices

## Common Patterns:

- Tools should perform actions and return results
- Resources should provide data access
- Prompts should return structured templates for AI

Implement this {project_type} MCP server following these guidelines.
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

## Dependencies
- [ ] Keep dependencies updated
- [ ] Use dependency scanning tools
- [ ] Minimize external dependencies

## Review the code for:
- Unrestricted file access
- Command injection possibilities  
- Information disclosure
- Resource exhaustion

Server content review: {server_content[:200]}...
"""


def _create_mcp_config_impl(
    config_type: str = "basic",
    settings: Dict[str, Any] = None
) -> Dict[str, str]:
    """
    Create configuration files for MCP servers - core implementation
    """
    try:
        logger.info(f"Creating {config_type} configuration")
        
        if settings is None:
            settings = {}
        
        # Different types of configuration files
        config_templates = {
            "basic": {
                "file": "config.json",
                "content": json.dumps({
                    "name": settings.get("name", "New MCP Server"),
                    "version": settings.get("version", "1.0.0"),
                    "instructions": settings.get("instructions", "A new MCP server"),
                    "host": settings.get("host", "127.0.0.1"),
                    "port": settings.get("port", 8000),
                    "log_level": settings.get("log_level", "INFO")
                }, indent=2)
            },
            "advanced": {
                "file": "advanced_config.json",
                "content": json.dumps({
                    "name": settings.get("name", "New MCP Server"),
                    "version": settings.get("version", "1.0.0"),
                    "instructions": settings.get("instructions", "A new MCP server"),
                    "host": settings.get("host", "127.0.0.1"),
                    "port": settings.get("port", 8000),
                    "log_level": settings.get("log_level", "INFO"),
                    "cache": {
                        "max_size": settings.get("cache_max_size", 100),
                        "ttl": settings.get("cache_ttl", 300)
                    },
                    "rate_limiting": {
                        "max_requests": settings.get("rate_limit_max_requests", 100),
                        "window_seconds": settings.get("rate_limit_window", 3600)
                    },
                    "security": {
                        "allow_directory_traversal": settings.get("allow_directory_traversal", False)
                    }
                }, indent=2)
            },
            "env": {
                "file": ".env",
                "content": f"""# MCP Server Configuration
FASTMCP_SERVER_NAME={settings.get('name', 'New MCP Server')}
FASTMCP_VERSION={settings.get('version', '1.0.0')}
FASTMCP_INSTRUCTIONS={settings.get('instructions', 'A new MCP server')}
FASTMCP_HOST={settings.get('host', '127.0.0.1')}
FASTMCP_PORT={settings.get('port', 8000)}
FASTMCP_LOG_LEVEL={settings.get('log_level', 'INFO')}
CACHE_MAX_SIZE={settings.get('cache_max_size', 100)}
CACHE_TTL={settings.get('cache_ttl', 300)}
RATE_LIMIT_MAX_REQUESTS={settings.get('rate_limit_max_requests', 100)}
RATE_LIMIT_WINDOW={settings.get('rate_limit_window', 3600)}
ALLOW_DIRECTORY_TRAVERSAL={settings.get('allow_directory_traversal', False)}
"""
            }
        }
        
        template = config_templates.get(config_type)
        if not template:
            raise ValueError(f"Unknown config type: {config_type}. Available: {', '.join(config_templates.keys())}")
        
        return {
            "file_name": template["file"],
            "content": template["content"],
            "config_type": config_type
        }
    except Exception as e:
        logger.error(f"Error creating MCP configuration: {str(e)}")
        raise


def _migrate_mcp_impl(
    old_server_content: str,
    target_version: str = "latest"
) -> Dict[str, str]:
    """
    Migrate an existing MCP server to a newer version or structure - core implementation
    """
    try:
        logger.info(f"Migrating MCP server to version {target_version}")
        
        # In a real implementation, this would handle actual migration
        # For now, we'll provide migration guidance
        migration_guide = f"""
# MCP Migration Guide

Migrating to version {target_version}

## Changes to Implement

1. Update FastMCP version in requirements.txt
2. Review deprecated decorators or functions
3. Update configuration format if needed
4. Test all tools, resources, and prompts

## Migration Steps

1. Backup current server
2. Update dependencies
3. Apply code changes
4. Test thoroughly
5. Deploy to staging
6. Deploy to production

## Diff Analysis
Based on your code, the following will need attention:
- Import statements
- Decorator usage
- Configuration setup
- Error handling patterns
"""
        
        return {
            "status": "migration guide generated",
            "guide": migration_guide,
            "target_version": target_version
        }
    except Exception as e:
        logger.error(f"Error migrating MCP: {str(e)}")
        raise


def _integrate_mcp_impl(
    primary_server: str,
    secondary_server: str,
    integration_type: str = "simple"
) -> Dict[str, str]:
    """
    Integrate two MCP servers - core implementation
    """
    try:
        logger.info(f"Integrating servers with {integration_type} approach")
        
        integration_guide = f"""
# MCP Server Integration Guide

Integrating:
- Primary: {primary_server[:50]}...
- Secondary: {secondary_server[:50]}...

## Approaches

### Simple Integration
Direct communication between servers

### Orchestrated Integration  
Use a third server to coordinate

### Event-Based Integration
Use event pub/sub pattern

## Implementation
1. Define interaction patterns
2. Handle error propagation
3. Implement circuit breakers
4. Add monitoring and logging

## Generated Integration Code
# This would contain the actual integration code
# based on the specific servers and integration type
"""
        
        return {
            "status": "integration guide generated",
            "guide": integration_guide,
            "integration_type": integration_type
        }
    except Exception as e:
        logger.error(f"Error integrating MCPs: {str(e)}")
        raise


@mcp.tool
def create_mcp_config(
    config_type: str = "basic",
    settings: Dict[str, Any] = None
) -> Dict[str, str]:
    """
    Create configuration files for MCP servers
    """
    return _create_mcp_config_impl(config_type, settings)


@mcp.tool
def migrate_mcp(
    old_server_content: str,
    target_version: str = "latest"
) -> Dict[str, str]:
    """
    Migrate an existing MCP server to a newer version or structure
    """
    return _migrate_mcp_impl(old_server_content, target_version)


@mcp.tool
def integrate_mcp(
    primary_server: str,
    secondary_server: str,
    integration_type: str = "simple"
) -> Dict[str, str]:
    """
    Integrate two MCP servers
    """
    return _integrate_mcp_impl(primary_server, secondary_server, integration_type)


@mcp.resource("http://meta-fastmcp-server.local/config-templates")
def get_config_templates() -> Dict[str, Any]:
    """
    Get available configuration templates
    """
    return {
        "basic": {
            "description": "Basic configuration with essential settings",
            "file": "config.json"
        },
        "advanced": {
            "description": "Advanced configuration with caching, rate limiting, etc.",
            "file": "advanced_config.json" 
        },
        "env": {
            "description": "Environment variable configuration",
            "file": ".env"
        }
    }


@mcp.prompt("/mcp-deployment-strategy")
def mcp_deployment_strategy(
    server_type: str,
    scale_requirements: str = "small"
) -> str:
    """
    Generate a deployment strategy for an MCP server
    """
    return f"""
# Deployment Strategy for {server_type} MCP

Scale Requirements: {scale_requirements}

## Recommended Architecture

### Small Scale
- Single instance deployment
- Basic monitoring
- Simple backup strategy

### Medium Scale
- Load balancing across multiple instances
- Auto-scaling based on demand
- Comprehensive monitoring

### Large Scale
- Container orchestration (Kubernetes)
- Multi-region deployment
- Advanced security measures
- Disaster recovery plan

## Deployment Steps

1. Prepare infrastructure
2. Set up monitoring and logging
3. Deploy initial version
4. Test functionality
5. Scale as needed
6. Monitor performance

## Considerations
- Security hardening
- Backup and recovery
- Performance optimization
- Cost management
"""


def get_cache_stats():
    """Get cache statistics for admin purposes"""
    return {
        "cache_size": len(doc_cache.cache),
        "cache_keys": list(doc_cache.cache.keys()),
        "max_size": doc_cache.max_size,
        "ttl_seconds": doc_cache.ttl
    }


if __name__ == "__main__":
    # Update logging level based on config
    logging.getLogger().setLevel(config.log_level)
    
    # Use stdio transport for MCP server (proper MCP protocol communication)
    import asyncio
    asyncio.run(mcp.run_stdio_async())