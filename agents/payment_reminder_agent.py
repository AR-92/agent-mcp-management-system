"""
Payment Reminder Agent using Strands Agents SDK

This agent uses the Payment Reminder MCP to manage overdue invoices and payment tracking.
"""

from strandsagents import Agent
from typing import Dict, Any, List
import json
from datetime import datetime, timedelta


def get_overdue_invoices(days_overdue: int = 0) -> List[Dict[str, Any]]:
    """
    Get invoices that are overdue by specified number of days or more.
    
    Args:
        days_overdue: Minimum number of days overdue (0 for all overdue invoices)
        
    Returns:
        List of dictionaries containing overdue invoice information
    """
    # This would connect to the Payment Reminder MCP server in a real implementation
    return [
        {
            "id": f"inv_{i}",
            "invoice_number": f"INV-{datetime.now().strftime('%Y%m')}-{i:03d}",
            "client_name": f"Client {i}",
            "client_email": f"client{i}@example.com",
            "amount": 1250.00 + (i * 100),
            "currency": "USD",
            "issue_date": (datetime.now() - timedelta(days=45 + i*5)).isoformat(),
            "due_date": (datetime.now() - timedelta(days=15 + i*3)).isoformat(),
            "days_overdue": (datetime.now() - datetime.fromisoformat((datetime.now() - timedelta(days=15 + i*3)).isoformat())).days,
            "status": "overdue",
            "payment_terms": "Net 30",
            "line_items": [
                {"description": "Service", "amount": 1000.00},
                {"description": "Tax", "amount": 250.00}
            ]
        }
        for i in range(1, 6)
        if (datetime.now() - datetime.fromisoformat((datetime.now() - timedelta(days=15 + i*3)).isoformat())).days >= days_overdue
    ]


def send_payment_reminder(
    invoice_id: str,
    client_email: str,
    reminder_level: int = 1,
    custom_message: str = None
) -> Dict[str, Any]:
    """
    Send a payment reminder for an overdue invoice.
    
    Args:
        invoice_id: ID of the invoice to send reminder for
        client_email: Email address of the client
        reminder_level: Level of the reminder (1=first reminder, 2=second, etc.)
        custom_message: Optional custom message to include in the reminder
        
    Returns:
        Dictionary containing the payment reminder result
    """
    # This would connect to the Payment Reminder MCP server in a real implementation
    level_messages = {
        1: "First reminder",
        2: "Second reminder", 
        3: "Final notice",
        4: "Legal notice"
    }
    
    return {
        "status": "sent",
        "reminder_id": f"rem_{invoice_id}_{reminder_level}",
        "invoice_id": invoice_id,
        "client_email": client_email,
        "reminder_level": reminder_level,
        "reminder_type": level_messages.get(reminder_level, f"Level {reminder_level} reminder"),
        "message": f"Payment reminder {reminder_level} sent for invoice {invoice_id}",
        "scheduled_followup": (datetime.now() + timedelta(days=7)).isoformat() if reminder_level < 3 else None
    }


def create_payment_plan(
    invoice_id: str,
    client_id: str,
    total_amount: float,
    installments: int,
    start_date: str,
    frequency: str = "monthly"  # weekly, biweekly, monthly
) -> Dict[str, Any]:
    """
    Create a payment plan for an overdue invoice.
    
    Args:
        invoice_id: ID of the invoice to create plan for
        client_id: ID of the client
        total_amount: Total amount of the invoice
        installments: Number of installments for the plan
        start_date: Start date for the payment plan
        frequency: Frequency of payments
        
    Returns:
        Dictionary containing the payment plan information
    """
    # This would connect to the Payment Reminder MCP server in a real implementation
    installment_amount = round(total_amount / installments, 2)
    
    plan_id = f"plan_{invoice_id}_{client_id}"
    
    return {
        "status": "created",
        "plan_id": plan_id,
        "invoice_id": invoice_id,
        "client_id": client_id,
        "total_amount": total_amount,
        "installments": installments,
        "installment_amount": installment_amount,
        "frequency": frequency,
        "start_date": start_date,
        "next_payment_date": start_date,
        "message": f"Payment plan created for invoice {invoice_id} with {installments} installments"
    }


def update_invoice_status(
    invoice_id: str,
    new_status: str,
    notes: str = None
) -> Dict[str, Any]:
    """
    Update the status of an invoice.
    
    Args:
        invoice_id: ID of the invoice to update
        new_status: New status (e.g., 'paid', 'partial', 'overdue', 'disputed', 'written-off')
        notes: Optional notes about the status change
        
    Returns:
        Dictionary containing the invoice status update result
    """
    # This would connect to the Payment Reminder MCP server in a real implementation
    return {
        "status": "updated",
        "invoice_id": invoice_id,
        "previous_status": "overdue",
        "new_status": new_status,
        "timestamp": datetime.now().isoformat(),
        "notes": notes,
        "message": f"Invoice {invoice_id} status updated to {new_status}"
    }


