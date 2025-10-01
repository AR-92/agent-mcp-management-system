# Deployment

This section covers everything you need to know about deploying FastMCP applications in production environments. Learn about different deployment options, security considerations, and operational best practices.

## Deployment Options

### Local Deployment

For development and testing, you can run FastMCP servers locally:

```python
from fastmcp import FastMCP

mcp = FastMCP("Local Development Server")

@mcp.tool
def hello() -> str:
    return "Hello from local server!"

if __name__ == "__main__":
    # Run with default settings for development
    mcp.run(host="127.0.0.1", port=8000)
```

### Container Deployment

Docker is the recommended approach for containerized deployments:

```Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "-m", "my_mcp_server"]
```

```docker-compose.yml
version: '3.8'
services:
  mcp-server:
    build: .
    ports:
      - "8000:8000"
    environment:
      - FASTMCP_HOST=0.0.0.0
      - FASTMCP_PORT=8000
    restart: unless-stopped
```

### Cloud Deployment

FastMCP servers can be deployed to any cloud platform that supports Python applications.

#### Using FastMCP Cloud

FastMCP Cloud provides free hosting for personal servers:

```bash
# Deploy directly from command line
fastmcp deploy --name my-server --token YOUR_TOKEN
```

#### Platform-as-a-Service (Heroku, Railway, etc.)

Prepare your app for PaaS deployment with a Procfile:

```
web: python -m my_mcp_server
```

And ensure your server runs on the port specified by the environment:

```python
import os
from fastmcp import FastMCP

mcp = FastMCP("Cloud Server")

# Read port from environment variable
port = int(os.getenv("PORT", 8000))

if __name__ == "__main__":
    mcp.run(host="0.0.0.0", port=port)
```

#### Kubernetes Deployment

For complex deployments, use Kubernetes manifests:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mcp-server
  template:
    metadata:
      labels:
        app: mcp-server
    spec:
      containers:
      - name: mcp-server
        image: my-mcp-server:latest
        ports:
        - containerPort: 8000
        env:
        - name: FASTMCP_HOST
          value: "0.0.0.0"
        - name: FASTMCP_PORT
          value: "8000"
---
apiVersion: v1
kind: Service
metadata:
  name: mcp-server-service
spec:
  selector:
    app: mcp-server
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

## Production Configuration

### Environment Variables

Configure your production server with environment variables:

```bash
# Server configuration
FASTMCP_HOST=0.0.0.0
FASTMCP_PORT=8000
FASTMCP_DEBUG=false

# Security
FASTMCP_AUTH_REQUIRED=true
FASTMCP_ALLOWED_ORIGINS=https://yourdomain.com

# Performance
FASTMCP_MAX_CONCURRENT_REQUESTS=100
FASTMCP_REQUEST_TIMEOUT=30
```

### Security Considerations

Secure your MCP server with proper authentication and authorization:

```python
from fastmcp import FastMCP
from fastmcp.auth import require_auth

mcp = FastMCP("Secure Server")

# Enable authentication for all tools
mcp.middleware.append(require_auth)

@mcp.tool
def secure_operation() -> str:
    """This tool requires authentication"""
    return "Secure operation completed"
```

### HTTPS Configuration

Always use HTTPS in production:

```python
from fastmcp import FastMCP

mcp = FastMCP(
    name="HTTPS Server",
    ssl_certfile="/path/to/cert.pem",
    ssl_keyfile="/path/to/key.pem"
)

if __name__ == "__main__":
    mcp.run(host="0.0.0.0", port=8443)
```

## Monitoring and Logging

### Application Logging

Configure comprehensive logging for your MCP server:

```python
import logging
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
mcp = FastMCP("Monitored Server")

@mcp.tool
def logged_operation(data: str) -> str:
    """Operation with comprehensive logging"""
    logger.info(f"Starting operation with data: {data}")
    try:
        result = f"Processed: {data}"
        logger.info(f"Operation completed successfully: {result}")
        return result
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        raise
```

### Health Checks

Implement health check endpoints for monitoring:

```python
from fastmcp import FastMCP
import asyncio

mcp = FastMCP("Health-monitored Server")

@mcp.tool
def health_check() -> dict:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": asyncio.get_event_loop().time()
    }
```

## Performance Optimization

### Caching

Implement caching for expensive operations:

