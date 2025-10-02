#!/usr/bin/env python3
"""
Go High Level MCP Server

Provides access to Go High Level marketing automation platform functionality for LLMs through MCP protocol.
"""

from fastmcp import FastMCP
from typing import List, Dict, Any
import asyncio
from datetime import datetime


# Initialize the MCP server
mcp = FastMCP(
    name="Go High Level MCP Server",
    instructions="Provides access to Go High Level marketing automation platform functionality including lead management, campaigns, and CRM operations",
    version="1.0.0"
)


# Tools
@mcp.tool
def create_lead(
    first_name: str,
    last_name: str,
    phone: str,
    email: str,
    location_id: str,
    custom_fields: Dict[str, str] = None
) -> Dict[str, str]:
    """
    Create a new lead in Go High Level
    """
    lead_id = f"ghl_lead_{hash(first_name + last_name + phone) % 10000}"
    
    return {
        "status": "created",
        "lead_id": lead_id,
        "message": f"Lead {first_name} {last_name} created successfully",
        "contact_info": f"{email}, {phone}"
    }


@mcp.tool
def get_lead(lead_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific lead
    """
    # In a real implementation, this would fetch from GHL API
    return {
        "id": lead_id,
        "first_name": "John",
        "last_name": "Doe",
        "phone": "(555) 123-4567",
        "email": "john.doe@example.com",
        "location_id": "loc_12345",
        "status": "new",
        "source": "web-form",
        "created_at": "2023-01-15T10:30:00Z",
        "custom_fields": {
            "service_of_interest": "marketing",
            "budget": "5000-10000",
            "timeline": "1-3 months"
        },
        "tags": ["prospect", "high-value"]
    }


@mcp.tool
def update_lead(
    lead_id: str,
    status: str = None,
    tags: List[str] = None,
    custom_fields: Dict[str, str] = None
) -> Dict[str, str]:
    """
    Update lead information in Go High Level
    """
    changes = []
    if status:
        changes.append(f"status: {status}")
    if tags:
        changes.append(f"tags: {', '.join(tags)}")
    if custom_fields:
        changes.append(f"custom fields: {len(custom_fields)} updates")
    
    return {
        "status": "updated",
        "lead_id": lead_id,
        "message": f"Lead {lead_id} updated: {', '.join(changes) if changes else 'no changes'}"
    }


@mcp.tool
def list_leads(
    location_id: str = None,
    status: str = None,
    tags: List[str] = None,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    List leads in Go High Level with optional filters
    """
    # In a real implementation, this would fetch from GHL API
    leads = []
    for i in range(limit):
        leads.append({
            "id": f"lead_{i:04d}",
            "first_name": f"LeadFirstName{i}",
            "last_name": f"LeadLastName{i}",
            "phone": f"(555) 123-45{i:02d}",
            "email": f"lead{i}@example.com",
            "status": "new" if i % 3 == 0 else "contacted" if i % 3 == 1 else "qualified",
            "location_id": location_id or f"loc_{i}",
            "source": "web-form",
            "created_at": (datetime.now().replace(day=1) - timedelta(days=i)).isoformat()
        })
    
    return leads


@mcp.tool
def create_appointment(
    lead_id: str,
    title: str,
    start_time: str,
    end_time: str,
    assignee_id: str,
    location_id: str = None
) -> Dict[str, str]:
    """
    Create an appointment for a lead in Go High Level
    """
    appointment_id = f"ghl_appt_{hash(lead_id + start_time) % 10000}"
    
    return {
        "status": "created",
        "appointment_id": appointment_id,
        "message": f"Appointment '{title}' created for lead {lead_id}",
        "scheduled_time": f"{start_time} to {end_time}"
    }


@mcp.tool
def send_sms(
    contact_id: str,
    message: str,
    location_id: str = None
) -> Dict[str, str]:
    """
    Send an SMS message to a contact through Go High Level
    """
    return {
        "status": "sent",
        "message_id": f"sms_{hash(contact_id + message) % 10000}",
        "contact_id": contact_id,
        "message": "SMS sent successfully"
    }


@mcp.tool
def send_email(
    contact_id: str,
    subject: str,
    body: str,
    location_id: str = None
) -> Dict[str, str]:
    """
    Send an email to a contact through Go High Level
    """
    return {
        "status": "sent",
        "message_id": f"email_{hash(contact_id + subject) % 10000}",
        "contact_id": contact_id,
        "message": "Email sent successfully"
    }


@mcp.tool
def create_pipeline_deal(
    lead_id: str,
    title: str,
    value: float,
    pipeline_id: str,
    stage_id: str,
    assignee_id: str
) -> Dict[str, str]:
    """
    Create a pipeline deal in Go High Level
    """
    deal_id = f"ghl_deal_{hash(lead_id + title) % 10000}"
    
    return {
        "status": "created",
        "deal_id": deal_id,
        "message": f"Deal '{title}' created for lead {lead_id}",
        "value": f"${value:,.2f}"
    }


@mcp.tool
def get_pipeline_deals(
    pipeline_id: str,
    stage_id: str = None,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Get deals in a specific pipeline
    """
    # In a real implementation, this would fetch from GHL API
    deals = []
    for i in range(limit):
        deals.append({
            "id": f"deal_{i:04d}",
            "title": f"Deal Title {i}",
            "value": 2500.0 + (i * 500.0),
            "stage": "proposal" if i % 3 == 0 else "negotiation" if i % 3 == 1 else "won",
            "pipeline_id": pipeline_id,
            "lead_id": f"lead_{i:04d}",
            "assigned_to": f"user_{i}",
            "created_at": (datetime.now() - timedelta(days=i)).isoformat()
        })
    
    return deals


@mcp.tool
def trigger_automation(
    automation_id: str,
    contact_id: str,
    custom_data: Dict[str, str] = None
) -> Dict[str, str]:
    """
    Trigger an automation in Go High Level
    """
    return {
        "status": "triggered",
        "automation_id": automation_id,
        "contact_id": contact_id,
        "message": f"Automation {automation_id} triggered for contact {contact_id}"
    }


# Resources
@mcp.resource("http://go-high-level-mcp-server.local/pipeline-stages")
def get_pipeline_stages(pipeline_id: str) -> List[Dict[str, str]]:
    """
    Get stages for a specific pipeline
    """
    return [
        {"id": "new", "name": "New Lead", "order": 1, "probability": 0.1},
        {"id": "contacted", "name": "Contacted", "order": 2, "probability": 0.3},
        {"id": "qualified", "name": "Qualified", "order": 3, "probability": 0.5},
        {"id": "proposal", "name": "Proposal Sent", "order": 4, "probability": 0.7},
        {"id": "negotiation", "name": "In Negotiation", "order": 5, "probability": 0.8},
        {"id": "won", "name": "Won", "order": 6, "probability": 1.0},
        {"id": "lost", "name": "Lost", "order": 7, "probability": 0.0}
    ]


@mcp.resource("http://go-high-level-mcp-server.local/automations")
def get_automations() -> List[Dict[str, str]]:
    """
    Get available automations in Go High Level
    """
    return [
        {"id": "welcome", "name": "Welcome Series", "type": "email"},
        {"id": "follow-up", "name": "Follow-up Sequence", "type": "multi-channel"},
        {"id": "appointment-reminder", "name": "Appointment Reminders", "type": "sms"},
        {"id": "abandoned-cart", "name": "Abandoned Cart Recovery", "type": "multi-channel"}
    ]


@mcp.resource("http://go-high-level-mcp-server.local/locations")
def get_locations() -> List[Dict[str, str]]:
    """
    Get all locations in Go High Level
    """
    return [
        {"id": "loc_12345", "name": "Main Location", "address": "123 Business Ave, City, State"},
        {"id": "loc_67890", "name": "Branch Office", "address": "456 Branch St, City, State"}
    ]


# Prompts
@mcp.prompt("/lead-nurturing-strategy")
def lead_nurturing_prompt(
    lead_profile: str,
    business_type: str,
    conversion_goal: str,
    context: str = ""
) -> str:
    """
    Generate a prompt for creating a lead nurturing strategy
    """
    return f"""
Create a lead nurturing strategy for: {lead_profile}
Business type: {business_type}
Conversion goal: {conversion_goal}
Context: {context}

Develop a multi-touch approach using Go High Level's automation features.
"""


@mcp.prompt("/sales-funnel-optimization")
def sales_funnel_prompt(
    current_funnel_data: Dict[str, Any],
    conversion_issues: List[str],
    business_goals: List[str],
    context: str = ""
) -> str:
    """
    Generate a prompt for optimizing a sales funnel in Go High Level
    """
    return f"""
Optimize the sales funnel based on:
Current data: {current_funnel_data}
Conversion issues: {conversion_issues}
Business goals: {business_goals}
Context: {context}

Suggest improvements to stages, automations, and lead management.
"""


@mcp.prompt("/appointment-scheduling-workflow")
def scheduling_workflow_prompt(
    business_type: str,
    ideal_customer_profile: str,
    availability_constraints: List[str],
    context: str = ""
) -> str:
    """
    Generate a prompt for creating an appointment scheduling workflow
    """
    return f"""
Design an appointment scheduling workflow for: {business_type}
Customer profile: {ideal_customer_profile}
Constraints: {availability_constraints}
Context: {context}

Use Go High Level's scheduling and automation features effectively.
"""


@mcp.prompt("/customer-retention-campaign")
def retention_campaign_prompt(
    customer_segment: str,
    churn_risk_factors: List[str],
    retention_goals: List[str],
    context: str = ""
) -> str:
    """
    Generate a prompt for creating a customer retention campaign
    """
    return f"""
Create a retention campaign for segment: {customer_segment}
Churn risk factors: {churn_risk_factors}
Retention goals: {retention_goals}
Context: {context}

Leverage Go High Level's communication and automation tools.
"""


if __name__ == "__main__":
    # Use stdio transport for MCP server (proper MCP protocol communication)
    asyncio.run(mcp.run_stdio_async())