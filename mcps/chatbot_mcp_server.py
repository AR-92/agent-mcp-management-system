#!/usr/bin/env python3
"""
Chatbot MCP Server

Provides access to chatbot functionality for LLMs through MCP protocol.
"""

from fastmcp import FastMCP
from typing import List, Dict, Any
import asyncio
from datetime import datetime


# Initialize the MCP server
mcp = FastMCP(
    name="Chatbot MCP Server",
    instructions="Provides access to chatbot functionality including conversation management, intent recognition, and response generation",
    version="1.0.0"
)


# Tools
@mcp.tool
def process_user_input(
    user_id: str,
    message: str,
    conversation_context: Dict[str, Any] = None
) -> Dict[str, str]:
    """
    Process user input and generate an appropriate response
    """
    # In a real implementation, this would use NLP models for intent recognition
    # For simulation, returning sample responses based on keywords
    lower_msg = message.lower()
    
    if any(greeting in lower_msg for greeting in ["hello", "hi", "hey", "greetings"]):
        response = "Hello! How can I assist you today?"
    elif any(phrase in lower_msg for phrase in ["help", "support", "assistance"]):
        response = "I'm here to help! You can ask me questions about our products, services, or general information."
    elif any(phrase in lower_msg for phrase in ["thank", "thanks", "appreciate"]):
        response = "You're welcome! Is there anything else I can help with?"
    elif any(phrase in lower_msg for phrase in ["bye", "goodbye", "see you"]):
        response = "Goodbye! Feel free to reach out if you need any assistance."
    else:
        response = "Thanks for your message. How else can I assist you today?"
    
    return {
        "response": response,
        "user_id": user_id,
        "timestamp": datetime.now().isoformat(),
        "message_id": f"msg_{hash(message) % 10000}"
    }


@mcp.tool
def start_conversation(user_id: str, initial_context: Dict[str, Any] = None) -> Dict[str, str]:
    """
    Start a new conversation with a user
    """
    conversation_id = f"conv_{hash(user_id + datetime.now().isoformat()) % 10000}"
    
    return {
        "status": "started",
        "conversation_id": conversation_id,
        "user_id": user_id,
        "message": "New conversation started",
        "timestamp": datetime.now().isoformat()
    }


