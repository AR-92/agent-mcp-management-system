#!/usr/bin/env python3
"""
Interview Scheduler MCP Server

Provides access to interview scheduling functionality for LLMs through MCP protocol.
"""

from fastmcp import FastMCP
from typing import List, Dict, Any
import asyncio
from datetime import datetime, timedelta


# Initialize the MCP server
mcp = FastMCP(
    name="Interview Scheduler MCP Server",
    instructions="Provides access to interview scheduling functionality including calendar management, candidate coordination, and interview logistics",
    version="1.0.0"
)


# Tools
@mcp.tool
def schedule_interview(
    candidate_name: str,
    candidate_email: str,
    interviewer_names: List[str],
    interview_date: str,
    interview_time: str,
    duration_minutes: int = 60,
    interview_type: str = "technical",
    location: str = "virtual",
    meeting_link: str = None,
    notes: str = ""
) -> Dict[str, str]:
    """
    Schedule a new interview
    """
    # In a real implementation, this would integrate with a calendar system
    return {
        "status": "scheduled",
        "message": f"Interview scheduled for {candidate_name} with {', '.join(interviewer_names)}",
        "interview_id": f"int_{hash(candidate_name + interview_date + interview_time) % 10000}",
        "candidate": candidate_name,
        "date": interview_date,
        "time": interview_time,
        "duration": f"{duration_minutes} minutes"
    }


@mcp.tool
def get_candidate_schedule(candidate_email: str) -> List[Dict[str, Any]]:
    """
    Get scheduled interviews for a candidate
    """
    # This would retrieve from a database in a real implementation
    # For simulation, returning sample data
    return [
        {
            "interview_id": "int_1234",
            "candidate": "John Doe",
            "position": "Software Engineer",
            "date": "2023-06-15",
            "time": "10:00",
            "duration": "60 minutes",
            "status": "scheduled",
            "interviewers": ["Alice Johnson", "Bob Smith"],
            "type": "technical",
            "location": "virtual",
            "meeting_link": "https://meet.example.com/interview/1234"
        },
        {
            "interview_id": "int_5678",
            "candidate": "John Doe",
            "position": "Software Engineer",
            "date": "2023-06-16",
            "time": "14:00",
            "duration": "45 minutes",
            "status": "scheduled",
            "interviewers": ["Carol Davis"],
            "type": "behavioral",
            "location": "virtual",
            "meeting_link": "https://meet.example.com/interview/5678"
        }
    ]


@mcp.tool
def get_interviewer_schedule(
    interviewer_email: str = None,
    interviewer_name: str = None,
    date_range_start: str = None,
    date_range_end: str = None
) -> List[Dict[str, Any]]:
    """
    Get scheduled interviews for an interviewer
    """
    # This would retrieve from a database in a real implementation
    # For simulation, returning sample data
    return [
        {
            "interview_id": "int_1234",
            "candidate": "John Doe",
            "position": "Software Engineer",
            "date": "2023-06-15",
            "time": "10:00",
            "duration": "60 minutes",
            "status": "scheduled",
            "interviewers": ["Alice Johnson", "Bob Smith"],
            "type": "technical"
        },
        {
            "interview_id": "int_9012",
            "candidate": "Jane Smith",
            "position": "Product Manager",
            "date": "2023-06-15",
            "time": "15:00",
            "duration": "45 minutes",
            "status": "scheduled",
            "interviewers": ["Alice Johnson"],
            "type": "behavioral"
        }
    ]


@mcp.tool
def cancel_interview(interview_id: str, reason: str = "") -> Dict[str, str]:
    """
    Cancel a scheduled interview
    """
    # This would update a database in a real implementation
    return {
        "status": "cancelled",
        "message": f"Interview {interview_id} has been cancelled",
        "reason": reason or "No reason provided"
    }


