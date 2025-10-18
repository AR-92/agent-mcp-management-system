"""
Payment Reminder Agent using Strands Agents SDK

This agent uses the Payment Reminder MCP to manage related operations.
"""

from strands import Agent
from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters
from strands.tools.mcp import MCPClient


def create_stdio_transport():
    """Create a stdio transport to connect to the Payment Reminder MCP server"""
    return stdio_client(StdioServerParameters(command="python", args=["-u", "/home/rana/Documents/agent-mcp-managnet-system/mcps/payment_reminder_mcp_server.py"]))

def run_payment_reminder_mcp_server_agent(user_input: str):
    """
    Run the Payment Reminder agent with the given user input.
    
    Args:
        user_input: The input from the user
        
    Returns:
        The agent's response
    """
    # Create an MCP client
    stdio_mcp_client = MCPClient(create_stdio_transport)
    
    with stdio_mcp_client:
        try:
            tools = stdio_mcp_client.list_tools_sync()
            agent = Agent(
                system_prompt="You are a Payment Reminder assistant. You can perform operations related to payment reminder. When asked about payment reminder operations, provide detailed information and perform requested actions.",
                tools=tools
            )
            print("Payment Reminder tools successfully registered with the agent.")
        except Exception as e:
            print(f"Error connecting to MCP server: {e}")
            # Fallback to basic agent without tools
            agent = Agent(
                system_prompt="You are a Payment Reminder assistant. You can perform operations related to payment reminder. When asked about payment reminder operations, provide detailed information and perform requested actions."
            )
    
        try:
            response = agent.run(user_input)
            return response
        except ImportError:
            # If strands is not available, return a simulated response
            return f"Simulated response: Payment Reminder agent. You requested: '{user_input}'"
        except Exception as e:
            return f"Error processing your request: {str(e)}"


def main():
    """Main function to run the Payment Reminder agent."""
    
    print("Payment Reminder Agent")
    print("This agent can:")
    print("- Perform operations related to payment reminder")
    print("- Handle various tasks based on available MCP tools")
    print("Type 'quit' to exit.\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print(f"Agent: Goodbye! Payment Reminder assistant signing off.")
            break
            
        response = run_payment_reminder_mcp_server_agent(user_input)
        print(f"Agent: {response}\n")


if __name__ == "__main__":
    main()