def generate_payment_report(
    start_date: str,
    end_date: str,
    client_id: str = None
) -> Dict[str, Any]:
    """
    Generate a payment report for a date range.
    
    Args:
        start_date: Start date for the report
        end_date: End date for the report
        client_id: Optional client ID to filter by
        
    Returns:
        Dictionary containing the payment report
    """
    # This would connect to the Payment Reminder MCP server in a real implementation
    return {
        "date_range": {"start": start_date, "end": end_date},
        "report_type": "Payment Activity Report",
        "filters": {"client_id": client_id} if client_id else {},
        "summary": {
            "total_invoices": 45,
            "paid_invoices": 32,
            "overdue_invoices": 10,
            "disputed_invoices": 3,
            "total_amount_billed": 87500.00,
            "total_amount_paid": 62500.00,
            "outstanding_amount": 25000.00,
            "average_days_to_payment": 28.5,
            "collection_rate": 0.714  # 71.4%
        },
        "top_delinquent_customers": [
            {"name": "ABC Corp", "amount_owed": 8500.00, "days_overdue": 52},
            {"name": "XYZ Ltd", "amount_owed": 6200.00, "days_overdue": 48},
            {"name": "123 Inc", "amount_owed": 4100.00, "days_overdue": 35}
        ],
        "message": "Payment report generated successfully"
    }


def schedule_payment_reminder_campaign(
    invoice_ids: List[str],
    reminder_template: str,
    send_date: str,
    priority: str = "normal"  # low, normal, high
) -> Dict[str, Any]:
    """
    Schedule a payment reminder campaign for multiple invoices.
    
    Args:
        invoice_ids: List of invoice IDs to include in campaign
        reminder_template: Template to use for the reminders
        send_date: Date to send the reminders
        priority: Priority level for the campaign
        
    Returns:
        Dictionary containing the campaign scheduling result
    """
    # This would connect to the Payment Reminder MCP server in a real implementation
    campaign_id = f"camp_{hash(str(invoice_ids)) % 10000}"
    
    return {
        "status": "scheduled",
        "campaign_id": campaign_id,
        "invoice_count": len(invoice_ids),
        "reminder_template": reminder_template,
        "scheduled_date": send_date,
        "priority": priority,
        "message": f"Payment reminder campaign scheduled for {len(invoice_ids)} invoices"
    }


def get_invoice_aging_report(
    as_of_date: str = None
) -> Dict[str, Any]:
    """
    Get an aging report showing how long invoices have been outstanding.
    
    Args:
        as_of_date: Date to calculate aging from (defaults to today)
        
    Returns:
        Dictionary containing the aging report
    """
    # This would connect to the Payment Reminder MCP server in a real implementation
    as_of_date = as_of_date or datetime.now().isoformat()
    
    return {
        "as_of_date": as_of_date,
        "report_type": "Invoice Aging Report",
        "aging_buckets": {
            "current": {"count": 15, "amount": 22500.00},  # 0-30 days
            "1_to_30_days": {"count": 8, "amount": 12000.00},  # 1-30 days overdue
            "31_to_60_days": {"count": 5, "amount": 8500.00},  # 31-60 days overdue
            "61_to_90_days": {"count": 3, "amount": 5200.00},  # 61-90 days overdue
            "90_plus_days": {"count": 2, "amount": 3800.00}  # 90+ days overdue
        },
        "total_overdue": {
            "count": 18,
            "amount": 29500.00
        },
        "message": "Aging report generated successfully"
    }


def process_payment(
    invoice_id: str,
    amount_paid: float,
    payment_method: str,
    transaction_id: str = None,
    notes: str = None
) -> Dict[str, Any]:
    """
    Process a payment for an invoice.
    
    Args:
        invoice_id: ID of the invoice being paid
        amount_paid: Amount being paid
        payment_method: Method of payment (e.g., 'check', 'wire', 'credit_card', 'ach')
        transaction_id: Optional transaction ID from payment processor
        notes: Optional notes about the payment
        
    Returns:
        Dictionary containing the payment processing result
    """
    # This would connect to the Payment Reminder MCP server in a real implementation
    return {
        "status": "processed",
        "payment_id": f"pay_{invoice_id}_{hash(str(amount_paid)) % 10000}",
        "invoice_id": invoice_id,
        "amount_paid": amount_paid,
        "payment_method": payment_method,
        "transaction_id": transaction_id,
        "remaining_balance": max(0, 1500.00 - amount_paid),  # Example remaining balance
        "payment_date": datetime.now().isoformat(),
        "message": f"Payment of ${amount_paid} processed for invoice {invoice_id}"
    }


