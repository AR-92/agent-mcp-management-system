# Qwen MCP Manager

This directory contains tools for integrating the Agent MCP Management System with Qwen's configuration system.

## Overview

The Qwen MCP Manager automatically discovers MCP servers in the `mcps/` directory and integrates them with Qwen's global configuration system. This enables seamless use of custom MCP servers with Qwen.

## Features

- **Automatic Discovery**: Scans the `mcps/` directory for MCP server implementations
- **Qwen Integration**: Adds discovered MCPs to Qwen's global configuration
- **Configuration Management**: Manages enabling/disabling MCP servers
- **Status Tracking**: Shows currently integrated MCP servers

## Scripts

### qwen_mcp_manager.py

Python script that handles all MCP integration logic:

```bash
# Integrate all MCPs with Qwen
python scripts/qwen_mcp_manager.py integrate

# List currently integrated MCPs
python scripts/qwen_mcp_manager.py list

# Remove all MCPs from Qwen
python scripts/qwen_mcp_manager.py remove-all

# Show Qwen config file path
python scripts/qwen_mcp_manager.py config-path
```

### qwen-mcp-manager.sh

Convenient shell script wrapper:

```bash
# Integrate all MCPs with Qwen
./scripts/qwen-mcp-manager.sh integrate

# List currently integrated MCPs
./scripts/qwen-mcp-manager.sh list
```

## Usage

1. **Integration**:
   ```bash
   ./scripts/qwen-mcp-manager.sh integrate
   ```
   This will scan for MCP servers and add them to Qwen's configuration.

2. **Listing**:
   ```bash
   ./scripts/qwen-mcp-manager.sh list
   ```
   Shows all currently integrated MCP servers.

3. **Removal**:
   ```bash
   ./scripts/qwen-mcp-manager.sh remove-all
   ```
   Removes all MCP servers from Qwen's configuration.

## Configuration

The integration creates or updates a configuration file at:
```
~/.config/qwen/settings.json
```

This file contains the list of integrated MCP servers that Qwen can use.

## Requirements

- Python 3.6+
- Qwen Code installation
- MCP servers in the `mcps/` directory with `server.py` entry points

## How It Works

1. **Discovery**: Scans the `mcps/` directory for subdirectories containing `server.py`
2. **Integration**: Adds discovered servers to Qwen's global configuration
3. **Activation**: Qwen automatically recognizes and can use these MCP servers
4. **Management**: Allows enabling/disabling specific servers as needed

## Notes

- The integration is non-destructive and preserves existing Qwen settings
- MCP servers are identified by their directory names
- New MCP servers are automatically detected on subsequent runs
- Configuration changes take effect immediately in Qwen