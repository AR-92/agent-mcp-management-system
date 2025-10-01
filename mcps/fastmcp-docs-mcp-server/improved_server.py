#!/usr/bin/env python3
"""
Improved FastMCP Documentation MCP Server

This server provides access to FastMCP documentation for LLMs.
It allows LLMs to search, read, and get information about FastMCP framework.
"""

from fastmcp import FastMCP
from typing import List, Dict, Any, Optional
import os
import glob
from pathlib import Path
import re
import logging
import hashlib
from datetime import datetime, timedelta
import time
import asyncio
from pydantic import BaseModel, validator, Field
import json
import yaml
import pathlib  # Import here after other imports

# Set up logging
logging.basicConfig(
    level=os.getenv("FASTMCP_LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration class for server settings
class ServerConfig:
    """Configuration class to manage server settings"""
    
    def __init__(self):
        # Server settings
        self.name = os.getenv("FASTMCP_SERVER_NAME", "FastMCP Documentation Server")
        self.version = os.getenv("FASTMCP_VERSION", "2.0.0")
        self.instructions = os.getenv("FASTMCP_INSTRUCTIONS", "Provides access to FastMCP documentation for LLMs")
        
        # Documentation path settings
        self.docs_base_path = os.getenv(
            "DOCS_BASE_PATH", 
            str(pathlib.Path(__file__).parent.parent.parent / "docs" / "fastmcp_docs")
        )
        
        # Cache settings
        self.cache_max_size = int(os.getenv("CACHE_MAX_SIZE", "100"))
        self.cache_ttl = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes in seconds
        
        # Rate limiting settings
        self.rate_limit_max_requests = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "100"))
        self.rate_limit_window = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # 1 hour in seconds
        
        # Server settings
        self.host = os.getenv("FASTMCP_HOST", "127.0.0.1")
        self.port = int(os.getenv("FASTMCP_PORT", "8001"))
        self.log_level = os.getenv("FASTMCP_LOG_LEVEL", "INFO")
        
        # Security settings
        self.allow_directory_traversal = os.getenv("ALLOW_DIRECTORY_TRAVERSAL", "false").lower() == "true"
        
        # Load from config file if it exists
        self.load_from_config_file()
    
    def load_from_config_file(self):
        """Load configuration from config.json file if it exists"""
        config_file_paths = [
            os.path.join(os.path.dirname(__file__), "config.json"),
            os.path.join(os.path.dirname(__file__), "config.yaml"),
            os.path.join(os.path.dirname(__file__), "config.yml")
        ]
        
        for config_path in config_file_paths:
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        if config_path.endswith('.json'):
                            config_data = json.load(f)
                        else:  # YAML file
                            config_data = yaml.safe_load(f)
                    
                    # Update configuration from file
                    for key, value in config_data.items():
                        if hasattr(self, key):
                            setattr(self, key, value)
                    
                    logger.info(f"Configuration loaded from {config_path}")
                    return
                except Exception as e:
                    logger.error(f"Error loading configuration from {config_path}: {e}")
    
    def to_dict(self):
        """Convert configuration to dictionary for debugging/inspection"""
        return {
            'name': self.name,
            'version': self.version,
            'docs_base_path': self.docs_base_path,
            'cache_max_size': self.cache_max_size,
            'cache_ttl': self.cache_ttl,
            'rate_limit_max_requests': self.rate_limit_max_requests,
            'rate_limit_window': self.rate_limit_window,
            'host': self.host,
            'port': self.port,
            'log_level': self.log_level,
            'allow_directory_traversal': self.allow_directory_traversal
        }

# Load configuration
config = ServerConfig()

# Initialize the MCP server with configuration
mcp = FastMCP(
    name=config.name,
    instructions=config.instructions,
    version=config.version
)

# Use configured documentation path
DOCS_BASE_PATH = config.docs_base_path

