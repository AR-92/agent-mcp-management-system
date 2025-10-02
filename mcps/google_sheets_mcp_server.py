#!/usr/bin/env python3
"""
Google Sheets MCP Server

Provides access to Google Sheets functionality for LLMs through MCP protocol.
"""

from fastmcp import FastMCP
from typing import List, Dict, Any
import asyncio


# Initialize the MCP server
mcp = FastMCP(
    name="Google Sheets MCP Server",
    instructions="Provides access to Google Sheets functionality including spreadsheet management, data operations, and formulas",
    version="1.0.0"
)


# Tools
@mcp.tool
def list_spreadsheets(
    query: str = None, 
    max_results: int = 20
) -> List[Dict[str, Any]]:
    """
    List spreadsheets in Google Drive that are Google Sheets
    """
    # This would connect to Google Sheets API in a real implementation
    return [
        {
            "id": f"sheet_{i}",
            "name": f"Sample Spreadsheet {i}",
            "mimeType": "application/vnd.google-apps.spreadsheet",
            "createdTime": "2023-01-01T10:00:00Z",
            "modifiedTime": "2023-01-02T15:30:00Z",
            "owners": ["user@example.com"],
            "webViewLink": f"https://docs.google.com/spreadsheets/d/sheet_{i}/edit"
        }
        for i in range(max_results)
    ]


@mcp.tool
def get_sheet_data(spreadsheet_id: str, sheet_name: str = "Sheet1", range: str = "A1:Z1000") -> List[List[str]]:
    """
    Get data from a specified range in a Google Sheet
    """
    # This would fetch the actual sheet data from Google Sheets API in a real implementation
    return [
        [f"Header {j}", f"Column {j} Data 1", f"Column {j} Data 2"]
        for j in range(3)
    ]


@mcp.tool
def get_spreadsheet_info(spreadsheet_id: str) -> Dict[str, Any]:
    """
    Get information about a specific spreadsheet
    """
    return {
        "spreadsheet_id": spreadsheet_id,
        "name": f"Spreadsheet {spreadsheet_id}",
        "sheets": [
            {"sheetId": 1, "title": "Sheet1", "rowCount": 1000, "columnCount": 26},
            {"sheetId": 2, "title": "Sheet2", "rowCount": 500, "columnCount": 10}
        ],
        "last_modified": "2023-01-02T15:30:00Z",
        "revision_id": "rev_123"
    }


@mcp.tool
def create_spreadsheet(title: str, sheets: List[str] = None) -> Dict[str, str]:
    """
    Create a new Google Sheet
    """
    if sheets is None:
        sheets = ["Sheet1"]
    
    return {
        "status": "created",
        "spreadsheet_id": "new_sheet_id",
        "message": f"Spreadsheet '{title}' created successfully with sheets: {sheets}"
    }


@mcp.tool
def update_cells(
    spreadsheet_id: str, 
    sheet_name: str, 
    range: str, 
    values: List[List[str]]
) -> Dict[str, str]:
    """
    Update values in specific cells of a Google Sheet
    """
    return {
        "status": "updated",
        "message": f"Updated cells in range {range} of sheet {sheet_name} in spreadsheet {spreadsheet_id}"
    }


@mcp.tool
def append_rows(
    spreadsheet_id: str, 
    sheet_name: str, 
    values: List[List[str]]
) -> Dict[str, str]:
    """
    Append new rows to a Google Sheet
    """
    return {
        "status": "appended",
        "message": f"Appended {len(values)} rows to sheet {sheet_name} in spreadsheet {spreadsheet_id}"
    }


@mcp.tool
def search_in_spreadsheet(spreadsheet_id: str, query: str) -> List[Dict[str, Any]]:
    """
    Search for values in a spreadsheet
    """
    return [
        {
            "sheet": "Sheet1",
            "range": f"A{i+1}",
            "value": f"Found '{query}'",
            "row": i+1,
            "column": 1
        }
        for i in range(5)
    ]


