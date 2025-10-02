"""
Gmail Agent using Strands Agents SDK

This agent uses the Gmail MCP to manage email operations through Gmail.
"""

from strandsagents import Agent
from typing import Dict, Any, List
import json
from datetime import datetime, timedelta


def list_emails(
    limit: int = 10,
    folder: str = "inbox",
    unread_only: bool = False,
    query: str = None
) -> List[Dict[str, Any]]:
    """
    List emails from a specified folder.
    
    Args:
        limit: Maximum number of emails to retrieve
        folder: Folder to list emails from (e.g., inbox, sent, drafts, spam)
        unread_only: Whether to return only unread emails
        query: Additional search query to filter emails
        
    Returns:
        List of dictionaries containing email information
    """
    # This would connect to the Gmail MCP server in a real implementation
    return [
        {
            "id": f"email_{i}",
            "thread_id": f"thread_{i}",
            "subject": f"Email Subject {i}" if not query else f"{query} Subject {i}",
            "sender": f"sender{i}@example.com",
            "recipient": "me@example.com",
            "date": (datetime.now() - timedelta(days=i)).isoformat(),
            "size": f"{2 + (i % 5)}KB",
            "has_attachments": i % 4 == 0,
            "is_read": i % 3 != 0,
            "snippet": f"This is a snippet of email {i} content...",
            "labels": ["INBOX" if folder == "inbox" else folder.upper(), "CATEGORY_UPDATES" if i % 2 == 0 else "CATEGORY_PERSONAL"]
        }
        for i in range(1, limit + 1)
    ]


def read_email(
    email_id: str,
    mark_as_read: bool = True
) -> Dict[str, Any]:
    """
    Read a specific email.
    
    Args:
        email_id: ID of the email to read
        mark_as_read: Whether to mark the email as read after reading
        
    Returns:
        Dictionary containing the email content and metadata
    """
    # This would connect to the Gmail MCP server in a real implementation
    return {
        "id": email_id,
        "thread_id": f"thread_{email_id}",
        "subject": f"Subject for Email {email_id}",
        "sender": f"sender_{email_id}@example.com",
        "recipient": "me@example.com",
        "date": (datetime.now() - timedelta(hours=2)).isoformat(),
        "body": f"This is the body content of email {email_id}. It contains detailed information that the sender wanted to communicate.",
        "html_body": f"<p>This is the HTML body content of email {email_id}.</p>",
        "has_attachments": email_id.endswith("4"),
        "attachment_count": 1 if email_id.endswith("4") else 0,
        "is_read": mark_as_read,
        "labels": ["INBOX", "IMPORTANT" if email_id.endswith("1") else "CATEGORY_UPDATES"],
        "size": "3.2KB"
    }


def send_email(
    to: List[str],
    subject: str,
    body: str,
    cc: List[str] = None,
    bcc: List[str] = None,
    attachments: List[str] = None,
    html_body: str = None
) -> Dict[str, Any]:
    """
    Send an email via Gmail.
    
    Args:
        to: List of recipient email addresses
        subject: Email subject
        body: Email body content
        cc: List of CC recipients
        bcc: List of BCC recipients
        attachments: List of file paths to attach
        html_body: HTML version of the email body
        
    Returns:
        Dictionary containing the send result
    """
    # This would connect to the Gmail MCP server in a real implementation
    total_recipients = len(to) + (len(cc) if cc else 0) + (len(bcc) if bcc else 0)
    
    return {
        "status": "sent",
        "message_id": f"msg_{hash(''.join(to) + subject) % 10000}",
        "recipients_count": total_recipients,
        "message": f"Email sent successfully to {len(to)} recipients",
        "timestamp": datetime.now().isoformat()
    }


