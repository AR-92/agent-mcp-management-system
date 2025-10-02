"""
FastMCP Documentation Agent using Strands Agents SDK

This agent uses the FastMCP Documentation MCP to provide access to FastMCP documentation.
"""

from strandsagents import Agent
from typing import Dict, Any, List
import json
from datetime import datetime


def get_docs_list(
    category: str = None,
    format: str = "markdown",  # markdown, html, json
    search_query: str = None
) -> List[Dict[str, Any]]:
    """
    Get a list of available documentation resources.
    
    Args:
        category: Filter by documentation category
        format: Preferred format ('markdown', 'html', 'json')
        search_query: Search query to filter documentation
        
    Returns:
        List of dictionaries containing documentation information
    """
    # This would connect to the FastMCP Documentation MCP server in a real implementation
    docs_list = [
        {
            "id": f"doc_{i}",
            "title": f"Documentation Topic {i}",
            "category": "getting-started" if i % 3 == 0 else "api-reference" if i % 3 == 1 else "tutorials",
            "summary": f"Summary of documentation topic {i}",
            "format": format,
            "size_kb": 120 + (i * 10),
            "updated_date": (datetime.now() - timedelta(days=i)).isoformat(),
            "url": f"https://docs.example.com/doc_{i}",
            "tags": ["fastmcp", "mcp", f"topic-{i}"]
        }
        for i in range(1, 11)
    ]
    
    if category:
        docs_list = [doc for doc in docs_list if doc["category"] == category]
        
    if search_query:
        docs_list = [doc for doc in docs_list if search_query.lower() in doc["title"].lower() or search_query.lower() in doc["summary"].lower()]
    
    return docs_list


def get_documentation(
    doc_id: str,
    format: str = "markdown"  # markdown, html, json
) -> Dict[str, Any]:
    """
    Get specific documentation content.
    
    Args:
        doc_id: ID of the documentation to retrieve
        format: Desired format ('markdown', 'html', 'json')
        
    Returns:
        Dictionary containing the documentation content
    """
    # This would connect to the FastMCP Documentation MCP server in a real implementation
    docs_content = {
        "id": doc_id,
        "title": f"Complete Documentation for {doc_id}",
        "content": f"""
# {doc_id}

This is the complete documentation for {doc_id}. This document provides comprehensive information about FastMCP and its usage.

## Overview

FastMCP provides a framework for creating Model Context Protocol (MCP) servers that can be used by LLMs to access external tools and resources. FastMCP simplifies the process of creating MCP servers with built-in functionality for common operations.

## Key Features

1. **Easy MCP Server Creation**: FastMCP simplifies the process of creating MCP servers.
2. **Built-in Tools**: Common tools are provided out-of-the-box.
3. **Flexible Configuration**: Easy to configure and customize.
4. **Resource Management**: Tools for managing documentation and resources.

## Usage

```python
from fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP(
    name="Example Server",
    instructions="Provides access to example functionality",
    version="1.0.0"
)

# Define tools using decorators
@mcp.tool
def example_tool(param1: str) -> dict:
    return {"result": f"Processed {param1}"}

# Run the server with stdio transport
if __name__ == "__main__":
    import asyncio
    asyncio.run(mcp.run_stdio_async())
```

## Configuration Options

- `name`: Name of the MCP server
- `instructions`: Description of what the server provides
- `version`: Version of the server

## Best Practices

1. Use proper type hints in tool definitions
2. Include comprehensive docstrings
3. Handle errors gracefully
4. Follow MCP protocol specifications
        """,
        "format": format,
        "updated_date": (datetime.now() - timedelta(days=1)).isoformat(),
        "version": "1.0.0",
        "size_kb": 8,
        "related_docs": [f"doc_{i}" for i in range(1, 4)]
    }
    
    return docs_content


def search_documentation(
    query: str,
    max_results: int = 10,
    category: str = None
) -> List[Dict[str, Any]]:
    """
    Search documentation based on query.
    
    Args:
        query: Search query
        max_results: Maximum number of results to return
        category: Optional category to filter search
        
    Returns:
        List of dictionaries containing search results
    """
    # This would connect to the FastMCP Documentation MCP server in a real implementation
    search_results = [
        {
            "id": f"search_result_{i}",
            "title": f"Result {i} for query '{query}'",
            "summary": f"This document contains information about {query} and related topics...",
            "relevance_score": round(0.95 - (i * 0.05), 2),
            "category": "api-reference" if i % 2 == 0 else "tutorials",
            "url": f"https://docs.example.com/search/{i}",
            "updated_date": (datetime.now() - timedelta(days=i)).isoformat()
        }
        for i in range(1, max_results + 1)
    ]
    
    if category:
        search_results = [result for result in search_results if result["category"] == category]
    
    return search_results[:max_results]


