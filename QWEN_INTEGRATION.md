# Qwen MCP Integration Guide

This guide explains how to integrate your Agent MCP Management System with Qwen's global configuration system for seamless use of custom MCP servers.

## Overview

The integration allows Qwen to automatically discover and use MCP (Model Context Protocol) servers that you've developed in the `mcps/` directory. Once integrated, these servers become available to Qwen as part of its tool ecosystem.

## Prerequisites

1. **Qwen Installation**: Ensure Qwen is properly installed on your system
2. **MCP Servers**: Have MCP server implementations in the `mcps/` directory with proper `server.py` entry points
3. **Python 3.6+**: Required for running the integration scripts

## Integration Process

### 1. Automatic Discovery and Integration

Run the integration command to automatically discover and register all MCP servers:

```bash
# Navigate to your project directory
cd /home/rana/Documents/agent-mcp-managnet-system

# Integrate all MCP servers with Qwen
./qwen-mcp-manager integrate
```

This will:
- Scan the `mcps/` directory for valid MCP server implementations
- Register each discovered server with Qwen's global configuration
- Set the first discovered server as the default

### 2. Verify Integration

Check that the servers were properly integrated:

```bash
# List all integrated MCP servers
./qwen-mcp-manager list
```

This will show output similar to:
```
MCP servers integrated with Qwen:
  - Meta Fastmcp Server [ENABLED] (DEFAULT)
    ID: meta-fastmcp-mcp-server
    Path: /home/rana/Documents/agent-mcp-managnet-system/mcps/meta-fastmcp-mcp-server
    Description: Automatically discovered MCP server: Meta Fastmcp

  - Fastmcp Docs Server [ENABLED]
    ID: fastmcp-docs-mcp-server
    Path: /home/rana/Documents/agent-mcp-managnet-system/mcps/fastmcp-docs-mcp-server
    Description: Automatically discovered MCP server: Fastmcp Docs
```

### 3. Configuration File

The integration creates or updates a configuration file at:
```
~/.config/qwen/settings.json
```

This file contains the registry of integrated MCP servers:

```json
{
  "mcpServers": [
    {
      "id": "meta-fastmcp-mcp-server",
      "name": "Meta Fastmcp Server",
      "path": "/home/rana/Documents/agent-mcp-managnet-system/mcps/meta-fastmcp-mcp-server",
      "entryPoint": "server.py",
      "enabled": true,
      "description": "Automatically discovered MCP server: Meta Fastmcp"
    }
  ],
  "defaultServer": "meta-fastmcp-mcp-server",
  "serverDiscovery": {
    "autoDiscover": true,
    "scanDirectories": [
      "/home/rana/Documents/agent-mcp-managnet-system/mcps"
    ]
  }
}
```

## Using Integrated MCP Servers with Qwen

Once integrated, your MCP servers are automatically available to Qwen:

### In Qwen Chat Interface

```qwen
# Qwen will automatically detect and use your MCP servers
# You can interact with them just like any other Qwen tools

# For example, if you have a documentation MCP server:
Can you help me understand how FastMCP works?

# Or if you have a meta MCP server:
What tools are available for managing agent systems?
```

### Programmatic Usage

In code that uses the Qwen SDK:

```python
from qwen import Qwen

# Qwen automatically loads integrated MCP servers
qwen = Qwen()

# Your MCP tools are now available alongside built-in tools
response = qwen.chat("List all available documentation sections")
```

## Managing Integrated MCP Servers

### Listing Current Integration

```bash
./qwen-mcp-manager list
```

Shows all currently integrated MCP servers with their status.

### Removing All Integrations

```bash
./qwen-mcp-manager remove-all
```

Removes all MCP server registrations from Qwen's configuration.

### Re-integrating Servers

After adding new MCP servers to the `mcps/` directory:

```bash
./qwen-mcp-manager integrate
```

Automatically discovers and integrates any new servers.

## MCP Server Requirements

For an MCP server to be automatically discovered and integrated, it must:

1. **Be in the `mcps/` directory**: Each server should have its own subdirectory
2. **Have a `server.py` entry point**: This is the main executable file for the server
3. **Implement the MCP specification**: Follow the Model Context Protocol standards
4. **Be runnable**: The server should start successfully when executed

Example directory structure:
```
mcps/
├── meta-fastmcp-mcp-server/
│   ├── server.py          # Entry point (required)
│   ├── requirements.txt   # Dependencies
│   └── ...                # Other server files
└── fastmcp-docs-mcp-server/
    ├── server.py          # Entry point (required)
    ├── requirements.txt   # Dependencies
    └── ...                # Other server files
```

## Advanced Configuration

### Manual Configuration

You can manually edit the Qwen configuration file at `~/.config/qwen/settings.json` to:

- Enable/disable specific MCP servers
- Change the default server
- Add custom descriptions
- Modify server paths

### Custom Server Names

The integration automatically generates clean names from directory names:
- `meta-fastmcp-mcp-server` → "Meta Fastmcp Server"
- `fastmcp-docs-mcp-server` → "Fastmcp Docs Server"

### Multiple Integration Directories

You can configure Qwen to scan additional directories by modifying the `serverDiscovery.scanDirectories` array in the settings file.

## Troubleshooting

### Servers Not Appearing in Qwen

1. **Verify integration**:
   ```bash
   ./qwen-mcp-manager list
   ```

2. **Check server paths**:
   Ensure the paths in the configuration are correct and accessible.

3. **Test server execution**:
   ```bash
   cd /path/to/mcp/server
   python server.py
   ```

### Configuration File Issues

1. **Backup existing configuration**:
   ```bash
   cp ~/.config/qwen/settings.json ~/.config/qwen/settings.json.backup
   ```

2. **Re-run integration**:
   ```bash
   ./qwen-mcp-manager integrate
   ```

### Qwen Not Recognizing MCP Servers

1. **Verify Qwen installation**: Ensure you're using a version that supports MCP
2. **Check Qwen logs**: Look for any errors related to MCP server loading
3. **Restart Qwen**: Sometimes a restart is needed after integration

## Best Practices

1. **Keep servers organized**: Use descriptive directory names in the `mcps/` directory
2. **Maintain server quality**: Ensure your MCP servers are stable and well-tested
3. **Document your servers**: Add README files explaining server capabilities
4. **Version control**: Keep your MCP servers in version control
5. **Regular updates**: Update server dependencies regularly
6. **Security considerations**: Review server permissions and access controls

## Integration Benefits

1. **Seamless tool availability**: Your MCP servers appear automatically in Qwen
2. **Centralized management**: Manage all MCP servers from one configuration
3. **Automatic discovery**: New servers are automatically detected
4. **Persistent configuration**: Integration survives Qwen restarts
5. **Flexible management**: Enable/disable servers as needed
6. **Enhanced functionality**: Extend Qwen's capabilities with custom tools

## Removing Integration

To completely remove all MCP server integrations:

```bash
# Remove all MCP server registrations
./qwen-mcp-manager remove-all

# Optionally remove the configuration file
rm ~/.config/qwen/settings.json
```

This will revert Qwen to its default state without your custom MCP servers.

## Conclusion

The Qwen MCP integration provides a powerful way to extend Qwen's capabilities with custom tools while maintaining simplicity in management. Once integrated, your MCP servers become first-class citizens in Qwen's tool ecosystem, available alongside built-in capabilities.

For more information about developing MCP servers, refer to the Model Context Protocol specification and the documentation for your specific MCP implementations.