# Cache for storing search results and file contents
class DocumentCache:
    def __init__(self, max_size: int = None, ttl: int = None):
        # Use config values if available, otherwise defaults
        self.max_size = max_size if max_size is not None else config.cache_max_size
        self.ttl = ttl if ttl is not None else config.cache_ttl
        self.cache = {}
        self.access_times = {}
    
    def _is_expired(self, key: str) -> bool:
        if key not in self.access_times:
            return True
        return time.time() - self.access_times[key] > self.ttl
    
    def get(self, key: str):
        if key in self.cache and not self._is_expired(key):
            self.access_times[key] = time.time()
            return self.cache[key]
        elif key in self.cache:
            # Remove expired entry
            del self.cache[key]
            del self.access_times[key]
        return None
    
    def set(self, key: str, value):
        # Remove oldest entries if cache is full
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
            del self.cache[oldest_key]
            del self.access_times[oldest_key]
        
        self.cache[key] = value
        self.access_times[key] = time.time()
    
    def clear(self):
        self.cache.clear()
        self.access_times.clear()

# Initialize cache
doc_cache = DocumentCache()

# Rate limiting
class RateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    def is_allowed(self, identifier: str = "default") -> bool:
        now = time.time()
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        # Remove old requests outside the window
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if now - req_time < self.window_seconds
        ]
        
        if len(self.requests[identifier]) >= self.max_requests:
            return False
        
        # Add current request
        self.requests[identifier].append(now)
        return True

rate_limiter = RateLimiter()

def validate_file_path(file_path: str) -> str:
    """Validate and sanitize file paths to prevent directory traversal"""
    if not file_path or not isinstance(file_path, str):
        raise ValueError("Invalid file path: path must be a non-empty string")
    
    # Security check: ensure the path is within the docs directory
    requested_path = os.path.abspath(os.path.join(DOCS_BASE_PATH, file_path))
    base_path = os.path.abspath(DOCS_BASE_PATH)
    
    if not requested_path.startswith(base_path):
        raise ValueError("Invalid file path: directory traversal detected")
    
    # Additional checks
    if '..' in file_path or './' in file_path:
        raise ValueError("Invalid file path: contains invalid path characters")
    
    # Only allow markdown files
    if not file_path.lower().endswith(('.md', '.txt')):
        raise ValueError("Invalid file path: only markdown and text files allowed")
    
    return file_path

def get_cache_key(*args, **kwargs) -> str:
    """Generate a cache key from function arguments"""
    key_data = str(args) + str(sorted(kwargs.items()))
    return hashlib.md5(key_data.encode()).hexdigest()

