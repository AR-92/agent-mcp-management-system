#!/usr/bin/env python3
"""
Twenty CRM MCP Server

Provides access to Twenty CRM functionality for LLMs through MCP protocol.
Generated from Twenty CRM OpenAPI specification.
"""

import httpx
from fastmcp import FastMCP
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API configuration from environment
API_KEY = os.getenv("TWENTY_CRM_API_KEY")
API_BASE_URL = os.getenv("TWENTY_CRM_API_BASE_URL", "https://api.twenty.com")

# Verify API key exists
if not API_KEY:
    raise ValueError("TWENTY_CRM_API_KEY environment variable is required")

# Create an HTTP client for the API
client = httpx.AsyncClient(
    base_url=API_BASE_URL,
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
)

# Load the OpenAPI spec from the local file
import json
from pathlib import Path

# Get the project root directory (two levels up from mcps directory)
project_root = Path(__file__).parent.parent
openapi_file = project_root / "OpenApi" / "twenty.json"

with open(openapi_file, 'r') as f:
    openapi_spec = json.load(f)

# Create the MCP server from the OpenAPI spec
mcp = FastMCP.from_openapi(
    openapi_spec=openapi_spec,
    client=client,
    name="Twenty CRM Server",
    instructions="Provides access to Twenty CRM functionality including contact management, lead tracking, and sales operations. Use this server to interact with contacts, companies, opportunities, and other CRM entities."
)

if __name__ == "__main__":
    import asyncio
    # Use stdio transport for MCP server (proper MCP protocol communication)
    asyncio.run(mcp.run_stdio_async())