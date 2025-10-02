"""
Business Operations Agent using Strands Agents SDK

This agent uses multiple MCPs to handle business operations, including customer feedback,
CRM management, invoice generation, and proposal creation.
"""

from strandsagents import Agent
from typing import Dict, Any, List
import json
from datetime import datetime, timedelta


def collect_customer_feedback(
    customer_id: str,
    rating: int,
    comment: str,
    category: str = "general"
) -> Dict[str, Any]:
    """
    Collect customer feedback.
    
    Args:
        customer_id: Unique identifier for the customer
        rating: Rating from 1-5
        comment: Customer's comment
        category: Category of feedback (e.g., product, service, billing)
        
    Returns:
        Dictionary containing the feedback submission result
    """
    # This would connect to the Customer Feedback MCP server in a real implementation
    return {
        "status": "success",
        "feedback_id": f"feedback_{customer_id}_{datetime.now().strftime('%Y%m%d')}",
        "customer_id": customer_id,
        "rating": rating,
        "category": category,
        "timestamp": datetime.now().isoformat()
    }


def list_crm_contacts(
    limit: int = 20, 
    offset: int = 0,
    search_query: str = None
) -> List[Dict[str, Any]]:
    """
    List contacts from CRM system.
    
    Args:
        limit: Maximum number of contacts to return
        offset: Offset for pagination
        search_query: Optional search query
        
    Returns:
        List of dictionaries containing contact information
    """
    # This would connect to the Twenty CRM MCP server in a real implementation
    return [
        {
            "id": f"contact_{i}",
            "first_name": f"Contact {i}",
            "last_name": f"Lastname {i}",
            "email": f"contact{i}@company.com",
            "phone": f"+1-555-000-{str(i).zfill(4)}",
            "company": f"Company {i}",
            "last_interaction": (datetime.now() - timedelta(days=i*2)).isoformat(),
            "status": "active" if i % 3 != 0 else "inactive"
        }
        for i in range(1 + offset, limit + 1 + offset)
    ]


def create_invoice(
    client_name: str,
    client_email: str,
    client_address: str,
    items: List[Dict[str, Any]],
    due_date: str = None,
    invoice_number: str = None,
    notes: str = ""
) -> Dict[str, Any]:
    """
    Create an invoice for a client.
    
    Args:
        client_name: Name of the client
        client_email: Email of the client
        client_address: Address of the client
        items: List of items/services with name, quantity, price
        due_date: Due date for the invoice
        invoice_number: Optional invoice number
        notes: Optional notes for the invoice
        
    Returns:
        Dictionary containing the created invoice information
    """
    # This would connect to the Invoice MCP server in a real implementation
    total = sum(item['quantity'] * item['price'] for item in items)
    return {
        "status": "created",
        "invoice_id": f"INV-{datetime.now().strftime('%Y%m%d')}-{len(items)}",
        "client_name": client_name,
        "total_amount": total,
        "due_date": due_date or (datetime.now() + timedelta(days=30)).isoformat(),
        "item_count": len(items)
    }


def generate_business_proposal(
    client_name: str,
    project_title: str,
    project_description: str,
    timeline: str,
    budget: float,
    deliverables: List[str],
    special_terms: str = ""
) -> Dict[str, Any]:
    """
    Generate a business proposal.
    
    Args:
        client_name: Name of the client
        project_title: Title of the project
        project_description: Detailed description of the project
        timeline: Expected project timeline
        budget: Project budget
        deliverables: List of project deliverables
        special_terms: Any special terms or conditions
        
    Returns:
        Dictionary containing the generated proposal information
    """
    # This would connect to the Proposal Generator MCP server in a real implementation
    return {
        "status": "generated",
        "proposal_id": f"PROPOSAL-{client_name[:3].upper()}-{datetime.now().strftime('%Y%m')}",
        "client_name": client_name,
        "project_title": project_title,
        "budget": budget,
        "timeline": timeline,
        "deliverable_count": len(deliverables)
    }


