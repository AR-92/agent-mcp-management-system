#!/usr/bin/env python3
"""
Invoice MCP Server

Provides access to invoice creation and management functionality for LLMs through MCP protocol.
"""

from fastmcp import FastMCP
from typing import List, Dict, Any
import asyncio
from datetime import datetime, timedelta


# Initialize the MCP server
mcp = FastMCP(
    name="Invoice MCP Server",
    instructions="Provides access to invoice creation and management functionality including generation, tracking, and payment processing",
    version="1.0.0"
)


# Tools
@mcp.tool
def create_invoice(
    client_name: str,
    client_email: str,
    client_address: str,
    items: List[Dict[str, Any]],
    invoice_date: str = None,
    due_date: str = None,
    currency: str = "USD",
    tax_rate: float = 0.0,
    notes: str = ""
) -> Dict[str, Any]:
    """
    Create a new invoice
    """
    if invoice_date is None:
        invoice_date = datetime.now().strftime("%Y-%m-%d")
    if due_date is None:
        # Default to 30 days from invoice date
        due_date_obj = datetime.strptime(invoice_date, "%Y-%m-%d") + timedelta(days=30)
        due_date = due_date_obj.strftime("%Y-%m-%d")
    
    # Calculate totals
    subtotal = sum(item['quantity'] * item['unit_price'] for item in items)
    tax_amount = subtotal * tax_rate
    total = subtotal + tax_amount
    
    invoice = {
        "invoice_id": f"INV-{datetime.now().strftime('%Y%m')}-{hash(client_name) % 10000:04d}",
        "client_name": client_name,
        "client_email": client_email,
        "client_address": client_address,
        "items": items,
        "invoice_date": invoice_date,
        "due_date": due_date,
        "currency": currency,
        "subtotal": round(subtotal, 2),
        "tax_rate": tax_rate,
        "tax_amount": round(tax_amount, 2),
        "total": round(total, 2),
        "status": "draft",
        "notes": notes,
        "created_at": datetime.now().isoformat()
    }
    
    return invoice


@mcp.tool
def get_invoice(invoice_id: str) -> Dict[str, Any]:
    """
    Get details of a specific invoice
    """
    # In a real implementation, this would retrieve from a database
    # For simulation, returning sample invoice data
    return {
        "invoice_id": invoice_id,
        "client_name": "ACME Corporation",
        "client_email": "billing@acme.com",
        "client_address": "123 Business Ave, City, State 12345",
        "items": [
            {"description": "Web Development Services", "quantity": 40, "unit_price": 100.0, "total": 4000.0},
            {"description": "UI/UX Design", "quantity": 15, "unit_price": 80.0, "total": 1200.0}
        ],
        "invoice_date": "2023-06-01",
        "due_date": "2023-07-01",
        "currency": "USD",
        "subtotal": 5200.0,
        "tax_rate": 0.08,
        "tax_amount": 416.0,
        "total": 5616.0,
        "status": "sent",
        "notes": "Thank you for your business!",
        "sent_date": "2023-06-01T10:30:00Z",
        "payment_status": "pending"
    }


@mcp.tool
def list_invoices(
    status: str = None,
    client_name: str = None,
    date_from: str = None,
    date_to: str = None
) -> List[Dict[str, Any]]:
    """
    List invoices with optional filters
    """
    # In a real implementation, this would query a database
    # For simulation, returning sample invoice data
    invoices = [
        {
            "invoice_id": "INV-202306-0001",
            "client_name": "ACME Corporation",
            "total": 5616.0,
            "status": "paid",
            "invoice_date": "2023-06-01",
            "due_date": "2023-07-01",
            "payment_date": "2023-06-15"
        },
        {
            "invoice_id": "INV-202306-0002",
            "client_name": "Globex Inc",
            "total": 3200.0,
            "status": "sent",
            "invoice_date": "2023-06-05",
            "due_date": "2023-07-05",
            "payment_date": None
        },
        {
            "invoice_id": "INV-202306-0003",
            "client_name": "Wayne Enterprises",
            "total": 8950.0,
            "status": "overdue",
            "invoice_date": "2023-05-01",
            "due_date": "2023-06-01",
            "payment_date": None
        }
    ]
    
    # Apply filters if specified
    if status:
        invoices = [inv for inv in invoices if inv['status'] == status]
    if client_name:
        invoices = [inv for inv in invoices if client_name.lower() in inv['client_name'].lower()]
    if date_from:
        invoices = [inv for inv in invoices if inv['invoice_date'] >= date_from]
    if date_to:
        invoices = [inv for inv in invoices if inv['invoice_date'] <= date_to]
    
    return invoices


@mcp.tool
def update_invoice_status(invoice_id: str, status: str) -> Dict[str, str]:
    """
    Update the status of an invoice
    """
    valid_statuses = ["draft", "sent", "paid", "overdue", "cancelled"]
    
    if status not in valid_statuses:
        return {
            "status": "error",
            "message": f"Invalid status. Valid options: {valid_statuses}"
        }
    
    return {
        "status": "success",
        "message": f"Invoice {invoice_id} status updated to {status}"
    }


@mcp.tool
def send_invoice(invoice_id: str) -> Dict[str, str]:
    """
    Send an invoice to the client
    """
    # In a real implementation, this would send an actual email
    return {
        "status": "sent",
        "message": f"Invoice {invoice_id} sent to client",
        "sent_date": datetime.now().isoformat()
    }


@mcp.tool
def mark_invoice_paid(invoice_id: str, payment_date: str = None) -> Dict[str, str]:
    """
    Mark an invoice as paid
    """
    if not payment_date:
        payment_date = datetime.now().strftime("%Y-%m-%d")
    
    return {
        "status": "paid",
        "message": f"Invoice {invoice_id} marked as paid",
        "payment_date": payment_date
    }


