import logging

from config import ADMIN_CHANNEL_ID


logger = logging.getLogger(__name__)


def is_admin(client, user_id: str | None) -> bool:
    if not user_id:
        return False

    try:
        response = client.conversations_members(
            channel=ADMIN_CHANNEL_ID,
            limit=10,
        )
        return user_id in response.get("members", [])

    except Exception:
        logger.exception(
            "Не удалось получить участников канала админов"
        )
        return False


def get_user_name(client, user_id: str | None) -> str:
    if not user_id:
        return "Неизвестный пользователь"

    try:
        response = client.users_info(user=user_id)
        user = response.get("user", {})
        profile = user.get("profile", {})

        return (
            profile.get("display_name")
            or profile.get("real_name")
            or user.get("real_name")
            or user_id
        )

    except Exception:
        logger.exception(
            "Не удалось получить имя пользователя %s",
            user_id,
        )
        return user_id


def get_channel_name(client, channel_id: str) -> str:
    try:
        response = client.conversations_info(
            channel=channel_id,
        )
        channel = response.get("channel", {})

        return channel.get("name") or channel_id

    except Exception:
        logger.exception(
            "Не удалось получить название канала %s",
            channel_id,
        )
        return channel_id