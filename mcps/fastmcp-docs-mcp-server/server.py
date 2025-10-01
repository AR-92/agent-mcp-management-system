#!/usr/bin/env python3
"""
Improved FastMCP Documentation MCP Server with Testable Functions

This server provides access to FastMCP documentation for LLMs.
It allows LLMs to search, read, and get information about FastMCP framework.
"""

import pathlib  # Import at the top to use in config
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
    def __init__(self, max_requests: int = None, window_seconds: int = None):
        self.max_requests = max_requests if max_requests is not None else config.rate_limit_max_requests
        self.window_seconds = window_seconds if window_seconds is not None else config.rate_limit_window
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


# Core function implementations (not decorated, so they can be tested directly)
def _list_documentation_sections_impl() -> List[str]:
    """
    List all available documentation sections - core implementation
    """
    try:
        logger.info("Listing documentation sections")
        
        cache_key = get_cache_key("_list_documentation_sections_impl")
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


def _search_documentation_impl(query: str) -> List[Dict[str, str]]:
    """
    Search for documentation files that contain the query string - core implementation
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
        
        cache_key = get_cache_key("_search_documentation_impl", query)
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


def _read_documentation_file_impl(file_path: str) -> str:
    """
    Read the content of a specific documentation file - core implementation
    """
    try:
        logger.info(f"Reading documentation file: {file_path}")
        
        # Rate limit check
        if not rate_limiter.is_allowed("read_file"):
            logger.warning(f"Rate limit exceeded for reading file: {file_path}")
            raise Exception("Rate limit exceeded. Please try again later.")
        
        validated_path = validate_file_path(file_path)
        
        cache_key = get_cache_key("_read_documentation_file_impl", validated_path)
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


def _get_documentation_toc_impl() -> Dict[str, Any]:
    """
    Get the table of contents for the FastMCP documentation - core implementation
    """
    try:
        logger.info("Getting documentation table of contents")
        
        cache_key = get_cache_key("_get_documentation_toc_impl")
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


def _get_section_files_impl(section: str) -> List[str]:
    """
    Get all files in a specific documentation section - core implementation
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
        
        cache_key = get_cache_key("_get_section_files_impl", section)
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


def _explain_fastmcp_concept_impl(concept: str, context: str = "") -> str:
    """
    Generate a prompt to explain a FastMCP concept with context - core implementation
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


def _implementation_guide_prompt_impl(topic: str, requirements: str = "") -> str:
    """
    Generate a prompt for implementing a FastMCP feature - core implementation
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


def _get_latest_docs_updates_impl() -> List[Dict[str, Any]]:
    """
    Get information about recently updated documentation - core implementation
    """
    try:
        logger.info("Getting latest documentation updates")
        
        cache_key = get_cache_key("_get_latest_docs_updates_impl")
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