@mcp.tool
def calculate_invoice_totals(items: List[Dict[str, Any]], tax_rate: float = 0.0) -> Dict[str, float]:
    """
    Calculate totals for invoice items
    """
    subtotal = sum(item['quantity'] * item['unit_price'] for item in items)
    tax_amount = subtotal * tax_rate
    total = subtotal + tax_amount
    
    return {
        "subtotal": round(subtotal, 2),
        "tax_amount": round(tax_amount, 2),
        "total": round(total, 2)
    }


@mcp.tool
def generate_invoice_pdf(invoice_id: str) -> Dict[str, str]:
    """
    Generate a PDF version of an invoice
    """
    # In a real implementation, this would generate an actual PDF
    return {
        "status": "generated",
        "message": f"PDF generated for invoice {invoice_id}",
        "file_path": f"/invoices/{invoice_id}.pdf",
        "download_url": f"https://example.com/invoices/{invoice_id}/download"
    }


@mcp.tool
def add_payment_record(
    invoice_id: str,
    amount: float,
    payment_method: str,
    transaction_id: str = None
) -> Dict[str, str]:
    """
    Add a payment record to an invoice
    """
    return {
        "status": "success",
        "message": f"Payment of ${amount} recorded for invoice {invoice_id}",
        "payment_method": payment_method,
        "transaction_id": transaction_id or f"txn_{hash(invoice_id) % 10000}"
    }


@mcp.tool
def get_client_outstanding_balance(client_name: str) -> Dict[str, float]:
    """
    Get the outstanding balance for a client
    """
    # In a real implementation, this would query actual invoice data
    # For simulation, returning sample data
    return {
        "client_name": client_name,
        "outstanding_invoices": 3,
        "outstanding_amount": 12150.0,
        "overdue_amount": 8950.0,
        "current_amount": 3200.0
    }


# Resources
@mcp.resource("http://invoice-mcp-server.local/invoice-templates")
def get_invoice_templates() -> List[Dict[str, str]]:
    """
    Get available invoice templates
    """
    return [
        {"id": "standard", "name": "Standard Template", "description": "Simple and professional"},
        {"id": "minimal", "name": "Minimal Template", "description": "Clean and modern design"},
        {"id": "detailed", "name": "Detailed Template", "description": "Includes more sections and information"},
        {"id": "freelancer", "name": "Freelancer Template", "description": "Designed for individual contractors"}
    ]


@mcp.resource("http://invoice-mcp-server.local/tax-rates")
def get_tax_rates() -> Dict[str, float]:
    """
    Get common tax rates by region
    """
    return {
        "US-Federal": 0.0,
        "US-CA": 0.0725,
        "US-NY": 0.08,
        "US-TX": 0.0625,
        "US-FL": 0.06,
        "EU-VAT": 0.20,
        "UK-VAT": 0.20,
        "CA-GST": 0.05
    }


@mcp.resource("http://invoice-mcp-server.local/payment-methods")
def get_payment_methods() -> List[Dict[str, str]]:
    """
    Get supported payment methods
    """
    return [
        {"id": "ach", "name": "ACH Transfer", "description": "Automated Clearing House"},
        {"id": "wire", "name": "Wire Transfer", "description": "Electronic funds transfer"},
        {"id": "check", "name": "Check", "description": "Physical check payment"},
        {"id": "credit_card", "name": "Credit Card", "description": "Major credit cards accepted"},
        {"id": "paypal", "name": "PayPal", "description": "PayPal business account"},
        {"id": "stripe", "name": "Stripe", "description": "Online payment processing"}
    ]


# Prompts
@mcp.prompt("/invoice-dispute-resolution")
def invoice_dispute_prompt(
    invoice_id: str,
    client_concerns: List[str],
    invoice_amount: float,
    context: str = ""
) -> str:
    """
    Generate a prompt for resolving invoice disputes
    """
    return f"""
Resolve dispute for invoice {invoice_id} with amount ${invoice_amount}
Client concerns: {client_concerns}
Context: {context}

Address concerns professionally and find an acceptable resolution.
"""


@mcp.prompt("/payment-follow-up")
def payment_follow_up_prompt(
    invoice_id: str,
    days_overdue: int,
    client_history: str,
    context: str = ""
) -> str:
    """
    Generate a prompt for following up on overdue payments
    """
    return f"""
Handle payment follow-up for invoice {invoice_id} (overdue by {days_overdue} days)
Client history: {client_history}
Context: {context}

Determine appropriate follow-up approach and timeline.
"""


@mcp.prompt("/invoice-terms-negotiation")
def terms_negotiation_prompt(
    client_request: str,
    standard_terms: Dict[str, Any],
    business_impact: str,
    context: str = ""
) -> str:
    """
    Generate a prompt for negotiating invoice terms
    """
    return f"""
Negotiate invoice terms based on client request: {client_request}
Standard terms: {standard_terms}
Business impact: {business_impact}
Context: {context}

Balance client needs with business requirements.
"""


@mcp.prompt("/pricing-strategy-review")
def pricing_strategy_prompt(
    invoice_data: List[Dict[str, Any]],
    payment_patterns: Dict[str, Any],
    competitive_factors: List[str],
    context: str = ""
) -> str:
    """
    Generate a prompt for reviewing pricing strategy based on invoice data
    """
    return f"""
Review pricing strategy based on:
- Invoice data: {invoice_data}
- Payment patterns: {payment_patterns}
- Competitive factors: {competitive_factors}
Context: {context}

Analyze payment behavior and pricing effectiveness.
"""


if __name__ == "__main__":
    # Use stdio transport for MCP server (proper MCP protocol communication)
    asyncio.run(mcp.run_stdio_async())