# Demo Script (5–7 minutes)

## 1. Problem framing (30s)
"Enterprise teams need answers grounded in their own documents — not an LLM's
general knowledge, which can be outdated, generic, or wrong for their
specific policies. This is a research agent that only answers from indexed
enterprise documents, and tells you when it can't."

## 2. Architecture walkthrough (1 min)
Show `docs/architecture.md` diagram or the folder structure. Name the layers
out loud: frontend, backend API, ingestion, retrieval, orchestration, LLM
provider layer, storage. Emphasize: "each of these is a separate, swappable
module."

## 3. Live query — grounded answer (1.5 min)
- Ask: "How many paid leave days do full-time employees get?"
- Point out: grounded badge, latency, sources chip showing `leave_policy.txt`.
- Open the source doc briefly to show the answer really is in there.

## 4. Live query — out-of-scope / ungrounded (1 min)
- Ask something the indexed docs don't cover, e.g. "What is the capital of
  France?"
- Point out: it does NOT guess. It returns "insufficient information."
- This is the single best proof point for Q44/Q51 — say that explicitly.

## 5. Show the audit trail (1 min)
- Open `/metrics` or query the `audit_logs` table directly (psql or a quick
  script) to show both queries were logged with timestamps, latency, and
  grounded/ungrounded status.
- "This isn't just a demo — every query is auditable."

## 6. Show adding a new document, no code change (1 min)
- Upload a new .txt file through the UI.
- Ask a question that only the new document answers.
- "New knowledge sources plug in through the ingestion pipeline — no
  redeploy, no code change."

## 7. Close — what's designed but not built, and why (30s)
- Mention: async ingestion at scale, real JWT auth, multi-language support —
  all designed for in the architecture, deliberately not built in 2 days
  because they don't change the core proof of concept.
- "The goal wasn't to build everything — it was to build the right modular
  core, correctly, so all of that is a plug-in away."

## Recording tips
- Have the backend + frontend already running before you hit record —
  don't show `pip install` or `npm install` on camera, it's dead time.
- Keep terminal font large if you show curl/logs.
- Have the 3 sample docs already indexed before recording starts.
