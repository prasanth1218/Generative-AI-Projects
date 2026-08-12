import React, { useState, useEffect, useCallback } from "react";
import "./App.css";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";
const API_KEY = import.meta.env.VITE_API_KEY || "dev-local-key";

const SAMPLE_QUERIES = [
  "How many paid leave days do full-time employees get?",
  "What are the password requirements for company systems?",
  "How long does expense reimbursement take?",
  "What is the capital of France?", // deliberately out-of-scope, for the demo
];

function useApi() {
  const call = useCallback(async (path, options = {}) => {
    const res = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: {
        "x-api-key": API_KEY,
        ...(options.headers || {}),
      },
    });
    if (!res.ok) {
      const text = await res.text().catch(() => "");
      throw new Error(`${res.status} ${res.statusText} ${text}`);
    }
    return res.json();
  }, []);
  return call;
}

function GroundedBadge({ isGrounded }) {
  return (
    <span className={`badge ${isGrounded ? "badge--grounded" : "badge--ungrounded"}`}>
      <span className="badge__dot" />
      {isGrounded ? "Grounded in source documents" : "Not grounded — insufficient evidence"}
    </span>
  );
}

function AnswerCard({ result }) {
  if (!result) return null;
  return (
    <div className="answer-card">
      <div className="answer-card__meta">
        <GroundedBadge isGrounded={result.is_grounded} />
        <span className="answer-card__stat">
          {result.used_llm ? "LLM call made" : "No LLM call"}
        </span>
        <span className="answer-card__stat">{Math.round(result.latency_ms)} ms</span>
      </div>

      <p className="answer-card__text">{result.answer}</p>

      {result.sources && result.sources.length > 0 && (
        <div className="provenance">
          <div className="provenance__label">Traced to</div>
          <div className="provenance__chips">
            {result.sources.map((s) => (
              <span key={s} className="provenance__chip">
                <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                  <path
                    d="M3 1.5h4.5L9.5 3.5V10.5H3V1.5Z"
                    stroke="currentColor"
                    strokeWidth="1"
                  />
                </svg>
                {s}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function DocumentsPanel({ documents, onUpload, uploading }) {
  const [open, setOpen] = useState(false);
  const fileInputRef = React.useRef(null);

  return (
    <div className="docs-panel">
      <button className="docs-panel__toggle" onClick={() => setOpen((o) => !o)}>
        <span>{open ? "▾" : "▸"} Indexed documents ({documents.length})</span>
      </button>
      {open && (
        <div className="docs-panel__body">
          <ul className="docs-panel__list">
            {documents.map((d) => (
              <li key={d.id}>
                <span className="docs-panel__title">{d.title}</span>
                <span className="docs-panel__tag">{d.domain_tag}</span>
              </li>
            ))}
            {documents.length === 0 && (
              <li className="docs-panel__empty">
                No documents indexed yet. Upload one to get started.
              </li>
            )}
          </ul>
          <input
            ref={fileInputRef}
            type="file"
            accept=".txt,.md,.pdf,.docx"
            style={{ display: "none" }}
            onChange={(e) => {
              if (e.target.files?.[0]) onUpload(e.target.files[0]);
              e.target.value = "";
            }}
          />
          <button
            className="docs-panel__upload"
            disabled={uploading}
            onClick={() => fileInputRef.current?.click()}
          >
            {uploading ? "Uploading & indexing…" : "+ Upload document"}
          </button>
        </div>
      )}
    </div>
  );
}

export default function App() {
  const api = useApi();
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [metrics, setMetrics] = useState(null);

  const loadDocuments = useCallback(async () => {
    try {
      const docs = await api("/documents/");
      setDocuments(docs);
    } catch (e) {
      // silent — backend may not be running yet during frontend-only dev
    }
  }, [api]);

  const loadMetrics = useCallback(async () => {
    try {
      const m = await api("/metrics/");
      setMetrics(m);
    } catch (e) {
      /* silent */
    }
  }, [api]);

  useEffect(() => {
    loadDocuments();
    loadMetrics();
  }, [loadDocuments, loadMetrics]);

  const submitQuery = async (q) => {
    const question = (q ?? query).trim();
    if (!question || loading) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const res = await api("/query/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      setResult(res);
      loadMetrics();
    } catch (e) {
      setError(
        "Couldn't reach the research agent backend. Is the FastAPI server running on " +
          API_BASE +
          "?"
      );
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (file) => {
    setUploading(true);
    try {
      const form = new FormData();
      form.append("file", file);
      form.append("domain_tag", "general");
      await api("/documents/upload", { method: "POST", body: form });
      await loadDocuments();
    } catch (e) {
      setError("Upload failed: " + e.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="shell">
      <header className="header">
        <div className="header__mark">
          <span className="header__mark-glyph">◈</span>
          <span className="header__mark-text">Research Console</span>
        </div>
        <div className="header__sub">Enterprise AI Research Agent</div>
      </header>

      <main className="main">
        <section className="query-section">
          <label className="query-section__label" htmlFor="query-input">
            Ask a question grounded in your indexed documents
          </label>
          <div className="query-box">
            <input
              id="query-input"
              className="query-box__input"
              placeholder="e.g. How many paid leave days do full-time employees get?"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && submitQuery()}
            />
            <button
              className="query-box__submit"
              onClick={() => submitQuery()}
              disabled={loading}
            >
              {loading ? "Thinking…" : "Ask"}
            </button>
          </div>

          <div className="samples">
            {SAMPLE_QUERIES.map((s) => (
              <button
                key={s}
                className="samples__chip"
                onClick={() => {
                  setQuery(s);
                  submitQuery(s);
                }}
              >
                {s}
              </button>
            ))}
          </div>
        </section>

        {error && <div className="error-banner">{error}</div>}

        {loading && (
          <div className="loading-row">
            <span className="loading-dot" />
            <span className="loading-dot" />
            <span className="loading-dot" />
            <span className="loading-row__label">
              retrieving → generating → validating
            </span>
          </div>
        )}

        <AnswerCard result={result} />

        <DocumentsPanel
          documents={documents}
          onUpload={handleUpload}
          uploading={uploading}
        />

        {metrics && (
          <div className="metrics-strip">
            <div className="metrics-strip__item">
              <span className="metrics-strip__value">{metrics.total_queries}</span>
              <span className="metrics-strip__label">queries logged</span>
            </div>
            <div className="metrics-strip__item">
              <span className="metrics-strip__value">
                {Math.round((metrics.grounded_rate || 0) * 100)}%
              </span>
              <span className="metrics-strip__label">grounded rate</span>
            </div>
            <div className="metrics-strip__item">
              <span className="metrics-strip__value">
                {Math.round((metrics.llm_call_rate || 0) * 100)}%
              </span>
              <span className="metrics-strip__label">LLM call rate</span>
            </div>
            <div className="metrics-strip__item">
              <span className="metrics-strip__value">{metrics.avg_latency_ms}</span>
              <span className="metrics-strip__label">avg latency (ms)</span>
            </div>
          </div>
        )}
      </main>

      <footer className="footer">
        Retrieval-augmented · modular · every answer traced to its source
      </footer>
    </div>
  );
}
