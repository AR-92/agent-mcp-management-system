#!/usr/bin/env python3
"""
Simple client to test the Meta FastMCP Server
"""

import asyncio
from fastmcp import Client


async def test_server():
    """
    Test the Meta FastMCP Server by connecting to it and calling some functions
    NOTE: This requires the server to be running on http://127.0.0.1:8000
    """
    try:
        # Connect to the server (this assumes the server is running)
        async with Client("http://127.0.0.1:8000") as client:
            print("Connected to server successfully!")
            
            # Test getting server info (resource)
            try:
                server_info = await client.read_resource("get_server_info")
                print(f"Server info: {server_info}")
            except Exception as e:
                print(f"Could not read server info resource: {e}")
            
            # Test listing tools
            try:
                tools = await client.list_tools()
                print(f"Available tools count: {len(tools)}")
                for tool in tools[:3]:  # Show first 3 tools
                    print(f"  - {tool.name}")
            except Exception as e:
                print(f"Could not list tools: {e}")
                
            # Test listing resources  
            try:
                resources = await client.list_resources()
                print(f"Available resources count: {len(resources)}")
                for resource in resources[:3]:  # Show first 3 resources
                    print(f"  - {resource.name}")
            except Exception as e:
                print(f"Could not list resources: {e}")
                
    except Exception as e:
        print(f"Could not connect to server (expected if server not running): {e}")
        print("To test fully, start the server with: python server.py")


if __name__ == "__main__":
    print("Testing Meta FastMCP Server connection...")
    asyncio.run(test_server())