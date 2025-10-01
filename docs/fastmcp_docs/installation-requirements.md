# Requirements

This page details the system and software requirements for installing and running FastMCP.

## System Requirements

### Operating System
FastMCP runs on:
- **Linux**: All major distributions (Ubuntu, CentOS, Arch, etc.)
- **macOS**: Version 10.14 (Mojave) or later
- **Windows**: Windows 10 or later (with WSL recommended for best experience)

### Hardware
- **CPU**: Modern x86-64 or ARM processor
- **Memory**: Minimum 512MB RAM, recommended 2GB+ for development
- **Storage**: 50MB for FastMCP installation, additional space for your projects

## Software Requirements

### Python
- **Version**: Python 3.8 or higher (Python 3.9+ recommended)
- **Installation**: Can be verified with:
  ```bash
  python --version
  # or
  python3 --version
  ```

### Package Manager
- **pip**: Latest version recommended (comes with Python 3.4+)
  ```bash
  pip --version
  ```

### Optional Development Tools
- **Git**: For cloning repositories and version control
- **Virtual Environment Tool**: venv (built-in), conda, or pipenv

## Python Dependencies

FastMCP has minimal runtime dependencies that will be installed automatically:

- `pydantic`: For data validation and settings management
- `anyio`: For async/await support
- `httpx`: For HTTP client functionality
- `click`: For command-line interface
- `pyyaml`: For YAML configuration files (optional)
- `uvicorn`: For server execution (optional)

### Optional Dependencies for Advanced Features
- `cryptography`: For advanced authentication features
- `jose`: For JWT token handling
- `fastapi`: For FastAPI integration
- `openapi`: For OpenAPI specification support

## Network Requirements

### For Installation
- Internet connection to download packages from PyPI
- Access to `pypi.org` and `files.pythonhosted.org`

### For Runtime
- FastMCP servers listen on local ports by default
- For remote access, appropriate firewall rules may be needed
- For authentication integrations, access to identity providers (Google, GitHub, etc.)

## Verification Commands

To check if your system meets the requirements:

```bash
# Check Python version
python3 --version
# Should be Python 3.8 or higher

# Check pip version
pip --version
# Should be available

# Check if all dependencies can be imported
python3 -c "
import sys
if sys.version_info < (3, 8):
    print('Python 3.8 or higher is required')
else:
    print('Python version OK')
    
# Check for optional dependencies
try:
    import pydantic
    print('pydantic OK')
except ImportError:
    print('pydantic will be installed automatically')

try:
    import anyio
    print('anyio OK')
except ImportError:
    print('anyio will be installed automatically')
"
```

## Development Environment Setup

For development, you might also want:

### Code Editor
- VS Code with Python extension
- PyCharm
- Vim/Neovim with Python plugins
- Or any editor with Python support

### Development Tools
- **pytest**: For running tests
- **black**: For code formatting
- **flake8**: For linting
- **mypy**: For type checking

### Environment Management
```bash
# Recommended packages for development
pip install pytest black flake8 mypy
```

## Container Requirements

If using FastMCP in containers:

### Docker
- Docker version 18.09 or higher
- Docker Compose (optional) for multi-container setups

### Container Base Images
- Any Python base image (python:3.9-slim, python:3.10, etc.)
- Alpine Linux with Python (smaller image size)

Example Dockerfile:
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "server.py"]
```

## Platform-Specific Notes

### Linux
- No special requirements beyond the general ones
- systemd or similar can be used for service management

### macOS
- Requires Xcode command-line tools for some dependencies
- Install with: `xcode-select --install`

### Windows
- Windows Subsystem for Linux (WSL) recommended for development
- Powershell or Command Prompt for execution
- Ensure Python is added to PATH during installation

## Minimum Viable Setup

For a basic FastMCP server, you need:
1. Python 3.8+
2. pip
3. About 50MB of disk space
4. A text editor

That's it! FastMCP is designed to be lightweight and easy to set up.