def add_label_to_email(
    email_id: str,
    label: str
) -> Dict[str, Any]:
    """
    Add a label to an email.
    
    Args:
        email_id: ID of the email to add label to
        label: Label to add (e.g., 'IMPORTANT', 'TRAVEL', 'WORK')
        
    Returns:
        Dictionary containing the labeling result
    """
    # This would connect to the Gmail MCP server in a real implementation
    return {
        "status": "success",
        "email_id": email_id,
        "label_added": label,
        "timestamp": datetime.now().isoformat(),
        "message": f"Label '{label}' added to email {email_id}"
    }


def delete_email(
    email_id: str,
    move_to_trash: bool = True
) -> Dict[str, Any]:
    """
    Delete an email.
    
    Args:
        email_id: ID of the email to delete
        move_to_trash: Whether to move to trash instead of permanent delete
        
    Returns:
        Dictionary containing the deletion result
    """
    # This would connect to the Gmail MCP server in a real implementation
    action = "moved to trash" if move_to_trash else "permanently deleted"
    
    return {
        "status": "success",
        "email_id": email_id,
        "action": action,
        "timestamp": datetime.now().isoformat(),
        "message": f"Email {email_id} {action}"
    }


def search_emails(
    query: str,
    limit: int = 10,
    date_from: str = None,
    date_to: str = None
) -> List[Dict[str, Any]]:
    """
    Search emails based on a query.
    
    Args:
        query: Search query (e.g., 'from:user@example.com subject:meeting')
        limit: Maximum number of results to return
        date_from: Start date for search (ISO format)
        date_to: End date for search (ISO format)
        
    Returns:
        List of dictionaries containing matching email information
    """
    # This would connect to the Gmail MCP server in a real implementation
    return [
        {
            "id": f"search_{i}",
            "thread_id": f"thread_search_{i}",
            "subject": f"Search Result {i} for query '{query}'",
            "sender": f"sender_{i}@example.com",
            "recipient": "me@example.com",
            "date": (datetime.now() - timedelta(days=i)).isoformat(),
            "snippet": f"Snippet containing the searched query: {query} in the email content...",
            "relevance_score": round(0.95 - (i * 0.05), 2),
            "labels": ["INBOX", "IMPORTANT" if i % 3 == 0 else "CATEGORY_UPDATES"]
        }
        for i in range(1, limit + 1)
    ]


def get_email_labels() -> List[Dict[str, Any]]:
    """
    Get list of available email labels.
    
    Returns:
        List of dictionaries containing label information
    """
    # This would connect to the Gmail MCP server in a real implementation
    return [
        {
            "id": "label_1",
            "name": "INBOX",
            "message_count": 125,
            "type": "system"
        },
        {
            "id": "label_2", 
            "name": "SENT",
            "message_count": 89,
            "type": "system"
        },
        {
            "id": "label_3",
            "name": "DRAFTS",
            "message_count": 5,
            "type": "system"
        },
        {
            "id": "label_4",
            "name": "IMPORTANT",
            "message_count": 32,
            "type": "system"
        },
        {
            "id": "label_5",
            "name": "TRAVEL",
            "message_count": 12,
            "type": "user"
        },
        {
            "id": "label_6",
            "name": "WORK",
            "message_count": 67,
            "type": "user"
        }
    ]


def create_label(
    name: str,
    color: str = None
) -> Dict[str, Any]:
    """
    Create a new email label.
    
    Args:
        name: Name of the label
        color: Color for the label (optional)
        
    Returns:
        Dictionary containing the label creation result
    """
    # This would connect to the Gmail MCP server in a real implementation
    label_id = f"new_label_{hash(name) % 10000}"
    
    return {
        "status": "created",
        "label_id": label_id,
        "label_name": name,
        "color": color or "#4285F4",
        "message": f"Label '{name}' created successfully"
    }


def move_email(
    email_id: str,
    destination: str  # folder or label
) -> Dict[str, Any]:
    """
    Move an email to a different folder or apply a different label.
    
    Args:
        email_id: ID of the email to move
        destination: Destination folder or label
        
    Returns:
        Dictionary containing the move result
    """
    # This would connect to the Gmail MCP server in a real implementation
    return {
        "status": "moved",
        "email_id": email_id,
        "destination": destination,
        "timestamp": datetime.now().isoformat(),
        "message": f"Email {email_id} moved to {destination}"
    }