@mcp.tool
def update_interview(
    interview_id: str,
    candidate_name: str = None,
    interview_date: str = None,
    interview_time: str = None,
    interviewer_names: List[str] = None,
    notes: str = None
) -> Dict[str, str]:
    """
    Update details of a scheduled interview
    """
    # This would update a database in a real implementation
    changes = []
    if candidate_name:
        changes.append(f"candidate: {candidate_name}")
    if interview_date:
        changes.append(f"date: {interview_date}")
    if interview_time:
        changes.append(f"time: {interview_time}")
    if interviewer_names:
        changes.append(f"interviewers: {', '.join(interviewer_names)}")
    
    return {
        "status": "updated",
        "message": f"Interview {interview_id} updated: {', '.join(changes) if changes else 'no changes made'}"
    }


@mcp.tool
def get_available_time_slots(
    interviewer_names: List[str],
    date: str,
    start_time: str = "09:00",
    end_time: str = "17:00",
    interval_minutes: int = 30
) -> List[str]:
    """
    Get available time slots for interviewers on a specific date
    """
    # This would check actual calendars in a real implementation
    # For simulation, returning sample available slots
    import random
    
    # Generate all possible time slots in the range
    start_hour, start_min = map(int, start_time.split(':'))
    end_hour, end_min = map(int, end_time.split(':'))
    
    current_time = start_hour * 60 + start_min
    end_time_minutes = end_hour * 60 + end_min
    
    available_slots = []
    while current_time < end_time_minutes:
        time_str = f"{current_time // 60:02d}:{current_time % 60:02d}"
        
        # Simulate 30% chance of slot being unavailable
        if random.random() > 0.3:
            available_slots.append(time_str)
        
        current_time += interval_minutes
    
    # Return maximum 6 available slots for this example
    return available_slots[:6]


@mcp.tool
def send_interview_reminder(interview_id: str) -> Dict[str, str]:
    """
    Send a reminder for an upcoming interview
    """
    # This would send an actual email in a real implementation
    return {
        "status": "sent",
        "message": f"Reminder sent for interview {interview_id}"
    }


@mcp.tool
def get_upcoming_interviews(
    days_ahead: int = 7,
    candidate_name: str = None
) -> List[Dict[str, Any]]:
    """
    Get interviews scheduled within the specified number of days
    """
    # This would retrieve from a database in a real implementation
    # For simulation, returning sample data
    from datetime import datetime, timedelta
    
    base_date = datetime.now()
    interviews = []
    
    for i in range(3):
        interview_date = base_date + timedelta(days=i+1)
        interviews.append({
            "interview_id": f"int_{1000+i}",
            "candidate": candidate_name or f"Candidate {i+1}",
            "position": "Software Engineer",
            "date": interview_date.strftime("%Y-%m-%d"),
            "time": f"1{2+i}:00",
            "duration": "60 minutes",
            "status": "scheduled",
            "interviewers": ["Interviewer A", "Interviewer B"],
            "type": "technical",
            "location": "virtual"
        })
    
    return interviews


@mcp.tool
def check_candidate_availability(
    candidate_email: str,
    proposed_date: str,
    proposed_time: str,
    duration_minutes: int = 60
) -> Dict[str, bool]:
    """
    Check if a candidate is available at the proposed time
    """
    # This would check actual candidate calendar in a real implementation
    # For simulation, returning a random availability check
    import random
    is_available = random.choice([True, False])
    
    return {
        "available": is_available,
        "candidate": candidate_email,
        "proposed_time": f"{proposed_date} {proposed_time}",
        "duration": f"{duration_minutes} minutes"
    }


@mcp.tool
def get_interview_feedback(interview_id: str) -> Dict[str, Any]:
    """
    Get feedback for a completed interview
    """
    # This would retrieve from a database in a real implementation
    # For simulation, returning sample feedback
    return {
        "interview_id": interview_id,
        "candidate": "John Doe",
        "interviewer": "Alice Johnson",
        "date": "2023-06-15",
        "rating": 4.2,
        "overall_status": "move-forward",
        "technical_skills": "Strong",
        "communication": "Good",
        "cultural_fit": "Good",
        "strengths": ["Problem-solving", "Technical depth"],
        "improvements": ["System design experience", "Leadership examples"],
        "recommendation": "Strongly recommend proceeding to next round"
    }


