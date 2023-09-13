from pathlib import Path

from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra="ignore")

    token: str
    webhook_url: str

    api_token: str
    backend_url: HttpUrl
    auth_url: HttpUrl

    port: int

    sentry_dsn: str
    debug: bool

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


app = AppConfig(_env_file='.env', _env_file_encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"

tortoise = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "database": app.postgres_db,
                "host": app.postgres_host,  # db for docker
                "password": app.postgres_password,
                "port": app.postgres_port,
                "user": app.postgres_user,
            },
        }
    },
    "apps": {
        "main": {
            "models": [
                "app.services.api.models",
                "app.services.channel.models",
                "app.services.message.models",
                "app.services.render.models",
                "aerich.models"
            ],
        }
    },
}