def _find_examples_for_feature_impl(feature: str) -> List[Dict[str, str]]:
    """
    Find documentation examples related to a specific feature - core implementation
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
        
        cache_key = get_cache_key("_find_examples_for_feature_impl", feature)
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


# MCP Decorated Functions (for the MCP protocol)
@mcp.tool
def list_documentation_sections() -> List[str]:
    """MCP tool to list all available documentation sections"""
    return _list_documentation_sections_impl()


@mcp.tool
def search_documentation(query: str) -> List[Dict[str, str]]:
    """MCP tool to search for documentation files that contain the query string"""
    return _search_documentation_impl(query)


@mcp.tool
def read_documentation_file(file_path: str) -> str:
    """MCP tool to read the content of a specific documentation file"""
    return _read_documentation_file_impl(file_path)


@mcp.resource("http://fastmcp-docs.local/table-of-contents")
def get_documentation_toc() -> Dict[str, Any]:
    """MCP resource to get the table of contents for the FastMCP documentation"""
    return _get_documentation_toc_impl()


@mcp.tool
def get_section_files(section: str) -> List[str]:
    """MCP tool to get all files in a specific documentation section"""
    return _get_section_files_impl(section)


@mcp.prompt("/fastmcp-concept-explanation")
def explain_fastmcp_concept(concept: str, context: str = "") -> str:
    """MCP prompt to explain a FastMCP concept with context"""
    return _explain_fastmcp_concept_impl(concept, context)


@mcp.prompt("/fastmcp-implementation-guide")
def implementation_guide_prompt(topic: str, requirements: str = "") -> str:
    """MCP prompt to generate a prompt for implementing a FastMCP feature"""
    return _implementation_guide_prompt_impl(topic, requirements)


@mcp.resource("http://fastmcp-docs.local/latest-updates")
def get_latest_docs_updates() -> List[Dict[str, Any]]:
    """MCP resource to get information about recently updated documentation"""
    return _get_latest_docs_updates_impl()


@mcp.tool
def find_examples_for_feature(feature: str) -> List[Dict[str, str]]:
    """MCP tool to find documentation examples related to a specific feature"""
    return _find_examples_for_feature_impl(feature)


# Core implementation functions for additional tools

def _count_docs_in_section_impl(section: str) -> int:
    """
    Count the number of documentation files in a specific section - core implementation
    """
    try:
        files = _get_section_files_impl(section)
        return len(files)
    except Exception as e:
        logger.error(f"Error counting docs in section {section}: {str(e)}")
        raise


def _search_by_file_type_impl(file_type: str = "md") -> List[str]:
    """
    Search for documentation files by type (md, txt, etc.) - core implementation
    """
    try:
        logger.info(f"Searching documentation by file type: {file_type}")
        
        if not file_type or not isinstance(file_type, str):
            file_type = "md"
        
        # Ensure file_type starts with a dot
        if not file_type.startswith('.'):
            file_type = '.' + file_type
            
        results = []
        for root, dirs, files in os.walk(DOCS_BASE_PATH):
            for file in files:
                if file.lower().endswith(file_type.lower()):
                    relative_path = os.path.relpath(os.path.join(root, file), DOCS_BASE_PATH)
                    results.append(relative_path)
        
        return sorted(results)
    
    except Exception as e:
        logger.error(f"Error searching by file type {file_type}: {str(e)}")
        raise


def _get_file_metadata_impl(file_path: str) -> Dict[str, Any]:
    """
    Get metadata for a specific documentation file including size, creation/modification dates - core implementation
    """
    try:
        validated_path = validate_file_path(file_path)
        
        full_path = os.path.abspath(os.path.join(DOCS_BASE_PATH, validated_path))
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"Documentation file not found: {validated_path}")
        
        stat_info = os.stat(full_path)
        import datetime
        modification_time = datetime.datetime.fromtimestamp(stat_info.st_mtime).isoformat()
        creation_time = datetime.datetime.fromtimestamp(stat_info.st_ctime).isoformat()
        
        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        return {
            "file_path": validated_path,
            "size_bytes": stat_info.st_size,
            "modification_time": modification_time,
            "creation_time": creation_time,
            "word_count": len(content.split()),
            "line_count": len(content.splitlines()),
            "char_count": len(content)
        }
    except Exception as e:
        logger.error(f"Error getting metadata for file {file_path}: {str(e)}")
        raise


def _get_recently_accessed_docs_impl(limit: int = 10) -> List[str]:
    """
    Get a list of recently accessed documentation files (based on cache) - core implementation
    """
    try:
        # Sort cache items by access time (most recent first)
        sorted_keys = sorted(
            doc_cache.access_times.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        recent_docs = []
        for key, _ in sorted_keys[:limit]:
            # Extract file path from cache key if possible
            recent_docs.append(key)
        
        return recent_docs
    except Exception as e:
        logger.error(f"Error getting recently accessed docs: {str(e)}")
        raise


def _get_documentation_stats_impl() -> Dict[str, Any]:
    """
    Get comprehensive statistics about the documentation - core implementation
    """
    try:
        logger.info("Getting documentation statistics")
        
        cache_key = get_cache_key("_get_documentation_stats_impl")
        cached_result = doc_cache.get(cache_key)
        if cached_result is not None:
            logger.info("Returning cached result for get_documentation_stats")
            return cached_result
        
        stats = {
            "total_sections": 0,
            "total_files": 0,
            "total_size": 0,
            "file_types": {},
            "last_updated": datetime.now().isoformat()
        }
        
        for root, dirs, files in os.walk(DOCS_BASE_PATH):
            for file in files:
                if file.lower().endswith(('.md', '.txt')):
                    file_path = os.path.join(root, file)
                    stats["total_files"] += 1
                    stats["total_size"] += os.path.getsize(file_path)
                    
                    # Track file types
                    ext = os.path.splitext(file)[1]
                    if ext in stats["file_types"]:
                        stats["file_types"][ext] += 1
                    else:
                        stats["file_types"][ext] = 1
        
        # Count sections
        stats["total_sections"] = len(_list_documentation_sections_impl()) - 1  # -1 to exclude index.md
        
        doc_cache.set(cache_key, stats)
        return stats
    except Exception as e:
        logger.error(f"Error getting documentation stats: {str(e)}")
        raise


def _get_server_health_impl() -> Dict[str, Any]:
    """
    Get the health status of the documentation server - core implementation
    """
    try:
        logger.info("Getting server health")
        
        is_docs_path_accessible = os.path.exists(DOCS_BASE_PATH)
        
        health = {
            "status": "healthy" if is_docs_path_accessible else "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "docs_path_accessible": is_docs_path_accessible,
            "docs_path": DOCS_BASE_PATH,
            "cache_stats": get_cache_stats(),
            "server_config": {
                "name": config.name,
                "version": config.version,
                "host": config.host,
                "port": config.port
            }
        }
        
        return health
    except Exception as e:
        logger.error(f"Error getting server health: {str(e)}")
        raise


def _best_practices_prompt_impl(topic: str, context: str = "") -> str:
    """
    Generate a prompt about best practices for a specific FastMCP topic - core implementation
    """
    try:
        logger.info(f"Generating best practices prompt for: {topic}")
        
        if not topic or not isinstance(topic, str):
            logger.warning("Invalid topic provided for best practices")
            raise ValueError("Topic must be a non-empty string")
        
        # Rate limit check
        if not rate_limiter.is_allowed("best_practices"):
            logger.warning(f"Rate limit exceeded for best practices: {topic}")
            raise Exception("Rate limit exceeded. Please try again later.")
        
        result = f"""
