from backend.config.settings import settings
from backend.llm.base import LLMProvider
from backend.llm.groq_provider import GroqProvider
from backend.llm.mock_provider import MockProvider


def get_llm_provider() -> LLMProvider:
    provider = settings.llm_provider.lower()
    if provider == "groq":
        return GroqProvider()
    if provider == "mock":
        return MockProvider()
    raise ValueError(f"Unknown LLM_PROVIDER: {provider}")


def get_llm_provider_with_fallback() -> LLMProvider:
    """
    Used by the orchestrator. Tries the configured provider; if it's
    misconfigured (no key) falls back to mock rather than crashing the
    whole request -- a lightweight version of the Q53 resilience answer.
    """
    try:
        provider = get_llm_provider()
        if isinstance(provider, GroqProvider) and not provider.api_key:
            return MockProvider()
        return provider
    except Exception:
        return MockProvider()
