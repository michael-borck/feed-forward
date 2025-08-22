# FeedForward LLM Integration Setup Guide

## Overview
FeedForward uses LiteLLM to support multiple AI providers for generating educational feedback. This guide covers setting up and managing LLM integrations.

## Quick Start

### 1. Configure API Keys
Run the interactive setup script to configure your API keys:

```bash
python tools/setup_api_keys.py
```

This will guide you through:
- Configuring API keys for OpenAI, Anthropic, Google, Groq, or Ollama
- Testing each provider's connectivity
- Saving configuration to your `.env` file

### 2. Check Provider Health
Verify all configured providers are working:

```bash
python tools/check_llm_health.py
```

For continuous monitoring:
```bash
python tools/check_llm_health.py --monitor --interval 30
```

### 3. Test the Integration
Run the AI integration test to verify everything works end-to-end:

```bash
python tools/test_ai_integration.py
```

## Supported Providers

| Provider | Models | Environment Variable |
|----------|--------|---------------------|
| OpenAI | GPT-4o, GPT-3.5-turbo | `OPENAI_API_KEY` |
| Anthropic | Claude 3 Sonnet, Haiku | `ANTHROPIC_API_KEY` |
| Google | Gemini 1.5 Pro, Flash | `GOOGLE_API_KEY` |
| Groq | Llama 3.1 | `GROQ_API_KEY` |
| Ollama | Local models | `OLLAMA_API_BASE` |

## Features Implemented

### 1. **API Key Management**
- Automatic detection of API keys from environment variables
- Encrypted storage for instructor-specific keys
- Interactive setup script for configuration
- Validation of API keys before use

### 2. **Error Handling**
- Clear error messages when API keys are missing
- Helpful instructions for configuration
- Graceful degradation with mock feedback
- Retry logic with exponential backoff

### 3. **Health Monitoring**
- Provider health check tool
- Real-time status monitoring
- Response time tracking
- Automatic detection of issues (rate limits, auth errors, etc.)

### 4. **Mock Feedback Fallback**
- Automatic fallback to mock feedback when no API keys configured
- Simulated feedback that follows rubric structure
- Clear indication that feedback is simulated
- Useful for testing and demonstrations

### 5. **Multi-Model Support**
- Run multiple models concurrently
- Aggregate feedback from multiple sources
- Configurable aggregation methods (mean, weighted mean, median, trimmed mean)
- Support for model-specific configurations

## Configuration Files

### `.env` File
Your API keys and configuration are stored in the `.env` file:

```env
# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Google
GOOGLE_API_KEY=AIza...

# Groq
GROQ_API_KEY=gsk_...

# Ollama (Local)
OLLAMA_API_BASE=http://localhost:11434
```

### Database Configuration
AI models are configured in the database via `app/init_db.py`. Default models include:
- GPT-4o (OpenAI)
- Claude 3 Sonnet (Anthropic)
- Gemini 1.5 Pro (Google)

## Troubleshooting

### No API Keys Configured
If you see "No API keys configured" errors:
1. Run `python tools/setup_api_keys.py`
2. Enter at least one provider's API key
3. Verify with `python tools/check_llm_health.py`

### Connection Errors
For Ollama connection errors:
1. Install Ollama: https://ollama.ai
2. Start Ollama: `ollama serve`
3. Pull a model: `ollama pull llama3.2`

### Rate Limits
If experiencing rate limits:
1. Wait for the limit to reset
2. Consider using multiple providers
3. Reduce the number of concurrent model runs

### Authentication Errors
For "Invalid API key" errors:
1. Verify your API key is correct
2. Check the provider's dashboard for key status
3. Regenerate the key if needed

## Development Tips

### Testing Without API Keys
The system will automatically use mock feedback when no API keys are configured. This is useful for:
- Local development
- UI testing
- Demonstrations

### Adding New Providers
To add a new provider:
1. Update `app/utils/ai_client.py` with provider mapping
2. Add to `tools/setup_api_keys.py` PROVIDERS dict
3. Update `app/init_db.py` with default models
4. Test with `tools/check_llm_health.py`

### Cost Management
- Monitor usage through provider dashboards
- Set spending limits on provider accounts
- Use cheaper models for development/testing
- Consider local models (Ollama) for development

## Next Steps

1. **Configure API Keys**: Start with at least one provider
2. **Test Integration**: Run the test scripts to verify setup
3. **Create Content**: Add courses, assignments, and rubrics
4. **Submit Drafts**: Test the feedback generation pipeline
5. **Monitor Health**: Use the health check tool to monitor providers

## Support

For issues or questions:
- Check logs in the application output
- Run health checks to diagnose provider issues
- Review this guide for configuration steps
- Check provider-specific documentation for API details