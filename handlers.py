import logging
from datetime import datetime, timezone

from config import EMOJI
from database import insert_message
from slack_helper import (
    get_channel_name,
    get_user_name,
    is_admin,
)


logger = logging.getLogger(__name__)


def handle_reaction_added(event, client):
    user_id = event.get("user")
    item = event.get("item") or {}
    reaction = event.get("reaction")

    if reaction != EMOJI:
        return

    if item.get("type") != "message":
        return

    if not is_admin(client, user_id):
        logger.info(
            "Реакция обычного пользователя проигнорирована: %s",
            user_id,
        )
        return

    channel_id = item.get("channel")
    message_ts = item.get("ts")

    if not channel_id or not message_ts:
        logger.error(
            "В событии отсутствует канал или время сообщения"
        )
        return

    try:
        history = client.conversations_history(
            channel=channel_id,
            latest=message_ts,
            inclusive=True,
            limit=1,
        )
    except Exception:
        logger.exception(
            "Не удалось получить сообщение %s",
            message_ts,
        )
        return

    messages = history.get("messages", [])

    if not messages:
        logger.info(
            "Сообщение %s не найдено в истории канала",
            message_ts,
        )
        return

    target_message = messages[0]

    if target_message.get("ts") != message_ts:
        logger.info(
            "Реакция на сообщение внутри ветки проигнорирована: %s",
            message_ts,
        )
        return

    files = target_message.get("files") or []

    has_image = any(
        (file.get("mimetype") or "").startswith("image/")
        for file in files
    )

    original_message = (
        target_message.get("text") or ""
    ).strip()

    if not original_message:
        original_message = (
            "Картинка"
            if has_image
            else "Пустое сообщение"
        )

    original_user_id = (
        target_message.get("user")
        or event.get("item_user")
    )
    resolved_by_user_id = user_id

    original_user_name = get_user_name(
        client,
        original_user_id,
    )
    resolved_by_user_name = get_user_name(
        client,
        resolved_by_user_id,
    )
    channel_name = get_channel_name(
        client,
        channel_id,
    )

    resolved_ts = event.get("event_ts")

    if not resolved_ts:
        logger.error(
            "В событии отсутствует время реакции"
        )
        return

    try:
        created_at = datetime.fromtimestamp(
            float(message_ts),
            tz=timezone.utc,
        )
        resolved_at = datetime.fromtimestamp(
            float(resolved_ts),
            tz=timezone.utc,
        )
    except (TypeError, ValueError):
        logger.exception(
            "Slack передал некорректное время события"
        )
        return

    inserted = insert_message(
        channel_id=channel_id,
        channel_name=channel_name,
        message_ts=message_ts,
        original_message=original_message,
        has_image=has_image,
        original_user_id=original_user_id,
        original_user_name=original_user_name,
        resolved_by_user_id=resolved_by_user_id,
        resolved_by_user_name=resolved_by_user_name,
        created_at=created_at,
        resolved_at=resolved_at,
    )

    if inserted:
        logger.info(
            "Сообщение %s записано в PostgreSQL",
            message_ts,
        )
    else:
        logger.info(
            "Сообщение %s не было добавлено",
            message_ts,
        )


def register_handlers(app):
    app.event("reaction_added")(handle_reaction_added)