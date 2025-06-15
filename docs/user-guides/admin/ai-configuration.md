---
layout: default
title: AI Configuration
parent: Admin Guide
grand_parent: User Guides
nav_order: 3
---

# AI Configuration Guide
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Overview

FeedForward's AI configuration system allows you to integrate multiple Large Language Model (LLM) providers to generate diverse, high-quality feedback for students. This guide covers setting up AI providers, managing API keys, configuring models, and optimizing for cost and performance.

## Understanding AI Components

### Three-Level Architecture

FeedForward uses a hierarchical system for AI configuration:

1. **Providers** - Companies that offer AI services (OpenAI, Anthropic, Google)
2. **Models** - Specific AI models from providers (GPT-4, Claude-3, Gemini)
3. **Model Instances** - Configured versions with specific parameters

```
Provider (OpenAI)
  └── Model (GPT-4)
      └── Instance (GPT-4 for Essays - High Temperature)
      └── Instance (GPT-4 for Code - Low Temperature)
```

## Setting Up AI Providers

### Adding a Provider

1. Navigate to **AI Configuration** → **Providers**
2. Click **"Add New Provider"**
3. Select provider type from the dropdown

### OpenAI Configuration

```yaml
Provider Details:
  Name: OpenAI
  Type: openai
  Display Name: OpenAI GPT Models

API Configuration:
  API Key: sk-...your-key-here
  Organization ID: org-... (optional)
  API Base URL: https://api.openai.com/v1 (default)
  
Advanced Settings:
  Request Timeout: 60 seconds
  Max Retries: 3
  Rate Limit: 60 requests/minute
```

{: .tip }
> For Azure OpenAI, use a custom API Base URL and add the API Version.

### Anthropic Configuration

```yaml
Provider Details:
  Name: Anthropic
  Type: anthropic
  Display Name: Claude Models

API Configuration:
  API Key: sk-ant-api...your-key-here
  API Base URL: https://api.anthropic.com (default)
  
Advanced Settings:
  Request Timeout: 120 seconds
  Max Retries: 3
  Rate Limit: 50 requests/minute
```

### Google AI Configuration

```yaml
Provider Details:
  Name: Google AI
  Type: google
  Display Name: Google Gemini

API Configuration:
  API Key: AI...your-key-here
  # OR for Vertex AI:
  Service Account JSON: (upload file)
  Project ID: your-gcp-project
  Location: us-central1
```

### Local Models (Ollama)

```yaml
Provider Details:
  Name: Ollama Local
  Type: ollama
  Display Name: Local LLM Models

API Configuration:
  Base URL: http://localhost:11434
  No API Key Required
  
Note: Requires Ollama running locally
```

### Testing Provider Connection

After adding a provider:

1. Click **"Test Connection"**
2. System will verify:
   - API key validity
   - Network connectivity
   - Available models
3. Review test results
4. Save configuration if successful

## Managing API Keys

### Security Best Practices

1. **API Key Storage**
   - Keys are encrypted using Fernet encryption
   - Stored in database with AES-256
   - Never logged or displayed in full
   - Accessible only to admin role

2. **Key Rotation**
   - Set reminders for regular rotation
   - Keep previous key during transition
   - Update all model instances
   - Test before removing old key

3. **Access Control**
   - System-wide keys (admin only)
   - Instructor keys (optional feature)
   - Audit trail for key usage
   - IP restrictions where supported

### Adding API Keys

1. In provider configuration, locate **API Key** field
2. Paste your key (will be masked after save)
3. Click **"Validate Key"**
4. Save configuration

{: .warning }
> Never share API keys via email or messaging. Always enter them directly into the system.

### Monitoring API Usage

1. Go to **AI Configuration** → **Usage Monitor**
2. View metrics by:
   - Provider
   - Model
   - Time period
   - Cost estimates

```
Example Dashboard:
- OpenAI GPT-4: 1,234 requests ($12.34)
- Anthropic Claude: 567 requests ($5.67)
- Total this month: $18.01
```

