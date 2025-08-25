# LLM Provider Configuration Guide

FeedForward supports multiple LLM providers through LiteLLM, allowing flexibility in choosing AI models for feedback generation.

## Supported Providers

### 1. OpenAI
- **Models**: GPT-4, GPT-4 Turbo, GPT-3.5 Turbo
- **API Key**: `OPENAI_API_KEY`
- **Get Key**: https://platform.openai.com/api-keys

### 2. Anthropic (Claude)
- **Models**: Claude 3 Opus, Claude 3 Sonnet, Claude 3 Haiku
- **API Key**: `ANTHROPIC_API_KEY`
- **Get Key**: https://console.anthropic.com/settings/keys

### 3. Google (PaLM/Bard)
- **Models**: text-bison, chat-bison
- **API Key**: `GOOGLE_API_KEY`
- **Get Key**: https://makersuite.google.com/app/apikey

### 4. Google Gemini
- **Models**: gemini-1.5-flash, gemini-1.5-pro, gemini-ultra
- **API Key**: `GEMINI_API_KEY`
- **Get Key**: https://aistudio.google.com/app/apikey

### 5. Groq
- **Models**: Llama 3.1, Mixtral, Gemma
- **API Key**: `GROQ_API_KEY`
- **Get Key**: https://console.groq.com/keys
- **Note**: Very fast inference with Groq's LPU technology

### 6. Ollama (Local Models)
- **Models**: llama3.2, mistral, phi, codellama, and more
- **Base URL**: `OLLAMA_API_BASE` (default: http://localhost:11434)
- **API Key**: `OLLAMA_API_KEY` (optional, for secured instances)
- **Setup**: Install from https://ollama.ai

### 7. OpenRouter
- **Models**: Access to 100+ models through one API
- **API Key**: `OPENROUTER_API_KEY`
- **Get Key**: https://openrouter.ai/keys
- **Note**: Automatic model routing and fallbacks

### 8. Custom OpenAI-Compatible
- **Models**: Any OpenAI-compatible endpoint
- **Base URL**: `CUSTOM_LLM_BASE_URL` (required)
- **API Key**: `CUSTOM_LLM_API_KEY`
- **Examples**: Together AI, Anyscale, vLLM, FastChat

## Configuration Methods

### Method 1: Environment Variables (System-wide)

Add to your `.env` file:

```bash
# Choose the providers you want to use
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...
GROQ_API_KEY=gsk_...
OPENROUTER_API_KEY=sk-or-...

# For Ollama (local)
OLLAMA_API_BASE=http://localhost:11434
OLLAMA_API_KEY=optional-key

# For custom endpoints
CUSTOM_LLM_BASE_URL=https://api.together.xyz/v1
CUSTOM_LLM_API_KEY=your-key
```

### Method 2: Interactive Setup Tool

Run the setup tool for guided configuration:

```bash
python tools/setup_api_keys.py
```

This tool will:
- Guide you through provider selection
- Test your API keys
- Save configuration to `.env`

### Method 3: Web UI Configuration

#### Admin (System-wide Models)
1. Login as admin
2. Navigate to `/admin/ai-models`
3. Click "Add New Model"
4. Configure provider, API key, and settings
5. Models become available to all instructors

#### Instructor (Personal Models)
1. Login as instructor
2. Navigate to `/instructor/models`
3. Click "New Model"
4. Configure your personal API key
5. Models are private to your account

## Model Configuration in UI

When adding a model through the UI, you'll need:

1. **Provider**: Select from dropdown
2. **Model ID**: The specific model identifier
   - OpenAI: `gpt-4`, `gpt-3.5-turbo`
   - Anthropic: `claude-3-opus-20240229`
   - Gemini: `gemini-1.5-pro`, `gemini-1.5-flash`
   - Groq: `llama-3.1-8b-instant`, `mixtral-8x7b-32768`
   - Ollama: `llama3.2`, `mistral`, `phi`
3. **Display Name**: Friendly name for the UI
4. **API Key**: Your provider API key (encrypted)
5. **Base URL**: Only for custom/Ollama providers

## Access Control

- **System Models**: Configured by admins, available to all instructors
- **Instructor Models**: Private to individual instructors
- **API Keys**: Encrypted in database using Fernet encryption
- **Environment Variables**: Take precedence over database configuration

## Testing Your Configuration

### Using the Health Check Tool

```bash
python tools/check_llm_health.py
```

### Testing in the UI

When adding a model, use the "Test Connection" button to verify:
- API key validity
- Model availability
- Network connectivity

## Troubleshooting

### Connection Errors

**Ollama**: Ensure Ollama is running
```bash
ollama serve
ollama list  # Check available models
```

**Custom Endpoints**: Verify the base URL format
- Should end with `/v1` for OpenAI-compatible
- Example: `https://api.together.xyz/v1`

### API Key Issues

- Check environment variables are loaded: `echo $OPENAI_API_KEY`
- Verify key format matches provider requirements
- Ensure keys have necessary permissions/credits

### Rate Limits

- Consider using multiple providers for load distribution
- OpenRouter provides automatic fallbacks
- Implement retry logic in production

## Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** for production deployments
3. **Rotate keys regularly**
4. **Set spending limits** on provider dashboards
5. **Use read-only keys** where possible
6. **Monitor usage** through provider dashboards

## Cost Optimization

- **Development**: Use Ollama for local testing (free)
- **Low volume**: Groq offers free tier with fast inference
- **Production**: OpenRouter for automatic cost optimization
- **High volume**: Consider self-hosted with vLLM or FastChat