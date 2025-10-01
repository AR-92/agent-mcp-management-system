# MCP Protocol Specifications

This document defines the MCP (Multi-Component Protocol) specifications used by the servers.

## Protocol Version

Current version: MCP/1.0

## Message Structure

The MCP protocol uses a structured message format:

```
[HEADER_LENGTH][HEADER][BODY_LENGTH][BODY]
```

Where:
- HEADER_LENGTH: 4-byte integer representing the length of the header
- HEADER: JSON-encoded header object
- BODY_LENGTH: 4-byte integer representing the length of the body
- BODY: JSON-encoded body object (or binary data for certain message types)

### Header Format

```json
{
  "id": "string, unique message identifier",
  "method": "string, MCP method name",
  "version": "string, protocol version",
  "timestamp": "number, Unix timestamp in milliseconds",
  "contentType": "string, content type (json, binary, etc.)"
}
```

### Body Format

The body format depends on the method but generally follows:

```json
{
  "data": "mixed, the actual payload",
  "metadata": "object, additional information",
  "status": "string, for responses (success, error, etc.)"
}
```

## MCP Methods

### Connection Methods

#### CONNECT
Initiates a connection with the server.

Request Header:
```json
{
  "id": "unique-id",
  "method": "CONNECT",
  "version": "MCP/1.0",
  "timestamp": 1234567890123,
  "contentType": "json"
}
```

Request Body:
```json
{
  "clientInfo": {
    "id": "client-identifier",
    "version": "client-version",
    "capabilities": ["capability1", "capability2"]
  }
}
```

Response Body:
```json
{
  "sessionId": "session-identifier",
  "serverInfo": {
    "version": "server-version",
    "protocolVersion": "MCP/1.0",
    "supportedMethods": ["method1", "method2"]
  }
}
```

#### DISCONNECT
Terminates a connection with the server.

Request Header:
```json
{
  "id": "unique-id",
  "method": "DISCONNECT",
  "version": "MCP/1.0",
  "timestamp": 1234567890123,
  "contentType": "json"
}
```

Request Body:
```json
{
  "sessionId": "session-identifier",
  "reason": "disconnection-reason"
}
```

Response Body:
```json
{
  "status": "disconnected",
  "timestamp": 1234567890123
}
```

### Data Methods

#### SEND
Sends data to the server.

Request Header:
```json
{
  "id": "unique-id",
  "method": "SEND",
  "version": "MCP/1.0",
  "timestamp": 1234567890123,
  "contentType": "json"
}
```

Request Body:
```json
{
  "sessionId": "session-identifier",
  "payload": { ... },
  "destination": "target-identifier"
}
```

Response Body:
```json
{
  "status": "accepted|rejected",
  "messageId": "assigned-message-id"
}
```

#### RECEIVE
Receives data from the server.

Request Header:
```json
{
  "id": "unique-id",
  "method": "RECEIVE",
  "version": "MCP/1.0",
  "timestamp": 1234567890123,
  "contentType": "json"
}
```

Request Body:
```json
{
  "sessionId": "session-identifier",
  "timeout": "timeout-in-milliseconds"
}
```

Response Body:
```json
{
  "messages": [
    {
      "id": "message-id",
      "sender": "sender-identifier",
      "payload": { ... },
      "timestamp": 1234567890123
    }
  ]
}
```

## Security

All MCP communications should be encrypted using TLS 1.2 or higher when transmitted over untrusted networks.

Authentication is performed during the CONNECT phase and maintained throughout the session using the sessionId.

## Error Handling

Errors in the MCP protocol are communicated through specific response codes:

- 200: Success
- 400: Bad Request - Invalid message format
- 401: Unauthorized - Authentication required
- 403: Forbidden - Insufficient permissions
- 408: Request Timeout
- 429: Too Many Requests
- 500: Internal Server Error
- 503: Service Unavailable