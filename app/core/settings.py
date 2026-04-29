from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "trend-driven-category-system"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    postgres_user: str = "trend_user"
    postgres_password: str = "trend_password"
    postgres_db: str = "trend_db"
    postgres_host: str = "db"
    postgres_port: int = 5432

    database_url: str = "postgresql+psycopg2://trend_user:trend_password@db:5432/trend_db"

    ai_enabled: bool = False
    openai_api_key: str | None = None
    openai_model: str = "gpt-5.4"

    feature_ai_explanation: bool = True
    feature_docker_actions: bool = False
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
