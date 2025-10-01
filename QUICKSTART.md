# Quick Start Guide - MCP Server Manager

This guide provides quick instructions to get the MCP Server Manager running immediately.

## Prerequisites
- Python 3.8+
- pip package manager

## Installation Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# The system uses default settings from .env
# Review and modify if needed:
cat .env  # View current settings
```

### 3. Verify Setup
```bash
# Check discovered servers
python mcp_manager.py status
```

## Quick Operations

### Start All Servers
```bash
python mcp_manager.py start-all
```

### Check Status
```bash
python mcp_manager.py status
```

### View Live Metrics
```bash
# In one terminal - start monitoring
python mcp_manager.py monitor

# In another terminal - start servers
python mcp_manager.py start-all
```

### Stop All Servers
```bash
python mcp_manager.py stop-all
```

## Essential Commands

| Command | Description |
|---------|-------------|
| `python mcp_manager.py status` | Show all server status |
| `python mcp_manager.py start-all` | Start all servers |
| `python mcp_manager.py stop-all` | Stop all servers |
| `python mcp_manager.py restart-all` | Restart all servers |
| `python mcp_manager.py logs <server>` | View server logs |
| `python mcp_manager.py health-all` | Check all server health |
| `python mcp_manager.py system-info` | Show system information |

## Default Configuration

- **Base Port**: 8000 (servers get 8000, 8001, 8002, etc.)
- **Host**: 127.0.0.1
- **Environment**: development
- **Monitoring**: enabled
- **Auto-start on boot**: false
- **Log rotation**: enabled

## Troubleshooting Quick Fixes

### Server Won't Start
```bash
# Check what servers are discovered
python mcp_manager.py status

# Check specific server logs
python mcp_manager.py logs <server-name>

# Try starting a specific server
python mcp_manager.py start <server-name>
```

### Check System Health
```bash
python mcp_manager.py system-info
python mcp_manager.py health-all
```

### View Recent Logs
```bash
python logs/log_util.py list
python logs/log_util.py stats
```

## Ready to Run Examples

### Scenario 1: Start and Monitor
```bash
# Start all servers
python mcp_manager.py start-all

# Check status
python mcp_manager.py status

# View logs for first server
python mcp_manager.py logs meta-fastmcp-mcp-server

# Check health
python mcp_manager.py health-all
```

### Scenario 2: Development Cycle
```bash
# Start monitoring in background
python mcp_manager.py monitor &

# Work with servers
python mcp_manager.py start-all
python mcp_manager.py status

# Stop when done
python mcp_manager.py stop-all
```

### Scenario 3: Maintenance
```bash
# Check system info
python mcp_manager.py system-info

# Get current configuration
python mcp_manager.py export-config

# Clean old logs (keep last 14 days)
python logs/log_util.py clean -k 14

# Check all health
python mcp_manager.py health-all
```

For detailed configuration and advanced operations, see [RUNNING.md](RUNNING.md).