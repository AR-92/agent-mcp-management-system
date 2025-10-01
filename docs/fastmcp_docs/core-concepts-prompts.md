# Prompts

Prompts are reusable templates for LLM interactions. They provide a way to define common interaction patterns that can be used across different contexts.

## Basic Prompt Definition

A prompt is any function decorated with `@mcp.prompt`:

```python
from fastmcp import FastMCP

mcp = FastMCP("Prompt Example Server")

@mcp.prompt
def summarize_text(text: str) -> str:
    """Please summarize the following text: {text}"""
```

## Prompt Requirements

### Docstrings as Templates
Prompts use the docstring as the template, with parameters inserted using Python's `.format()` syntax:

```python
@mcp.prompt
def analyze_sentiment(text: str) -> str:
    """
    Analyze the sentiment of the following text:
    
    Text: {text}
    
    Please determine if the sentiment is positive, negative, or neutral, 
    and explain your reasoning in 1-2 sentences.
    """
```

### Parameters
Prompts can have parameters that are substituted into the template:

```python
@mcp.prompt
def compare_products(product_a: str, product_b: str, criteria: list[str]) -> str:
    """
    Compare these two products based on specific criteria:
    
    Product A: {product_a}
    Product B: {product_b}
    
    Evaluation Criteria: {criteria}
    
    Please provide a detailed comparison covering each criterion.
    """
```

## Prompt Features

### Simple Prompts
Basic prompts with straightforward templates:

```python
@mcp.prompt
def spell_check(text: str) -> str:
    """Please correct any spelling errors in the following text:\n\n{text}"""
```

### Multi-parameter Prompts
Prompts that accept multiple parameters:

```python
@mcp.prompt
def generate_email(subject: str, recipient: str, tone: str = "professional") -> str:
    """
    Write an email with the following details:
    
    Subject: {subject}
    Recipient: {recipient}
    Tone: {tone}
    
    Please write a complete email following these specifications.
    """
```

### Complex Formatting
Prompts with complex parameter handling:

```python
from typing import List

@mcp.prompt
def code_review(changes: List[dict], language: str = "Python") -> str:
    """
    Please review the following {language} code changes:
    
    Changes:
    {changes}
    
    For each change, please provide:
    1. A brief summary of what was changed
    2. Whether the change improves the code quality
    3. Any suggestions for improvement
    
    Format your response as a structured review.
    """
```

## Prompt Variables

### Variable Substitution
Parameters are substituted using Python string formatting:

```python
@mcp.prompt
def interview_question(topic: str, difficulty: str = "intermediate") -> str:
    """
    Generate a technical interview question about {topic} at {difficulty} level.
    
    Please include:
    1. The question itself
    2. Expected approach/solution
    3. Key concepts being tested
    """
```

### List Handling
Lists and collections are automatically formatted:

```python
@mcp.prompt
def meeting_agenda(topics: list[str], participants: list[str], duration: int) -> str:
    """
    Create a meeting agenda for the following topics:
    Topics: {topics}
    
    Participants: {participants}
    Duration: {duration} minutes
    
    Please create a structured agenda with time allocations for each topic.
    """
```

### Custom Formatting
Use custom formatting for special cases:

```python
from typing import Dict, Any

@mcp.prompt
def system_report(metrics: Dict[str, Any], threshold: float = 0.8) -> str:
    """
    Generate a system health report based on the following metrics:
    
    Metrics:
    {metrics}
    
    Threshold for alerts: {threshold} (values below this are concerning)
    
    Please identify any issues and provide recommendations.
    """
```

## Advanced Prompt Techniques

### Prompt Chaining
Use one prompt's output as input to another:

```python
@mcp.prompt
def extract_key_points(document: str) -> str:
    """Extract the key points from this document:\n\n{document}"""

@mcp.prompt  
def create_summary(key_points: str, audience: str = "executive") -> str:
    """
    Create a {audience}-level summary from these key points:
    
    {key_points}
    """

# Usage example:
# key_points = extract_key_points(document="...")
# summary = create_summary(key_points=key_points, audience="technical")
```

### Conditional Prompts
Prompts that adapt based on parameters:

```python
@mcp.prompt
def feedback_request(performance: str, area: str = None) -> str:
    """
    Request feedback on {performance} performance{f' in {area}' if area else ''}.
    
    Please provide:
    1. Strengths
    2. Areas for improvement
    3. Specific actionable suggestions
    """
```

### Prompt Libraries
Organize related prompts in classes or modules:

```python
class WritingPrompts:
    @staticmethod
    @mcp.prompt
    def creative_story(theme: str, genre: str = "fantasy") -> str:
        """
        Write a creative story with {theme} in a {genre} setting.
        
        Include characters, plot development, and a resolution.
        Keep it under 500 words.
        """
    
    @staticmethod
    @mcp.prompt
    def technical_explanation(concept: str, audience: str = "beginner") -> str:
        """
        Explain the concept of {concept} to a {audience} audience.
        
        Use clear language and provide examples where helpful.
        """

writing_prompts = WritingPrompts()
```

## Prompt Validation

### Input Validation
Validate inputs before using prompts:

```python
@mcp.prompt
def translate_text(text: str, target_language: str, source_language: str = "English") -> str:
    """
    Translate the following text from {source_language} to {target_language}:
    
    {text}
    """
    
    # Validation could be implemented in the calling code
    SUPPORTED_LANGUAGES = ["English", "Spanish", "French", "German", "Chinese", "Japanese"]
    
    if target_language not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported target language: {target_language}")
```

## Prompt Management

### Prompt Versioning
Manage different versions of prompts:

```python
@mcp.prompt(name="analyze_document_v1")
def analyze_document_v1(document: str) -> str:
    """Analyze: {document}"""

@mcp.prompt(name="analyze_document_v2")  
def analyze_document_v2(document: str, focus_areas: list[str] = None) -> str:
    """
    Analyze the following document:
    
    {document}
    
    Focus Areas: {focus_areas if focus_areas else 'General Analysis'}
    
    Provide insights for each focus area.
    """
```

### Prompt Organization
Group related prompts:

```python
# prompts/customer_service.py
@mcp.prompt
def handle_complaint(complaint: str, customer_history: dict = None) -> str:
    """
    Handle a customer complaint:
    
    Complaint: {complaint}
    Customer History: {customer_history}
    
    Respond professionally and offer solutions.
    """

@mcp.prompt
def upsell_opportunity(customer_data: dict, product: str) -> str:
    """
    Identify upsell opportunities for customer:
    
    Customer Data: {customer_data}
    Product: {product}
    
    Suggest relevant complementary products or services.
    """
```

## Best Practices

1. **Clear Instructions**: Write explicit instructions in your prompts
2. **Structured Output**: Ask for structured responses when possible
3. **Context Awareness**: Include relevant context in prompts
4. **Parameter Validation**: Validate parameters before using prompts
5. **Consistent Naming**: Use descriptive names for prompt functions
6. **Versioning**: Version prompts when changing significantly
7. **Documentation**: Document expected input/output formats
8. **Safety**: Avoid prompts that could generate harmful content

## Next Steps

- Explore [MCP Context](./mcp-context.md) - for advanced prompt features
- Check out [Server Development](../server-development/index.md) for implementation details
- See [Examples](../examples/index.md) for practical usage patterns