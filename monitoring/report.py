#!/usr/bin/env python3
"""
MCP Server Monitoring Report

Generate a summary report of server health and performance.
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
import argparse
import sys


def generate_report(hours: int = 24):
    """Generate a monitoring report for the specified number of hours."""
    print(f"MCP Server Monitoring Report (Last {hours} hours)")
    print("=" * 60)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Find all server metrics files
    metrics_dir = Path("monitoring/data")
    if not metrics_dir.exists():
        print("No monitoring data directory found!")
        return
    
    metrics_files = list(metrics_dir.glob("*_metrics.json"))
    if not metrics_files:
        print("No monitoring data found!")
        return
    
    # Calculate time threshold
    time_threshold = datetime.now() - timedelta(hours=hours)
    
    for metrics_file in metrics_files:
        server_name = metrics_file.name.replace("_metrics.json", "")
        print(f"Server: {server_name}")
        print("-" * 40)
        
        try:
            with open(metrics_file, 'r') as f:
                metrics = json.load(f)
            
            # Filter metrics for the specified time period
            recent_metrics = [
                m for m in metrics 
                if datetime.fromisoformat(m['timestamp'].replace('Z', '+00:00')) > time_threshold
            ]
            
            if not recent_metrics:
                print("  No data available for this time period")
                print()
                continue
            
            # Calculate statistics
            running_count = sum(1 for m in recent_metrics if m['is_running'])
            total_count = len(recent_metrics)
            uptime_percent = (running_count / total_count) * 100 if total_count > 0 else 0
            
            cpu_values = [m['cpu_percent'] for m in recent_metrics if m['cpu_percent'] > 0]
            memory_values = [m['memory_percent'] for m in recent_metrics if m['memory_percent'] > 0]
            
            avg_cpu = sum(cpu_values) / len(cpu_values) if cpu_values else 0
            avg_memory = sum(memory_values) / len(memory_values) if memory_values else 0
            
            max_cpu = max(cpu_values) if cpu_values else 0
            max_memory = max(memory_values) if memory_values else 0
            
            # Count alerts
            alert_count = sum(len(m['alerts']) for m in recent_metrics)
            
            # Display summary
            print(f"  Uptime: {uptime_percent:.1f}% ({running_count}/{total_count})")
            print(f"  Average CPU: {avg_cpu:.1f}% (Max: {max_cpu:.1f}%)")
            print(f"  Average Memory: {avg_memory:.1f}% (Max: {max_memory:.1f}%)")
            print(f"  Total Alerts: {alert_count}")
            
            # Show recent alerts if any
            if alert_count > 0:
                recent_alerts = []
                for m in recent_metrics:
                    for alert in m['alerts']:
                        recent_alerts.append((m['timestamp'], alert))
                
                recent_alerts = recent_alerts[-5:]  # Show last 5 alerts
                print("  Recent Alerts:")
                for timestamp, alert in recent_alerts:
                    print(f"    {timestamp.split('.')[0]} - {alert}")
            
            print()
        
        except Exception as e:
            print(f"  Error reading metrics for {server_name}: {str(e)}")
            print()


def main():
    parser = argparse.ArgumentParser(description="MCP Server Monitoring Report")
    parser.add_argument(
        "-h", "--hours",
        type=int,
        default=24,
        help="Number of hours to include in the report (default: 24)"
    )
    
    args = parser.parse_args()
    
    generate_report(args.hours)


if __name__ == "__main__":
    main()