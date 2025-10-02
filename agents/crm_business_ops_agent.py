"""
CRM & Business Operations Agent using Strands Agents SDK

This agent combines Twenty CRM, Go High Level, Customer Feedback, Invoice, 
Proposal Generator, Interview Scheduler, and Mailchimp MCPs to provide 
comprehensive CRM and business operations capabilities.
"""

from strandsagents import Agent
from typing import Dict, Any, List
import json
from datetime import datetime, timedelta


def list_contacts(
    limit: int = 20, 
    offset: int = 0,
    search_query: str = None
) -> List[Dict[str, Any]]:
    """
    List contacts from the CRM system.
    
    Args:
        limit: Maximum number of contacts to return
        offset: Offset for pagination
        search_query: Optional search query to filter contacts
        
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
            "job_title": f"Position {i}",
            "status": "active" if i % 3 != 0 else "inactive",
            "last_interaction": (datetime.now() - timedelta(days=i*2)).isoformat(),
            "created_date": (datetime.now() - timedelta(days=i*10)).isoformat(),
            "tags": ["customer", "lead"] if i % 2 == 0 else ["prospect", "vip"]
        }
        for i in range(1 + offset, limit + 1 + offset)
    ]


def create_lead(
    first_name: str,
    last_name: str,
    phone: str,
    email: str,
    company: str = "",
    campaign_source: str = "",
    notes: str = ""
) -> Dict[str, Any]:
    """
    Create a new lead in the CRM system.
    
    Args:
        first_name: Lead's first name
        last_name: Lead's last name
        phone: Lead's phone number
        email: Lead's email address
        company: Lead's company
        campaign_source: Source of the lead
        notes: Additional notes about the lead
        
    Returns:
        Dictionary containing the lead creation result
    """
    # This would connect to the Go High Level MCP server in a real implementation
    lead_id = f"lead_{hash(first_name + last_name + phone) % 10000}"
    
    return {
        "status": "created",
        "lead_id": lead_id,
        "name": f"{first_name} {last_name}",
        "phone": phone,
        "email": email,
        "timestamp": datetime.now().isoformat(),
        "message": f"Lead {first_name} {last_name} created successfully"
    }


def collect_feedback(
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
    feedback_id = f"feedback_{customer_id}_{datetime.now().strftime('%Y%m%d')}"
    
    return {
        "status": "submitted",
        "feedback_id": feedback_id,
        "customer_id": customer_id,
        "rating": rating,
        "category": category,
        "timestamp": datetime.now().isoformat(),
        "message": f"Feedback from customer {customer_id} submitted"
    }


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
    invoice_id = f"INV-{datetime.now().strftime('%Y%m%d')}-{len(items)}"
    
    return {
        "status": "created",
        "invoice_id": invoice_id,
        "client_name": client_name,
        "total_amount": total,
        "due_date": due_date or (datetime.now() + timedelta(days=30)).isoformat(),
        "item_count": len(items),
        "message": f"Invoice {invoice_id} created for {client_name}"
    }


def generate_proposal(
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
    proposal_id = f"PROPOSAL-{client_name[:3].upper()}-{datetime.now().strftime('%Y%m')}"
    
    return {
        "status": "generated",
        "proposal_id": proposal_id,
        "client_name": client_name,
        "project_title": project_title,
        "budget": budget,
        "timeline": timeline,
        "deliverable_count": len(deliverables),
        "message": f"Proposal for {client_name} generated successfully"
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
    interview_id = f"interview_{candidate_name.replace(' ', '_')}_{interview_date.replace('-', '').replace(':', '')}"
    
    return {
        "status": "scheduled",
        "interview_id": interview_id,
        "candidate_name": candidate_name,
        "candidate_email": candidate_email,
        "interviewers": interviewer_names,
        "interview_date": interview_date,
        "duration_minutes": duration_minutes,
        "location": location,
        "message": f"Interview scheduled for {candidate_name}"
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
    campaign_id = f"camp_{audience_segment}_{datetime.now().strftime('%Y%m%d')}"
    
    return {
        "status": "queued",
        "campaign_id": campaign_id,
        "audience_segment": audience_segment,
        "subject": subject,
        "estimated_recipients": 1500,
        "scheduled_time": send_time or datetime.now().isoformat(),
        "message": f"Campaign email queued for {audience_segment} segment"
    }


def get_customer_analytics(
    customer_id: str = None,
    date_from: str = None,
    date_to: str = None
) -> Dict[str, Any]:
    """
    Get customer analytics and engagement metrics.
    
    Args:
        customer_id: Optional specific customer to analyze
        date_from: Start date for analytics
        date_to: End date for analytics
        
    Returns:
        Dictionary containing customer analytics
    """
    # This would combine data from CRM, feedback, and invoice systems
    return {
        "date_range": {
            "start": date_from or (datetime.now() - timedelta(days=90)).isoformat(),
            "end": date_to or datetime.now().isoformat()
        },
        "analytics": {
            "total_customers": 420 if not customer_id else 1,
            "new_customers": 25,
            "churn_rate": 0.023,  # 2.3%
            "avg_customer_value": 2450.00,
            "revenue": 1_050_000.00,
            "engagement_score": 0.78 if not customer_id else 0.85,
            "feedback_score": 4.2 if not customer_id else 4.5,  # out of 5
            "repeat_purchase_rate": 0.65,  # 65%
            "most_popular_segment": "enterprise" if not customer_id else "small_business",
            "top_feedback_categories": [
                {"category": "product_quality", "score": 4.3},
                {"category": "customer_service", "score": 4.1},
                {"category": "pricing", "score": 3.8}
            ]
        },
        "customer_specific": {
            "id": customer_id,
            "name": "Example Customer",
            "total_purchases": 12,
            "last_purchase_date": (datetime.now() - timedelta(days=15)).isoformat(),
            "preferred_contact": "email",
            "lifetime_value": 29400.00
        } if customer_id else None,
        "message": f"Analytics retrieved for {'specific customer' if customer_id else 'all customers'}"
    }


def update_contact(
    contact_id: str,
    updates: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Update contact information in CRM.
    
    Args:
        contact_id: ID of the contact to update
        updates: Dictionary containing fields to update
        
    Returns:
        Dictionary containing the update result
    """
    # This would connect to the Twenty CRM MCP server in a real implementation
    return {
        "status": "updated",
        "contact_id": contact_id,
        "updated_fields": list(updates.keys()),
        "timestamp": datetime.now().isoformat(),
        "message": f"Contact {contact_id} updated with {len(updates)} changes"
    }


