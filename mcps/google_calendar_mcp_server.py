#!/usr/bin/env python3
"""
Google Calendar MCP Server

Provides access to Google Calendar functionality for LLMs through MCP protocol.
"""

from fastmcp import FastMCP
from typing import List, Dict, Any
import asyncio
from datetime import datetime, timedelta


# Initialize the MCP server
mcp = FastMCP(
    name="Google Calendar MCP Server",
    instructions="Provides access to Google Calendar functionality including events, scheduling, and calendar management",
    version="1.0.0"
)


# Tools
@mcp.tool
def list_events(calendar_id: str = "primary", time_min: str = None, time_max: str = None, max_results: int = 10) -> List[Dict[str, Any]]:
    """
    List events from a specified calendar
    """
    # This would connect to Google Calendar API in a real implementation
    now = datetime.now()
    return [
        {
            "id": f"event_{i}",
            "summary": f"Sample Event {i}",
            "start": {"dateTime": (now + timedelta(days=i)).isoformat()},
            "end": {"dateTime": (now + timedelta(days=i, hours=1)).isoformat()},
            "location": f"Location {i}",
            "description": f"Description for event {i}"
        }
        for i in range(max_results)
    ]


@mcp.tool
def get_event(event_id: str, calendar_id: str = "primary") -> Dict[str, Any]:
    """
    Get the details of a specific event
    """
    # This would fetch the actual event from Google Calendar API in a real implementation
    return {
        "id": event_id,
        "summary": f"Event: {event_id}",
        "start": {"dateTime": datetime.now().isoformat()},
        "end": {"dateTime": (datetime.now() + timedelta(hours=1)).isoformat()},
        "location": "Sample Location",
        "description": f"Details for event {event_id}",
        "attendees": [
            {"email": "attendee1@example.com", "responseStatus": "accepted"},
            {"email": "attendee2@example.com", "responseStatus": "pending"}
        ]
    }


@mcp.tool
def create_event(
    summary: str, 
    start_time: str, 
    end_time: str, 
    description: str = "", 
    location: str = "",
    attendees: List[str] = None,
    calendar_id: str = "primary"
) -> Dict[str, str]:
    """
    Create a new event in Google Calendar
    """
    if attendees is None:
        attendees = []
    
    return {
        "status": "created",
        "message": f"Event '{summary}' created successfully",
        "event_id": "new_event_id"
    }


@mcp.tool
def update_event(
    event_id: str,
    summary: str = None,
    start_time: str = None,
    end_time: str = None,
    description: str = None,
    location: str = None,
    calendar_id: str = "primary"
) -> Dict[str, str]:
    """
    Update an existing event in Google Calendar
    """
    return {
        "status": "updated",
        "message": f"Event {event_id} has been updated"
    }


@mcp.tool
def delete_event(event_id: str, calendar_id: str = "primary") -> Dict[str, str]:
    """
    Delete an event from Google Calendar
    """
    return {
        "status": "deleted",
        "message": f"Event {event_id} has been deleted"
    }


@mcp.tool
def search_events(query: str, calendar_id: str = "primary") -> List[Dict[str, Any]]:
    """
    Search for events matching a query
    """
    return [
        {
            "id": f"search_result_{i}",
            "summary": f"Search Result {i} for '{query}'",
            "start": {"dateTime": (datetime.now() + timedelta(days=i)).isoformat()},
            "end": {"dateTime": (datetime.now() + timedelta(days=i, hours=1)).isoformat()},
            "description": f"Event containing '{query}'"
        }
        for i in range(5)
    ]


# Resources
@mcp.resource("http://google-calendar-mcp-server.local/status")
def get_calendar_status() -> Dict[str, Any]:
    """
    Get the status of the Google Calendar MCP server
    """
    return {
        "status": "connected",
        "account": "user@gmail.com",  # This would be the connected account
        "server_time": datetime.now().isoformat(),
        "connected": True
    }


@mcp.resource("http://google-calendar-mcp-server.local/calendars")
def get_calendars() -> List[Dict[str, str]]:
    """
    Get list of available calendars
    """
    return [
        {"id": "primary", "summary": "Primary Calendar", "description": "Default calendar"},
        {"id": "work", "summary": "Work Calendar", "description": "Work-related events"},
        {"id": "personal", "summary": "Personal Calendar", "description": "Personal events"}
    ]


@mcp.resource("http://google-calendar-mcp-server.local/settings")
def get_calendar_settings() -> Dict[str, Any]:
    """
    Get calendar settings
    """
    return {
        "working_hours_start": "09:00",
        "working_hours_end": "18:00",
        "default_reminder_time": 10,  # minutes
        "default_timezone": "America/New_York"
    }


# Prompts
@mcp.prompt("/calendar-schedule-meeting")
def schedule_meeting_prompt(
    participants: List[str], 
    duration_minutes: int = 60, 
    preferred_times: List[str] = None,
    context: str = ""
) -> str:
    """
    Generate a prompt for scheduling a meeting
    """
    return f"""
Schedule a meeting with participants: {', '.join(participants)}
Duration: {duration_minutes} minutes
Preferred times: {preferred_times or 'Any available time'}
Context: {context}

Consider:
1. Preferred times if specified
2. Working hours (9am-6pm)
3. Participant availability
4. Meeting purpose and context
"""


@mcp.prompt("/calendar-event-reminder")
def event_reminder_prompt(event_id: str, time_before: int = 10, context: str = "") -> str:
    """
    Generate a reminder message for an upcoming event
    """
    return f"""
Create a reminder for event {event_id}
Time before event: {time_before} minutes
Context: {context}

Include:
1. Event details
2. Action items if any
3. Preparation needed
4. Connection information if applicable
"""


@mcp.prompt("/calendar-conflict-resolution")
def resolve_calendar_conflict_prompt(event1_id: str, event2_id: str, context: str = "") -> str:
    """
    Generate suggestions for resolving calendar conflicts
    """
    return f"""
Resolve conflict between events:
- Event 1: {event1_id}
- Event 2: {event2_id}

Context: {context}

Provide options for resolving this conflict:
1. Rescheduling possibilities
2. Priority considerations
3. Alternative solutions
"""


if __name__ == "__main__":
    # Use stdio transport for MCP server (proper MCP protocol communication)
    asyncio.run(mcp.run_stdio_async())