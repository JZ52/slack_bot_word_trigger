import logging

import psycopg2
from psycopg2 import OperationalError

from config import (
    SQL_ADRES,
    SQL_DATABASE,
    SQL_PASSWORD,
    SQL_PORT,
    SQL_USER,
)


logger = logging.getLogger(__name__)


def create_connection():
    try:
        connection = psycopg2.connect(
            host=SQL_ADRES,
            user=SQL_USER,
            password=SQL_PASSWORD,
            database=SQL_DATABASE,
            port=SQL_PORT,
            client_encoding="UTF8",
        )
        logger.info("Успешное подключение к PostgreSQL")
        return connection

    except OperationalError:
        logger.exception("Ошибка подключения к PostgreSQL")
        return None


def check_database() -> bool:
    connection = create_connection()

    if connection is None:
        return False

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            result = cursor.fetchone()

        return result == (1,)

    except psycopg2.Error:
        logger.exception("Ошибка проверки PostgreSQL")
        return False

    finally:
        connection.close()


def insert_message(
    *,
    channel_id,
    channel_name,
    message_ts,
    original_message,
    has_image,
    original_user_id,
    original_user_name,
    resolved_by_user_id,
    resolved_by_user_name,
    created_at,
    resolved_at,
):
    connection = create_connection()

    if connection is None:
        return False

    insert_query = """
        INSERT INTO public.slack_messages (
            channel_id,
            channel_name,
            message_ts,
            original_message,
            has_image,
            original_user_id,
            original_user_name,
            resolved_by_user_id,
            resolved_by_user_name,
            created_at,
            resolved_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (channel_id, message_ts) DO NOTHING;
    """

    values = (
        channel_id,
        channel_name,
        message_ts,
        original_message,
        has_image,
        original_user_id,
        original_user_name,
        resolved_by_user_id,
        resolved_by_user_name,
        created_at,
        resolved_at,
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute(insert_query, values)
            inserted = cursor.rowcount == 1

        connection.commit()

        if inserted:
            logger.info("Сообщение добавлено в PostgreSQL")
        else:
            logger.info("Сообщение уже существует")

        return inserted

    except psycopg2.Error:
        connection.rollback()
        logger.exception("Ошибка записи сообщения")
        return False

    finally:
        connection.close()