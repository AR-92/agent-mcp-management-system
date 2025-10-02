#!/usr/bin/env python3
"""
Twenty CRM MCP Server

Provides access to Twenty CRM functionality for LLMs through MCP protocol.
"""

from fastmcp import FastMCP
from typing import List, Dict, Any
import asyncio


# Initialize the MCP server
mcp = FastMCP(
    name="Twenty CRM MCP Server",
    instructions="Provides access to Twenty CRM functionality including contact management, lead tracking, and sales operations",
    version="1.0.0"
)


# Tools
@mcp.tool
def list_contacts(
    limit: int = 20, 
    offset: int = 0,
    search_query: str = None
) -> List[Dict[str, Any]]:
    """
    List contacts in the Twenty CRM system
    """
    # This would connect to Twenty CRM API in a real implementation
    return [
        {
            "id": f"contact_{i:04d}",
            "first_name": f"Contact {i}",
            "last_name": f"Person {i}",
            "display_name": f"Contact {i} Person {i}",
            "email": f"contact{i}@example.com",
            "phone": f"+1-555-010{i:02d}",
            "company": f"Company {i}",
            "job_title": f"Position {i}",
            "city": f"City {i}",
            "country": "US",
            "tags": ["Prospect", "Lead"],
            "created_at": "2023-01-01T10:00:00Z",
            "updated_at": "2023-01-15T10:00:00Z"
        }
        for i in range(limit)
    ]


