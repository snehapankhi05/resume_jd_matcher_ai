from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    GROQ_API_KEY: str

    MODEL_NAME: str

    EMBEDDING_MODEL: str

    CHROMA_DB_PATH: str

    UPLOAD_FOLDER: str

    REPORT_FOLDER: str

    MAX_FILE_SIZE_MB: int

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()