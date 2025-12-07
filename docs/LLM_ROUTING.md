# LLM Model Routing Guide

This guide explains how to configure and use the LLM routing system in the AI Customer Support Agent.

## Overview

The application now supports multiple LLM providers through a unified routing system:
- **OpenRouter** - Access to multiple models (Claude, GPT-4, Llama, etc.) with one API key
- **ChatGPT** - Direct OpenAI integration
- **Claude** - Direct Anthropic integration

## Quick Start

1. **Choose your provider** by setting `LLM_PROVIDER` in your `.env` file
2. **Add your API key** for the chosen provider
3. **Restart the application** - the model router handles everything automatically

## Configuration

### Using OpenRouter (Recommended)

OpenRouter gives you access to multiple models with a single API key:

```bash
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=anthropic/claude-3-haiku
```

**Popular OpenRouter Models:**
- `anthropic/claude-3-opus` - Most powerful
- `anthropic/claude-3-sonnet` - Balanced performance
- `anthropic/claude-3-haiku` - Fast and cost-effective
- `openai/gpt-4-turbo` - GPT-4 latest
- `openai/gpt-3.5-turbo` - GPT-3.5
- `meta-llama/llama-3-70b-instruct` - Open source
- `google/gemini-pro` - Google's model

Get your API key: https://openrouter.ai/keys

### Using ChatGPT/OpenAI

```bash
LLM_PROVIDER=openai  # or "chatgpt"
OPENAI_API_KEY=sk-your-key-here
```

Get your API key: https://platform.openai.com/api-keys

### Using Claude/Anthropic

```bash
LLM_PROVIDER=anthropic  # or "claude"
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Get your API key: https://console.anthropic.com/

### Mock Mode (Development)

```bash
LLM_PROVIDER=mock
```

Uses predefined responses - no API key required.

## How It Works

The model routing is handled by `app/integrations/llm_router.py`:

```python
from app.integrations.llm_router import get_llm, get_llm_cached

# Get LLM based on settings
llm = get_llm()

# Get cached instance (recommended)
llm = get_llm_cached()

# Override provider
llm = get_llm(provider="openrouter", model_name="openai/gpt-4")
```

## Switching Models

### Method 1: Environment Variable (Recommended)

Change `LLM_PROVIDER` in `.env` and restart:

```bash
LLM_PROVIDER=openrouter  # Change this
```

### Method 2: Programmatic Override

```python
from app.integrations.llm_router import get_llm

# Use a specific provider
llm = get_llm(provider="openrouter")

# With custom model
llm = get_llm(
    provider="openrouter",
    model_name="anthropic/claude-3-sonnet",
    temperature=0.8
)
```

## Agent Configuration

Additional agent settings in `.env`:

```bash
AGENT_MAX_TOKENS=500        # Maximum response length
AGENT_TEMPERATURE=0.7       # Creativity (0.0-1.0)
AGENT_TIMEOUT_SECONDS=30    # Request timeout
```

## Architecture

```
┌─────────────┐
│   Agent     │
│   Nodes     │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│   LLM Router     │
│  (llm_router.py) │
└────────┬─────────┘
         │
    ┌────┴────┬────────┬────────┐
    ▼         ▼        ▼        ▼
┌─────────┐ ┌────┐ ┌──────┐ ┌──────┐
│OpenRouter ChatGPT│ Claude │ Mock │
└─────────┘ └────┘ └──────┘ └──────┘
```

## Key Features

✅ **Single point of configuration** - Change provider without touching code  
✅ **Automatic fallback** - Falls back to mock mode if provider fails  
✅ **Caching** - LLM instances are cached for performance  
✅ **Flexible** - Override provider per request if needed  
✅ **Clean separation** - Router handles all provider-specific logic

## Migration from Gemini

All Gemini code has been removed. To use Gemini models, use OpenRouter:

```bash
LLM_PROVIDER=openrouter
OPENROUTER_MODEL=google/gemini-pro
```

## Troubleshooting

**Error: "OPENROUTER_API_KEY not set"**
- Add your API key to `.env` file

**Error: "langchain_openai is required"**
- Run: `pip install -r requirements.txt`

**Provider not working**
- Check API key is valid
- Verify provider name is correct
- Check logs for detailed error messages

## Cost Optimization

OpenRouter provides transparent pricing and allows you to set spending limits. Compare model costs at: https://openrouter.ai/docs#models

**Recommendations:**
- **Development**: Use `mock` provider (free)
- **Testing**: Use `anthropic/claude-3-haiku` (fast, cheap)
- **Production**: Use `anthropic/claude-3-sonnet` (balanced)
- **High-quality**: Use `anthropic/claude-3-opus` or `openai/gpt-4`