def get_api_reference(
    endpoint: str = None,
    category: str = None
) -> Dict[str, Any]:
    """
    Get API reference documentation.
    
    Args:
        endpoint: Specific endpoint to get reference for
        category: Category of API endpoints to retrieve
        
    Returns:
        Dictionary containing API reference information
    """
    # This would connect to the FastMCP Documentation MCP server in a real implementation
    if endpoint:
        return {
            "endpoint": endpoint,
            "method": "POST",
            "description": f"API endpoint for {endpoint}",
            "parameters": [
                {
                    "name": "param1",
                    "type": "string",
                    "required": True,
                    "description": "First parameter"
                },
                {
                    "name": "param2", 
                    "type": "integer",
                    "required": False,
                    "description": "Second parameter"
                }
            ],
            "response": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "data": {"type": "object"}
                }
            },
            "examples": [
                {
                    "request": {
                        "url": f"https://api.example.com/{endpoint}",
                        "method": "POST",
                        "body": {"param1": "value"}
                    },
                    "response": {
                        "status": "success",
                        "data": {"result": "value"}
                    }
                }
            ]
        }
    else:
        return {
            "category": category or "all",
            "endpoints": [
                {
                    "name": f"endpoint_{i}",
                    "path": f"/api/endpoint_{i}",
                    "method": "GET" if i % 2 == 0 else "POST",
                    "description": f"Description for endpoint {i}",
                    "parameters_count": i % 3 + 1
                }
                for i in range(1, 6)
            ],
            "base_url": "https://api.example.com",
            "version": "v1"
        }


def get_tutorial_list(
    topic: str = None,
    difficulty: str = None,  # beginner, intermediate, advanced
    max_results: int = 20
) -> List[Dict[str, Any]]:
    """
    Get list of tutorials.
    
    Args:
        topic: Filter by tutorial topic
        difficulty: Filter by difficulty level
        max_results: Maximum number of tutorials to return
        
    Returns:
        List of dictionaries containing tutorial information
    """
    # This would connect to the FastMCP Documentation MCP server in a real implementation
    tutorials = [
        {
            "id": f"tutorial_{i}",
            "title": f"FastMCP Tutorial {i}: Getting Started",
            "topic": "getting-started" if i % 3 == 0 else "configuration" if i % 3 == 1 else "advanced-usage",
            "difficulty": "beginner" if i % 3 == 0 else "intermediate" if i % 3 == 1 else "advanced",
            "estimated_duration_minutes": 15 + (i * 5),
            "prerequisites": ["Basic Python knowledge"] if i < 5 else ["Advanced Python", "MCP knowledge"],
            "objectives": [f"Learn how to create an MCP server", f"Implement tool {i}"],
            "url": f"https://tutorials.example.com/tutorial_{i}",
            "rating": round(4.0 + (i % 5) * 0.2, 1),
            "completed_by": 1250 + (i * 100)
        }
        for i in range(1, max_results + 1)
    ]
    
    if topic:
        tutorials = [tut for tut in tutorials if topic.lower() in tut["topic"]]
        
    if difficulty:
        tutorials = [tut for tut in tutorials if tut["difficulty"] == difficulty]
    
    return tutorials[:max_results]


def get_glossary_terms(
    search_term: str = None
) -> List[Dict[str, str]]:
    """
    Get glossary of terms related to FastMCP and MCP.
    
    Args:
        search_term: Optional term to search for specifically
        
    Returns:
        List of dictionaries containing glossary terms and definitions
    """
    # This would connect to the FastMCP Documentation MCP server in a real implementation
    glossary = [
        {
            "term": "MCP",
            "definition": "Model Context Protocol - A protocol that allows LLMs to access external tools and resources"
        },
        {
            "term": "FastMCP",
            "definition": "A framework for creating Model Context Protocol (MCP) servers"
        },
        {
            "term": "MCP Server",
            "definition": "A server that implements the Model Context Protocol and provides tools to LLMs"
        },
        {
            "term": "Tool",
            "definition": "A function or method exposed by an MCP server that can be called by LLMs"
        },
        {
            "term": "Resource",
            "definition": "A static or semi-static piece of information provided by an MCP server"
        },
        {
            "term": "Prompt",
            "definition": "A template or example that guides the LLM on how to use tools effectively"
        }
    ]
    
    if search_term:
        glossary = [item for item in glossary if search_term.lower() in item["term"].lower()]
    
    return glossary


