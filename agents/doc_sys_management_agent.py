"""
Documentation & System Management Agent using Strands Agents SDK

This agent combines Dokploy, Google Drive, Google Docs, Google Sheets, 
and Meta MCPs to provide documentation and system management capabilities.
"""

from strandsagents import Agent
from typing import Dict, Any, List
import json
from datetime import datetime, timedelta


def list_applications() -> List[Dict[str, Any]]:
    """
    List applications managed by Dokploy.
    
    Returns:
        List of dictionaries containing application information
    """
    # This would connect to the Dokploy MCP server in a real implementation
    return [
        {
            "id": f"app_{i}",
            "name": f"Application {i}",
            "status": "running" if i % 4 != 0 else "stopped",
            "containers": 3 if i % 2 == 0 else 1,
            "memory_usage": f"{2.4 if i % 2 == 0 else 1.2}GB",
            "cpu_usage": f"{45 if i % 2 == 0 else 30}%",
            "last_deployed": (datetime.now() - timedelta(days=i)).isoformat(),
            "health_status": "healthy" if i % 3 != 0 else "warning",
            "environment": "production" if i % 2 == 0 else "staging"
        }
        for i in range(1, 8)
    ]


def deploy_application(
    app_id: str,
    new_image: str,
    environment: str = "production"
) -> Dict[str, Any]:
    """
    Deploy a new version of an application.
    
    Args:
        app_id: ID of the application to deploy
        new_image: New Docker image to deploy
        environment: Environment to deploy to (staging/production)
        
    Returns:
        Dictionary containing the deployment result
    """
    # This would connect to the Dokploy MCP server in a real implementation
    return {
        "status": "initiated",
        "deployment_id": f"deploy_{app_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "app_id": app_id,
        "new_image": new_image,
        "environment": environment,
        "estimated_completion": "5-10 minutes",
        "message": f"Deployment of {new_image} to {environment} initiated for {app_id}"
    }


def list_files(
    folder_id: str = "root", 
    file_type: str = None, 
    query: str = None, 
    max_results: int = 20
) -> List[Dict[str, Any]]:
    """
    List files in Google Drive.
    
    Args:
        folder_id: ID of the folder to list files from
        file_type: Type of files to filter (e.g., document, spreadsheet, pdf)
        query: Search query to filter files
        max_results: Maximum number of files to return
        
    Returns:
        List of dictionaries containing file information
    """
    # This would connect to the Google Drive MCP server in a real implementation
    return [
        {
            "id": f"file_{i}",
            "name": f"Document {i}.docx" if i % 3 == 0 else f"Spreadsheet {i}.xlsx" if i % 3 == 1 else f"Presentation {i}.pptx",
            "mimeType": "application/vnd.google-apps.document" if i % 3 == 0 else "application/vnd.google-apps.spreadsheet" if i % 3 == 1 else "application/vnd.google-apps.presentation",
            "size": f"{(i * 100) % 5000}KB",
            "modifiedTime": (datetime.now() - timedelta(days=i)).isoformat(),
            "owners": [{"displayName": "User Name", "emailAddress": "user@example.com"}],
            "owners_count": 1,
            "viewers_count": i % 5,
            "editors_count": 1
        }
        for i in range(1, max_results + 1)
    ]


def create_document(
    title: str,
    content: str = "",
    folder_id: str = "root",
    document_type: str = "document"  # document, spreadsheet, presentation
) -> Dict[str, Any]:
    """
    Create a new document in Google Drive.
    
    Args:
        title: Title of the document
        content: Initial content of the document
        folder_id: Folder to create the document in
        document_type: Type of document to create
        
    Returns:
        Dictionary containing the creation result
    """
    # This would connect to the Google Docs or Google Sheets MCP server in a real implementation
    doc_id = f"doc_{hash(title) % 10000}"
    
    return {
        "status": "created",
        "document_id": doc_id,
        "title": title,
        "document_type": document_type,
        "folder_id": folder_id,
        "document_url": f"https://docs.google.com/{'document' if document_type == 'document' else 'spreadsheets' if document_type == 'spreadsheet' else 'presentation'}/d/{doc_id}",
        "message": f"{document_type.capitalize()} '{title}' created successfully"
    }


def get_document_content(
    document_id: str
) -> Dict[str, Any]:
    """
    Get the content of a document.
    
    Args:
        document_id: ID of the document to retrieve content from
        
    Returns:
        Dictionary containing the document content
    """
    # This would connect to the Google Docs MCP server in a real implementation
    return {
        "document_id": document_id,
        "title": f"Document {document_id}",
        "content": f"This is the content of document {document_id}. It contains important information related to the topic.",
        "last_modified": (datetime.now() - timedelta(hours=1)).isoformat(),
        "version": "1.0",
        "word_count": 1250,
        "paragraph_count": 8
    }


