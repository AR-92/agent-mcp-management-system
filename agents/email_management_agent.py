"""
Email Management Agent using Strands Agents SDK

This agent uses the Gmail and SMTP MCPs to handle email operations.
"""

from strandsagents import Agent
from typing import Dict, Any, List
import json


def send_email(
    to: str,
    subject: str,
    body: str,
    cc: str = "",
    bcc: str = "",
    attachments: List[str] = []
) -> Dict[str, Any]:
    """
    Send an email using SMTP functionality.
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body content
        cc: CC recipients (comma-separated)
        bcc: BCC recipients (comma-separated)
        attachments: List of file paths to attach
        
    Returns:
        Dictionary containing the result of the email sending operation
    """
    # This would connect to the SMTP MCP server in a real implementation
    return {
        "status": "success",
        "message": f"Email sent to {to} with subject '{subject}'",
        "details": {
            "recipient": to,
            "subject": subject,
            "has_attachments": len(attachments) > 0,
            "attachment_count": len(attachments)
        }
    }


def read_emails(limit: int = 10, folder: str = "inbox") -> List[Dict[str, Any]]:
    """
    Read emails from a specified folder.
    
    Args:
        limit: Maximum number of emails to retrieve
        folder: Folder to read from (e.g., inbox, sent, drafts)
        
    Returns:
        List of dictionaries containing email information
    """
    # This would connect to the Gmail MCP server in a real implementation
    return [
        {
            "id": f"email_{i}",
            "subject": f"Sample Email Subject {i}",
            "sender": f"sender{i}@example.com",
            "date": "2023-10-02",
            "snippet": f"This is a sample email snippet for email {i}"
        }
        for i in range(1, limit + 1)
    ]


def create_calendar_event(
    title: str,
    start_time: str,
    end_time: str,
    description: str = "",
    attendees: List[str] = [],
    location: str = ""
) -> Dict[str, Any]:
    """
    Create a calendar event using Google Calendar MCP.
    
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
        "event_id": "event_12345",
        "title": title,
        "start_time": start_time,
        "end_time": end_time,
        "attendees": attendees
    }


# Create an email management agent that can send emails, read emails, and create calendar events
agent = Agent(
    system_prompt="You are an email management assistant. You can send emails, read emails from various folders, and create calendar events. When asked to schedule meetings, suggest creating calendar events and sending confirmation emails. Be helpful and provide clear information about email and calendar operations."
)


def setup_email_management_agent():
    """Set up the email management agent with tools."""
    try:
        agent.add_tool(send_email)
        agent.add_tool(read_emails)
        agent.add_tool(create_calendar_event)
        print("Email management tools successfully registered with the agent.")
        return True
    except AttributeError as e:
        print(f"Note: Tool registration API may vary depending on the specific Strands implementation. Error: {e}")
        return False


def run_email_agent(user_input: str):
    """
    Run the email management agent with the given user input.
    
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
        return f"Simulated response: Email management agent. You requested: '{user_input}'"
    except Exception as e:
        return f"Error processing your request: {str(e)}"


def main():
    """Main function to run the email management agent."""
    # Set up tools
    tools_setup = setup_email_management_agent()
    
    print("Email Management Agent")
    print("This agent can:")
    print("- Send emails (e.g., 'send an email to user@example.com with subject Hello')")
    print("- Read emails (e.g., 'read my last 5 emails')")
    print("- Create calendar events (e.g., 'schedule a meeting tomorrow at 10am')")
    print("Type 'quit' to exit.\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Agent: Goodbye! Email management assistant signing off.")
            break
            
        response = run_email_agent(user_input)
        print(f"Agent: {response}\n")


if __name__ == "__main__":
    main()