def create_contact_task(
    contact_id: str,
    task_title: str,
    due_date: str,
    assigned_to: str,
    priority: str = "medium",  # low, medium, high
    description: str = ""
) -> Dict[str, Any]:
    """
    Create a task for a contact in CRM.
    
    Args:
        contact_id: ID of the contact the task is for
        task_title: Title of the task
        due_date: Due date for the task
        assigned_to: User assigned to the task
        priority: Priority level of the task
        description: Description of the task
        
    Returns:
        Dictionary containing the task creation result
    """
    # This would connect to the Twenty CRM MCP server in a real implementation
    task_id = f"task_{hash(task_title + contact_id) % 10000}"
    
    return {
        "status": "created",
        "task_id": task_id,
        "contact_id": contact_id,
        "title": task_title,
        "due_date": due_date,
        "assigned_to": assigned_to,
        "priority": priority,
        "message": f"Task '{task_title}' created for contact {contact_id}"
    }


def get_pipeline_performance(pipeline_id: str) -> Dict[str, Any]:
    """
    Get performance metrics for a sales pipeline.
    
    Args:
        pipeline_id: ID of the pipeline to analyze
        
    Returns:
        Dictionary containing pipeline performance metrics
    """
    # This would connect to the Go High Level MCP server in a real implementation
    return {
        "pipeline_id": pipeline_id,
        "name": "Sales Process",
        "total_leads": 85,
        "stage_performance": [
            {
                "stage_name": "Initial Contact",
                "leads_in_stage": 85,
                "conversion_rate_to_next": 0.65,
                "avg_time_in_stage_days": 2.1
            },
            {
                "stage_name": "Needs Analysis",
                "leads_in_stage": 55,
                "conversion_rate_to_next": 0.45,
                "avg_time_in_stage_days": 4.3
            },
            {
                "stage_name": "Proposal",
                "leads_in_stage": 25,
                "conversion_rate_to_next": 0.52,
                "avg_time_in_stage_days": 7.2
            },
            {
                "stage_name": "Negotiation",
                "leads_in_stage": 13,
                "conversion_rate_to_next": 0.69,
                "avg_time_in_stage_days": 5.8
            },
            {
                "stage_name": "Closed Won",
                "leads_in_stage": 9,
                "conversion_rate_to_next": 0,  # Final stage
                "avg_time_in_stage_days": 1.0
            }
        ],
        "overall_conversion_rate": 0.106,  # 10.6%
        "avg_sales_cycle_days": 19.4,
        "pipeline_value": 125000.00,
        "message": f"Performance metrics retrieved for pipeline {pipeline_id}"
    }


