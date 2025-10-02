#!/usr/bin/env python3
"""
Proposal Generator MCP Server

Provides access to business proposal generation functionality for LLMs through MCP protocol.
"""

from fastmcp import FastMCP
from typing import List, Dict, Any
import asyncio
from datetime import datetime


# Initialize the MCP server
mcp = FastMCP(
    name="Proposal Generator MCP Server",
    instructions="Provides access to business proposal generation functionality including document creation, pricing, and project planning",
    version="1.0.0"
)


# Tools
@mcp.tool
def generate_proposal(
    client_name: str,
    project_title: str,
    project_description: str,
    deliverables: List[str],
    timeline: str,
    pricing: Dict[str, Any],
    sections: List[str] = None
) -> Dict[str, Any]:
    """
    Generate a comprehensive business proposal
    """
    if sections is None:
        sections = ["executive-summary", "scope", "timeline", "pricing", "terms"]

    # In a real implementation, this would generate a full proposal document
    return {
        "status": "generated",
        "message": f"Proposal generated for {client_name} - {project_title}",
        "proposal_id": f"prop_{hash(client_name + project_title) % 10000}",
        "client": client_name,
        "title": project_title,
        "sections": sections,
        "deliverables_count": len(deliverables),
        "estimated_timeline": timeline,
        "total_pricing": pricing.get('total', 'TBD'),
        "generated_at": datetime.now().isoformat()
    }


@mcp.tool
def get_pricing_options(
    service_type: str,
    complexity_level: str,
    urgency: str = "standard"
) -> List[Dict[str, Any]]:
    """
    Get pricing options for different service types and complexity levels
    """
    # In a real implementation, this would retrieve from a pricing database
    # For simulation, returning sample pricing options
    base_prices = {
        "web-development": {"basic": 5000, "standard": 10000, "complex": 25000},
        "mobile-app": {"basic": 8000, "standard": 15000, "complex": 35000},
        "consulting": {"basic": 1000, "standard": 5000, "complex": 15000},
        "design": {"basic": 2000, "standard": 5000, "complex": 10000}
    }
    
    if service_type in base_prices:
        base_price = base_prices[service_type].get(complexity_level, 0)
        multiplier = 1.0 if urgency == "standard" else 1.5 if urgency == "urgent" else 2.0
        
        return [
            {
                "option": "basic",
                "description": "Essential features and functionality",
                "price": base_price * 0.8 * multiplier,
                "features": ["Core implementation", "Basic testing", "Limited support"]
            },
            {
                "option": "standard", 
                "description": "Standard implementation with additional features",
                "price": base_price * multiplier,
                "features": ["Full functionality", "Comprehensive testing", "1 month support"]
            },
            {
                "option": "premium",
                "description": "Full implementation with advanced features",
                "price": base_price * 1.5 * multiplier,
                "features": ["All features", "Extensive testing", "3 months support", "Training"]
            }
        ]
    else:
        return []


@mcp.tool
def calculate_project_cost(
    hours_estimate: int,
    hourly_rate: float,
    materials_cost: float = 0,
    additional_fees: List[Dict[str, float]] = None
) -> Dict[str, float]:
    """
    Calculate the total cost of a project based on hours, rate, and other costs
    """
    if additional_fees is None:
        additional_fees = []
    
    labor_cost = hours_estimate * hourly_rate
    fees_total = sum(fee.get("amount", 0) for fee in additional_fees)
    
    subtotal = labor_cost + materials_cost + fees_total
    tax = subtotal * 0.08  # Assuming 8% tax
    total_cost = subtotal + tax
    
    return {
        "labor_cost": labor_cost,
        "materials_cost": materials_cost,
        "additional_fees": fees_total,
        "subtotal": subtotal,
        "tax": tax,
        "total_cost": total_cost,
        "hours_estimate": hours_estimate,
        "hourly_rate": hourly_rate
    }


