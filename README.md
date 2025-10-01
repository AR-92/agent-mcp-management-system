# Agent MCP Management System

This repository contains the Agent MCP (Multi-Component Protocol) Management System.

## MCP Server Management

This project now includes a professional centralized management system for controlling all MCP servers with a single interface:

- **Dynamic Discovery**: Automatically discovers all MCP servers in the mcps/ directory
- **Start/Stop/Restart**: Control individual or all servers at once
- **Status Monitoring**: Monitor running status, CPU, memory, and uptime
- **Health Checks**: Perform detailed health checks on individual or all servers
- **Log Management**: View logs for any server with advanced log utilities
- **System Information**: Get detailed system resource information
- **Configuration Export**: Export current configuration settings
- **Graceful Operations**: Support for graceful restarts with proper shutdown handling
- **Signal Handling**: Proper signal handling for graceful shutdown on interrupts
- **Centralized Configuration**: Manage all settings from a single `.env` file with port management
- **Docker Integration**: Full support for Docker deployments with resource limits and container management
- **Environment Control**: Different configurations for development, staging, and production
- **Comprehensive Monitoring**: Real-time health checks, performance metrics, and alerting
- **Metrics Dashboard**: Visual monitoring dashboard with real-time updates

### Quick Start with Management System

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure your settings in `.env`

3. Start all servers:
   ```bash
   python mcp_manager.py start-all
   ```

4. Check status:
   ```bash
   python mcp_manager.py status
   ```

5. View logs:
   ```bash
   python mcp_manager.py logs meta-fastmcp-mcp-server
   ```

6. Monitor servers:
   ```bash
   python mcp_manager.py monitor
   # or
   python monitoring/dashboard.py watch
   ```

For full usage instructions, see [MANAGER-README.md](MANAGER-README.md).

## Documentation

- [Complete Setup Guide](RUNNING.md) - Detailed instructions for installation, configuration, and operation
- [Quick Start Guide](QUICKSTART.md) - Immediate getting started instructions
- [Manager Documentation](MANAGER-README.md) - MCP manager specific documentation
- [Monitoring Documentation](monitoring/README.md) - Monitoring system documentation
- [Logging Documentation](logs/README.md) - Logging system documentation
- [Qwen Integration Guide](QWEN_INTEGRATION.md) - Instructions for integrating with Qwen's global configuration

### Docker Deployment

For Docker deployments, use the `docker.env` file with appropriate settings:

```bash
# Example for Docker deployment
DOCKER_MODE=true
START_ON_BOOT=true
ENVIRONMENT=production
CONTAINER_MEMORY_LIMIT=2g
```

## Project Structure

- [Documentation](./docs/) - Project documentation
- [MCP Protocols](./mcps/) - MCP protocol implementations (automatically discovered)
- [Servers](./servers/) - Server implementations
- [Agents](./agents/) - Agent implementations
- [Tests](./tests/) - Test files
- [Logs](./logs/) - **NEW: Comprehensive log management including:**
  - [Log Manager](logs/log_manager.py) - Centralized logging with rotation and archiving
  - [Log Utility](logs/log_util.py) - Command-line tool for log management
  - [Server Logs](logs/mcp_servers/) - Individual server logs
  - [Manager Logs](logs/manager/) - Manager application logs
  - [Monitoring Logs](logs/monitoring/) - Monitoring system logs
- [Monitoring](./monitoring/) - **NEW: Comprehensive monitoring system including:**
  - [Monitoring Service](monitoring/monitor_service.py) - Real-time server monitoring
  - [Dashboard](monitoring/dashboard.py) - Visual metrics dashboard
  - [Configuration](monitoring/monitoring_config.env) - Monitoring settings
  - [Data Directory](monitoring/data/) - Stored metrics and logs
- [Scripts](./scripts/) - **NEW: Utility scripts including:**
  - [Qwen MCP Manager](scripts/qwen_mcp_manager.py) - Python script for Qwen integration
  - [Shell Wrapper](scripts/qwen-mcp-manager.sh) - Convenient shell script wrapper
  - [Qwen Integration Documentation](scripts/README.md) - Documentation for Qwen integration
- [Qwen Integration](QWEN_INTEGRATION.md) - Complete guide for integrating with Qwen
- [MCP Manager](mcp_manager.py) - Centralized control script with dynamic discovery
- [Configuration](.env) - Centralized configuration file
- [Docker Config](docker.env) - Docker-specific configuration template

For a detailed breakdown of the project structure, see [SUBSYSTEMS.md](./SUBSYSTEMS.md).