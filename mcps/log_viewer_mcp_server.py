#!/usr/bin/env python3
"""
Log Viewer MCP Server

Provides access to log viewing and analysis functionality for LLMs through MCP protocol.
"""

from fastmcp import FastMCP
from typing import List, Dict, Any
import asyncio
import os
import re
from datetime import datetime, timedelta


# Initialize the MCP server
mcp = FastMCP(
    name="Log Viewer MCP Server",
    instructions="Provides access to log viewing and analysis functionality including file-based and system log operations",
    version="1.0.0"
)


# Tools
@mcp.tool
def read_log_file(
    file_path: str, 
    lines: int = 50,
    reverse: bool = True
) -> List[str]:
    """
    Read the last N lines from a log file
    """
    if not os.path.exists(file_path):
        return [f"Error: Log file does not exist: {file_path}"]
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            # Read all lines
            all_lines = f.readlines()
            
        # Return the last N lines
        if reverse:
            return [line.rstrip('\n') for line in all_lines[-lines:]]
        else:
            return [line.rstrip('\n') for line in all_lines[:lines]]
    except Exception as e:
        return [f"Error reading log file: {str(e)}"]


@mcp.tool
def search_logs(
    file_path: str,
    search_term: str,
    case_sensitive: bool = False
) -> List[Dict[str, Any]]:
    """
    Search for a term in a log file and return matching lines with context
    """
    if not os.path.exists(file_path):
        return [{"error": f"Log file does not exist: {file_path}"}]
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        matches = []
        flags = 0 if case_sensitive else re.IGNORECASE
        
        for i, line in enumerate(lines):
            if re.search(search_term, line, flags):
                matches.append({
                    "line_number": i + 1,
                    "content": line.rstrip('\n'),
                    "timestamp": extract_timestamp(line) or "N/A"
                })
        
        return matches
    except Exception as e:
        return [{"error": f"Error searching log file: {str(e)}"}]


@mcp.tool
def get_log_stats(file_path: str) -> Dict[str, Any]:
    """
    Get statistics about a log file
    """
    if not os.path.exists(file_path):
        return {"error": f"Log file does not exist: {file_path}"}
    
    try:
        stat = os.stat(file_path)
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            line_count = sum(1 for line in f)
        
        return {
            "file_path": file_path,
            "size_bytes": stat.st_size,
            "size_formatted": format_bytes(stat.st_size),
            "line_count": line_count,
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "last_accessed": datetime.fromtimestamp(stat.st_atime).isoformat()
        }
    except Exception as e:
        return {"error": f"Error getting log stats: {str(e)}"}


@mcp.tool
def get_recent_logs(
    directory: str, 
    pattern: str = "*.log",
    hours: int = 24
) -> List[Dict[str, str]]:
    """
    Get log files modified in the last N hours
    """
    if not os.path.exists(directory):
        return [{"error": f"Directory does not exist: {directory}"}]
    
    try:
        recent_files = []
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        for filename in os.listdir(directory):
            if filename.endswith('.log'):  # Basic pattern matching
                filepath = os.path.join(directory, filename)
                if os.path.isfile(filepath):
                    modified_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                    if modified_time > cutoff_time:
                        recent_files.append({
                            "filename": filename,
                            "path": filepath,
                            "modified": modified_time.isoformat(),
                            "size": format_bytes(os.path.getsize(filepath))
                        })
        
        return sorted(recent_files, key=lambda x: x['modified'], reverse=True)
    except Exception as e:
        return [{"error": f"Error getting recent logs: {str(e)}"}]


@mcp.tool
def extract_errors(log_file: str) -> List[Dict[str, str]]:
    """
    Extract error messages from a log file
    """
    error_patterns = [
        r'error', r'exception', r'fail', r'critical', r'fatal', r'warn'
    ]
    
    if not os.path.exists(log_file):
        return [{"error": f"Log file does not exist: {log_file}"}]
    
    try:
        errors = []
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                for pattern in error_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        errors.append({
                            "line_number": line_num,
                            "content": line.rstrip('\n'),
                            "level": "error" if 'error' in line.lower() else 
                                   "warning" if 'warn' in line.lower() else "other",
                            "timestamp": extract_timestamp(line) or "N/A"
                        })
                        break  # Only add line once even if it matches multiple patterns
        
        return errors
    except Exception as e:
        return [{"error": f"Error extracting errors: {str(e)}"}]


