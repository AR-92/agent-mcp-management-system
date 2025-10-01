# Concepts

The Strands Agents SDK is built around several core concepts that enable you to build powerful, production-ready multi-agent AI systems. This section covers the fundamental ideas and components you'll need to understand to effectively use the SDK.

## Main Concepts

- [Agents](./agents/): The fundamental building blocks of your AI applications
  - [Agent Loop](./agents/#agent-loop): The core mechanism driving agent execution
  - [State](./agents/#state): Managing context across multiple interactions
  - [Session Management](./agents/#session-management): Grouping related interactions
  - [Prompts](./agents/#prompts): Managing prompt engineering
  - [Hooks](./agents/#hooks): Customizing agent behavior
  - [Structured Output](./agents/#structured-output): Reliable information extraction
  - [Conversation Management](./agents/#conversation-management): Handling multi-turn interactions
- [Tools](./tools/): Mechanisms for interacting with external systems and performing actions
  - [Overview](./tools/#overview): Introduction to tools
  - [Python](./tools/#python): Python-based tools
  - [Model Context Protocol (MCP)](./tools/#model-context-protocol-mcp): Standardized interfaces
  - [Executors](./tools/#executors): Infrastructure for running tools
  - [Community Tools Package](./tools/#community-tools-package): Pre-built tools collection
- [Model Providers](./model-providers/): Support for various LLM providers with flexibility
  - [Amazon Bedrock](./model-providers/#amazon-bedrock): Amazon Bedrock integration
  - [Anthropic](./model-providers/#anthropic): Anthropic Claude models
  - [LiteLLM](./model-providers/#litellm): Unified access through LiteLLM
  - [llama.cpp](./model-providers/#llama-cpp): Local inference with llama.cpp
  - [LlamaAPI](./model-providers/#llamaapi): LlamaAPI integration
  - [MistralAI](./model-providers/#mistralai): MistralAI support
  - [Ollama](./model-providers/#ollama): Ollama provider
  - [OpenAI](./model-providers/#openai): OpenAI integration
  - [SageMaker](./model-providers/#sagemaker): Amazon SageMaker integration
  - [Writer](./model-providers/#writer): Writer integration
  - [Cohere](./model-providers/#cohere): Cohere support
  - [Custom Providers](./model-providers/#custom-providers): Framework for custom providers
- [Streaming](./streaming/): Real-time, incremental responses for better user experience
  - [Overview](./streaming/#overview): Basic streaming concepts
  - [Async Iterators](./streaming/#async-iterators): Handling streaming responses
  - [Callback Handlers](./streaming/#callback-handlers): Processing streaming data
- [Multi-agent](./multi-agent/): Patterns for orchestrating multiple specialized agents
  - [Agent2Agent (A2A)](./multi-agent/#agent2agent-a2a): Direct agent communication
  - [Agents as Tools](./multi-agent/#agents-as-tools): Agents used as tools by other agents
  - [Swarm](./multi-agent/#swarm): Coordinated multi-agent systems
  - [Graph](./multi-agent/#graph): Graph-based agent orchestration
  - [Workflow](./multi-agent/#workflow): Structured multi-agent execution
  - [Multi-agent Patterns](./multi-agent/#multi-agent-patterns): Common patterns and best practices

## Additional Topics

- [Safety & Security](../safety-security/): Implementing secure and responsible AI practices
- [Observability & Evaluation](../observability-evaluation/): Monitoring and evaluating agent performance
- [Deploy](../deploy/): Best practices for production deployment