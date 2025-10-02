"""
Google Sheets Agent using Strands Agents SDK

This agent uses the Google Sheets MCP to manage spreadsheet operations.
"""

from strandsagents import Agent
from typing import Dict, Any, List
import json
from datetime import datetime


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


def write_to_sheet(
    spreadsheet_id: str,
    sheet_name: str,
    range: str,
    values: List[List[Any]],
    value_input_option: str = "RAW"
) -> Dict[str, Any]:
    """
    Write data to a Google Sheet.
    
    Args:
        spreadsheet_id: ID of the spreadsheet to write to
        sheet_name: Name of the sheet to write to
        range: A1 notation range to write to
        values: 2D array of values to write
        value_input_option: How the input data should be interpreted (RAW or USER_ENTERED)
        
    Returns:
        Dictionary containing the write operation result
    """
    # This would connect to the Google Sheets MCP server in a real implementation
    return {
        "status": "success",
        "spreadsheet_id": spreadsheet_id,
        "sheet_name": sheet_name,
        "range": range,
        "updated_range": range,
        "updated_rows": len(values),
        "updated_columns": len(values[0]) if values else 0,
        "value_input_option": value_input_option,
        "message": f"Successfully updated {len(values)} rows in {sheet_name}"
    }


def append_to_sheet(
    spreadsheet_id: str,
    sheet_name: str,
    range: str,
    values: List[List[Any]],
    insert_data_option: str = "OVERWRITE"
) -> Dict[str, Any]:
    """
    Append data to a Google Sheet.
    
    Args:
        spreadsheet_id: ID of the spreadsheet to append to
        sheet_name: Name of the sheet to append to
        range: A1 notation range to append to
        values: 2D array of values to append
        insert_data_option: How the data should be inserted (OVERWRITE or INSERT_ROWS)
        
    Returns:
        Dictionary containing the append operation result
    """
    # This would connect to the Google Sheets MCP server in a real implementation
    return {
        "status": "success",
        "spreadsheet_id": spreadsheet_id,
        "sheet_name": sheet_name,
        "range": range,
        "updates": {
            "spreadsheet_id": spreadsheet_id,
            "updated_range": range,
            "updated_rows": len(values),
            "updated_columns": len(values[0]) if values else 0
        },
        "message": f"Successfully appended {len(values)} rows to {sheet_name}"
    }


def create_spreadsheet(
    title: str,
    sheets: List[Dict[str, Any]] = None,
    locale: str = "en_US",
    timeZone: str = "America/New_York"
) -> Dict[str, Any]:
    """
    Create a new Google Spreadsheet.
    
    Args:
        title: Title of the new spreadsheet
        sheets: Optional list of sheet configurations
        locale: Locale for the spreadsheet
        timeZone: Timezone for the spreadsheet
        
    Returns:
        Dictionary containing the spreadsheet creation result
    """
    # This would connect to the Google Sheets MCP server in a real implementation
    spreadsheet_id = f"new_sheet_{hash(title) % 10000}"
    
    default_sheets = [
        {"properties": {"title": "Sheet1", "sheetType": "GRID", "sheetId": 0}}
    ]
    
    return {
        "status": "created",
        "spreadsheet_id": spreadsheet_id,
        "title": title,
        "sheets": sheets or default_sheets,
        "spreadsheet_url": f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}",
        "message": f"Spreadsheet '{title}' created successfully"
    }