@mcp.tool
def tail_log_file(file_path: str, num_lines: int = 10) -> List[str]:
    """
    Tail a log file (show last N lines) - similar to Unix tail command
    """
    return read_log_file(file_path, num_lines, reverse=True)


@mcp.tool
def follow_log_file(file_path: str) -> str:
    """
    Simulate following a log file (like tail -f) - returns last few lines
    """
    # In a real implementation, this would implement actual following
    # For now, just return the last 10 lines
    lines = read_log_file(file_path, 10, reverse=True)
    return f"Following {file_path}:\n" + "\n".join(lines)


@mcp.tool
def analyze_log_frequency(log_file: str, hours: int = 1) -> Dict[str, int]:
    """
    Analyze the frequency of log entries over the last N hours
    """
    if not os.path.exists(log_file):
        return {"error": f"Log file does not exist: {log_file}"}
    
    try:
        time_threshold = datetime.now() - timedelta(hours=hours)
        entries_count = 0
        
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                timestamp = extract_timestamp(line)
                if timestamp:
                    try:
                        dt = parse_timestamp(timestamp)
                        if dt and dt > time_threshold:
                            entries_count += 1
                    except:
                        continue  # Skip lines with unparseable timestamps
                else:
                    entries_count += 1  # Count the line even without timestamp
        
        return {
            "time_period_hours": hours,
            "log_entries_count": entries_count,
            "average_per_hour": round(entries_count / hours, 2) if hours > 0 else 0
        }
    except Exception as e:
        return {"error": f"Error analyzing log frequency: {str(e)}"}


@mcp.tool
def filter_logs_by_level(log_file: str, level: str) -> List[Dict[str, str]]:
    """
    Filter log entries by level (ERROR, WARN, INFO, DEBUG)
    """
    level_patterns = {
        'ERROR': r'error|exception|critical|fatal',
        'WARN': r'warn|warning',
        'INFO': r'info|information',
        'DEBUG': r'debug'
    }
    
    if level.upper() not in level_patterns:
        return [{"error": f"Invalid log level: {level}"}]
    
    if not os.path.exists(log_file):
        return [{"error": f"Log file does not exist: {log_file}"}]
    
    try:
        pattern = level_patterns[level.upper()]
        filtered_logs = []
        
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    filtered_logs.append({
                        "line_number": line_num,
                        "content": line.rstrip('\n'),
                        "timestamp": extract_timestamp(line) or "N/A"
                    })
        
        return filtered_logs
    except Exception as e:
        return [{"error": f"Error filtering logs: {str(e)}"}]


def extract_timestamp(log_line: str) -> str:
    """
    Extract timestamp from a log line using common patterns
    """
    # Common timestamp patterns
    patterns = [
        r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',  # YYYY-MM-DD HH:MM:SS
        r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}',  # YYYY/MM/DD HH:MM:SS
        r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}',  # MM/DD/YYYY HH:MM:SS
        r'\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}',  # MM-DD-YYYY HH:MM:SS
        r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',  # ISO format
    ]
    
    for pattern in patterns:
        match = re.search(pattern, log_line)
        if match:
            return match.group()
    
    return None


def parse_timestamp(timestamp_str: str) -> datetime:
    """
    Parse timestamp string to datetime object
    """
    # Common formats
    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y/%m/%d %H:%M:%S',
        '%m/%d/%Y %H:%M:%S',
        '%m-%d-%Y %H:%M:%S',
        '%Y-%m-%dT%H:%M:%S',
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(timestamp_str, fmt)
        except ValueError:
            continue
    
    return None


