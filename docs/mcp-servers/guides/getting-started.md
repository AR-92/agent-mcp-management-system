# Getting Started with MCP Servers

This guide will help you set up and run MCP servers in the Agent MCP Management System.

## Prerequisites

- Node.js (version 18 or higher)
- npm or yarn package manager
- Docker (optional, for containerized deployment)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/AR-92/agent-mcp-management-system.git
   ```

2. Navigate to the servers directory:
   ```bash
   cd agent-mcp-management-system/servers
   ```

3. Install dependencies:
   ```bash
   npm install
   # or
   yarn install
   ```

## Running an MCP Server

1. Start the MCP server:
   ```bash
   npm run start:mcp
   # or
   yarn start:mcp
   ```

2. The server will start on the default port (usually 3000) unless configured otherwise.

## Configuration

MCP servers can be configured using environment variables or a configuration file:

```env
MCP_PORT=3000
MCP_HOST=localhost
MCP_PROTOCOL_VERSION=1.0
MCP_MAX_CONNECTIONS=100
MCP_TIMEOUT=30000
```

## Basic Example

```javascript
const { MCPServer } = require('@agent-mcp/server');

const server = new MCPServer({
  port: 3000,
  host: 'localhost',
  protocol: 'MCP/1.0'
});

server.start()
  .then(() => console.log('MCP Server running on port 3000'))
  .catch(err => console.error('Failed to start server:', err));
```

## Next Steps

- Check out the [API Reference](../api/) for detailed endpoint information
- Learn about the [Protocol Specifications](../protocols/)
- Explore [Architecture](../architecture/) for system design details