def rate_limit_check(identifier: str = "default"):
    """Decorator to check rate limiting"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not rate_limiter.is_allowed(identifier):
                raise Exception(f"Rate limit exceeded for {identifier}")
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Tool functions with improved error handling and validation

@mcp.tool
def list_documentation_sections() -> List[str]:
    """
    List all available documentation sections
    """
    try:
        logger.info("Listing documentation sections")
        
        cache_key = get_cache_key("list_documentation_sections")
        cached_result = doc_cache.get(cache_key)
        if cached_result is not None:
            logger.info("Returning cached result for list_documentation_sections")
            return cached_result
        
        sections = []
        if not os.path.exists(DOCS_BASE_PATH):
            logger.error(f"Documentation base path does not exist: {DOCS_BASE_PATH}")
            raise FileNotFoundError(f"Documentation directory not found: {DOCS_BASE_PATH}")
        
        for item in os.listdir(DOCS_BASE_PATH):
            item_path = os.path.join(DOCS_BASE_PATH, item)
            if os.path.isdir(item_path):
                sections.append(item)
        sections.append("index.md")  # Add the main index
        
        result = sorted(sections)
        doc_cache.set(cache_key, result)
        logger.info(f"Found {len(result)} documentation sections")
        return result
    
    except Exception as e:
        logger.error(f"Error listing documentation sections: {str(e)}")
        raise


@mcp.tool
def search_documentation(query: str) -> List[Dict[str, str]]:
    """
    Search for documentation files that contain the query string
    Uses sophisticated search with scoring based on match quality
    """
    try:
        logger.info(f"Searching documentation for query: {query}")
        
        if not query or not isinstance(query, str):
            logger.warning("Empty or invalid query provided")
            return []
        
        # Rate limit check
        if not rate_limiter.is_allowed("search"):
            logger.warning("Rate limit exceeded for search operation")
            raise Exception("Rate limit exceeded. Please try again later.")
        
        cache_key = get_cache_key("search_documentation", query)
        cached_result = doc_cache.get(cache_key)
        if cached_result is not None:
            logger.info("Returning cached result for search_documentation")
            return cached_result
        
        results = []
        query_lower = query.lower()
        
        # Tokenize query for better matching
        query_tokens = re.findall(r'\b\w+\b', query_lower)
        
        # Search in all markdown and text files
        for root, dirs, files in os.walk(DOCS_BASE_PATH):
            for file in files:
                if file.lower().endswith(('.md', '.txt')):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, DOCS_BASE_PATH)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        content_lower = content.lower()
                        
                        # Calculate match score based on multiple factors
                        score = 0
                        snippet_info = None
                        
                        # Check for exact phrase matches (highest score)
                        if query_lower in content_lower:
                            score += 100
                            
                            # Find the first occurrence of the query and extract a snippet
                            start_idx = content_lower.find(query_lower)
                            if start_idx != -1:
                                # Find context around the match
                                start_context = max(0, start_idx - 100)
                                end_context = min(start_idx + len(query) + 100, len(content))
                                
                                snippet = content[start_context:end_context]
                                if start_context > 0:
                                    snippet = "... " + snippet
                                if end_context < len(content):
                                    snippet += " ..."
                                
                                snippet_info = {
                                    "file": relative_path,
                                    "snippet": snippet,
                                    "path": file_path,
                                    "score": score
                                }
                        
                        # Check for individual token matches
                        for token in query_tokens:
                            if token in content_lower:
                                score += 10  # Add to score for each token match
                                
                        # If we have a match (either phrase or token), add to results
                        if score > 0:
                            if snippet_info is None:  # This was just a token match
                                # Find a context that includes at least one of the query tokens
                                start_idx = len(content)  # Default to end of content
                                for token in query_tokens:
                                    token_pos = content_lower.find(token)
                                    if token_pos != -1:
                                        start_idx = min(start_idx, token_pos)
                                
                                if start_idx < len(content):
                                    start_context = max(0, start_idx - 100)
                                    end_context = min(start_idx + 50, len(content))
                                    
                                    snippet = content[start_context:end_context]
                                    if start_context > 0:
                                        snippet = "... " + snippet
                                    if end_context < len(content):
                                        snippet += " ..."
                                    
                                    snippet_info = {
                                        "file": relative_path,
                                        "snippet": snippet,
                                        "path": file_path,
                                        "score": score
                                    }
                            
                            # Update score in the snippet_info
                            snippet_info["score"] = score
                            results.append(snippet_info)
                            
                    except Exception as e:
                        logger.error(f"Error reading file {file_path}: {str(e)}")
                        continue  # Continue with other files
        
        # Sort results by score (descending)
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        # Remove the score from the result before returning (for compatibility with original format)
        for result in results:
            result.pop("score", None)
        
        doc_cache.set(cache_key, results)
        logger.info(f"Search completed, found {len(results)} results for query: {query}")
        return results
    
    except Exception as e:
        logger.error(f"Error searching documentation for '{query}': {str(e)}")
        raise


@mcp.tool
def read_documentation_file(file_path: str) -> str:
    """
    Read the content of a specific documentation file
    """
    try:
        logger.info(f"Reading documentation file: {file_path}")
        
        # Rate limit check
        if not rate_limiter.is_allowed("read_file"):
            logger.warning(f"Rate limit exceeded for reading file: {file_path}")
            raise Exception("Rate limit exceeded. Please try again later.")
        
        validated_path = validate_file_path(file_path)
        
        cache_key = get_cache_key("read_documentation_file", validated_path)
        cached_result = doc_cache.get(cache_key)
        if cached_result is not None:
            logger.info(f"Returning cached result for file: {validated_path}")
            return cached_result
        
        requested_path = os.path.abspath(os.path.join(DOCS_BASE_PATH, validated_path))
        
        if not os.path.exists(requested_path):
            logger.error(f"Documentation file not found: {validated_path}")
            raise FileNotFoundError(f"Documentation file not found: {validated_path}")
        
        if not os.path.isfile(requested_path):
            logger.error(f"Path is not a file: {validated_path}")
            raise ValueError(f"Path is not a file: {validated_path}")
        
        with open(requested_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        doc_cache.set(cache_key, content)
        logger.info(f"Successfully read file: {validated_path}")
        return content
    
    except ValueError as e:
        logger.error(f"Validation error reading file {file_path}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error reading documentation file {file_path}: {str(e)}")
        raise


@mcp.resource("http://fastmcp-docs.local/table-of-contents")
def get_documentation_toc() -> Dict[str, Any]:
    """
    Get the table of contents for the FastMCP documentation
    """
    try:
        logger.info("Getting documentation table of contents")
        
        cache_key = get_cache_key("get_documentation_toc")
        cached_result = doc_cache.get(cache_key)
        if cached_result is not None:
            logger.info("Returning cached result for get_documentation_toc")
            return cached_result
        
        toc = {
            "title": "FastMCP Documentation",
            "description": "Comprehensive documentation for the FastMCP framework",
            "sections": {},
            "last_updated": datetime.now().isoformat()
        }
        
        # Add the main index
        index_path = os.path.join(DOCS_BASE_PATH, "index.md")
        if os.path.exists(index_path):
            try:
                with open(index_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Extract the title from the markdown
                    lines = content.split('\n')
                    title = "FastMCP Documentation"
                    for line in lines:
                        if line.startswith('# '):
                            title = line[2:].strip()
                            break
                toc["sections"]["index"] = {
                    "title": title,
                    "path": "index.md",
                    "description": "Main documentation index"
                }
            except Exception as e:
                logger.error(f"Error reading index file: {str(e)}")
                toc["sections"]["index"] = {
                    "title": "FastMCP Documentation",
                    "path": "index.md",
                    "description": "Main documentation index (error reading details)"
                }
        
        # Add other sections
        for item in os.listdir(DOCS_BASE_PATH):
            item_path = os.path.join(DOCS_BASE_PATH, item)
            if os.path.isdir(item_path):
                # Look for index.md in the subdirectory
                section_index = os.path.join(item_path, "index.md")
                if os.path.exists(section_index):
                    try:
                        with open(section_index, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Extract the title from the markdown
                            lines = content.split('\n')
                            title = item
                            description = ""
                            for line in lines:
                                if line.startswith('# '):
                                    title = line[2:].strip()
                                elif line.strip() and not line.startswith('#'):
                                    description = line.strip()
                                    break
                        toc["sections"][item] = {
                            "title": title,
                            "path": f"{item}/index.md",
                            "description": description
                        }
                    except Exception as e:
                        logger.error(f"Error reading section index for {item}: {str(e)}")
                        toc["sections"][item] = {
                            "title": item,
                            "path": f"{item}/index.md",
                            "description": f"Section {item} (error reading details)"
                        }
        
        doc_cache.set(cache_key, toc)
        logger.info("Successfully generated documentation TOC")
        return toc
    
    except Exception as e:
        logger.error(f"Error getting documentation TOC: {str(e)}")
        raise


@mcp.tool
def get_section_files(section: str) -> List[str]:
    """
    Get all files in a specific documentation section
    """
    try:
        logger.info(f"Getting files for section: {section}")
        
        # Validate section name
        if not section or not isinstance(section, str):
            logger.error("Invalid section name provided")
            raise ValueError("Section name must be a non-empty string")
        
        # Rate limit check
        if not rate_limiter.is_allowed("get_section_files"):
            logger.warning(f"Rate limit exceeded for getting section files: {section}")
            raise Exception("Rate limit exceeded. Please try again later.")
        
        section_path = os.path.join(DOCS_BASE_PATH, section)
        if not os.path.exists(section_path):
            logger.error(f"Section not found: {section}")
            raise ValueError(f"Section not found: {section}")
        
        if not os.path.isdir(section_path):
            logger.error(f"Path is not a directory: {section}")
            raise ValueError(f"Path is not a directory: {section}")
        
        cache_key = get_cache_key("get_section_files", section)
        cached_result = doc_cache.get(cache_key)
        if cached_result is not None:
            logger.info(f"Returning cached result for section: {section}")
            return cached_result
        
        files = []
        for root, dirs, filenames in os.walk(section_path):
            for filename in filenames:
                if filename.lower().endswith(('.md', '.txt')):
                    relative_path = os.path.relpath(os.path.join(root, filename), DOCS_BASE_PATH)
                    files.append(relative_path)
        
        result = sorted(files)
        doc_cache.set(cache_key, result)
        logger.info(f"Found {len(result)} files in section: {section}")
        return result
    
    except ValueError as e:
        logger.error(f"Validation error getting section files for {section}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error getting files for section {section}: {str(e)}")
        raise


@mcp.prompt("/fastmcp-concept-explanation")
def explain_fastmcp_concept(concept: str, context: str = "") -> str:
    """
    Generate a prompt to explain a FastMCP concept with context
    """
    try:
        logger.info(f"Generating concept explanation for: {concept}")
        
        if not concept or not isinstance(concept, str):
            logger.warning("Invalid concept provided for explanation")
            raise ValueError("Concept must be a non-empty string")
        
        # Rate limit check
        if not rate_limiter.is_allowed("explain_concept"):
            logger.warning(f"Rate limit exceeded for explaining concept: {concept}")
            raise Exception("Rate limit exceeded. Please try again later.")
        
        result = f"""