Provide best practices for: {topic}

Context: {context}

Include:
1. Recommended approaches
2. Common pitfalls to avoid
3. Performance considerations
4. Security considerations
5. Configuration recommendations
6. Testing strategies
7. Maintenance guidelines
"""
        logger.info(f"Generated best practices prompt for: {topic}")
        return result
    
    except ValueError as e:
        logger.error(f"Validation error in best_practices_prompt for {topic}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error generating best practices for {topic}: {str(e)}")
        raise


def _comparison_prompt_impl(subject1: str, subject2: str, context: str = "") -> str:
    """
    Generate a prompt to compare two FastMCP concepts or features - core implementation
    """
    try:
        logger.info(f"Generating comparison prompt for: {subject1} vs {subject2}")
        
        if not subject1 or not isinstance(subject1, str) or not subject2 or not isinstance(subject2, str):
            logger.warning("Invalid subjects provided for comparison")
            raise ValueError("Both subjects must be non-empty strings")
        
        # Rate limit check
        if not rate_limiter.is_allowed("comparison"):
            logger.warning(f"Rate limit exceeded for comparison: {subject1} vs {subject2}")
            raise Exception("Rate limit exceeded. Please try again later.")
        
        result = f"""
Compare and contrast the following FastMCP concepts/features:
- {subject1}
- {subject2}

Context: {context}

Include:
1. Key similarities
2. Key differences
3. When to use each
4. Performance characteristics
5. Limitations of each
6. Integration considerations
"""
        logger.info(f"Generated comparison prompt for: {subject1} vs {subject2}")
        return result
    
    except ValueError as e:
        logger.error(f"Validation error in comparison_prompt for {subject1} vs {subject2}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error generating comparison for {subject1} vs {subject2}: {str(e)}")
        raise


def _troubleshooting_prompt_impl(issue_description: str, environment: str = "") -> str:
    """
    Generate a prompt for troubleshooting a FastMCP issue - core implementation
    """
    try:
        logger.info(f"Generating troubleshooting prompt for: {issue_description}")
        
        if not issue_description or not isinstance(issue_description, str):
            logger.warning("Invalid issue description provided for troubleshooting")
            raise ValueError("Issue description must be a non-empty string")
        
        # Rate limit check
        if not rate_limiter.is_allowed("troubleshooting"):
            logger.warning(f"Rate limit exceeded for troubleshooting: {issue_description}")
            raise Exception("Rate limit exceeded. Please try again later.")
        
        result = f"""
Help troubleshoot this FastMCP issue:
Issue: {issue_description}

Environment: {environment}

