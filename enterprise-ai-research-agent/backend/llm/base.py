"""
Abstract interface every LLM provider must implement. Orchestration code
only ever calls `.generate(prompt)` on whatever provider `get_llm_provider()`
returns -- it has no idea whether that's Groq, OpenAI, Ollama, or a mock.

This is the direct implementation of your Q53 answer (graceful fallback to
another provider) and Q69 (new AI capabilities without redesigning the system).
"""
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        ...
