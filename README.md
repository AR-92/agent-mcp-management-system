# Simple MCP Management System

A simplified MCP (Model Context Protocol) server management system with essential functionality to manage multiple MCP servers with Qwen integration.

## Project Structure

```
.
├── simple_mcp_manager.py      # Simple manager for MCP servers
├── requirements.txt          # Dependencies
├── mcps/                   # MCP server implementations
│   ├── simple_meta_fastmcp_server.py
│   └── simple_fastmcp_docs_server.py
└── docs/                   # Documentation directory
    └── fastmcp_docs/       # FastMCP documentation
```

## Features

- **Simple Management**: Start, stop, restart, and monitor MCP servers
- **Qwen Integration**: Automatic integration with Qwen configuration
- **Documentation Server**: Access FastMCP documentation via MCP
- **Meta Server**: Tools for creating new MCP servers and managing configurations
- **Comprehensive Tools**: All essential MCP components (tools, resources, prompts)

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Managing MCP Servers

Start all servers:
```bash
python simple_mcp_manager.py start-all
```

Stop all servers:
```bash
python simple_mcp_manager.py stop-all
```

Start a specific server:
```bash
python simple_mcp_manager.py start simple-meta-fastmcp-server
```

Check status of all servers:
```bash
python simple_mcp_manager.py status
```

### Qwen Integration

Integrate MCP servers with Qwen:
```bash
python simple_mcp_manager.py integrate
```

List integrated MCPs:
```bash
python simple_mcp_manager.py list-qwen
```

Get Qwen configuration path:
```bash
python simple_mcp_manager.py qwen-config-path
```

## Servers

### Simple Meta MCP Server

Provides utilities for managing and creating MCP servers:

**Tools:**
- `create_mcp_skeleton`: Create a skeleton for a new MCP server
- `validate_mcp_config`: Validate MCP configuration content
- `analyze_existing_mcp`: Analyze existing MCP server code
- `run_system_command`: Execute system commands safely
- `generate_mcp_project`: Generate a complete MCP project

**Resources:**
- `get_server_info`: Server information
- `get_system_metrics`: System metrics
- `get_config_templates`: Configuration templates

**Prompts:**
- `mcp_implementation_guide`: Implementation guides
- `mcp_security_checklist`: Security checklists
- `error_resolution_prompt`: Error resolution guides

### Simple FastMCP Documentation Server

Provides access to FastMCP documentation:

**Tools:**
- `list_documentation_sections`: List documentation sections
- `search_documentation`: Search documentation by query
- `read_documentation_file`: Read specific documentation files
- `get_section_files`: Get files in a documentation section
- `find_examples_for_feature`: Find examples for specific features

**Resources:**
- `get_documentation_toc`: Documentation table of contents
- `get_latest_docs_updates`: Get recently updated docs
- `get_documentation_stats`: Documentation statistics
- `get_server_health`: Server health status

**Prompts:**
- `explain_fastmcp_concept`: Explain FastMCP concepts
- `implementation_guide_prompt`: Implementation guides
- `best_practices_prompt`: Best practices
- `comparison_prompt`: Feature comparisons
- `troubleshooting_prompt`: Troubleshooting guides

## Configuration

The system uses environment variables for configuration (via `.env` file):

- `START_ON_BOOT`: Start servers on boot (default: false)
- `SHUTDOWN_ON_EXIT`: Shutdown servers on exit (default: true)
- `ENVIRONMENT`: Environment name (default: development)