## Configuring AI Models

### Adding Models

1. Navigate to **AI Configuration** → **Models**
2. Click **"Add Model"**
3. Fill in model details:

```yaml
Basic Information:
  Provider: OpenAI (select from dropdown)
  Model ID: gpt-4-turbo-preview
  Display Name: GPT-4 Turbo
  Description: Latest GPT-4 with 128k context

Capabilities:
  Max Tokens: 4096
  Context Window: 128000
  Supports Functions: Yes
  Supports Vision: Yes
  
Cost Information:
  Input Cost: $0.01 per 1k tokens
  Output Cost: $0.03 per 1k tokens
  
Availability:
  Status: Active
  Available to: All Instructors
```

### Model Parameters

Configure default parameters for each model:

```yaml
Generation Parameters:
  Temperature: 0.7 (0.0-2.0)
  Top P: 1.0 (0.0-1.0)
  Frequency Penalty: 0.0 (-2.0-2.0)
  Presence Penalty: 0.0 (-2.0-2.0)
  
Response Settings:
  Max Output Tokens: 2000
  Stop Sequences: ["\n\n", "END"]
  Response Format: text
  
Safety Settings:
  Content Filter: Enabled
  Personal Info Filter: Enabled
  Profanity Filter: Enabled
```

### Creating Model Instances

Model instances allow different configurations of the same model:

1. Go to **AI Configuration** → **Model Instances**
2. Click **"Create Instance"**
3. Configure:

```yaml
Instance Name: GPT-4 Essay Feedback
Base Model: GPT-4 Turbo
Description: Optimized for essay feedback

Parameter Overrides:
  Temperature: 0.8 (more creative)
  Max Tokens: 3000 (longer responses)
  
System Prompt: |
  You are an experienced writing instructor providing
  constructive feedback on student essays. Focus on
  improvement rather than just criticism.
  
Usage Restrictions:
  Available for: Essay assignments
  Department: English, Humanities
```

## System-Wide AI Settings

### Default Models

Set system defaults for different contexts:

1. Navigate to **Settings** → **AI Defaults**
2. Configure:

```yaml
Default Models:
  Primary Feedback: GPT-4 Turbo
  Quick Feedback: GPT-3.5 Turbo
  Code Review: Claude-3 Opus
  
Fallback Chain:
  1. Primary Model
  2. Secondary Model
  3. Tertiary Model
  
Error Handling:
  On Model Failure: Use fallback
  On Provider Failure: Queue for retry
  Max Retries: 3
```

### Aggregation Settings

When using multiple models or runs:

```yaml
Aggregation Methods:
  Available Methods:
    - Average (mean of all scores)
    - Weighted Average (based on model confidence)
    - Maximum (highest score)
    - Median (middle score)
    - Consensus (most common)
  
Default Method: Weighted Average

Confidence Weights:
  GPT-4: 1.0
  Claude-3: 0.95
  GPT-3.5: 0.8
  Local Models: 0.7
```

### Rate Limiting

Protect against excessive usage:

```yaml
Global Limits:
  Total API Calls/Day: 10000
  Per Provider/Hour: 1000
  Per Instructor/Day: 500
  Per Student/Day: 20
  
Burst Limits:
  Requests/Minute: 60
  Concurrent Requests: 10
  Queue Size: 1000
  
Cost Controls:
  Daily Spend Limit: $100
  Alert Threshold: 80%
  Auto-Pause at Limit: Yes
```

## Cost Management

### Setting Cost Alerts

1. Go to **AI Configuration** → **Cost Management**
2. Configure alerts:

```yaml
Alert Thresholds:
  Daily: $50, $75, $100
  Monthly: $500, $1000, $1500
  
Alert Recipients:
  - admin@university.edu
  - billing@university.edu
  
Actions on Limit:
  Soft Limit (80%): Email alert
  Hard Limit (100%): Pause non-essential
  Emergency: Pause all AI calls
```

