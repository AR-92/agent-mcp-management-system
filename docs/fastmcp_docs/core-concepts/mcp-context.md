# MCP Context

MCP Context provides tools and resources with access to the MCP system during execution. It enables advanced features like progress reporting, logging, user elicitation, and LLM sampling.

## What is MCP Context?

MCP Context is a special parameter that FastMCP can inject into your tools and resources, giving them access to the MCP system's capabilities:

```python
from fastmcp import FastMCP

mcp = FastMCP("Context Example Server")

@mcp.tool
def long_running_task(context):
    """A task that can report progress and log messages"""
    # Use context for advanced features
    context.progress(0, 100, "Starting task...")
    context.log("Task initialized")
    # ... do work ...
    context.progress(100, 100, "Task completed!")
    return "Success"
```

## Accessing Context

### Automatic Injection
FastMCP can automatically inject context when a parameter is named `context`:

```python
@mcp.tool
def example_with_context(context):
    """Example showing automatic context injection"""
    context.log("Context automatically injected")
    return "Done"
```

### Explicit Parameter
You can also access context through typed parameters:

```python
from fastmcp.context import Context

@mcp.tool
def example_with_typed_context(ctx: Context):
    """Example showing typed context parameter"""
    ctx.log("Using typed context parameter")
    return "Done"
```

## Context Features

### Progress Reporting
Report progress on long-running operations to the client:

```python
import time

@mcp.tool
def process_files(file_list: list[str], context):
    """Process a list of files with progress reporting"""
    total_files = len(file_list)
    
    for i, filename in enumerate(file_list):
        # Report progress
        context.progress(
            current=i+1,
            total=total_files,
            message=f"Processing {filename} ({i+1}/{total_files})"
        )
        
        # Simulate file processing
        time.sleep(0.5)
        
        # Log individual file completion
        context.log(f"Processed {filename}")
    
    return f"Processed {total_files} files successfully"
```

### Logging
Send log messages back to the MCP client:

```python
@mcp.tool
def data_analysis(dataset: str, context):
    """Analyze data and send logs"""
    context.log("Starting data analysis", level="info")
    
    try:
        # Simulate analysis
        context.log(f"Loading dataset: {dataset}", level="debug")
        time.sleep(1)
        
        context.log("Performing statistical analysis", level="info")
        # ... analysis logic ...
        
        context.log("Analysis complete", level="info")
        return {"result": "analysis_complete", "dataset": dataset}
        
    except Exception as e:
        context.log(f"Analysis failed: {str(e)}", level="error")
        raise
```

### User Elicitation
Request structured input from users during tool execution:

```python
from pydantic import BaseModel
from typing import Optional

class UserPreferences(BaseModel):
    theme: str
    notifications: bool
    language: str

@mcp.tool
def configure_user_settings(context):
    """Configure user settings by requesting input"""
    # Request structured input from user
    preferences = context.elicit(
        schema=UserPreferences,
        description="Please configure your preferences"
    )
    
    # Use the provided preferences
    context.log(f"User selected theme: {preferences.theme}")
    context.log(f"Notifications enabled: {preferences.notifications}")
    
    return {
        "status": "configured",
        "preferences": preferences.dict()
    }
```

### LLM Sampling
Request the client's LLM to generate text based on messages:

```python
@mcp.tool
def generate_with_client_llm(prompt: str, context):
    """Use the client's LLM to generate text"""
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]
    
    # Request the client's LLM to generate a response
    response = context.sample(messages)
    
    context.log("Generated response with client LLM")
    return response
```

## Context Methods

### progress()
Report progress on long-running operations:

```python
context.progress(current: int, total: int, message: str = "")
```

Parameters:
- `current`: Current progress value
- `total`: Total progress value  
- `message`: Optional progress message

### log()
Send log messages to the client:

```python
context.log(message: str, level: str = "info")
```

Parameters:
- `message`: Log message content
- `level`: Log level ("debug", "info", "warning", "error")

### elicit()
Request structured input from the user:

```python
context.elicit(schema: Type[BaseModel], description: str = "", examples: list = [])
```

Parameters:
- `schema`: Pydantic model defining the expected input structure
- `description`: Description of what input is requested
- `examples`: Example inputs to guide the user

### sample()
Request LLM sampling from the client:

```python
context.sample(messages: list[dict], max_tokens: Optional[int] = None, temperature: Optional[float] = None)
```

Parameters:
- `messages`: List of message dictionaries with role/content
- `max_tokens`: Maximum tokens to generate
- `temperature`: Sampling temperature (0.0-2.0)

## Advanced Context Usage

### Context Managers
Use context managers for automatic cleanup:

```python
@mcp.tool
def managed_operation(context):
    """Operation with managed context lifecycle"""
    with context.operation("data_processing") as op:
        op.log("Starting operation")
        op.progress(0, 100)
        
        # Do work
        for i in range(100):
            if i % 10 == 0:
                op.progress(i, 100, f"Step {i}/100")
        
        op.progress(100, 100, "Complete")
        op.log("Operation finished")
    
    return "Managed operation complete"
```

### Conditional Context Usage
Use context features conditionally:

```python
@mcp.tool
def adaptive_tool(use_advanced_features: bool = False, context=None):
    """Tool that adapts based on available context"""
    if context and use_advanced_features:
        context.log("Using advanced features", level="info")
        context.progress(0, 100, "Initializing advanced mode")
        # ... advanced logic with context features ...
        context.progress(100, 100, "Advanced mode complete")
    else:
        # ... basic logic without context features ...
        pass
    
    return "Operation completed"
```

### Context Properties
Access contextual information:

```python
@mcp.tool
def context_info(context):
    """Display available context information"""
    info = {
        "has_progress": hasattr(context, 'progress'),
        "has_logging": hasattr(context, 'log'),
        "has_elicit": hasattr(context, 'elicit'),
        "has_sample": hasattr(context, 'sample'),
        "client_capabilities": getattr(context, 'capabilities', 'unknown')
    }
    
    if hasattr(context, 'log'):
        context.log(f"Context info: {info}")
    
    return info
```

## Error Handling with Context

### Graceful Degradation
Handle cases where context features aren't available:

```python
@mcp.tool
def robust_tool(context=None):
    """Tool that works with or without context"""
    # Try to use context features if available
    if context and hasattr(context, 'log'):
        context.log("Using context logging")
    else:
        # Fallback behavior
        print("Using standard output")
    
    # Continue with main logic
    result = "Tool execution result"
    
    # Report completion
    if context and hasattr(context, 'log'):
        context.log("Tool completed successfully")
    
    return result
```

## Context Best Practices

1. **Optional Usage**: Make context usage optional for broader compatibility
2. **Meaningful Messages**: Use descriptive progress and log messages
3. **Appropriate Levels**: Use correct log levels (debug, info, warning, error)
4. **Structured Elicitation**: Define clear schemas for user input requests
5. **Error Handling**: Handle cases where context features aren't available
6. **Performance**: Don't overuse context features in performance-critical paths
7. **Security**: Validate any user input received through elicit()

## Next Steps

- Explore [Server Development](../server-development/index.md) for advanced server features
- Check out [Examples](../examples/index.md) for practical implementations
- Learn about [Authentication](../server-development/authentication.md) for securing context features