"""
Deterministic offline provider. Two uses:
1. Local development/testing without burning API calls or needing a key.
2. A concrete demonstration of the Q53 "external service unavailable" fallback
   -- you can literally show the app switching to this provider live if you
   want to prove the resilience story instead of just describing it.
"""
from backend.llm.base import LLMProvider


class MockProvider(LLMProvider):
    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        return (
            "[MOCK RESPONSE] This is a placeholder answer generated without "
            "calling an external LLM. In a real run, this would be a grounded "
            "answer synthesized from the retrieved context below the prompt. "
            "Set LLM_PROVIDER=groq and GROQ_API_KEY to get real generations."
        )
