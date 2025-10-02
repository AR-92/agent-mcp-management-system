"""
Simple Agent Example using Strands Agents SDK

This is a basic agent implementation that demonstrates:
- Creating a simple agent
- Adding basic tools
- Running the agent
"""

from strandsagents import Agent
import json
from datetime import datetime
from typing import Dict, Any, Union


# Define tools as functions with proper type hints and docstrings
def get_current_time() -> Dict[str, str]:
    """
    Get the current time.
    
    Returns:
        A dictionary containing the current time in ISO format.
    """
    return {"current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}


def simple_calculator(operation: str, a: float, b: float) -> Dict[str, Union[float, str]]:
    """
    A simple calculator that performs basic arithmetic operations.
    
    Args:
        operation: The operation to perform. One of 'add', 'subtract', 'multiply', 'divide'.
        a: The first operand.
        b: The second operand.
        
    Returns:
        A dictionary containing the result of the calculation or an error message.
    """
    try:
        if operation.lower() == "add":
            result = a + b
        elif operation.lower() == "subtract":
            result = a - b
        elif operation.lower() == "multiply":
            result = a * b
        elif operation.lower() == "divide":
            if b == 0:
                return {"error": "Cannot divide by zero"}
            result = a / b
        else:
            return {"error": f"Unknown operation: {operation}. Use add, subtract, multiply, or divide."}
        
        return {"result": result, "operation_performed": f"{a} {operation} {b} = {result}"}
    except Exception as e:
        return {"error": f"Calculation error: {str(e)}"}


def echo_message(message: str) -> Dict[str, str]:
    """
    Echo back the provided message.
    
    Args:
        message: The message to echo back.
        
    Returns:
        A dictionary containing the original message.
    """
    return {"echo": message}


def get_system_info() -> Dict[str, str]:
    """
    Get basic system information.
    
    Returns:
        A dictionary containing basic system information.
    """
    import platform
    return {
        "system": platform.system(),
        "node": platform.node(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor()
    }


# Create the agent with a system prompt
agent = Agent(
    system_prompt="You are a helpful assistant. You can provide the current time, perform calculations, echo messages, or provide system information. Always be friendly and concise in your responses. Use the appropriate tool when needed."
)


def setup_tools():
    """Set up tools for the agent."""
    try:
        # Add tools to the agent - this follows the API reference pattern
        # The exact syntax may depend on the specific implementation of Strands
        agent.add_tool(get_current_time)
        agent.add_tool(simple_calculator)
        agent.add_tool(echo_message)
        agent.add_tool(get_system_info)
        print("Tools successfully registered with the agent.")
        return True
    except AttributeError as e:
        print(f"Note: Tool registration API may vary depending on the specific Strands implementation. Error: {e}")
        return False


def run_simple_agent(user_input: str):
    """
    Run the simple agent with the given user input.
    
    Args:
        user_input: The input from the user.
        
    Returns:
        The agent's response.
    """
    try:
        # Try to run the agent with the provided input
        response = agent.run(user_input)
        return response
    except ImportError:
        # If strandsagents is not available, return a simulated response
        return f"Simulated response: I'm a simple agent. You said: '{user_input}'. Current time is {datetime.now().strftime('%H:%M:%S')}."
    except Exception as e:
        # For any other error, return an error response
        return f"Error processing your request: {str(e)}"


def main():
    """Main function to run the simple agent in CLI mode."""
    # Set up tools
    tools_setup = setup_tools()
    
    print("Simple Agent Example")
    print("This agent can:")
    print("- Tell you the current time (ask 'What time is it?' or 'current time')")
    print("- Perform calculations (e.g., 'add 5 and 3', 'multiply 4 and 6')")
    print("- Echo messages (e.g., 'echo hello world')")
    print("- Get system information (ask 'system info' or 'system information')")
    print("Type 'quit' to exit.\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Agent: Goodbye!")
            break
            
        response = run_simple_agent(user_input)
        print(f"Agent: {response}\n")


if __name__ == "__main__":
    main()