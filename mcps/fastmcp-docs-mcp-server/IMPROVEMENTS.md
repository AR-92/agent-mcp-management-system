# Improved FastMCP Documentation Server

This is an enhanced version of the FastMCP Documentation Server with multiple improvements for better functionality, security, and performance.

## Improvements Made

### 1. Enhanced Error Handling and Logging
- Added comprehensive error handling throughout all functions
- Implemented structured logging with configurable log levels
- Added detailed error messages for debugging

### 2. Robust Input Validation and Security
- Added thorough validation for file paths to prevent directory traversal
- Implemented security checks for all inputs
- Added proper content filtering to only allow markdown and text files

### 3. Performance Optimizations
- Implemented intelligent caching system with TTL (Time To Live)
- Added cache with configurable size limits
- Added cache statistics and management functions

### 4. Advanced Search Algorithms
- Implemented sophisticated search with scoring based on match quality
- Added support for both phrase and token matching
- Results are sorted by relevance score

### 5. Rate Limiting
- Added configurable rate limiting to prevent abuse
- Configurable limits for different types of requests
- Rate limiter with sliding window algorithm

### 6. Comprehensive Configuration Management
- Added ServerConfig class for centralized configuration
- Support for environment variables
- Configuration file support (JSON/YAML)
- Dynamic configuration loading

### 7. Testable Architecture
- Created separate implementation functions that can be directly tested
- Maintained MCP decorators for protocol compliance
- Allows both functional testing and MCP protocol usage

## Configuration Options

The server can be configured using:

### Environment Variables
- `FASTMCP_SERVER_NAME` - Server name (default: "FastMCP Documentation Server")
- `FASTMCP_VERSION` - Server version (default: "2.0.0")
- `FASTMCP_INSTRUCTIONS` - Server instructions (default: "Provides access to FastMCP documentation for LLMs")
- `DOCS_BASE_PATH` - Path to documentation (default: relative to project)
- `CACHE_MAX_SIZE` - Maximum cache size (default: 100)
- `CACHE_TTL` - Cache TTL in seconds (default: 300)
- `RATE_LIMIT_MAX_REQUESTS` - Max requests per window (default: 100)
- `RATE_LIMIT_WINDOW` - Rate limit window in seconds (default: 3600)
- `FASTMCP_HOST` - Server host (default: "127.0.0.1")
- `FASTMCP_PORT` - Server port (default: 8001)
- `FASTMCP_LOG_LEVEL` - Logging level (default: "INFO")

### Configuration Files
The server will automatically load configuration from:
- `config.json`
- `config.yaml`
- `config.yml`

## API Reference

### Tools
- `list_documentation_sections()` - Returns a list of all available documentation sections
- `search_documentation(query: str)` - Searches documentation for content matching the query
- `read_documentation_file(file_path: str)` - Reads the content of a specific documentation file
- `get_section_files(section: str)` - Gets all files in a specific documentation section
- `find_examples_for_feature(feature: str)` - Finds documentation examples related to a specific feature

### Resources
- `get_documentation_toc()` - Returns the table of contents for the FastMCP documentation
- `get_latest_docs_updates()` - Returns information about recently updated documentation

### Prompts
- `explain_fastmcp_concept(concept: str, context: str)` - Generates a prompt to explain a FastMCP concept
- `implementation_guide_prompt(topic: str, requirements: str)` - Generates a prompt for implementing a FastMCP feature

## Admin Functions
- `get_cache_stats()` - Get cache statistics
- `clear_cache()` - Clear the document cache

## Running the Server

### Method 1: Direct Python execution
```bash
python testable_improved_server.py
```

### Method 2: Using environment variables for configuration
```bash
FASTMCP_HOST=0.0.0.0 FASTMCP_PORT=8001 python testable_improved_server.py
```

## Testing

Run the comprehensive test suite:
```bash
python test_improved_server.py
```

## Architecture Notes

The server implements a dual-layer architecture:
1. Implementation functions (prefixed with `_`) - These can be directly tested
2. MCP-decorated functions - These are registered with the MCP protocol

This allows both proper MCP functionality and comprehensive testing of business logic.