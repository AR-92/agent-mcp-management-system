"""
Go High Level CRM Agent using Strands Agents SDK

This agent uses the Go High Level MCP to manage marketing automation and CRM operations.
"""

from strandsagents import Agent
from typing import Dict, Any, List
import json
from datetime import datetime


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
    Create a new lead in Go High Level.
    
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


def update_lead(
    lead_id: str,
    status: str = None,
    contact_date: str = None,
    notes: str = None
) -> Dict[str, Any]:
    """
    Update an existing lead in Go High Level.
    
    Args:
        lead_id: ID of the lead to update
        status: New status for the lead
        contact_date: Date of last contact
        notes: Additional notes
        
    Returns:
        Dictionary containing the lead update result
    """
    # This would connect to the Go High Level MCP server in a real implementation
    return {
        "status": "updated",
        "lead_id": lead_id,
        "updated_fields": [f for f in [status, contact_date, notes] if f is not None],
        "timestamp": datetime.now().isoformat(),
        "message": f"Lead {lead_id} updated successfully"
    }


def list_leads(
    status: str = "all",
    limit: int = 20,
    offset: int = 0,
    search_query: str = None
) -> List[Dict[str, Any]]:
    """
    List leads in Go High Level.
    
    Args:
        status: Filter by status ('all', 'new', 'contacted', 'qualified', 'closed')
        limit: Maximum number of leads to return
        offset: Offset for pagination
        search_query: Optional search query
        
    Returns:
        List of dictionaries containing lead information
    """
    # This would connect to the Go High Level MCP server in a real implementation
    sample_leads = [
        {
            "id": f"lead_{i}",
            "first_name": f"Lead {i}",
            "last_name": f"Lastname {i}",
            "phone": f"+1-555-0{i:03d}-{i:04d}",
            "email": f"lead{i}@example.com",
            "company": f"Company {i}",
            "status": "qualified" if i % 4 == 0 else "new" if i % 4 == 1 else "contacted",
            "source": "website" if i % 3 == 0 else "referral" if i % 3 == 1 else "advertising",
            "date_created": (datetime.now() - timedelta(days=i)).isoformat(),
            "last_contacted": (datetime.now() - timedelta(days=i//2)).isoformat() if i > 2 else None
        }
        for i in range(1 + offset, limit + 1 + offset)
    ]
    
    if status != "all":
        sample_leads = [lead for lead in sample_leads if lead["status"] == status]
        
    return sample_leads


def create_campaign(
    name: str,
    description: str,
    start_date: str,
    end_date: str,
    target_audience: str,
    budget: float
) -> Dict[str, Any]:
    """
    Create a new marketing campaign in Go High Level.
    
    Args:
        name: Campaign name
        description: Campaign description
        start_date: Campaign start date
        end_date: Campaign end date
        target_audience: Description of target audience
        budget: Campaign budget
        
    Returns:
        Dictionary containing the campaign creation result
    """
    # This would connect to the Go High Level MCP server in a real implementation
    campaign_id = f"camp_{hash(name) % 10000}"
    
    return {
        "status": "created",
        "campaign_id": campaign_id,
        "name": name,
        "budget": budget,
        "start_date": start_date,
        "end_date": end_date,
        "message": f"Marketing campaign '{name}' created successfully"
    }


def get_campaign_analytics(campaign_id: str) -> Dict[str, Any]:
    """
    Get analytics for a specific marketing campaign.
    
    Args:
        campaign_id: ID of the campaign to analyze
        
    Returns:
        Dictionary containing campaign analytics
    """
    # This would connect to the Go High Level MCP server in a real implementation
    return {
        "campaign_id": campaign_id,
        "impressions": 12500,
        "clicks": 420,
        "conversions": 32,
        "conversion_rate": 0.076,  # 7.6%
        "cost_per_click": 1.25,
        "cost_per_conversion": 16.41,
        "roi": 3.2,  # 320%
        "engagement_rate": 0.034,  # 3.4%
        "date_range": {
            "start": "2023-09-01T00:00:00Z",
            "end": "2023-09-30T23:59:59Z"
        }
    }


def create_appointment(
    lead_id: str,
    appointment_datetime: str,
    duration_minutes: int,
    purpose: str,
    location: str = "virtual",
    notes: str = ""
) -> Dict[str, Any]:
    """
    Create an appointment for a lead in Go High Level.
    
    Args:
        lead_id: ID of the lead to schedule appointment for
        appointment_datetime: Date and time of the appointment
        duration_minutes: Duration of the appointment in minutes
        purpose: Purpose of the appointment
        location: Location of the appointment (virtual/in-person)
        notes: Additional notes
        
    Returns:
        Dictionary containing the appointment creation result
    """
    # This would connect to the Go High Level MCP server in a real implementation
    appointment_id = f"apt_{lead_id}_{appointment_datetime.replace('-', '').replace(':', '')}"
    
    return {
        "status": "scheduled",
        "appointment_id": appointment_id,
        "lead_id": lead_id,
        "datetime": appointment_datetime,
        "duration_minutes": duration_minutes,
        "purpose": purpose,
        "location": location,
        "message": f"Appointment scheduled for lead {lead_id}"
    }


def send_sms_message(
    to_numbers: List[str],
    message: str,
    from_number: str = None,
    scheduled_time: str = None
) -> Dict[str, Any]:
    """
    Send an SMS message via Go High Level.
    
    Args:
        to_numbers: List of phone numbers to send to
        message: Content of the message
        from_number: Sender's phone number (optional)
        scheduled_time: Time to schedule the message (optional)
        
    Returns:
        Dictionary containing the SMS sending result
    """
    # This would connect to the Go High Level MCP server in a real implementation
    return {
        "status": "sent" if not scheduled_time else "scheduled",
        "message_id": f"sms_{hash(message) % 10000}",
        "recipients_count": len(to_numbers),
        "message_length": len(message),
        "scheduled_time": scheduled_time,
        "message": f"SMS sent to {len(to_numbers)} recipients"
    }


def get_lead_conversion_report(
    start_date: str,
    end_date: str,
    metrics: List[str] = None
) -> Dict[str, Any]:
    """
    Get a lead conversion report for a date range.
    
    Args:
        start_date: Start date for the report
        end_date: End date for the report
        metrics: List of metrics to include in the report
        
    Returns:
        Dictionary containing the lead conversion report
    """
    # This would connect to the Go High Level MCP server in a real implementation
    default_metrics = ["leads_created", "leads_contacted", "appointments_scheduled", "deals_closed", "conversion_rate"]
    selected_metrics = metrics if metrics else default_metrics
    
    return {
        "date_range": {"start": start_date, "end": end_date},
        "metrics": {
            "leads_created": 125,
            "leads_contacted": 98,
            "appointments_scheduled": 42,
            "deals_closed": 18,
            "conversion_rate": 0.144,  # 14.4%
            "avg_response_time_hours": 4.2,
            "top_sources": [
                {"source": "website", "count": 52},
                {"source": "referral", "count": 38},
                {"source": "advertising", "count": 35}
            ]
        }
    }


def create_pipeline_stage(
    pipeline_name: str,
    stage_name: str,
    stage_order: int,
    success_probability: float = 0.5
) -> Dict[str, Any]:
    """
    Create a new stage in a sales pipeline.
    
    Args:
        pipeline_name: Name of the pipeline
        stage_name: Name of the stage
        stage_order: Order position of the stage in the pipeline
        success_probability: Probability of advancing to the next stage (0-1)
        
    Returns:
        Dictionary containing the pipeline stage creation result
    """
    # This would connect to the Go High Level MCP server in a real implementation
    stage_id = f"stage_{hash(pipeline_name + stage_name) % 10000}"
    
    return {
        "status": "created",
        "stage_id": stage_id,
        "pipeline_name": pipeline_name,
        "stage_name": stage_name,
        "stage_order": stage_order,
        "success_probability": success_probability,
        "message": f"Stage '{stage_name}' created in pipeline '{pipeline_name}'"
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
        "pipeline_value": 125000.00
    }


# Create a Go High Level CRM agent
agent = Agent(
    system_prompt="You are a Go High Level CRM assistant. You can create and manage leads, run marketing campaigns, schedule appointments, send SMS messages, and generate reports. When asked about CRM operations, provide detailed information about lead management, conversion tracking, and pipeline performance. Follow best practices for marketing automation and customer relationship management."
)


def setup_ghl_agent():
    """Set up the Go High Level CRM agent with tools."""
    try:
        agent.add_tool(create_lead)
        agent.add_tool(update_lead)
        agent.add_tool(list_leads)
        agent.add_tool(create_campaign)
        agent.add_tool(get_campaign_analytics)
        agent.add_tool(create_appointment)
        agent.add_tool(send_sms_message)
        agent.add_tool(get_lead_conversion_report)
        agent.add_tool(create_pipeline_stage)
        agent.add_tool(get_pipeline_performance)
        print("Go High Level CRM tools successfully registered with the agent.")
        return True
    except AttributeError as e:
        print(f"Note: Tool registration API may vary depending on the specific Strands implementation. Error: {e}")
        return False


def run_ghl_agent(user_input: str):
    """
    Run the Go High Level CRM agent with the given user input.
    
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
        return f"Simulated response: Go High Level CRM agent. You requested: '{user_input}'"
    except Exception as e:
        return f"Error processing your request: {str(e)}"


def main():
    """Main function to run the Go High Level CRM agent."""
    # Set up tools
    tools_setup = setup_ghl_agent()
    
    print("Go High Level CRM Agent")
    print("This agent can:")
    print("- Create leads (e.g., 'create a new lead named John Doe')")
    print("- Update leads (e.g., 'update lead status to qualified')")
    print("- List leads (e.g., 'show all new leads')")
    print("- Create marketing campaigns (e.g., 'create a summer promotion campaign')")
    print("- Get campaign analytics (e.g., 'show analytics for campaign 123')")
    print("- Schedule appointments (e.g., 'schedule an appointment for lead 456')")
    print("- Send SMS messages (e.g., 'send SMS to 555-0123')")
    print("- Generate conversion reports (e.g., 'show lead conversion report')")
    print("- Manage sales pipelines (e.g., 'create a new pipeline stage')")
    print("Type 'quit' to exit.\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Agent: Goodbye! Go High Level CRM assistant signing off.")
            break
            
        response = run_ghl_agent(user_input)
        print(f"Agent: {response}\n")


if __name__ == "__main__":
    main()