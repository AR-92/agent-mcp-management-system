# MCP Server API Reference

This document provides detailed information about the MCP server API endpoints and methods.

## Base Protocol

All MCP communications follow the MCP/1.0 protocol specification.

## Connection Endpoints

### Establish Connection
- Method: CONNECT
- Purpose: Establish a new connection to the MCP server
- Headers: 
  - MCP-Version: 1.0
  - Client-ID: [unique client identifier]
- Response: Connection established with session token

### Close Connection
- Method: DISCONNECT
- Purpose: Close an existing connection
- Request: Session token
- Response: Connection closed confirmation

## Message Endpoints

### Send Message
- Method: SEND
- Purpose: Send a message from client to server
- Request Format:
  ```
  {
    "id": "unique-message-id",
    "type": "request-type",
    "timestamp": "ISO-8601-timestamp",
    "data": { ... },
    "metadata": { ... }
  }
  ```
- Response: ACK or error message

### Receive Message
- Method: RECEIVE
- Purpose: Receive messages from server
- Response Format:
  ```
  {
    "id": "corresponding-request-id",
    "type": "response-type",
    "timestamp": "ISO-8601-timestamp",
    "data": { ... },
    "status": "success|error"
  }
  ```

## Management Endpoints

### Get Server Status
- Method: STATUS
- Purpose: Retrieve server operational status
- Response:
  ```
  {
    "status": "healthy|unhealthy|degraded",
    "uptime": "seconds",
    "connections": "current-connection-count",
    "requests": "recent-request-count",
    "version": "server-version"
  }
  ```

### Get Server Info
- Method: INFO
- Purpose: Retrieve server metadata
- Response:
  ```
  {
    "version": "server-version",
    "protocol": "supported-protocol-versions",
    "features": ["feature-list"],
    "limits": {
      "max-connections": "maximum-connections",
      "message-size-limit": "bytes"
    }
  }
  ```

## Error Codes

- 1000: General error
- 1001: Invalid message format
- 1002: Authentication failed
- 1003: Session expired
- 1004: Rate limit exceeded
- 1005: Server unavailable
- 1006: Timeout

## Message Format

All messages follow this structure:
```
{
  "header": {
    "id": "unique-identifier",
    "type": "message-type",
    "version": "protocol-version",
    "timestamp": "ISO-8601-timestamp"
  },
  "body": {
    "data": { ... },
    "metadata": { ... }
  }
}
```