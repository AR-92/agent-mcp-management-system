# Core Concepts

Understanding the core concepts of FastMCP is essential for building effective Model Context Protocol applications. This section covers the fundamental building blocks of MCP: Tools, Resources, Prompts, and Context.

## The FastMCP Application

The `FastMCP` class is the core of every MCP server:

```python
from fastmcp import FastMCP

# Create an MCP server instance
mcp = FastMCP("My Server Name")
```

The FastMCP instance serves as a registry for all tools, resources, and prompts in your application.

## Three Core Components

MCP applications work with three core types of components:

1. **[Tools](./tools.md)** - Functions that perform actions (like POST requests)
2. **[Resources](./resources.md)** - Data providers (like GET requests) 
3. **[Prompts](./prompts.md)** - Templates for LLM interactions

## MCP Context

The **[MCP Context](./mcp-context.md)** allows your tools and resources to interact with the MCP system during execution, enabling features like progress reporting, logging, and more.

## Key Principles

### 1. Convention over Configuration
FastMCP uses Python type hints and docstrings to automatically generate schemas:

```python
@mcp.tool
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b
```

### 2. Async-First Design
FastMCP is designed with async/await in mind:

```python
import asyncio

@mcp.tool
async def async_operation(data: str) -> str:
    """An asynchronous operation"""
    await asyncio.sleep(1)  # Simulate async work
    return f"Processed: {data}"
```

### 3. Type Safety
Leverage Python types for automatic validation:

```python
from typing import List, Optional
from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str

@mcp.tool
def create_users(users: List[User]) -> int:
    """Create multiple users and return count"""
    # FastMCP validates the input structure automatically
    return len(users)
```

## Getting Started with Components

Each component type has its own use case:

- Use **Tools** when you need to perform an action, transform data, or interact with external systems
- Use **Resources** when you need to provide data to the LLM context 
- Use **Prompts** when you want to define reusable prompt templates

## Next Steps

1. Learn about [Tools](./tools.md) - executable functions in your MCP server
2. Explore [Resources](./resources.md) - data providers for your LLM
3. Understand [Prompts](./prompts.md) - reusable prompt templates
4. Discover how to use [MCP Context](./mcp-context.md) in your components