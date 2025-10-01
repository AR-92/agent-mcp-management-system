# MCP Server Manager

A centralized control system for managing all MCP servers in the agent-mcp-management-system project.

## Overview

The MCP Server Manager provides a unified interface to start, stop, restart, monitor, and view logs for all MCP servers in the project. It uses a single control script and a `.env` file for configuration.

## Features

- **Start/Stop/Restart**: Control individual servers or all servers at once
- **Status Monitoring**: Monitor running status, CPU, and memory usage of servers
- **Log Management**: View logs for any server with configurable line count
- **Centralized Configuration**: Manage all server settings from a single `.env` file
- **Process Management**: Properly handle process groups to avoid orphaned processes

## Requirements

- Python 3.8+
- `psutil` library
- `python-dotenv` library

Install dependencies:
```bash
pip install psutil python-dotenv
```

## Configuration

All configuration is managed through the `.env` file in the project root:

```bash
# Common settings
FASTMCP_HOST=127.0.0.1
FASTMCP_DEBUG=true
FASTMCP_BASE_PORT=8000  # Port assignment starts from this number and increments

# Docker/Deployment settings
DOCKER_MODE=false
CONTAINER_PREFIX=agent-mcp
NETWORK_NAME=agent-mcp-net
COMPOSE_FILE=docker-compose.yml

# Server management settings
START_ON_BOOT=false
SHUTDOWN_ON_EXIT=true
HEALTH_CHECK_ENABLED=true
HEALTH_CHECK_INTERVAL=30

# Container resource limits (for Docker)
CONTAINER_MEMORY_LIMIT=1g
CONTAINER_CPU_LIMIT=1.0

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_TO_FILE=true
LOG_MAX_SIZE=10MB
LOG_BACKUP_COUNT=5

# Security settings
META_ALLOWED_COMMANDS="ls,pwd,whoami,date,echo"
FASTMCP_DOCS_BASE_PATH="/home/rana/Documents/agent-mcp-managnet-system/docs/fastmcp_docs"

# Server-specific configurations
SERVER_STARTUP_TIMEOUT=60
SERVER_SHUTDOWN_TIMEOUT=30
SERVER_HEALTH_ENDPOINT=/health
SERVER_MONITOR_INTERVAL=10

# Environment settings
ENVIRONMENT=development
DEPLOYMENT_REGION=us-east-1
SERVICE_NAMESPACE=agent-mcp-services
```

## Professional Features

The MCP Manager includes several professional-grade features:

### Health Checks
```bash
# Check health of a specific server
python mcp_manager.py health-check meta-fastmcp-mcp-server

# Check health of all servers
python mcp_manager.py health-all

# Get system information
python mcp_manager.py system-info

# Export current configuration
python mcp_manager.py export-config
```

### Graceful Operations
```bash
# Perform graceful restart (waits for proper shutdown)
python mcp_manager.py restart meta-fastmcp-mcp-server --graceful
```

### Signal Handling
- Proper handling of SIGINT (Ctrl+C) and SIGTERM signals
- Graceful shutdown with configurable cleanup
- Process tracking and cleanup

### Advanced Status Display
- Detailed server uptime information
- Formatted status display with tree-like structure
- Summary statistics

## Usage

The manager script supports several commands:

### Start a server
```bash
python mcp_manager.py start <server-name>
# Examples (use the directory names from mcps/):
python mcp_manager.py start meta-fastmcp-mcp-server
python mcp_manager.py start fastmcp-docs-mcp-server
```

### Start all servers
```bash
python mcp_manager.py start-all
# or
python mcp_manager.py start all
```

### Stop a server
```bash
python mcp_manager.py stop <server-name>
```

### Stop all servers
```bash
python mcp_manager.py stop-all
# or
python mcp_manager.py stop all
```

### Restart a server
```bash
python mcp_manager.py restart <server-name>
```

### Restart all servers
```bash
python mcp_manager.py restart-all
# or
python mcp_manager.py restart all
```

### Check status of servers
```bash
python mcp_manager.py status
```

### View server logs
```bash
python mcp_manager.py logs <server-name> [-l lines-count]
# Examples:
python mcp_manager.py logs meta-fastmcp-mcp-server
python mcp_manager.py logs fastmcp-docs-mcp-server -l 50

# For advanced log management, use the log utility:
python logs/log_util.py list                    # List all log files
python logs/log_util.py view <server>          # View server logs
python logs/log_util.py search -p "ERROR"      # Search for errors
python logs/log_util.py stats                  # Show log statistics
```

## Server Discovery

The manager dynamically discovers all MCP servers by scanning the `mcps/` directory. Each subdirectory that contains a `server.py` file is treated as an MCP server. Server names are derived from the directory names, with common suffixes like `-mcp-server` automatically removed for cleaner display names. The servers are automatically assigned ports sequentially starting from `FASTMCP_BASE_PORT`.

## Logging System

The manager includes a comprehensive logging system with:

### Centralized Logging
- Dedicated loggers for manager, servers, and monitoring components
- Automatic log rotation based on size and time
- Archiving of old logs to prevent disk space issues
- Configurable log levels and formats

