# MCP Server Manager (mcp_manager.py) - User Guide

The `mcp_manager.py` file is a comprehensive management tool for controlling all MCP servers in the agent-mcp-management-system project. Here's how to use it:

## Basic Usage

```bash
python mcp_manager.py [action] [server_name] [options]
```

## Available Actions

### 1. Server Control
- `start [server_name]` - Start a specific MCP server
- `stop [server_name]` - Stop a specific MCP server
- `restart [server_name]` - Restart a specific MCP server
- `start-all` - Start all discovered MCP servers
- `stop-all` - Stop all MCP servers
- `restart-all` - Restart all MCP servers

### 2. Status & Monitoring
- `status` - Show status of all MCP servers (running, stopped, CPU/memory usage, uptime)
- `health-check [server_name]` - Check health of a specific server
- `health-all` - Check health of all servers
- `monitor` - Start the monitoring console
- `metrics [server_name]` - View metrics for a specific server or all servers

### 3. Logs & Information
- `logs [server_name] -l [lines]` - Display logs for a specific server (default: last 20 lines)
- `system-info` - Show system information (CPU, memory, disk usage)
- `export-config` - Show current configuration

## Common Usage Examples

### Check Status of All Servers
```bash
python mcp_manager.py status
```

### Start a Specific Server
```bash
python mcp_manager.py start fastmcp-docs-mcp-server
```

### Start All Servers
```bash
python mcp_manager.py start-all
```

### View Logs for a Server
```bash
python mcp_manager.py logs fastmcp-docs-mcp-server -l 50
```

### Stop a Specific Server
```bash
python mcp_manager.py stop fastmcp-docs-mcp-server
```

### Restart All Servers
```bash
python mcp_manager.py restart-all
```

### Check Health of All Servers
```bash
python mcp_manager.py health-all
```

## Configuration

The manager reads configuration from environment variables in the `.env` file:

```bash
# .env file
FASTMCP_HOST=127.0.0.1          # Host for MCP servers
FASTMCP_BASE_PORT=8000          # Base port (servers get sequential ports: 8001, 8002, etc.)
START_ON_BOOT=false             # Start servers automatically on boot
SHUTDOWN_ON_EXIT=true           # Shutdown servers when manager exits
HEALTH_CHECK_ENABLED=true       # Enable health checks
HEALTH_CHECK_INTERVAL=30        # Health check interval in seconds
ENVIRONMENT=development         # Environment (development, production)
LOG_TO_FILE=true                # Log to file or console
SERVER_STARTUP_TIMEOUT=60       # Server startup timeout in seconds
SERVER_SHUTDOWN_TIMEOUT=30      # Server shutdown timeout in seconds
```

## Server Discovery

The manager automatically discovers MCP servers in the `mcps/` directory by:
- Looking for subdirectories containing a `server.py` file
- Assigning sequential ports starting from the base port
- Creating log files in the `logs/` directory

## Docker Mode

The manager supports Docker mode with these environment variables:
```bash
DOCKER_MODE=false                # Enable/disable Docker mode
CONTAINER_PREFIX=agent-mcp       # Prefix for container names
NETWORK_NAME=agent-mcp-net       # Docker network name
COMPOSE_FILE=docker-compose.yml  # Docker Compose file to use
CONTAINER_MEMORY_LIMIT=1g        # Memory limit per container
CONTAINER_CPU_LIMIT=1.0          # CPU limit per container
```

## Graceful Operations

You can perform graceful restarts that wait for proper shutdown:
```bash
python mcp_manager.py restart fastmcp-docs-mcp-server --graceful
```

## Features

- **Automatic Server Discovery**: Automatically finds and manages all MCP servers
- **Process Management**: Start, stop, restart processes with proper PID tracking
- **Health Monitoring**: Check if servers are running and responsive
- **Resource Monitoring**: Track CPU and memory usage
- **Log Management**: View and manage logs for all servers
- **Port Management**: Automatically assign ports to avoid conflicts
- **Graceful Shutdown**: Properly terminate processes
- **System Information**: Monitor system resources
- **Configuration Export**: View current configuration
- **Environment Support**: Different configurations for dev/prod
- **Signal Handling**: Graceful shutdown on system signals

## Log Files

The manager creates log files in the `logs/` directory:
- `mcp_manager_pids.json` - Stores process IDs for running servers
- `[server_name].log` - Individual log files for each server
- `manager.log` - Main manager logs (if logging is enabled)

## Auto-start on Boot

If `START_ON_BOOT=true` in the .env file, all servers will automatically start when the manager is launched. The manager will also automatically shutdown all servers when it exits if `SHUTDOWN_ON_EXIT=true`.

This tool provides a centralized, professional way to manage all MCP servers in your system with comprehensive monitoring and control capabilities.