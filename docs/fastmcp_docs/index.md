# FastMCP Documentation

Welcome to the comprehensive documentation for FastMCP, the fast, Pythonic way to build Model Context Protocol (MCP) servers and clients.

## What is FastMCP?

FastMCP is a Python framework that provides a high-level, Pythonic interface for building, managing, and interacting with Model Context Protocol (MCP) servers and clients. MCP enables standardized communication between LLM applications and tools, data, and other resources.

## Sections

- [Getting Started](./getting-started/index.md) - Quick start guide for FastMCP
- [Overview](./overview/index.md) - Understand the basics of FastMCP and MCP
- [Installation](./installation/index.md) - How to install and set up FastMCP
- [Core Concepts](./core-concepts/index.md) - Fundamental concepts you need to know
- [Server Development](./server-development/index.md) - Creating MCP servers
- [Client Development](./client-development/index.md) - Working with MCP clients
- [Patterns](./patterns/index.md) - Common implementation patterns
- [Integrations](./integrations/index.md) - Connecting with other systems
- [Deployment](./deployment/index.md) - Deploying your MCP applications
- [Examples](./examples/index.md) - Practical examples to get you started
- [API Reference](./api-reference/index.md) - Complete API documentation
- [Contributing](./contributing/index.md) - How to contribute to FastMCP

## Quick Start

```python
from fastmcp import FastMCP

mcp = FastMCP("Demo 🚀")

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

if __name__ == "__main__":
    mcp.run()
```

FastMCP provides everything you need for production: advanced MCP patterns, enterprise authentication, deployment tools, testing frameworks, and comprehensive client libraries.