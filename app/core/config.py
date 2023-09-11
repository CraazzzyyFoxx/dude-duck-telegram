from pathlib import Path

from pydantic import HttpUrl
from pydantic_settings import SettingsConfigDict, BaseSettings


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

    token: str
    webhook_url: str

    api_token: str
    backend_url: HttpUrl
    auth_url: HttpUrl

    host: str
    port: int

    sentry_dsn: str
    debug: bool

    log_level: str = "info"
    logs_root_path: str = f"{Path.cwd()}/logs"

    mongo_name: str
    mongo_dsn: str

    redis_dsn: str

    admin_order: int
    admin_important_events: int
    admin_events: int
    admin_noise_events: int


app = AppConfig(_env_file='.env', _env_file_encoding='utf-8')


BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