def escalate_invoice(
    invoice_id: str,
    escalation_level: int,
    reason: str,
    assign_to: str = None
) -> Dict[str, Any]:
    """
    Escalate an overdue invoice to a higher level of collection.
    
    Args:
        invoice_id: ID of the invoice to escalate
        escalation_level: Level to escalate to (2=manager, 3=legal, etc.)
        reason: Reason for the escalation
        assign_to: Optional user to assign to the escalated case
        
    Returns:
        Dictionary containing the escalation result
    """
    # This would connect to the Payment Reminder MCP server in a real implementation
    level_names = {2: "Manager Review", 3: "Legal Review", 4: "Collections Agency"}
    
    return {
        "status": "escalated",
        "invoice_id": invoice_id,
        "previous_level": "1",
        "escalation_level": escalation_level,
        "level_name": level_names.get(escalation_level, f"Level {escalation_level}"),
        "reason": reason,
        "assigned_to": assign_to,
        "timestamp": datetime.now().isoformat(),
        "message": f"Invoice {invoice_id} escalated to {level_names.get(escalation_level, f'Level {escalation_level}')}"
    }


def create_dunning_letter(
    invoice_id: str,
    client_address: Dict[str, str],
    letter_type: str = "standard",  # standard, certified, legal
    include_penalty: bool = False,
    penalty_amount: float = 0.0
) -> Dict[str, Any]:
    """
    Create a dunning letter for an overdue invoice.
    
    Args:
        invoice_id: ID of the invoice
        client_address: Dictionary containing client address information
        letter_type: Type of letter ('standard', 'certified', 'legal')
        include_penalty: Whether to include a penalty fee
        penalty_amount: Amount of penalty to add if included
        
    Returns:
        Dictionary containing the dunning letter creation result
    """
    # This would connect to the Payment Reminder MCP server in a real implementation
    letter_id = f"letter_{invoice_id}_{letter_type}"
    
    return {
        "status": "created",
        "letter_id": letter_id,
        "invoice_id": invoice_id,
        "letter_type": letter_type,
        "client_address": client_address,
        "include_penalty": include_penalty,
        "penalty_amount": penalty_amount if include_penalty else 0.0,
        "message": f"Dunning letter of type '{letter_type}' created for invoice {invoice_id}"
    }


# Create a Payment Reminder agent
agent = Agent(
    system_prompt="You are a payment reminder assistant. You can identify overdue invoices, send payment reminders, create payment plans, update invoice statuses, generate reports, and manage collections processes. When asked about payment operations, provide detailed information about payment statuses, aging reports, and collection strategies. Follow best practices for professional and compliant payment collection."
)


def setup_payment_agent():
    """Set up the Payment Reminder agent with tools."""
    try:
        agent.add_tool(get_overdue_invoices)
        agent.add_tool(send_payment_reminder)
        agent.add_tool(create_payment_plan)
        agent.add_tool(update_invoice_status)
        agent.add_tool(generate_payment_report)
        agent.add_tool(schedule_payment_reminder_campaign)
        agent.add_tool(get_invoice_aging_report)
        agent.add_tool(process_payment)
        agent.add_tool(escalate_invoice)
        agent.add_tool(create_dunning_letter)
        print("Payment reminder tools successfully registered with the agent.")
        return True
    except AttributeError as e:
        print(f"Note: Tool registration API may vary depending on the specific Strands implementation. Error: {e}")
        return False


def run_payment_agent(user_input: str):
    """
    Run the Payment Reminder agent with the given user input.
    
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
        return f"Simulated response: Payment reminder agent. You requested: '{user_input}'"
    except Exception as e:
        return f"Error processing your request: {str(e)}"


def main():
    """Main function to run the Payment Reminder agent."""
    # Set up tools
    tools_setup = setup_payment_agent()
    
    print("Payment Reminder Agent")
    print("This agent can:")
    print("- Get overdue invoices (e.g., 'show invoices overdue by 30 days')")
    print("- Send payment reminders (e.g., 'send reminder for invoice 123')")
    print("- Create payment plans (e.g., 'create payment plan for invoice 123')")
    print("- Update invoice statuses (e.g., 'mark invoice 123 as paid')")
    print("- Generate payment reports (e.g., 'show payment report for last month')")
    print("- Schedule reminder campaigns (e.g., 'schedule reminders for 5 invoices')")
    print("- Get aging reports (e.g., 'show aging report')")
    print("- Process payments (e.g., 'process payment for invoice 123')")
    print("- Escalate invoices (e.g., 'escalate invoice 123 to manager level')")
    print("- Create dunning letters (e.g., 'create dunning letter for invoice 123')")
    print("Type 'quit' to exit.\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Agent: Goodbye! Payment reminder assistant signing off.")
            break
            
        response = run_payment_agent(user_input)
        print(f"Agent: {response}\n")


if __name__ == "__main__":
    main()