def list_spreadsheets(
    query: str = None, 
    max_results: int = 20
) -> List[Dict[str, Any]]:
    """
    List Google Sheets spreadsheets.
    
    Args:
        query: Optional search query to filter spreadsheets
        max_results: Maximum number of results to return
        
    Returns:
        List of dictionaries containing spreadsheet information
    """
    # This would connect to the Google Sheets MCP server in a real implementation
    return [
        {
            "id": f"sheet_{i}",
            "name": f"Spreadsheet {i}" if not query else f"{query} Spreadsheet {i}",
            "description": f"Sample spreadsheet {i} for testing",
            "owners": [{"name": "User Name", "email": "user@example.com"}],
            "modifiedTime": (datetime.now() - timedelta(days=i)).isoformat(),
            "createdTime": (datetime.now() - timedelta(days=i*2)).isoformat(),
            "lastModifier": {"name": "User Name", "email": "user@example.com"},
            "sheetsCount": i % 5 + 1,  # 1-5 sheets
            "size": f"{(i * 100) % 5000}KB"
        }
        for i in range(1, max_results + 1)
    ]


def read_sheet_data(
    spreadsheet_id: str, 
    sheet_name: str = None,
    range: str = None,
    headers: bool = True
) -> Dict[str, Any]:
    """
    Read data from a Google Sheet.
    
    Args:
        spreadsheet_id: ID of the spreadsheet to read from
        sheet_name: Name of the sheet to read from (optional)
        range: A1 notation range to read (optional)
        headers: Whether to include headers in the result
        
    Returns:
        Dictionary containing the sheet data
    """
    # This would connect to the Google Sheets MCP server in a real implementation
    sample_data = [
        {
            "name": "John Doe",
            "email": "john@example.com",
            "department": "Engineering",
            "salary": 75000,
            "hire_date": "2020-05-15"
        },
        {
            "name": "Jane Smith", 
            "email": "jane@example.com",
            "department": "Marketing",
            "salary": 68000,
            "hire_date": "2019-11-22"
        },
        {
            "name": "Robert Johnson",
            "email": "robert@example.com",
            "department": "Sales",
            "salary": 72000,
            "hire_date": "2021-03-10"
        }
    ]
    
    return {
        "spreadsheet_id": spreadsheet_id,
        "sheet_name": sheet_name or "Sheet1",
        "range": range or "A1:E100",
        "headers": headers,
        "data": sample_data,
        "rows_count": len(sample_data),
        "columns_count": len(sample_data[0]) if sample_data else 0
    }


def update_document(
    document_id: str,
    content: str,
    append: bool = False
) -> Dict[str, Any]:
    """
    Update the content of a document.
    
    Args:
        document_id: ID of the document to update
        content: Content to update the document with
        append: Whether to append to existing content or replace it
        
    Returns:
        Dictionary containing the update result
    """
    # This would connect to the Google Docs MCP server in a real implementation
    return {
        "status": "updated",
        "document_id": document_id,
        "action": "appended" if append else "replaced",
        "characters_changed": len(content),
        "timestamp": datetime.now().isoformat(),
        "message": f"Document {document_id} {'appended to' if append else 'updated'} successfully"
    }


def share_document(
    document_id: str,
    email_addresses: List[str],
    role: str = "reader",  # reader, writer, commenter
    send_notification: bool = True
) -> Dict[str, Any]:
    """
    Share a document with specified users.
    
    Args:
        document_id: ID of the document to share
        email_addresses: List of email addresses to share with
        role: Access role ('reader', 'writer', 'commenter')
        send_notification: Whether to send notification emails
        
    Returns:
        Dictionary containing the sharing result
    """
    # This would connect to the Google Drive MCP server in a real implementation
    return {
        "status": "shared",
        "document_id": document_id,
        "shared_with": email_addresses,
        "role": role,
        "notifications_sent": send_notification,
        "message": f"Document shared with {len(email_addresses)} users"
    }


def create_folder(
    name: str,
    parent_folder_id: str = "root"
) -> Dict[str, Any]:
    """
    Create a new folder in Google Drive.
    
    Args:
        name: Name of the folder to create
        parent_folder_id: ID of the parent folder
        
    Returns:
        Dictionary containing the folder creation result
    """
    # This would connect to the Google Drive MCP server in a real implementation
    folder_id = f"folder_{hash(name) % 10000}"
    
    return {
        "status": "created",
        "folder_id": folder_id,
        "name": name,
        "parent_folder_id": parent_folder_id,
        "folder_url": f"https://drive.google.com/drive/folders/{folder_id}",
        "message": f"Folder '{name}' created successfully"
    }


