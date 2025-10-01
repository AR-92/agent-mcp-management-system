# Examples

This section provides comprehensive examples of FastMCP applications, from simple to complex use cases. These examples demonstrate practical implementations of the concepts covered in other sections.

## Simple Calculator Server

A basic example showing tools, resources, and prompts:

```python
from fastmcp import FastMCP

mcp = FastMCP("Calculator Server")

# Simple arithmetic tools
@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b

@mcp.tool
def multiply(x: float, y: float) -> float:
    """Multiply two numbers"""
    return x * y

@mcp.tool
def divide(dividend: float, divisor: float) -> float:
    """Divide dividend by divisor"""
    if divisor == 0:
        raise ValueError("Cannot divide by zero")
    return dividend / divisor

# Resources to provide data
@mcp.resource
def pi_value() -> float:
    """Get the value of Pi"""
    return 3.14159265359

@mcp.resource 
def fibonacci_sequence(n: int) -> list:
    """Generate first n numbers in Fibonacci sequence"""
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    
    sequence = [0, 1]
    for i in range(2, n):
        sequence.append(sequence[i-1] + sequence[i-2])
    return sequence

# Prompts for LLM interaction templates
@mcp.prompt
def math_problem_template(operation: str, a: float, b: float) -> str:
    """Template for math problems"""
    return f"Solve this math problem: {a} {operation} {b}"

if __name__ == "__main__":
    mcp.run()
```

## Data Management Server

An example showing database integration and complex data operations:

```python
from fastmcp import FastMCP
import sqlite3
from typing import List, Optional
from pydantic import BaseModel

class User(BaseModel):
    id: Optional[int] = None
    name: str
    email: str
    age: int

class UserManager:
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                age INTEGER
            )
        ''')
        conn.commit()
        conn.close()
    
    def create_user(self, name: str, email: str, age: int) -> User:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
            (name, email, age)
        )
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return User(id=user_id, name=name, email=email, age=age)
    
    def get_user(self, user_id: int) -> Optional[User]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, age FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return User(id=row[0], name=row[1], email=row[2], age=row[3])
        return None
    
    def get_all_users(self) -> List[User]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, age FROM users")
        rows = cursor.fetchall()
        conn.close()
        return [User(id=row[0], name=row[1], email=row[2], age=row[3]) for row in rows]

user_manager = UserManager()

mcp = FastMCP("Data Management Server")

@mcp.tool
def create_user(name: str, email: str, age: int) -> User:
    """Create a new user"""
    return user_manager.create_user(name, email, age)

@mcp.resource
def get_user_by_id(user_id: int) -> Optional[User]:
    """Get user by ID"""
    return user_manager.get_user(user_id)

@mcp.resource
def get_all_users() -> List[User]:
    """Get all users"""
    return user_manager.get_all_users()

if __name__ == "__main__":
    mcp.run()
```

## File Processing Server

An example showing file handling and processing:

```python
from fastmcp import FastMCP
from typing import List, Dict
import json
import csv
from io import StringIO
import os
from pathlib import Path

mcp = FastMCP("File Processing Server")

@mcp.tool
def process_json_file(file_content: str) -> Dict:
    """Process and validate JSON content"""
    try:
        data = json.loads(file_content)
        return {
            "valid": True,
            "keys": list(data.keys()),
            "size": len(json.dumps(data))
        }
    except json.JSONDecodeError as e:
        return {
            "valid": False,
            "error": str(e)
        }

@mcp.tool
def csv_to_json(csv_content: str) -> List[Dict]:
    """Convert CSV content to JSON"""
    # Create a StringIO object from the string
    csv_io = StringIO(csv_content)
    reader = csv.DictReader(csv_io)
    return [row for row in reader]

@mcp.tool
def analyze_text_file(text_content: str) -> Dict:
    """Analyze text content and return statistics"""
    words = text_content.split()
    sentences = [s.strip() for s in text_content.split('.') if s.strip()]
    
    return {
        "word_count": len(words),
        "character_count": len(text_content),
        "sentence_count": len(sentences),
        "average_word_length": sum(len(word) for word in words) / len(words) if words else 0,
        "paragraph_count": text_content.count('\n\n') + 1
    }

@mcp.resource
def file_formats_info() -> Dict:
    """Information about supported file formats"""
    return {
        "supported_formats": ["JSON", "CSV", "TXT", "XML"],
        "max_size_mb": 10,
        "processing_notes": "Files are processed in memory, so keep them reasonably sized"
    }

if __name__ == "__main__":
    mcp.run()
```

## Client Example: Weather Application

A client application that uses external APIs:

