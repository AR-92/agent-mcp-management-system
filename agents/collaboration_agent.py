"""
Collaboration & Communication Agent using Strands Agents SDK

This agent uses multiple MCPs to manage various communication and collaboration tools,
including Slack, Trello, Google services, and more.
"""

from strandsagents import Agent
from typing import Dict, Any, List
import json
from datetime import datetime, timedelta


def list_slack_channels(exclude_archived: bool = True) -> List[Dict[str, Any]]:
    """
    List channels in the Slack workspace.
    
    Args:
        exclude_archived: Whether to exclude archived channels
        
    Returns:
        List of dictionaries containing channel information
    """
    # This would connect to the Slack MCP server in a real implementation
    return [
        {
            "id": f"C{i:04d}",
            "name": f"general" if i == 1 else f"channel-{i}",
            "num_members": 25 if i == 1 else 8,
            "created": (datetime.now() - timedelta(days=i*10)).isoformat(),
            "is_archived": False,
            "purpose": f"General discussion" if i == 1 else f"Project discussion for team {i}"
        }
        for i in range(1, 6)
    ]


def send_slack_message(
    channel_id: str, 
    message: str, 
    thread_ts: str = None,
    attachments: List[Dict[str, Any]] = []
) -> Dict[str, Any]:
    """
    Send a message to a Slack channel.
    
    Args:
        channel_id: ID of the channel to send the message to
        message: Content of the message
        thread_ts: Optional timestamp to reply in a thread
        attachments: Optional list of attachments
        
    Returns:
        Dictionary containing the message sending result
    """
    # This would connect to the Slack MCP server in a real implementation
    return {
        "status": "sent",
        "message_ts": f"{datetime.now().timestamp()}",
        "channel": channel_id,
        "message_length": len(message),
        "threaded": thread_ts is not None
    }


def list_trello_boards() -> List[Dict[str, Any]]:
    """
    List Trello boards accessible to the user.
    
    Returns:
        List of dictionaries containing board information
    """
    # This would connect to the Trello MCP server in a real implementation
    return [
        {
            "id": f"board_{i}",
            "name": f"Project Board {i}",
            "description": f"Board for Project {i} management",
            "member_count": 5,
            "card_count": 12,
            "list_count": 4,
            "created_at": (datetime.now() - timedelta(days=i*7)).isoformat(),
            "is_closed": False
        }
        for i in range(1, 5)
    ]


def add_trello_card(
    board_id: str,
    list_id: str,
    card_name: str,
    description: str = "",
    due_date: str = None,
    labels: List[str] = []
) -> Dict[str, Any]:
    """
    Add a card to a Trello list.
    
    Args:
        board_id: ID of the board
        list_id: ID of the list
        card_name: Name of the card
        description: Description of the card
        due_date: Due date for the card
        labels: List of labels to apply to the card
        
    Returns:
        Dictionary containing the card creation result
    """
    # This would connect to the Trello MCP server in a real implementation
    return {
        "status": "created",
        "card_id": f"card_{board_id}_{card_name.replace(' ', '_')}",
        "card_name": card_name,
        "board_id": board_id,
        "list_id": list_id,
        "labels": labels
    }


def list_google_calendar_events(
    calendar_id: str = "primary", 
    time_min: str = None, 
    time_max: str = None, 
    max_results: int = 10
) -> List[Dict[str, Any]]:
    """
    List events from a Google Calendar.
    
    Args:
        calendar_id: ID of the calendar to query
        time_min: Lower bound for event start time
        time_max: Upper bound for event start time
        max_results: Maximum number of events to return
        
    Returns:
        List of dictionaries containing event information
    """
    # This would connect to the Google Calendar MCP server in a real implementation
    time_min = time_min or datetime.now().isoformat()
    time_max = time_max or (datetime.now() + timedelta(days=7)).isoformat()
    
    return [
        {
            "id": f"event_{i}",
            "summary": f"Meeting {i}",
            "start": {
                "dateTime": (datetime.now() + timedelta(days=i)).isoformat()
            },
            "end": {
                "dateTime": (datetime.now() + timedelta(days=i, hours=1)).isoformat()
            },
            "attendees": [
                {"email": f"attendee{i}@example.com", "responseStatus": "accepted"}
            ],
            "location": f"Conference Room {i}" if i < 3 else f"Virtual Meeting"
        }
        for i in range(1, max_results + 1)
    ]


