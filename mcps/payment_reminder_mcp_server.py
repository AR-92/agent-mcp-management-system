#!/usr/bin/env python3
"""
Payment Reminder MCP Server

Provides access to payment reminder functionality for LLMs through MCP protocol.
"""

from fastmcp import FastMCP
from typing import List, Dict, Any
import asyncio
from datetime import datetime, timedelta


# Initialize the MCP server
mcp = FastMCP(
    name="Payment Reminder MCP Server",
    instructions="Provides access to payment reminder functionality including overdue tracking, reminder generation, and client communication",
    version="1.0.0"
)


# Tools
@mcp.tool
def get_overdue_invoices(days_overdue: int = 0) -> List[Dict[str, Any]]:
    """
    Get invoices that are overdue by specified number of days or more
    """
    # In a real implementation, this would query a database
    # For simulation, returning sample overdue invoice data
    from datetime import datetime, timedelta
    
    base_date = datetime.now() - timedelta(days=10)  # Example: 10 days ago
    
    overdue_invoices = []
    for i in range(5):
        days_late = days_overdue + i*5  # Increment by 5 days for each invoice
        due_date = base_date - timedelta(days=days_late)
        
        overdue_invoices.append({
            "invoice_id": f"INV-{1000+i}",
            "client_name": f"Client {i+1}",
            "client_email": f"client{i+1}@example.com",
            "due_date": due_date.strftime("%Y-%m-%d"),
            "amount": 1200.0 + (i * 500.0),
            "days_overdue": days_late,
            "status": "overdue",
            "last_reminder_sent": "2023-06-01" if i % 2 == 0 else None
        })
    
    return overdue_invoices


@mcp.tool
def send_payment_reminder(
    invoice_id: str,
    client_email: str,
    reminder_level: int = 1,
    custom_message: str = None
) -> Dict[str, str]:
    """
    Send a payment reminder for an overdue invoice
    """
    level_messages = {
        1: "friendly reminder",
        2: "second reminder",
        3: "final reminder before late fees",
        4: "final notice before collection"
    }
    
    message = custom_message or f"This is a {level_messages.get(reminder_level, 'reminder')} for invoice {invoice_id}."
    
    # In a real implementation, this would send an actual email
    return {
        "status": "sent",
        "message": f"Payment reminder sent for invoice {invoice_id}",
        "reminder_level": reminder_level,
        "client_email": client_email,
        "sent_at": datetime.now().isoformat()
    }


@mcp.tool
def schedule_payment_reminder(
    invoice_id: str,
    delay_days: int,
    reminder_level: int = 1
) -> Dict[str, str]:
    """
    Schedule a payment reminder to be sent after a specified delay
    """
    scheduled_time = datetime.now() + timedelta(days=delay_days)
    
    return {
        "status": "scheduled",
        "message": f"Payment reminder scheduled for invoice {invoice_id}",
        "scheduled_time": scheduled_time.isoformat(),
        "delay_days": delay_days,
        "reminder_level": reminder_level
    }


@mcp.tool
def get_client_payment_history(client_name: str) -> List[Dict[str, Any]]:
    """
    Get payment history for a specific client
    """
    # In a real implementation, this would query actual payment data
    # For simulation, returning sample data
    history = []
    for i in range(6):
        history.append({
            "invoice_id": f"INV-{2000+i}",
            "issue_date": (datetime.now() - timedelta(days=(i+1)*30)).strftime("%Y-%m-%d"),
            "due_date": (datetime.now() - timedelta(days=(i+1)*30 - 2)).strftime("%Y-%m-%d"),
            "amount": 1500.0 + (i * 200.0),
            "status": "paid" if i < 4 else "overdue",
            "days_to_payment": 5 if i < 4 else 0,  # Only for paid invoices
            "payment_date": (datetime.now() - timedelta(days=(i+1)*30 - 5)).strftime("%Y-%m-%d") if i < 4 else None
        })
    
    return history


