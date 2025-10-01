# Event Loop API Reference

Documentation for the event loop implementation in Strands Agents SDK.

## Overview

The Event Loop manages the execution flow of agents, handling asynchronous operations, tool execution, and state management in a continuous cycle.

## Key Components

### Core Loop Functions
- `start()`: Begin the event loop execution
- `process()`: Process a single iteration of the loop
- `stop()`: Gracefully stop the event loop

### Asynchronous Handling
- `handle_async_tasks()`: Manage concurrent asynchronous operations
- `wait_for_completion()`: Wait for all pending tasks to complete
- `schedule_task()`: Schedule a task for future execution

## Integration Points

The Event Loop provides integration points for hooks, custom handlers, and monitoring components that can observe and influence the execution flow.

More details about the Event Loop API including comprehensive method documentation, usage examples, and implementation details would be available in the full documentation.