def get_folder_contents(
    folder_id: str
) -> Dict[str, Any]:
    """
    Get contents of a specific folder.
    
    Args:
        folder_id: ID of the folder to get contents for
        
    Returns:
        Dictionary containing folder contents
    """
    # This would connect to the Google Drive MCP server in a real implementation
    return {
        "folder_id": folder_id,
        "name": f"Folder {folder_id}",
        "contents": {
            "files": [
                {"id": f"file_{i}", "name": f"File {i}.txt", "type": "file"}
                for i in range(1, 4)
            ],
            "folders": [
                {"id": f"subfolder_{i}", "name": f"Subfolder {i}", "type": "folder"}
                for i in range(1, 3)
            ]
        },
        "total_items": 6,
        "file_count": 3,
        "folder_count": 2,
        "message": f"Contents of folder {folder_id} retrieved"
    }


def get_documentation_resources() -> List[Dict[str, Any]]:
    """
    Get available documentation resources from the meta server.
    
    Returns:
        List of dictionaries containing documentation resources
    """
    # This would connect to the Meta FastMCP server in a real implementation
    return [
        {
            "id": f"resource_{i}",
            "name": f"Documentation Resource {i}",
            "type": "guide" if i % 3 == 0 else "api_reference" if i % 3 == 1 else "tutorial",
            "description": f"Resource for documenting system {i} or process {i}",
            "url": f"https://docs.example.com/resource_{i}",
            "last_updated": (datetime.now() - timedelta(days=i)).isoformat(),
            "tags": ["documentation", f"system-{i}", "guide"]
        }
        for i in range(1, 6)
    ]


# Create a Documentation & System Management agent
agent = Agent(
    system_prompt="You are a Documentation & System Management assistant. You can manage Dokploy applications, create and manage documents in Google Drive, handle document content and sharing, create folders, and access documentation resources. When asked about system management or documentation operations, provide detailed information about available resources, deployment processes, and document management best practices."
)


def setup_doc_sys_agent():
    """Set up the Documentation & System Management agent with tools."""
    try:
        agent.add_tool(list_applications)
        agent.add_tool(deploy_application)
        agent.add_tool(list_files)
        agent.add_tool(create_document)
        agent.add_tool(get_document_content)
        agent.add_tool(list_spreadsheets)
        agent.add_tool(read_sheet_data)
        agent.add_tool(update_document)
        agent.add_tool(share_document)
        agent.add_tool(create_folder)
        agent.add_tool(get_folder_contents)
        agent.add_tool(get_documentation_resources)
        print("Documentation & System Management tools successfully registered with the agent.")
        return True
    except AttributeError as e:
        print(f"Note: Tool registration API may vary depending on the specific Strands implementation. Error: {e}")
        return False


def run_doc_sys_agent(user_input: str):
    """
    Run the Documentation & System Management agent with the given user input.
    
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
        return f"Simulated response: Documentation & System Management agent. You requested: '{user_input}'"
    except Exception as e:
        return f"Error processing your request: {str(e)}"


def main():
    """Main function to run the Documentation & System Management agent."""
    # Set up tools
    tools_setup = setup_doc_sys_agent()
    
    print("Documentation & System Management Agent")
    print("This agent can:")
    print("- List applications (e.g., 'show all applications')")
    print("- Deploy applications (e.g., 'deploy app_1 with new image')")
    print("- List files (e.g., 'list all files in Drive')")
    print("- Create documents (e.g., 'create a new document')")
    print("- Get document content (e.g., 'get content of document 123')")
    print("- List spreadsheets (e.g., 'show all spreadsheets')")
    print("- Read sheet data (e.g., 'read data from sheet 123')")
    print("- Update documents (e.g., 'update document 123')")
    print("- Share documents (e.g., 'share document 123 with user@example.com')")
    print("- Create folders (e.g., 'create a new folder')")
    print("- Get folder contents (e.g., 'show contents of folder 123')")
    print("- Get documentation resources (e.g., 'show documentation resources')")
    print("Type 'quit' to exit.\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Agent: Goodbye! Documentation & System Management assistant signing off.")
            break
            
        response = run_doc_sys_agent(user_input)
        print(f"Agent: {response}\n")


if __name__ == "__main__":
    main()