@mcp.tool
def create_work_breakdown_structure(
    project_name: str,
    project_scope: str,
    phases: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Create a Work Breakdown Structure (WBS) for a project
    """
    # In a real implementation, this would create a detailed WBS
    wbs = {
        "project_name": project_name,
        "scope": project_scope,
        "phases": [],
        "total_duration": 0,
        "wbs_id": f"wbs_{hash(project_name) % 10000}"
    }
    
    total_duration = 0
    for i, phase in enumerate(phases):
        phase_wbs = {
            "phase_id": f"{wbs['wbs_id']}_p{i+1}",
            "name": phase.get("name", f"Phase {i+1}"),
            "description": phase.get("description", ""),
            "duration_weeks": phase.get("duration_weeks", 2),
            "dependencies": phase.get("dependencies", []),
            "deliverables": phase.get("deliverables", []),
            "resources": phase.get("resources", [])
        }
        wbs["phases"].append(phase_wbs)
        total_duration += phase_wbs["duration_weeks"]
    
    wbs["total_duration"] = total_duration
    
    return wbs


@mcp.tool
def validate_proposal_data(
    proposal_data: Dict[str, Any]
) -> List[Dict[str, str]]:
    """
    Validate proposal data for completeness and accuracy
    """
    errors = []
    
    required_fields = [
        "client_name", "project_title", "project_description", 
        "deliverables", "timeline", "pricing"
    ]
    
    for field in required_fields:
        if field not in proposal_data or not proposal_data[field]:
            errors.append({
                "field": field,
                "error": "This field is required"
            })
    
    # Validate deliverables
    if "deliverables" in proposal_data and not proposal_data["deliverables"]:
        errors.append({
            "field": "deliverables",
            "error": "At least one deliverable is required"
        })
    
    # Validate pricing
    if "pricing" in proposal_data:
        pricing = proposal_data["pricing"]
        if not isinstance(pricing, dict):
            errors.append({
                "field": "pricing",
                "error": "Pricing must be a dictionary"
            })
    
    return errors


@mcp.tool
def get_client_history(client_name: str) -> List[Dict[str, str]]:
    """
    Get history of previous projects with a client
    """
    # In a real implementation, this would retrieve from a client database
    # For simulation, returning sample client history
    return [
        {
            "project_name": "E-commerce Website",
            "status": "Completed",
            "start_date": "2022-03-01",
            "end_date": "2022-06-15",
            "value": "$24,500",
            "rating": "5/5"
        },
        {
            "project_name": "Mobile App Development",
            "status": "Completed",
            "start_date": "2021-10-01",
            "end_date": "2022-01-20",
            "value": "$32,000",
            "rating": "4/5"
        }
    ]


@mcp.tool
def format_proposal_output(
    proposal_data: Dict[str, Any],
    output_format: str = "json"
) -> Dict[str, str]:
    """
    Format proposal data for output in different formats
    """
    if output_format.lower() == "json":
        return {
            "format": "json",
            "content": str(proposal_data),
            "message": "Proposal formatted as JSON"
        }
    elif output_format.lower() == "markdown":
        # Simplified markdown formatting
        md_content = f"# {proposal_data.get('project_title', 'Project Proposal')}\n\n"
        md_content += f"## Client: {proposal_data.get('client_name', 'N/A')}\n\n"
        md_content += f"### Description\n{proposal_data.get('project_description', 'N/A')}\n\n"
        
        deliverables = proposal_data.get('deliverables', [])
        if deliverables:
            md_content += "### Deliverables\n"
            for i, deliverable in enumerate(deliverables, 1):
                md_content += f"{i}. {deliverable}\n"
        
        return {
            "format": "markdown",
            "content": md_content,
            "message": "Proposal formatted as Markdown"
        }
    else:
        return {
            "format": output_format,
            "content": "",
            "error": f"Unsupported format: {output_format}"
        }


@mcp.tool
def compare_proposals(
    proposal_ids: List[str]
) -> Dict[str, Any]:
    """
    Compare multiple proposals based on various metrics
    """
    # In a real implementation, this would retrieve and compare actual proposals
    # For simulation, returning sample comparison
    return {
        "comparison_id": f"cmp_{hash(''.join(proposal_ids)) % 10000}",
        "proposals": [
            {
                "proposal_id": pid,
                "title": f"Proposal {pid}",
                "total_value": f"${(hash(pid) % 50000) + 10000}",
                "timeline": f"{(hash(pid) % 6) + 4} weeks",
                "complexity": "Standard" if hash(pid) % 2 == 0 else "Complex"
            } for pid in proposal_ids
        ],
        "key_differences": [
            "Pricing structures vary",
            "Timeline commitments differ", 
            "Scope of deliverables varies"
        ]
    }


@mcp.tool
def estimate_resource_requirements(
    project_scope: str,
    complexity: str,
    timeline_weeks: int
) -> Dict[str, Any]:
    """
    Estimate resource requirements for a project
    """
    # In a real implementation, this would use historical data for estimates
    base_team_sizes = {
        "basic": {"developers": 1, "designers": 0.5, "project_manager": 0.5},
        "standard": {"developers": 2, "designers": 1, "project_manager": 1},
        "complex": {"developers": 3, "designers": 2, "project_manager": 1, "architect": 0.5}
    }
    
    team_size = base_team_sizes.get(complexity, base_team_sizes["standard"])
    
    # Calculate monthly burn rate based on team size
    monthly_rates = {
        "developer": 8000,
        "designer": 6000,
        "project_manager": 7000,
        "architect": 12000
    }
    
    monthly_burn = 0
    for role, count in team_size.items():
        monthly_burn += monthly_rates.get(role, 0) * count
    
    total_project_cost = monthly_burn * (timeline_weeks / 4)  # Approximate months
    
    return {
        "estimated_team_size": team_size,
        "timeline_weeks": timeline_weeks,
        "estimated_monthly_burn": monthly_burn,
        "estimated_total_cost": total_project_cost,
        "project_scope": project_scope,
        "complexity": complexity
    }


@mcp.tool
def generate_risk_assessment(
    project_details: Dict[str, Any]
) -> List[Dict[str, str]]:
    """
    Generate risk assessment for a project proposal
    """
    risks = []
    
    # Common risks based on project attributes
    if project_details.get("complexity") == "complex":
        risks.append({
            "risk": "Technical complexity",
            "likelihood": "High",
            "impact": "High",
            "mitigation": "Thorough architecture planning and prototyping"
        })
    
    if project_details.get("timeline_weeks", 0) < 8:
        risks.append({
            "risk": "Aggressive timeline",
            "likelihood": "Medium",
            "impact": "High", 
            "mitigation": "Phased delivery approach with MVP focus"
        })
    
    if project_details.get("budget") and project_details["budget"] < 10000:
        risks.append({
            "risk": "Budget constraints",
            "likelihood": "High",
            "impact": "Medium",
            "mitigation": "Scope prioritization and phased implementation"
        })
    
    # Add default risks
    risks.extend([
        {
            "risk": "Scope creep",
            "likelihood": "Medium",
            "impact": "Medium",
            "mitigation": "Change management process"
        },
        {
            "risk": "Resource availability",
            "likelihood": "Low",
            "impact": "Medium",
            "mitigation": "Early resource commitment"
        }
    ])
    
    return risks


# Resources
@mcp.resource("http://proposal-generator-mcp-server.local/proposal-templates")
def get_proposal_templates() -> List[Dict[str, str]]:
    """
    Get available proposal templates
    """
    return [
        {
            "id": "software-dev",
            "name": "Software Development Proposal",
            "description": "Template for custom software development projects"
        },
        {
            "id": "consulting",
            "name": "Consulting Services Proposal", 
            "description": "Template for consulting and advisory services"
        },
        {
            "id": "design",
            "name": "Design Services Proposal",
            "description": "Template for design and creative projects"
        },
        {
            "id": "maintenance",
            "name": "Maintenance & Support Proposal",
            "description": "Template for ongoing maintenance and support contracts"
        }
    ]


@mcp.resource("http://proposal-generator-mcp-server.local/success-metrics")
def get_success_metrics() -> Dict[str, Any]:
    """
    Get metrics for successful proposals
    """
    return {
        "overall_conversion_rate": 0.32,
        "average_proposal_value": 24500,
        "most_successful_categories": ["web-development", "mobile-app", "consulting"],
        "average_response_time": "3.2 days",
        "client_satisfaction_rate": 0.94
    }


@mcp.resource("http://proposal-generator-mcp-server.local/pitching-tips")
def get_pitching_tips() -> List[str]:
    """
    Get tips for successful proposal pitching
    """
    return [
        "Customize the proposal to the client's specific needs and pain points",
        "Use clear and concise language, avoiding industry jargon",
        "Lead with the value proposition and expected outcomes",
        "Include examples of similar successful projects",
        "Be transparent about limitations and potential challenges",
        "Provide clear timelines and communication protocols",
        "Include a strong call to action with next steps"
    ]


# Prompts
@mcp.prompt("/proposal-strategy")
def proposal_strategy_prompt(
    client_profile: str,
    project_requirements: List[str],
    competitive_landscape: str,
    context: str = ""
) -> str:
    """
    Generate a prompt for developing a proposal strategy
    """
    return f"""
Develop a proposal strategy for client: {client_profile}
Project Requirements: {project_requirements}
Competitive Landscape: {competitive_landscape}
Context: {context}

Focus on differentiation, value proposition, and winning approach.
"""


@mcp.prompt("/value-proposition")
def value_proposition_prompt(
    service_offering: str,
    client_pain_points: List[str],
    success_metrics: List[str],
    context: str = ""
) -> str:
    """
    Generate a prompt for crafting a value proposition
    """
    return f"""
Craft a compelling value proposition for: {service_offering}
Addressing client pain points: {client_pain_points}
Expected success metrics: {success_metrics}
Context: {context}

Quantify benefits and differentiate from competitors.
"""


@mcp.prompt("/pricing-strategy")
def pricing_strategy_prompt(
    project_complexity: str,
    market_rates: Dict[str, float],
    client_budget: str,
    context: str = ""
) -> str:
    """
    Generate a prompt for determining pricing strategy
    """
    return f"""
Determine optimal pricing for project complexity: {project_complexity}
Market rates: {market_rates}
Client budget: {client_budget}
Context: {context}

Balance competitiveness with profitability and value delivery.
"""


@mcp.prompt("/proposal-follow-up")
def proposal_follow_up_prompt(
    proposal_status: str,
    client_feedback: str,
    negotiation_points: List[str],
    context: str = ""
) -> str:
    """
    Generate a prompt for following up on a proposal
    """
    return f"""
Plan follow-up strategy for proposal status: {proposal_status}
Client feedback: {client_feedback}
Negotiation points: {negotiation_points}
Context: {context}

Address concerns and move toward agreement.
"""


if __name__ == "__main__":
    # Use stdio transport for MCP server (proper MCP protocol communication)
    asyncio.run(mcp.run_stdio_async())