Include:
1. Common causes
2. Diagnostic steps
3. Possible solutions
4. Debugging techniques
5. Configuration checks
6. Log analysis tips
"""
        logger.info(f"Generated troubleshooting prompt for: {issue_description}")
        return result
    
    except ValueError as e:
        logger.error(f"Validation error in troubleshooting_prompt for {issue_description}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error generating troubleshooting for {issue_description}: {str(e)}")
        raise


# Additional Tools for enhanced functionality

@mcp.tool
def count_docs_in_section(section: str) -> int:
    """
    Count the number of documentation files in a specific section
    """
    return _count_docs_in_section_impl(section)


@mcp.tool
def search_by_file_type(file_type: str = "md") -> List[str]:
    """
    Search for documentation files by type (md, txt, etc.)
    """
    return _search_by_file_type_impl(file_type)


@mcp.tool
def get_file_metadata(file_path: str) -> Dict[str, Any]:
    """
    Get metadata for a specific documentation file including size, creation/modification dates
    """
    return _get_file_metadata_impl(file_path)


@mcp.tool
def get_recently_accessed_docs(limit: int = 10) -> List[str]:
    """
    Get a list of recently accessed documentation files (based on cache)
    """
    return _get_recently_accessed_docs_impl(limit)


# Enhanced Resources

@mcp.resource("http://fastmcp-docs.local/stats")
def get_documentation_stats() -> Dict[str, Any]:
    """
    Get comprehensive statistics about the documentation
    """
    return _get_documentation_stats_impl()


@mcp.resource("http://fastmcp-docs.local/health")
def get_server_health() -> Dict[str, Any]:
    """
    Get the health status of the documentation server
    """
    return _get_server_health_impl()


# Enhanced Prompts

@mcp.prompt("/fastmcp-best-practices")
def best_practices_prompt(topic: str, context: str = "") -> str:
    """
    Generate a prompt about best practices for a specific FastMCP topic
    """
    return _best_practices_prompt_impl(topic, context)


@mcp.prompt("/fastmcp-comparison")
def comparison_prompt(subject1: str, subject2: str, context: str = "") -> str:
    """
    Generate a prompt to compare two FastMCP concepts or features
    """
    return _comparison_prompt_impl(subject1, subject2, context)


@mcp.prompt("/fastmcp-troubleshooting")
def troubleshooting_prompt(issue_description: str, environment: str = "") -> str:
    """
    Generate a prompt for troubleshooting a FastMCP issue
    """
    return _troubleshooting_prompt_impl(issue_description, environment)


# Qwen CLI MCP Management Tools

def _create_mcp_skeleton_impl(
    name: str, 
    description: str, 
    tools: List[str] = None, 
    resources: List[str] = None, 
    prompts: List[str] = None
) -> Dict[str, Any]:
    """
    Create a skeleton for a new MCP server - core implementation
    """
    try:
        logger.info(f"Creating MCP skeleton for: {name}")
        
        if not name or not isinstance(name, str):
            raise ValueError("Name must be a non-empty string")
        
        if tools is None:
            tools = ["list_items", "get_item", "search_items"]
        if resources is None:
            resources = ["get_status", "get_config"]
        if prompts is None:
            prompts = ["explain_concept", "implementation_guide"]
        
        skeleton = {
            "project_name": name,
            "description": description,
            "files": {
                "server.py": f'''#!/usr/bin/env python3
"""
{name} MCP Server
{description}
"""

from fastmcp import FastMCP
from typing import List, Dict, Any

# Initialize the MCP server
mcp = FastMCP(
    name="{name}",
    instructions="{description}",
    version="1.0.0"
)

# Example tools
{chr(10).join([f"@mcp.tool{chr(10)}def {tool}():{chr(10)}    return \"\"\"Tool implementation for {tool}\"\"\"{chr(10)}" for tool in tools])}

# Example resources
{chr(10).join([f"@mcp.resource(\"http://{name.replace(' ', '-').lower()}.local/{resource}\"){chr(10)}def get_{resource}():{chr(10)}    return {{\"message\": \"Resource implementation for {resource}\"}}{chr(10)}" for resource in resources])}

# Example prompts
{chr(10).join([f"@mcp.prompt(\"/{name.replace(' ', '').lower()}-{prompt}\"){chr(10)}def {prompt}_prompt():{chr(10)}    return \"\"\"Prompt for {name} {prompt}\"\"\"{chr(10)}" for prompt in prompts])}

if __name__ == "__main__":
    import asyncio
    asyncio.run(mcp.run_stdio_async())
''',
                "README.md": f'''# {name} MCP Server

{description}

## Setup
```bash
pip install -r requirements.txt
```

## Run
```bash
python server.py
```

## Features
- Tools: {", ".join(tools)}
- Resources: {", ".join(resources)}
- Prompts: {", ".join(prompts)}
''',
                "requirements.txt": "fastmcp>=2.0.0\npydantic>=2.0.0\nanyio>=4.0.0",
                "Dockerfile": f'''# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \\
    PYTHONUNBUFFERED=1 \\
    FASTMCP_HOST=0.0.0.0 \\
    FASTMCP_PORT=8001

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \\
    && apt-get install -y --no-install-recommends \\
        build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8001

# Run the application
CMD ["python", "server.py"]
''',
                "docker-compose.yml": f'''version: '3.8'

services:
  {name.replace(" ", "-").lower()}:
    build: .
    ports:
      - "8001:8001"
    environment:
      - FASTMCP_HOST=0.0.0.0
      - FASTMCP_PORT=8001
    restart: unless-stopped
'''
            }
        }
        
        return skeleton
    except Exception as e:
        logger.error(f"Error creating MCP skeleton for {name}: {str(e)}")
        raise


def _validate_mcp_config_impl(config_content: str) -> Dict[str, Any]:
    """
    Validate MCP configuration content - core implementation
    """
    try:
        logger.info("Validating MCP configuration")
        
        issues = []
        
        # Check for common issues
        if "fastmcp" not in config_content.lower():
            issues.append("Missing 'fastmcp' import or usage")
        
        if "mcp = FastMCP" not in config_content:
            issues.append("Missing FastMCP server initialization")
        
        if "run_stdio_async" not in config_content:
            issues.append("Missing proper MCP server execution")
        
        # Check for decorators
        tool_count = config_content.count("@mcp.tool")
        resource_count = config_content.count("@mcp.resource") 
        prompt_count = config_content.count("@mcp.prompt")
        
        if tool_count == 0 and resource_count == 0 and prompt_count == 0:
            issues.append("No MCP components (tools, resources, or prompts) defined")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "tool_count": tool_count,
            "resource_count": resource_count,
            "prompt_count": prompt_count
        }
    except Exception as e:
        logger.error(f"Error validating MCP configuration: {str(e)}")
        raise


def _generate_mcp_implementation_guide_impl(
    project_type: str,
    features: List[str],
    requirements: str = ""
) -> str:
    """
    Generate a complete implementation guide for an MCP server - core implementation
    """
    try:
        logger.info(f"Generating MCP implementation guide for: {project_type}")
        
        guide = f"""
