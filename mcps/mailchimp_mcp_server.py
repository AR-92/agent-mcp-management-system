#!/usr/bin/env python3
"""
Mailchimp MCP Server

Provides access to Mailchimp functionality for LLMs through MCP protocol.
"""

from fastmcp import FastMCP
from typing import List, Dict, Any
import asyncio


# Initialize the MCP server
mcp = FastMCP(
    name="Mailchimp MCP Server",
    instructions="Provides access to Mailchimp functionality including email campaigns, audience management, and marketing automation",
    version="1.0.0"
)


# Tools
@mcp.tool
def list_campaigns(
    status: str = "sent", 
    type: str = "regular",
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    List campaigns in the Mailchimp account
    """
    # This would connect to Mailchimp API in a real implementation
    return [
        {
            "id": f"camp_{i:04d}",
            "type": type,
            "status": status,
            "title": f"Campaign {i}: Newsletter",
            "subject_line": f"Subject for Campaign {i}",
            "preview_text": f"Preview text for Campaign {i}",
            "recipients": {"list_id": "list_1", "list_name": "Subscribers"},
            "send_time": "2023-01-01T10:00:00Z",
            "emails_sent": 1250 + i * 100
        }
        for i in range(limit)
    ]


@mcp.tool
def get_campaign_info(campaign_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific campaign
    """
    return {
        "id": campaign_id,
        "type": "regular",
        "status": "sent",
        "title": f"Campaign {campaign_id}",
        "subject_line": f"Subject for {campaign_id}",
        "preview_text": f"Preview text for {campaign_id}",
        "recipients": {
            "list_id": "list_1",
            "list_name": "Main Subscribers",
            "recipient_count": 2500
        },
        "from_name": "Marketing Team",
        "reply_to": "marketing@example.com",
        "send_time": "2023-01-01T10:00:00Z",
        "emails_sent": 2450,
        "open_rate": 28.5,
        "click_rate": 3.2
    }


@mcp.tool
def create_campaign(
    subject_line: str,
    title: str,
    content: str,
    list_id: str,
    from_name: str = "Marketing Team",
    reply_to: str = "noreply@example.com"
) -> Dict[str, str]:
    """
    Create a new email campaign
    """
    return {
        "status": "created",
        "campaign_id": "new_campaign_id",
        "message": f"Campaign '{title}' created successfully"
    }


@mcp.tool
def list_audiences(limit: int = 20) -> List[Dict[str, Any]]:
    """
    List audiences (email lists) in the Mailchimp account
    """
    return [
        {
            "id": f"list_{i:03d}",
            "name": f"Audience {i}",
            "member_count": 1200 + i * 100,
            "type": "html",
            "email_type_option": True,
            "subscribe_url_short": f"https://example.com/subscribe/{i}",
            "stats": {
                "member_count": 1200 + i * 100,
                "unsubscribe_count": 10 + i,
                "cleaned_count": 5 + i,
                "member_count_since_send": 50 + i,
                "unsubscribe_count_since_send": 1 + i
            }
        }
        for i in range(limit)
    ]


@mcp.tool
def get_audience_info(list_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific audience
    """
    return {
        "id": list_id,
        "name": f"Audience {list_id}",
        "member_count": 2500,
        "type": "html",
        "email_type_option": True,
        "subscribe_url_short": f"https://example.com/subscribe/{list_id}",
        "stats": {
            "member_count": 2500,
            "unsubscribe_count": 25,
            "cleaned_count": 10,
            "member_count_since_send": 75,
            "unsubscribe_count_since_send": 3
        },
        "merge_fields": [
            {"tag": "FNAME", "name": "First Name", "type": "text"},
            {"tag": "LNAME", "name": "Last Name", "type": "text"},
            {"tag": "PHONE", "name": "Phone", "type": "phone"}
        ]
    }


@mcp.tool
def add_subscriber(
    list_id: str,
    email: str,
    first_name: str = "",
    last_name: str = "",
    merge_fields: Dict[str, str] = None
) -> Dict[str, str]:
    """
    Add a subscriber to an audience
    """
    return {
        "status": "added",
        "message": f"Subscriber {email} added to list {list_id}"
    }


@mcp.tool
def get_subscriber_info(list_id: str, email: str) -> Dict[str, Any]:
    """
    Get information about a specific subscriber
    """
    return {
        "id": "sub_12345",
        "email_address": email,
        "status": "subscribed",
        "timestamp_signup": "2023-01-01T10:00:00Z",
        "timestamp_optin": "2023-01-01T10:00:00Z",
        "merge_fields": {
            "FNAME": first_name,
            "LNAME": last_name
        },
        "tags": ["New Subscriber", "Web Signup"],
        "stats": {
            "avg_open_rate": 32.5,
            "avg_click_rate": 4.1
        }
    }


@mcp.tool
def get_campaign_report(campaign_id: str) -> Dict[str, Any]:
    """
    Get detailed report for a specific campaign
    """
    return {
        "campaign_id": campaign_id,
        "emails_sent": 2450,
        "ab_split": None,
        "send_time": "2023-01-01T10:00:00Z",
        "opens": {
            "opens_total": 698,
            "unique_opens": 524,
            "open_rate": 28.5
        },
        "clicks": {
            "clicks_total": 78,
            "unique_clicks": 65,
            "click_rate": 3.2
        },
        "industry_stats": {
            "type": "All",
            "open_rate": 17.86,
            "click_rate": 2.33,
            "bounce_rate": 0.69
        },
        "bounce_hard": 5,
        "bounce_soft": 12,
        "unsubscribe_count": 8
    }


@mcp.tool
def schedule_campaign(campaign_id: str, send_time: str) -> Dict[str, str]:
    """
    Schedule a campaign to be sent at a specific time
    """
    return {
        "status": "scheduled",
        "message": f"Campaign {campaign_id} scheduled for {send_time}"
    }


# Resources
@mcp.resource("http://mailchimp-mcp-server.local/status")
def get_mailchimp_status() -> Dict[str, Any]:
    """
    Get the status of the Mailchimp MCP server
    """
    return {
        "status": "connected",
        "account_id": "account_12345",
        "server_time": asyncio.get_event_loop().time(),
        "connected": True,
        "username": "user@example.com"
    }


@mcp.resource("http://mailchimp-mcp-server.local/account-info")
def get_account_info() -> Dict[str, Any]:
    """
    Get Mailchimp account information
    """
    return {
        "account_id": "account_12345",
        "username": "user@example.com",
        "account_name": "Example Marketing Account",
        "email": "user@example.com",
        "first_name": "Marketing",
        "last_name": "Manager",
        "total_subscribers": 12500,
        "creation_date": "2020-01-15T10:00:00Z"
    }


@mcp.resource("http://mailchimp-mcp-server.local/templates")
def get_templates() -> List[Dict[str, str]]:
    """
    Get available email templates
    """
    return [
        {"id": "temp_1", "name": "Monthly Newsletter", "category": "Newsletter"},
        {"id": "temp_2", "name": "Promotional Offer", "category": "Promotion"},
        {"id": "temp_3", "name": "Welcome Series", "category": "Automation"},
        {"id": "temp_4", "name": "Event Announcement", "category": "Event"},
        {"id": "temp_5", "name": "Product Launch", "category": "Product"}
    ]


# Prompts
@mcp.prompt("/mailchimp-email-template")
def email_template_prompt(
    template_type: str, 
    target_audience: str,
    brand_voice: str,
    context: str = ""
) -> str:
    """
    Generate a prompt for creating an email template
    """
    return f"""
Create an email template for: {template_type}
Target Audience: {target_audience}
Brand Voice: {brand_voice}
Context: {context}

Design a responsive template that aligns with brand guidelines and engages the target audience.
"""


@mcp.prompt("/mailchimp-campaign-strategy")
def campaign_strategy_prompt(
    goal: str, 
    audience: str,
    budget: str,
    context: str = ""
) -> str:
    """
    Generate a prompt for planning a Mailchimp campaign strategy
    """
    return f"""
Plan a Mailchimp campaign strategy for goal: {goal}
Target Audience: {audience}
Budget: {budget}
Context: {context}

Include timing, segmentation, content themes, and success metrics.
"""


@mcp.prompt("/mailchimp-subject-line")
def subject_line_prompt(
    campaign_type: str, 
    audience: str,
    context: str = ""
) -> str:
    """
    Generate a prompt for creating effective subject lines
    """
    return f"""
Create compelling subject lines for campaign type: {campaign_type}
Target Audience: {audience}
Context: {context}

Focus on increasing open rates while accurately representing the email content.
"""


@mcp.prompt("/mailchimp-audience-segmentation")
def audience_segmentation_prompt(
    list_id: str, 
    segmentation_criteria: List[str],
    context: str = ""
) -> str:
    """
    Generate a prompt for audience segmentation
    """
    return f"""
Segment audience in list {list_id} based on: {segmentation_criteria}
Context: {context}

Determine the most effective ways to divide the audience for targeted messaging.
"""


if __name__ == "__main__":
    # Use stdio transport for MCP server (proper MCP protocol communication)
    asyncio.run(mcp.run_stdio_async())