def update_spreadsheet(
    spreadsheet_id: str,
    title: str = None,
    sheet_properties: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Update properties of a Google Spreadsheet.
    
    Args:
        spreadsheet_id: ID of the spreadsheet to update
        title: New title for the spreadsheet (optional)
        sheet_properties: List of sheet property updates (optional)
        
    Returns:
        Dictionary containing the spreadsheet update result
    """
    # This would connect to the Google Sheets MCP server in a real implementation
    return {
        "status": "updated",
        "spreadsheet_id": spreadsheet_id,
        "updated_fields": [f for f in [title] if f is not None],
        "timestamp": datetime.now().isoformat(),
        "message": f"Spreadsheet {spreadsheet_id} updated successfully"
    }


def delete_spreadsheet_row(
    spreadsheet_id: str,
    sheet_id: int,
    row_index: int
) -> Dict[str, Any]:
    """
    Delete a specific row from a Google Sheet.
    
    Args:
        spreadsheet_id: ID of the spreadsheet
        sheet_id: ID of the sheet
        row_index: Index of the row to delete (0-based)
        
    Returns:
        Dictionary containing the row deletion result
    """
    # This would connect to the Google Sheets MCP server in a real implementation
    return {
        "status": "deleted",
        "spreadsheet_id": spreadsheet_id,
        "sheet_id": sheet_id,
        "row_index": row_index,
        "message": f"Row {row_index} deleted from sheet {sheet_id}"
    }


def filter_data(
    spreadsheet_id: str,
    sheet_name: str,
    filter_criteria: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Filter data in a Google Sheet based on criteria.
    
    Args:
        spreadsheet_id: ID of the spreadsheet
        sheet_name: Name of the sheet to filter
        filter_criteria: Dictionary containing filter conditions
        
    Returns:
        Dictionary containing the filtered data
    """
    # This would connect to the Google Sheets MCP server in a real implementation
    return {
        "spreadsheet_id": spreadsheet_id,
        "sheet_name": sheet_name,
        "filter_criteria": filter_criteria,
        "filtered_data": [
            {
                "name": "Jane Smith",
                "email": "jane@example.com",
                "department": "Marketing",
                "salary": 68000,
                "hire_date": "2019-11-22"
            }
        ],  # Example filtered data
        "total_matching_rows": 1,
        "message": f"Filter applied to {sheet_name}, 1 row matched criteria"
    }


def create_pivot_table(
    spreadsheet_id: str,
    source_range: str,
    pivot_table_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create a pivot table in a Google Sheet.
    
    Args:
        spreadsheet_id: ID of the spreadsheet
        source_range: A1 notation range for the source data
        pivot_table_config: Configuration for the pivot table
        
    Returns:
        Dictionary containing the pivot table creation result
    """
    # This would connect to the Google Sheets MCP server in a real implementation
    return {
        "status": "created",
        "spreadsheet_id": spreadsheet_id,
        "source_range": source_range,
        "pivot_table_config": pivot_table_config,
        "pivot_table_id": f"pivot_{hash(source_range) % 10000}",
        "message": f"Pivot table created in {spreadsheet_id} from {source_range}"
    }


def get_sheet_stats(
    spreadsheet_id: str,
    sheet_name: str
) -> Dict[str, Any]:
    """
    Get statistical information about a Google Sheet.
    
    Args:
        spreadsheet_id: ID of the spreadsheet
        sheet_name: Name of the sheet to analyze
        
    Returns:
        Dictionary containing statistical information
    """
    # This would connect to the Google Sheets MCP server in a real implementation
    return {
        "spreadsheet_id": spreadsheet_id,
        "sheet_name": sheet_name,
        "stats": {
            "total_rows": 150,
            "total_columns": 10,
            "filled_cells": 1250,
            "empty_cells": 250,
            "data_density": 0.83,  # 83% of cells are filled
            "last_edit_time": (datetime.now() - timedelta(hours=2)).isoformat(),
            "contributors_count": 3,
            "total_formulas": 12
        },
        "message": f"Statistics retrieved for {sheet_name}"
    }


def share_spreadsheet(
    spreadsheet_id: str,
    email_addresses: List[str],
    role: str = "reader",  # writer, commenter, reader
    send_notification: bool = True
) -> Dict[str, Any]:
    """
    Share a Google Spreadsheet with specified users.
    
    Args:
        spreadsheet_id: ID of the spreadsheet to share
        email_addresses: List of email addresses to share with
        role: Access role ('reader', 'writer', 'commenter')
        send_notification: Whether to send notification emails
        
    Returns:
        Dictionary containing the sharing result
    """
    # This would connect to the Google Sheets MCP server in a real implementation
    return {
        "status": "shared",
        "spreadsheet_id": spreadsheet_id,
        "shared_with": email_addresses,
        "role": role,
        "notifications_sent": send_notification,
        "message": f"Spreadsheet shared with {len(email_addresses)} users"
    }


# Create a Google Sheets agent
agent = Agent(
    system_prompt="You are a Google Sheets assistant. You can list, read, write, and manage Google Spreadsheets. You can also create new spreadsheets, update existing ones, filter data, create pivot tables, and share sheets with others. When asked about spreadsheet operations, provide detailed information about ranges, data formats, and best practices for data management."
)


def setup_gsheets_agent():
    """Set up the Google Sheets agent with tools."""
    try:
        agent.add_tool(list_spreadsheets)
        agent.add_tool(read_sheet_data)
        agent.add_tool(write_to_sheet)
        agent.add_tool(append_to_sheet)
        agent.add_tool(create_spreadsheet)
        agent.add_tool(update_spreadsheet)
        agent.add_tool(delete_spreadsheet_row)
        agent.add_tool(filter_data)
        agent.add_tool(create_pivot_table)
        agent.add_tool(get_sheet_stats)
        agent.add_tool(share_spreadsheet)
        print("Google Sheets tools successfully registered with the agent.")
        return True
    except AttributeError as e:
        print(f"Note: Tool registration API may vary depending on the specific Strands implementation. Error: {e}")
        return False


def run_gsheets_agent(user_input: str):
    """
    Run the Google Sheets agent with the given user input.
    
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
        return f"Simulated response: Google Sheets agent. You requested: '{user_input}'"
    except Exception as e:
        return f"Error processing your request: {str(e)}"


def main():
    """Main function to run the Google Sheets agent."""
    # Set up tools
    tools_setup = setup_gsheets_agent()
    
    print("Google Sheets Agent")
    print("This agent can:")
    print("- List spreadsheets (e.g., 'list my spreadsheets')")
    print("- Read data from sheets (e.g., 'read data from sheet 123')")
    print("- Write data to sheets (e.g., 'write data to range A1:B5')")
    print("- Create new spreadsheets (e.g., 'create a new spreadsheet')")
    print("- Update spreadsheet properties (e.g., 'update spreadsheet title')")
    print("- Delete rows (e.g., 'delete row 5 from sheet 123')")
    print("- Filter data (e.g., 'filter data where salary > 70000')")
    print("- Create pivot tables (e.g., 'create a pivot table')")
    print("- Get sheet statistics (e.g., 'show statistics for sheet 123')")
    print("- Share spreadsheets (e.g., 'share sheet 123 with user@example.com')")
    print("Type 'quit' to exit.\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Agent: Goodbye! Google Sheets assistant signing off.")
            break
            
        response = run_gsheets_agent(user_input)
        print(f"Agent: {response}\n")


if __name__ == "__main__":
    main()