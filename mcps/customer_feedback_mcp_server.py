#!/usr/bin/env python3
"""
Customer Feedback MCP Server

Provides access to customer feedback management functionality for LLMs through MCP protocol.
"""

from fastmcp import FastMCP
from typing import List, Dict, Any
import asyncio
from datetime import datetime


# Initialize the MCP server
mcp = FastMCP(
    name="Customer Feedback MCP Server",
    instructions="Provides access to customer feedback management functionality including collection, analysis, and response generation",
    version="1.0.0"
)


# Tools
@mcp.tool
def collect_feedback(
    customer_id: str,
    rating: int,
    comment: str,
    category: str = "general",
    interaction_id: str = None
) -> Dict[str, str]:
    """
    Collect and store customer feedback
    """
    if not 1 <= rating <= 5:
        return {"status": "error", "message": "Rating must be between 1 and 5"}
    
    feedback_id = f"fb_{hash(customer_id + comment) % 100000}"
    
    # In a real implementation, this would store in a database
    return {
        "status": "success",
        "feedback_id": feedback_id,
        "message": "Feedback collected successfully",
        "customer_id": customer_id,
        "rating": rating,
        "category": category
    }


@mcp.tool
def get_feedback_by_customer(customer_id: str) -> List[Dict[str, Any]]:
    """
    Get all feedback from a specific customer
    """
    # In a real implementation, this would query a database
    # For simulation, returning sample feedback
    return [
        {
            "feedback_id": f"fb_{i}",
            "customer_id": customer_id,
            "rating": 4,
            "comment": f"Sample feedback comment {i} from customer {customer_id}",
            "category": "service" if i % 2 == 0 else "product",
            "date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
            "resolved": i % 3 != 0
        }
        for i in range(1, 6)
    ]


