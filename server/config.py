"""Centralised settings, loaded from environment variables."""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # LLM
    llm_provider: str = "anthropic"
    llm_model: str = "claude-haiku-4-5-20251001"
    llm_api_key: str = ""
    ollama_host: str = "http://localhost:11434"

    # Server
    port: int = 8000
    timezone: str = "America/Lima"
    log_level: str = "INFO"

    # Paths
    recipes_dir: Path = Path("./recipes")
    data_dir: Path = Path("./data")

    # DB
    database_url: str = "sqlite:///./data/whendo.db"

    # Channels — all optional
    telegram_bot_token: str = ""
    telegram_default_chat_id: str = ""
    ntfy_server: str = "https://ntfy.sh"
    ntfy_default_topic: str = ""
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_pass: str = ""
    smtp_from: str = ""
    discord_webhook_url: str = ""

    # External APIs
    openweather_api_key: str = ""
    spotify_client_id: str = ""
    spotify_client_secret: str = ""
    github_token: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
