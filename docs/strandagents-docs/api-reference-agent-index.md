# Agent API Reference

Documentation for the Agent class and its methods in the Strands Agents SDK.

## Overview

The Agent class is the fundamental building block of the Strands framework. It encapsulates the logic for interacting with models, managing state, and executing tools.

## Key Methods

### Core Agent Methods
- `run()`: Execute the agent with a given input
- `stream()`: Execute the agent with streaming response support
- `init()`: Initialize the agent with configuration parameters

### State Management
- `get_state()`: Retrieve the current state of the agent
- `set_state()`: Update the agent's state
- `clear_state()`: Reset the agent's state

### Tool Integration
- `add_tool()`: Add a new tool to the agent's capabilities
- `execute_tool()`: Execute a specific tool
- `list_tools()`: Get a list of available tools

## Configuration Options

The Agent class supports various configuration options to customize its behavior, including model selection, system prompts, and execution parameters.

More details about the Agent API including comprehensive method documentation, usage examples, and implementation details would be available in the full documentation.