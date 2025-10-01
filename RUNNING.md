# MCP Server Manager - Complete Setup and Operations Guide

This document provides comprehensive instructions for setting up and running the MCP Server Manager system, including all features, configurations, and operational procedures.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Starting the System](#starting-the-system)
5. [Managing MCP Servers](#managing-mcp-servers)
6. [Monitoring and Health Checks](#monitoring-and-health-checks)
7. [Logging and Troubleshooting](#logging-and-troubleshooting)
8. [Docker Deployment](#docker-deployment)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- Python 3.8 or higher
- Linux, macOS, or Windows with WSL2
- Minimum 4GB RAM (8GB+ recommended)
- 10GB+ free disk space
- Network access for external dependencies

### Software Dependencies
- Python package manager (pip)
- Git (for cloning/fetching)
- Docker and Docker Compose (optional, for containerized deployments)

## Installation

### 1. Cloning the Repository
```bash
git clone <repository-url>
cd agent-mcp-managnet-system
```

### 2. Setting up Python Environment
```bash
# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required dependencies
pip install -r requirements.txt
```

### 3. Verify Dependencies
```bash
python -c "import psutil, dotenv, requests; print('All dependencies installed successfully')"
```

## Configuration

### 1. Environment Configuration
The system uses a comprehensive `.env` file for all configurations:

```bash
# Copy the default configuration
cp .env.example .env  # If provided
# or create manually
```

### 2. Core Configuration Options
Edit the `.env` file with your specific settings:

```bash
# Basic Network Settings
FASTMCP_HOST=0.0.0.0
FASTMCP_DEBUG=true
FASTMCP_BASE_PORT=8000

# Server Management
START_ON_BOOT=false
SHUTDOWN_ON_EXIT=true
SERVER_STARTUP_TIMEOUT=60
SERVER_SHUTDOWN_TIMEOUT=30

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_TO_FILE=true
LOG_TO_CONSOLE=true
LOG_MAX_SIZE=10MB
LOG_BACKUP_COUNT=5
LOG_RETENTION_DAYS=30

# Monitoring Settings
MONITORING_ENABLED=true
MONITORING_INTERVAL=10
HEALTH_CHECK_ENABLED=true
HEALTH_CHECK_TIMEOUT=5

# Performance Thresholds
CPU_THRESHOLD=80
MEMORY_THRESHOLD=85
RESPONSE_TIME_THRESHOLD=5000

# Environment
ENVIRONMENT=development
```

### 3. Server-Specific Configuration
For each MCP server in the `mcps/` directory, ensure:
- Server has a `server.py` file
- Server has valid configuration in its directory
- Required dependencies are installed

## Starting the System

### 1. Initial System Check
```bash
# Verify all components are available
python mcp_manager.py status

# This will show discovered servers and their current status
```

### 2. Starting Individual Servers
```bash
# Start a specific server
python mcp_manager.py start meta-fastmcp-mcp-server

# Start with specific port and configuration (from env file)
python mcp_manager.py start fastmcp-docs-mcp-server
```

### 3. Starting All Servers
```bash
# Start all discovered servers
python mcp_manager.py start-all

# Or using the start command with 'all'
python mcp_manager.py start all
```

### 4. Auto-start Configuration
To automatically start servers on system boot:
1. Set `START_ON_BOOT=true` in your `.env` file
2. The servers will start automatically when the manager is initialized

## Managing MCP Servers

### 1. Server Lifecycle Management

#### Starting Servers
```bash
# Start a specific server
python mcp_manager.py start <server-name>

# Examples:
python mcp_manager.py start meta-fastmcp-mcp-server
python mcp_manager.py start fastmcp-docs-mcp-server
```

#### Stopping Servers
```bash
# Stop a specific server
python mcp_manager.py stop <server-name>

# Stop all servers
python mcp_manager.py stop-all
# or
python mcp_manager.py stop all
```

#### Restarting Servers
```bash
# Restart a specific server
python mcp_manager.py restart <server-name>

# Restart with graceful shutdown
python mcp_manager.py restart <server-name> --graceful

# Restart all servers
python mcp_manager.py restart-all
```

### 2. Server Status and Information

#### Checking Status
```bash
# View status of all servers
python mcp_manager.py status

# The output will show:
# - Server name and status
# - Port and host information
# - Uptime
# - CPU and memory usage (if running)
# - Process ID
```

#### Health Checks
```bash
# Check health of a specific server
python mcp_manager.py health-check <server-name>

# Check health of all servers
python mcp_manager.py health-all

# Example output:
# Health of meta-fastmcp-mcp-server: {
#   "status": "running",
#   "pid": 12345,
#   "cpu_percent": 12.3,
#   "memory_percent": 45.6,
#   "uptime_seconds": 3600
# }
```

#### System Information
```bash
# Get comprehensive system information
python mcp_manager.py system-info

# Shows platform, Python version, CPU, memory, disk usage, etc.
```

#### Configuration Export
```bash
# Export current configuration
python mcp_manager.py export-config

# Useful for backup or deployment verification
```

### 3. Server Discovery
The system automatically discovers all MCP servers in the `mcps/` directory:
- Any subdirectory with a `server.py` file is treated as an MCP server
- Servers are assigned ports sequentially starting from `FASTMCP_BASE_PORT`
- Server names are derived from directory names with common suffixes cleaned

## Monitoring and Health Checks

### 1. Real-time Monitoring
```bash
# Start the monitoring console
python mcp_manager.py monitor

# This will continuously monitor all servers and display real-time metrics
```

### 2. Metrics Access
```bash
# View current metrics for a server
python mcp_manager.py metrics <server-name>

# View overall system metrics
python mcp_manager.py metrics
```

### 3. Monitoring Dashboard
```bash
# View status dashboard
python monitoring/dashboard.py status

# Monitor real-time updates
python monitoring/dashboard.py watch

# View specific server metrics
python monitoring/dashboard.py metrics <server-name>
```

### 4. Metrics Reporting
```bash
# Generate comprehensive report
python monitoring/report.py --hours 24

# View report for last 7 days
python monitoring/report.py
```

## Logging and Troubleshooting

### 1. Log Management
```bash
# View logs for a specific server
python mcp_manager.py logs <server-name>

# View last N lines
python mcp_manager.py logs <server-name> -l 50

# Use the advanced log utility
python logs/log_util.py list                    # List all log files
python logs/log_util.py view <server>          # View server logs
python logs/log_util.py search -p "ERROR"      # Search for errors
python logs/log_util.py search -p "ERROR" -d 7 # Search in last 7 days
python logs/log_util.py stats                  # Show log statistics
python logs/log_util.py clean -k 14            # Clean logs older than 14 days
```

### 2. Log Directory Structure
- `logs/manager/` - Main manager application logs
- `logs/mcp_servers/` - Individual server logs
- `logs/monitoring/` - Monitoring system logs
- `logs/archive/` - Compressed archives of old logs

### 3. Log Rotation and Retention
- Logs are automatically rotated when they reach `LOG_MAX_SIZE`
- Up to `LOG_BACKUP_COUNT` old files are kept
- Logs older than `LOG_RETENTION_DAYS` are archived/compressed
- A background daemon manages cleanup automatically

## Docker Deployment

### 1. Docker Configuration
Set up Docker-specific environment variables:

```bash
## In your .env file:
DOCKER_MODE=true
CONTAINER_PREFIX=agent-mcp
NETWORK_NAME=agent-mcp-net
COMPOSE_FILE=docker-compose.yml
CONTAINER_MEMORY_LIMIT=2g
CONTAINER_CPU_LIMIT=2.0
```

### 2. Building Docker Images
For each MCP server that supports Docker:

```bash
# Navigate to the specific server directory
cd mcps/meta-fastmcp-mcp-server
docker build -t meta-fastmcp-server .

cd mcps/fastmcp-docs-mcp-server
docker build -t fastmcp-docs-server .
```

### 3. Running with Docker
When `DOCKER_MODE=true`, the system will automatically:
- Start servers as Docker containers instead of processes
- Apply resource limits
- Use the configured network
- Apply the container prefix

### 4. Production Docker Environment
Use the `docker.env` file for production settings:

```bash
# Example docker.env
FASTMCP_HOST=0.0.0.0
FASTMCP_DEBUG=false
FASTMCP_BASE_PORT=8000

DOCKER_MODE=true
START_ON_BOOT=true
ENVIRONMENT=production
CONTAINER_MEMORY_LIMIT=2g
CONTAINER_CPU_LIMIT=2.0

LOG_LEVEL=WARNING
LOG_TO_FILE=true
LOG_RETENTION_DAYS=90
```

## Best Practices

### 1. Security
- Never commit sensitive API keys to version control
- Use environment variables for sensitive data
- Regularly rotate API keys
- Limit system resources to prevent abuse
- Use a firewall to restrict access to management ports

### 2. Performance
- Monitor resource usage regularly
- Set appropriate CPU and memory limits
- Use load balancing for high-traffic deployments
- Implement proper caching strategies

### 3. Reliability
- Set up health checks and monitoring
- Use the health check endpoints regularly
- Implement proper backup strategies
- Test failover procedures regularly
- Maintain system health reports

### 4. Maintenance
- Regular log rotation and cleanup
- Update dependencies regularly
- Monitor for security vulnerabilities
- Keep systems patched and updated
- Schedule regular maintenance windows

## Troubleshooting

### 1. Common Issues and Solutions

#### Server Won't Start
- **Check logs**: Look in the appropriate log directory for error messages
- **Check port availability**: Ensure the configured port isn't used by another process
- **Check dependencies**: Verify all required Python packages are installed
- **Verify permissions**: Ensure the system has permissions to start processes

#### Server Stops Unexpectedly
- **Check logs**: Look for error messages that caused the termination
- **Check resource limits**: Verify system has enough memory/CPU
- **Check timeouts**: Adjust `SERVER_STARTUP_TIMEOUT` if needed
- **Check configuration**: Ensure the server configuration is valid

#### Monitoring Not Working
- **Check monitoring configuration**: Verify `MONITORING_ENABLED=true`
- **Check port listening**: Ensure server is listening on the configured port
- **Check network**: Verify network connectivity to health endpoints

#### Log Issues
- **Check permissions**: Ensure logs directory is writable
- **Check disk space**: Verify sufficient disk space for logs
- **Check rotation**: Verify log rotation is configured properly

### 2. Diagnostic Commands

```bash
# Check system status
python mcp_manager.py status

# Perform health checks
python mcp_manager.py health-all

# Get system information
python mcp_manager.py system-info

# Export configuration for review
python mcp_manager.py export-config

# Check detailed server health
python mcp_manager.py health-check <server-name>
```

### 3. Emergency Procedures

#### Immediate Server Restart
```bash
# Stop all servers
python mcp_manager.py stop-all

# Start all servers
python mcp_manager.py start-all
```

#### Configuration Reset
1. Backup current `.env` file
2. Restore from known good configuration
3. Restart the manager system

#### Log Cleanup (Emergency)
```bash
# Clean old logs to free space
python logs/log_util.py clean -k 1

# Or manually remove old logs
find logs/ -name "*.log" -atime +7 -delete
```

### 4. Monitoring Critical Issues
- High CPU usage (>80%)
- High memory usage (>85%) 
- Server response times >5000ms
- Server not responding to health checks
- Process crashes or unexpected exits
- Log file sizes growing unexpectedly

## Operational Checklist

### Daily Operations
- [ ] Check server status: `python mcp_manager.py status`
- [ ] Review system health: `python mcp_manager.py health-all`
- [ ] Check for errors in logs
- [ ] Verify monitoring is active

### Weekly Operations
- [ ] Review performance reports
- [ ] Check log sizes and rotation
- [ ] Verify backup procedures
- [ ] Update dependencies if needed

### Monthly Operations
- [ ] Comprehensive system health check
- [ ] Performance trend analysis
- [ ] Security audit
- [ ] Configuration review

### Quarterly Operations
- [ ] Disaster recovery testing
- [ ] Performance optimization
- [ ] Capacity planning
- [ ] Documentation review

This comprehensive guide should enable you to successfully run and maintain the MCP Server Manager system in any environment.