def get_best_practices(
    category: str = None
) -> List[Dict[str, str]]:
    """
    Get best practices for using FastMCP.
    
    Args:
        category: Category of best practices to retrieve
        
    Returns:
        List of dictionaries containing best practices
    """
    # This would connect to the FastMCP Documentation MCP server in a real implementation
    practices = [
        {
            "title": "Use Type Hints",
            "description": "Always include proper type hints in your tool functions for better LLM understanding",
            "category": "development"
        },
        {
            "title": "Include Comprehensive Docstrings",
            "description": "Provide detailed documentation for parameters, return values, and function purpose",
            "category": "development"
        },
        {
            "title": "Handle Errors Gracefully",
            "description": "Implement proper error handling in your tools and return meaningful error messages",
            "category": "development"
        },
        {
            "title": "Follow MCP Protocol",
            "description": "Ensure your server follows the official MCP protocol specifications",
            "category": "development"
        },
        {
            "title": "Secure Your Server",
            "description": "Implement proper authentication and authorization for production deployments",
            "category": "security"
        }
    ]
    
    if category:
        practices = [practice for practice in practices if practice["category"] == category]
    
    return practices


def get_release_notes(
    version: str = None,
    max_results: int = 10
) -> List[Dict[str, Any]]:
    """
    Get release notes for FastMCP versions.
    
    Args:
        version: Specific version to get notes for
        max_results: Maximum number of releases to return (if version is not specified)
        
    Returns:
        List of dictionaries containing release notes
    """
    # This would connect to the FastMCP Documentation MCP server in a real implementation
    if version:
        return [{
            "version": version,
            "date": (datetime.now() - timedelta(days=5)).isoformat(),
            "changes": [
                "Added new documentation features",
                "Improved search functionality",
                "Fixed various bugs",
                "Enhanced performance"
            ],
            "features": ["New API endpoints", "Better error handling"],
            "breaking_changes": [],
            "upgraded_dependencies": ["mcp-core>=2.1.0"]
        }]
    else:
        return [
            {
                "version": f"1.0.{i}",
                "date": (datetime.now() - timedelta(days=i*10)).isoformat(),
                "changes": [
                    f"Added feature {i}",
                    "Improved performance",
                    f"Fixed bug #{i*10}"
                ],
                "features": [f"Feature {i}", "Enhancement A"],
                "breaking_changes": ["Changed API in version 1.0.5"] if i == 5 else [],
                "upgraded_dependencies": [f"dependency>=1.{i}.0"]
            }
            for i in range(max_results, 0, -1)
        ]


def get_faq(
    category: str = None,
    search_query: str = None
) -> List[Dict[str, str]]:
    """
    Get frequently asked questions about FastMCP.
    
    Args:
        category: Category of FAQs to retrieve
        search_query: Search query to filter FAQs
        
    Returns:
        List of dictionaries containing frequently asked questions and answers
    """
    # This would connect to the FastMCP Documentation MCP server in a real implementation
    faq_list = [
        {
            "question": "What is FastMCP?",
            "answer": "FastMCP is a framework for creating Model Context Protocol (MCP) servers that allow LLMs to access external tools and resources.",
            "category": "general"
        },
        {
            "question": "How do I create an MCP server with FastMCP?",
            "answer": "Use the FastMCP class, define tools with decorators, and run with stdio transport.",
            "category": "development"
        },
        {
            "question": "What are the system requirements?",
            "answer": "FastMCP requires Python 3.8+ and the mcp-core package.",
            "category": "requirements"
        },
        {
            "question": "Can I use FastMCP with any LLM?",
            "answer": "Yes, FastMCP servers can be used with any LLM that supports the Model Context Protocol.",
            "category": "compatibility"
        },
        {
            "question": "Is FastMCP production-ready?",
            "answer": "FastMCP is suitable for production with proper configuration and security measures.",
            "category": "deployment"
        }
    ]
    
    if category:
        faq_list = [faq for faq in faq_list if faq["category"] == category]
        
    if search_query:
        faq_list = [faq for faq in faq_list if search_query.lower() in faq["question"].lower() or search_query.lower() in faq["answer"].lower()]
    
    return faq_list


