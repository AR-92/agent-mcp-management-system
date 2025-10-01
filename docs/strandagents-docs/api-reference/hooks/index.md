# Hooks API Reference

Documentation for hook mechanisms and available hook types in the Strands Agents SDK.

## Overview

Hooks provide a mechanism to customize agent behavior by injecting custom logic at various points during agent execution.

## Available Hooks

### Pre-execution Hooks
- `before_run()`: Executed before agent execution begins
- `on_input()`: Called when input is received
- `validate_input()`: Validates input before processing

### Execution Hooks
- `on_tool_call()`: Executed when a tool is called
- `on_model_request()`: Called before model requests
- `on_state_change()`: Triggered when state changes

### Post-execution Hooks
- `after_run()`: Executed after agent execution completes
- `on_output()`: Called when output is generated
- `on_error()`: Handled when errors occur

## Hook Registration

Hooks can be registered using the agent's hook registration system and support both synchronous and asynchronous implementations.

More details about Hook APIs including comprehensive method documentation, usage examples, and implementation details would be available in the full documentation.