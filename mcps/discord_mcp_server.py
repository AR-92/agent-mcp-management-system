#!/usr/bin/env python3
"""
Discord MCP Server

Provides access to Discord functionality for LLMs through MCP protocol.
"""

from fastmcp import FastMCP
from typing import List, Dict, Any
import asyncio


# Initialize the MCP server
mcp = FastMCP(
    name="Discord MCP Server",
    instructions="Provides access to Discord functionality including messaging, channel management, and server operations",
    version="1.0.0"
)


# Tools
@mcp.tool
def list_servers() -> List[Dict[str, Any]]:
    """
    List Discord servers the bot is connected to
    """
    # This would connect to Discord API in a real implementation
    return [
        {
            "id": f"server_{i}",
            "name": f"Server {i}",
            "member_count": 50 + i * 10,
            "owner_id": f"owner_{i}",
            "region": "us-east",
            "icon_url": f"https://example.com/icons/server_{i}.png"
        }
        for i in range(5)
    ]


@mcp.tool
def list_channels(server_id: str) -> List[Dict[str, Any]]:
    """
    List channels in a specific Discord server
    """
    return [
        {
            "id": f"text_{i:03d}",
            "name": f"text-channel-{i}",
            "type": "text",
            "topic": f"Topic for channel {i}",
            "position": i
        }
        for i in range(8)
    ] + [
        {
            "id": f"voice_{i:03d}",
            "name": f"voice-channel-{i}",
            "type": "voice",
            "bitrate": 64000,
            "user_limit": 0
        }
        for i in range(3)
    ]


@mcp.tool
def get_channel_info(channel_id: str) -> Dict[str, Any]:
    """
    Get information about a specific channel
    """
    return {
        "id": channel_id,
        "name": f"channel-{channel_id}",
        "type": "text",
        "topic": f"Topic for channel {channel_id}",
        "server_id": "server_1",
        "position": 5,
        "nsfw": False
    }


@mcp.tool
def send_message(channel_id: str, content: str) -> Dict[str, str]:
    """
    Send a message to a Discord channel
    """
    return {
        "status": "sent",
        "message": f"Message sent to channel {channel_id}",
        "message_id": "msg_12345"
    }


@mcp.tool
def get_messages(
    channel_id: str, 
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Get recent messages from a Discord channel
    """
    return [
        {
            "id": f"msg_{i:05d}",
            "author": f"user_{i}",
            "content": f"Sample message {i} in channel {channel_id}",
            "timestamp": "2023-01-01T10:00:00Z",
            "pinned": False
        }
        for i in range(limit)
    ]


@mcp.tool
def search_messages(query: str, channel_id: str = None) -> List[Dict[str, Any]]:
    """
    Search for messages in Discord
    """
    return [
        {
            "id": f"search_result_{i}",
            "channel_id": channel_id or f"text_{i:03d}",
            "author": f"user_{i}",
            "content": f"Found message containing '{query}'",
            "timestamp": "2023-01-01T10:00:00Z"
        }
        for i in range(10)
    ]


@mcp.tool
def create_text_channel(server_id: str, name: str, topic: str = None) -> Dict[str, Any]:
    """
    Create a new text channel in a Discord server
    """
    return {
        "status": "created",
        "channel_id": "new_text_channel_id",
        "message": f"Created text channel '{name}' in server {server_id}"
    }


@mcp.tool
def create_voice_channel(server_id: str, name: str, bitrate: int = 64000) -> Dict[str, Any]:
    """
    Create a new voice channel in a Discord server
    """
    return {
        "status": "created",
        "channel_id": "new_voice_channel_id",
        "message": f"Created voice channel '{name}' in server {server_id}"
    }


@mcp.tool
def get_server_members(server_id: str) -> List[Dict[str, str]]:
    """
    Get list of members in a Discord server
    """
    return [
        {
            "id": f"user_{i:05d}",
            "username": f"user.{i:03d}",
            "display_name": f"User {i}",
            "is_bot": i % 7 == 0,
            "join_date": "2023-01-01T10:00:00Z"
        }
        for i in range(25)
    ]


# Resources
@mcp.resource("http://discord-mcp-server.local/status")
def get_discord_status() -> Dict[str, Any]:
    """
    Get the status of the Discord MCP server
    """
    return {
        "status": "connected",
        "user": "BotUser#1234",  # This would be the connected bot user
        "server_time": asyncio.get_event_loop().time(),
        "connected": True,
        "guilds": 3,
        "channels": 32
    }


@mcp.resource("http://discord-mcp-server.local/bot-info")
def get_bot_info() -> Dict[str, Any]:
    """
    Get information about the Discord bot
    """
    return {
        "id": "bot_12345",
        "username": "MCPBot",
        "discriminator": "1234",
        "avatar_url": "https://example.com/bot_avatar.png",
        "created_at": "2023-01-01T00:00:00Z",
        "permissions": ["SEND_MESSAGES", "VIEW_CHANNEL", "READ_MESSAGE_HISTORY"]
    }


@mcp.resource("http://discord-mcp-server.local/emojis")
def get_server_emojis(server_id: str) -> List[Dict[str, str]]:
    """
    Get custom emojis in a Discord server
    """
    return [
        {"id": f"emoji_{i}", "name": f"custom_emoji_{i}", "url": f"https://example.com/emoji_{i}.png"}
        for i in range(10)
    ]


# Prompts
@mcp.prompt("/discord-welcome-message")
def welcome_message_prompt(
    server_name: str, 
    new_member_name: str,
    channel_id: str,
    context: str = ""
) -> str:
    """
    Generate a prompt for creating a welcome message
    """
    return f"""
Create a welcome message for new member '{new_member_name}' in server '{server_name}'
Channel: {channel_id}
Context: {context}

Make the message friendly and help the new member understand the server rules and channels.
"""


@mcp.prompt("/discord-announcement")
def announcement_prompt(
    server_id: str, 
    target_channel: str,
    topic: str,
    context: str = ""
) -> str:
    """
    Generate a prompt for creating a Discord announcement
    """
    return f"""
Create an announcement for server {server_id} in channel {target_channel} about: {topic}
Context: {context}

Format the message appropriately for Discord with any necessary mentions or attachments.
"""


@mcp.prompt("/discord-channel-topic")
def channel_topic_prompt(
    channel_id: str, 
    topic_description: str,
    context: str = ""
) -> str:
    """
    Generate a prompt for creating a channel topic
    """
    return f"""
Create an appropriate channel topic for channel {channel_id} related to: {topic_description}
Context: {context}

Make it concise but informative for users visiting the channel.
"""


@mcp.prompt("/discord-event-announcement")
def event_announcement_prompt(
    server_id: str, 
    event_details: str,
    target_role: str = None,
    context: str = ""
) -> str:
    """
    Generate a prompt for announcing an event in Discord
    """
    return f"""
Create an event announcement for server {server_id} with details: {event_details}
Target role to mention: {target_role or 'None'}
Context: {context}

Include all relevant event information and encourage participation.
"""


if __name__ == "__main__":
    # Use stdio transport for MCP server (proper MCP protocol communication)
    asyncio.run(mcp.run_stdio_async())