def schedule_interview(
    candidate_name: str,
    candidate_email: str,
    interviewer_names: List[str],
    interview_date: str,
    duration_minutes: int = 60,
    location: str = "virtual",
    notes: str = ""
) -> Dict[str, Any]:
    """
    Schedule an interview.
    
    Args:
        candidate_name: Name of the candidate
        candidate_email: Email of the candidate
        interviewer_names: List of names of interviewers
        interview_date: Date and time of the interview
        duration_minutes: Duration of the interview in minutes
        location: Location of the interview (virtual/in-person)
        notes: Any additional notes
        
    Returns:
        Dictionary containing the interview scheduling result
    """
    # This would connect to the Interview Scheduler MCP server in a real implementation
    return {
        "status": "scheduled",
        "interview_id": f"interview_{candidate_name.replace(' ', '_')}_{interview_date.replace('-', '').replace(':', '')}",
        "candidate_name": candidate_name,
        "candidate_email": candidate_email,
        "interviewers": interviewer_names,
        "interview_date": interview_date,
        "duration_minutes": duration_minutes,
        "location": location
    }


def send_campaign_email(
    audience_segment: str,
    subject: str,
    content: str,
    send_time: str = None
) -> Dict[str, Any]:
    """
    Send a marketing campaign email.
    
    Args:
        audience_segment: Target segment for the campaign
        subject: Subject of the email
        content: Content of the email
        send_time: Optional send time (now if not specified)
        
    Returns:
        Dictionary containing the campaign email result
    """
    # This would connect to the Mailchimp MCP server in a real implementation
    return {
        "status": "queued",
        "campaign_id": f"camp_{audience_segment}_{datetime.now().strftime('%Y%m%d')}",
        "audience_segment": audience_segment,
        "subject": subject,
        "estimated_recipients": 1500,
        "scheduled_time": send_time or datetime.now().isoformat()
    }


# Create a business operations agent
agent = Agent(
    system_prompt="You are a business operations assistant. You can collect customer feedback, manage CRM contacts, create invoices, generate business proposals, schedule interviews, and send marketing campaign emails. Always be professional and provide accurate business information. When creating invoices or proposals, ensure all required information is provided."
)


def setup_business_ops_agent():
    """Set up the business operations agent with tools."""
    try:
        agent.add_tool(collect_customer_feedback)
        agent.add_tool(list_crm_contacts)
        agent.add_tool(create_invoice)
        agent.add_tool(generate_business_proposal)
        agent.add_tool(schedule_interview)
        agent.add_tool(send_campaign_email)
        print("Business operations tools successfully registered with the agent.")
        return True
    except AttributeError as e:
        print(f"Note: Tool registration API may vary depending on the specific Strands implementation. Error: {e}")
        return False


def run_business_agent(user_input: str):
    """
    Run the business operations agent with the given user input.
    
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
        return f"Simulated response: Business operations agent. You requested: '{user_input}'"
    except Exception as e:
        return f"Error processing your request: {str(e)}"


def main():
    """Main function to run the business operations agent."""
    # Set up tools
    tools_setup = setup_business_ops_agent()
    
    print("Business Operations Agent")
    print("This agent can:")
    print("- Collect customer feedback (e.g., 'collect feedback from customer 123 with rating 4')")
    print("- Manage CRM contacts (e.g., 'list first 10 contacts')")
    print("- Create invoices (e.g., 'create an invoice for Acme Corp')")
    print("- Generate business proposals (e.g., 'create a proposal for new project')")
    print("- Schedule interviews (e.g., 'schedule an interview for tomorrow')")
    print("- Send marketing emails (e.g., 'send campaign to newsletter subscribers')")
    print("Type 'quit' to exit.\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Agent: Goodbye! Business operations assistant signing off.")
            break
            
        response = run_business_agent(user_input)
        print(f"Agent: {response}\n")


if __name__ == "__main__":
    main()