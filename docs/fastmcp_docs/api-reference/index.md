# API Reference

This section provides comprehensive documentation for the FastMCP API, including all classes, methods, and functions available in the framework.

## FastMCP Class

The main entry point for creating MCP servers.

### `FastMCP(name: str, description: str = "", version: str = "1.0.0", debug: bool = False)`

Creates a new FastMCP server instance.

**Parameters:**
- `name` (str): The name of the server
- `description` (str): Optional description of the server
- `version` (str): Version string for the server
- `debug` (bool): Enable debug mode for additional logging

**Example:**
```python
from fastmcp import FastMCP

mcp = FastMCP(
    name="My Server",
    description="Handles various operations",
    version="1.0.0",
    debug=True
)
```

### Methods

#### `mcp.tool(func) -> Callable`
Decorator to register a function as an MCP tool.

```python
@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b
```

**Parameters:**
- `func` (Callable): The function to register as a tool

**Returns:**
- The original function, now registered as an MCP tool

#### `mcp.resource(func) -> Callable`
Decorator to register a function as an MCP resource.

```python
@mcp.resource
def current_time() -> str:
    """Get the current time"""
    import datetime
    return str(datetime.datetime.now())
```

**Parameters:**
- `func` (Callable): The function to register as a resource

**Returns:**
- The original function, now registered as an MCP resource

#### `mcp.prompt(func) -> Callable`
Decorator to register a function as an MCP prompt.

```python
@mcp.prompt
def greeting_template(name: str) -> str:
    """Generate a greeting prompt"""
    return f"Please greet the user named {name}"
```

**Parameters:**
- `func` (Callable): The function to register as a prompt

**Returns:**
- The original function, now registered as an MCP prompt

#### `mcp.run(host: str = "127.0.0.1", port: int = 8000, **kwargs)`
Start the MCP server.

**Parameters:**
- `host` (str): Host address to bind to (default: "127.0.0.1")
- `port` (int): Port to listen on (default: 8000)
- `**kwargs`: Additional server configuration options

**Example:**
```python
if __name__ == "__main__":
    mcp.run(host="0.0.0.0", port=8000)
```

#### `FastMCP.compose(*servers: FastMCP) -> FastMCP`
Compose multiple servers into a single server.

**Parameters:**
- `*servers` (FastMCP): Multiple FastMCP server instances to compose

**Returns:**
- A new FastMCP instance that combines all input servers

#### `mcp.middleware(func) -> Callable`
Decorator to register a middleware function.

```python
@mcp.middleware
def logging_middleware(request, call_next):
    print(f"Processing request: {request}")
    response = call_next(request)
    print(f"Response: {response}")
    return response
```

**Parameters:**
- `func` (Callable): The middleware function to register

**Returns:**
- The original function, now registered as middleware

#### `mcp.on_startup(func) -> Callable`
Decorator to register a startup handler function.

```python
@mcp.on_startup
async def startup_handler():
    print("Server is starting up...")
    # Initialize resources
```

**Parameters:**
- `func` (Callable): The startup handler function to register

**Returns:**
- The original function, now registered as a startup handler

#### `mcp.on_shutdown(func) -> Callable`
Decorator to register a shutdown handler function.

```python
@mcp.on_shutdown
async def shutdown_handler():
    print("Server is shutting down...")
    # Cleanup resources
```

**Parameters:**
- `func` (Callable): The shutdown handler function to register

**Returns:**
- The original function, now registered as a shutdown handler

## Client Class

The Client class provides methods to interact with MCP servers.

### `Client(server_url: str, config: Optional[ClientConfig] = None)`

Creates a new Client instance for interacting with an MCP server.

**Parameters:**
- `server_url` (str): The URL of the MCP server to connect to
- `config` (Optional[ClientConfig]): Optional client configuration

**Example:**
```python
from fastmcp import Client

async with Client("https://example.com/mcp") as client:
    result = await client.call_tool(name="add", arguments={"a": 5, "b": 3})
```

### Methods

#### `client.call_tool(name: str, arguments: dict) -> Any`
Call a tool on the MCP server.

