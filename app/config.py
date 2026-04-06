import os
from dataclasses import dataclass
from functools import lru_cache


def _load_env_file(path: str = ".env") -> None:
    if not os.path.exists(path):
        return

    with open(path, "r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


@dataclass(frozen=True)
class Settings:
    app_env: str = "development"
    database_path: str = "agent.db"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"
    slack_signing_secret: str | None = None
    slack_bot_token: str | None = None
    slack_alert_channel: str | None = None
    notion_api_key: str | None = None
    notion_database_id: str | None = None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    _load_env_file()
    return Settings(
        app_env=os.getenv("APP_ENV", "development"),
        database_path=os.getenv("DATABASE_PATH", "agent.db"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        slack_signing_secret=os.getenv("SLACK_SIGNING_SECRET"),
        slack_bot_token=os.getenv("SLACK_BOT_TOKEN"),
        slack_alert_channel=os.getenv("SLACK_ALERT_CHANNEL"),
        notion_api_key=os.getenv("NOTION_API_KEY"),
        notion_database_id=os.getenv("NOTION_DATABASE_ID"),
    )