def get_code_examples(
    language: str = "python",
    category: str = None,
    max_results: int = 5
) -> List[Dict[str, str]]:
    """
    Get code examples for using FastMCP.
    
    Args:
        language: Programming language for examples
        category: Category of examples
        max_results: Maximum number of examples to return
        
    Returns:
        List of dictionaries containing code examples
    """
    # This would connect to the FastMCP Documentation MCP server in a real implementation
    examples = [
        {
            "title": "Basic MCP Server",
            "language": language,
            "category": "getting-started",
            "code": """from fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP(
    name="Example Server",
    instructions="Provides access to example functionality",
    version="1.0.0"
)

# Define a simple tool
@mcp.tool
def hello_world(name: str) -> dict:
    return {"message": f"Hello, {name}!"}

if __name__ == "__main__":
    import asyncio
    asyncio.run(mcp.run_stdio_async())""",
            "description": "A basic example of creating an MCP server with one tool"
        },
        {
            "title": "Tool with Multiple Parameters",
            "language": language,
            "category": "intermediate",
            "code": """from fastmcp import FastMCP
from typing import Dict, Any

mcp = FastMCP(
    name="Calculator Server",
    instructions="Provides calculator functionality",
    version="1.0.0"
)

@mcp.tool
def calculate(operation: str, a: float, b: float) -> Dict[str, Any]:
    if operation == "add":
        result = a + b
    elif operation == "subtract":
        result = a - b
    elif operation == "multiply":
        result = a * b
    elif operation == "divide":
        if b == 0:
            return {"error": "Cannot divide by zero"}
        result = a / b
    else:
        return {"error": f"Unknown operation: {operation}"}
    
    return {"result": result}""",
            "description": "Example of a tool with multiple parameters and complex return types"
        }
    ]
    
    if category:
        examples = [ex for ex in examples if ex["category"] == category]
    
    return examples[:max_results]


def get_migration_guide(
    from_version: str,
    to_version: str
) -> Dict[str, Any]:
    """
    Get migration guide from one version to another.
    
    Args:
        from_version: Starting version
        to_version: Target version
        
    Returns:
        Dictionary containing migration guide
    """
    # This would connect to the FastMCP Documentation MCP server in a real implementation
    return {
        "from_version": from_version,
        "to_version": to_version,
        "migration_guide": f"""
# Migration Guide: {from_version} to {to_version}

## Breaking Changes
- List of breaking changes

## New Features
- List of new features

## Deprecated Features
- List of deprecated features

## Migration Steps
1. Step 1
2. Step 2
3. Step 3

## Examples
Updated code examples showing the differences
        """,
        "estimated_time": "15-30 minutes",
        "difficulty": "intermediate",
        "prerequisites": [f"Understanding of version {from_version}"],
        "post_migration_steps": [
            "Test your MCP server",
            "Verify all tools work correctly",
            "Update documentation"
        ]
    }


# Create a FastMCP Documentation agent
agent = Agent(
    system_prompt="You are a FastMCP Documentation assistant. You can provide access to FastMCP documentation, search documentation, get API references, tutorials, glossary terms, best practices, release notes, FAQs, code examples, and migration guides. When asked about FastMCP, provide detailed documentation and examples to help users understand and use the framework effectively."
)


def setup_docs_agent():
    """Set up the FastMCP Documentation agent with tools."""
    try:
        agent.add_tool(get_docs_list)
        agent.add_tool(get_documentation)
        agent.add_tool(search_documentation)
        agent.add_tool(get_api_reference)
        agent.add_tool(get_tutorial_list)
        agent.add_tool(get_glossary_terms)
        agent.add_tool(get_best_practices)
        agent.add_tool(get_release_notes)
        agent.add_tool(get_faq)
        agent.add_tool(get_code_examples)
        agent.add_tool(get_migration_guide)
        print("FastMCP Documentation tools successfully registered with the agent.")
        return True
    except AttributeError as e:
        print(f"Note: Tool registration API may vary depending on the specific Strands implementation. Error: {e}")
        return False


def run_docs_agent(user_input: str):
    """
    Run the FastMCP Documentation agent with the given user input.
    
    Args:
        user_input: The input from the user
        
    Returns:
        The agent's response
    """
    try:
        response = agent.run(user_input)
        return response
    except ImportError:
        # If strandsagents is not available, return a simulated response
        return f"Simulated response: FastMCP Documentation agent. You requested: '{user_input}'"
    except Exception as e:
        return f"Error processing your request: {str(e)}"


def main():
    """Main function to run the FastMCP Documentation agent."""
    # Set up tools
    tools_setup = setup_docs_agent()
    
    print("FastMCP Documentation Agent")
    print("This agent can:")
    print("- List documentation (e.g., 'list all documentation')")
    print("- Get specific documentation (e.g., 'get documentation for server creation')")
    print("- Search documentation (e.g., 'search for authentication')")
    print("- Get API references (e.g., 'show API reference')")
    print("- List tutorials (e.g., 'show tutorials for beginners')")
    print("- Get glossary terms (e.g., 'what is MCP')")
    print("- Get best practices (e.g., 'show best practices')")
    print("- Get release notes (e.g., 'show latest release notes')")
    print("- Get FAQs (e.g., 'show FAQs about deployment')")
    print("- Get code examples (e.g., 'show code examples for tools')")
    print("- Get migration guides (e.g., 'show migration guide')")
    print("Type 'quit' to exit.\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Agent: Goodbye! FastMCP Documentation assistant signing off.")
            break
            
        response = run_docs_agent(user_input)
        print(f"Agent: {response}\n")


if __name__ == "__main__":
    main()