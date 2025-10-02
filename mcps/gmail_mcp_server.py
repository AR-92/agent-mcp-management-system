#!/usr/bin/env python3
"""
Gmail MCP Server

Provides access to Gmail functionality for LLMs through MCP protocol.
"""

from fastmcp import FastMCP
from typing import List, Dict, Any
import asyncio


# Initialize the MCP server
mcp = FastMCP(
    name="Gmail MCP Server",
    instructions="Provides access to Gmail functionality including reading, sending, and managing emails",
    version="1.0.0"
)


# Tools
@mcp.tool
def list_emails(limit: int = 10, folder: str = "inbox") -> List[Dict[str, Any]]:
    """
    List emails from a specified folder
    """
    # This would connect to Gmail API in a real implementation
    return [
        {
            "id": f"email_{i}",
            "subject": f"Sample Email Subject {i}",
            "from": f"sender{i}@example.com",
            "date": "2023-01-01T10:00:00Z",
            "snippet": f"This is a snippet of email {i} content"
        }
        for i in range(limit)
    ]


@mcp.tool
def get_email(email_id: str) -> Dict[str, Any]:
    """
    Get the full content of a specific email
    """
    # This would fetch the actual email from Gmail API in a real implementation
    return {
        "id": email_id,
        "subject": f"Subject for {email_id}",
        "from": "sender@example.com",
        "to": ["recipient@example.com"],
        "date": "2023-01-01T10:00:00Z",
        "body": f"Full body content for email {email_id}",
        "attachments": []
    }


@mcp.tool
def send_email(to: List[str], subject: str, body: str, cc: List[str] = None, bcc: List[str] = None) -> Dict[str, str]:
    """
    Send an email via Gmail
    """
    return {
        "status": "sent",
        "message": f"Email sent successfully to {', '.join(to)}",
        "subject": subject
    }


@mcp.tool
def search_emails(query: str) -> List[Dict[str, Any]]:
    """
    Search for emails matching a query
    """
    return [
        {
            "id": f"search_result_{i}",
            "subject": f"Search Result {i} for '{query}'",
            "from": f"sender{i}@example.com",
            "date": "2023-01-01T10:00:00Z",
            "snippet": f"Snippet containing {query}"
        }
        for i in range(5)
    ]


@mcp.tool
def delete_email(email_id: str) -> Dict[str, str]:
    """
    Delete an email from Gmail
    """
    return {
        "status": "deleted",
        "message": f"Email {email_id} has been deleted"
    }


# Resources
@mcp.resource("http://gmail-mcp-server.local/status")
def get_gmail_status() -> Dict[str, Any]:
    """
    Get the status of the Gmail MCP server
    """
    return {
        "status": "connected",
        "account": "user@gmail.com",  # This would be the connected account
        "server_time": asyncio.get_event_loop().time(),
        "connected": True
    }


@mcp.resource("http://gmail-mcp-server.local/folders")
def get_folders() -> List[Dict[str, str]]:
    """
    Get list of available folders in Gmail
    """
    return [
        {"name": "inbox", "id": "inbox", "displayName": "Inbox"},
        {"name": "sent", "id": "sent", "displayName": "Sent"},
        {"name": "drafts", "id": "drafts", "displayName": "Drafts"},
        {"name": "spam", "id": "spam", "displayName": "Spam"},
        {"name": "trash", "id": "trash", "displayName": "Trash"}
    ]


@mcp.resource("http://gmail-mcp-server.local/stats")
def get_gmail_stats() -> Dict[str, Any]:
    """
    Get statistics about Gmail usage
    """
    return {
        "total_emails": 1500,
        "unread_emails": 5,
        "storage_used": "12.5 GB",
        "storage_quota": "15 GB"
    }


# Prompts
@mcp.prompt("/gmail-compose-email")
def compose_email_prompt(recipient: str, subject: str = "", context: str = "") -> str:
    """
    Generate a prompt for composing an email
    """
    return f"""
Compose an email to {recipient}
Subject: {subject}

Context: {context}

Please write a professional email considering:
1. Appropriate greeting
2. Clear subject matter
3. Professional tone
4. Appropriate closing
"""


@mcp.prompt("/gmail-follow-up")
def follow_up_email_prompt(thread_id: str, previous_context: str = "") -> str:
    """
    Generate a prompt for following up on an email thread
    """
    return f"""
Follow up on email thread: {thread_id}

Previous context: {previous_context}

Create a follow-up email that:
1. References the previous conversation
2. Addresses any pending questions or actions
3. Maintains continuity with the conversation
"""


if __name__ == "__main__":
    # Use stdio transport for MCP server (proper MCP protocol communication)
    asyncio.run(mcp.run_stdio_async())