"""
Builds the grounded prompt from retrieved chunks and calls the LLM.
The prompt explicitly instructs the model to answer only from context and
say so when it can't -- this is the core mechanism behind Q44
("ensure responses are based on reliable information").
"""
from typing import List

from backend.retrieval.retriever import RetrievedChunk
from backend.llm.factory import get_llm_provider_with_fallback

PROMPT_TEMPLATE = """You are an enterprise research assistant. Answer the user's \
question using ONLY the context provided below. Do not use outside knowledge.

If the context does not contain enough information to answer confidently, \
say clearly: "I don't have enough information in the available documents to \
answer this confidently." Do not guess.

When you use a piece of context, mention which source it came from by title.

Context:
{context}

Question: {question}

Answer:"""


def build_prompt(question: str, chunks: List[RetrievedChunk]) -> str:
    if not chunks:
        context = "(no relevant context was retrieved)"
    else:
        context = "\n\n".join(
            f"[Source: {c.title}]\n{c.text}" for c in chunks
        )
    return PROMPT_TEMPLATE.format(context=context, question=question)


def generate_answer(question: str, chunks: List[RetrievedChunk]) -> str:
    prompt = build_prompt(question, chunks)
    provider = get_llm_provider_with_fallback()
    return provider.generate(prompt)
