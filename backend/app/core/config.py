from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/core/config.py -> project root is three levels above "core"
PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    GROQ_API_KEY: str

    GROQ_MODEL: str

    EMBEDDING_MODEL: str

    CHROMA_DB_PATH: str

    UPLOAD_FOLDER: str

    REPORT_FOLDER: str

    MAX_FILE_SIZE_MB: int

    # Optional settings (safe defaults, so an existing .env keeps working)
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    LLM_TIMEOUT_SECONDS: int = 60

    # Share of the overall score that comes from skill coverage; the
    # remainder (1 - weight) comes from semantic similarity.
    SKILL_SCORE_WEIGHT: float = Field(default=0.6, ge=0, le=1)

    # How skills are extracted from the resume and the JD:
    #   "rules"  = vocabulary + rule-based mining (offline, deterministic)
    #   "hybrid" = rules + LLM extraction, verified against the document text
    #              (finds skills the rules cannot read; falls back to rules on any error)
    SKILL_EXTRACTION_MODE: str = "hybrid"

    # LangSmith tracing (optional). Tracing is only switched on when
    # LANGSMITH_TRACING=true AND an API key is present.
    LANGSMITH_TRACING: bool = False
    LANGSMITH_API_KEY: str = ""
    LANGSMITH_PROJECT: str = "resume-jd-matcher"
    LANGSMITH_ENDPOINT: str = ""

    # Resumes contain personal data. Set these to true to keep the text out of
    # LangSmith: traces then only show timings, structure and errors.
    LANGSMITH_HIDE_INPUTS: bool = False
    LANGSMITH_HIDE_OUTPUTS: bool = False

    # Always load the .env that sits in the project root, no matter which
    # directory the server is started from.
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        extra="ignore"
    )

    @field_validator(
        "CHROMA_DB_PATH",
        "UPLOAD_FOLDER",
        "REPORT_FOLDER"
    )
    @classmethod
    def _resolve_against_project_root(cls, value: str) -> str:
        """Relative paths are resolved against the project root, not the CWD."""
        path = Path(value)

        if not path.is_absolute():
            path = PROJECT_ROOT / path

        return str(path.resolve())

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")
            if origin.strip()
        ]


settings = Settings()