def send_followup_email(
    customer_id: str,
    template_name: str,
    personalization_vars: Dict[str, str] = None
) -> Dict[str, Any]:
    """
    Send a personalized follow-up email to a customer.
    
    Args:
        customer_id: ID of the customer to send to
        template_name: Name of the email template to use
        personalization_vars: Variables to personalize the email
        
    Returns:
        Dictionary containing the email sending result
    """
    # This would connect to the Mailchimp MCP server in a real implementation
    email_id = f"followup_{customer_id}_{hash(template_name) % 10000}"
    
    return {
        "status": "sent",
        "email_id": email_id,
        "customer_id": customer_id,
        "template_used": template_name,
        "personalized_variables": list(personalization_vars.keys()) if personalization_vars else [],
        "message": f"Follow-up email sent to customer {customer_id} using template '{template_name}'"
    }


# Create a CRM & Business Operations agent
agent = Agent(
    system_prompt="You are a CRM & Business Operations assistant. You can manage contacts, create leads, collect customer feedback, generate invoices and proposals, schedule interviews, send marketing campaigns, and analyze customer data. When asked about business operations, provide detailed information about customer relationships, sales processes, and operational metrics."
)


def setup_crm_ops_agent():
    """Set up the CRM & Business Operations agent with tools."""
    try:
        agent.add_tool(list_contacts)
        agent.add_tool(create_lead)
        agent.add_tool(collect_feedback)
        agent.add_tool(create_invoice)
        agent.add_tool(generate_proposal)
        agent.add_tool(schedule_interview)
        agent.add_tool(send_campaign_email)
        agent.add_tool(get_customer_analytics)
        agent.add_tool(update_contact)
        agent.add_tool(create_contact_task)
        agent.add_tool(get_pipeline_performance)
        agent.add_tool(send_followup_email)
        print("CRM & Business Operations tools successfully registered with the agent.")
        return True
    except AttributeError as e:
        print(f"Note: Tool registration API may vary depending on the specific Strands implementation. Error: {e}")
        return False


def run_crm_ops_agent(user_input: str):
    """
    Run the CRM & Business Operations agent with the given user input.
    
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
        return f"Simulated response: CRM & Business Operations agent. You requested: '{user_input}'"
    except Exception as e:
        return f"Error processing your request: {str(e)}"


def main():
    """Main function to run the CRM & Business Operations agent."""
    # Set up tools
    tools_setup = setup_crm_ops_agent()
    
    print("CRM & Business Operations Agent")
    print("This agent can:")
    print("- List contacts (e.g., 'show first 10 contacts')")
    print("- Create leads (e.g., 'create lead John Doe')")
    print("- Collect customer feedback (e.g., 'collect feedback from customer 123')")
    print("- Create invoices (e.g., 'create invoice for Acme Corp')")
    print("- Generate proposals (e.g., 'create proposal for new project')")
    print("- Schedule interviews (e.g., 'schedule interview for tomorrow')")
    print("- Send campaign emails (e.g., 'send newsletter campaign')")
    print("- Get customer analytics (e.g., 'show customer analytics')")
    print("- Update contact info (e.g., 'update contact 123')")
    print("- Create contact tasks (e.g., 'create follow-up task')")
    print("- Get pipeline performance (e.g., 'show pipeline performance')")
    print("- Send follow-up emails (e.g., 'send follow-up to customer 123')")
    print("Type 'quit' to exit.\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Agent: Goodbye! CRM & Business Operations assistant signing off.")
            break
            
        response = run_crm_ops_agent(user_input)
        print(f"Agent: {response}\n")


if __name__ == "__main__":
    main()