import logging

from slack_bolt import App
from slack_bolt.adapter.socket_mode.builtin import SocketModeHandler

from config import BOT_USER_OAUTH_TOKEN, SLACK_APP_TOKEN, validate_config
from database import check_database
from handlers import register_handlers


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)


def main():
    validate_config()

    if not check_database():
        logger.critical("PostgreSQL недоступен")
        raise SystemExit(1)

    app = App(token=BOT_USER_OAUTH_TOKEN)
    register_handlers(app)

    logger.info("Slack bot started")
    SocketModeHandler(app, SLACK_APP_TOKEN).start()


if __name__ == "__main__":
    main()