# Implementation Guide for {project_type} MCP Server

## Project Overview
{requirements or f"This MCP server will provide access to {project_type} functionality."}

## Required Features
{chr(10).join([f"- {feature}" for feature in features])}

## Step-by-Step Implementation

### 1. Setup Project Structure
```
{project_type.lower().replace(' ', '_')}/
├── server.py          # Main MCP server
├── requirements.txt   # Dependencies
├── README.md         # Documentation
├── Dockerfile        # Containerization (optional)
└── docker-compose.yml # Deployment (optional)
```

### 2. Install Dependencies
```bash
pip install fastmcp>=2.0.0 pydantic>=2.0.0
```

### 3. Create the Server File
Create `server.py` with the following structure:

```python
from fastmcp import FastMCP
from typing import List, Dict, Any

# Initialize the MCP server
mcp = FastMCP(
    name="{project_type}",
    instructions="Provide access to {project_type.lower()} functionality",
    version="1.0.0"
)

# Implement your tools here
# @mcp.tool
# def example_tool():
#     return "Example implementation"

# Implement your resources here  
# @mcp.resource("http://example.local/data")
# def get_example_data():
#     return {{"data": "example"}}

# Implement your prompts here
# @mcp.prompt("/example-prompt")
# def example_prompt():
#     return "Example prompt content"

if __name__ == "__main__":
    import asyncio
    asyncio.run(mcp.run_stdio_async())
```

### 4. Add Your Specific Components
Based on your features, implement the following components:
{chr(10).join([f"- {feature}: Implement as appropriate @mcp.tool, @mcp.resource, or @mcp.prompt" for feature in features])}