### Log Management Commands
```bash
# List all available logs
python logs/log_util.py list

# View logs for a specific server
python logs/log_util.py view meta-fastmcp-mcp-server

# View last N lines
python logs/log_util.py view meta-fastmcp-mcp-server -n 100

# Search logs for a pattern
python logs/log_util.py search -p "ERROR" -d 7

# Search for pattern in specific server logs
python logs/log_util.py search -p "timeout" -d 3 -s meta-fastmcp-mcp-server

# Show log statistics
python logs/log_util.py stats

# Clean old logs (keep last 14 days)
python logs/log_util.py clean -k 14
```

### Log Configuration
All logging settings are controlled through environment variables:
```bash
# Basic logging settings
LOG_LEVEL=INFO
LOG_FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_TO_FILE=true
LOG_TO_CONSOLE=true

# Rotation settings
LOG_MAX_SIZE=10MB
LOG_BACKUP_COUNT=5
LOG_ROTATION_ENABLED=true

# Retention settings
LOG_RETENTION_DAYS=30
```

### Log Organization
- Server-specific logs in `logs/mcp_servers/`
- Manager logs in `logs/manager/`
- Monitoring logs in `logs/monitoring/`
- Automatic archiving of old logs with compression

## Monitoring System

The manager includes a comprehensive monitoring system that tracks server health, performance, and availability:

### Real-time Monitoring
```bash
# Start the monitoring console
python mcp_manager.py monitor

# Check current metrics for a server
python mcp_manager.py metrics meta-fastmcp-mcp-server

# Check current status for all servers
python mcp_manager.py metrics
```

### Dashboard
The monitoring dashboard provides visual metrics:
```bash
# View current status
python monitoring/dashboard.py status

# View metrics for specific server
python monitoring/dashboard.py metrics meta-fastmcp-mcp-server

# Watch real-time updates
python monitoring/dashboard.py watch
```

### Monitoring Configuration
All monitoring settings are controlled through environment variables:
```bash
# General monitoring settings
MONITORING_ENABLED=true
MONITORING_INTERVAL=10  # seconds between checks
HEALTH_CHECK_TIMEOUT=5  # seconds for health check timeout

# Alert settings
ALERT_ON_FAILURE=true
ALERT_EMAIL=""
ALERT_WEBHOOK=""

# Performance thresholds
CPU_THRESHOLD=80      # percentage
MEMORY_THRESHOLD=85   # percentage
RESPONSE_TIME_THRESHOLD=5000  # milliseconds

# Metrics retention
METRICS_RETENTION_DAYS=30
```

The monitoring system automatically:
- Tracks CPU and memory usage
- Performs health checks on server endpoints
- Monitors response times
- Generates alerts when thresholds are exceeded
- Stores metrics in JSON format for analysis
- Provides historical data for trend analysis

## Docker Integration

The system supports Docker deployments through the following environment variables:
- `DOCKER_MODE`: Set to `true` to enable Docker-specific behavior
- `CONTAINER_PREFIX`: Prefix for Docker container names
- `NETWORK_NAME`: Docker network name
- `CONTAINER_MEMORY_LIMIT`: Memory limit for containers (e.g., "1g")
- `CONTAINER_CPU_LIMIT`: CPU limit for containers (e.g., "1.0")

When `DOCKER_MODE=true`, the manager will handle servers as Docker containers instead of direct processes.

## Deployment Configuration

For deployment scenarios:
- Set `START_ON_BOOT=true` to automatically start all servers when the manager starts
- Set `ENVIRONMENT` to `production`, `staging`, or `development` for environment-specific behavior
- Configure resource limits with `CONTAINER_MEMORY_LIMIT` and `CONTAINER_CPU_LIMIT`
- Adjust timeouts with `SERVER_STARTUP_TIMEOUT` and `SERVER_SHUTDOWN_TIMEOUT`
- Enable monitoring with `MONITORING_ENABLED=true`
- Set up alerting with `ALERT_ON_FAILURE=true`

## Process Management

- The manager tracks process IDs in `logs/mcp_manager_pids.json`
- All processes are started in new process groups to allow proper signal handling
- Stopped processes are removed from the tracking file

## Troubleshooting

### Server won't start
- Check that the server directory exists and contains the required files
- Check the logs in the `logs/` directory for error messages
- Verify that the configured port is available

### Commands not working
- Make sure you're running the commands from the project root directory
- Ensure `python-dotenv` and `psutil` libraries are installed

## Project Structure

```
agent-mcp-management-system/
├── mcp_manager.py          # The central control script
├── .env                   # Centralized configuration
├── mcps/                  # MCP server implementations
│   ├── meta-fastmcp-mcp-server/
│   ├── fastmcp-docs-mcp-server/
│   └── strandagents-mcp-server/
└── logs/                  # Log files and process tracking
    ├── meta-fastmcp.log
    ├── fastmcp-docs.log
    ├── strandagents.log
    └── mcp_manager_pids.json
```