"""
File Operations Agent Example using Strands Agents SDK

This agent demonstrates file operations as agent tools, following the patterns 
described in the Strands documentation.
"""

from strandsagents import Agent
import os
import json
from datetime import datetime
from typing import Dict, Any, List, Union


def read_file_content(filepath: str) -> Dict[str, Union[str, List[str]]]:
    """
    Read the content of a file.
    
    Args:
        filepath: Path to the file to read
        
    Returns:
        A dictionary containing the file content or an error message.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.splitlines()
            return {
                "filepath": filepath,
                "content": content,
                "line_count": len(lines),
                "size": len(content)
            }
    except FileNotFoundError:
        return {"error": f"File not found: {filepath}"}
    except PermissionError:
        return {"error": f"Permission denied: {filepath}"}
    except Exception as e:
        return {"error": f"Error reading file: {str(e)}"}


def write_file_content(filepath: str, content: str) -> Dict[str, str]:
    """
    Write content to a file.
    
    Args:
        filepath: Path to the file to write
        content: Content to write to the file
        
    Returns:
        A dictionary confirming the write operation or an error message.
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return {
            "status": "success",
            "message": f"Content successfully written to {filepath}",
            "filepath": filepath
        }
    except PermissionError:
        return {"error": f"Permission denied: {filepath}"}
    except Exception as e:
        return {"error": f"Error writing file: {str(e)}"}


def list_directory_contents(directory_path: str = ".") -> Dict[str, Union[List[str], str]]:
    """
    List contents of a directory.
    
    Args:
        directory_path: Path to the directory to list (default is current directory)
        
    Returns:
        A dictionary containing the directory contents or an error message.
    """
    try:
        if not os.path.isdir(directory_path):
            return {"error": f"Path is not a directory: {directory_path}"}
        
        contents = os.listdir(directory_path)
        files = [item for item in contents if os.path.isfile(os.path.join(directory_path, item))]
        dirs = [item for item in contents if os.path.isdir(os.path.join(directory_path, item))]
        
        return {
            "directory": directory_path,
            "contents": contents,
            "files": files,
            "directories": dirs,
            "total_items": len(contents)
        }
    except PermissionError:
        return {"error": f"Permission denied: {directory_path}"}
    except Exception as e:
        return {"error": f"Error listing directory: {str(e)}"}


def get_file_info(filepath: str) -> Dict[str, Union[str, int, float]]:
    """
    Get information about a file.
    
    Args:
        filepath: Path to the file to get info for
        
    Returns:
        A dictionary containing file information or an error message.
    """
    try:
        if not os.path.exists(filepath):
            return {"error": f"File does not exist: {filepath}"}
        
        stat_info = os.stat(filepath)
        return {
            "filepath": filepath,
            "size_bytes": stat_info.st_size,
            "created": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
            "permissions": oct(stat_info.st_mode)[-3:],
        }
    except Exception as e:
        return {"error": f"Error getting file info: {str(e)}"}


# Create an agent specialized for file operations
agent = Agent(
    system_prompt="You are an assistant specialized in file operations. You can read/write files, list directory contents, and get file information. Always be careful with file operations and verify paths before performing operations. Be helpful and provide clear feedback."
)


def setup_file_operations_agent():
    """Set up the file operations agent with tools."""
    try:
        agent.add_tool(read_file_content)
        agent.add_tool(write_file_content)
        agent.add_tool(list_directory_contents)
        agent.add_tool(get_file_info)
        print("File operations tools successfully registered with the agent.")
        return True
    except AttributeError as e:
        print(f"Note: Tool registration API may vary depending on the specific Strands implementation. Error: {e}")
        return False


def run_file_agent(user_input: str):
    """
    Run the file operations agent with the given user input.
    
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
        return f"Simulated response: File operations agent. You requested: '{user_input}'."
    except Exception as e:
        return f"Error processing your request: {str(e)}"


def main():
    """Main function to run the file operations agent."""
    # Set up tools
    tools_setup = setup_file_operations_agent()
    
    print("File Operations Agent Example")
    print("This agent can perform file operations such as:")
    print("- Reading file contents (e.g., 'read the file at /path/to/file.txt')")
    print("- Writing to files (e.g., 'write hello world to /path/to/file.txt')")
    print("- Listing directory contents (e.g., 'list files in current directory')")
    print("- Getting file information (e.g., 'info for /path/to/file.txt')")
    print("Be careful to specify file paths correctly.")
    print("Type 'quit' to exit.\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Agent: Goodbye! Remember to be careful with file operations.")
            break
            
        response = run_file_agent(user_input)
        print(f"Agent: {response}\n")


if __name__ == "__main__":
    main()