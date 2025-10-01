# Integrations

This section covers how to integrate FastMCP with various external systems, with a focus on authentication providers and third-party services.

## Authentication Integrations

FastMCP provides built-in support for multiple authentication providers, enabling enterprise-level security for your MCP servers.

### Google Authentication

Integrate Google OAuth2 for user authentication:

```python
from fastmcp import FastMCP
from fastmcp.auth import google_auth
import os

mcp = FastMCP("Google Auth Server")

# Configure Google auth with environment variables
google_auth.setup(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    redirect_uri=os.getenv("GOOGLE_REDIRECT_URI")
)

# Apply Google authentication to specific tools
@mcp.tool
@google_auth.required
def google_protected_operation() -> str:
    """Operation requiring Google authentication"""
    return "Google-authenticated operation completed"
```

### GitHub Authentication

Use GitHub OAuth for authentication:

```python
from fastmcp.auth import github_auth

github_auth.setup(
    client_id=os.getenv("GITHUB_CLIENT_ID"),
    client_secret=os.getenv("GITHUB_CLIENT_SECRET"),
    redirect_uri=os.getenv("GITHUB_REDIRECT_URI")
)

@mcp.tool
@github_auth.required
def github_protected_operation() -> str:
    """Operation requiring GitHub authentication"""
    return "GitHub-authenticated operation completed"
```

### Azure Active Directory

Integrate with Azure AD for enterprise authentication:

```python
from fastmcp.auth import azure_auth

azure_auth.setup(
    tenant_id=os.getenv("AZURE_TENANT_ID"),
    client_id=os.getenv("AZURE_CLIENT_ID"),
    client_secret=os.getenv("AZURE_CLIENT_SECRET")
)

@mcp.tool
@azure_auth.required
def azure_protected_operation() -> str:
    """Operation requiring Azure AD authentication"""
    return "Azure AD-authenticated operation completed"
```

### Auth0 Integration

Use Auth0 for flexible authentication:

```python
from fastmcp.auth import auth0_auth

auth0_auth.setup(
    domain=os.getenv("AUTH0_DOMAIN"),
    client_id=os.getenv("AUTH0_CLIENT_ID"),
    client_secret=os.getenv("AUTH0_CLIENT_SECRET")
)

@mcp.tool
@auth0_auth.required
def auth0_protected_operation() -> str:
    """Operation requiring Auth0 authentication"""
    return "Auth0-authenticated operation completed"
```

### WorkOS Integration

Enterprise authentication with WorkOS:

```python
from fastmcp.auth import workos_auth

workos_auth.setup(
    api_key=os.getenv("WORKOS_API_KEY"),
    client_id=os.getenv("WORKOS_CLIENT_ID")
)

@mcp.tool
@workos_auth.required
def workos_protected_operation() -> str:
    """Operation requiring WorkOS authentication"""
    return "WorkOS-authenticated operation completed"
```

## Generic OAuth2 Integration

For other OAuth2 providers, use the generic integration:

```python
from fastmcp.auth import oauth2_auth

oauth2_auth.setup(
    provider_name="Custom Provider",
    authorize_url=os.getenv("CUSTOM_AUTHORIZE_URL"),
    token_url=os.getenv("CUSTOM_TOKEN_URL"),
    client_id=os.getenv("CUSTOM_CLIENT_ID"),
    client_secret=os.getenv("CUSTOM_CLIENT_SECRET"),
    scopes=["read", "write"]
)

@mcp.tool
@oauth2_auth.required
def oauth2_protected_operation() -> str:
    """Operation requiring generic OAuth2 authentication"""
    return "OAuth2-authenticated operation completed"
```

## API Key Authentication

Simple API key authentication for service-to-service communication:

```python
from fastmcp.auth import api_key_auth

# Define valid API keys
valid_keys = {
    "prod-key-123": {"service": "production-client", "permissions": ["read", "write"]},
    "dev-key-456": {"service": "development-client", "permissions": ["read"]}
}

api_key_auth.setup(valid_keys)

@mcp.tool
@apik_key_auth.required
def api_key_protected_operation() -> str:
    """Operation requiring API key authentication"""
    return "API key-authenticated operation completed"
```

## JWT Token Authentication

Custom JWT authentication:

```python
from fastmcp.auth import jwt_auth
import jwt
from datetime import datetime, timedelta

# Setup JWT authentication
jwt_auth.setup(
    secret=os.getenv("JWT_SECRET"),
    algorithm="HS256"
)

@mcp.tool
@jwt_auth.required
def jwt_protected_operation() -> str:
    """Operation requiring JWT authentication"""
    return "JWT-authenticated operation completed"
```

## Database Integrations

### PostgreSQL Integration

Connect to PostgreSQL databases:

