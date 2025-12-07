"""LLM Model Routing - Centralized model management for OpenRouter, ChatGPT, and Claude."""

import os
from typing import Optional, Any
from dotenv import load_dotenv
from langchain_core.utils.utils import secret_from_env
from pydantic import Field, SecretStr

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None

try:
    from langchain_anthropic import ChatAnthropic
except ImportError:
    ChatAnthropic = None

from app.config import settings
from app.utils.logger import log

load_dotenv()


class ChatOpenRouter(ChatOpenAI):
    """OpenRouter LLM client extending ChatOpenAI."""
    
    openai_api_key: Optional[SecretStr] = Field(
        alias="api_key",
        default_factory=secret_from_env("OPENROUTER_API_KEY", default=None),
    )
    
    @property
    def lc_secrets(self) -> dict[str, str]:
        return {"openai_api_key": "OPENROUTER_API_KEY"}

    def __init__(self,
                 openai_api_key: Optional[str] = None,
                 **kwargs):
        """
        Initialize OpenRouter client.
        
        Args:
            openai_api_key: OpenRouter API key
            **kwargs: Additional arguments passed to ChatOpenAI
        """
        openai_api_key = (
            openai_api_key or os.environ.get("OPENROUTER_API_KEY")
        )
        super().__init__(
            base_url="https://openrouter.ai/api/v1",
            openai_api_key=openai_api_key,
            **kwargs
        )


def get_openrouter_llm(
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    **kwargs
) -> Any:
    """
    Get OpenRouter LLM instance.
    
    Args:
        model_name: Model identifier (e.g., "anthropic/claude-3-sonnet", "openai/gpt-4")
        temperature: Sampling temperature
        max_tokens: Maximum tokens in response
        **kwargs: Additional arguments
        
    Returns:
        Configured ChatOpenRouter instance
    """
    if ChatOpenAI is None:
        raise ImportError("langchain_openai is required for OpenRouter. Install with: pip install langchain-openai")
    
    if not settings.openrouter_api_key:
        raise ValueError("OPENROUTER_API_KEY not set in environment or settings")
    
    model_name = model_name or settings.openrouter_model
    temperature = temperature if temperature is not None else settings.agent_temperature
    max_tokens = max_tokens if max_tokens is not None else settings.agent_max_tokens
    
    log.info(f"Initializing OpenRouter LLM with model: {model_name}")
    
    return ChatOpenRouter(
        openai_api_key=settings.openrouter_api_key,
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs
    )


def get_chatgpt_llm(
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    **kwargs
) -> Any:
    """
    Get ChatGPT (OpenAI) LLM instance.
    
    Args:
        model_name: Model identifier (e.g., "gpt-4", "gpt-3.5-turbo")
        temperature: Sampling temperature
        max_tokens: Maximum tokens in response
        **kwargs: Additional arguments
        
    Returns:
        Configured ChatOpenAI instance
    """
    if ChatOpenAI is None:
        raise ImportError("langchain_openai is required for ChatGPT. Install with: pip install langchain-openai")
    
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY not set in environment or settings")
    
    model_name = model_name or "gpt-3.5-turbo"
    temperature = temperature if temperature is not None else settings.agent_temperature
    max_tokens = max_tokens if max_tokens is not None else settings.agent_max_tokens
    
    log.info(f"Initializing ChatGPT LLM with model: {model_name}")
    
    return ChatOpenAI(
        api_key=settings.openai_api_key,
        model=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs
    )


def get_claude_llm(
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    **kwargs
) -> Any:
    """
    Get Claude (Anthropic) LLM instance.
    
    Args:
        model_name: Model identifier (e.g., "claude-3-opus-20240229", "claude-3-sonnet-20240229")
        temperature: Sampling temperature
        max_tokens: Maximum tokens in response
        **kwargs: Additional arguments
        
    Returns:
        Configured ChatAnthropic instance
    """
    if ChatAnthropic is None:
        raise ImportError("langchain_anthropic is required for Claude. Install with: pip install langchain-anthropic")
    
    if not settings.anthropic_api_key:
        raise ValueError("ANTHROPIC_API_KEY not set in environment or settings")
    
    model_name = model_name or "claude-3-haiku-20240307"
    temperature = temperature if temperature is not None else settings.agent_temperature
    max_tokens = max_tokens if max_tokens is not None else settings.agent_max_tokens
    
    log.info(f"Initializing Claude LLM with model: {model_name}")
    
    return ChatAnthropic(
        api_key=settings.anthropic_api_key,
        model=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs
    )


def get_llm(provider: Optional[str] = None, **kwargs) -> Any:
    """
    Get LLM instance based on provider configuration.
    
    This is the main entry point for getting an LLM. It routes to the appropriate
    provider based on settings or the provider argument.
    
    Args:
        provider: LLM provider ("openrouter", "openai", "anthropic", "chatgpt", "claude")
                 If None, uses settings.llm_provider
        **kwargs: Additional arguments passed to the specific LLM constructor
        
    Returns:
        Configured LLM instance
        
    Raises:
        ValueError: If provider is invalid or not configured
        
    Example:
        # Use configured provider
        llm = get_llm()
        
        # Override provider
        llm = get_llm(provider="openrouter", model_name="anthropic/claude-3-sonnet")
        
        # Use ChatGPT specifically
        llm = get_llm(provider="chatgpt", model_name="gpt-4")
    """
    provider = provider or settings.llm_provider
    provider = provider.lower().strip()
    
    log.info(f"Routing to LLM provider: {provider}")
    
    if provider in ("openrouter", "open_router"):
        return get_openrouter_llm(**kwargs)
    elif provider in ("openai", "chatgpt", "gpt"):
        return get_chatgpt_llm(**kwargs)
    elif provider in ("anthropic", "claude"):
        return get_claude_llm(**kwargs)
    elif provider == "mock":
        log.warning("Mock provider selected - returning None (use mock responses)")
        return None
    else:
        raise ValueError(
            f"Invalid LLM provider: {provider}. "
            f"Valid options: openrouter, openai, chatgpt, anthropic, claude, mock"
        )


# Singleton instance for reuse
_llm_instance = None
_llm_provider = None


def get_llm_cached(provider: Optional[str] = None, **kwargs) -> Any:
    """
    Get cached LLM instance. Creates new instance if provider changed.
    
    Args:
        provider: LLM provider
        **kwargs: Additional arguments
        
    Returns:
        Cached or new LLM instance
    """
    global _llm_instance, _llm_provider
    
    current_provider = provider or settings.llm_provider
    
    # Return cached instance if provider hasn't changed
    if _llm_instance is not None and _llm_provider == current_provider:
        log.debug(f"Returning cached LLM instance for provider: {current_provider}")
        return _llm_instance
    
    # Create new instance
    log.info(f"Creating new LLM instance for provider: {current_provider}")
    _llm_instance = get_llm(provider=provider, **kwargs)
    _llm_provider = current_provider
    
    return _llm_instance


def reset_llm_cache():
    """Reset the cached LLM instance. Useful when changing configuration."""
    global _llm_instance, _llm_provider
    log.info("Resetting LLM cache")
    _llm_instance = None
    _llm_provider = None
