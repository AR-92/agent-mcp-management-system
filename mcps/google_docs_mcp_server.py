#!/usr/bin/env python3
"""
Google Docs MCP Server

Provides access to Google Docs functionality for LLMs through MCP protocol.
"""

from fastmcp import FastMCP
from typing import List, Dict, Any
import asyncio


# Initialize the MCP server
mcp = FastMCP(
    name="Google Docs MCP Server",
    instructions="Provides access to Google Docs functionality including document creation, editing, and management",
    version="1.0.0"
)


# Tools
@mcp.tool
def list_documents(
    query: str = None, 
    max_results: int = 20
) -> List[Dict[str, Any]]:
    """
    List documents in Google Drive that are Google Docs
    """
    # This would connect to Google Docs API in a real implementation
    return [
        {
            "id": f"doc_{i}",
            "title": f"Sample Document {i}",
            "mimeType": "application/vnd.google-apps.document",
            "createdTime": "2023-01-01T10:00:00Z",
            "modifiedTime": "2023-01-02T15:30:00Z",
            "owners": ["user@example.com"],
            "webViewLink": f"https://docs.google.com/document/d/doc_{i}/view"
        }
        for i in range(max_results)
    ]


@mcp.tool
def get_document_content(document_id: str) -> Dict[str, Any]:
    """
    Get the content of a Google Doc
    """
    # This would fetch the actual document content from Google Docs API in a real implementation
    return {
        "document_id": document_id,
        "title": f"Document {document_id}",
        "content": f"This is the content of document {document_id}. It contains sample text that would normally be retrieved from the Google Docs API.",
        "last_modified": "2023-01-02T15:30:00Z",
        "revision_id": "rev_123"
    }


@mcp.tool
def create_document(title: str, content: str = "") -> Dict[str, str]:
    """
    Create a new Google Doc
    """
    return {
        "status": "created",
        "document_id": "new_doc_id",
        "message": f"Document '{title}' created successfully"
    }


@mcp.tool
def update_document(document_id: str, content: str, append: bool = False) -> Dict[str, str]:
    """
    Update the content of an existing Google Doc
    """
    action = "appended to" if append else "updated in"
    return {
        "status": "updated",
        "message": f"Content {action} document {document_id}"
    }


@mcp.tool
def search_in_document(document_id: str, query: str) -> List[Dict[str, str]]:
    """
    Search for text within a specific document
    """
    return [
        {
            "text": f"Found '{query}' in document {document_id}",
            "startIndex": 10 * i,
            "endIndex": 10 * i + len(query)
        }
        for i in range(3)
    ]


@mcp.tool
def add_comment(
    document_id: str, 
    content: str, 
    quoted_text: str = None,
    suggested_reply: str = None
) -> Dict[str, str]:
    """
    Add a comment to a Google Doc
    """
    return {
        "status": "comment_added",
        "message": f"Comment added to document {document_id}"
    }


@mcp.tool
def get_comments(document_id: str) -> List[Dict[str, Any]]:
    """
    Get all comments in a Google Doc
    """
    return [
        {
            "id": f"comment_{i}",
            "content": f"This is comment {i} in document {document_id}",
            "author": "user@example.com",
            "createdTime": f"2023-01-02T15:{30+i:02d}:00Z",
            "resolved": False
        }
        for i in range(5)
    ]


@mcp.tool
def delete_document(document_id: str) -> Dict[str, str]:
    """
    Delete a Google Doc
    """
    return {
        "status": "deleted",
        "message": f"Document {document_id} has been deleted"
    }


# Resources
@mcp.resource("http://google-docs-mcp-server.local/status")
def get_docs_status() -> Dict[str, Any]:
    """
    Get the status of the Google Docs MCP server
    """
    return {
        "status": "connected",
        "account": "user@gmail.com",  # This would be the connected account
        "server_time": asyncio.get_event_loop().time(),
        "connected": True
    }


@mcp.resource("http://google-docs-mcp-server.local/templates")
def get_document_templates() -> List[Dict[str, str]]:
    """
    Get available document templates
    """
    return [
        {"id": "template_1", "name": "Business Report", "description": "Template for business reports"},
        {"id": "template_2", "name": "Meeting Notes", "description": "Template for meeting minutes"},
        {"id": "template_3", "name": "Project Proposal", "description": "Template for project proposals"}
    ]


@mcp.resource("http://google-docs-mcp-server.local/usage-stats")
def get_usage_stats() -> Dict[str, Any]:
    """
    Get usage statistics for Google Docs
    """
    return {
        "total_documents": 42,
        "documents_shared": 18,
        "documents_edited_today": 5,
        "storage_used": "150 MB"
    }


# Prompts
@mcp.prompt("/docs-create-document")
def create_document_prompt(
    title: str, 
    content_description: str, 
    template: str = None,
    context: str = ""
) -> str:
    """
    Generate a prompt for creating a new Google Doc
    """
    return f"""
Create a Google Doc with the following requirements:
- Title: {title}
- Content Description: {content_description}
- Template: {template or 'None specified'}
- Context: {context}

Include appropriate structure, formatting, and content based on the description.
"""


@mcp.prompt("/docs-edit-document")
def edit_document_prompt(
    document_id: str, 
    edit_instructions: str, 
    context: str = ""
) -> str:
    """
    Generate a prompt for editing an existing Google Doc
    """
    return f"""
Edit the document {document_id} according to these instructions: {edit_instructions}

Context: {context}

Preserve the document's existing structure while implementing the requested changes.
"""


@mcp.prompt("/docs-review-content")
def review_content_prompt(
    document_id: str, 
    review_aspects: List[str],
    context: str = ""
) -> str:
    """
    Generate a prompt for reviewing document content
    """
    return f"""
Review the document {document_id} focusing on: {review_aspects}

Context: {context}

Provide feedback on content quality, structure, clarity, and any other relevant aspects.
"""


@mcp.prompt("/docs-summarize")
def summarize_document_prompt(
    document_id: str,
    summary_length: str = "medium",
    context: str = ""
) -> str:
    """
    Generate a prompt for summarizing a Google Doc
    """
    return f"""
Create a {summary_length} summary of document {document_id}

Context: {context}

Focus on the key points, main arguments, and important information in the document.
"""


if __name__ == "__main__":
    # Use stdio transport for MCP server (proper MCP protocol communication)
    asyncio.run(mcp.run_stdio_async())