```python
import asyncpg
from fastmcp import FastMCP

class DatabaseManager:
    def __init__(self):
        self.pool = None
    
    async def init_pool(self):
        self.pool = await asyncpg.create_pool(
            dsn=os.getenv("DATABASE_URL"),
            min_size=1,
            max_size=10
        )
    
    async def execute_query(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

db = DatabaseManager()

mcp = FastMCP("Database Server")

# Initialize database connection when server starts
@mcp.on_startup
async def startup():
    await db.init_pool()

@mcp.tool
async def get_user_by_id(user_id: str) -> dict:
    """Get user from database"""
    result = await db.execute_query(
        "SELECT id, name, email FROM users WHERE id = $1", 
        user_id
    )
    
    if result:
        record = result[0]
        return {
            "id": record["id"],
            "name": record["name"], 
            "email": record["email"]
        }
    return None
```

### MongoDB Integration

Connect to MongoDB:

```python
import motor.motor_asyncio
from fastmcp import FastMCP

class MongoManager:
    def __init__(self):
        self.client = None
        self.db = None
    
    async def connect(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(
            os.getenv("MONGODB_URL")
        )
        self.db = self.client[os.getenv("MONGODB_DB", "fastmcp")]
    
    def get_collection(self, name: str):
        return self.db[name]

mongo = MongoManager()

@mcp.on_startup
async def mongo_startup():
    await mongo.connect()

@mcp.tool
async def find_user(user_id: str) -> dict:
    """Find user in MongoDB"""
    collection = mongo.get_collection("users")
    user = await collection.find_one({"_id": user_id})
    return user
```

## Third-Party API Integrations

### REST API Integration

Connect to external REST APIs:

```python
import aiohttp
from fastmcp import FastMCP

class APIClient:
    def __init__(self):
        self.session = None
    
    async def get_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={"Authorization": f"Bearer {os.getenv('API_TOKEN')}"}
            )
        return self.session

api_client = APIClient()

@mcp.tool
async def fetch_external_data(endpoint: str) -> dict:
    """Fetch data from external API"""
    session = await api_client.get_session()
    async with session.get(f"https://api.example.com/{endpoint}") as response:
        return await response.json()
```

### GraphQL Integration

Connect to GraphQL APIs:

```python
import httpx
from fastmcp import FastMCP

class GraphQLClient:
    def __init__(self, url: str, token: str = None):
        self.url = url
        self.headers = {}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"
    
    async def query(self, query: str, variables: dict = None) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.url,
                json={"query": query, "variables": variables or {}},
                headers=self.headers
            )
            return response.json()

graphql_client = GraphQLClient(
    url=os.getenv("GRAPHQL_ENDPOINT"),
    token=os.getenv("GRAPHQL_TOKEN")
)

@mcp.tool
async def query_external_graphql(query: str, variables: dict = None) -> dict:
    """Query external GraphQL API"""
    return await graphql_client.query(query, variables)
```

## Message Queue Integration

### Redis Integration

Use Redis for caching and message queues:

```python
import redis.asyncio as redis
from fastmcp import FastMCP

class RedisManager:
    def __init__(self):
        self.redis = None
    
    async def connect(self):
        self.redis = await redis.from_url(os.getenv("REDIS_URL"))
    
    async def get(self, key: str):
        return await self.redis.get(key)
    
    async def set(self, key: str, value: str, expire: int = 3600):
        await self.redis.setex(key, expire, value)

redis_manager = RedisManager()

@mcp.on_startup
async def redis_startup():
    await redis_manager.connect()

@mcp.tool
async def cache_data(key: str, value: str, ttl: int = 3600) -> bool:
    """Cache data in Redis"""
    await redis_manager.set(key, value, ttl)
    return True

@mcp.resource
async def get_cached_data(key: str) -> str:
    """Retrieve cached data from Redis"""
    data = await redis_manager.get(key)
    return data.decode() if data else None
```

### RabbitMQ Integration

Connect to RabbitMQ for message queuing:

```python
import aio_pika
from fastmcp import FastMCP

class RabbitMQManager:
    def __init__(self):
        self.connection = None
        self.channel = None
    
    async def connect(self):
        self.connection = await aio_pika.connect_robust(
            os.getenv("RABBITMQ_URL")
        )
        self.channel = await self.connection.channel()
    
    async def publish_message(self, queue: str, message: str):
        await self.channel.default_exchange.publish(
            aio_pika.Message(message.encode()),
            routing_key=queue
        )

rabbitmq = RabbitMQManager()

@mcp.on_startup
async def rabbitmq_startup():
    await rabbitmq.connect()

@mcp.tool
async def send_message_to_queue(queue: str, message: str) -> bool:
    """Send message to RabbitMQ queue"""
    await rabbitmq.publish_message(queue, message)
    return True
```

## File Storage Integration

### AWS S3 Integration

Connect to AWS S3 for file storage:

```python
import aioboto3
from fastmcp import FastMCP

class S3Manager:
    def __init__(self):
        self.session = None
    
    async def get_session(self):
        if not self.session:
            self.session = aioboto3.Session()
        return self.session

s3_manager = S3Manager()

@mcp.tool
async def upload_file_to_s3(bucket: str, key: str, content: str) -> bool:
    """Upload file to S3"""
    session = await s3_manager.get_session()
    async with session.client("s3") as s3:
        await s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=content
        )
    return True

@mcp.tool
async def download_file_from_s3(bucket: str, key: str) -> str:
    """Download file from S3"""
    session = await s3_manager.get_session()
    async with session.client("s3") as s3:
        response = await s3.get_object(Bucket=bucket, Key=key)
        content = await response["Body"].read()
        return content.decode()
```