### Cost Optimization Strategies

1. **Model Selection**
   - Use expensive models sparingly
   - Quick feedback with cheaper models
   - Premium models for final drafts

2. **Prompt Optimization**
   - Shorter, focused prompts
   - Reuse successful prompts
   - Cache common responses

3. **Usage Patterns**
   - Batch processing during off-peak
   - Limit retries and regenerations
   - Set per-course budgets

### Cost Reports

Generate usage reports:

1. Navigate to **Reports** → **AI Usage**
2. Select parameters:
   - Date range
   - Group by (provider/model/course)
   - Include projections
3. Export as CSV/PDF

## Advanced Configuration

### Custom Providers

Add non-standard providers:

1. Go to **AI Configuration** → **Custom Providers**
2. Define provider:

```yaml
Provider Configuration:
  Name: Custom LLM
  Base URL: https://api.custom-llm.com
  Auth Type: Bearer Token
  
Request Format:
  Endpoint: /v1/completions
  Method: POST
  Headers:
    Authorization: Bearer {api_key}
    Content-Type: application/json
    
Response Parsing:
  Success Path: $.choices[0].text
  Error Path: $.error.message
```

### Prompt Engineering

Create reusable prompt templates:

1. Navigate to **AI Configuration** → **Prompt Templates**
2. Create template:

```yaml
Template Name: Essay Feedback Standard
Variables:
  - rubric_criteria
  - word_count
  - assignment_type
  
Template: |
  Analyze this {assignment_type} based on the rubric.
  
  Rubric criteria:
  {rubric_criteria}
  
  Expected length: {word_count} words
  
  Provide specific, actionable feedback for improvement.
```

### A/B Testing

Test different models or configurations:

1. Go to **AI Configuration** → **Experiments**
2. Create experiment:

```yaml
Experiment: Model Comparison
Duration: 2 weeks
Sample Size: 100 submissions

Variants:
  A: GPT-4 (50%)
  B: Claude-3 (50%)
  
Metrics:
  - Student satisfaction
  - Instructor approval rate
  - Cost per feedback
```

## Troubleshooting

### Common Issues

**API Key Invalid**
- Verify key is active
- Check for typos
- Ensure correct provider
- Verify billing active

**Model Not Available**
- Check provider status
- Verify model ID
- Ensure region access
- Check quota limits

**High Latency**
- Review timeout settings
- Check network connectivity
- Consider closer regions
- Optimize prompt length

**Inconsistent Results**
- Adjust temperature
- Improve prompt clarity
- Check model version
- Consider different model

### Monitoring and Logs

Access AI-specific logs:

1. Go to **System** → **Logs** → **AI Calls**
2. Filter by:
   - Provider
   - Status (success/failure)
   - Response time
   - Error type

## Best Practices

### Model Selection

1. **Match Model to Task**
   - Essays: High creativity models
   - Code: Precise, technical models
   - Math: Logical reasoning models

2. **Consider Context Length**
   - Long assignments need large context
   - Chunk if necessary
   - Monitor token usage

3. **Balance Quality/Cost**
   - Premium for final feedback
   - Standard for drafts
   - Quick for real-time

### Prompt Design

1. **Clear Instructions**
   - Specific evaluation criteria
   - Desired output format
   - Tone and style

2. **Include Context**
   - Assignment details
   - Rubric criteria
   - Student level

3. **Iterative Improvement**
   - Monitor feedback quality
   - Gather instructor input
   - Refine prompts

## Next Steps

- [Maintenance Guide](./maintenance) - Keep your AI system running smoothly
- [Instructor AI Settings](/user-guides/instructor/assignments#ai-configuration) - How instructors use AI
- [Privacy & Security](/technical/privacy-security) - AI data handling

---

{: .note }
> AI models and pricing change frequently. Check provider documentation for the latest information.