# Agent MCP Management System

This project provides a comprehensive framework for managing Model Context Protocol (MCP) services through intelligent agents built with the Strands Agents SDK.

## Overview

This system contains various MCP servers and corresponding agents that provide access to external tools and services for LLMs. The agents enable LLMs to interact with different systems like email, CRM, system administration tools, documentation, and more through standardized interfaces.

## MCP Servers

The `/mcps` directory contains various MCP servers that expose functionality through the Model Context Protocol:

- `backup_restore_mcp_server.py` - Backup and restore operations
- `chatbot_mcp_server.py` - Chatbot functionality
- `customer_feedback_mcp_server.py` - Customer feedback management
- `discord_mcp_server.py` - Discord integration
- `dokploy_mcp_server.py` - Dokploy deployment management
- `fastmcp_docs_server.py` - FastMCP documentation access
- `firewall_mcp_server.py` - Firewall management
- `gmail_mcp_server.py` - Gmail operations
- `go_high_level_mcp_server.py` - Go High Level CRM operations
- `google_calendar_mcp_server.py` - Google Calendar operations
- `google_docs_mcp_server.py` - Google Docs operations
- `google_drive_mcp_server.py` - Google Drive operations
- `google_forms_mcp_server.py` - Google Forms operations
- `google_meet_mcp_server.py` - Google Meet operations
- `google_sheets_mcp_server.py` - Google Sheets operations
- `interview_scheduler_mcp_server.py` - Interview scheduling
- `invoice_mcp_server.py` - Invoice management
- `linux_admin_mcp_server.py` - Linux system administration
- `log_viewer_mcp_server.py` - Log viewing and analysis
- `mailchimp_mcp_server.py` - Mailchimp integration
- `meta_fastmcp_server.py` - Meta MCP operations
- `payment_reminder_mcp_server.py` - Payment reminders
- `port_scanner_mcp_server.py` - Network port scanning
- `process_manager_mcp_server.py` - Process management
- `proposal_generator_mcp_server.py` - Proposal generation
- `server_health_mcp_server.py` - Server health monitoring
- `slack_mcp_server.py` - Slack integration
- `smtp_mcp_server.py` - SMTP email operations
- `system_monitoring_mcp_server.py` - System monitoring
- `trello_mcp_server.py` - Trello integration
- `twenty_crm_mcp_server.py` - Twenty CRM operations
- `woocommerce_mcp_server.py` - WooCommerce operations

## Agents

The `/agents` directory contains intelligent agents built with the Strands Agents SDK that utilize the MCP services:

### Basic Agents
- `simple_agent.py` - Basic functionality with time, calculator, echo, system info tools
- `file_operations_agent.py` - File system operations agent

### Communication & Collaboration Agents
- `email_management_agent.py` - Email operations using Gmail, SMTP, and Google Calendar
- `gmail_agent.py` - Gmail-specific operations
- `smtp_email_agent.py` - SMTP email operations
- `discord_agent.py` - Discord integration
- `slack_mcp_server.py` - Slack integration
- `google_calendar_mcp_server.py` - Google Calendar operations
- `google_meet_mcp_server.py` - Google Meet operations
- `trello_mcp_server.py` - Trello integration
- `google_forms_mcp_server.py` - Google Forms operations
- `collaboration_agent.py` - Multi-platform collaboration tools

### Business Operations Agents
- `business_ops_agent.py` - Multi-business operations
- `crm_business_ops_agent.py` - CRM and business operations combining Twenty CRM, Go High Level, Customer Feedback, Invoice, Proposal Generator, Interview Scheduler, and Mailchimp
- `ghl_crm_agent.py` - Go High Level CRM
- `twenty_crm_mcp_server.py` - Twenty CRM operations
- `customer_feedback_mcp_server.py` - Customer feedback management
- `invoice_mcp_server.py` - Invoice management
- `proposal_generator_mcp_server.py` - Proposal generation
- `interview_scheduler_mcp_server.py` - Interview scheduling
- `mailchimp_mcp_server.py` - Mailchimp marketing operations
- `payment_reminder_agent.py` - Payment reminder operations

### System & DevOps Agents
- `system_admin_agent.py` - System administration combining Linux Admin, Process Manager, Server Health, Log Viewer, Firewall
- `security_monitoring_agent.py` - Security monitoring combining Firewall, Server Health, System Monitoring, Port Scanner
- `devops_agent.py` - DevOps operations combining Dokploy, Linux admin, system monitoring
- `dokploy_mcp_server.py` - Dokploy deployment management
- `linux_admin_mcp_server.py` - Linux system administration
- `server_health_mcp_server.py` - Server health monitoring
- `system_monitoring_mcp_server.py` - System monitoring
- `process_manager_mcp_server.py` - Process management
- `log_viewer_mcp_server.py` - Log viewing and analysis
- `firewall_mcp_server.py` - Firewall management
- `port_scanner_mcp_server.py` - Network port scanning

### Documentation & Data Management Agents
- `doc_sys_management_agent.py` - Documentation and system management combining Dokploy, Google Drive, Google Docs, Google Sheets
- `fastmcp_docs_agent.py` - FastMCP documentation access
- `google_drive_mcp_server.py` - Google Drive operations
- `google_docs_mcp_server.py` - Google Docs operations
- `google_sheets_agent.py` - Google Sheets operations

### E-commerce & Specialized Agents
- `ecommerce_agent.py` - WooCommerce e-commerce operations
- `woocommerce_mcp_server.py` - WooCommerce operations
- `backup_restore_agent.py` - Backup and restore operations
- `chatbot_agent.py` - Chatbot operations

## Requirements

- Python 3.8+
- `strandsagents` - The Strands Agents SDK
- `fastmcp` - FastMCP framework
- `psutil` - System monitoring
- `python-dotenv` - Environment variable management

## Usage

Each agent can be run independently using Python:

```bash
python agents/simple_agent.py
```

The agents are designed to work with LLMs that support the Model Context Protocol, enabling AI systems to access external tools and services.

## Documentation

The `/docs/strandagents-docs/` directory contains comprehensive documentation for the Strands Agents SDK with examples for implementing agents, tools, and multi-agent systems.

## Architecture

The system follows the Model Context Protocol (MCP) standard, enabling LLMs to access external tools and services through standardized interfaces. The Strands Agents SDK provides the framework for creating intelligent agents that can coordinate multiple MCP services for complex operations.