```python
import asyncio
from fastmcp import Client, FastMCP
import aiohttp
import os

class WeatherClient:
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "http://api.openweathermap.org/data/2.5"
    
    async def get_current_weather(self, city: str) -> dict:
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/weather"
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric"
            }
            async with session.get(url, params=params) as response:
                return await response.json()

weather_client = WeatherClient()

mcp = FastMCP("Weather Information Server")

@mcp.tool
async def get_weather(city: str) -> dict:
    """Get current weather for a city"""
    return await weather_client.get_current_weather(city)

@mcp.prompt
def weather_summary_prompt(city: str, temperature: float) -> str:
    """Generate a weather summary prompt"""
    return f"Provide a friendly weather update for {city} where the temperature is {temperature}°C."

# Client usage example
async def main():
    # Server
    import threading
    import time
    
    def run_server():
        mcp.run(host="127.0.0.1", port=8000)
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Give server time to start
    time.sleep(1)
    
    # Client
    async with Client("http://127.0.0.1:8000") as client:
        # Get weather
        weather = await client.call_tool("get_weather", {"city": "London"})
        temp = weather.get("main", {}).get("temp", "N/A")
        
        # Generate summary prompt
        summary_prompt = await client.call_tool(
            "weather_summary_prompt", 
            {"city": "London", "temperature": temp}
        )
        
        print(f"Weather: {weather}")
        print(f"Summary prompt: {summary_prompt}")

if __name__ == "__main__":
    # Uncomment to run the example
    # asyncio.run(main())
    mcp.run()
```

## Authentication Example

A server with multiple authentication methods:

```python
from fastmcp import FastMCP
from fastmcp.auth import require_auth, api_key_auth
from fastmcp.errors import AuthenticationError
import os
from typing import List

# Setup authentication
valid_api_keys = {
    "dev-key-123": {"user": "developer", "permissions": ["read", "write"]},
    "admin-key-456": {"user": "admin", "permissions": ["read", "write", "admin"]},
}

api_key_auth.setup(valid_api_keys)

mcp = FastMCP("Secure API Server")

# Public endpoint
@mcp.tool
def public_endpoint() -> str:
    """Public endpoint accessible to all"""
    return "This is a public endpoint"

# API key protected endpoint
@mcp.tool
def protected_by_api_key() -> str:
    """Endpoint requiring API key authentication"""
    return "This endpoint is protected by API key"

# Custom authentication with additional checks
def check_permission(required_permission: str):
    def auth_middleware(ctx):
        # In real app, this would come from the auth context
        user_permissions = getattr(ctx, 'permissions', [])
        if required_permission not in user_permissions:
            raise AuthenticationError(f"Permission {required_permission} required")
    return auth_middleware

@mcp.tool
def admin_only_operation() -> str:
    """Operation only available to admins"""
    return "This is an admin-only operation"

if __name__ == "__main__":
    mcp.run()
```

## Advanced Pattern: Server Composition

Composing multiple specialized servers:

```python
from fastmcp import FastMCP

# User management server
user_server = FastMCP("User Management")

@user_server.tool
def create_user(name: str, email: str) -> dict:
    """Create a user"""
    user_id = f"user_{hash(name + email) % 10000}"
    return {"id": user_id, "name": name, "email": email}

@user_server.tool
def get_user(user_id: str) -> dict:
    """Get user by ID"""
    return {"id": user_id, "name": "Sample User", "email": "sample@example.com"}

# Data processing server
data_server = FastMCP("Data Processing")

@data_server.tool
def process_data(data: str) -> str:
    """Process input data"""
    return f"Processed: {data.upper()}"

@data_server.resource
def get_processing_stats() -> dict:
    """Get processing statistics"""
    return {"processed_count": 12345, "last_processed": "2023-01-01"}

# Analytics server
analytics_server = FastMCP("Analytics")

@analytics_server.tool
def get_user_analytics(user_id: str) -> dict:
    """Get analytics for a user"""
    return {
        "user_id": user_id,
        "page_views": 125,
        "session_duration": 45.2
    }

@analytics_server.resource
def get_global_analytics() -> dict:
    """Get global analytics"""
    return {
        "total_users": 1000,
        "avg_session": 35.5,
        "active_today": 250
    }

# Compose all servers into one
composed_server = FastMCP.compose(user_server, data_server, analytics_server)

print("Available tools in composed server:")
for tool in composed_server._tools:
    print(f"  - {tool.name}")

if __name__ == "__main__":
    # Run the composed server
    composed_server.run()
```

## Docker Deployment Example

A complete example with Docker configuration:

```python
# server.py
from fastmcp import FastMCP
import os

mcp = FastMCP("Dockerized Server")

@mcp.tool
def health_check() -> dict:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "version": "1.0.0"
    }

@mcp.tool
def process_request(data: str) -> str:
    """Process incoming request"""
    return f"Processed: {data}"

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    mcp.run(host=host, port=port)
```

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "server.py"]
```

```docker-compose.yml
# docker-compose.yml
version: '3.8'

