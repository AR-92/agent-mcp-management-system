# Tools

Tools are the executable functions in your MCP server. They're similar to POST endpoints in traditional APIs - they perform actions, transform data, or interact with external systems.

## Basic Tool Definition

A tool is any Python function decorated with `@mcp.tool`:

```python
from fastmcp import FastMCP

mcp = FastMCP("Tool Example Server")

@mcp.tool
def greet(name: str) -> str:
    """Greet someone by name"""
    return f"Hello, {name}!"
```

## Tool Requirements

### Type Hints
Tools must have proper type hints:

```python
# Good - with type hints
@mcp.tool
def add(a: int, b: int) -> int:
    return a + b

# Bad - no type hints (will cause an error)
@mcp.tool
def bad_tool(a, b):
    return a + b
```

### Docstrings
Always include docstrings that describe what the tool does. This description is used by LLMs to understand when and how to use your tool:

```python
@mcp.tool
def calculate_area(length: float, width: float) -> float:
    """Calculate the area of a rectangle given its length and width in square units"""
    return length * width
```

## Tool Parameters

### Basic Types
Tools support common Python types:

```python
@mcp.tool
def process_data(
    name: str,
    count: int, 
    price: float,
    active: bool
) -> dict:
    return {
        "name": name,
        "count": count,
        "price": price,
        "active": active
    }
```

### Complex Types
Tools also support complex types using Pydantic:

```python
from pydantic import BaseModel
from typing import List, Optional

class Person(BaseModel):
    name: str
    age: int
    email: Optional[str] = None

class Address(BaseModel):
    street: str
    city: str
    country: str

@mcp.tool
def process_person(
    person: Person,
    addresses: List[Address],
    tags: List[str]
) -> dict:
    """Process a person with their addresses and tags"""
    return {
        "person": person.dict(),
        "addresses": [addr.dict() for addr in addresses],
        "tags": tags,
        "summary": f"Processed {person.name} with {len(addresses)} addresses"
    }
```

## Async Tools

For non-blocking operations, use async tools:

```python
import asyncio
import aiohttp

@mcp.tool
async def fetch_data(url: str) -> dict:
    """Fetch JSON data from a URL"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

@mcp.tool
async def process_multiple_urls(urls: list[str]) -> list[dict]:
    """Fetch data from multiple URLs concurrently"""
    tasks = [fetch_data(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return results
```

## Tool Validation

FastMCP automatically validates tool inputs based on type hints:

```python
@mcp.tool
def divide(dividend: float, divisor: float) -> float:
    """Divide two numbers"""
    if divisor == 0:
        raise ValueError("Division by zero is not allowed")
    return dividend / divisor
```

## Tool Categories

### Simple Tools
Basic functions that perform straightforward operations:

```python
@mcp.tool
def concatenate_strings(*strings: str) -> str:
    """Concatenate multiple strings"""
    return "".join(strings)
```

### Stateful Tools
Tools that can access application state (when properly configured):

```python
class DataProcessor:
    def __init__(self):
        self.processed_count = 0
    
    @mcp.tool
    def process_item(self, item: str) -> str:
        """Process an item and track count"""
        self.processed_count += 1
        return f"Processed ({self.processed_count}): {item}"

processor = DataProcessor()
```

### Context-Aware Tools
Tools that can use MCP context (see MCP Context documentation):

```python
@mcp.tool
def long_running_task(context):
    """A task that reports progress"""
    for i in range(10):
        # Report progress to the client
        context.progress(i, 10, f"Processing step {i+1}/10")
        # Simulate work
        time.sleep(0.5)
    
    context.log("Task completed successfully")
    return "Long running task complete"
```

## Error Handling

Tools should raise appropriate exceptions for error conditions:

```python
import os

@mcp.tool
def read_file(filename: str) -> str:
    """Read the contents of a file"""
    if not os.path.exists(filename):
        raise FileNotFoundError(f"File {filename} does not exist")
    
    if not os.access(filename, os.R_OK):
        raise PermissionError(f"Cannot read file {filename}")
    
    with open(filename, 'r') as f:
        return f.read()
```

## Tool Metadata

You can provide additional metadata for tools:

```python
@mcp.tool(
    name="custom_tool_name",  # Override the function name
    description="Custom description that overrides docstring"  # Override docstring
)
def my_tool(x: int) -> int:
    """This docstring will be overridden by the description parameter"""
    return x * 2
```

## Advanced Tool Features

### Tool Transformation
Create variations of tools with modified behavior:

```python
# Original tool
@mcp.tool
def calculate_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate Euclidean distance between two points"""
    return ((x2-x1)**2 + (y2-y1)**2)**0.5

# Transform the tool to accept a single dictionary parameter instead
from fastmcp.tools import ToolTransform

def coordinates_to_dict(tool_func):
    """Transform a tool that takes coordinates to accept a single dict parameter"""
    def wrapper(points: dict) -> float:
        return tool_func(
            points['x1'], points['y1'], 
            points['x2'], points['y2']
        )
    return wrapper

# Apply the transformation to create a new tool variant
transformed_distance = ToolTransform(
    calculate_distance,
    wrapper=coordinates_to_dict,
    name="calculate_distance_dict"
)
```

## Best Practices

1. **Clear Descriptions**: Write clear, action-oriented docstrings
2. **Proper Typing**: Always use type hints for parameters and return values
3. **Error Handling**: Handle errors gracefully with appropriate exceptions
4. **Validation**: Validate inputs and provide meaningful error messages
5. **Async When Appropriate**: Use async for I/O-bound operations
6. **Security**: Sanitize inputs and validate user data before processing

## Next Steps

- Learn about [Resources](./resources.md) - for providing data to LLMs
- Explore [Prompts](./prompts.md) - for reusable prompt templates
- Discover [MCP Context](./mcp-context.md) - for advanced tool features