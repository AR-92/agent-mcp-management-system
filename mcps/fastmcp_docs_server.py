#!/usr/bin/env python3
"""
Simple FastMCP Documentation MCP Server

Provides access to FastMCP documentation for LLMs in a simplified form.
"""

from fastmcp import FastMCP
from typing import List, Dict, Any
import os
from pathlib import Path
import json
from datetime import datetime


# Initialize the MCP server
mcp = FastMCP(
    name="Simple FastMCP Documentation Server",
    instructions="Provides access to FastMCP documentation for LLMs",
    version="1.0.0"
)


# Use a simple documentation path
DOCS_BASE_PATH = str(Path(__file__).parent.parent / "docs" / "fastmcp_docs")


# Tools
@mcp.tool
def list_documentation_sections() -> List[str]:
    """
    List all available documentation sections
    """
    sections = []
    if not os.path.exists(DOCS_BASE_PATH):
        raise FileNotFoundError(f"Documentation directory not found: {DOCS_BASE_PATH}")
    
    for item in os.listdir(DOCS_BASE_PATH):
        item_path = os.path.join(DOCS_BASE_PATH, item)
        if os.path.isdir(item_path):
            sections.append(item)
    sections.append("index.md")  # Add the main index
    
    return sorted(sections)


@mcp.tool
def search_documentation(query: str) -> List[Dict[str, str]]:
    """
    Search for documentation files that contain the query string
    """
    if not query:
        return []
    
    results = []
    
    # Search in all markdown and text files
    for root, dirs, files in os.walk(DOCS_BASE_PATH):
        for file in files:
            if file.lower().endswith(('.md', '.txt')):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, DOCS_BASE_PATH)
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    if query.lower() in content.lower():
                        # Find context around the match
                        content_lower = content.lower()
                        start_idx = content_lower.find(query.lower())
                        
                        if start_idx != -1:
                            start_context = max(0, start_idx - 100)
                            end_context = min(start_idx + len(query) + 100, len(content))
                            
                            snippet = content[start_context:end_context]
                            if start_context > 0:
                                snippet = "... " + snippet
                            if end_context < len(content):
                                snippet += " ..."
                            
                            results.append({
                                "file": relative_path,
                                "snippet": snippet,
                                "path": file_path
                            })
                
                except Exception as e:
                    continue  # Continue with other files
    
    return results


