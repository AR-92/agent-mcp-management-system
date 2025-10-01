#!/bin/bash

# Qwen MCP Manager Shell Script
# Wrapper for the Python Qwen MCP Manager

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/qwen_mcp_manager.py"

# Check if the Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Error: Python script $PYTHON_SCRIPT not found"
    exit 1
fi

# Check if a command was provided
if [ $# -eq 0 ]; then
    echo "Usage:"
    echo "  $0 integrate     - Integrate all MCPs with Qwen"
    echo "  $0 remove-all     - Remove all MCPs from Qwen"
    echo "  $0 list            - List integrated MCPs"
    echo "  $0 config-path    - Show Qwen config file path"
    exit 1
fi

# Execute the Python script with the provided command
python3 "$PYTHON_SCRIPT" "$@"