@mcp.tool
def get_contact(contact_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific contact
    """
    return {
        "id": contact_id,
        "first_name": f"Contact {contact_id}",
        "last_name": f"Lastname {contact_id}",
        "display_name": f"Contact {contact_id} Lastname {contact_id}",
        "email": f"{contact_id}@example.com",
        "phone": "+1-555-0100",
        "company": f"Company {contact_id}",
        "job_title": "Position Title",
        "city": "Anytown",
        "country": "US",
        "tags": ["Customer", "VIP"],
        "created_at": "2023-01-01T10:00:00Z",
        "updated_at": "2023-01-15T10:00:00Z",
        "linkedin_url": f"https://linkedin.com/in/{contact_id}",
        "twitter_handle": f"@{contact_id}"
    }


@mcp.tool
def create_contact(
    first_name: str, 
    last_name: str, 
    email: str, 
    company: str = "",
    phone: str = "",
    job_title: str = "",
    tags: List[str] = None
) -> Dict[str, str]:
    """
    Create a new contact in Twenty CRM
    """
    if tags is None:
        tags = ["New"]
    
    return {
        "status": "created",
        "contact_id": "new_contact_id",
        "message": f"Contact '{first_name} {last_name}' created successfully"
    }


@mcp.tool
def update_contact(
    contact_id: str,
    first_name: str = None,
    last_name: str = None,
    email: str = None,
    company: str = None,
    phone: str = None
) -> Dict[str, str]:
    """
    Update an existing contact in Twenty CRM
    """
    return {
        "status": "updated",
        "message": f"Contact {contact_id} updated successfully"
    }


@mcp.tool
def list_leads(
    limit: int = 20, 
    offset: int = 0,
    status: str = "new"
) -> List[Dict[str, Any]]:
    """
    List leads in the Twenty CRM system
    """
    return [
        {
            "id": f"lead_{i:04d}",
            "full_name": f"Lead {i} Person",
            "email": f"lead{i}@example.com",
            "phone": f"+1-555-020{i:02d}",
            "company": f"Lead Company {i}",
            "status": status,
            "source": "Website" if i % 2 == 0 else "Referral",
            "owner_id": f"user_{i % 3}",
            "created_at": f"2023-01-{10+i:02d}T09:00:00Z",
            "updated_at": f"2023-01-{10+i:02d}T15:00:00Z",
            "estimated_value": f"{5000 + i * 1000}.00",
            "probability": 0.75
        }
        for i in range(limit)
    ]


@mcp.tool
def get_lead(lead_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific lead
    """
    return {
        "id": lead_id,
        "full_name": f"Lead {lead_id}",
        "email": f"lead.{lead_id}@example.com",
        "phone": "+1-555-0200",
        "company": f"Lead Company {lead_id}",
        "status": "qualified",
        "source": "Trade Show",
        "owner_id": "user_1",
        "created_at": "2023-01-15T10:00:00Z",
        "updated_at": "2023-01-16T14:00:00Z",
        "estimated_value": "7500.00",
        "probability": 0.80,
        "notes": f"Initial contact made with lead {lead_id}",
        "linkedin_url": f"https://linkedin.com/in/lead-{lead_id}",
        "tags": ["Hot Lead", "Enterprise"]
    }


@mcp.tool
def create_lead(
    full_name: str,
    email: str,
    company: str,
    source: str = "Website",
    estimated_value: float = 5000.0,
    notes: str = ""
) -> Dict[str, str]:
    """
    Create a new lead in Twenty CRM
    """
    return {
        "status": "created",
        "lead_id": "new_lead_id",
        "message": f"Lead '{full_name}' from '{company}' created successfully"
    }


@mcp.tool
def list_opportunities(
    limit: int = 20, 
    offset: int = 0,
    stage: str = "prospecting"
) -> List[Dict[str, Any]]:
    """
    List sales opportunities in Twenty CRM
    """
    return [
        {
            "id": f"opp_{i:04d}",
            "name": f"Opportunity {i}",
            "company": f"Company {i}",
            "stage": stage,
            "value": f"{10000 + i * 5000}.00",
            "probability": 0.5 + (i * 0.05),
            "close_date": f"2023-06-{15+i:02d}",
            "owner_id": f"user_{i % 3}",
            "created_at": f"2023-01-{5+i:02d}T08:00:00Z",
            "updated_at": f"2023-01-{10+i:02d}T12:00:00Z",
            "description": f"Sales opportunity for {f'Company {i}'}"
        }
        for i in range(limit)
    ]


@mcp.tool
def get_opportunity(opportunity_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific opportunity
    """
    return {
        "id": opportunity_id,
        "name": f"Opportunity {opportunity_id}",
        "company": f"Company {opportunity_id}",
        "stage": "proposal",
        "value": "25000.00",
        "probability": 0.75,
        "close_date": "2023-07-15",
        "owner_id": "user_1",
        "created_at": "2023-01-10T09:00:00Z",
        "updated_at": "2023-01-20T14:00:00Z",
        "description": f"Detailed description for opportunity {opportunity_id}",
        "contact_ids": [f"contact_{i}" for i in range(3)],
        "notes": f"Follow up required for opportunity {opportunity_id}"
    }


@mcp.tool
def search_contacts(query: str) -> List[Dict[str, Any]]:
    """
    Search for contacts based on a query
    """
    return [
        {
            "id": f"search_result_{i}",
            "display_name": f"Search Result {i} for '{query}'",
            "email": f"result{i}@example.com",
            "company": f"Result Company {i}",
            "job_title": "Search Result Position",
            "tags": ["Search Result"]
        }
        for i in range(10)
    ]


# Resources
@mcp.resource("http://twenty-crm-mcp-server.local/status")
def get_crm_status() -> Dict[str, Any]:
    """
    Get the status of the Twenty CRM MCP server
    """
    return {
        "status": "connected",
        "server_time": asyncio.get_event_loop().time(),
        "connected": True,
        "api_version": "v1.0",
        "data_center": "us-east-1"
    }


@mcp.resource("http://twenty-crm-mcp-server.local/pipeline-stages")
def get_pipeline_stages() -> List[Dict[str, Any]]:
    """
    Get the sales pipeline stages
    """
    return [
        {"id": "new", "name": "New", "order": 1, "probability": 0.1},
        {"id": "qualified", "name": "Qualified", "order": 2, "probability": 0.3},
        {"id": "proposal", "name": "Proposal", "order": 3, "probability": 0.6},
        {"id": "negotiation", "name": "Negotiation", "order": 4, "probability": 0.8},
        {"id": "won", "name": "Won", "order": 5, "probability": 1.0},
        {"id": "lost", "name": "Lost", "order": 6, "probability": 0.0}
    ]


@mcp.resource("http://twenty-crm-mcp-server.local/team")
def get_team_members() -> List[Dict[str, str]]:
    """
    Get team members in the CRM
    """
    return [
        {"id": "user_1", "name": "Sales Manager", "email": "sales@company.com", "role": "Manager"},
        {"id": "user_2", "name": "Account Executive 1", "email": "ae1@company.com", "role": "Executive"},
        {"id": "user_3", "name": "Account Executive 2", "email": "ae2@company.com", "role": "Executive"}
    ]


# Prompts
@mcp.prompt("/crm-follow-up-strategy")
def follow_up_strategy_prompt(
    contact_id: str, 
    last_interaction: str,
    opportunity_id: str = None,
    context: str = ""
) -> str:
    """
    Generate a prompt for creating a follow-up strategy
    """
    return f"""
Create a follow-up strategy for contact {contact_id}
Last interaction: {last_interaction}
Opportunity: {opportunity_id or 'None'}
Context: {context}

Consider the right timing, communication channel, and message content for effective follow-up.
"""


@mcp.prompt("/crm-lead-qualification")
def lead_qualification_prompt(
    lead_id: str, 
    qualification_criteria: List[str],
    context: str = ""
) -> str:
    """
    Generate a prompt for qualifying a lead
    """
    return f"""
Qualify lead {lead_id} based on: {qualification_criteria}
Context: {context}

Apply qualification frameworks like BANT (Budget, Authority, Need, Timeline) to assess lead quality.
"""


@mcp.prompt("/crm-sales-approach")
def sales_approach_prompt(
    opportunity_id: str, 
    customer_profile: str,
    product_service: str,
    context: str = ""
) -> str:
    """
    Generate a prompt for planning a sales approach
    """
    return f"""
Plan a sales approach for opportunity {opportunity_id}
Customer Profile: {customer_profile}
Product/Service: {product_service}
Context: {context}

Outline the sales strategy, key talking points, and potential objections to address.
"""


@mcp.prompt("/crm-account-plan")
def account_plan_prompt(
    contact_id: str, 
    account_strategies: List[str],
    context: str = ""
) -> str:
    """
    Generate a prompt for creating an account plan
    """
    return f"""
Create an account plan for contact {contact_id} with strategies: {account_strategies}
Context: {context}

Develop a comprehensive plan for managing and growing the relationship with this account.
"""


if __name__ == "__main__":
    # Use stdio transport for MCP server (proper MCP protocol communication)
    asyncio.run(mcp.run_stdio_async())