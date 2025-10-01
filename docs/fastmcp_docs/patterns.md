# Patterns

This section covers common implementation patterns and best practices for FastMCP applications. These patterns help you structure your MCP servers and clients effectively.

## Tool Transformation Patterns

### Retry Pattern
Implement automatic retries for unreliable operations:

```python
from fastmcp import FastMCP
from fastmcp.transform import retry

mcp = FastMCP("Resilient Server")

@mcp.tool
@retry(max_attempts=3, delay=1.0)
def unreliable_api_call(data: str) -> str:
    """API call that might occasionally fail"""
    # Implementation that might fail
    import random
    if random.random() < 0.3:
        raise Exception("Random failure")
    return f"Processed: {data}"
```

### Rate Limiting Pattern
Control the frequency of tool calls:

```python
from fastmcp.transform import rate_limit

@mcp.tool
@rate_limit(calls=10, per=60)  # 10 calls per minute
def rate_limited_operation(data: str) -> str:
    """Operation with rate limiting"""
    return f"Rate-limited: {data}"
```

### Caching Pattern
Cache expensive operations:

```python
import functools

@functools.lru_cache(maxsize=128)
def expensive_computation(n: int) -> int:
    """Expensive computation with caching"""
    result = 0
    for i in range(n):
        result += i ** 2
    return result

@mcp.tool
def compute_cached(n: int) -> int:
    """Tool that uses cached computation"""
    return expensive_computation(n)
```

## Server Composition Patterns

### Modular Server Pattern
Break your server into logical modules:

```python
# user_server.py
from fastmcp import FastMCP

user_mcp = FastMCP("User Management Server")

@user_mcp.tool
def create_user(name: str, email: str) -> dict:
    """Create a new user"""
    return {"id": "123", "name": name, "email": email}

# data_server.py
from fastmcp import FastMCP

data_mcp = FastMCP("Data Server")

@data_mcp.resource
def get_user_data(user_id: str) -> dict:
    """Get user data"""
    return {"user_id": user_id, "preferences": {}}

# main.py
from fastmcp import FastMCP
from user_server import user_mcp
from data_server import data_mcp

# Compose servers into a single interface
composed_server = FastMCP.compose(user_mcp, data_mcp)

if __name__ == "__main__":
    composed_server.run()
```

### Proxy Server Pattern
Create a server that forwards requests to other servers:

```python
from fastmcp import FastMCP
from fastmcp import Client

mcp = FastMCP("Proxy Server")

# Client to forward requests to another server
upstream_client = Client("https://upstream-server.com/mcp")

@mcp.tool
async def proxy_tool(tool_name: str, args: dict) -> any:
    """Proxy tool that forwards to upstream server"""
    return await upstream_client.call_tool(tool_name, args)
```

## Resource Patterns

### Streaming Resource Pattern
For large data resources, implement streaming:

```python
from fastmcp import FastMCP
import asyncio

mcp = FastMCP("Streaming Server")

@mcp.resource
async def large_dataset_resource() -> list:
    """Resource that returns a large dataset"""
    # Simulate loading a large dataset
    result = []
    for i in range(1000):
        result.append({"id": i, "value": f"data_{i}"})
    return result
```

### Parameterized Resource Pattern
Create resources that accept parameters:

```python
@mcp.resource
def user_info_resource(user_id: str, include_preferences: bool = False) -> dict:
    """User information resource with optional preferences"""
    user_data = {
        "id": user_id,
        "name": "John Doe",
        "email": "john@example.com"
    }
    
    if include_preferences:
        user_data["preferences"] = {"theme": "dark", "language": "en"}
    
    return user_data
```

## Authentication and Authorization Patterns

### Custom Authentication Pattern
Implement custom authentication logic:

```python
from fastmcp import FastMCP
from fastmcp.context import MCPContext
from fastmcp.errors import AuthenticationError
import jwt

def require_auth(ctx: MCPContext):
    """Custom authentication middleware"""
    auth_header = ctx.request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise AuthenticationError("Missing or invalid authorization header")
    
    token = auth_header.split(" ")[1]
    try:
        # Verify JWT token
        payload = jwt.decode(token, "your-secret-key", algorithms=["HS256"])
        ctx.authenticated_user = payload["user_id"]
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid token")

mcp = FastMCP("Auth Server")
mcp.middleware.append(require_auth)

@mcp.tool
def secure_operation(ctx: MCPContext) -> str:
    """Operation requiring authentication"""
    return f"User {ctx.authenticated_user} performed secure operation"
```

### Role-Based Access Control Pattern
Implement role-based access control:

```python
from enum import Enum
from fastmcp.errors import AuthorizationError

class Role(Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

def require_role(required_role: Role):
    """Middleware to require specific role"""
    def middleware(ctx: MCPContext):
        user_role = getattr(ctx, "user_role", Role.GUEST)
        if user_role != required_role:
            raise AuthorizationError(f"Role {required_role.value} required")
    return middleware

admin_middleware = require_role(Role.ADMIN)
mcp.middleware.append(admin_middleware)

@mcp.tool
def admin_only_operation() -> str:
    """Operation available only to admins"""
    return "Admin operation completed"
```

