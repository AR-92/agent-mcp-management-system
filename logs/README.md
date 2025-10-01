# MCP Logging System

This directory contains the comprehensive logging system for the MCP Manager.

## Overview

The logging system provides centralized logging with rotation, archiving, and management capabilities for all components of the MCP management system.

## Components

### Log Manager (`log_manager.py`)
- Centralized logging with automatic rotation
- Dedicated loggers for different components
- Archive old logs to prevent disk space issues
- Configurable through environment variables

### Log Utility (`log_util.py`)
- Command-line interface for log management
- View, search, and analyze log files
- Statistics and cleanup capabilities
- Follow logs in real-time

## Log Organization

- `manager/` - Logs for the main MCP manager process
- `mcp_servers/` - Individual logs for each MCP server
- `monitoring/` - Logs for the monitoring system
- `archive/` - Compressed archives of old logs (created automatically)

## Configuration

All logging settings are controlled through environment variables in the `.env` file:

```
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

## Usage

### Command Line Utilities

List all log files:
```bash
python logs/log_util.py list
```

View logs for a server:
```bash
python logs/log_util.py view <server-name>
```

Search logs for patterns:
```bash
python logs/log_util.py search -p "ERROR" -d 7
```

Show statistics:
```bash
python logs/log_util.py stats
```

Clean old logs:
```bash
python logs/log_util.py clean -k 14
```

## Features

- **Automatic Rotation**: Logs automatically rotate when they reach the configured size
- **Archiving**: Old logs are compressed and archived
- **Component-Specific**: Separate loggers for manager, servers, and monitoring
- **Configurable Retention**: Automatic cleanup of logs older than configured days
- **Search Capabilities**: Find specific patterns across all log files
- **Real-time Following**: Monitor logs in real-time like `tail -f`

## Integration

The logging system is automatically integrated with:
- MCP Manager (main operations)
- Server processes (individual server logs)
- Monitoring service (health and performance)
- All components use the same configuration