# Strands Agents SDK Documentation

Welcome to the comprehensive documentation for the Strands Agents SDK. This documentation provides everything you need to know to build production-ready, multi-agent AI systems.

BUILD PRODUCTION-READY, MULTI-AGENT AI SYSTEMS IN A FEW LINES OF CODE

Strands leverages model reasoning to plan, orchestrate tasks, and reflect on goals. It works with any LLM provider - Amazon Bedrock, OpenAI, Anthropic, local models - letting you switch providers without changing your code. The SDK provides simple primitives for handoffs, swarms, and graph workflows with built-in support for A2A. With native tools for AWS service interactions, you can deploy easily into EKS, Lambda, EC2, and more, with native MCP tool integration.

## Navigation

- [Home](./home/) - Overview of the Strands Agents SDK
- [User Guide](./user-guide/) - Comprehensive guide to using the SDK
  - [Quickstart](./user-guide/quickstart/) - Get started quickly
  - [Concepts](./user-guide/concepts/) - Core concepts and architecture
    - [Agents](./user-guide/concepts/agents/) - Agent fundamentals, loop, state, session management, prompts, hooks, structured output, conversation management
    - [Tools](./user-guide/concepts/tools/) - Tool integration, Python tools, MCP, executors, community tools package
    - [Model Providers](./user-guide/concepts/model-providers/) - Amazon Bedrock, Anthropic, LiteLLM, llama.cpp, LlamaAPI, MistralAI, Ollama, OpenAI, SageMaker, Writer, Cohere, custom providers
    - [Streaming](./user-guide/concepts/streaming/) - Real-time streaming with async iterators and callback handlers
    - [Multi-agent](./user-guide/concepts/multi-agent/) - Agent-to-Agent communication, agents as tools, swarm, graph, workflow, multi-agent patterns
  - [Safety & Security](./user-guide/safety-security/) - Responsible AI, guardrails, prompt engineering, PII redaction
  - [Observability & Evaluation](./user-guide/observability-evaluation/) - Monitoring, metrics, traces, logs, evaluation
  - [Deploy](./user-guide/deploy/) - Production operations, AWS Lambda, Fargate, Bedrock AgentCore, EKS, EC2
- [Examples](./examples/) - Practical implementation examples
  - [CLI Reference Agent Implementation](./examples/cli-reference-agent/) - Complete CLI agent example
  - [Weather Forecaster](./examples/weather/) - Weather information retrieval agent
  - [Memory Agent](./examples/memory/) - Advanced memory management example
  - [File Operations](./examples/file-ops/) - File system interaction example
  - [Agents Workflows](./examples/workflows/) - Complex agent workflow example
  - [Knowledge-Base Workflow](./examples/knowledge-base/) - Knowledge base interaction example
  - [Structured Output](./examples/structured-output/) - Structured output generation example
  - [Multi Agents](./examples/multi-agents/) - Multi-agent coordination example
  - [Cyclic Graph](./examples/cyclic-graph/) - Cyclic dependency handling example
  - [Meta Tooling](./examples/meta-tooling/) - Meta-tooling capabilities example
  - [MCP](./examples/mcp/) - Model Context Protocol example
  - [Multi-modal](./examples/multi-modal/) - Multi-modal agent example
- [API Reference](./api-reference/) - Detailed API documentation
  - [Agent](./api-reference/agent/) - Core agent classes and methods
  - [Event Loop](./api-reference/event-loop/) - Event loop implementation
  - [Experimental](./api-reference/experimental/) - Experimental features and APIs
  - [Handlers](./api-reference/handlers/) - Handler classes and interfaces
  - [Hooks](./api-reference/hooks/) - Hook mechanisms and types
  - [Models](./api-reference/models/) - Model interfaces and implementations
  - [Multiagent](./api-reference/multiagent/) - Multi-agent orchestration APIs
  - [Session](./api-reference/session/) - Session management classes
  - [Telemetry](./api-reference/telemetry/) - Telemetry and observability APIs
  - [Tools](./api-reference/tools/) - Tool interfaces and implementations
  - [Types](./api-reference/types/) - Type definitions and interfaces
- [Contribute](./contribute/) - Information for contributors

## Key Features

**MODEL DRIVEN ORCHESTRATION**
Strands leverages model reasoning to plan, orchestrate tasks, and reflect on goals

**MODEL & PROVIDER AGNOSTIC**
Work with any LLM provider - Amazon Bedrock, OpenAI, Anthropic, local models. Switch providers without changing your code.

**SIMPLE MULTI-AGENT PRIMITIVES**
Simple primitives for handoffs, swarms, and graph workflows with built-in support for A2A

**BEST IN-CLASS AWS INTEGRATIONS**
Native tools for AWS service interactions. Deploy easily into EKS, Lambda, EC2, and more. Native MCP tool integration.

The Strands Agents SDK enables you to build model-driven, multi-agent AI systems with the flexibility to work with any LLM provider while providing native AWS integrations and enterprise-ready features.