# Resources
@mcp.resource("http://interview-scheduler-mcp-server.local/interview-types")
def get_interview_types() -> List[Dict[str, str]]:
    """
    Get available interview types
    """
    return [
        {"type": "technical", "description": "Technical skills and coding assessment"},
        {"type": "behavioral", "description": "Behavioral and cultural fit assessment"},
        {"type": "system-design", "description": "System design and architecture discussion"},
        {"type": "culture-fit", "description": "Company culture and values alignment"},
        {"type": "take-home", "description": "Take-home assignment review"}
    ]


@mcp.resource("http://interview-scheduler-mcp-server.local/interview-stats")
def get_interview_stats() -> Dict[str, Any]:
    """
    Get interview statistics
    """
    return {
        "total_scheduled": 125,
        "completed": 110,
        "cancelled": 8,
        "pending": 7,
        "avg_duration_minutes": 55,
        "most_popular_day": "Tuesday",
        "most_popular_type": "technical"
    }


@mcp.resource("http://interview-scheduler-mcp-server.local/interview-guidelines")
def get_interview_guidelines() -> Dict[str, str]:
    """
    Get interview guidelines and best practices
    """
    return {
        "title": "Interview Best Practices",
        "preparation": "Review candidate's resume and portfolio before interview",
        "conduct": [
            "Start on time",
            "Introduce yourself and explain the interview structure",
            "Ask consistent questions across candidates for fair evaluation",
            "Take notes during the interview"
        ],
        "evaluation": [
            "Rate candidates on technical skills, communication, and cultural fit",
            "Provide specific examples in feedback",
            "Submit feedback within 24 hours of interview"
        ],
        "follow_up": "Coordinate with other interviewers to discuss candidate before making a decision"
    }


# Prompts
@mcp.prompt("/interview-preparation")
def interview_preparation_prompt(
    candidate_profile: str,
    interview_type: str,
    position_requirements: List[str],
    context: str = ""
) -> str:
    """
    Generate a prompt for preparing for an interview
    """
    return f"""
Prepare for interview with candidate: {candidate_profile}
Interview Type: {interview_type}
Position Requirements: {position_requirements}
Context: {context}

Suggest relevant questions, technical challenges, and evaluation criteria.
"""


@mcp.prompt("/candidate-evaluation")
def candidate_evaluation_prompt(
    interview_notes: str,
    technical_skills: str,
    communication_skills: str,
    cultural_fit: str,
    context: str = ""
) -> str:
    """
    Generate a prompt for evaluating a candidate's interview
    """
    return f"""
Evaluate candidate based on:
Interview Notes: {interview_notes}
Technical Skills: {technical_skills}
Communication Skills: {communication_skills}
Cultural Fit: {cultural_fit}
Context: {context}

Provide a comprehensive assessment with recommendations.
"""


@mcp.prompt("/interview-logistics-planning")
def logistics_planning_prompt(
    interview_type: str,
    participants: List[str],
    technical_requirements: List[str],
    context: str = ""
) -> str:
    """
    Generate a prompt for planning interview logistics
    """
    return f"""
Plan logistics for {interview_type} interview with participants: {participants}
Technical Requirements: {technical_requirements}
Context: {context}

Coordinate technology, materials, and scheduling needs.
"""


@mcp.prompt("/feedback-template")
def feedback_template_prompt(
    interview_type: str,
    position_level: str,
    evaluation_criteria: List[str],
    context: str = ""
) -> str:
    """
    Generate a prompt for creating interview feedback template
    """
    return f"""
Create a feedback template for {interview_type} interview for {position_level} position
Evaluation Criteria: {evaluation_criteria}
Context: {context}

Include specific fields for skills assessment and recommendation.
"""


if __name__ == "__main__":
    # Use stdio transport for MCP server (proper MCP protocol communication)
    asyncio.run(mcp.run_stdio_async())