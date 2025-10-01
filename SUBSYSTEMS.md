# Project Structure

## Directories

- `docs/` - Documentation for the project
  - `guides/` - User guides and tutorials
  - `api/` - API reference documentation
  - `architecture/` - Architecture decision records and diagrams

- `mcps/` - MCP Protocol implementations
  - `protocols/` - Core protocol definitions
  - `handlers/` - Request/response handlers
  - `validators/` - Input validators

- `servers/` - Server implementations
  - `http/` - HTTP server code
  - `websocket/` - WebSocket server code
  - `mcp/` - MCP-specific server components

- `agents/` - Agent implementations
  - `core/` - Core agent functionality
  - `types/` - Agent type definitions
  - `plugins/` - Agent plugins and extensions

- `tests/` - Test files
  - `unit/` - Unit tests
  - `integration/` - Integration tests
  - `e2e/` - End-to-end tests