def get_email_thread(
    thread_id: str
) -> List[Dict[str, Any]]:
    """
    Get all emails in a thread.
    
    Args:
        thread_id: ID of the thread to retrieve
        
    Returns:
        List of dictionaries containing emails in the thread
    """
    # This would connect to the Gmail MCP server in a real implementation
    return [
        {
            "id": f"thread_email_{i}",
            "thread_id": thread_id,
            "subject": f"Re: Thread Subject",
            "sender": f"sender_{i}@example.com",
            "recipient": "me@example.com",
            "date": (datetime.now() - timedelta(hours=i*2)).isoformat(),
            "body": f"Response #{i} in the thread...",
            "is_read": i % 2 == 0
        }
        for i in range(1, 4)  # Example: 3 emails in thread
    ]


def mark_as_read(
    email_id: str
) -> Dict[str, Any]:
    """
    Mark an email as read.
    
    Args:
        email_id: ID of the email to mark as read
        
    Returns:
        Dictionary containing the marking result
    """
    # This would connect to the Gmail MCP server in a real implementation
    return {
        "status": "marked_read",
        "email_id": email_id,
        "timestamp": datetime.now().isoformat(),
        "message": f"Email {email_id} marked as read"
    }


# Create a Gmail agent
agent = Agent(
    system_prompt="You are a Gmail assistant. You can list, read, send, search, and manage emails in Gmail. You can also add labels, delete emails, create new labels, move emails between folders, and manage email threads. When asked about email operations, provide detailed information about email content, metadata, and available actions."
)


def setup_gmail_agent():
    """Set up the Gmail agent with tools."""
    try:
        agent.add_tool(list_emails)
        agent.add_tool(read_email)
        agent.add_tool(send_email)
        agent.add_tool(add_label_to_email)
        agent.add_tool(delete_email)
        agent.add_tool(search_emails)
        agent.add_tool(get_email_labels)
        agent.add_tool(create_label)
        agent.add_tool(move_email)
        agent.add_tool(get_email_thread)
        agent.add_tool(mark_as_read)
        print("Gmail tools successfully registered with the agent.")
        return True
    except AttributeError as e:
        print(f"Note: Tool registration API may vary depending on the specific Strands implementation. Error: {e}")
        return False


def run_gmail_agent(user_input: str):
    """
    Run the Gmail agent with the given user input.
    
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
        return f"Simulated response: Gmail agent. You requested: '{user_input}'"
    except Exception as e:
        return f"Error processing your request: {str(e)}"


def main():
    """Main function to run the Gmail agent."""
    # Set up tools
    tools_setup = setup_gmail_agent()
    
    print("Gmail Agent")
    print("This agent can:")
    print("- List emails (e.g., 'show my last 5 emails')")
    print("- Read specific emails (e.g., 'read email 123')")
    print("- Send emails (e.g., 'send email to user@example.com')")
    print("- Add labels to emails (e.g., 'add IMPORTANT label to email 123')")
    print("- Delete emails (e.g., 'delete email 123')")
    print("- Search emails (e.g., 'search for meeting')")
    print("- Get email labels (e.g., 'show all labels')")
    print("- Create new labels (e.g., 'create TRAVEL label')")
    print("- Move emails (e.g., 'move email 123 to TRAVEL')")
    print("- Get email threads (e.g., 'show thread for email 123')")
    print("- Mark emails as read (e.g., 'mark email 123 as read')")
    print("Type 'quit' to exit.\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Agent: Goodbye! Gmail assistant signing off.")
            break
            
        response = run_gmail_agent(user_input)
        print(f"Agent: {response}\n")


if __name__ == "__main__":
    main()