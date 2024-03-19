from pathlib import Path

from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    project_name: str = "Dude Duck CRM"
    project_version: str = "1.0.0"
    debug: bool = False
    username_regex: str = r"([a-zA-Z0-9_-]+)"

    # CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000"]'
    cors_origins: list[str] = []
    use_correlation_id: bool = False

    port: int

    token: str
    webhook_url: str

    api_token: str
    backend_url: HttpUrl
    auth_url: HttpUrl

    sentry_dsn: str

    log_level: str = "info"
    logs_root_path: str = f"{Path.cwd()}/logs"

    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: str

    admin_order: int
    admin_important_events: int
    admin_events: int
    admin_noise_events: int

    @property
    def db_url_asyncpg(self):
        url = (
            f"{self.postgres_user}:{self.postgres_password}@"
            f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
        return f"postgresql+asyncpg://{url}"

    @property
    def db_url(self):
        url = (
            f"{self.postgres_user}:{self.postgres_password}@"
            f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
        return f"postgresql+psycopg://{url}"


app = AppConfig(_env_file=".env", _env_file_encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