@mcp.tool
def get_conversation_history(conversation_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get the history of messages in a conversation
    """
    # In a real implementation, this would retrieve from a database
    # For simulation, returning sample conversation
    import random
    
    messages = []
    for i in range(min(limit, 5)):  # Return max 5 sample messages
        messages.append({
            "message_id": f"msg_{i}",
            "user_id": f"user_{hash(conversation_id) % 1000}",
            "role": "user" if i % 2 == 0 else "assistant",
            "content": f"Sample message {i} for conversation {conversation_id}",
            "timestamp": (datetime.now() - timedelta(minutes=(limit-i)*2)).isoformat()
        })
    
    return messages


@mcp.tool
def classify_intent(message: str) -> Dict[str, Any]:
    """
    Classify the intent of a user message
    """
    # In a real implementation, this would use NLP models for intent classification
    # For simulation, returning sample intents based on keywords
    lower_msg = message.lower()
    
    if any(word in lower_msg for word in ["product", "buy", "purchase", "order", "price", "cost"]):
        intent = "product_inquiry"
        confidence = 0.85
    elif any(word in lower_msg for word in ["support", "help", "issue", "problem", "bug", "error"]):
        intent = "support_request"
        confidence = 0.90
    elif any(word in lower_msg for word in ["return", "refund", "cancel", "change"]):
        intent = "return_request"
        confidence = 0.88
    elif any(word in lower_msg for word in ["account", "profile", "settings", "login", "password"]):
        intent = "account_inquiry"
        confidence = 0.82
    elif any(greeting in lower_msg for greeting in ["hello", "hi", "hey", "greetings"]):
        intent = "greeting"
        confidence = 0.95
    elif any(phrase in lower_msg for phrase in ["thank", "thanks", "appreciate"]):
        intent = "appreciation"
        confidence = 0.92
    else:
        intent = "general_inquiry"
        confidence = 0.70
    
    return {
        "intent": intent,
        "confidence": confidence,
        "original_message": message
    }


@mcp.tool
def generate_response(
    intent: str,
    user_context: Dict[str, Any],
    conversation_history: List[Dict[str, str]]
) -> str:
    """
    Generate an appropriate response based on intent and context
    """
    # In a real implementation, this would use more sophisticated response generation
    responses = {
        "greeting": "Hello! How can I assist you today?",
        "product_inquiry": "I'd be happy to help you with product information. Could you specify which product you're interested in?",
        "support_request": "I understand you need support. Let me connect you with our support team or help troubleshoot the issue.",
        "return_request": "I can help with your return request. Let me guide you through the return process.",
        "account_inquiry": "For account-related issues, I can help you access your account settings or reset your password.",
        "general_inquiry": "I'm here to help. Could you please provide more details about your question?"
    }
    
    return responses.get(intent, "I'm sorry, I didn't understand. Could you please rephrase?")


@mcp.tool
def update_user_profile(
    user_id: str,
    attributes: Dict[str, Any]
) -> Dict[str, str]:
    """
    Update user profile attributes
    """
    # In a real implementation, this would update a user database
    return {
        "status": "updated",
        "user_id": user_id,
        "updated_attributes": list(attributes.keys()),
        "message": f"Profile updated for user {user_id}"
    }


@mcp.tool
def get_user_profile(user_id: str) -> Dict[str, Any]:
    """
    Get user profile information
    """
    # In a real implementation, this would retrieve from a user database
    # For simulation, returning sample profile
    return {
        "user_id": user_id,
        "name": f"User {hash(user_id) % 1000}",
        "email": f"{user_id}@example.com",
        "join_date": "2023-01-01",
        "last_active": datetime.now().isoformat(),
        "preferences": {
            "communication_channel": "chat",
            "timezone": "UTC",
            "language": "en"
        },
        "interaction_count": 25,
        "satisfaction_score": 4.2
    }


@mcp.tool
def escalate_to_human(
    conversation_id: str,
    reason: str = "complex_issue"
) -> Dict[str, str]:
    """
    Escalate a conversation to human support
    """
    return {
        "status": "escalated",
        "conversation_id": conversation_id,
        "reason": reason,
        "message": f"Conversation {conversation_id} escalated to human agent",
        "estimated_wait_time": "2-3 minutes",
        "agent_assigned": f"agent_{hash(conversation_id) % 100}"
    }


@mcp.tool
def get_chatbot_analytics(
    date_from: str = None,
    date_to: str = None,
    metric: str = "all"
) -> Dict[str, Any]:
    """
    Get analytics about chatbot performance
    """
    # In a real implementation, this would query analytics database
    # For simulation, returning sample analytics
    return {
        "period": f"{date_from or '2023-01-01'} to {date_to or '2023-12-31'}",
        "metrics": {
            "total_conversations": 1250,
            "resolution_rate": 0.78,  # 78% of issues resolved by chatbot
            "avg_response_time_seconds": 2.4,
            "satisfaction_score": 4.1,
            "escalation_rate": 0.22,  # 22% of conversations escalated to humans
            "top_intents": [
                {"intent": "greeting", "count": 320},
                {"intent": "product_inquiry", "count": 280},
                {"intent": "support_request", "count": 195},
                {"intent": "account_inquiry", "count": 150},
                {"intent": "general_inquiry", "count": 305}
            ]
        }
    }


@mcp.tool
def train_model(
    training_data: List[Dict[str, str]],
    model_type: str = "intent_classification"
) -> Dict[str, Any]:
    """
    Train the chatbot model with new data
    """
    # In a real implementation, this would perform actual model training
    return {
        "status": "training_started",
        "model_type": model_type,
        "training_samples": len(training_data),
        "estimated_completion": "2023-06-15T10:30:00Z",
        "message": f"Training started for {model_type} model with {len(training_data)} samples"
    }


# Resources
@mcp.resource("http://chatbot-mcp-server.local/available-intents")
def get_available_intents() -> List[Dict[str, str]]:
    """
    Get list of available intents the chatbot can handle
    """
    return [
        {"id": "greeting", "description": "Handle greetings and pleasantries"},
        {"id": "product_inquiry", "description": "Answer questions about products and services"},
        {"id": "support_request", "description": "Handle technical support requests"},
        {"id": "order_status", "description": "Provide order status information"},
        {"id": "return_request", "description": "Process return requests"},
        {"id": "account_inquiry", "description": "Handle account-related questions"},
        {"id": "feedback", "description": "Collect customer feedback"},
        {"id": "general_inquiry", "description": "Handle general questions"}
    ]


@mcp.resource("http://chatbot-mcp-server.local/conversation-guidelines")
def get_conversation_guidelines() -> Dict[str, str]:
    """
    Get conversation guidelines for the chatbot
    """
    return {
        "title": "Chatbot Conversation Guidelines",
        "tone": "Professional, friendly, and helpful",
        "response_principles": [
            "Always acknowledge the user's concern",
            "Provide clear and concise answers",
            "Offer relevant follow-up options",
            "Escalate complex issues to human agents",
            "Respect user privacy and data security"
        ],
        "escalation_triggers": [
            "Expressed frustration or anger",
            "Complex technical issues",
            "Account security concerns",
            "Request for human agent",
            "Legal or compliance matters"
        ]
    }


@mcp.resource("http://chatbot-mcp-server.local/model-performance")
def get_model_performance() -> Dict[str, float]:
    """
    Get performance metrics for the NLP models
    """
    return {
        "intent_classification_accuracy": 0.92,
        "entity_extraction_f1_score": 0.87,
        "response_relevance_score": 0.89,
        "user_satisfaction_prediction": 0.85
    }


# Prompts
@mcp.prompt("/conversation-strategy")
def conversation_strategy_prompt(
    user_personality: str,
    conversation_goal: str,
    user_context: Dict[str, Any],
    context: str = ""
) -> str:
    """
    Generate a prompt for determining conversation strategy
    """
    return f"""
Determine conversation strategy for user with personality: {user_personality}
Goal: {conversation_goal}
User Context: {user_context}
Context: {context}

Adjust tone, approach, and information depth accordingly.
"""


@mcp.prompt("/escalation-decision")
def escalation_decision_prompt(
    conversation_context: str,
    user_emotion: str,
    issue_complexity: str,
    context: str = ""
) -> str:
    """
    Generate a prompt for deciding whether to escalate to a human agent
    """
    return f"""
Evaluate if conversation should be escalated based on:
Context: {conversation_context}
User emotion: {user_emotion}
Issue complexity: {issue_complexity}
Context: {context}

Determine if human intervention is needed.
"""


@mcp.prompt("/response-personalization")
def response_personalization_prompt(
    user_profile: Dict[str, Any],
    conversation_history: List[str],
    current_request: str,
    context: str = ""
) -> str:
    """
    Generate a prompt for personalizing responses based on user data
    """
    return f"""
Personalize response based on user profile: {user_profile}
Conversation history: {conversation_history}
Current request: {current_request}
Context: {context}

Create a tailored response that accounts for user preferences and history.
"""


@mcp.prompt("/chatbot-improvement")
def chatbot_improvement_prompt(
    common_issues: List[str],
    user_feedback: List[str],
    performance_metrics: Dict[str, float],
    context: str = ""
) -> str:
    """
    Generate a prompt for improving chatbot performance
    """
    return f"""
Suggest improvements for chatbot based on:
Common issues: {common_issues}
User feedback: {user_feedback}
Performance metrics: {performance_metrics}
Context: {context}

Focus on addressing gaps and enhancing user satisfaction.
"""


if __name__ == "__main__":
    # Use stdio transport for MCP server (proper MCP protocol communication)
    asyncio.run(mcp.run_stdio_async())