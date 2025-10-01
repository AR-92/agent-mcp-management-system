# Resources

Resources provide data to LLM applications. They're similar to GET endpoints in traditional APIs - they return information to be used in the LLM's context.

## Basic Resource Definition

A resource is any function decorated with `@mcp.resource`:

```python
from fastmcp import FastMCP

mcp = FastMCP("Resource Example Server")

@mcp.resource
def get_current_time() -> str:
    """Get the current time"""
    from datetime import datetime
    return datetime.now().isoformat()
```

## Resource Requirements

### Type Hints
Like tools, resources require proper type hints:

```python
# Good - with type hints
@mcp.resource
def get_server_info() -> dict:
    return {"version": "1.0", "status": "running"}

# Bad - no type hints
@mcp.resource
def bad_resource():  # This will cause an error
    return "data"
```

### Docstrings
Include descriptive docstrings that explain what the resource provides:

```python
@mcp.resource
def get_weather_data(city: str) -> dict:
    """Get current weather data for a specified city"""
    # Implementation here
    return {"city": city, "temperature": 22, "condition": "sunny"}
```

## Resource Parameters

### Simple Resources (No Parameters)
Resources that provide static data:

```python
@mcp.resource
def get_server_metadata() -> dict:
    """Get server metadata and configuration"""
    return {
        "name": "My Server",
        "version": "1.0.0",
        "features": ["tool1", "tool2", "resource1"]
    }
```

### Parameterized Resources
Resources that accept parameters to customize the returned data:

```python
from typing import Optional

@mcp.resource
def get_user_profile(user_id: str, include_private: bool = False) -> dict:
    """Get user profile information"""
    # In a real implementation, this would fetch from a database
    profile = {
        "id": user_id,
        "name": f"User {user_id}",
        "public_info": "This is public data"
    }
    
    if include_private:
        profile["private_info"] = "This is private data"
    
    return profile
```

### Complex Parameter Types
Resources support complex parameter types like Tools do:

```python
from pydantic import BaseModel
from typing import List

class FilterOptions(BaseModel):
    category: str
    max_results: int = 10
    include_inactive: bool = False

@mcp.resource
def get_filtered_data(filters: FilterOptions) -> List[dict]:
    """Get data based on specified filters"""
    # Implementation would use filters.category, filters.max_results, etc.
    return [
        {"id": i, "category": filters.category, "active": True} 
        for i in range(min(filters.max_results, 100))
    ]
```

## Types of Resources

### Static Resources
Resources that return the same data every time:

```python
@mcp.resource
def get_constants() -> dict:
    """Get application constants"""
    return {
        "PI": 3.14159,
        "E": 2.71828,
        "GRAVITY": 9.81
    }
```

### Dynamic Resources
Resources that return different data based on current state:

```python
import time

@mcp.resource
def get_server_stats() -> dict:
    """Get current server statistics"""
    return {
        "timestamp": time.time(),
        "active_connections": 5,
        "memory_usage": "45%",
        "uptime": time.time() - get_server_stats.start_time
    }

# Initialize with start time
get_server_stats.start_time = time.time()
```

### File Resources
Resources that return file contents:

```python
import os
from typing import Optional

@mcp.resource
def read_file(path: str, encoding: str = "utf-8", max_size: int = 1024*1024) -> str:
    """Read a file with safety checks"""
    # Safety checks
    if not os.path.isabs(path):
        path = os.path.abspath(path)
    
    # Prevent directory traversal
    if not path.startswith(os.getcwd()):
        raise ValueError("Path traversal detected")
    
    # Check file size
    if os.path.getsize(path) > max_size:
        raise ValueError(f"File too large: {path}")
    
    with open(path, 'r', encoding=encoding) as f:
        return f.read()
```

## Async Resources

For non-blocking data retrieval:

```python
import aiohttp
import asyncio

@mcp.resource
async def fetch_external_data(url: str) -> dict:
    """Fetch data from an external API"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

@mcp.resource
async def get_multiple_sources(urls: list[str]) -> list[dict]:
    """Get data from multiple sources concurrently"""
    tasks = [fetch_external_data(url) for url in urls]
    return await asyncio.gather(*tasks)
```

## Resource Templates

Resources can be parameterized to create reusable templates:

```python
from fastmcp import template

# Define a template resource
@template
def file_template(path: str, encoding: str = "utf-8") -> str:
    """Template for reading files"""
    with open(path, 'r', encoding=encoding) as f:
        return f.read()

# Register multiple resource instances from the template
@mcp.resource
def read_config() -> str:
    """Read the application configuration file"""
    return file_template("config.json")

@mcp.resource 
def read_readme() -> str:
    """Read the project README file"""
    return file_template("README.md")
```

## Advanced Resource Features

### Streaming Resources
For large data that should be streamed:

```python
from typing import Generator

@mcp.resource
def stream_large_dataset(limit: int = 1000) -> Generator[dict, None, None]:
    """Stream a large dataset as a sequence of records"""
    for i in range(limit):
        yield {"id": i, "data": f"record_{i}"}
```

### Conditional Resources
Resources that return different data based on context:

```python
@mcp.resource
def get_user_data(user_id: str, context: dict = None) -> dict:
    """Get user data with optional context"""
    data = {"user_id": user_id, "last_login": "2023-01-01"}
    
    # If context provides permissions, include private data
    if context and context.get("permissions", {}).get("read_private"):
        data["private_data"] = "sensitive information"
    
    return data
```

## Resource Caching

Implement caching for expensive resources:

```python
import functools
import time

# Simple in-memory cache
_resource_cache = {}
_CACHE_TTL = 60  # seconds

def cached_resource(ttl: int = 60):
    """Decorator for caching resource results"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            now = time.time()
            
            if cache_key in _resource_cache:
                result, timestamp = _resource_cache[cache_key]
                if now - timestamp < ttl:
                    return result
            
            result = func(*args, **kwargs)
            _resource_cache[cache_key] = (result, now)
            return result
        return wrapper
    return decorator

@cached_resource(ttl=30)
@mcp.resource
def get_external_config() -> dict:
    """Get external configuration with caching"""
    # Simulate external API call
    import time
    time.sleep(0.1)  # Simulate network delay
    return {"config": "value", "timestamp": time.time()}
```

## Error Handling

Resources should handle errors appropriately:

```python
import os

@mcp.resource
def get_file_info(path: str) -> dict:
    """Get information about a file"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    
    if not os.access(path, os.R_OK):
        raise PermissionError(f"Cannot access file: {path}")
    
    stat = os.stat(path)
    return {
        "size": stat.st_size,
        "modified": stat.st_mtime,
        "permissions": oct(stat.st_mode)[-3:]
    }
```

## Best Practices

1. **Clear Descriptions**: Write clear docstrings explaining what data is provided
2. **Proper Typing**: Always use type hints for parameters and return values
3. **Safety**: Validate paths and parameters to prevent security issues
4. **Performance**: Consider caching expensive resources
5. **Error Handling**: Handle common errors gracefully
6. **Async When Appropriate**: Use async for I/O-bound operations
7. **Security**: Sanitize inputs and validate user data

## Next Steps

- Learn about [Prompts](./prompts.md) - reusable prompt templates
- Explore [MCP Context](./mcp-context.md) - for advanced resource features
- Check out [Server Development](../server-development/index.md) for more complex scenarios