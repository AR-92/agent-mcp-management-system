"""
Chatbot Agent using Strands Agents SDK

This agent uses the Chatbot MCP to manage conversation management, intent recognition, 
and response generation.
"""

from strandsagents import Agent
from typing import Dict, Any, List
import json
from datetime import datetime, timedelta


def process_user_input(
    user_id: str,
    message: str,
    conversation_context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Process user input in a chatbot conversation.
    
    Args:
        user_id: Unique identifier for the user
        message: The message from the user
        conversation_context: Context from the ongoing conversation
        
    Returns:
        Dictionary containing the chatbot's response and updated context
    """
    # This would connect to the Chatbot MCP server in a real implementation
    return {
        "response": f"I received your message: '{message}'. How can I assist you today?",
        "intent": "greeting" if any(word in message.lower() for word in ["hello", "hi", "hey"]) else "general_query",
        "confidence_score": 0.85,
        "action_required": False,
        "follow_up_questions": [
            "Is there anything specific I can help you with?",
            "Do you have any questions?"
        ],
        "updated_context": {
            "last_message": message,
            "last_intent": "greeting",
            "conversation_turns": (conversation_context or {}).get("conversation_turns", 0) + 1
        }
    }


def create_intent(
    intent_name: str,
    utterances: List[str],
    response_templates: List[str],
    parameters: List[Dict[str, Any]] = None,
    context_triggers: List[str] = None
) -> Dict[str, Any]:
    """
    Create a new intent for the chatbot.
    
    Args:
        intent_name: Name of the intent
        utterances: Sample phrases that trigger this intent
        response_templates: Templates for responses to this intent
        parameters: Parameters to extract from user input
        context_triggers: Context values that make this intent more likely
        
    Returns:
        Dictionary containing the intent creation result
    """
    # This would connect to the Chatbot MCP server in a real implementation
    intent_id = f"intent_{hash(intent_name) % 10000}"
    
    return {
        "status": "created",
        "intent_id": intent_id,
        "intent_name": intent_name,
        "utterances_count": len(utterances),
        "response_templates_count": len(response_templates),
        "parameters_count": len(parameters) if parameters else 0,
        "message": f"Intent '{intent_name}' created successfully"
    }


def list_intents(
    include_training_status: bool = True,
    filter_by_status: str = None,  # active, inactive, training
    max_results: int = 50
) -> List[Dict[str, Any]]:
    """
    List available intents in the chatbot.
    
    Args:
        include_training_status: Whether to include training status for each intent
        filter_by_status: Filter by status ('active', 'inactive', 'training')
        max_results: Maximum number of results to return
        
    Returns:
        List of dictionaries containing intent information
    """
    # This would connect to the Chatbot MCP server in a real implementation
    sample_intents = [
        {
            "id": f"intent_{i}",
            "name": f"intent_{i}",
            "description": f"Sample intent {i} for demonstration",
            "utterances_count": 15 + (i * 3),
            "response_templates_count": 3 + (i % 2),
            "status": "active" if i % 4 != 0 else "inactive",
            "created_at": (datetime.now() - timedelta(days=i*5)).isoformat(),
            "last_trained_at": (datetime.now() - timedelta(days=i*2)).isoformat(),
            "training_status": "completed" if i % 4 != 0 else "pending",
            "confidence_threshold": 0.7 + (i % 10) * 0.01
        }
        for i in range(1, max_results + 1)
    ]
    
    if filter_by_status:
        sample_intents = [intent for intent in sample_intents if intent["status"] == filter_by_status]
        
    return sample_intents


def update_intent(
    intent_id: str,
    updates: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Update an existing intent in the chatbot.
    
    Args:
        intent_id: ID of the intent to update
        updates: Dictionary containing fields to update
        
    Returns:
        Dictionary containing the intent update result
    """
    # This would connect to the Chatbot MCP server in a real implementation
    return {
        "status": "updated",
        "intent_id": intent_id,
        "updated_fields": list(updates.keys()),
        "timestamp": datetime.now().isoformat(),
        "message": f"Intent {intent_id} updated successfully"
    }


def train_chatbot_model(
    intents_to_train: List[str] = None,
    training_data_source: str = "internal",
    validation_split: float = 0.2
) -> Dict[str, Any]:
    """
    Train the chatbot's NLP model.
    
    Args:
        intents_to_train: Specific intents to retrain (None for all)
        training_data_source: Source of training data ('internal', 'external', 'mixed')
        validation_split: Fraction of data to use for validation
        
    Returns:
        Dictionary containing the training result
    """
    # This would connect to the Chatbot MCP server in a real implementation
    return {
        "status": "started",
        "training_id": f"train_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "intents_trained": intents_to_train or ["all"],
        "training_data_source": training_data_source,
        "validation_split": validation_split,
        "estimated_completion": "30-60 minutes",
        "message": "Model training initiated"
    }


def get_conversation_analytics(
    user_id: str = None,
    date_from: str = None,
    date_to: str = None,
    include_user_details: bool = False
) -> Dict[str, Any]:
    """
    Get analytics for chatbot conversations.
    
    Args:
        user_id: Optional user ID to filter analytics for
        date_from: Start date for analytics
        date_to: End date for analytics
        include_user_details: Whether to include user-specific details
        
    Returns:
        Dictionary containing conversation analytics
    """
    # This would connect to the Chatbot MCP server in a real implementation
    return {
        "date_range": {
            "start": date_from or (datetime.now() - timedelta(days=30)).isoformat(),
            "end": date_to or datetime.now().isoformat()
        },
        "analytics": {
            "total_conversations": 1250 if not user_id else 25,
            "total_messages": 4850 if not user_id else 86,
            "avg_conversation_length": 3.9 if not user_id else 3.4,
            "resolved_without_transfer": 0.78 if not user_id else 0.84,  # 78% or 84% resolved
            "avg_response_time_seconds": 1.2,
            "peak_hours": [
                {"hour": 10, "conversations": 180},
                {"hour": 14, "conversations": 165},
                {"hour": 15, "conversations": 158}
            ],
            "intents_distribution": [
                {"intent": "greeting", "count": 420},
                {"intent": "faq", "count": 320},
                {"intent": "support", "count": 280},
                {"intent": "booking", "count": 150}
            ],
            "satisfaction_score": 4.2 if not user_id else 4.5  # out of 5
        },
        "user_specific_data": {
            "user_id": user_id,
            "total_interactions": 86,
            "preferred_topics": ["support", "faq"],
            "satisfaction_trend": [4.0, 4.2, 4.5],
            "last_interaction": (datetime.now() - timedelta(hours=2)).isoformat()
        } if user_id and include_user_details else None,
        "message": f"Analytics retrieved for {'specific user' if user_id else 'all users'}"
    }


def create_response_template(
    template_name: str,
    template_content: str,
    variables: List[str],
    fallback_template: str = None
) -> Dict[str, Any]:
    """
    Create a response template for chatbot responses.
    
    Args:
        template_name: Name of the template
        template_content: Content of the template with variable placeholders
        variables: List of variables that can be inserted into the template
        fallback_template: Template to use if the primary one fails
        
    Returns:
        Dictionary containing the response template creation result
    """
    # This would connect to the Chatbot MCP server in a real implementation
    template_id = f"tmpl_{hash(template_name) % 10000}"
    
    return {
        "status": "created",
        "template_id": template_id,
        "template_name": template_name,
        "variables_count": len(variables),
        "has_fallback": fallback_template is not None,
        "message": f"Response template '{template_name}' created successfully"
    }


def get_intent_accuracy(
    intent_id: str,
    date_from: str = None,
    date_to: str = None
) -> Dict[str, Any]:
    """
    Get accuracy metrics for a specific intent.
    
    Args:
        intent_id: ID of the intent to analyze
        date_from: Start date for accuracy calculation
        date_to: End date for accuracy calculation
        
    Returns:
        Dictionary containing intent accuracy metrics
    """
    # This would connect to the Chatbot MCP server in a real implementation
    return {
        "intent_id": intent_id,
        "accuracy_metrics": {
            "precision": 0.92,
            "recall": 0.88,
            "f1_score": 0.90,
            "confidence_threshold": 0.7,
            "true_positives": 320,
            "false_positives": 25,
            "false_negatives": 42,
            "total_evaluations": 400,
            "accuracy_rate": 0.91  # 91% accurate
        },
        "date_range": {
            "start": date_from or (datetime.now() - timedelta(days=7)).isoformat(),
            "end": date_to or datetime.now().isoformat()
        },
        "improvement_suggestions": [
            "Add more training phrases",
            "Adjust confidence threshold"
        ],
        "message": f"Accuracy metrics retrieved for intent {intent_id}"
    }


def simulate_conversation(
    user_inputs: List[str],
    initial_context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Simulate a conversation with the chatbot.
    
    Args:
        user_inputs: List of user inputs to simulate
        initial_context: Initial context to start the simulation
        
    Returns:
        Dictionary containing the simulated conversation
    """
    # This would connect to the Chatbot MCP server in a real implementation
    simulation_id = f"sim_{hash(str(user_inputs)) % 10000}"
    
    simulated_exchanges = []
    for i, user_input in enumerate(user_inputs):
        simulated_exchanges.append({
            "turn": i + 1,
            "user_input": user_input,
            "bot_response": f"Simulated response to: {user_input}",
            "detected_intent": "general_query",
            "confidence": 0.85,
            "context_after_response": {"turn": i + 1, "last_intent": "general_query"}
        })
    
    return {
        "simulation_id": simulation_id,
        "initial_context": initial_context or {},
        "exchanges": simulated_exchanges,
        "simulation_results": {
            "total_turns": len(user_inputs),
            "intent_detection_accuracy": 0.89,
            "response_relevance_score": 4.2  # out of 5
        },
        "message": f"Conversation simulation completed with {len(user_inputs)} exchanges"
    }


def create_custom_action(
    action_name: str,
    function_name: str,
    parameters: Dict[str, Any],
    description: str = ""
) -> Dict[str, Any]:
    """
    Create a custom action for the chatbot.
    
    Args:
        action_name: Name of the action
        function_name: Name of the function to execute
        parameters: Parameters required by the function
        description: Description of what the action does
        
    Returns:
        Dictionary containing the custom action creation result
    """
    # This would connect to the Chatbot MCP server in a real implementation
    action_id = f"action_{hash(action_name) % 10000}"
    
    return {
        "status": "created",
        "action_id": action_id,
        "action_name": action_name,
        "function_name": function_name,
        "parameters_count": len(parameters),
        "description": description,
        "message": f"Custom action '{action_name}' created successfully"
    }


def get_chatbot_performance(
    date_from: str = None,
    date_to: str = None
) -> Dict[str, Any]:
    """
    Get overall performance metrics for the chatbot.
    
    Args:
        date_from: Start date for performance calculation
        date_to: End date for performance calculation
        
    Returns:
        Dictionary containing chatbot performance metrics
    """
    # This would connect to the Chatbot MCP server in a real implementation
    return {
        "date_range": {
            "start": date_from or (datetime.now() - timedelta(days=30)).isoformat(),
            "end": date_to or datetime.now().isoformat()
        },
        "performance_metrics": {
            "conversations_count": 1250,
            "messages_count": 4850,
            "avg_response_time_ms": 1200,
            "intent_detection_accuracy": 0.89,
            "user_satisfaction": 4.2,  # out of 5
            "tasks_completed": 965,
            "tasks_completed_rate": 0.77,  # 77% of tasks completed
            "escalations_to_human": 125,   # Number of times escalated
            "escalation_rate": 0.10,       # 10% escalation rate
            "active_users": 420,
            "return_users": 280,           # Users who came back
            "return_rate": 0.67            # 67% return rate
        },
        "trends": [
            {
                "date": (datetime.now() - timedelta(days=i)).date().isoformat(),
                "conversations": 45 - i,
                "satisfaction": round(4.2 + (i * 0.01), 2),
                "response_time_ms": 1200 - (i * 10)
            }
            for i in range(7)
        ],
        "message": "Chatbot performance metrics retrieved"
    }


# Create a Chatbot agent
agent = Agent(
    system_prompt="You are a Chatbot assistant. You can process user inputs, create and manage intents, train models, generate analytics, create response templates, test intent accuracy, simulate conversations, create custom actions, and report performance. When asked about chatbot operations, provide detailed information about conversation flows, intent handling, and performance metrics."
)


def setup_chatbot_agent():
    """Set up the Chatbot agent with tools."""
    try:
        agent.add_tool(process_user_input)
        agent.add_tool(create_intent)
        agent.add_tool(list_intents)
        agent.add_tool(update_intent)
        agent.add_tool(train_chatbot_model)
        agent.add_tool(get_conversation_analytics)
        agent.add_tool(create_response_template)
        agent.add_tool(get_intent_accuracy)
        agent.add_tool(simulate_conversation)
        agent.add_tool(create_custom_action)
        agent.add_tool(get_chatbot_performance)
        print("Chatbot tools successfully registered with the agent.")
        return True
    except AttributeError as e:
        print(f"Note: Tool registration API may vary depending on the specific Strands implementation. Error: {e}")
        return False


def run_chatbot_agent(user_input: str):
    """
    Run the Chatbot agent with the given user input.
    
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
        return f"Simulated response: Chatbot agent. You requested: '{user_input}'"
    except Exception as e:
        return f"Error processing your request: {str(e)}"


def main():
    """Main function to run the Chatbot agent."""
    # Set up tools
    tools_setup = setup_chatbot_agent()
    
    print("Chatbot Agent")
    print("This agent can:")
    print("- Process user input (e.g., 'process the message hello')")
    print("- Create intents (e.g., 'create a greeting intent')")
    print("- List intents (e.g., 'show all intents')")
    print("- Update intents (e.g., 'update intent 123')")
    print("- Train the chatbot model (e.g., 'start training')")
    print("- Get conversation analytics (e.g., 'show conversation analytics')")
    print("- Create response templates (e.g., 'create a response template')")
    print("- Check intent accuracy (e.g., 'show accuracy for intent 123')")
    print("- Simulate conversations (e.g., 'simulate conversation with hello, how are you')")
    print("- Create custom actions (e.g., 'create custom action for booking')")
    print("- Get performance metrics (e.g., 'show performance report')")
    print("Type 'quit' to exit.\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Agent: Goodbye! Chatbot assistant signing off.")
            break
            
        response = run_chatbot_agent(user_input)
        print(f"Agent: {response}\n")


if __name__ == "__main__":
    main()