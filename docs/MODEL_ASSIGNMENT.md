# AI Model Configuration and Assignment Guide

## Overview
FeedForward uses a flexible system for managing AI models and assigning them to assignments for feedback generation.

## Setting Up Ollama with HTTPS

### For Remote Ollama Servers (like https://ollama.serveur.au)

1. **Go to Instructor Models**
   - Navigate to `/instructor/models`
   - Click "New Model"

2. **Configure Ollama**
   - **Provider**: Select "Ollama (Local)"
   - **Base URL**: Enter your full HTTPS URL (e.g., `https://ollama.serveur.au`)
   - **API Key**: Leave empty unless your server requires authentication
   - **Model ID**: Either:
     - Type manually (e.g., `llama2`, `mistral`, `codellama`)
     - Click "Fetch Available Models" after entering Base URL to see available models
   - **Display Name**: Give it a friendly name (e.g., "Ollama Llama 2")

3. **Test Connection**
   - Click "Test Connection" to verify it works
   - The system will:
     - Try to connect to your Ollama server
     - Fetch available models if possible
     - Run a test prompt

### Common Issues with Ollama

1. **SSL Certificate Errors**
   - For self-signed certificates, the connection may fail
   - Solutions:
     - Use a valid SSL certificate
     - Configure certificate verification in your environment
     - Use HTTP if the connection is secure (internal network)

2. **Connection Failures**
   - Ensure the Ollama server is running
   - Check firewall rules allow access
   - Verify the URL is correct (with or without trailing slash)

3. **No Models Available**
   - SSH into your Ollama server and pull models:
     ```bash
     ollama pull llama2
     ollama pull mistral
     ollama pull codellama
     ```

## How Models are Assigned to Assignments

### Current System Architecture

1. **Model Availability**
   - **System Models**: Configured by admins, available to all instructors
   - **Instructor Models**: Personal models configured by individual instructors
   - Both types appear in the instructor's model list

2. **Assignment Creation**
   Currently, when creating an assignment:
   - The system uses default model configurations
   - Models are selected automatically based on availability
   - Priority: Instructor's personal models > System models

3. **Feedback Generation Process**
   When a student submits work:
   1. The system checks for configured models for the assignment
   2. It runs each configured model (multiple runs possible)
   3. Feedback is aggregated from all model runs
   4. Students receive the combined feedback

### Future Enhancement: Model Selection UI

The system architecture supports per-assignment model selection, but the UI is not yet implemented. Here's what's planned:

1. **During Assignment Creation**
   - Add a "Model Configuration" section
   - Allow selecting which models to use
   - Set number of runs per model
   - Configure model parameters (temperature, max tokens)

2. **Assignment Settings**
   ```
   Model Configuration:
   [ ] System GPT-4 (3 runs)
   [✓] My Ollama Llama 2 (2 runs)
   [✓] My Claude 3 (1 run)
   ```

3. **Database Structure** (Already exists)
   - `assignment_settings` table stores configuration
   - `assignment_model_configs` links models to assignments
   - `model_runs` tracks each model execution

## Current Workaround

Until the UI is implemented, models are assigned through:

1. **System Defaults**
   - The system uses all active models
   - Default number of runs is configured in system settings

2. **Database Modification**
   - Advanced users can modify the `assignment_model_configs` table directly
   - Set `assignment_settings_id`, `ai_model_id`, and `num_runs`

## Viewing Available Models

### As an Instructor
1. Go to `/instructor/models`
2. You'll see:
   - System models (marked as "System Model")
   - Your personal models (marked as "Your Model")
   - Status (Active/Inactive)

### Testing Models
- Click on any model to view details
- Use "Test Connection" to verify it works
- Check response time and quality

## Best Practices

1. **For Ollama Users**
   - Use models appropriate for your task (e.g., `codellama` for code review)
   - Smaller models (7B) are faster but less capable
   - Larger models (70B) give better feedback but are slower

2. **Model Diversity**
   - Use multiple different models for better feedback
   - Combine fast models (Groq) with capable models (GPT-4)
   - Consider cost vs quality tradeoffs

3. **Testing**
   - Always test new models before using in production
   - Monitor response times
   - Check feedback quality with sample submissions

## Troubleshooting

### "No AI models configured for assignment"
- Ensure you have at least one active model
- Check system models are available
- Verify your personal models are active

### "Connection failed" for Ollama
- Check the base URL is correct
- Verify Ollama is running: `curl https://your-server/api/tags`
- Check network connectivity
- For HTTPS issues, try HTTP if secure

### Models Not Appearing
- Refresh the page
- Check model is marked as "active"
- Verify you have the correct permissions

## API Endpoints

- `GET /instructor/models` - List all available models
- `POST /instructor/models/new` - Create new model
- `POST /instructor/models/test` - Test model connection
- `POST /instructor/models/fetch-ollama` - Get Ollama models
- `GET /instructor/models/view/{id}` - View/edit model

## Environment Variables

For system-wide Ollama configuration:
```bash
OLLAMA_API_BASE=https://ollama.serveur.au
OLLAMA_API_KEY=optional-key-if-needed
```

These serve as defaults but can be overridden per model configuration.