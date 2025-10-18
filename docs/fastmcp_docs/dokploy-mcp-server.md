# Dokploy MCP Server Documentation

The Dokploy MCP Server provides an interface between LLM applications and the Dokploy platform through the Model Context Protocol (MCP). This server automatically generates tools from the Dokploy OpenAPI specification, allowing LLMs to manage applications, databases, projects, and infrastructure on Dokploy.

## Getting Started

### Prerequisites

- Python 3.8+
- FastMCP framework
- Dokploy API key

### Configuration

Before running the server, ensure you have configured your environment properly:

1. Create a `.env` file in the project root with the following variables:
   ```
   DOKPLOY_API_KEY=your_actual_api_key_here
   DOKPLOY_API_URL=https://dokploy.flowchat.info/api
   DOKPLOY_SERVER_NAME=Dokploy MCP Server
   DOKPLOY_SERVER_DESCRIPTION=Provides access to Dokploy functionality for LLMs through MCP protocol
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Server

```python
from mcps.dokploy_openapi_mcp_server import mcp

if __name__ == "__main__":
    mcp.run(host="127.0.0.1", port=8000)
```

## OpenAPI Integration

This server automatically parses the OpenAPI specification file at `OpenApi/dokploy.json` and generates MCP tools for each endpoint defined in the specification. The server:

1. Reads the OpenAPI specification
2. Creates Pydantic models for request bodies and parameters
3. Generates async tool functions for each endpoint
4. Handles authentication and API calls automatically

All endpoints in the Dokploy OpenAPI specification are made available as MCP tools with appropriate type hints and parameter validation.

## Available Tools

The server automatically generates tools from the OpenAPI specification. The available tools include operations for:

- **Admin operations**: Server monitoring setup, configuration management
- **Docker operations**: Container management, configuration retrieval, restart operations
- **Project operations**: Creation, retrieval, updates, duplication, removal
- **Application operations**: Creation, deployment, management, configuration
- **Database operations**: MySQL, PostgreSQL, Redis, and MongoDB management

Each tool is dynamically created based on the OpenAPI specification and includes proper parameter validation based on the schema definitions.

### Example Tool Usage

For example, if the OpenAPI spec includes an endpoint for creating applications, the server will automatically generate a tool like:

```python
result = await client.call_tool(
    name="application_create",  # Automatically derived from operationId
    arguments={
        "name": "My Application",
        "environmentId": "env_123",
        "description": "An example application"
    }
)
```

The exact parameters will depend on the schema defined in the OpenAPI specification for that endpoint.

## Error Handling

The server follows standard MCP error handling. When API requests fail, the server returns error information including the HTTP status code and error message.

## Security

This server uses API key authentication with the Dokploy API. The API key is loaded from the environment variables and included in the Authorization header for all requests.

## Development

The server automatically updates when new endpoints are added to the OpenAPI specification. Simply add new paths to the `OpenApi/dokploy.json` file, and they will be automatically made available as tools.