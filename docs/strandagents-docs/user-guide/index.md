# User Guide

The User Guide provides comprehensive information about working with the Strands Agents SDK. Whether you're a beginner looking to get started or an experienced developer wanting to leverage advanced features, this guide will help you understand the concepts and implementation details.

## Sections

- [Quickstart](./quickstart/): Get up and running quickly with the basics
- [Concepts](./concepts/): Understanding the core building blocks and architecture
  - [Agents](./concepts/agents/): The fundamental building blocks of your AI applications
    - [Agent Loop](./concepts/agents/#agent-loop): Core execution mechanism
    - [State](./concepts/agents/#state): Managing agent state across interactions
    - [Session Management](./concepts/agents/#session-management): Grouping related interactions
    - [Prompts](./concepts/agents/#prompts): Crafting and managing prompts
    - [Hooks](./concepts/agents/#hooks): Customizing agent behavior
    - [Structured Output](./concepts/agents/#structured-output): Reliable information extraction
    - [Conversation Management](./concepts/agents/#conversation-management): Handling multi-turn interactions
  - [Tools](./concepts/tools/): Mechanisms for interacting with external systems and performing actions
    - [Overview](./concepts/tools/#overview): Introduction to tools
    - [Python](./concepts/tools/#python): Python-based tools
    - [Model Context Protocol (MCP)](./concepts/tools/#model-context-protocol-mcp): Standardized service interaction
    - [Executors](./concepts/tools/#executors): Tool execution infrastructure
    - [Community Tools Package](./concepts/tools/#community-tools-package): Pre-built tools collection
  - [Model Providers](./concepts/model-providers/): Support for various LLM providers with flexibility
    - [Amazon Bedrock](./concepts/model-providers/#amazon-bedrock): Foundation models with enterprise security
    - [Anthropic](./concepts/model-providers/#anthropic): Claude models with safety features
    - [LiteLLM](./concepts/model-providers/#litellm): Unified access to multiple providers
    - [llama.cpp](./concepts/model-providers/#llama-cpp): Local inference support
    - [LlamaAPI](./concepts/model-providers/#llamaapi): Hosted Llama model inference
    - [MistralAI](./concepts/model-providers/#mistralai): Mistral models and capabilities
    - [Ollama](./concepts/model-providers/#ollama): Running open-source models locally
    - [OpenAI](./concepts/model-providers/#openai): GPT models and integrations
    - [SageMaker](./concepts/model-providers/#sagemaker): Custom model deployment and inference
    - [Writer](./concepts/model-providers/#writer): Writer's AI models and services
    - [Cohere](./concepts/model-providers/#cohere): Cohere's language models and embeddings
    - [Custom Providers](./concepts/model-providers/#custom-providers): Integrating your own providers
  - [Streaming](./concepts/streaming/): Real-time, incremental responses for better user experience
    - [Overview](./concepts/streaming/#overview): Basic streaming concepts
    - [Async Iterators](./concepts/streaming/#async-iterators): Clean mechanism for streaming
    - [Callback Handlers](./concepts/streaming/#callback-handlers): Custom processing of streaming data
  - [Multi-agent](./concepts/multi-agent/): Patterns for orchestrating multiple specialized agents
    - [Agent2Agent (A2A)](./concepts/multi-agent/#agent2agent-a2a): Direct agent communication
    - [Agents as Tools](./concepts/multi-agent/#agents-as-tools): Using agents as tools
    - [Swarm](./concepts/multi-agent/#swarm): Coordinated agent systems
    - [Graph](./concepts/multi-agent/#graph): Dependencies and execution paths
    - [Workflow](./concepts/multi-agent/#workflow): Structured multi-agent execution
    - [Multi-agent Patterns](./concepts/multi-agent/#multi-agent-patterns): Common patterns and best practices
- [Safety & Security](./safety-security/): Best practices for responsible AI
- [Observability & Evaluation](./observability-evaluation/): Monitoring and measuring performance
- [Deploy](./deploy/): Production deployment strategies

Start with the [Quickstart](./quickstart/) section if you're new to Strands Agents SDK, or browse the [Concepts](./concepts/) section to understand the underlying architecture.