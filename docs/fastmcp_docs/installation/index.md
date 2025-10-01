# Installation

This section covers how to install and set up FastMCP for your projects.

## Requirements

- Python 3.8 or higher
- pip (Python package installer) or uv

FastMCP is compatible with major operating systems including Linux, macOS, and Windows.

## Installing FastMCP

We recommend using uv to install and manage FastMCP. If you plan to use FastMCP in your project, you can add it as a dependency with:

```
uv add fastmcp
```

Alternatively, you can install it directly with pip or uv pip:

### Using uv:
```
uv pip install fastmcp
```

### Using pip:
```
pip install fastmcp
```

## Verify Installation

To verify that FastMCP is installed correctly, you can run the following command:

```
fastmcp version
```

You should see output like the following:
```
$ fastmcp version

FastMCP version:                           2.11.3
MCP version:                               1.12.4
Python version:                            3.12.2
Platform:            macOS-15.3.1-arm64-arm-64bit
FastMCP root path:            ~/Developer/fastmcp
```

## Upgrading from the Official MCP SDK

Upgrading from the official MCP SDK's FastMCP 1.0 to FastMCP 2.0 is generally straightforward. The core server API is highly compatible, and in many cases, changing your import statement from `from mcp.server.fastmcp import FastMCP` to `from fastmcp import FastMCP` will be sufficient.

```python
# Before
# from mcp.server.fastmcp import FastMCP

# After
from fastmcp import FastMCP

mcp = FastMCP("My MCP Server")
```

Prior to fastmcp==2.3.0 and mcp==1.8.0, the 2.x API always mirrored the official 1.0 API. However, as the projects diverge, this can not be guaranteed. You may see deprecation warnings if you attempt to use 1.0 APIs in FastMCP 2.x. Please refer to this documentation for details on new capabilities.

## Versioning Policy

FastMCP follows semantic versioning with pragmatic adaptations for the rapidly evolving MCP ecosystem. Breaking changes may occur in minor versions (e.g., 2.3.x to 2.4.0) when necessary to stay current with the MCP Protocol. For production use, always pin to exact versions:

```
fastmcp==2.11.0  # Good
fastmcp>=2.11.0  # Bad - will install breaking changes
```

See the full versioning and release policy for details on our public API, deprecation practices, and breaking change philosophy.

## Contributing to FastMCP

Interested in contributing to FastMCP? See the Contributing Guide for details on:
- Setting up your development environment
- Running tests and pre-commit hooks
- Submitting issues and pull requests
- Code standards and review process

## Virtual Environment (Recommended)

For best practices, we recommend installing FastMCP in a virtual environment:

### Using venv
```bash
# Create a virtual environment
python -m venv fastmcp-env

# Activate it (Linux/macOS)
source fastmcp-env/bin/activate

# Activate it (Windows)
fastmcp-env\Scripts\activate

# Install FastMCP
pip install fastmcp
```

### Using conda
```bash
# Create a conda environment
conda create -n fastmcp-env python=3.9

# Activate the environment
conda activate fastmcp-env

# Install FastMCP
pip install fastmcp
```

### Using pipenv
```bash
# Install pipenv if you don't have it
pip install pipenv

# Create and enter the environment
pipenv install fastmcp
pipenv shell
```

## Development Installation

If you want to contribute to FastMCP or use the development version:

```bash
# Clone the repository
git clone https://github.com/jlowin/fastmcp.git
cd fastmcp

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
```

## Verifying Installation

To verify that FastMCP is installed correctly:

```python
python -c "import fastmcp; print(fastmcp.__version__)"
```

Or create a simple test file:

```python
# test_installation.py
from fastmcp import FastMCP

def test():
    mcp = FastMCP("Test Server")
    
    @mcp.tool
    def hello() -> str:
        return "Installation successful!"
    
    print("FastMCP imported successfully!")
    print("Available methods:", [method for method in dir(mcp) if not method.startswith('_')])

if __name__ == "__main__":
    test()
```

## Common Installation Issues

### Permission Errors
If you encounter permission errors, try installing with the `--user` flag:
```bash
pip install --user fastmcp
```

### Dependencies Issues
FastMCP has minimal dependencies, but if you have conflicts:
```bash
pip install fastmcp --no-deps  # Install without dependencies
pip install fastmcp[all]       # Install with all optional dependencies
```

### Upgrade FastMCP
To upgrade to the latest version:
```bash
pip install --upgrade fastmcp
```

## Next Steps

After installation, continue with:
- [Getting Started Guide](../overview/getting-started.md) - Build your first MCP server
- [Core Concepts](../core-concepts/index.md) - Learn the fundamental concepts
- [Server Development](../server-development/index.md) - Create advanced MCP servers