**Parameters:**
- `name` (str): Name of the tool to call
- `arguments` (dict): Arguments to pass to the tool

**Returns:**
- The result of the tool call

#### `client.read_resource(name: str, parameters: Optional[dict] = None) -> Any`
Read a resource from the MCP server.

**Parameters:**
- `name` (str): Name of the resource to read
- `parameters` (Optional[dict]): Optional parameters for the resource

**Returns:**
- The resource data

#### `client.get_prompt(name: str, arguments: Optional[dict] = None) -> str`
Get a prompt template from the MCP server.

**Parameters:**
- `name` (str): Name of the prompt to get
- `arguments` (Optional[dict]): Optional arguments to substitute in the prompt

**Returns:**
- The prompt template with substituted arguments

#### `client.get_server_info() -> dict`
Get information about the connected MCP server.

**Returns:**
- Dictionary containing server information

#### `client.list_tools() -> list`
List all available tools on the server.

**Returns:**
- List of available tools

#### `client.list_resources() -> list`
List all available resources on the server.

**Returns:**
- List of available resources

## Configuration Classes

### `ClientConfig`

Configuration options for the Client class.

**Parameters:**
- `timeout` (int): Request timeout in seconds (default: 30)
- `retries` (int): Number of retries for failed requests (default: 3)
- `headers` (dict): Additional headers to send with requests
- `verify_ssl` (bool): Whether to verify SSL certificates (default: True)

**Example:**
```python
from fastmcp import Client, ClientConfig

config = ClientConfig(
    timeout=60,
    retries=5,
    headers={"Authorization": "Bearer token"}
)

async with Client("https://example.com/mcp", config=config) as client:
    # Use configured client
    pass
```

## Context Class

The Context class provides access to MCP system features during tool/resource execution.

### `Context`

Provides access to MCP Context features during execution.

#### `context.log(message: str, level: str = "info") -> None`
Send a log message back to the MCP client.

**Parameters:**
- `message` (str): The log message
- `level` (str): Log level ("debug", "info", "warning", "error")

#### `context.progress(current: int, total: int, message: str = "") -> None`
Report progress on a long-running operation.

**Parameters:**
- `current` (int): Current progress value
- `total` (int): Total progress value
- `message` (str): Optional progress message

#### `context.request_user_input(spec: dict) -> dict`
Request structured input from the user.

**Parameters:**
- `spec` (dict): Specification of the requested input

**Returns:**
- User-provided input data

## Auth Classes

Authentication-related classes and functions.

### `google_auth`
Google OAuth2 authentication provider.

#### `google_auth.setup(client_id: str, client_secret: str, redirect_uri: str) -> None`
Configure Google authentication.

**Parameters:**
- `client_id` (str): Google OAuth2 client ID
- `client_secret` (str): Google OAuth2 client secret
- `redirect_uri` (str): Redirect URI for OAuth2 flow

#### `google_auth.required(func) -> Callable`
Decorator to require Google authentication for a tool.

**Parameters:**
- `func` (Callable): The function to protect

**Returns:**
- The function with Google authentication requirement

### `github_auth`
GitHub OAuth2 authentication provider.

#### `github_auth.setup(client_id: str, client_secret: str, redirect_uri: str) -> None`
Configure GitHub authentication.

**Parameters:**
- `client_id` (str): GitHub OAuth2 client ID
- `client_secret` (str): GitHub OAuth2 client secret
- `redirect_uri` (str): Redirect URI for OAuth2 flow

#### `github_auth.required(func) -> Callable`
Decorator to require GitHub authentication for a tool.

**Parameters:**
- `func` (Callable): The function to protect

**Returns:**
- The function with GitHub authentication requirement

### `azure_auth`
Azure Active Directory authentication provider.

#### `azure_auth.setup(tenant_id: str, client_id: str, client_secret: str) -> None`
Configure Azure AD authentication.

**Parameters:**
- `tenant_id` (str): Azure AD tenant ID
- `client_id` (str): Azure AD client ID
- `client_secret` (str): Azure AD client secret