@mcp.tool
def calculate_late_fees(
    invoice_amount: float,
    days_overdue: int,
    daily_rate: float = 0.0005  # 0.05% daily
) -> Dict[str, float]:
    """
    Calculate late fees for an overdue invoice
    """
    late_fee = invoice_amount * daily_rate * days_overdue
    total_with_fees = invoice_amount + late_fee
    
    return {
        "original_amount": invoice_amount,
        "late_fee": round(late_fee, 2),
        "total_with_fees": round(total_with_fees, 2),
        "days_overdue": days_overdue,
        "daily_rate": daily_rate
    }


@mcp.tool
def update_payment_terms(
    invoice_id: str,
    new_due_date: str,
    late_fee_applied: bool = False
) -> Dict[str, str]:
    """
    Update payment terms for an invoice (e.g., extend due date)
    """
    return {
        "status": "updated",
        "message": f"Payment terms updated for invoice {invoice_id}",
        "new_due_date": new_due_date,
        "late_fee_applied": late_fee_applied
    }


@mcp.tool
def get_reminder_statistics() -> Dict[str, Any]:
    """
    Get statistics about payment reminders
    """
    # In a real implementation, this would aggregate actual data
    # For simulation, returning sample data
    return {
        "total_overdue_invoices": 24,
        "total_overdue_amount": 42500.0,
        "reminders_sent_this_week": 12,
        "payment_rate_after_reminder": 0.35,  # 35% of invoices get paid after reminder
        "avg_days_to_payment_after_reminder": 8.5,
        "most_reminded_clients": ["ACME Corp", "Globex Inc", "Wayne Enterprises"]
    }


@mcp.tool
def create_payment_plan(
    invoice_id: str,
    client_name: str,
    total_amount: float,
    installments: int,
    frequency: str = "monthly"
) -> Dict[str, Any]:
    """
    Create a payment plan for an overdue invoice
    """
    installment_amount = total_amount / installments
    
    plan = {
        "invoice_id": invoice_id,
        "client_name": client_name,
        "total_amount": total_amount,
        "installments": installments,
        "frequency": frequency,
        "installment_amount": round(installment_amount, 2),
        "plan_id": f"PP-{hash(invoice_id) % 10000}",
        "schedule": []
    }
    
    # Generate payment schedule
    start_date = datetime.now() + timedelta(days=7)  # Start in one week
    for i in range(installments):
        payment_date = start_date + timedelta(days=30*i if frequency == "monthly" else 7*i)
        plan["schedule"].append({
            "installment_number": i + 1,
            "due_date": payment_date.strftime("%Y-%m-%d"),
            "amount": round(installment_amount, 2),
            "status": "pending"
        })
    
    return plan


@mcp.tool
def get_payment_reminder_template(reminder_level: int) -> str:
    """
    Get a payment reminder template based on reminder level
    """
    templates = {
        1: "Dear Valued Customer, This is a courtesy reminder that your invoice is now overdue. We would appreciate payment at your earliest convenience. Thank you for your business.",
        2: "Dear Customer, This is a second reminder that your invoice remains outstanding. Please arrange payment as soon as possible to avoid any additional fees. We appreciate your prompt attention to this matter.",
        3: "Dear Customer, This is our final reminder before we begin charging late fees. Please remit payment immediately to avoid any additional charges. We value your business and hope to resolve this quickly.",
        4: "Dear Customer, This is our final notice before referring your account to a collection agency. Please contact us immediately to arrange payment and avoid further actions. We still hope to resolve this matter directly with you."
    }
    
    return templates.get(reminder_level, templates[1])


@mcp.tool
def track_reminder_effectiveness(reminder_level: int) -> Dict[str, float]:
    """
    Track effectiveness of different reminder levels
    """
    # In a real implementation, this would analyze historical data
    # For simulation, returning sample effectiveness rates
    effectiveness_rates = {
        1: 0.20,  # 20% pay after first reminder
        2: 0.35,  # 35% pay after second reminder
        3: 0.50,  # 50% pay after third reminder
        4: 0.65   # 65% pay after final notice
    }
    
    return {
        "reminder_level": reminder_level,
        "effectiveness_rate": effectiveness_rates.get(reminder_level, 0.10),
        "avg_days_to_payment": [12, 8, 5, 3][min(reminder_level-1, 3)]
    }


