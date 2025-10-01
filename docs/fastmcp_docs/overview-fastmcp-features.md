# FastMCP Features

FastMCP provides a comprehensive set of features for building production-ready Model Context Protocol applications.

## Core Features

### Fast, Pythonic Interface
FastMCP provides a clean, intuitive API that feels natural to Python developers:

```python
from fastmcp import FastMCP

mcp = FastMCP("My Server")

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b
```

### Rich Type Support
Leverages Python type hints for automatic schema generation and validation:

```python
from typing import List, Optional
from pydantic import BaseModel

class Person(BaseModel):
    name: str
    age: int

@mcp.tool
def greet_people(people: List[Person], greeting: str = "Hello") -> str:
    """Greet a list of people"""
    names = ", ".join([p.name for p in people])
    return f"{greeting}, {names}!"
```

## Server Features

### Advanced MCP Patterns
- **Server Composition**: Combine multiple FastMCP servers into a single application
- **Proxy Servers**: Use FastMCP to act as an intermediary for other MCP servers
- **Tool Transformation**: Create enhanced tool variants with modified schemas

### Authentication & Authorization
- **Enterprise Auth**: Integration with Google, GitHub, Azure, Auth0, WorkOS, and other providers
- **Bearer Token Authentication**: Simple token-based authentication
- **OAuth 2.1**: Full OAuth implementation for secure access

### Middleware Support
Add cross-cutting functionality to your MCP server with middleware:

```python
@mcp.middleware
def logging_middleware(request, call_next):
    print(f"Processing request: {request}")
    response = call_next(request)
    print(f"Response: {response}")
    return response
```

### Advanced Operations
- **User Elicitation**: Request structured input from users during tool execution
- **Server Logging**: Send log messages back to MCP clients
- **Progress Reporting**: Update clients on long-running operations
- **LLM Sampling**: Request client's LLM to generate text based on messages

## Client Features

### Comprehensive Client Libraries
- **Typed Client**: Programmatic client with type safety
- **Multiple Transports**: Support for various communication protocols
- **Error Handling**: Robust error management
- **Async Support**: Full async/await support

### Client Operations
- **Tool Operations**: Discover and execute server-side tools
- **Resource Operations**: Access static and templated resources
- **Prompt Operations**: Use server-side prompt templates
- **Message Handling**: Process MCP messages and notifications

## Deployment Features

### Multiple Deployment Options
- **Local Development**: Easy local server running
- **FastMCP Cloud**: Hosted solution for quick deployments
- **Self-Hosted**: Deploy to your own infrastructure
- **Container Support**: Docker and container orchestration ready

### Production Ready
- **Testing Frameworks**: Built-in tools for testing MCP applications
- **Configuration Management**: Declarative project configuration
- **Monitoring**: Built-in logging and metrics
- **Security**: Production security best practices built-in

## Integration Features

### Authentication Providers
- Google OAuth
- GitHub OAuth
- Azure (Microsoft Entra)
- Auth0
- WorkOS
- And more

### AI Assistant Integration
- Claude Desktop/Code
- ChatGPT
- Cursor
- And more

### Framework Integration
- FastAPI integration
- OpenAPI generation
- ASGI/Starlette compatibility

## Advanced Features

### MCP Context
Access MCP capabilities like logging, progress, and resources within your MCP objects:

```python
@mcp.tool
def long_running_task(context):
    """A tool that reports progress"""
    for i in range(10):
        context.progress(i, 10, f"Step {i+1}/10")
        # Do work
    return "Complete"
```

### CLI Tools
Built-in command line interface for common operations:

```bash
fastmcp run my_server:app
fastmcp install claude my-server
```