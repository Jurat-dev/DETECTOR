import os
from pathlib import Path
from dotenv import load_dotenv

BASE = Path(__file__).resolve().parent.parent
load_dotenv(BASE / ".env")


def _p(v: str) -> Path:
    p = Path(v)
    return p if p.is_absolute() else (BASE / p).resolve()


class Settings:
    search_backend = os.getenv("SEARCH_BACKEND", "local")
    database_url = os.getenv("DATABASE_URL", "")
    data_dir = _p(os.getenv("DATA_DIR", "./data"))
    pdf_dir = _p(os.getenv("PDF_DIR", "../detector/KITOBLAR"))
    embedding_model = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-large")
    enable_semantic = os.getenv("ENABLE_SEMANTIC", "false").lower() in ("1", "true", "yes")
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    llm_model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    cors_origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if o.strip()]


settings = Settings()