Explain the FastMCP concept '{concept}' in detail.

Context: {context}

Please provide a comprehensive explanation of this concept including:
1. What it is
2. Why it's important
3. How it works
4. When to use it
5. Code examples if applicable
6. Best practices
7. Common pitfalls to avoid
"""
        logger.info(f"Generated concept explanation prompt for: {concept}")
        return result
    
    except ValueError as e:
        logger.error(f"Validation error in explain_fastmcp_concept for {concept}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error generating concept explanation for {concept}: {str(e)}")
        raise


@mcp.prompt("/fastmcp-implementation-guide")
def implementation_guide_prompt(topic: str, requirements: str = "") -> str:
    """
    Generate a prompt for implementing a FastMCP feature
    """
    try:
        logger.info(f"Generating implementation guide for: {topic}")
        
        if not topic or not isinstance(topic, str):
            logger.warning("Invalid topic provided for implementation guide")
            raise ValueError("Topic must be a non-empty string")
        
        # Rate limit check
        if not rate_limiter.is_allowed("implementation_guide"):
            logger.warning(f"Rate limit exceeded for implementation guide: {topic}")
            raise Exception("Rate limit exceeded. Please try again later.")
        
        result = f"""
Provide a detailed implementation guide for: {topic}

Requirements: {requirements}

