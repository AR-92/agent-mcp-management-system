# What is the Model Context Protocol (MCP)?

The Model Context Protocol (MCP) is a standardized way to connect LLMs to tools, data, and other resources they can use. Think of it as a universal adapter that enables LLM applications to access external functionality in a consistent way.

## Core Concepts

MCP defines three main types of interactions:

### Tools
Tools are executable functions that perform actions. They're like POST endpoints that execute code or produce side effects:

```python
@mcp.tool
def create_file(filename: str, content: str):
    """Create a new file with the given content"""
    with open(filename, 'w') as f:
        f.write(content)
```

### Resources
Resources provide data to LLMs. They're like GET endpoints that return information:

```python
@mcp.resource
def read_file(path: str):
    """Read the contents of a file"""
    with open(path, 'r') as f:
        return f.read()
```

### Prompts
Prompts are reusable templates for LLM interactions:

```python
@mcp.prompt
def summarize_text(text: str):
    """Please summarize the following text: {text}"""
```

## How MCP Works

MCP uses JSON-RPC over HTTP to enable communication between the LLM client (like Claude Desktop, Cursor, etc.) and MCP servers. The protocol standardizes:

- Request/response formats
- Error handling
- Authentication
- Discovery of available tools and resources

## Benefits of MCP

1. **Standardization**: One protocol works with multiple clients and servers
2. **Security**: Built-in authentication and authorization
3. **Discoverability**: Clients can automatically discover what tools are available
4. **Flexibility**: Can expose any Python function as a tool

## FastMCP and MCP 2.0

FastMCP pioneered Python MCP development, with FastMCP 1.0 being incorporated into the official MCP SDK in 2024.

This is FastMCP 2.0 — the actively maintained version that extends far beyond basic protocol implementation. While the SDK provides core functionality, FastMCP 2.0 delivers everything needed for production: advanced MCP patterns (server composition, proxying, OpenAPI/FastAPI generation, tool transformation), enterprise auth (Google, GitHub, Azure, Auth0, WorkOS, and more), deployment tools, testing frameworks, and comprehensive client libraries.