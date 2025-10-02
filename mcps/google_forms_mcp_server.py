#!/usr/bin/env python3
"""
Google Forms MCP Server

Provides access to Google Forms functionality for LLMs through MCP protocol.
"""

from fastmcp import FastMCP
from typing import List, Dict, Any
import asyncio
from datetime import datetime


# Initialize the MCP server
mcp = FastMCP(
    name="Google Forms MCP Server",
    instructions="Provides access to Google Forms functionality including form creation, management, and response handling",
    version="1.0.0"
)


# Tools
@mcp.tool
def create_form(
    title: str,
    description: str = "",
    fields: List[Dict[str, Any]] = None,
    is_quiz: bool = False,
    collect_email: bool = False
) -> Dict[str, str]:
    """
    Create a new Google Form
    """
    form_id = f"form_{hash(title + description[:10]) % 10000}"
    form_url = f"https://docs.google.com/forms/d/e/{form_id}/viewform"
    
    if fields is None:
        fields = [
            {"type": "short_answer", "title": "Name", "required": True},
            {"type": "email", "title": "Email", "required": True}
        ]
    
    return {
        "status": "created",
        "form_id": form_id,
        "form_url": form_url,
        "title": title,
        "fields_count": len(fields),
        "message": f"Form '{title}' created successfully"
    }


@mcp.tool
def get_form_details(form_id: str) -> Dict[str, Any]:
    """
    Get details of a specific Google Form
    """
    # In a real implementation, this would fetch from Google Forms API
    return {
        "form_id": form_id,
        "title": f"Form Title for {form_id}",
        "description": f"Description for form {form_id}",
        "is_quiz": False,
        "collects_response_emails": True,
        "creation_time": "2023-01-15T10:30:00Z",
        "last_modified_time": "2023-01-16T14:20:00Z",
        "form_url": f"https://docs.google.com/forms/d/e/{form_id}/viewform",
        "responses_url": f"https://docs.google.com/forms/d/e/{form_id}/responses",
        "total_responses": 42,
        "fields": [
            {"id": "field_1", "title": "Name", "type": "short_answer", "required": True},
            {"id": "field_2", "title": "Email", "type": "email", "required": True},
            {"id": "field_3", "title": "Feedback", "type": "paragraph", "required": False}
        ]
    }


@mcp.tool
def list_forms(limit: int = 20) -> List[Dict[str, str]]:
    """
    List Google Forms with basic information
    """
    forms = []
    for i in range(limit):
        forms.append({
            "form_id": f"form_{i:04d}",
            "title": f"Form Title {i+1}",
            "description": f"Description for form {i+1}",
            "response_count": (i + 1) * 5,
            "last_modified": (datetime.now() - timedelta(days=i)).isoformat(),
            "view_url": f"https://docs.google.com/forms/d/e/form_{i:04d}/viewform",
            "responses_url": f"https://docs.google.com/forms/d/e/form_{i:04d}/responses"
        })
    
    return forms


@mcp.tool
def add_form_field(
    form_id: str,
    field_type: str,  # short_answer, paragraph, multiple_choice, checkbox, dropdown, date, time, etc.
    title: str,
    required: bool = False,
    choices: List[str] = None
) -> Dict[str, str]:
    """
    Add a field to an existing Google Form
    """
    field_id = f"field_{hash(form_id + title) % 10000}"
    
    return {
        "status": "added",
        "form_id": form_id,
        "field_id": field_id,
        "title": title,
        "type": field_type,
        "message": f"Field '{title}' added to form {form_id}"
    }


