# Enterprise AI Research Agent

A retrieval-augmented research assistant that answers questions grounded in
enterprise documents, with full source citation and traceability — built for
the Modus Enterprise AI Build Challenge.

## What this is

Every answer is generated **only** from retrieved document context, never
from the model's general knowledge. If the retrieved context isn't good
enough, the system says so instead of guessing. Every query, its retrieved
sources, and its outcome are logged for monitoring.

## Architecture

```
Frontend (React) → Backend (FastAPI) → Orchestration Pipeline
                                          ├── Query Understanding (rule-based)
                                          ├── Retrieval (ChromaDB + MiniLM embeddings)
                                          ├── Generation (Groq LLM, swappable)
                                          └── Validation (grounding + citation check)

Storage: PostgreSQL (users, doc metadata, audit logs) + ChromaDB (vectors)
```

See `docs/architecture.md` for the full breakdown and `docs/demo-script.md`
for what to walk through in your video.

## Quick start (local, no Docker)

### 1. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env:
#   - Set GROQ_API_KEY (free at https://console.groq.com)
#   - Or set LLM_PROVIDER=mock to run without any API key
#   - For local dev without Postgres running, you can temporarily use:
#     DATABASE_URL=sqlite:///./dev.db

uvicorn backend.main:app --reload --port 8000
```

Then index the sample documents:

```bash
curl -X POST http://localhost:8000/documents/upload \
  -H "x-api-key: dev-local-key" \
  -F "file=@../data/sample_docs/leave_policy.txt" \
  -F "domain_tag=hr"

curl -X POST http://localhost:8000/documents/upload \
  -H "x-api-key: dev-local-key" \
  -F "file=@../data/sample_docs/it_security_policy.txt" \
  -F "domain_tag=security"

curl -X POST http://localhost:8000/documents/upload \
  -H "x-api-key: dev-local-key" \
  -F "file=@../data/sample_docs/expense_policy.txt" \
  -F "domain_tag=finance"
```

Test a query:

```bash
curl -X POST http://localhost:8000/query/ \
  -H "x-api-key: dev-local-key" \
  -H "Content-Type: application/json" \
  -d '{"question": "How many paid leave days do full-time employees get?"}'
```

API docs are auto-generated at `http://localhost:8000/docs` (FastAPI's
built-in Swagger UI) — useful to show live in your technical validation round.

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env      # defaults already point at localhost:8000
npm run dev
```

Open `http://localhost:5173`. Upload a document from the UI, or use the
sample-doc curl commands above, then ask a question.

## Quick start (Docker)

```bash
cp backend/.env.example .env   # then edit GROQ_API_KEY at the repo root .env
docker compose up --build
```

Backend will be on `http://localhost:8000`. Run the same curl upload/query
commands above against it. (Frontend isn't in docker-compose by default —
run it locally with `npm run dev` pointed at the dockerized backend, or add
a frontend service later; kept out here to keep the compose file simple for
a 2-day build.)

## Project structure

```
backend/
  api/            → FastAPI routers (documents, query, metrics, auth)
  ingestion/       → load → chunk → index pipeline
  retrieval/       → embeddings + Chroma wrapper + retriever interface
  orchestration/   → the 4-step pipeline: understand → retrieve → generate → validate
  llm/             → provider interface + Groq + mock implementations
  db/              → SQLAlchemy models + session
  config/          → environment-driven settings
frontend/
  src/App.jsx      → query console UI
data/sample_docs/  → 3 sample enterprise policy documents for the demo
docs/               → architecture notes + demo script
```

## Why these choices (for your defense)

- **No LangChain agents / heavy framework**: the 4-step pipeline is plain
  Python functions. Every step is independently testable and inspectable —
  critical for explainability in a live technical round.
- **Groq, not local Ollama, for the demo**: free tier, fast enough for a live
  demo, and fully swappable — `backend/llm/factory.py` is the only file that
  changes to add a new provider.
- **ChromaDB's built-in ONNX embedding function, not full sentence-transformers**:
  same MiniLM model family, no PyTorch dependency, far smaller install —
  a deliberate lightweight choice, not a missing feature.
- **Rule-based query classification before any LLM call**: directly
  implements "reduce unnecessary LLM calls" — trivial/out-of-scope queries
  never reach the model.
- **Validator runs before generation, not just after**: if retrieval quality
  is too low, the pipeline returns an honest "not enough information"
  response and skips the LLM call entirely — saves cost and avoids
  hallucination risk at the same time.

## Known limitations (be upfront about these if asked)

- Auth is a single static API key, not full JWT/RBAC — the `users` table and
  schema are there, but wiring real auth was out of scope for 2 days.
- Query classification and validation are rule-based, not ML-based — a
  deliberate simplicity trade-off explained in the architecture answers.
- No async/queue-based ingestion — fine at demo scale (a few docs), and the
  scaling path (Q43 in the assessment) is documented, not built, since it's
  not needed to prove the concept.