### 5. Testing
Test your server with:
```bash
python server.py
```

### 6. Deployment Options
- Direct execution: `python server.py`
- Docker: `docker build -t {project_type.lower().replace(' ', '-')} . && docker run -p 8001:8001 {project_type.lower().replace(' ', '-')}`
- Docker Compose: `docker-compose up`

## Best Practices
1. Use proper typing for all function parameters and return values
2. Include comprehensive error handling
3. Implement rate limiting for public APIs
4. Add logging for debugging
5. Document your API endpoints
6. Follow security best practices (validate inputs, sanitize outputs)

## Common Pitfalls to Avoid
1. Forgetting to await async operations
2. Not implementing proper error handling
3. Missing MCP decorators
4. Incorrect function signatures
5. Forgetting to call asyncio.run() in main

## Example Implementation
Here's a basic example based on your requirements:

```python
from fastmcp import FastMCP
from typing import List, Dict, Any

mcp = FastMCP(
    name="{project_type}",
    instructions="Provide access to {project_type.lower()} functionality",
    version="1.0.0"
)

# Add your implementations here

if __name__ == "__main__":
    import asyncio
    asyncio.run(mcp.run_stdio_async())
```
"""
        return guide
    except Exception as e:
        logger.error(f"Error generating MCP implementation guide for {project_type}: {str(e)}")
        raise


def _generate_mcp_debugging_guide_impl(server_code: str) -> str:
    """
    Generate a debugging guide for an MCP server - core implementation
    """
    try:
        logger.info("Generating MCP debugging guide")
        
        guide = f"""
# Debugging Guide for MCP Server

## Common Issues and Solutions

### 1. Import Errors
Issue: `ModuleNotFoundError: No module named 'fastmcp'`
Solution: Install using `pip install fastmcp>=2.0.0`

### 2. Server Not Starting
Issue: Server fails to start
Solution: Check that you're running `asyncio.run(mcp.run_stdio_async())` in the main block

### 3. Tools/Resource/Prompts Not Registering
Issue: MCP components not appearing in client
Solution: Ensure all functions are decorated with appropriate @mcp decorators

### 4. Configuration Issues
Issue: Server not responding as expected
Solution: Verify your FastMCP initialization parameters

## Debugging Your Code

Based on your code:
{server_code[:500]}...

Here are specific suggestions:

1. Check that all your @mcp decorators are properly applied
2. Verify that your functions have correct type hints
3. Ensure async/await usage is correct
4. Make sure all imports are present
5. Validate that the server is running with proper permissions

## Debugging Commands
```bash
# Check if server is running
curl -I http://localhost:8001

# Check imports
python -c "import fastmcp; print(fastmcp.__version__)"

# Test basic functionality
python server.py
```

## Logging and Monitoring
Add logging to your server to help debug:

```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@mcp.tool
def example_tool():
    logger.info("Example tool called")
    # your implementation here
```

## Testing Your Server
Create a simple test client:

