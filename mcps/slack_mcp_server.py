#!/usr/bin/env python3
"""
Slack MCP Server

Provides access to Slack functionality for LLMs through MCP protocol.
"""

from fastmcp import FastMCP
from typing import List, Dict, Any
import asyncio


# Initialize the MCP server
mcp = FastMCP(
    name="Slack MCP Server",
    instructions="Provides access to Slack functionality including messaging, channel management, and workspace operations",
    version="1.0.0"
)


# Tools
@mcp.tool
def list_channels(exclude_archived: bool = True) -> List[Dict[str, Any]]:
    """
    List channels in the Slack workspace
    """
    # This would connect to Slack API in a real implementation
    return [
        {
            "id": f"C012AB{i:03d}",
            "name": f"channel-{i}",
            "purpose": f"Purpose for channel {i}",
            "num_members": 10 + i,
            "created": "2023-01-01T10:00:00Z",
            "is_private": i % 2 == 0
        }
        for i in range(10)
    ]


@mcp.tool
def get_channel_info(channel_id: str) -> Dict[str, Any]:
    """
    Get information about a specific channel
    """
    return {
        "id": channel_id,
        "name": f"channel-{channel_id}",
        "purpose": f"Purpose for channel {channel_id}",
        "num_members": 15,
        "created": "2023-01-01T10:00:00Z",
        "creator": "U012ABCDEF",
        "is_private": False,
        "is_member": True
    }


@mcp.tool
def send_message(channel_id: str, text: str, thread_ts: str = None) -> Dict[str, str]:
    """
    Send a message to a Slack channel
    """
    return {
        "status": "sent",
        "message": f"Message sent to channel {channel_id}",
        "timestamp": "1234567890.001200"
    }


@mcp.tool
def get_messages(
    channel_id: str, 
    limit: int = 20, 
    oldest: str = None, 
    latest: str = None
) -> List[Dict[str, Any]]:
    """
    Get messages from a Slack channel
    """
    return [
        {
            "ts": f"123456789{i}.00{i:02d}",
            "user": f"U{i:08d}",
            "text": f"Sample message {i} in channel {channel_id}",
            "thread_ts": f"123456789{i}.00{i:02d}" if i % 5 == 0 else None
        }
        for i in range(limit)
    ]


@mcp.tool
def search_messages(query: str, channel_id: str = None) -> List[Dict[str, Any]]:
    """
    Search for messages in Slack
    """
    return [
        {
            "ts": f"123456789{i}.00{i:02d}",
            "channel": channel_id or f"C012AB{i:03d}",
            "user": f"U{i:08d}",
            "text": f"Found message containing '{query}' in channel {channel_id or f'C012AB{i:03d}'}",
            "permalink": f"https://example.slack.com/archives/C012AB{i:03d}/p123456789{i}00{i:02d}"
        }
        for i in range(10)
    ]


@mcp.tool
def join_channel(channel_id: str) -> Dict[str, str]:
    """
    Join a Slack channel
    """
    return {
        "status": "joined",
        "message": f"Joined channel {channel_id}"
    }


@mcp.tool
def create_channel(name: str, is_private: bool = False) -> Dict[str, str]:
    """
    Create a new Slack channel
    """
    return {
        "status": "created",
        "channel_id": "CNEWCHANNELID",
        "message": f"Created {'private' if is_private else 'public'} channel {name}"
    }


@mcp.tool
def get_users() -> List[Dict[str, str]]:
    """
    Get list of users in the Slack workspace
    """
    return [
        {
            "id": f"U{i:08d}",
            "name": f"user.{i:03d}",
            "real_name": f"User {i}",
            "email": f"user{i}@example.com",
            "is_bot": i % 7 == 0
        }
        for i in range(20)
    ]


@mcp.tool
def get_user_info(user_id: str) -> Dict[str, str]:
    """
    Get information about a specific user
    """
    return {
        "id": user_id,
        "name": f"user.{user_id}",
        "real_name": f"User {user_id}",
        "email": f"user.{user_id}@example.com",
        "is_bot": False,
        "is_admin": user_id == "U012ADMIN"
    }


# Resources
@mcp.resource("http://slack-mcp-server.local/status")
def get_slack_status() -> Dict[str, Any]:
    """
    Get the status of the Slack MCP server
    """
    return {
        "status": "connected",
        "workspace": "example-workspace",  # This would be the connected workspace
        "bot_user_id": "B012ABCDEF",
        "server_time": asyncio.get_event_loop().time(),
        "connected": True
    }


@mcp.resource("http://slack-mcp-server.local/workspace-info")
def get_workspace_info() -> Dict[str, Any]:
    """
    Get information about the Slack workspace
    """
    return {
        "id": "T012ABCDEF",
        "name": "Example Workspace",
        "domain": "example-workspace",
        "num_users": 42,
        "is_verified": True
    }


@mcp.resource("http://slack-mcp-server.local/apps")
def get_installed_apps() -> List[Dict[str, str]]:
    """
    Get list of installed Slack apps
    """
    return [
        {"id": "A012APP1", "name": "Google Drive", "description": "Google Drive integration"},
        {"id": "A012APP2", "name": "Trello", "description": "Trello integration"},
        {"id": "A012APP3", "name": "Zoom", "description": "Zoom integration"}
    ]


# Prompts
@mcp.prompt("/slack-message-thread")
def create_message_thread_prompt(
    channel_id: str, 
    topic: str, 
    participants: List[str] = None,
    context: str = ""
) -> str:
    """
    Generate a prompt for creating a message thread in Slack
    """
    return f"""
Start a message thread in channel {channel_id} about: {topic}
Participants: {participants or 'All channel members'}
Context: {context}

Create an engaging opening message that prompts discussion.
"""


@mcp.prompt("/slack-channel-summary")
def channel_summary_prompt(
    channel_id: str, 
    time_period: str = "last_24_hours",
    context: str = ""
) -> str:
    """
    Generate a prompt for summarizing channel activity
    """
    return f"""
Generate a summary of activity in channel {channel_id} for the {time_period}
Context: {context}

Include important discussions, key decisions, and action items.
"""


@mcp.prompt("/slack-standup-template")
def standup_template_prompt(
    team_members: List[str], 
    channel_id: str,
    context: str = ""
) -> str:
    """
    Generate a prompt for creating a daily standup template
    """
    return f"""
Create a daily standup template for team: {team_members}
In channel: {channel_id}
Context: {context}

Structure the template to include: what was accomplished yesterday, plans for today, and blockers.
"""


@mcp.prompt("/slack-announcement")
def announcement_prompt(
    audience: List[str], 
    topic: str,
    channel_id: str,
    context: str = ""
) -> str:
    """
    Generate a prompt for creating a Slack announcement
    """
    return f"""
Create an announcement for {audience} about: {topic}
Channel: {channel_id}
Context: {context}

Make the announcement clear, concise, and engaging.
"""


if __name__ == "__main__":
    # Use stdio transport for MCP server (proper MCP protocol communication)
    asyncio.run(mcp.run_stdio_async())