import os
import logging

from dotenv import load_dotenv


load_dotenv("key.env")

logger = logging.getLogger(__name__)

SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
BOT_USER_OAUTH_TOKEN = os.getenv("BOT_USER_OAUTH_TOKEN")
ADMIN_CHANNEL_ID = os.getenv("ADMIN_CHANNEL_ID")
EMOJI = os.getenv("emoji")

SQL_ADRES = os.getenv("SQL_ADRES")
SQL_USER = os.getenv("SQL_USER")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_PORT = os.getenv("SQL_PORT")


def validate_config() -> None:
    required_settings = {
        "SLACK_APP_TOKEN": SLACK_APP_TOKEN,
        "BOT_USER_OAUTH_TOKEN": BOT_USER_OAUTH_TOKEN,
        "ADMIN_CHANNEL_ID": ADMIN_CHANNEL_ID,
        "emoji": EMOJI,
        "SQL_ADRES": SQL_ADRES,
        "SQL_USER": SQL_USER,
        "SQL_PASSWORD": SQL_PASSWORD,
        "SQL_DATABASE": SQL_DATABASE,
        "SQL_PORT": SQL_PORT,
    }

    missing_settings = [
        name
        for name, value in required_settings.items()
        if not value
    ]

    if missing_settings:
        logger.critical(
            "Не заполнены настройки: %s",
            ", ".join(missing_settings),
        )
        raise SystemExit(1)