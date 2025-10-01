#!/usr/bin/env python3
"""
MCP Log Management Utility

View, search, and manage logs from the MCP system.
"""

import os
import sys
import argparse
from pathlib import Path
import json
from datetime import datetime, timedelta
from typing import List, Dict

# Add parent directory to path so we can import from logs module
sys.path.insert(0, str(Path(__file__).parent.parent))

from logs.log_manager import get_log_manager, MCPLogManager


def list_logs(log_manager: MCPLogManager):
    """List all available log files."""
    stats = log_manager.get_log_stats()
    
    print("Available Log Files:")
    print("=" * 80)
    
    for category, files in stats.items():
        if files:
            print(f"\n{category.upper()}:")
            for file_info in files:
                if not file_info['name'].endswith('.gz'):  # Skip archived files
                    size_mb = file_info['size'] / (1024 * 1024)
                    print(f"  {file_info['name']:<30} {size_mb:>6.2f}MB  {file_info['modified']}")


def view_log(server_name: str, lines: int = 50, follow: bool = False):
    """View logs for a specific server."""
    log_dir = Path("logs/mcp_servers")
    log_file = log_dir / f"{server_name}.log"
    
    if not log_file.exists():
        print(f"Log file not found: {log_file}")
        return
    
    if follow:
        # Implement simple tail -f functionality
        print(f"Following {log_file}... (Press Ctrl+C to stop)")
        try:
            with open(log_file, 'r') as f:
                # Go to end of file
                f.seek(0, 2)
                while True:
                    line = f.readline()
                    if line:
                        print(line.rstrip())
                    else:
                        import time
                        time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nStopped following log")
    else:
        # Show last N lines
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            all_lines = f.readlines()
            last_lines = all_lines[-lines:] if len(all_lines) >= lines else all_lines
            
            print(f"Last {len(last_lines)} lines of {log_file.name}:")
            print("-" * 80)
            for line in last_lines:
                print(line.rstrip())


def search_logs(pattern: str, days: int = 7, server: str = None):
    """Search logs for a specific pattern."""
    start_date = datetime.now() - timedelta(days=days)
    
    # Search in all log directories
    log_dirs = [Path("logs/mcp_servers"), Path("logs/manager"), Path("logs/monitoring")]
    
    found_matches = []
    
    for log_dir in log_dirs:
        if not log_dir.exists():
            continue
            
        for log_file in log_dir.glob("*.log"):
            if server and server not in log_file.name and server + ".log" != log_file.name:
                continue
                
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    
                for i, line in enumerate(lines):
                    if pattern.lower() in line.lower():
                        timestamp_str = line.split(' - ')[0] if ' - ' in line else 'Unknown'
                        found_matches.append({
                            'file': log_file.name,
                            'line_num': i + 1,
                            'timestamp': timestamp_str,
                            'content': line.strip()
                        })
            except Exception as e:
                print(f"Error reading {log_file}: {str(e)}")
    
    # Sort by timestamp if possible
    def try_parse_time(match):
        try:
            # Try to parse the timestamp from the log line
            ts_str = match['timestamp']
            return datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S,%f')
        except:
            return datetime.min
    
    found_matches.sort(key=try_parse_time)
    
    print(f"Found {len(found_matches)} matches for '{pattern}' in the last {days} days:")
    print("-" * 100)
    
    for match in found_matches:
        print(f"[{match['file']}] {match['timestamp']} - Line {match['line_num']}")
        print(f"  {match['content']}")
        print()


def clean_logs(keep_days: int = 30):
    """Clean old logs based on retention settings."""
    log_manager = get_log_manager()
    log_manager.archive_old_logs(keep_days)
    print(f"Cleaned logs older than {keep_days} days")


def log_stats():
    """Show statistics about all log files."""
    log_manager = get_log_manager()
    stats = log_manager.get_log_stats()
    
    print("Log Statistics:")
    print("=" * 80)
    
    total_size = 0
    total_files = 0
    
    for category, files in stats.items():
        category_size = 0
        active_files = [f for f in files if not f['name'].endswith('.gz')]
        
        print(f"\n{category.upper()}:")
        print(f"  Active files: {len(active_files)}")
        
        for file_info in active_files:
            size_mb = file_info['size'] / (1024 * 1024)
            category_size += file_info['size']
            print(f"    {file_info['name']:<30} {size_mb:>6.2f}MB")
        
        cat_mb = category_size / (1024 * 1024)
        print(f"  Total size: {cat_mb:.2f}MB")
        
        total_size += category_size
        total_files += len(active_files)
    
    total_mb = total_size / (1024 * 1024)
    print(f"\nGRAND TOTAL: {total_files} files, {total_mb:.2f}MB")


def main():
    parser = argparse.ArgumentParser(description="MCP Log Management Utility")
    parser.add_argument(
        "command",
        choices=["list", "view", "search", "clean", "stats"],
        help="Command to execute"
    )
    parser.add_argument(
        "server",
        nargs="?",
        help="Server name for view/search commands"
    )
    parser.add_argument(
        "-n", "--lines",
        type=int,
        default=50,
        help="Number of lines to display (default: 50)"
    )
    parser.add_argument(
        "-f", "--follow",
        action="store_true",
        help="Follow log file (like tail -f)"
    )
    parser.add_argument(
        "-p", "--pattern",
        help="Search pattern for search command"
    )
    parser.add_argument(
        "-d", "--days",
        type=int,
        default=7,
        help="Number of days to search (default: 7)"
    )
    parser.add_argument(
        "-k", "--keep-days",
        type=int,
        default=30,
        help="Number of days to keep logs (for clean command, default: 30)"
    )
    
    args = parser.parse_args()
    
    log_manager = get_log_manager()
    
    if args.command == "list":
        list_logs(log_manager)
    elif args.command == "view":
        if not args.server:
            print("Please specify a server name to view logs")
            return
        view_log(args.server, args.lines, args.follow)
    elif args.command == "search":
        if not args.pattern:
            print("Please specify a search pattern with -p")
            return
        search_logs(args.pattern, args.days, args.server)
    elif args.command == "clean":
        clean_logs(args.keep_days)
    elif args.command == "stats":
        log_stats()


if __name__ == "__main__":
    main()