### Google Cloud Storage Integration

Connect to Google Cloud Storage:

```python
from google.cloud import storage
from fastmcp import FastMCP

class GCSManager:
    def __init__(self):
        self.client = storage.Client()

gcs_manager = GCSManager()

@mcp.tool
async def upload_to_gcs(bucket_name: str, blob_name: str, content: str) -> bool:
    """Upload file to Google Cloud Storage"""
    bucket = gcs_manager.client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_string(content)
    return True

@mcp.tool
async def download_from_gcs(bucket_name: str, blob_name: str) -> str:
    """Download file from Google Cloud Storage"""
    bucket = gcs_manager.client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    return blob.download_as_text()
```

## WebSocket Integration

Real-time communication with WebSockets:

```python
import websockets
from fastmcp import FastMCP

class WebSocketManager:
    def __init__(self):
        self.connections = set()
    
    async def register(self, websocket):
        self.connections.add(websocket)
    
    async def unregister(self, websocket):
        self.connections.discard(websocket)
    
    async def broadcast(self, message: str):
        if self.connections:
            await asyncio.wait([conn.send(message) for conn in self.connections])

ws_manager = WebSocketManager()

# WebSocket server running alongside MCP server
async def websocket_handler(websocket, path):
    await ws_manager.register(websocket)
    try:
        async for message in websocket:
            # Process message
            await ws_manager.broadcast(f"Broadcast: {message}")
    finally:
        await ws_manager.unregister(websocket)

# Start WebSocket server in background
async def start_websocket_server():
    server = await websockets.serve(websocket_handler, "localhost", 8765)
    await server.wait_closed()

# Run WebSocket server in background
import asyncio
asyncio.create_task(start_websocket_server())

@mcp.tool
async def send_broadcast_message(message: str) -> bool:
    """Send message to all WebSocket connections"""
    await ws_manager.broadcast(message)
    return True
```

## Monitoring and Logging Integration

### Prometheus Integration

Add Prometheus metrics:

```python
from prometheus_client import Counter, Histogram
from fastmcp import FastMCP
import time

# Define metrics
REQUEST_COUNT = Counter('fastmcp_requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_TIME = Histogram('fastmcp_request_duration_seconds', 'Request duration')

mcp = FastMCP("Monitored Server")

@mcp.middleware
async def metrics_middleware(ctx, call_next):
    start_time = time.time()
    try:
        response = await call_next(ctx)
        REQUEST_COUNT.labels(method=ctx.method, endpoint=ctx.endpoint).inc()
        return response
    finally:
        REQUEST_TIME.observe(time.time() - start_time)
```

### Logging Integration

Integrate with various logging systems:

```python
import logging
import sys
from pythonjsonlogger import jsonlogger
from fastmcp import FastMCP

# Configure structured logging
logger = logging.getLogger("fastmcp")
logger.setLevel(logging.INFO)

# JSON formatter for structured logs
json_handler = logging.StreamHandler(sys.stdout)
json_handler.setFormatter(jsonlogger.JsonFormatter(
    '%(asctime)s %(name)s %(levelname)s %(message)s'
))
logger.addHandler(json_handler)

mcp = FastMCP("Logging Server")

@mcp.tool
def operation_with_logging(data: str) -> str:
    """Operation with detailed logging"""
    logger.info("Starting operation", extra={"data": data})
    
    try:
        result = f"processed: {data}"
        logger.info("Operation completed", extra={"result": result})
        return result
    except Exception as e:
        logger.error("Operation failed", extra={"error": str(e)})
        raise
```

## Security Best Practices

### Input Validation

Always validate inputs from external integrations:

```python
from pydantic import BaseModel, ValidationError
from fastmcp.errors import McpError

class ExternalData(BaseModel):
    user_id: str
    action: str
    metadata: dict = {}

@mcp.tool
def process_external_data(raw_data: dict) -> str:
    """Process external data with validation"""
    try:
        validated_data = ExternalData(**raw_data)
        # Process validated data
        return f"Processed action: {validated_data.action}"
    except ValidationError as e:
        raise McpError(f"Invalid data format: {e}")
```

### Rate Limiting

Implement rate limiting for external integrations:

```python
from fastmcp.transform import rate_limit

@mcp.tool
@rate_limit(calls=100, per=60)  # 100 calls per minute
def external_api_integration(data: str) -> str:
    """External API call with rate limiting"""
    # Implementation that calls external API
    pass
```

## Next Steps

1. [Authentication](../server-development/authentication.md) - Detailed authentication setup
2. [Security](../deployment/security.md) - Security best practices for deployment
3. [Patterns](../patterns/index.md) - Implementation patterns for integrations