@mcp.tool
def read_documentation_file(file_path: str) -> str:
    """
    Read the content of a specific documentation file
    """
    # Validate and sanitize file path to prevent directory traversal
    if not file_path or '..' in file_path or './' in file_path:
        raise ValueError("Invalid file path: contains invalid path characters")
    
    # Only allow markdown and text files
    if not file_path.lower().endswith(('.md', '.txt')):
        raise ValueError("Invalid file path: only markdown and text files allowed")
    
    requested_path = os.path.abspath(os.path.join(DOCS_BASE_PATH, file_path))
    base_path = os.path.abspath(DOCS_BASE_PATH)
    
    if not requested_path.startswith(base_path):
        raise ValueError("Invalid file path: directory traversal detected")
    
    if not os.path.exists(requested_path):
        raise FileNotFoundError(f"Documentation file not found: {file_path}")
    
    if not os.path.isfile(requested_path):
        raise ValueError(f"Path is not a file: {file_path}")
    
    with open(requested_path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()


@mcp.tool
def get_section_files(section: str) -> List[str]:
    """
    Get all files in a specific documentation section
    """
    if not section:
        raise ValueError("Section name must be a non-empty string")
    
    section_path = os.path.join(DOCS_BASE_PATH, section)
    if not os.path.exists(section_path):
        raise ValueError(f"Section not found: {section}")
    
    if not os.path.isdir(section_path):
        raise ValueError(f"Path is not a directory: {section}")
    
    files = []
    for root, dirs, filenames in os.walk(section_path):
        for filename in filenames:
            if filename.lower().endswith(('.md', '.txt')):
                relative_path = os.path.relpath(os.path.join(root, filename), DOCS_BASE_PATH)
                files.append(relative_path)
    
    return sorted(files)


@mcp.tool
def find_examples_for_feature(feature: str) -> List[Dict[str, str]]:
    """
    Find documentation examples related to a specific feature
    """
    if not feature:
        return []
    
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
                            start_idx = content_lower.find(feature.lower())
                            
                            if start_idx != -1:
                                start = max(0, start_idx - 100)
                                end = min(len(content), start_idx + len(feature) + 100)
                                snippet = content[start:end]
                                
                                results.append({
                                    "file": os.path.relpath(file_path, DOCS_BASE_PATH),
                                    "snippet": f"...{snippet}...",
                                    "path": file_path
                                })
                    except Exception:
                        continue  # Continue with other files
    
    return results


@mcp.tool
def count_docs_in_section(section: str) -> int:
    """
    Count the number of documentation files in a specific section
    """
    files = get_section_files(section)
    return len(files)


# Resources
@mcp.resource("http://simple-fastmcp-docs.local/table-of-contents")
def get_documentation_toc() -> Dict[str, Any]:
    """
    Get the table of contents for the FastMCP documentation
    """
    toc = {
        "title": "FastMCP Documentation",
        "description": "Simple documentation for the FastMCP framework",
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
        except Exception:
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
                except Exception:
                    toc["sections"][item] = {
                        "title": item,
                        "path": f"{item}/index.md",
                        "description": f"Section {item} (error reading details)"
                    }
    
    return toc


@mcp.resource("http://simple-fastmcp-docs.local/latest-updates")
def get_latest_docs_updates() -> List[Dict[str, Any]]:
    """
    Get information about recently updated documentation
    """
    import glob
    updates = []
    
    # Find all markdown and text files and get their modification times
    md_files = glob.glob(f"{DOCS_BASE_PATH}/**/*", recursive=True)
    # Filter for markdown and text files
    md_files = [f for f in md_files if os.path.isfile(f) and 
                f.lower().endswith(('.md', '.txt'))]
    
    # Sort by modification time (most recent first)
    md_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    
    for file_path in md_files[:10]:  # Get the 10 most recently modified files
        rel_path = os.path.relpath(file_path, DOCS_BASE_PATH)
        mod_time = os.path.getmtime(file_path)
        mod_time_str = datetime.fromtimestamp(mod_time).isoformat()
        
        updates.append({
            "file": rel_path,
            "modified": mod_time_str,
            "size": os.path.getsize(file_path)
        })
    
    return updates


@mcp.resource("http://simple-fastmcp-docs.local/stats")
def get_documentation_stats() -> Dict[str, Any]:
    """
    Get comprehensive statistics about the documentation
    """
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
    
    # Use list of documentation sections to count sections
    sections = []
    for item in os.listdir(DOCS_BASE_PATH):
        item_path = os.path.join(DOCS_BASE_PATH, item)
        if os.path.isdir(item_path):
            sections.append(item)
    stats["total_sections"] = len(sections)
    
    return stats


@mcp.resource("http://simple-fastmcp-docs.local/health")
def get_server_health() -> Dict[str, Any]:
    """
    Get the health status of the documentation server
    """
    is_docs_path_accessible = os.path.exists(DOCS_BASE_PATH)
    
    health = {
        "status": "healthy" if is_docs_path_accessible else "unhealthy",
        "timestamp": datetime.now().isoformat(),
        "docs_path_accessible": is_docs_path_accessible,
        "docs_path": DOCS_BASE_PATH,
        "server_config": {
            "name": mcp.name,
            "version": mcp.version,
        }
    }
    
    return health


# Prompts
@mcp.prompt("/fastmcp-concept-explanation")
def explain_fastmcp_concept(concept: str, context: str = "") -> str:
    """
    Generate a prompt to explain a FastMCP concept with context
    """
    return f"""
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


@mcp.prompt("/fastmcp-implementation-guide")
def implementation_guide_prompt(topic: str, requirements: str = "") -> str:
    """
    Generate a prompt for implementing a FastMCP feature
    """
    return f"""
Provide a detailed implementation guide for: {topic}

Requirements: {requirements}

Include:
1. Step-by-step instructions
2. Code examples
3. Best practices
4. Common pitfalls to avoid
5. Configuration requirements
6. Testing strategies
"""


@mcp.prompt("/fastmcp-best-practices")
def best_practices_prompt(topic: str, context: str = "") -> str:
    """
    Generate a prompt about best practices for a specific FastMCP topic
    """
    return f"""
Provide best practices for: {topic}

Context: {context}

Include:
1. Recommended approaches
2. Common pitfalls to avoid
3. Performance considerations
4. Security considerations
5. Configuration recommendations
6. Testing strategies
"""


@mcp.prompt("/fastmcp-comparison")
def comparison_prompt(subject1: str, subject2: str, context: str = "") -> str:
    """
    Generate a prompt to compare two FastMCP concepts or features
    """
    return f"""
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


@mcp.prompt("/fastmcp-troubleshooting")
def troubleshooting_prompt(issue_description: str, environment: str = "") -> str:
    """
    Generate a prompt for troubleshooting a FastMCP issue
    """
    return f"""
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


if __name__ == "__main__":
    import asyncio
    # Use stdio transport for MCP server (proper MCP protocol communication)
    asyncio.run(mcp.run_stdio_async())