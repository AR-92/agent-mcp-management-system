# Setup

This guide provides step-by-step instructions for setting up FastMCP in different environments.

## Quick Setup

For getting started quickly:

```bash
# 1. Install FastMCP
pip install fastmcp

# 2. Create a simple server file (server.py)
cat > server.py << EOF
from fastmcp import FastMCP

mcp = FastMCP("Quick Start Server")

@mcp.tool
def hello(name: str = "World") -> str:
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run()
EOF

# 3. Run the server
python server.py
```

## Development Setup

### 1. Create a Project Directory
```bash
mkdir my-mcp-project
cd my-mcp-project
```

### 2. Set Up Virtual Environment
```bash
# Using venv (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

### 3. Install FastMCP
```bash
pip install fastmcp
```

### 4. Create Project Structure
```bash
mkdir -p src/{tools,resources,prompts}
touch src/__init__.py
touch src/tools/__init__.py
touch src/resources/__init__.py
touch src/prompts/__init__.py
touch main.py
```

### 5. Create Your Server (main.py)
```python
from fastmcp import FastMCP

# Initialize the server
mcp = FastMCP("My MCP Server")

# Add your tools, resources, etc.
@mcp.tool
def example_tool(greeting: str, name: str) -> str:
    """An example tool that greets someone"""
    return f"{greeting}, {name}! This is your MCP server."

# Run the server
if __name__ == "__main__":
    mcp.run()
```

### 6. Run Your Server
```bash
python main.py
```

## Production Setup

### 1. Configuration File

Create a `fastmcp.json` configuration file:

```json
{
  "name": "Production Server",
  "version": "1.0.0",
  "description": "Production MCP Server",
  "server": {
    "host": "0.0.0.0",
    "port": 8080,
    "workers": 4
  },
  "authentication": {
    "required": true,
    "type": "bearer"
  }
}
```

### 2. Production Server File (production_server.py)

```python
from fastmcp import FastMCP
import os

# Initialize with configuration
mcp = FastMCP(
    name=os.getenv("MCP_SERVER_NAME", "Production Server"),
    description=os.getenv("MCP_SERVER_DESCRIPTION", "Production MCP Server")
)

# Add your production tools
@mcp.tool
def production_tool(data: str) -> dict:
    """A production-ready tool"""
    return {
        "processed": True,
        "input_length": len(data),
        "status": "success"
    }

if __name__ == "__main__":
    # Run with production settings
    mcp.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8080)),
        workers=4
    )
```

### 3. Environment Variables (.env)

```bash
MCP_SERVER_NAME="My Production Server"
MCP_SERVER_DESCRIPTION="Production MCP Server"
PORT=8080
```

## Docker Setup

### 1. Create Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "server.py"]
```

### 2. Create requirements.txt

```
fastmcp>=2.0.0
```

### 3. Build and Run

```bash
# Build the image
docker build -t my-mcp-server .

# Run the container
docker run -p 8000:8000 my-mcp-server
```

## Development with Hot Reload

For development with automatic reloading:

```bash
# Install uvicorn for hot reload
pip install uvicorn

# Run with hot reload
uvicorn server:app --reload
```

## Environment-Specific Configurations

### Development Environment
```python
# development.py
from fastmcp import FastMCP

mcp = FastMCP("Development Server", debug=True)

@mcp.tool
def debug_tool(message: str) -> str:
    """A tool for development and testing"""
    return f"Debug: {message}"

if __name__ == "__main__":
    mcp.run(host="127.0.0.1", port=8000)
```

### Testing Environment
```python
# test_server.py
from fastmcp import FastMCP

mcp = FastMCP("Test Server", debug=True)

@mcp.tool
def test_tool(value: int) -> dict:
    """A tool used for testing"""
    return {
        "input": value,
        "doubled": value * 2,
        "squared": value ** 2
    }

# For use in tests
def get_test_client():
    from fastmcp import Client
    return Client("http://localhost:8000")
```

## Common Setup Issues and Solutions

### Port Already in Use
```bash
# Check what's using a port
lsof -i :8000  # On Linux/macOS
netstat -ano | findstr :8000  # On Windows

# Kill the process if needed
kill -9 <PID>  # Replace <PID> with process ID
```

### Permission Issues
```bash
# Run on a different port if 8000 is restricted
python server.py --port 8080
```

### Virtual Environment Not Activating
```bash
# Make sure you're in the right directory
cd /path/to/your/project

# Re-create virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install fastmcp
```

## Verification Steps

After setup, verify everything is working:

```bash
# 1. Check installation
python -c "import fastmcp; print(fastmcp.__version__)"

# 2. Run basic server
echo 'from fastmcp import FastMCP
mcp = FastMCP("Test")
@mcp.tool
def test(): return "OK"
if __name__ == "__main__":
    mcp.run(host="127.0.0.1", port=8080)
' > test_server.py

python test_server.py &
sleep 2
curl http://127.0.0.1:8080/health  # If supported
kill %1  # Kill the background server
```

## Next Steps

Once your environment is set up:

1. [Core Concepts](../core-concepts/index.md) - Learn how to build tools and resources
2. [Server Development](../server-development/index.md) - Build more advanced servers
3. [Examples](../examples/index.md) - Practical examples to extend your knowledge