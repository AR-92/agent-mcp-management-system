# Models API Reference

Documentation for model interfaces and implementations in the Strands Agents SDK.

## Overview

The Models API provides interfaces and implementations for integrating with various LLM providers and model types within the Strands framework.

## Core Interfaces

### Model Interface
- `invoke()`: Execute a model invocation
- `stream()`: Execute a streaming model invocation
- `get_metadata()`: Retrieve model metadata

### Provider Interface
- `initialize()`: Initialize the model provider
- `get_models()`: List available models
- `validate_config()`: Validate provider configuration

## Supported Providers

The Models API supports integration with various providers including OpenAI, Anthropic, Amazon Bedrock, Ollama, and others.

More details about the Models API including comprehensive method documentation, usage examples, and implementation details would be available in the full documentation.