@mcp.tool
def get_feedback_by_category(category: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get feedback in a specific category
    """
    # In a real implementation, this would query a database
    # For simulation, returning sample feedback
    return [
        {
            "feedback_id": f"fb_{category}_{i}",
            "customer_id": f"customer_{i}",
            "rating": 3 if i % 4 == 0 else 4 if i % 3 == 0 else 5,
            "comment": f"Feedback about {category} - comment {i}",
            "category": category,
            "date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
            "resolved": i % 2 == 0
        }
        for i in range(1, min(limit+1, 8))
    ]


@mcp.tool
def analyze_sentiment(feedback_text: str) -> Dict[str, Any]:
    """
    Analyze the sentiment of feedback text
    """
    # In a real implementation, this would use NLP models
    # For simulation, using simple keyword-based analysis
    positive_words = ["good", "great", "excellent", "amazing", "love", "wonderful", "fantastic", "perfect"]
    negative_words = ["bad", "terrible", "awful", "hate", "poor", "disappointed", "frustrated", "angry"]
    
    text_lower = feedback_text.lower()
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    if positive_count > negative_count:
        sentiment = "positive"
        score = 0.7 + (positive_count - negative_count) * 0.1
    elif negative_count > positive_count:
        sentiment = "negative"
        score = 0.3 - (negative_count - positive_count) * 0.1
    else:
        sentiment = "neutral"
        score = 0.5
    
    # Ensure score is between 0 and 1
    score = max(0.0, min(1.0, score))
    
    return {
        "sentiment": sentiment,
        "confidence": score,
        "text": feedback_text
    }


@mcp.tool
def search_feedback(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Search feedback containing specific terms
    """
    # In a real implementation, this would query a database with full-text search
    # For simulation, returning sample matching results
    return [
        {
            "feedback_id": f"search_{i}",
            "customer_id": f"customer_{i}",
            "rating": 4,
            "comment": f"Customer mentioned {query} in their feedback - comment {i}",
            "category": "service",
            "date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
            "relevance": 0.8 - (i * 0.1)
        }
        for i in range(1, min(limit+1, 6))
    ]


@mcp.tool
def get_feedback_trends(days: int = 30) -> Dict[str, Any]:
    """
    Get trends in feedback over the specified number of days
    """
    # In a real implementation, this would query a database
    # For simulation, returning sample trend data
    import random
    
    trend_data = []
    start_date = datetime.now() - timedelta(days=days)
    
    for i in range(days):
        date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
        daily_data = {
            "date": date,
            "total_feedback": random.randint(5, 25),
            "average_rating": round(random.uniform(3.5, 4.5), 2),
            "positive_count": random.randint(3, 18),
            "negative_count": random.randint(0, 7)
        }
        trend_data.append(daily_data)
    
    return {
        "period": f"Last {days} days",
        "trend_data": trend_data,
        "overall_average_rating": round(sum(day["average_rating"] for day in trend_data) / len(trend_data), 2),
        "total_feedback": sum(day["total_feedback"] for day in trend_data)
    }


@mcp.tool
def categorize_feedback(comment: str) -> Dict[str, Any]:
    """
    Automatically categorize feedback based on content
    """
    # In a real implementation, this would use NLP models
    # For simulation, using keyword-based categorization
    categories_keywords = {
        "product_quality": ["product", "quality", "defective", "broken", "material", "design"],
        "service": ["service", "customer service", "staff", "helpful", "response", "support"],
        "pricing": ["price", "expensive", "cost", "value", "affordable", "worth", "overpriced"],
        "delivery": ["delivery", "shipping", "arrived", "late", "package", "tracking"],
        "website": ["website", "interface", "navigation", "app", "platform", "user experience"],
        "billing": ["billing", "charge", "invoice", "payment", "refund", "account"]
    }
    
    comment_lower = comment.lower()
    detected_categories = []
    
    for category, keywords in categories_keywords.items():
        if any(keyword in comment_lower for keyword in keywords):
            detected_categories.append(category)
    
    # Default to general if no specific category detected
    if not detected_categories:
        detected_categories = ["general"]
    
    return {
        "detected_categories": detected_categories,
        "comment": comment
    }


@mcp.tool
def generate_response_to_feedback(
    feedback_id: str,
    feedback_text: str,
    customer_satisfaction: str = "neutral"
) -> Dict[str, str]:
    """
    Generate an appropriate response to customer feedback
    """
    # In a real implementation, this would use more sophisticated logic
    # For simulation, using basic rules based on satisfaction level
    if customer_satisfaction == "negative":
        response = f"Thank you for your feedback regarding '{feedback_text[:50]}...'. We're sorry to hear about your experience and are looking into this matter. A team member will follow up with you shortly."
    elif customer_satisfaction == "positive":
        response = f"Thank you for your positive feedback! We're glad to hear about your experience with '{feedback_text[:50]}...'. We appreciate your business."
    else:  # neutral
        response = f"Thank you for your feedback regarding '{feedback_text[:50]}...'. We appreciate you taking the time to share your thoughts with us."
    
    return {
        "feedback_id": feedback_id,
        "response": response,
        "response_type": "auto-generated"
    }


@mcp.tool
def get_feedback_analytics() -> Dict[str, Any]:
    """
    Get comprehensive analytics about customer feedback
    """
    # In a real implementation, this would query analytics database
    # For simulation, returning sample analytics
    return {
        "total_feedback": 1250,
        "average_rating": 4.2,
        "satisfaction_rate": 0.78,  # 78% of feedback is positive
        "most_common_categories": [
            {"category": "service", "count": 350},
            {"category": "product_quality", "count": 280},
            {"category": "pricing", "count": 195},
            {"category": "delivery", "count": 150},
            {"category": "website", "count": 125}
        ],
        "trending_topics": [
            {"topic": "shipping speed", "mentions": 85, "sentiment": "mixed"},
            {"topic": "product durability", "mentions": 65, "sentiment": "positive"},
            {"topic": "customer support", "mentions": 120, "sentiment": "positive"}
        ],
        "resolution_rate": 0.85  # 85% of feedback issues resolved
    }


@mcp.tool
def mark_feedback_resolved(feedback_id: str, resolution_notes: str = "") -> Dict[str, str]:
    """
    Mark a feedback item as resolved
    """
    return {
        "status": "resolved",
        "feedback_id": feedback_id,
        "message": f"Feedback {feedback_id} marked as resolved",
        "resolution_notes": resolution_notes
    }


# Resources
@mcp.resource("http://customer-feedback-mcp-server.local/feedback-categories")
def get_feedback_categories() -> List[Dict[str, str]]:
    """
    Get available feedback categories
    """
    return [
        {"id": "product_quality", "name": "Product Quality", "description": "Feedback about product quality and features"},
        {"id": "service", "name": "Customer Service", "description": "Feedback about support and service interactions"},
        {"id": "pricing", "name": "Pricing", "description": "Feedback about cost and value"},
        {"id": "delivery", "name": "Delivery/Shipping", "description": "Feedback about shipping and delivery experience"},
        {"id": "website", "name": "Website/App", "description": "Feedback about digital experience"},
        {"id": "billing", "name": "Billing", "description": "Feedback about invoices and payment processing"},
        {"id": "general", "name": "General", "description": "General feedback without specific category"}
    ]


@mcp.resource("http://customer-feedback-mcp-server.local/response-templates")
def get_response_templates() -> List[Dict[str, str]]:
    """
    Get available response templates for different feedback types
    """
    return [
        {
            "id": "positive_acknowledgment",
            "name": "Positive Feedback Acknowledgment",
            "template": "Thank you for your positive feedback! We're delighted to hear about your experience. Your satisfaction is our top priority."
        },
        {
            "id": "negative_apology",
            "name": "Negative Feedback Apology",
            "template": "We apologize for the inconvenience you experienced. We take your feedback seriously and are committed to addressing this issue."
        },
        {
            "id": "neutral_acknowledgment",
            "name": "Neutral Feedback Acknowledgment",
            "template": "Thank you for sharing your thoughts with us. We appreciate your feedback and will use it to improve our service."
        },
        {
            "id": "inquiry_response",
            "name": "Inquiry Response",
            "template": "Thank you for reaching out. We've received your feedback and will review it with our team to determine how we can improve."
        }
    ]


@mcp.resource("http://customer-feedback-mcp-server.local/nps-data")
def get_nps_data() -> Dict[str, Any]:
    """
    Get Net Promoter Score data
    """
    return {
        "nps_score": 62,
        "promoters_percentage": 65,
        "passives_percentage": 20,
        "detractors_percentage": 15,
        "survey_responses": 420,
        "trend": "improving",
        "period": "last_30_days"
    }


# Prompts
@mcp.prompt("/feedback-response-strategy")
def feedback_response_prompt(
    feedback_sentiment: str,
    feedback_category: str,
    customer_history: str,
    context: str = ""
) -> str:
    """
    Generate a prompt for developing a feedback response strategy
    """
    return f"""
Develop a response strategy for customer feedback that is {feedback_sentiment} in the {feedback_category} category
Customer history: {customer_history}
Context: {context}

Consider the customer's value, relationship history, and appropriate response tone.
"""


@mcp.prompt("/feedback-analysis")
def feedback_analysis_prompt(
    feedback_collection: List[str],
    business_goals: List[str],
    priority_areas: List[str],
    context: str = ""
) -> str:
    """
    Generate a prompt for analyzing a collection of feedback
    """
    return f"""
Analyze these customer feedback items: {feedback_collection}
Business goals: {business_goals}
Priority areas: {priority_areas}
Context: {context}

Identify patterns, issues, and opportunities for improvement.
"""


@mcp.prompt("/sentiment-intervention")
def sentiment_intervention_prompt(
    negative_feedback: str,
    customer_value: str,
    issue_severity: str,
    context: str = ""
) -> str:
    """
    Generate a prompt for determining appropriate intervention for negative sentiment
    """
    return f"""
Determine appropriate intervention for negative feedback: {negative_feedback}
Customer value: {customer_value}
Issue severity: {issue_severity}
Context: {context}

Suggest specific actions to address concerns and recover the relationship.
"""


@mcp.prompt("/feedback-classification")
def feedback_classification_prompt(
    feedback_text: str,
    existing_categories: List[str],
    classification_rules: List[str],
    context: str = ""
) -> str:
    """
    Generate a prompt for classifying feedback into appropriate categories
    """
    return f"""
Classify the following feedback: {feedback_text}
Existing categories: {existing_categories}
Classification rules: {classification_rules}
Context: {context}

Assign to one or more relevant categories based on the content.
"""


if __name__ == "__main__":
    # Use stdio transport for MCP server (proper MCP protocol communication)
    asyncio.run(mcp.run_stdio_async())