def format_bytes(bytes_value: int) -> str:
    """
    Format bytes value to human readable format
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"


# Resources
@mcp.resource("http://log-viewer-mcp-server.local/system-logs")
def get_system_logs_info() -> List[Dict[str, str]]:
    """
    Get information about common system log files
    """
    common_logs = [
        "/var/log/syslog",
        "/var/log/messages", 
        "/var/log/auth.log",
        "/var/log/kern.log",
        "/var/log/dmesg"
    ]
    
    logs_info = []
    for log_path in common_logs:
        if os.path.exists(log_path):
            stat = os.stat(log_path)
            logs_info.append({
                "name": os.path.basename(log_path),
                "path": log_path,
                "size": format_bytes(stat.st_size),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
    
    return logs_info


@mcp.resource("http://log-viewer-mcp-server.local/application-logs")
def get_application_logs_info() -> List[Dict[str, str]]:
    """
    Get information about common application log directories
    """
    app_log_dirs = [
        "/var/log/apache2",
        "/var/log/nginx",
        "/var/log/mysql",
        "/var/log/postgresql",
        "/var/log/applications"
    ]
    
    logs_info = []
    for log_dir in app_log_dirs:
        if os.path.exists(log_dir):
            for filename in os.listdir(log_dir):
                if filename.endswith('.log'):
                    filepath = os.path.join(log_dir, filename)
                    if os.path.isfile(filepath):
                        stat = os.stat(filepath)
                        logs_info.append({
                            "name": filename,
                            "path": filepath,
                            "size": format_bytes(stat.st_size),
                            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            "directory": log_dir
                        })
    
    return logs_info


@mcp.resource("http://log-viewer-mcp-server.local/log-statistics")
def get_log_statistics() -> Dict[str, Any]:
    """
    Get overall log statistics for the system
    """
    log_dirs = ["/var/log"]
    total_files = 0
    total_size = 0
    error_count = 0
    
    for log_dir in log_dirs:
        if os.path.exists(log_dir):
            for root, dirs, files in os.walk(log_dir):
                for file in files:
                    if file.endswith('.log'):
                        filepath = os.path.join(root, file)
                        try:
                            stat = os.stat(filepath)
                            total_size += stat.st_size
                            total_files += 1
                            
                            # Sample the file to count errors (first 100 lines)
                            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                                for i, line in enumerate(f):
                                    if i > 100:  # Only check first 100 lines for performance
                                        break
                                    if 'error' in line.lower() or 'exception' in line.lower():
                                        error_count += 1
                        except:
                            continue
    
    return {
        "total_log_files": total_files,
        "total_size_bytes": total_size,
        "total_size_formatted": format_bytes(total_size),
        "estimated_error_count": error_count
    }


# Prompts
@mcp.prompt("/log-analysis")
def log_analysis_prompt(
    log_file: str,
    analysis_type: str,
    time_period: str,
    context: str = ""
) -> str:
    """
    Generate a prompt for analyzing log files
    """
    return f"""
Analyze the log file: {log_file}
Analysis Type: {analysis_type}
Time Period: {time_period}
Context: {context}

Identify patterns, anomalies, errors, and performance issues in the logs.
"""


@mcp.prompt("/error-investigation")
def error_investigation_prompt(
    error_message: str,
    log_file: str,
    time_before: int = 5,
    time_after: int = 5,
    context: str = ""
) -> str:
    """
    Generate a prompt for investigating specific errors in logs
    """
    return f"""
Investigate this error: {error_message}
In log file: {log_file}
Look {time_before} minutes before and {time_after} minutes after the error
Context: {context}

Find root cause and suggest remediation steps.
"""


@mcp.prompt("/log-pattern-recognition")
def log_pattern_recognition_prompt(
    log_file: str,
    patterns_to_find: List[str],
    context: str = ""
) -> str:
    """
    Generate a prompt for recognizing patterns in logs
    """
    return f"""
Identify the following patterns in log file {log_file}: {patterns_to_find}
Context: {context}

Extract relevant information and summarize the findings.
"""


@mcp.prompt("/log-alert-configuration")
def log_alert_configuration_prompt(
    log_files: List[str],
    alert_conditions: List[str],
    notification_methods: List[str],
    context: str = ""
) -> str:
    """
    Generate a prompt for configuring log-based alerts
    """
    return f"""
Configure alerts for log files: {log_files}
Alert Conditions: {alert_conditions}
Notification Methods: {notification_methods}
Context: {context}

Set up monitoring rules and alert thresholds.
"""


if __name__ == "__main__":
    # Use stdio transport for MCP server (proper MCP protocol communication)
    asyncio.run(mcp.run_stdio_async())