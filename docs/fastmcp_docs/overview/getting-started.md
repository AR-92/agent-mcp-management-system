# Getting Started with FastMCP

This guide will help you get up and running with FastMCP quickly.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

Install FastMCP using pip:

```bash
pip install fastmcp
```

## Your First MCP Server

Create a simple server file `hello_server.py`:

```python
from fastmcp import FastMCP

# Create an instance of FastMCP
mcp = FastMCP("Hello Server")

# Define a tool using the @mcp.tool decorator
@mcp.tool
def hello(name: str) -> str:
    """Greet someone by name"""
    return f"Hello, {name}! Welcome to FastMCP."

# Define another tool
@mcp.tool
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b

# Define a resource to read data
@mcp.resource
def get_greeting_template() -> str:
    """Get a greeting template"""
    return "Hello, {name}! Today is {date}."

# Run the server
if __name__ == "__main__":
    mcp.run()
```

Run the server:

```bash
python hello_server.py
```

## Understanding the Components

### The FastMCP Instance

```python
mcp = FastMCP("Server Name")
```

This creates a new MCP server with the given name. The name appears to clients when they discover your server.

### Tools

Tools are functions that perform actions:

```python
@mcp.tool
def my_tool(param: str) -> str:
    """Description of what the tool does"""
    return f"Result: {param}"
```

- Tools are decorated with `@mcp.tool`
- Use type hints for automatic validation
- Include docstrings for tool descriptions
- Can return any JSON-serializable data

### Resources

Resources provide data to the client:

```python
@mcp.resource
def my_resource(path: str) -> str:
    """Description of what the resource provides"""
    with open(path, 'r') as f:
        return f.read()
```

- Resources are decorated with `@mcp.resource`
- Used to load information into the LLM's context

## Running Your Server

There are several ways to run your server:

### Direct Python Execution

```python
if __name__ == "__main__":
    mcp.run()
```

Then run with:
```bash
python my_server.py
```

### Using the FastMCP CLI

```bash
fastmcp run my_server:mcp
```

## Client Example

To interact with your server programmatically, you can create a client:

```python
import asyncio
from fastmcp import Client

async def main():
    async with Client("http://localhost:8000") as client:  # Adjust URL as needed
        # Call the hello tool
        result = await client.call_tool(
            name="hello",
            arguments={"name": "World"}
        )
        print(result)  # Output: "Hello, World! Welcome to FastMCP."

        # Call the add_numbers tool
        result = await client.call_tool(
            name="add_numbers",
            arguments={"a": 5, "b": 3}
        )
        print(result)  # Output: 8

asyncio.run(main())
```

## Next Steps

Now that you have a basic server running, you can:

1. **[Installation Guide](../installation/index.md)** - Learn more about installation options
2. **[Core Concepts](../core-concepts/index.md)** - Understand the fundamental building blocks
3. **[Server Development](../server-development/index.md)** - Build more advanced servers
4. **[Examples](../examples/index.md)** - Check out practical examples

## Troubleshooting

### Server Won't Start
- Make sure the port isn't already in use
- Check that your Python version meets the requirements
- Verify FastMCP is properly installed

### Tools Not Appearing
- Ensure your functions have proper type hints
- Check that docstrings are present for tool descriptions
- Verify the decorator is `@mcp.tool` not something else

### Connection Issues
- Verify the server is running
- Check the URL you're using to connect
- Ensure no firewall is blocking the connection