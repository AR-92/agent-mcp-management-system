# FastMCP Documentation Server

A Model Context Protocol (MCP) server that provides LLM access to FastMCP documentation.

## Overview

The FastMCP Documentation Server is an MCP implementation that allows LLMs to search, read, and understand FastMCP documentation. This server provides tools for accessing the comprehensive FastMCP documentation set, making it easier for AI systems to understand and use the FastMCP framework.

## Features

- 🔍 **Search Documentation**: Search through FastMCP documentation for specific terms
- 📚 **Read Documentation**: Read specific documentation files
- 🗂️ **List Sections**: Get a list of all documentation sections
- 📄 **Table of Contents**: Access the complete documentation table of contents
- 💡 **Concept Explanation**: Get detailed explanations of FastMCP concepts
- 🛠️ **Implementation Guides**: Generate implementation guides for specific topics
- 📈 **Latest Updates**: Track recently updated documentation
- 🧪 **Examples Finder**: Find example code related to specific features
- 📊 **Documentation Statistics**: Get comprehensive stats about the documentation
- 🔧 **File Metadata**: Retrieve metadata for documentation files
- 📁 **Section File Counting**: Count files in specific sections
- 🛡️ **Server Health Check**: Monitor server health and status
- ⚡ **File Type Search**: Search for files by their type
- 📋 **Best Practices**: Generate best practices recommendations
- 🔄 **Comparisons**: Compare different concepts or features
- 🔧 **Troubleshooting**: Generate troubleshooting guidance
- 🏗️ **MCP Skeleton Generation**: Create skeleton code for new MCP servers
- ✅ **MCP Configuration Validation**: Validate MCP configuration
- 📝 **MCP Implementation Guide**: Generate complete implementation guides
- 🔧 **MCP Debugging Guide**: Generate debugging guidance for MCP servers
- 📚 **MCP Best Practices**: Get MCP best practices and guidelines
- 🔍 **MCP Code Analysis**: Analyze existing MCP code for issues and suggestions

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. Clone or navigate to this directory
2. Install dependencies:

```bash
pip install -r requirements.txt
```

Or install directly:

```bash
pip install fastmcp>=2.0.0 pydantic>=2.0.0
```

## Usage

### Running the Server

#### Method 1: Direct Python execution
```bash
python server.py
```

#### Method 2: Using environment variables for configuration
```bash
FASTMCP_HOST=0.0.0.0 FASTMCP_PORT=8001 python server.py
```

#### Method 3: Using FastMCP CLI
```bash
fastmcp run server.py:mcp --transport http --port 8001
```

## API Reference

### Tools

#### `list_documentation_sections()`
Returns a list of all available documentation sections.

#### `search_documentation(query: str)`
Searches documentation for content matching the query string.

#### `read_documentation_file(file_path: str)`
Reads the content of a specific documentation file.

#### `get_section_files(section: str)`
Gets all files in a specific documentation section.

#### `find_examples_for_feature(feature: str)`
Finds documentation examples related to a specific feature.

#### `count_docs_in_section(section: str)`
Count the number of documentation files in a specific section.

#### `search_by_file_type(file_type: str)`
Search for documentation files by type (md, txt, etc.).

#### `get_file_metadata(file_path: str)`
Get metadata for a specific documentation file including size, creation/modification dates.

#### `get_recently_accessed_docs(limit: int)`
Get a list of recently accessed documentation files (based on cache).

### Resources

#### `get_documentation_toc()`
Returns the table of contents for the FastMCP documentation.

#### `get_latest_docs_updates()`
Returns information about recently updated documentation.

#### `get_documentation_stats()`
Get comprehensive statistics about the documentation.

#### `get_server_health()`
Get the health status of the documentation server.

### Prompts

#### `explain_fastmcp_concept(concept: str, context: str)`
Generates a prompt to explain a FastMCP concept with context.

#### `implementation_guide_prompt(topic: str, requirements: str)`
Generates a prompt for implementing a FastMCP feature.

#### `best_practices_prompt(topic: str, context: str)`
Generate a prompt about best practices for a specific FastMCP topic.

#### `comparison_prompt(subject1: str, subject2: str, context: str)`
Generate a prompt to compare two FastMCP concepts or features.

#### `troubleshooting_prompt(issue_description: str, environment: str)`
Generate a prompt for troubleshooting a FastMCP issue.

#### `create_mcp_skeleton(name: str, description: str, tools: List[str], resources: List[str], prompts: List[str])`
Create a skeleton for a new MCP server with all necessary files and configuration.

#### `validate_mcp_config(config_content: str)`
Validate MCP configuration content for common issues and proper setup.

#### `generate_mcp_implementation_guide(project_type: str, features: List[str], requirements: str)`
Generate a complete implementation guide for an MCP server.

#### `generate_mcp_debugging_guide(server_code: str)`
Generate a debugging guide for an MCP server based on provided code.

#### `get_mcp_best_practices()`
Get MCP best practices and guidelines.

#### `analyze_existing_mcp(server_content: str)`
Analyze existing MCP server code and provide insights, issues, and suggestions.

## Security Notes

- The server restricts file access to the documentation directory only
- Path validation is performed to prevent directory traversal attacks
- Only markdown files are accessible through the documentation tools

## Integration

This server can be integrated with any LLM that supports the Model Context Protocol (MCP), including:

- Claude Desktop
- Cursor IDE
- Other MCP-compatible clients

## License

This project is licensed under the MIT License - see the LICENSE file for details.