# MCP Server Configuration Guide

This guide explains how to configure MCP servers for different deployment scenarios.

## Environment Variables

MCP servers can be configured using environment variables:

### Basic Configuration
- `MCP_PORT`: Port number for the server (default: 3000)
- `MCP_HOST`: Host address to bind to (default: localhost)
- `MCP_PROTOCOL_VERSION`: Protocol version to use (default: 1.0)
- `MCP_MAX_CONNECTIONS`: Maximum concurrent connections (default: 100)
- `MCP_TIMEOUT`: Connection timeout in milliseconds (default: 30000)

### Security Configuration
- `MCP_ENABLE_TLS`: Enable TLS encryption (default: false)
- `MCP_TLS_CERT_PATH`: Path to TLS certificate file
- `MCP_TLS_KEY_PATH`: Path to TLS private key file
- `MCP_AUTH_REQUIRED`: Require authentication (default: true)
- `MCP_RATE_LIMIT`: Request rate limit per minute (default: 1000)

### Performance Configuration
- `MCP_BUFFER_SIZE`: Size of message buffer in bytes (default: 65536)
- `MCP_MESSAGE_QUEUE_SIZE`: Size of message queue (default: 1000)
- `MCP_WORKER_THREADS`: Number of worker threads (default: CPU cores)

## Configuration File

Alternatively, you can configure the server using a configuration file:

```json
{
  "server": {
    "port": 3000,
    "host": "0.0.0.0",
    "protocolVersion": "1.0"
  },
  "security": {
    "tls": {
      "enabled": true,
      "certPath": "/path/to/cert.pem",
      "keyPath": "/path/to/key.pem"
    },
    "authentication": {
      "required": true,
      "providers": ["api-key", "oauth"]
    },
    "rateLimiting": {
      "requestsPerMinute": 1000
    }
  },
  "performance": {
    "maxConnections": 500,
    "connectionTimeout": 30000,
    "bufferSize": 65536,
    "messageQueueSize": 1000
  }
}
```

## Production Deployment

For production deployments, consider these configuration settings:

```env
MCP_PORT=443
MCP_HOST=0.0.0.0
MCP_PROTOCOL_VERSION=1.0
MCP_MAX_CONNECTIONS=500
MCP_TIMEOUT=60000
MCP_ENABLE_TLS=true
MCP_AUTH_REQUIRED=true
MCP_RATE_LIMIT=5000
MCP_BUFFER_SIZE=131072
MCP_MESSAGE_QUEUE_SIZE=5000
```

## Docker Configuration

When running MCP servers in Docker containers, use these environment variables:

```yaml
version: '3.8'
services:
  mcp-server:
    image: agent-mcp-server:latest
    environment:
      - MCP_PORT=3000
      - MCP_HOST=0.0.0.0
      - MCP_MAX_CONNECTIONS=200
      - MCP_TIMEOUT=45000
    ports:
      - "3000:3000"
    volumes:
      - ./config:/app/config
```