@mcp.tool
def get_form_responses(form_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get responses for a specific Google Form
    """
    # In a real implementation, this would fetch from Google Forms API
    responses = []
    for i in range(min(limit, 25)):  # Limit to 25 sample responses
        responses.append({
            "response_id": f"resp_{i:04d}",
            "timestamp": (datetime.now() - timedelta(hours=i)).isoformat(),
            "responder_email": f"responder{i}@example.com",
            "answers": {
                "field_1": f"Response {i} for field 1",
                "field_2": f"responder{i}@example.com",
                "field_3": f"This is a longer response for question {i} in field 3"
            }
        })
    
    return responses


@mcp.tool
def get_form_response_summary(form_id: str) -> Dict[str, Any]:
    """
    Get a summary of responses for a Google Form
    """
    # In a real implementation, this would aggregate actual responses
    return {
        "form_id": form_id,
        "total_responses": 128,
        "completion_rate": 0.85,  # 85% completion rate
        "first_response": "2023-06-01T09:30:00Z",
        "last_response": "2023-06-15T15:45:00Z",
        "average_completion_time": 3.5,  # minutes
        "top_keywords": ["excellent", "good", "satisfied", "recommend"],
        "rating_average": 4.2  # if it's a rating form
    }


@mcp.tool
def update_form_settings(
    form_id: str,
    title: str = None,
    description: str = None,
    collect_email: bool = None,
    is_quiz: bool = None
) -> Dict[str, str]:
    """
    Update settings for an existing Google Form
    """
    changes = []
    if title:
        changes.append(f"title: {title}")
    if description:
        changes.append(f"description: {description[:30]}...")
    if collect_email is not None:
        changes.append(f"collect_email: {collect_email}")
    if is_quiz is not None:
        changes.append(f"is_quiz: {is_quiz}")
    
    return {
        "status": "updated",
        "form_id": form_id,
        "message": f"Form {form_id} updated: {', '.join(changes) if changes else 'no changes'}"
    }


@mcp.tool
def share_form(form_id: str, emails: List[str], role: str = "reader") -> Dict[str, str]:
    """
    Share a form with specific users
    """
    return {
        "status": "shared",
        "form_id": form_id,
        "recipient_count": len(emails),
        "role": role,
        "message": f"Form {form_id} shared with {len(emails)} users"
    }


@mcp.tool
def create_form_from_template(
    template_name: str,
    title: str,
    description: str = ""
) -> Dict[str, str]:
    """
    Create a form based on a predefined template
    """
    templates = {
        "contact": {
            "fields": [
                {"type": "short_answer", "title": "Full Name", "required": True},
                {"type": "email", "title": "Email Address", "required": True},
                {"type": "short_answer", "title": "Subject", "required": True},
                {"type": "paragraph", "title": "Message", "required": True}
            ]
        },
        "feedback": {
            "fields": [
                {"type": "short_answer", "title": "Your Name", "required": False},
                {"type": "rating", "title": "Overall Rating", "required": True},
                {"type": "paragraph", "title": "What did you like?", "required": False},
                {"type": "paragraph", "title": "What could be improved?", "required": False}
            ]
        },
        "survey": {
            "fields": [
                {"type": "short_answer", "title": "Name", "required": False},
                {"type": "dropdown", "title": "Department", "choices": ["Sales", "Marketing", "Engineering", "Other"]},
                {"type": "multiple_choice", "title": "Satisfaction Level", "choices": ["Very Satisfied", "Satisfied", "Neutral", "Dissatisfied", "Very Dissatisfied"]},
                {"type": "paragraph", "title": "Additional Comments", "required": False}
            ]
        }
    }
    
    if template_name not in templates:
        return {"status": "error", "message": f"Template '{template_name}' not available"}
    
    form_id = f"form_{hash(title) % 10000}"
    
    return {
        "status": "created",
        "form_id": form_id,
        "title": title,
        "template_used": template_name,
        "message": f"Form '{title}' created from {template_name} template"
    }


@mcp.tool
def export_responses(form_id: str, format_type: str = "csv") -> Dict[str, str]:
    """
    Export form responses in specified format
    """
    available_formats = ["csv", "excel", "pdf", "json"]
    if format_type not in available_formats:
        return {"status": "error", "message": f"Format {format_type} not supported. Available: {available_formats}"}
    
    filename = f"form_{form_id}_responses.{format_type}"
    
    return {
        "status": "exported",
        "form_id": form_id,
        "format": format_type,
        "filename": filename,
        "message": f"Responses for form {form_id} exported as {format_type}"
    }


# Resources
@mcp.resource("http://google-forms-mcp-server.local/form-templates")
def get_form_templates() -> List[Dict[str, str]]:
    """
    Get available form templates
    """
    return [
        {
            "id": "contact",
            "name": "Contact Form",
            "description": "Basic contact form with name, email, and message fields"
        },
        {
            "id": "feedback",
            "name": "Feedback Form", 
            "description": "Simple feedback form with rating and comments"
        },
        {
            "id": "survey",
            "name": "Survey Form",
            "description": "Multi-question survey with various field types"
        },
        {
            "id": "registration",
            "name": "Event Registration",
            "description": "Registration form for events with additional information"
        },
        {
            "id": "quiz",
            "name": "Quiz Form",
            "description": "Form configured as a quiz with grading"
        }
    ]


@mcp.resource("http://google-forms-mcp-server.local/field-types")
def get_field_types() -> List[Dict[str, str]]:
    """
    Get available field types for Google Forms
    """
    return [
        {"type": "short_answer", "name": "Short Answer", "description": "Single line text input"},
        {"type": "paragraph", "name": "Paragraph", "description": "Multi-line text input"},
        {"type": "multiple_choice", "name": "Multiple Choice", "description": "Select one option from list"},
        {"type": "checkbox", "name": "Checkboxes", "description": "Select multiple options from list"},
        {"type": "dropdown", "name": "Dropdown", "description": "Select one option from dropdown list"},
        {"type": "linear_scale", "name": "Linear Scale", "description": "Rate on a scale"},
        {"type": "date", "name": "Date", "description": "Date picker"},
        {"type": "time", "name": "Time", "description": "Time picker"},
        {"type": "file_upload", "name": "File Upload", "description": "Allow file attachments"},
        {"type": "section_header", "name": "Section Header", "description": "Organize form with headers"},
        {"type": "page_break", "name": "Page Break", "description": "Separate form into multiple pages"}
    ]


@mcp.resource("http://google-forms-mcp-server.local/response-analytics")
def get_response_analytics(form_id: str) -> Dict[str, Any]:
    """
    Get analytics for form responses
    """
    return {
        "form_id": form_id,
        "time_to_complete_distribution": {
            "0-1min": 15,
            "1-3min": 45,
            "3-5min": 30,
            "5+min": 10
        },
        "response_rate_by_hour": {
            "9am": 12,
            "10am": 20,
            "11am": 18,
            "12pm": 10,
            "1pm": 15,
            "2pm": 22,
            "3pm": 18,
            "4pm": 14
        },
        "device_type_breakdown": {
            "desktop": 65,
            "mobile": 30,
            "tablet": 5
        },
        "geographic_distribution": {
            "US": 70,
            "CA": 15,
            "UK": 10,
            "Other": 5
        }
    }


# Prompts
@mcp.prompt("/form-design-best-practices")
def form_design_prompt(
    form_purpose: str,
    target_audience: str,
    required_information: List[str],
    context: str = ""
) -> str:
    """
    Generate a prompt for designing an effective form
    """
    return f"""
Design an effective Google Form for: {form_purpose}
Target audience: {target_audience}
Required information: {required_information}
Context: {context}

Consider field types, layout, and user experience best practices.
"""


@mcp.prompt("/survey-question-crafting")
def question_crafting_prompt(
    question_topic: str,
    response_objective: str,
    target_demographic: str,
    context: str = ""
) -> str:
    """
    Generate a prompt for crafting effective survey questions
    """
    return f"""
Craft effective survey questions about: {question_topic}
Objective: {response_objective}
Target demographic: {target_demographic}
Context: {context}

Focus on clarity, neutrality, and appropriate question types.
"""


@mcp.prompt("/form-response-analysis")
def response_analysis_prompt(
    form_responses: List[Dict[str, Any]],
    analysis_goals: List[str],
    target_insights: List[str],
    context: str = ""
) -> str:
    """
    Generate a prompt for analyzing form responses
    """
    return f"""
Analyze these form responses: {form_responses[:3]} (showing first 3)
Analysis goals: {analysis_goals}
Target insights: {target_insights}
Context: {context}

Extract meaningful insights and identify patterns in the data.
"""


@mcp.prompt("/form-optimization")
def optimization_prompt(
    form_performance: Dict[str, Any],
    user_feedback: List[str],
    conversion_goals: List[str],
    context: str = ""
) -> str:
    """
    Generate a prompt for optimizing form performance
    """
    return f"""
Optimize form performance based on:
Performance data: {form_performance}
User feedback: {user_feedback}
Conversion goals: {conversion_goals}
Context: {context}

Suggest improvements to increase completion rate and data quality.
"""


if __name__ == "__main__":
    # Use stdio transport for MCP server (proper MCP protocol communication)
    asyncio.run(mcp.run_stdio_async())