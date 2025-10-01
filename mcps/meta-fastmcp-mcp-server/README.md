# Meta FastMCP Server

A professional Model Context Protocol (MCP) server built with FastMCP for managing agent systems and providing utility functions.

## Overview

The Meta FastMCP Server is a comprehensive MCP implementation that provides:

- **Agent Management**: Tools for creating, listing, and deleting agents
- **Task Execution**: Capabilities for running tasks with configurable parameters
- **System Utilities**: Safe system command execution and monitoring
- **Resource Access**: Information about server status, metrics, and documentation
- **Prompt Templates**: Predefined prompts for common AI interactions

## Features

- ✅ Professional FastMCP implementation
- ✅ Full tool, resource, and prompt support
- ✅ Type safety with Pydantic models
- ✅ Asynchronous operation support
- ✅ Safe system command execution
- ✅ Comprehensive error handling
- ✅ Environment-based configuration
- ✅ Detailed documentation

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. Clone or navigate to this directory
2. Install dependencies:

```bash
pip install -r requirements.txt
```

Or install directly:

```bash
pip install fastmcp>=2.0.0 pydantic>=2.0.0
```

## Usage

### Running the Server

#### Method 1: Direct Python execution
```bash
python server.py
```

#### Method 2: Using environment variables for configuration
```bash
FASTMCP_HOST=0.0.0.0 FASTMCP_PORT=8000 python server.py
```

#### Method 3: Using FastMCP CLI
```bash
fastmcp run server.py:mcp --transport http --port 8000
```

By default, the server runs on `http://127.0.0.1:8000` using the HTTP transport.

## Components

### Tools

- `create_agent`: Create new agents with specified configurations
- `delete_agent`: Remove existing agents
- `list_agents`: Get a list of all available agents
- `execute_task`: Execute tasks with configurable parameters
- `run_system_command`: Safely execute system commands (restricted to safe commands)
- `async_operation_simulation`: Demonstrate asynchronous operations
- `health_check`: Check server health status
- `calculate_expression`: Safely calculate mathematical expressions

### Resources

- `get_server_info`: Retrieve server metadata and status
- `get_agent_types`: List available agent types
- `get_system_metrics`: Get system resource metrics
- `get_documentation_links`: Access to relevant documentation

### Prompts

- `agent_selection_prompt`: Generate prompts for agent selection
- `error_resolution_prompt`: Create prompts for error resolution
- `task_breakdown_prompt`: Generate prompts for breaking down complex tasks

## Security Considerations

- System command execution is restricted to a whitelist of safe commands
- Input validation is performed using Pydantic models
- Mathematical expression evaluation has security checks
- Server configuration can be controlled via environment variables

## Configuration

The server can be configured using environment variables:

- `FASTMCP_HOST`: Host to bind to (default: 127.0.0.1)
- `FASTMCP_PORT`: Port to listen on (default: 8000)

## Integration

This server can be integrated with any LLM client that supports the Model Context Protocol, including:

- Cursor IDE
- Claude Desktop
- And other MCP-compatible clients

## Development

To extend the server functionality:

1. Add new tools using the `@mcp.tool` decorator
2. Add new resources using the `@mcp.resource` decorator  
3. Add new prompts using the `@mcp.prompt` decorator
4. Ensure all functions have proper type hints and docstrings

## Troubleshooting

If you encounter issues:

1. Ensure all dependencies are installed: `pip install -r requirements.txt`
2. Check the server is running and accessible at the configured address
3. Verify your MCP client is configured to connect to this server
4. Check server logs for error messages

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please file an issue in the repository or consult the FastMCP documentation at https://gofastmcp.com