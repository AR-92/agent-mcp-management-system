#!/usr/bin/env python3
"""
Dokploy OpenAPI MCP Server

This server automatically generates MCP tools from the Dokploy OpenAPI specification,
allowing LLMs to manage applications, databases, projects, and infrastructure on Dokploy.
"""

import os
import httpx
from fastmcp import FastMCP
from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import logging

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnvironmentConfig:
    """Configuration class for environment variables."""
    
    @staticmethod
    def get_api_key() -> str:
        """Get the Dokploy API key from environment."""
        api_key = os.getenv("DOKPLOY_API_KEY")
        if not api_key:
            raise ValueError(
                "DOKPLOY_API_KEY environment variable is required. "
                "Please set it in your .env file or environment. "
                "Example: DOKPLOY_API_KEY=your_actual_api_key_here"
            )
        return api_key

    @staticmethod
    def get_api_url() -> str:
        """Get the Dokploy API URL from environment."""
        return os.getenv("DOKPLOY_API_URL", "https://dokploy.flowchat.info/api")

    @staticmethod
    def get_server_name() -> str:
        """Get the server name from environment."""
        return os.getenv("DOKPLOY_SERVER_NAME", "Dokploy MCP Server")

    @staticmethod 
    def get_server_description() -> str:
        """Get the server description from environment."""
        return os.getenv("DOKPLOY_SERVER_DESCRIPTION", "Provides access to Dokploy functionality for LLMs through MCP protocol")

    @staticmethod
    def get_request_timeout() -> float:
        """Get the request timeout from environment."""
        try:
            return float(os.getenv("DOKPLOY_REQUEST_TIMEOUT", "30.0"))
        except ValueError:
            logger.warning("Invalid DOKPLOY_REQUEST_TIMEOUT value, using default 30.0 seconds")
            return 30.0

def load_openapi_spec() -> Dict[str, Any]:
    """Load the Dokploy OpenAPI specification from file."""
    openapi_spec_path = Path(__file__).parent.parent / "OpenApi" / "dokploy.json"
    
    if not openapi_spec_path.exists():
        raise FileNotFoundError(
            f"OpenAPI specification not found at {openapi_spec_path}. "
            f"Please ensure the file exists and is accessible."
        )
    
    try:
        with open(openapi_spec_path, 'r', encoding='utf-8') as f:
            spec = json.load(f)
        
        # Basic validation of the OpenAPI spec
        if not spec.get("openapi") and not spec.get("swagger"):
            raise ValueError("File does not appear to be a valid OpenAPI specification")
            
        return spec
    except json.JSONDecodeError as e:
        raise ValueError(f"OpenAPI specification file is not valid JSON: {e}")
    except Exception as e:
        raise Exception(f"Error reading OpenAPI specification: {e}")

def create_http_client() -> httpx.AsyncClient:
    """Create an HTTP client with proper authentication headers."""
    api_key = EnvironmentConfig.get_api_key()
    api_url = EnvironmentConfig.get_api_url()
    timeout = EnvironmentConfig.get_request_timeout()
    
    logger.info(f"Creating HTTP client for API: {api_url}")
    
    return httpx.AsyncClient(
        base_url=api_url,
        headers={
            "x-api-key": api_key,
            "Content-Type": "application/json"
        },
        timeout=timeout
    )

# Create the MCP server from the OpenAPI specification
def create_dokploy_mcp_server():
    """Create the Dokploy MCP server using FastMCP's from_openapi functionality."""
    try:
        # Load the OpenAPI spec
        spec = load_openapi_spec()
        
        # Create HTTP client with authentication
        client = create_http_client()
        
        # Create MCP server from OpenAPI spec
        mcp = FastMCP.from_openapi(
            openapi_spec=spec,
            client=client,
            name=EnvironmentConfig.get_server_name(),
            instructions=EnvironmentConfig.get_server_description(),
            # Add custom route mappings to exclude sensitive endpoints
            route_maps=[
                # Exclude admin endpoints
                RouteMap(pattern=r"^/admin/.*", mcp_type=MCPType.EXCLUDE),
                # Exclude internal endpoints if they exist
                RouteMap(tags={"internal"}, mcp_type=MCPType.EXCLUDE),
            ],
            # Add global tags
            tags={"dokploy", "infrastructure", "deployment"},
        )
        
        logger.info("Successfully created Dokploy MCP server from OpenAPI specification")
        return mcp
    except Exception as e:
        logger.error(f"Error creating Dokploy MCP server: {e}")
        raise

# Import route mapping components - do this at the top level
from fastmcp.server.openapi import RouteMap, MCPType

# Create the main MCP server
mcp = create_dokploy_mcp_server()

# Add utility tools that aren't in the OpenAPI spec
@mcp.tool
async def get_available_endpoints() -> List[Dict[str, str]]:
    """
    Get a list of all available endpoints from the Dokploy OpenAPI specification.
    """
    spec = load_openapi_spec()
    paths = spec.get("paths", {})
    endpoints = []
    
    for path, path_item in paths.items():
        for method, operation in path_item.items():
            if method not in ["parameters"]:
                endpoints.append({
                    "path": path,
                    "method": method.upper(),
                    "operationId": operation.get("operationId", f"{method}_{path}"),
                    "summary": operation.get("summary", "No description provided")
                })
    
    return endpoints

@mcp.tool
async def get_api_info() -> Dict[str, Any]:
    """
    Get information about the connected Dokploy API.
    """
    spec = load_openapi_spec()
    info = spec.get("info", {})
    
    return {
        "title": info.get("title", "Dokploy API"),
        "description": info.get("description", "Dokploy API for infrastructure management"),
        "version": info.get("version", "unknown"),
        "server_url": EnvironmentConfig.get_api_url()
    }

# Shutdown handler - need to register it properly
async def cleanup():
    """Clean up resources on server shutdown."""
    logger.info("Shutting down Dokploy MCP Server...")
    # Note: We don't have direct access to the HTTP client here
    # It's managed internally by the FastMCP OpenAPI server
    logger.info("Dokploy MCP Server shutdown complete")

# Register cleanup function if the method exists
if hasattr(mcp, 'on_shutdown'):
    mcp.on_shutdown(cleanup)

if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Run the MCP server using stdio transport
        await mcp.run_stdio_async()
    
    # Use run() instead of run_until_complete() for newer Python versions
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Error running MCP server: {e}")
        raise