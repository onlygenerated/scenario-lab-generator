"""Application configuration via pydantic-settings. Reads from .env automatically."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Anthropic
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-6"
    anthropic_max_tokens: int = 32768

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: list[str] = ["http://localhost:5173"]

    # Docker labs
    lab_port_range_start: int = 8888
    lab_port_range_end: int = 8988
    lab_base_dir: str = "./lab_workspaces"

    # Rate limiting
    generate_rate_limit_per_minute: int = 10

    # Demo mode
    demo_mode: bool = True

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