## Data Validation Patterns

### Pydantic Validation Pattern
Use Pydantic models for complex data validation:

```python
from pydantic import BaseModel, Field
from typing import List, Optional

class User(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    age: Optional[int] = Field(None, ge=0, le=150)

class CreateUserRequest(BaseModel):
    users: List[User]
    notify: bool = True

@mcp.tool
def create_multiple_users(request: CreateUserRequest) -> dict:
    """Create multiple users with validation"""
    user_ids = []
    for user in request.users:
        # Process user creation
        user_ids.append(f"user_{len(user_ids)}")
    
    return {
        "created_user_ids": user_ids,
        "total_created": len(request.users)
    }
```

## Error Handling Patterns

### Custom Error Responses
Provide detailed error information:

```python
from fastmcp.errors import McpError

class ValidationError(McpError):
    """Custom validation error"""
    def __init__(self, field: str, message: str):
        super().__init__(f"Validation error in field '{field}': {message}")
        self.field = field
        self.message = message

@mcp.tool
def validate_data(data: dict) -> bool:
    """Validate data with custom errors"""
    required_fields = ["name", "email", "age"]
    
    for field in required_fields:
        if field not in data:
            raise ValidationError(field, "Field is required")
    
    if not isinstance(data["age"], int) or data["age"] < 0:
        raise ValidationError("age", "Must be a positive integer")
    
    return True
```

## Async Pattern Best Practices

### Concurrent Operations Pattern
Perform multiple operations concurrently:

```python
import asyncio

@mcp.tool
async def process_multiple_items(items: list) -> list:
    """Process multiple items concurrently"""
    async def process_item(item):
        # Simulate async processing
        await asyncio.sleep(0.1)
        return f"processed_{item}"
    
    # Process all items concurrently
    results = await asyncio.gather(*[process_item(item) for item in items])
    return results
```

### Async Generator Pattern
For streaming data, use async generators:

```python
import asyncio

@mcp.tool 
async def stream_data_chunks(total_chunks: int) -> list:
    """Stream data in chunks"""
    chunks = []
    for i in range(total_chunks):
        await asyncio.sleep(0.01)  # Simulate async operation
        chunks.append(f"chunk_{i}")
    return chunks
```

## Testing Patterns

### Mock Dependencies Pattern
Isolate your tools from external dependencies during testing:

```python
from unittest.mock import Mock
import pytest
from fastmcp.testing import MockServer

# Production code
external_service = Mock()

def set_external_service_for_testing(mock_service):
    global external_service
    external_service = mock_service

@mcp.tool
def service_dependent_operation(data: str) -> str:
    """Operation that depends on external service"""
    result = external_service.process(data)
    return f"processed: {result}"

# Test code
@pytest.mark.asyncio
async def test_service_dependent_operation():
    # Create a mock service
    mock_service = Mock()
    mock_service.process.return_value = "mock_result"
    set_external_service_for_testing(mock_service)
    
    # Test with mock
    result = service_dependent_operation("test_data")
    assert result == "processed: mock_result"
    mock_service.process.assert_called_once_with("test_data")
```

## Performance Optimization Patterns

### Connection Pooling Pattern
Reuse connections for external services:

```python
import aiohttp
from contextlib import asynccontextmanager

class ConnectionPool:
    def __init__(self):
        self._session = None
    
    async def get_session(self):
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def close(self):
        if self._session:
            await self._session.close()

connection_pool = ConnectionPool()

@mcp.tool
async def http_request_tool(url: str) -> str:
    """Tool that makes HTTP requests using connection pooling"""
    session = await connection_pool.get_session()
    async with session.get(url) as response:
        return await response.text()

# Close connections when server shuts down
import atexit
atexit.register(lambda: asyncio.run(connection_pool.close()))
```

## Configuration Patterns

### Environment-Based Configuration
Configure your server based on environment:

```python
import os
from fastmcp import FastMCP

def create_server_from_env():
    """Create server configured from environment variables"""
    env = os.getenv("FASTMCP_ENV", "development")
    
    if env == "production":
        return FastMCP(
            name="Production Server",
            debug=False,
            cors_enabled=False
        )
    elif env == "staging":
        return FastMCP(
            name="Staging Server", 
            debug=False,
            cors_enabled=True
        )
    else:  # development
        return FastMCP(
            name="Development Server",
            debug=True,
            cors_enabled=True
        )

mcp = create_server_from_env()
```

## Next Steps

1. [Server Development](../server-development/index.md) - Deep dive into server implementation
2. [Client Development](../client-development/index.md) - Advanced client patterns
3. [Deployment](../deployment/index.md) - Production deployment patterns