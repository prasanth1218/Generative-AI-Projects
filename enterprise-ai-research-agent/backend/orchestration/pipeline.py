"""
The four-step flow described in Q38, as actual code:
  understand -> retrieve -> generate -> validate

Each step is a separate module already tested/testable in isolation.
This function just sequences them and packages the result. Nothing here
is "magic" -- in the live technical round you can point to any one of
these four function calls and open that file directly.
"""
import time
from dataclasses import dataclass, field
from typing import List

from backend.orchestration.query_understanding import classify_query
from backend.retrieval.retriever import retrieve, RetrievedChunk
from backend.orchestration.generator import generate_answer
from backend.orchestration.validator import validate


@dataclass
class PipelineResult:
    answer: str
    sources: List[str] = field(default_factory=list)
    is_grounded: bool = False
    used_llm: bool = False
    retrieved_doc_ids: List[str] = field(default_factory=list)
    latency_ms: float = 0.0
    skip_reason: str = ""


def run_pipeline(question: str, top_k: int = None) -> PipelineResult:
    start = time.time()

    # Step 1: query understanding (cheap, no LLM/retrieval call)
    intent = classify_query(question)
    if not intent.is_answerable:
        return PipelineResult(
            answer="This doesn't look like a research question I can answer. "
                   "Try asking about a specific topic from the indexed documents.",
            skip_reason=intent.reason,
            latency_ms=(time.time() - start) * 1000,
        )

    # Step 2: retrieval
    chunks: List[RetrievedChunk] = retrieve(question, top_k=top_k)

    # Step 3 (pre-check): validate retrieval quality BEFORE spending an LLM call
    pre_validation = validate(chunks)
    if not pre_validation.is_grounded:
        return PipelineResult(
            answer="I don't have enough relevant information in the indexed "
                   "documents to answer this confidently.",
            is_grounded=False,
            used_llm=False,
            skip_reason=pre_validation.reason,
            latency_ms=(time.time() - start) * 1000,
        )

    # Step 4: generation (only reached if retrieval was good enough to justify it)
    answer_text = generate_answer(question, chunks)

    return PipelineResult(
        answer=answer_text,
        sources=pre_validation.sources,
        is_grounded=True,
        used_llm=True,
        retrieved_doc_ids=[c.document_id for c in chunks],
        latency_ms=(time.time() - start) * 1000,
    )