# Resources
@mcp.resource("http://payment-reminder-mcp-server.local/communication-templates")
def get_communication_templates() -> List[Dict[str, str]]:
    """
    Get available payment reminder communication templates
    """
    return [
        {
            "id": "standard_reminder",
            "name": "Standard Reminder",
            "content": "This is a friendly reminder that your invoice is now overdue. Please arrange payment at your earliest convenience."
        },
        {
            "id": "formal_demand",
            "name": "Formal Payment Demand",
            "content": "This letter serves as a formal demand for payment of the outstanding invoice. Immediate payment is required."
        },
        {
            "id": "payment_plan_offer",
            "name": "Payment Plan Offer",
            "content": "We understand financial difficulties may arise. We're happy to work with you on a payment plan to resolve your outstanding balance."
        }
    ]


@mcp.resource("http://payment-reminder-mcp-server.local/client-risk-assessment")
def get_client_risk_assessment(client_name: str) -> Dict[str, str]:
    """
    Get risk assessment for a client based on payment history
    """
    # In a real implementation, this would analyze actual payment data
    # For simulation, returning sample risk assessment
    return {
        "client_name": client_name,
        "risk_level": "medium",
        "payment_score": 7.2,  # Out of 10
        "avg_days_to_payment": 18,
        "payment_trend": "improving",
        "recommendation": "Standard follow-up procedures"
    }


@mcp.resource("http://payment-reminder-mcp-server.local/automated-workflows")
def get_automated_workflows() -> List[Dict[str, Any]]:
    """
    Get available automated payment reminder workflows
    """
    return [
        {
            "id": "standard_workflow",
            "name": "Standard Follow-up",
            "steps": [
                {"day": 1, "action": "Send friendly reminder"},
                {"day": 15, "action": "Send second reminder"},
                {"day": 30, "action": "Apply late fee"},
                {"day": 45, "action": "Final notice"}
            ]
        },
        {
            "id": "premium_workflow",
            "name": "Premium Client Follow-up",
            "steps": [
                {"day": 5, "action": "Personal call"},
                {"day": 15, "action": "Send reminder"},
                {"day": 25, "action": "Manager escalation"}
            ]
        }
    ]


# Prompts
@mcp.prompt("/payment-negotiation")
def payment_negotiation_prompt(
    client_financial_situation: str,
    overdue_amount: float,
    payment_history: str,
    context: str = ""
) -> str:
    """
    Generate a prompt for negotiating payment with a client
    """
    return f"""
Negotiate payment with client facing financial situation: {client_financial_situation}
Overdue amount: ${overdue_amount}
Payment history: {payment_history}
Context: {context}

Propose a mutually acceptable resolution while preserving the business relationship.
"""


@mcp.prompt("/payment-policy-review")
def policy_review_prompt(
    current_policy: str,
    client_feedback: List[str],
    industry_standards: List[str],
    context: str = ""
) -> str:
    """
    Generate a prompt for reviewing payment policies
    """
    return f"""
Review current payment policy: {current_policy}
Client feedback: {client_feedback}
Industry standards: {industry_standards}
Context: {context}

Suggest improvements to optimize payment collection while maintaining client relationships.
"""


@mcp.prompt("/collection-strategy")
def collection_strategy_prompt(
    account_age: int,
    amount_owed: float,
    client_classification: str,
    previous_attempts: int,
    context: str = ""
) -> str:
    """
    Generate a prompt for determining collection strategy
    """
    return f"""
Determine collection strategy for account:
- Days overdue: {account_age}
- Amount owed: ${amount_owed}
- Client classification: {client_classification}
- Previous collection attempts: {previous_attempts}
Context: {context}

Recommend appropriate next steps based on account specifics.
"""


@mcp.prompt("/client-retention-approach")
def client_retention_prompt(
    client_value: str,
    payment_issues: List[str],
    relationship_duration: str,
    context: str = ""
) -> str:
    """
    Generate a prompt for retaining clients with payment issues
    """
    return f"""
Develop approach to retain client with:
- Client value: {client_value}
- Payment issues: {payment_issues}
- Relationship duration: {relationship_duration}
Context: {context}

Balance payment collection with client retention strategies. 
"""


if __name__ == "__main__":
    # Use stdio transport for MCP server (proper MCP protocol communication)
    asyncio.run(mcp.run_stdio_async())