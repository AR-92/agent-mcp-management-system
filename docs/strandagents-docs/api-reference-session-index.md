# Session API Reference

Documentation for session management classes in the Strands Agents SDK.

## Overview

The Session API provides mechanisms to group related interactions and maintain conversation context across multiple exchanges with agents.

## Core Classes

### Session Manager
- `create_session()`: Create a new session
- `get_session()`: Retrieve an existing session
- `end_session()`: End a session cleanly

### Session State
- `update_context()`: Update session context
- `get_history()`: Retrieve session conversation history
- `clear_context()`: Clear session context

### Session Persistence
- `serialize()`: Serialize session state
- `deserialize()`: Deserialize session from storage
- `save_to_store()`: Persist session to storage

## Lifecycle Management

The API handles session creation, maintenance, and cleanup with support for both in-memory and persistent storage backends.

More details about the Session API including comprehensive method documentation, usage examples, and implementation details would be available in the full documentation.