@mcp.tool
def delete_spreadsheet(spreadsheet_id: str) -> Dict[str, str]:
    """
    Delete a Google Sheet
    """
    return {
        "status": "deleted",
        "message": f"Spreadsheet {spreadsheet_id} has been deleted"
    }


@mcp.tool
def add_sheet(spreadsheet_id: str, sheet_title: str) -> Dict[str, str]:
    """
    Add a new sheet to an existing spreadsheet
    """
    return {
        "status": "created",
        "message": f"Added new sheet '{sheet_title}' to spreadsheet {spreadsheet_id}"
    }


# Resources
@mcp.resource("http://google-sheets-mcp-server.local/status")
def get_sheets_status() -> Dict[str, Any]:
    """
    Get the status of the Google Sheets MCP server
    """
    return {
        "status": "connected",
        "account": "user@gmail.com",  # This would be the connected account
        "server_time": asyncio.get_event_loop().time(),
        "connected": True
    }


@mcp.resource("http://google-sheets-mcp-server.local/formulas")
def get_common_formulas() -> Dict[str, str]:
    """
    Get a list of common Google Sheets formulas
    """
    return {
        "SUM": "=SUM(A1:A10) - Calculate sum of range A1 to A10",
        "AVERAGE": "=AVERAGE(B1:B10) - Calculate average of range B1 to B10",
        "COUNT": "=COUNT(C1:C10) - Count non-empty cells in range C1 to C10",
        "VLOOKUP": "=VLOOKUP(lookup_value, table_array, column_index, FALSE) - Vertical lookup",
        "IF": "=IF(condition, value_if_true, value_if_false) - Conditional statement"
    }


@mcp.resource("http://google-sheets-mcp-server.local/usage-stats")
def get_usage_stats() -> Dict[str, Any]:
    """
    Get usage statistics for Google Sheets
    """
    return {
        "total_spreadsheets": 15,
        "sheets_shared": 7,
        "spreadsheets_edited_today": 3,
        "total_cells_used": "2,500,000"
    }


# Prompts
@mcp.prompt("/sheets-create-analysis-sheet")
def create_analysis_sheet_prompt(
    title: str, 
    data_columns: List[str], 
    analysis_types: List[str],
    context: str = ""
) -> str:
    """
    Generate a prompt for creating a Google Sheet for data analysis
    """
    return f"""
Create a Google Sheet with the following specifications:
- Title: {title}
- Data Columns: {data_columns}
- Analysis Types: {analysis_types}
- Context: {context}

Set up appropriate headers, formatting, and formulas for the requested analysis.
"""


@mcp.prompt("/sheets-perform-analysis")
def perform_analysis_prompt(
    spreadsheet_id: str,
    sheet_name: str,
    analysis_request: str,
    context: str = ""
) -> str:
    """
    Generate a prompt for performing data analysis on a Google Sheet
    """
    return f"""
Perform the following analysis on spreadsheet {spreadsheet_id}, sheet {sheet_name}:
- Request: {analysis_request}
- Context: {context}

Use appropriate formulas and functions to extract insights from the data.
"""


@mcp.prompt("/sheets-chart-creation")
def create_chart_prompt(
    spreadsheet_id: str,
    chart_type: str,
    data_range: str,
    context: str = ""
) -> str:
    """
    Generate a prompt for creating a chart in Google Sheets
    """
    return f"""
Create a {chart_type} chart in spreadsheet {spreadsheet_id} using data range {data_range}
- Context: {context}

Set up appropriate axis labels, titles, and formatting for the chart.
"""


@mcp.prompt("/sheets-data-cleanup")
def data_cleanup_prompt(
    spreadsheet_id: str,
    sheet_name: str,
    cleanup_requirements: List[str],
    context: str = ""
) -> str:
    """
    Generate a prompt for cleaning up data in a Google Sheet
    """
    return f"""
Clean up data in spreadsheet {spreadsheet_id}, sheet {sheet_name} according to:
- Requirements: {cleanup_requirements}
- Context: {context}

Address issues like duplicates, formatting, null values, etc.
"""


if __name__ == "__main__":
    # Use stdio transport for MCP server (proper MCP protocol communication)
    asyncio.run(mcp.run_stdio_async())