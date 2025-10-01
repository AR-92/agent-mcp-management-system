#!/usr/bin/env python3
"""
Test script to verify Qwen MCP Manager functionality.
"""

import subprocess
import sys
import os
from pathlib import Path


def test_integration():
    """Test the Qwen MCP Manager integration."""
    print("Testing Qwen MCP Manager Integration")
    print("=" * 40)
    
    # Change to project directory
    project_dir = Path("/home/rana/Documents/agent-mcp-managnet-system")
    os.chdir(project_dir)
    
    # Test basic functionality
    print("\n1. Testing help command...")
    result = subprocess.run(["./qwen-mcp-manager"], capture_output=True, text=True)
    if result.returncode == 0:
        print("✓ Help command works")
    else:
        print("✗ Help command failed")
        print(result.stderr)
        return False
    
    # Test listing
    print("\n2. Testing list command...")
    result = subprocess.run(["./qwen-mcp-manager", "list"], capture_output=True, text=True)
    if result.returncode == 0:
        print("✓ List command works")
        print(f"  Output: {len(result.stdout.strip())} characters")
    else:
        print("✗ List command failed")
        print(result.stderr)
        return False
    
    # Test config path
    print("\n3. Testing config path command...")
    result = subprocess.run(["./qwen-mcp-manager", "config-path"], capture_output=True, text=True)
    if result.returncode == 0:
        print("✓ Config path command works")
        config_path = result.stdout.strip()
        print(f"  Config path: {config_path}")
        
        # Check if config file exists
        if Path(config_path).exists():
            print("✓ Config file exists")
        else:
            print("! Config file does not exist (this is OK for first run)")
    else:
        print("✗ Config path command failed")
        print(result.stderr)
        return False
    
    print("\n" + "=" * 40)
    print("All tests passed! Qwen MCP Manager is working correctly.")
    return True


if __name__ == "__main__":
    success = test_integration()
    sys.exit(0 if success else 1)