```python
from fastmcp import FastMCP
import functools

mcp = FastMCP("Caching Server")

@functools.lru_cache(maxsize=128)
def expensive_computation(n: int) -> int:
    """Expensive computation with caching"""
    # Simulate expensive operation
    result = 0
    for i in range(n):
        result += i ** 2
    return result

@mcp.tool
def compute_cached(n: int) -> int:
    """Tool that uses cached computation"""
    return expensive_computation(n)
```

### Async Operations

Use async/await for improved performance:

```python
import asyncio
from fastmcp import FastMCP

mcp = FastMCP("Async Server")

@mcp.tool
async def async_operation(data: str) -> str:
    """Async operation that yields control"""
    await asyncio.sleep(1)  # Simulate I/O operation
    return f"Processed async: {data}"

@mcp.tool
async def parallel_operations(items: list) -> list:
    """Process multiple items in parallel"""
    tasks = [async_operation(item) for item in items]
    return await asyncio.gather(*tasks)
```

## Scaling Strategies

### Horizontal Scaling

Deploy multiple instances behind a load balancer:

```python
from fastmcp import FastMCP
import os

# Use environment-specific configuration
instance_id = os.getenv("INSTANCE_ID", "unknown")
mcp = FastMCP(f"Server-{instance_id}")

@mcp.tool
def get_instance_info() -> dict:
    """Return information about this instance"""
    return {
        "instance_id": instance_id,
        "host": os.getenv("HOSTNAME", "unknown")
    }
```

### Auto-scaling

Configure auto-scaling based on metrics:

```python
from fastmcp import FastMCP
import time

mcp = FastMCP("Metrics-enabled Server")
request_count = 0
start_time = time.time()

@mcp.tool
def tracked_operation(data: str) -> str:
    """Operation with metrics tracking"""
    global request_count
    request_count += 1
    return f"Processed: {data}"
    
@mcp.tool
def get_metrics() -> dict:
    """Get server metrics"""
    uptime = time.time() - start_time
    return {
        "requests_served": request_count,
        "uptime_seconds": uptime,
        "requests_per_second": request_count / uptime if uptime > 0 else 0
    }
```

## Backup and Recovery

### Configuration Backup

Regularly backup your server configuration:

```python
import json
from pathlib import Path
from fastmcp import FastMCP

def backup_config(mcp: FastMCP, backup_path: str):
    """Backup server configuration"""
    config = {
        "name": mcp.name,
        "version": getattr(mcp, '__version__', 'unknown'),
        "tools": [tool.name for tool in mcp._tools],
        "resources": [resource.name for resource in mcp._resources]
    }
    
    Path(backup_path).parent.mkdir(parents=True, exist_ok=True)
    with open(backup_path, 'w') as f:
        json.dump(config, f, indent=2)
```

### Data Persistence

For stateful operations, implement proper data persistence:

```python
import sqlite3
from fastmcp import FastMCP

class PersistentStore:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS operations (
                id INTEGER PRIMARY KEY,
                operation TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    def log_operation(self, operation: str):
        self.conn.execute(
            'INSERT INTO operations (operation) VALUES (?)',
            (operation,)
        )
        self.conn.commit()

store = PersistentStore("operations.db")
mcp = FastMCP("Persistent Server")

@mcp.tool
def persistent_operation(data: str) -> str:
    """Operation with persistent logging"""
    result = f"Processed: {data}"
    store.log_operation(result)
    return result
```

## Troubleshooting

### Common Deployment Issues

1. **Port Binding Issues**: Ensure your server binds to the correct address:
   ```python
   # Use 0.0.0.0 in containerized environments
   mcp.run(host="0.0.0.0", port=8000)
   ```

2. **Environment Configuration**: Always read configuration from environment variables:
   ```python
   import os
   
   port = int(os.getenv("FASTMCP_PORT", 8000))
   host = os.getenv("FASTMCP_HOST", "127.0.0.1")
   ```

3. **Resource Limits**: Monitor memory and CPU usage, especially for async operations.

### Debugging Production Issues

Enable detailed logging in development but not in production:

```python
import os
import logging
from fastmcp import FastMCP

debug_mode = os.getenv("FASTMCP_DEBUG", "false").lower() == "true"
log_level = logging.DEBUG if debug_mode else logging.INFO

logging.basicConfig(level=log_level)
mcp = FastMCP("Debug-configurable Server")
```

## Next Steps

1. [Security](./security.md) - Deep dive into securing your MCP deployments
2. [Monitoring](./monitoring.md) - Implement comprehensive monitoring solutions
3. [Performance](./performance.md) - Optimize your MCP server performance
4. [CI/CD](./cicd.md) - Set up continuous integration and deployment pipelines