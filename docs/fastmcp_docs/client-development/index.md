# Client Development

This section covers how to interact with Model Context Protocol (MCP) servers using FastMCP's client libraries. Learn how to discover, connect to, and interact with MCP servers from your applications.

## Creating an MCP Client

The FastMCP client provides a simple interface for interacting with MCP servers:

```python
from fastmcp import Client

# Connect to an MCP server
async with Client("https://example.com/mcp") as client:
    # Use the client to call tools, fetch resources, etc.
    result = await client.call_tool(name="add", arguments={"a": 5, "b": 3})
    print(result)  # Output: 8
```

## Core Client Operations

### Calling Tools

Tools are functions on the server that perform actions. You can call them with arguments:

```python
import asyncio
from fastmcp import Client

async def call_server_tool():
    async with Client("https://example.com/mcp") as client:
        # Call a tool with arguments
        result = await client.call_tool(
            name="create_user",
            arguments={
                "name": "John Doe",
                "email": "john@example.com"
            }
        )
        return result

# Run the async function
asyncio.run(call_server_tool())
```

### Fetching Resources

Resources provide data to your application. Fetch them by name and optional parameters:

```python
async def fetch_resource():
    async with Client("https://example.com/mcp") as client:
        # Fetch a resource
        user_data = await client.read_resource(
            resource="user-info",
            parameters={"user_id": "12345"}
        )
        return user_data

asyncio.run(fetch_resource())
```

### Using Prompts

Prompts define reusable templates for LLM interactions:

```python
async def use_prompt():
    async with Client("https://example.com/mcp") as client:
        # Use a prompt template
        prompt_result = await client.get_prompt(
            name="generate_summary",
            arguments={"text": "This is a long document to summarize"}
        )
        return prompt_result

asyncio.run(use_prompt())
```

## Client Configuration

Configure the client for different scenarios:

```python
from fastmcp import Client
from fastmcp.config import ClientConfig

# Custom configuration
config = ClientConfig(
    timeout=30,  # 30 second timeout
    retries=3,   # Retry up to 3 times
    headers={"Authorization": "Bearer your-token-here"}
)

async with Client("https://example.com/mcp", config=config) as client:
    # Use configured client
    result = await client.call_tool(name="example", arguments={})
```

## Authentication

Secure clients with various authentication methods:

```python
from fastmcp import Client

# Bearer token authentication
async with Client(
    "https://example.com/mcp",
    headers={"Authorization": "Bearer your-token"}
) as client:
    result = await client.call_tool(name="secure_operation")
```

## Advanced Client Features

### Batch Operations

Execute multiple operations efficiently:

```python
async def batch_operations():
    async with Client("https://example.com/mcp") as client:
        # Call multiple tools in a batch
        results = await client.batch_call_tools([
            {"name": "add", "arguments": {"a": 1, "b": 2}},
            {"name": "multiply", "arguments": {"x": 3, "y": 4}}
        ])
        return results

asyncio.run(batch_operations())
```

### Streaming Responses

For large responses, use streaming:

```python
async def stream_response():
    async with Client("https://example.com/mcp") as client:
        async for chunk in client.stream_tool(
            name="long_running_operation",
            arguments={"data": "large dataset"}
        ):
            print(f"Received chunk: {chunk}")

asyncio.run(stream_response())
```

## Error Handling

Handle errors gracefully with proper exception handling:

```python
import asyncio
from fastmcp import Client
from fastmcp.errors import ToolCallError, ResourceNotFoundError

async def safe_client_operations():
    try:
        async with Client("https://example.com/mcp") as client:
            result = await client.call_tool(name="risky_operation")
            return result
    except ToolCallError as e:
        print(f"Tool call failed: {e}")
        return None
    except ResourceNotFoundError as e:
        print(f"Resource not found: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

asyncio.run(safe_client_operations())
```

## Discovery and Service Introspection

Discover available tools and resources on a server:

```python
async def discover_server_capabilities():
    async with Client("https://example.com/mcp") as client:
        # Get server info
        server_info = await client.get_server_info()
        print(f"Server: {server_info.name}")
        
        # List available tools
        tools = await client.list_tools()
        print(f"Available tools: {[t.name for t in tools]}")
        
        # List available resources
        resources = await client.list_resources()
        print(f"Available resources: {[r.name for r in resources]}")

asyncio.run(discover_server_capabilities())
```

## Testing with Clients

Test client code without external dependencies:

```python
import pytest
from fastmcp import Client
from fastmcp.testing import MockServer

@pytest.mark.asyncio
async def test_client_operations():
    # Use a mock server for testing
    async with MockServer() as mock_server:
        async with Client(mock_server.url) as client:
            # Test client operations with mock server
            result = await client.call_tool(
                name="add", 
                arguments={"a": 5, "b": 7}
            )
            assert result == 12
```

## Best Practices

### Connection Management
- Always use async context managers (`async with`) for proper connection handling
- Reuse clients when possible to benefit from connection pooling
- Handle connection errors gracefully

### Error Handling
- Implement retry logic for transient failures
- Distinguish between client errors and server errors
- Log errors appropriately for debugging

### Security
- Always use HTTPS for production
- Implement proper authentication
- Validate and sanitize all inputs

## Next Steps

1. [Client Configuration](./configuration.md) - Detailed client configuration options
2. [Authentication](./authentication.md) - Securing client-server communication
3. [Testing](./testing.md) - Comprehensive testing strategies for clients
4. [Performance](./performance.md) - Optimizing client performance