from .base import LLMClient
from .openai import OpenAIDirectClient
from .anthropic import AnthropicDirectClient
from .gemini import GeminiDirectClient

def get_client(client_name: str, **kwargs) -> LLMClient:
    """Get a client for a given client name."""
    if client_name == "anthropic-direct":
        return AnthropicDirectClient(**kwargs)
    elif client_name == "openai-direct":
        return OpenAIDirectClient(**kwargs)
    elif client_name == "gemini-direct":
        return GeminiDirectClient(**kwargs)
    else:
        raise ValueError(f"Unknown client name: {client_name}")


__all__ = [
    "LLMClient",
    "OpenAIDirectClient",
    "AnthropicDirectClient",
    "GeminiDirectClient",
    "get_client",
]