def create_google_calendar_event(
    title: str,
    start_time: str,
    end_time: str,
    description: str = "",
    attendees: List[str] = [],
    location: str = ""
) -> Dict[str, Any]:
    """
    Create a Google Calendar event.
    
    Args:
        title: Title of the event
        start_time: Start time in ISO format
        end_time: End time in ISO format
        description: Event description
        attendees: List of attendee email addresses
        location: Event location
        
    Returns:
        Dictionary containing the created event information
    """
    # This would connect to the Google Calendar MCP server in a real implementation
    return {
        "status": "created",
        "event_id": f"event_{title.replace(' ', '_')}_{start_time.replace(':', '-')}",
        "title": title,
        "start_time": start_time,
        "end_time": end_time,
        "attendees": attendees,
        "location": location
    }


def list_google_drive_files(
    folder_id: str = "root", 
    file_type: str = None, 
    query: str = None, 
    max_results: int = 20
) -> List[Dict[str, Any]]:
    """
    List files in Google Drive.
    
    Args:
        folder_id: ID of the folder to list files from
        file_type: Type of files to filter (e.g., document, spreadsheet, pdf)
        query: Search query to filter files
        max_results: Maximum number of files to return
        
    Returns:
        List of dictionaries containing file information
    """
    # This would connect to the Google Drive MCP server in a real implementation
    return [
        {
            "id": f"file_{i}",
            "name": f"Document {i}.docx" if i % 3 == 0 else f"Spreadsheet {i}.xlsx" if i % 3 == 1 else f"Presentation {i}.pptx",
            "mimeType": "application/vnd.google-apps.document" if i % 3 == 0 else "application/vnd.google-apps.spreadsheet" if i % 3 == 1 else "application/vnd.google-apps.presentation",
            "size": f"{(i * 100) % 5000}KB",
            "modifiedTime": (datetime.now() - timedelta(days=i)).isoformat(),
            "owners": [{"displayName": "User Name", "emailAddress": "user@example.com"}]
        }
        for i in range(1, max_results + 1)
    ]


def search_google_docs(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Search Google Docs for documents matching the query.
    
    Args:
        query: Search query
        max_results: Maximum number of results to return
        
    Returns:
        List of dictionaries containing document information
    """
    # This would connect to the Google Docs MCP server in a real implementation
    return [
        {
            "id": f"doc_{i}",
            "title": f"Document matching '{query}' - {i}",
            "snippet": f"This document contains information about {query} and related topics...",
            "last_modified": (datetime.now() - timedelta(days=i*2)).isoformat(),
            "owners": ["user@example.com"]
        }
        for i in range(1, max_results + 1)
    ]


# Create a collaboration and communication agent
agent = Agent(
    system_prompt="You are a collaboration and communication assistant. You can manage Slack channels and messages, Trello boards and cards, Google Calendar events, Google Drive files, and Google Docs. When asked to coordinate team activities, suggest using the appropriate tools and provide clear instructions for team collaboration."
)


def setup_collab_agent():
    """Set up the collaboration and communication agent with tools."""
    try:
        agent.add_tool(list_slack_channels)
        agent.add_tool(send_slack_message)
        agent.add_tool(list_trello_boards)
        agent.add_tool(add_trello_card)
        agent.add_tool(list_google_calendar_events)
        agent.add_tool(create_google_calendar_event)
        agent.add_tool(list_google_drive_files)
        agent.add_tool(search_google_docs)
        print("Collaboration and communication tools successfully registered with the agent.")
        return True
    except AttributeError as e:
        print(f"Note: Tool registration API may vary depending on the specific Strands implementation. Error: {e}")
        return False


def run_collab_agent(user_input: str):
    """
    Run the collaboration and communication agent with the given user input.
    
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
        return f"Simulated response: Collaboration and communication agent. You requested: '{user_input}'"
    except Exception as e:
        return f"Error processing your request: {str(e)}"


def main():
    """Main function to run the collaboration and communication agent."""
    # Set up tools
    tools_setup = setup_collab_agent()
    
    print("Collaboration & Communication Agent")
    print("This agent can:")
    print("- Manage Slack channels and send messages")
    print("- Manage Trello boards and add cards")
    print("- Manage Google Calendar events")
    print("- Access Google Drive files")
    print("- Search Google Docs")
    print("Type 'quit' to exit.\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Agent: Goodbye! Collaboration assistant signing off.")
            break
            
        response = run_collab_agent(user_input)
        print(f"Agent: {response}\n")


if __name__ == "__main__":
    main()