#### `azure_auth.required(func) -> Callable`
Decorator to require Azure AD authentication for a tool.

**Parameters:**
- `func` (Callable): The function to protect

**Returns:**
- The function with Azure AD authentication requirement

### `auth0_auth`
Auth0 authentication provider.

#### `auth0_auth.setup(domain: str, client_id: str, client_secret: str) -> None`
Configure Auth0 authentication.

**Parameters:**
- `domain` (str): Auth0 domain
- `client_id` (str): Auth0 client ID
- `client_secret` (str): Auth0 client secret

#### `auth0_auth.required(func) -> Callable`
Decorator to require Auth0 authentication for a tool.

**Parameters:**
- `func` (Callable): The function to protect

**Returns:**
- The function with Auth0 authentication requirement

## Transform Classes

Utility classes for transforming tools and resources.

### `retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0)`

Decorator to add retry logic to functions.

**Parameters:**
- `max_attempts` (int): Maximum number of retry attempts
- `delay` (float): Initial delay between attempts in seconds
- `backoff` (float): Multiplier for delay after each attempt

**Example:**
```python
from fastmcp.transform import retry

@mcp.tool
@retry(max_attempts=5, delay=1.0)
def unreliable_operation() -> str:
    # Implementation that might fail occasionally
    pass
```

### `rate_limit(calls: int, per: int)`

Decorator to add rate limiting to functions.

**Parameters:**
- `calls` (int): Number of calls allowed
- `per` (int): Time period in seconds

**Example:**
```python
from fastmcp.transform import rate_limit

@mcp.tool
@rate_limit(calls=10, per=60)  # 10 calls per minute
def rate_limited_operation() -> str:
    # Implementation with rate limiting
    pass
```

**Returns:**
- A new FastMCP instance containing all components from the input servers

**Example:**
```python
server1 = FastMCP("Server 1")
server2 = FastMCP("Server 2")

combined_server = FastMCP.compose(server1, server2)
```

## Client Class

The main class for interacting with MCP servers.

### `Client(url: str, config: Optional[ClientConfig] = None)`

Creates a new MCP client instance.

**Parameters:**
- `url` (str): The URL of the MCP server to connect to
- `config` (ClientConfig, optional): Configuration for the client

**Example:**
```python
from fastmcp import Client

async with Client("https://example.com/mcp") as client:
    # Use the client
    pass
```

### Methods

#### `async client.call_tool(name: str, arguments: dict = None) -> Any`
Call a tool on the MCP server.

**Parameters:**
- `name` (str): Name of the tool to call
- `arguments` (dict, optional): Arguments to pass to the tool

**Returns:**
- The result of the tool execution

**Example:**
```python
result = await client.call_tool(
    name="add",
    arguments={"a": 5, "b": 3}
)
```

#### `async client.read_resource(name: str, parameters: dict = None) -> Any`
Read a resource from the MCP server.

**Parameters:**
- `name` (str): Name of the resource to read
- `parameters` (dict, optional): Parameters for the resource

**Returns:**
- The resource data

**Example:**
```python
user_data = await client.read_resource(
    name="user-info",
    parameters={"user_id": "12345"}
)
```

#### `async client.get_prompt(name: str, arguments: dict = None) -> str`
Get a prompt from the MCP server.

**Parameters:**
- `name` (str): Name of the prompt
- `arguments` (dict, optional): Arguments for the prompt

**Returns:**
- The prompt string

**Example:**
```python
prompt = await client.get_prompt(
    name="generate_summary",
    arguments={"text": "Some text to summarize"}
)
```

#### `async client.list_tools() -> List[ToolInfo]`
Get a list of available tools on the server.

**Returns:**
- List of tool information objects

#### `async client.list_resources() -> List[ResourceInfo]`
Get a list of available resources on the server.

**Returns:**
- List of resource information objects

#### `async client.get_server_info() -> ServerInfo`
Get information about the connected server.

**Returns:**
- Server information object

## Configuration Classes

### `ClientConfig`

Configuration for MCP clients.