```python
import asyncio
from fastmcp import Client

async def test_client():
    async with Client("http://127.0.0.1:8001") as client:
        tools = await client.list_tools()
        print("Available tools:", [t.name for t in tools])
        
        resources = await client.list_resources()
        print("Available resources:", [r.name for r in resources])

asyncio.run(test_client())
```
"""
        return guide
    except Exception as e:
        logger.error(f"Error generating MCP debugging guide: {str(e)}")
        raise


def _get_mcp_best_practices_impl() -> List[Dict[str, str]]:
    """
    Get MCP best practices - core implementation
    """
    try:
        logger.info("Getting MCP best practices")
        
        practices = [
            {
                "category": "Security",
                "practice": "Validate all inputs to prevent injection attacks",
                "example": "Use proper type hints and validate parameters"
            },
            {
                "category": "Performance", 
                "practice": "Implement caching for expensive operations",
                "example": "Use in-memory cache for frequently accessed data"
            },
            {
                "category": "Reliability",
                "practice": "Include comprehensive error handling",
                "example": "Use try/catch blocks and return descriptive errors"
            },
            {
                "category": "Maintainability",
                "practice": "Use descriptive names for tools, resources, and prompts",
                "example": "Use names like get_user_profile instead of gu"
            },
            {
                "category": "Scalability",
                "practice": "Implement rate limiting to prevent abuse",
                "example": "Limit requests per IP or per time window"
            },
            {
                "category": "Usability",
                "practice": "Provide clear instructions in the MCP initialization",
                "example": "Instructions should explain what the server does"
            }
        ]
        
        return practices
    except Exception as e:
        logger.error(f"Error getting MCP best practices: {str(e)}")
        raise


def _analyze_existing_mcp_impl(server_content: str) -> Dict[str, Any]:
    """
    Analyze an existing MCP server code and provide insights - core implementation
    """
    try:
        logger.info("Analyzing existing MCP server code")
        
        analysis = {
            "imports": [],
            "tools_count": 0,
            "resources_count": 0,
            "prompts_count": 0,
            "decorators_found": [],
            "potential_issues": [],
            "suggestions": []
        }
        
        # Analyze imports
        if "from fastmcp import FastMCP" in server_content:
            analysis["imports"].append("fastmcp")
        
        # Count decorators
        analysis["tools_count"] = server_content.count("@mcp.tool")
        analysis["resources_count"] = server_content.count("@mcp.resource")
        analysis["prompts_count"] = server_content.count("@mcp.prompt")
        
        # Track all decorators found
        if analysis["tools_count"] > 0:
            analysis["decorators_found"].append("tools")
        if analysis["resources_count"] > 0:
            analysis["decorators_found"].append("resources")
        if analysis["prompts_count"] > 0:
            analysis["decorators_found"].append("prompts")
        
        # Check for common issues
        if "asyncio.run(mcp.run_stdio_async())" not in server_content:
            analysis["potential_issues"].append("Missing proper server execution")
            analysis["suggestions"].append("Add asyncio.run(mcp.run_stdio_async()) in main block")
        
        if "import asyncio" not in server_content and ("@mcp.tool" in server_content or "@mcp.resource" in server_content):
            analysis["potential_issues"].append("Missing asyncio import")
            analysis["suggestions"].append("Add 'import asyncio' at the top of the file")
        
        if len(analysis["imports"]) == 0:
            analysis["potential_issues"].append("Missing FastMCP import")
            analysis["suggestions"].append("Add 'from fastmcp import FastMCP'")
        
        # Check for error handling
        if "try:" not in server_content and ("@mcp.tool" in server_content or "@mcp.resource" in server_content):
            analysis["suggestions"].append("Consider adding error handling to your functions")
        
        return analysis
    except Exception as e:
        logger.error(f"Error analyzing existing MCP code: {str(e)}")
        raise


# Qwen CLI MCP Management Tools

@mcp.tool
def create_mcp_skeleton(
    name: str, 
    description: str, 
    tools: List[str] = None, 
    resources: List[str] = None, 
    prompts: List[str] = None
) -> Dict[str, Any]:
    """
    Create a skeleton for a new MCP server
    """
    return _create_mcp_skeleton_impl(name, description, tools, resources, prompts)


@mcp.tool
def validate_mcp_config(config_content: str) -> Dict[str, Any]:
    """
    Validate MCP configuration content
    """
    return _validate_mcp_config_impl(config_content)


@mcp.prompt("/fastmcp-implementation-guide")
def generate_mcp_implementation_guide(
    project_type: str,
    features: List[str],
    requirements: str = ""
) -> str:
    """
    Generate a complete implementation guide for an MCP server
    """
    return _generate_mcp_implementation_guide_impl(project_type, features, requirements)


@mcp.prompt("/fastmcp-debugging-guide")
def generate_mcp_debugging_guide(server_code: str) -> str:
    """
    Generate a debugging guide for an MCP server
    """
    return _generate_mcp_debugging_guide_impl(server_code)


@mcp.resource("http://fastmcp-docs.local/mcp-best-practices")
def get_mcp_best_practices() -> List[Dict[str, str]]:
    """
    Get MCP best practices
    """
    return _get_mcp_best_practices_impl()


@mcp.tool
def analyze_existing_mcp(server_content: str) -> Dict[str, Any]:
    """
    Analyze an existing MCP server code and provide insights
    """
    return _analyze_existing_mcp_impl(server_content)


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
    # Update logging level based on config
    logging.getLogger().setLevel(config.log_level)
    
    # Use stdio transport for MCP server (proper MCP protocol communication)
    import asyncio
    asyncio.run(mcp.run_stdio_async())