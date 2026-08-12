"""
Centralized, environment-driven configuration.

Why this file exists:
Nothing in the app should hardcode API keys, model names, or DB URLs.
Everything comes from environment variables (with sane local defaults),
so the same code runs in dev, Docker, or a cloud deployment without
code changes -- this is the "config-driven, not hardcoded" principle
from the architecture answers (Q46, Q71).
"""
import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

# Explicitly point at backend/.env regardless of the current working directory
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


@dataclass
class Settings:
    # Database
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/research_agent",
    )

    # Vector store
    chroma_persist_dir: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_store")
    chroma_collection_name: str = os.getenv("CHROMA_COLLECTION", "enterprise_docs")

    # Embeddings
    embedding_model_name: str = os.getenv(
        "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )

    # LLM provider
    llm_provider: str = os.getenv("LLM_PROVIDER", "groq")  # "groq" | "mock"
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

    # Retrieval
    top_k: int = int(os.getenv("TOP_K", "4"))
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "500"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "50"))

    # Auth
    api_key: str = os.getenv("APP_API_KEY", "dev-local-key")

    # App
    app_env: str = os.getenv("APP_ENV", "development")


settings = Settings()
