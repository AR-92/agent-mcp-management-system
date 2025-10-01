#!/usr/bin/env python3
"""
Simple client to test the FastMCP Documentation Server
"""

import asyncio
from fastmcp import Client


async def test_server():
    """
    Test the FastMCP Documentation Server by connecting to it and calling some functions
    NOTE: This requires the server to be running on http://127.0.0.1:8001
    """
    try:
        # Connect to the server (this assumes the server is running)
        async with Client("http://127.0.0.1:8001") as client:
            print("Connected to FastMCP Documentation Server successfully!")
            
            # Test getting documentation TOC (resource)
            try:
                toc = await client.read_resource("get_documentation_toc")
                print(f"Documentation TOC retrieved. Sections count: {len(toc.get('sections', {}))}")
            except Exception as e:
                print(f"Could not read TOC resource: {e}")
            
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
                
            # Test searching documentation
            try:
                result = await client.call_tool(
                    name="search_documentation",
                    arguments={"query": "FastMCP"}
                )
                print(f"Search results count: {len(result)}")
                if result:
                    print(f"  First result: {result[0]['file']}")
            except Exception as e:
                print(f"Could not search documentation: {e}")
                
    except Exception as e:
        print(f"Could not connect to server (expected if server not running): {e}")
        print("To test fully, start the server with: python server.py")


if __name__ == "__main__":
    print("Testing FastMCP Documentation Server connection...")
    asyncio.run(test_server())