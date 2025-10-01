#!/usr/bin/env python3
"""
MCP Server Monitoring Dashboard

A simple dashboard to view server metrics and health status.
"""

import json
import os
from datetime import datetime
from pathlib import Path
import time
import argparse
import sys


def load_metrics(server_name: str) -> list:
    """Load metrics for a specific server."""
    metrics_dir = Path("monitoring/data")
    metrics_file = metrics_dir / f"{server_name}_metrics.json"
    
    if not metrics_file.exists():
        return []
    
    try:
        with open(metrics_file, 'r') as f:
            return json.load(f)
    except:
        return []


def display_server_metrics(server_name: str, limit: int = 10):
    """Display metrics for a specific server."""
    metrics = load_metrics(server_name)
    
    if not metrics:
        print(f"No metrics found for server: {server_name}")
        return
    
    recent_metrics = metrics[-limit:] if len(metrics) >= limit else metrics
    
    print(f"\nMetrics for {server_name}:")
    print("-" * 80)
    print(f"{'Timestamp':<20} {'Status':<12} {'CPU%':<8} {'Mem%':<8} {'Resp(ms)':<10} {'Alerts'}")
    print("-" * 80)
    
    for metric in recent_metrics:
        timestamp = metric['timestamp'].split('.')[0].replace('T', ' ')
        status = metric['health_status'] if metric['is_running'] else 'STOPPED'
        cpu = f"{metric['cpu_percent']:.1f}" if metric['cpu_percent'] > 0 else "N/A"
        memory = f"{metric['memory_percent']:.1f}" if metric['memory_percent'] > 0 else "N/A"
        response = str(metric['response_time']) if metric['response_time'] is not None else "N/A"
        alerts = len(metric['alerts'])
        
        print(f"{timestamp:<20} {status:<12} {cpu:<8} {memory:<8} {response:<10} {alerts}")


def display_all_status():
    """Display current status of all servers."""
    print("\nCurrent Server Status:")
    print("=" * 80)
    
    # Get all server directories from mcps
    mcps_dir = Path("mcps")
    if not mcps_dir.exists():
        print("No mcps directory found!")
        return
    
    for server_dir in mcps_dir.iterdir():
        if server_dir.is_dir():
            server_name = server_dir.name
            metrics = load_metrics(server_name)
            
            if metrics:
                latest = metrics[-1]
                status = latest['health_status'] if latest['is_running'] else 'STOPPED'
                cpu = f"{latest['cpu_percent']:.1f}" if latest['cpu_percent'] > 0 else "N/A"
                memory = f"{latest['memory_percent']:.1f}" if latest['memory_percent'] > 0 else "N/A"
                response = str(latest['response_time']) if latest['response_time'] is not None else "N/A"
                alerts = len(latest['alerts'])
                
                print(f"{server_name:<30} {status:<12} CPU: {cpu:>5}%  Mem: {memory:>5}%  "
                      f"Resp: {response:>6}ms  Alerts: {alerts}")
            else:
                print(f"{server_name:<30} UNKNOWN")


def main():
    parser = argparse.ArgumentParser(description="MCP Server Monitoring Dashboard")
    parser.add_argument(
        "command",
        choices=["status", "metrics", "watch"],
        help="Command to execute"
    )
    parser.add_argument(
        "server",
        nargs="?",
        help="Server name to check (optional for status command)"
    )
    parser.add_argument(
        "-n", "--num",
        type=int,
        default=10,
        help="Number of metrics to display (default: 10)"
    )
    
    args = parser.parse_args()
    
    if args.command == "status":
        if args.server:
            display_server_metrics(args.server, args.num)
        else:
            display_all_status()
    
    elif args.command == "metrics":
        if args.server:
            display_server_metrics(args.server, args.num)
        else:
            print("Please specify a server name to view metrics")
    
    elif args.command == "watch":
        try:
            while True:
                os.system('clear' if os.name == 'posix' else 'cls')  # Clear screen
                print(f"MCP Server Monitoring Dashboard - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("=" * 80)
                display_all_status()
                time.sleep(5)  # Refresh every 5 seconds
        except KeyboardInterrupt:
            print("\nExiting monitor...")


if __name__ == "__main__":
    main()