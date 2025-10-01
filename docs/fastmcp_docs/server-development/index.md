# Server Development

This section covers everything you need to know about creating Model Context Protocol (MCP) servers with FastMCP. Learn how to build, configure, and manage MCP servers that expose data and functionality to LLM applications in a secure, standardized way.

## Creating Your First Server

FastMCP provides a clean, Pythonic interface for creating MCP servers. The simplest server requires just a few lines of code:

```python
from fastmcp import FastMCP

# Create an MCP server instance
mcp = FastMCP("Demo Server 🚀")

# Define a simple tool
@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b

if __name__ == "__main__":
    # Run the server
    mcp.run()
```

## Core Server Components

MCP servers are built around three core components:

### Tools
Tools are functions that perform actions and execute code. Think of them as POST endpoints that produce side effects.

```python
@mcp.tool
def send_email(recipient: str, subject: str, body: str) -> bool:
    """Send an email to the recipient"""
    # Implementation here
    return True
```

### Resources  
Resources provide data to LLMs. Think of them as GET endpoints that load information into the LLM's context.

```python
@mcp.resource
def get_user_info(user_id: str) -> dict:
    """Get information about a user"""
    # Implementation here
    return {"user_id": user_id, "name": "John Doe"}
```

### Prompts
Prompts define reusable templates for LLM interactions.

```python
@mcp.prompt
def generate_summary(text: str) -> str:
    """Generate a summary of the provided text"""
    return f"Please summarize the following text: {text}"
```

## Advanced Server Features

### Server Composition
FastMCP allows you to compose multiple servers together:

```python
from fastmcp import FastMCP

# Create multiple servers
data_server = FastMCP("Data Server")
tool_server = FastMCP("Tool Server")

# Compose them into a single server
composed_server = FastMCP.compose(data_server, tool_server)
```

### OpenAPI/FastAPI Generation
FastMCP can generate OpenAPI specifications and FastAPI applications from your MCP definitions.

### Tool Transformation
Transform tools to modify their behavior, inputs, or outputs:

```python
from fastmcp.transform import retry

@mcp.tool
@retry(max_attempts=3)
def unreliable_tool() -> str:
    """A tool that might fail occasionally"""
    # Implementation that might fail
    pass
```

## Configuration and Settings

Servers can be configured with various settings:

```python
from fastmcp import FastMCP

# Configure server with custom settings
mcp = FastMCP(
    name="My Production Server",
    description="Handles user data and operations",
    version="1.0.0",
    debug=False
)
```

## Error Handling

FastMCP provides robust error handling capabilities:

```python
from fastmcp.errors import McpError

@mcp.tool
def risky_operation(value: int) -> str:
    """Perform an operation that might fail"""
    if value < 0:
        raise McpError("Value must be non-negative")
    return f"Processed: {value}"
```

## Logging and Monitoring

Enable logging to track server activity:

```python
import logging
from fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
mcp = FastMCP("Monitored Server")

@mcp.tool
def logged_operation(data: str) -> str:
    """Operation with logging"""
    logging.info(f"Processing data: {data}")
    return f"Processed: {data}"
```

## Next Steps

1. [Server Configuration](./configuration.md) - Learn about advanced server setups
2. [Authentication](./authentication.md) - Secure your servers with authentication
3. [Testing](./testing.md) - Test your MCP servers effectively
4. [Performance](./performance.md) - Optimize server performance