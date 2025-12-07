"""
Example: How to use the LLM Router

This file demonstrates different ways to configure and use the LLM routing system.
"""

from app.integrations.llm_router import get_llm, get_llm_cached, reset_llm_cache
from app.config import settings

# ============================================================================
# Example 1: Using Default Provider from Settings
# ============================================================================
print("Example 1: Using default provider from .env")
print(f"Current provider: {settings.llm_provider}")

# Get LLM using settings configuration
llm = get_llm()
print(f"LLM initialized: {type(llm).__name__ if llm else 'Mock'}\n")


# ============================================================================
# Example 2: Using OpenRouter
# ============================================================================
print("Example 2: Using OpenRouter with Claude 3 Haiku")

try:
    llm_openrouter = get_llm(
        provider="openrouter",
        model_name="anthropic/claude-3-haiku",
        temperature=0.7
    )
    print(f"OpenRouter LLM: {type(llm_openrouter).__name__}")
    
    # Use it with LangChain
    # response = await llm_openrouter.ainvoke("Hello, how are you?")
    # print(f"Response: {response}")
except Exception as e:
    print(f"Error: {e}")
print()


# ============================================================================
# Example 3: Using ChatGPT (OpenAI)
# ============================================================================
print("Example 3: Using ChatGPT")

try:
    llm_chatgpt = get_llm(
        provider="chatgpt",
        model_name="gpt-3.5-turbo",
        temperature=0.8,
        max_tokens=1000
    )
    print(f"ChatGPT LLM: {type(llm_chatgpt).__name__}")
except Exception as e:
    print(f"Error: {e}")
print()


# ============================================================================
# Example 4: Using Claude (Anthropic)
# ============================================================================
print("Example 4: Using Claude")

try:
    llm_claude = get_llm(
        provider="claude",
        model_name="claude-3-sonnet-20240229",
        temperature=0.5
    )
    print(f"Claude LLM: {type(llm_claude).__name__}")
except Exception as e:
    print(f"Error: {e}")
print()


# ============================================================================
# Example 5: Cached Instance (Recommended for Production)
# ============================================================================
print("Example 5: Using cached LLM instance")

# First call creates instance
llm1 = get_llm_cached()
print(f"First call: {id(llm1)}")

# Second call returns same instance
llm2 = get_llm_cached()
print(f"Second call: {id(llm2)}")
print(f"Same instance? {llm1 is llm2}\n")


# ============================================================================
# Example 6: Switching Providers at Runtime
# ============================================================================
print("Example 6: Switching providers")

# Start with OpenRouter
llm_a = get_llm_cached(provider="openrouter")
print(f"Provider A: {type(llm_a).__name__ if llm_a else 'Mock'}")

# Reset cache to switch provider
reset_llm_cache()

# Now use ChatGPT
llm_b = get_llm_cached(provider="chatgpt")
print(f"Provider B: {type(llm_b).__name__ if llm_b else 'Mock'}")
print()


# ============================================================================
# Example 7: Error Handling
# ============================================================================
print("Example 7: Error handling")

try:
    # This will fail if API key is not set
    llm_invalid = get_llm(provider="openrouter")
    print("Success!")
except ValueError as e:
    print(f"Expected error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
print()


# ============================================================================
# Example 8: Using with LangChain Chains
# ============================================================================
print("Example 8: Integration with LangChain")

try:
    from langchain_core.prompts import ChatPromptTemplate
    
    # Get LLM
    llm = get_llm_cached()
    
    if llm:
        # Create a prompt
        prompt = ChatPromptTemplate.from_template(
            "You are a helpful assistant. User message: {message}"
        )
        
        # Create chain
        chain = prompt | llm
        
        # Use chain (async)
        # result = await chain.ainvoke({"message": "Hello!"})
        # print(f"Chain result: {result}")
        
        print("Chain created successfully")
    else:
        print("Using mock mode - chain not created")
        
except Exception as e:
    print(f"Error: {e}")
print()


# ============================================================================
# Configuration Summary
# ============================================================================
print("=" * 60)
print("Current Configuration Summary")
print("=" * 60)
print(f"Provider: {settings.llm_provider}")
print(f"OpenRouter Model: {settings.openrouter_model}")
print(f"Temperature: {settings.agent_temperature}")
print(f"Max Tokens: {settings.agent_max_tokens}")
print(f"OpenRouter API Key Set: {'Yes' if settings.openrouter_api_key else 'No'}")
print(f"OpenAI API Key Set: {'Yes' if settings.openai_api_key else 'No'}")
print(f"Anthropic API Key Set: {'Yes' if settings.anthropic_api_key else 'No'}")
print("=" * 60)
