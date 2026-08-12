"""
Cheap, non-LLM query classification before any retrieval or generation
happens. This is the direct implementation of Q49 (reduce unnecessary LLM
calls): trivial or out-of-scope inputs are caught here with plain rules,
so we don't spend a model call on "hi" or an empty string.
"""
from dataclasses import dataclass

GREETINGS = {"hi", "hello", "hey", "thanks", "thank you", "ok", "okay"}


@dataclass
class QueryIntent:
    is_answerable: bool
    reason: str


def classify_query(query_text: str) -> QueryIntent:
    text = query_text.strip().lower()

    if not text:
        return QueryIntent(is_answerable=False, reason="empty_query")

    if text in GREETINGS:
        return QueryIntent(is_answerable=False, reason="greeting_or_smalltalk")

    if len(text) < 3:
        return QueryIntent(is_answerable=False, reason="too_short")

    return QueryIntent(is_answerable=True, reason="ok")
