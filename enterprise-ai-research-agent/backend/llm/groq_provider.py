"""
Groq implementation of LLMProvider. Groq's API is OpenAI-compatible, so this
uses plain HTTP via `requests` -- no extra SDK dependency needed.
"""
import requests

from backend.llm.base import LLMProvider
from backend.config.settings import settings


class GroqProvider(LLMProvider):
    def __init__(self):
        self.api_key = settings.groq_api_key
        self.model = settings.groq_model
        self.url = "https://api.groq.com/openai/v1/chat/completions"

    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        if not self.api_key:
            raise RuntimeError(
                "GROQ_API_KEY not set. Set it in your environment, or switch "
                "LLM_PROVIDER=mock in .env for local testing without a key."
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.2,
        }

        try:
            resp = requests.post(self.url, headers=headers, json=payload, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            # Q53 fallback behavior: surface a clear, catchable error rather
            # than letting the request hang or crash the endpoint.
            raise RuntimeError(f"Groq API call failed: {e}")
