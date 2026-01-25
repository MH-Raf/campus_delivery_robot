from dataclasses import dataclass
import os

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    bot_token: str
    allowed_user_ids: set[int]


def load_settings() -> Settings:
    load_dotenv()

    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("BOT_TOKEN is not set. Put it into .env")

    raw_ids = os.getenv("ALLOWED_USER_IDS", "").strip()
    allowed: set[int] = set()
    if raw_ids:
        allowed = {int(x) for x in raw_ids.split(",") if x.strip()}

    return Settings(bot_token=token, allowed_user_ids=allowed)