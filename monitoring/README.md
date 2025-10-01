# MCP Server Monitoring System

This document provides an overview of the comprehensive monitoring system implemented for MCP servers.

## Overview

The monitoring system provides real-time health checks, performance metrics, and alerting for all MCP servers managed by the system. It automatically tracks the status, resource usage, and response times of all servers in the `mcps/` directory.

## Components

### 1. Monitor Service (`monitor_service.py`)
- Real-time monitoring of server health and performance
- CPU and memory usage tracking
- Health endpoint checking
- Response time monitoring
- Alert generation when thresholds are exceeded
- Metrics storage in JSON format
- Configurable through environment variables

### 2. Dashboard (`dashboard.py`)
- Visual representation of server status
- Real-time updates with "watch" mode
- Historical metrics viewing
- Command-line interface for monitoring

### 3. Report Generator (`report.py`)
- Generate summary reports of server performance
- Configurable time periods (default: last 24 hours)
- Uptime calculations and statistics
- Alert summaries

## Configuration

The monitoring system is controlled through environment variables in the `.env` file:

```
# Enable/disable monitoring
MONITORING_ENABLED=true

# Monitoring intervals
MONITORING_INTERVAL=10  # seconds between checks
HEALTH_CHECK_TIMEOUT=5  # timeout for health checks

# Performance thresholds
CPU_THRESHOLD=80        # percentage
MEMORY_THRESHOLD=85     # percentage
RESPONSE_TIME_THRESHOLD=5000  # milliseconds

# Alert settings
ALERT_ON_FAILURE=true
ALERT_EMAIL=""
ALERT_WEBHOOK=""
```

## Usage

### Real-time Monitoring
```bash
# Start monitoring console
python mcp_manager.py monitor

# Check current metrics
python mcp_manager.py metrics
python mcp_manager.py metrics <server-name>

# Monitor with dashboard
python monitoring/dashboard.py watch
python monitoring/dashboard.py status
python monitoring/dashboard.py metrics <server-name>

# Generate reports
python monitoring/report.py --hours 24
```

## Data Storage

- Metrics are stored in `monitoring/data/<server-name>_metrics.json`
- Each server has its own metrics file
- Files are rotated to prevent excessive growth
- Data includes timestamp, CPU, memory, response time, health status, and alerts

## Features

- **Automatic Discovery**: Monitors all servers in the mcps directory
- **Health Checks**: Verifies server endpoints are responding
- **Performance Tracking**: Monitors CPU and memory usage
- **Alert System**: Generates alerts when thresholds are exceeded
- **Historical Data**: Stores metrics for trend analysis
- **Real-time Updates**: Live dashboard with refresh capabilities
- **Configurable Thresholds**: Customizable performance limits
- **Reporting**: Summary reports for analysis

## Integration

The monitoring integrates seamlessly with the main MCP manager:
- Starts automatically when the manager starts (if enabled)
- Uses the same server discovery mechanism
- Shares configuration through the same .env file
- Provides status information through the same interface