Include:
1. Step-by-step instructions
2. Code examples
3. Best practices
4. Common pitfalls to avoid
5. Configuration requirements
6. Testing strategies
7. Performance considerations
"""
        logger.info(f"Generated implementation guide prompt for: {topic}")
        return result
    
    except ValueError as e:
        logger.error(f"Validation error in implementation_guide_prompt for {topic}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error generating implementation guide for {topic}: {str(e)}")
        raise


@mcp.resource("http://fastmcp-docs.local/latest-updates")
def get_latest_docs_updates() -> List[Dict[str, Any]]:
    """
    Get information about recently updated documentation
    """
    try:
        logger.info("Getting latest documentation updates")
        
        cache_key = get_cache_key("get_latest_docs_updates")
        cached_result = doc_cache.get(cache_key)
        if cached_result is not None:
            logger.info("Returning cached result for get_latest_docs_updates")
            return cached_result
        
        updates = []
        
        # Find all markdown and text files and get their modification times
        md_files = glob.glob(f"{DOCS_BASE_PATH}/**/*", recursive=True)
        # Filter for markdown and text files
        md_files = [f for f in md_files if os.path.isfile(f) and 
                    f.lower().endswith(('.md', '.txt'))]
        
        # Sort by modification time (most recent first)
        md_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        for file_path in md_files[:20]:  # Get the 20 most recently modified files
            rel_path = os.path.relpath(file_path, DOCS_BASE_PATH)
            mod_time = os.path.getmtime(file_path)
            mod_time_str = datetime.fromtimestamp(mod_time).isoformat()
            
            updates.append({
                "file": rel_path,
                "modified": mod_time_str,
                "size": os.path.getsize(file_path)
            })
        
        doc_cache.set(cache_key, updates)
        logger.info(f"Retrieved {len(updates)} recent documentation updates")
        return updates
    
    except Exception as e:
        logger.error(f"Error getting latest docs updates: {str(e)}")
        raise


@mcp.tool
def find_examples_for_feature(feature: str) -> List[Dict[str, str]]:
    """
    Find documentation examples related to a specific feature
    """
    try:
        logger.info(f"Finding examples for feature: {feature}")
        
        if not feature or not isinstance(feature, str):
            logger.warning("Invalid feature provided for example search")
            return []
        
        # Rate limit check
        if not rate_limiter.is_allowed("find_examples"):
            logger.warning(f"Rate limit exceeded for finding examples for feature: {feature}")
            raise Exception("Rate limit exceeded. Please try again later.")
        
        cache_key = get_cache_key("find_examples_for_feature", feature)
        cached_result = doc_cache.get(cache_key)
        if cached_result is not None:
            logger.info(f"Returning cached results for feature examples: {feature}")
            return cached_result
        
        results = []
        
        # Look for example files in the examples directory
        examples_dir = os.path.join(DOCS_BASE_PATH, "examples")
        if os.path.exists(examples_dir):
            for root, dirs, files in os.walk(examples_dir):
                for file in files:
                    if file.lower().endswith(('.md', '.txt')):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                
                            # Check if the content contains the feature
                            if feature.lower() in content.lower():
                                # Extract relevant snippets
                                content_lower = content.lower()
                                feature_matches = list(re.finditer(re.escape(feature.lower()), content_lower))
                                
                                for match in feature_matches[:3]:  # Take up to 3 occurrences
                                    start = max(0, match.start() - 100)
                                    end = min(len(content), match.start() + len(feature) + 100)
                                    snippet = content[start:end]
                                    
                                    results.append({
                                        "file": os.path.relpath(file_path, DOCS_BASE_PATH),
                                        "snippet": f"...{snippet}...",
                                        "path": file_path
                                    })
                        except Exception as e:
                            logger.error(f"Error reading example file {file_path}: {str(e)}")
                            continue  # Continue with other files
        else:
            logger.info(f"Examples directory does not exist: {examples_dir}")
        
        doc_cache.set(cache_key, results)
        logger.info(f"Found {len(results)} examples for feature: {feature}")
        return results
    
    except Exception as e:
        logger.error(f"Error finding examples for feature {feature}: {str(e)}")
        raise


# Admin/Utility functions that don't need to be MCP tools
def get_cache_stats():
    """Get cache statistics for admin purposes"""
    return {
        "cache_size": len(doc_cache.cache),
        "cache_keys": list(doc_cache.cache.keys()),
        "max_size": doc_cache.max_size,
        "ttl_seconds": doc_cache.ttl
    }


def clear_cache():
    """Clear the document cache"""
    doc_cache.clear()
    logger.info("Document cache cleared")
    return {"message": "Cache cleared successfully"}


if __name__ == "__main__":
    # Use configured values
    print(f"Starting FastMCP Documentation Server on {config.host}:{config.port}")
    print(f"Server: {mcp.name}")
    print(f"Version: {mcp.version}")
    print(f"Documentation base path: {DOCS_BASE_PATH}")
    print(f"Logging level: {config.log_level}")
    print(f"Cache size: {config.cache_max_size}, TTL: {config.cache_ttl}s")
    print(f"Rate limit: {config.rate_limit_max_requests} requests per {config.rate_limit_window}s")
    print(f"Configuration loaded from environment and config files")
    
    # Update logging level based on config
    logging.getLogger().setLevel(config.log_level)
    
    # Use stdio transport for MCP server (proper MCP protocol communication)
    import asyncio
    asyncio.run(mcp.run_stdio_async())