services:
  fastmcp-server:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - PORT=8000
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

```txt
# requirements.txt
fastmcp>=2.0.0
aiohttp>=3.8.0
pydantic>=2.0.0
```

## Testing Example

Complete example with testing:

```python
# my_server.py
from fastmcp import FastMCP

mcp = FastMCP("Testable Server")

@mcp.tool
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b

@mcp.tool 
def divide_numbers(numerator: int, denominator: int) -> float:
    """Divide two numbers"""
    if denominator == 0:
        raise ValueError("Cannot divide by zero")
    return numerator / denominator

# test_server.py
import pytest
import asyncio
from fastmcp.testing import MockServer
from fastmcp import Client
from my_server import mcp

@pytest.mark.asyncio
async def test_add_numbers():
    async with MockServer(mcp) as server:
        async with Client(server.url) as client:
            result = await client.call_tool(
                "add_numbers", 
                {"a": 5, "b": 3}
            )
            assert result == 8

@pytest.mark.asyncio
async def test_divide_numbers():
    async with MockServer(mcp) as server:
        async with Client(server.url) as client:
            result = await client.call_tool(
                "divide_numbers",
                {"numerator": 10, "denominator": 2}
            )
            assert result == 5.0

@pytest.mark.asyncio
async def test_divide_by_zero():
    async with MockServer(mcp) as server:
        async with Client(server.url) as client:
            # This should raise an error
            with pytest.raises(Exception):
                await client.call_tool(
                    "divide_numbers",
                    {"numerator": 10, "denominator": 0}
                )
```

## Real-World Example: Content Management System

```python
from fastmcp import FastMCP
from pydantic import BaseModel
from typing import List, Optional
import datetime
import uuid

class ContentItem(BaseModel):
    id: str
    title: str
    content: str
    author: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    tags: List[str]
    published: bool = False

class ContentManager:
    def __init__(self):
        self._items: dict[str, ContentItem] = {}
    
    def create_item(self, title: str, content: str, author: str, tags: List[str]) -> ContentItem:
        item_id = str(uuid.uuid4())
        now = datetime.datetime.now()
        item = ContentItem(
            id=item_id,
            title=title,
            content=content,
            author=author,
            created_at=now,
            updated_at=now,
            tags=tags or []
        )
        self._items[item_id] = item
        return item
    
    def get_item(self, item_id: str) -> Optional[ContentItem]:
        return self._items.get(item_id)
    
    def update_item(self, item_id: str, **updates) -> Optional[ContentItem]:
        if item_id not in self._items:
            return None
        
        item = self._items[item_id]
        for key, value in updates.items():
            if hasattr(item, key):
                setattr(item, key, value)
        
        item.updated_at = datetime.datetime.now()
        return item
    
    def list_items(self, author: Optional[str] = None, tag: Optional[str] = None) -> List[ContentItem]:
        items = list(self._items.values())
        
        if author:
            items = [item for item in items if item.author == author]
        
        if tag:
            items = [item for item in items if tag in item.tags]
        
        return sorted(items, key=lambda x: x.created_at, reverse=True)
    
    def publish_item(self, item_id: str) -> bool:
        item = self.get_item(item_id)
        if item:
            item.published = True
            item.updated_at = datetime.datetime.now()
            return True
        return False

content_manager = ContentManager()

mcp = FastMCP("Content Management Server")

@mcp.tool
def create_content(title: str, content: str, author: str, tags: List[str] = []) -> ContentItem:
    """Create a new content item"""
    return content_manager.create_item(title, content, author, tags)

@mcp.tool
def get_content(item_id: str) -> Optional[ContentItem]:
    """Get a content item by ID"""
    return content_manager.get_item(item_id)

@mcp.tool
def update_content(item_id: str, **updates) -> Optional[ContentItem]:
    """Update a content item"""
    return content_manager.update_item(item_id, **updates)

@mcp.tool
def publish_content(item_id: str) -> bool:
    """Publish a content item"""
    return content_manager.publish_item(item_id)

@mcp.resource
def list_content(author: Optional[str] = None, tag: Optional[str] = None) -> List[ContentItem]:
    """List content items with optional filters"""
    return content_manager.list_items(author, tag)

@mcp.prompt
def content_summary_prompt(title: str, content: str) -> str:
    """Generate a summary prompt for content"""
    return f"Please provide a brief summary of the following content titled '{title}':\n\n{content}"

if __name__ == "__main__":
    mcp.run()
```

## Next Steps

1. [Getting Started](../installation/index.md) - Install and set up FastMCP
2. [Core Concepts](../core-concepts/index.md) - Understand fundamental concepts
3. [Server Development](../server-development/index.md) - Build your own servers
4. Try modifying these examples to create your own applications