**Attributes:**
- `timeout` (int): Request timeout in seconds (default: 30)
- `retries` (int): Number of retry attempts (default: 3)
- `headers` (dict): HTTP headers to include with requests
- `ssl_context` (SSLContext, optional): SSL context for HTTPS connections

**Example:**
```python
from fastmcp.config import ClientConfig

config = ClientConfig(
    timeout=60,
    retries=5,
    headers={"Authorization": "Bearer token"}
)

async with Client("https://secure.example.com/mcp", config=config) as client:
    # Use configured client
    pass
```

## Decorators and Utilities

### `@fastmcp.transform`

Provides transformation utilities for tools and resources.

#### `@retry(max_attempts: int = 3, delay: float = 1.0)`
Retry decorator for tools that might fail.

**Parameters:**
- `max_attempts` (int): Maximum number of retry attempts
- `delay` (float): Delay between attempts in seconds

**Example:**
```python
from fastmcp.transform import retry

@mcp.tool
@retry(max_attempts=5, delay=2.0)
def unreliable_operation() -> str:
    # Implementation that might fail
    pass
```

#### `@rate_limit(calls: int, per: float)`
Rate limiting decorator.

**Parameters:**
- `calls` (int): Number of calls allowed
- `per` (float): Time period in seconds

**Example:**
```python
from fastmcp.transform import rate_limit

@mcp.tool
@rate_limit(calls=10, per=60)  # 10 calls per minute
def limited_operation() -> str:
    # Implementation with rate limiting
    pass
```

## Error Classes

### `McpError`
Base exception class for all MCP-related errors.

### `ToolCallError`
Raised when a tool call fails on the server.

### `ResourceNotFoundError`
Raised when a requested resource is not found.

### `AuthenticationError`
Raised when authentication fails.

**Example:**
```python
from fastmcp.errors import ToolCallError, ResourceNotFoundError

try:
    result = await client.call_tool("my_tool", {"param": "value"})
except ToolCallError as e:
    print(f"Tool call failed: {e}")
except ResourceNotFoundError as e:
    print(f"Resource not found: {e}")
```

## Context

### `MCPContext`
Provides access to MCP-specific context during tool/resource execution.

**Attributes:**
- `request_id` (str): Unique ID for the current request
- `created_at` (datetime): Timestamp when the request was created
- `server` (FastMCP): Reference to the server instance

**Example:**
```python
from fastmcp import FastMCP
from fastmcp.context import MCPContext

mcp = FastMCP("Context-aware Server")

@mcp.tool
def context_aware_operation(ctx: MCPContext) -> dict:
    """Operation that uses MCP context"""
    return {
        "request_id": ctx.request_id,
        "timestamp": ctx.created_at.isoformat(),
        "server_name": ctx.server.name
    }
```

## Testing Utilities

### `MockServer`
Provides a mock MCP server for testing purposes.

**Example:**
```python
import pytest
from fastmcp.testing import MockServer
from fastmcp import Client

@pytest.mark.asyncio
async def test_client_with_mock():
    async with MockServer() as mock_server:
        async with Client(mock_server.url) as client:
            # Test against mock server
            result = await client.call_tool("test_tool", {})
            assert result is not None
```

## Type Hints and Models

### `ToolInfo`
Information about an MCP tool.

**Attributes:**
- `name` (str): Tool name
- `description` (str): Tool description
- `input_schema` (dict): JSON schema for input
- `output_schema` (dict): JSON schema for output

### `ResourceInfo`
Information about an MCP resource.

**Attributes:**
- `name` (str): Resource name
- `description` (str): Resource description
- `schema` (dict): JSON schema for the resource

### `ServerInfo`
Information about an MCP server.

**Attributes:**
- `name` (str): Server name
- `version` (str): Server version
- `description` (str): Server description

## Next Steps

For implementation details and specific use cases, refer to:
1. [Server Development](../server-development/index.md) - Creating MCP servers
2. [Client Development](../client-development/index.md) - Using MCP clients
3. [Core Concepts](../core-concepts/index.md) - Understanding MCP fundamentals