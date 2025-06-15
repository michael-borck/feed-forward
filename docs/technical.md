---
layout: default
title: Technical Documentation
nav_order: 4
has_children: true
permalink: /technical
---

# Technical Documentation
{: .no_toc }

In-depth technical details for developers and system administrators.
{: .fs-6 .fw-300 }

This section provides comprehensive technical documentation for understanding, deploying, and extending FeedForward.

## Documentation Overview

### System Design
- **[Architecture](./technical/architecture)** - System design and component overview
- **[Database Schema](./technical/database-schema)** - Complete database structure reference
- **[Privacy & Security](./technical/privacy-security)** - Security model and privacy implementation

### Integration & APIs
- **[AI Integration](./technical/ai-integration)** - How feedback generation works with multiple LLMs
- **[API Reference](./technical/api-reference)** - Complete endpoint documentation

### Development
- **[Development Setup](./technical/development-setup)** - Setting up a development environment
- **[Contributing](./technical/contributing)** - Guidelines for contributing to FeedForward

---

## Key Technologies

FeedForward is built with:
- **FastHTML** - Python web framework combining Starlette, Uvicorn, and HTMX
- **SQLite** with FastLite ORM - Lightweight, serverless database
- **LiteLLM** - Unified interface for multiple LLM providers
- **Python 3.8+** - Modern Python with type hints

## Architecture Highlights

- **Privacy-First Design** - Student submissions are temporarily stored and automatically cleaned
- **Multi-Provider AI Support** - Seamlessly integrate OpenAI, Anthropic, Google, and local models
- **Role-Based Access Control** - Three distinct user roles with appropriate permissions
- **Asynchronous Processing** - Background tasks for feedback generation
- **Rubric-Based Assessment** - Structured feedback aligned with educational objectives