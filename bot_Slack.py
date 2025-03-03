import os
import json
from dotenv import load_dotenv
from flask import Flask, request, jsonify
<<<<<<< HEAD
from slack_sdk.rtm import RTMClient
=======
>>>>>>> d03ebd5 (Update all code)
from slack_sdk.web import WebClient
from slack_sdk.errors import SlackApiError
from datetime import datetime
from models import create_table, insert_message, load_users
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)

load_dotenv('key.env')

TRIGGER_EMOJI = "slack"

app = Flask(__name__)

SLACK_TOKEN = os.getenv("BOT_USER_OAUTH_TOKEN")
<<<<<<< HEAD
rtm_client = RTMClient(token=SLACK_TOKEN)
slack_client = WebClient(token=SLACK_TOKEN)
USER_FILE = "user.txt"

AUTHORIZED_USERS = load_users(USER_FILE)
logging.info(f"Загруженные авторизованные пользователи: {AUTHORIZED_USERS}")

=======
slack_client = WebClient(token=SLACK_TOKEN)

USER_FILE = "user.txt"
AUTHORIZED_USERS = load_users(USER_FILE)
logging.info(f"Загруженные авторизованные пользователи: {AUTHORIZED_USERS}")


def get_channel_name(channel_id):
    """Получаем имя канала по его ID."""
    try:
        response = slack_client.conversations_info(channel=channel_id)
        return response['channel']['name']
    except SlackApiError as e:
        logging.error(f"Ошибка при получении имени канала: {e.response['error']}")
        return channel_id  # Вернём ID, если имя не получилось достать


>>>>>>> d03ebd5 (Update all code)
@app.route("/slack/events", methods=["POST"])
def slack_events():
    try:
        data = request.json
<<<<<<< HEAD
        logging.info(f"Получены данные: {data}")

        if data.get("type") == "url_verification":
            challenge = data.get("challenge")
            logging.info(f"URL verification challenge: {challenge}")
            return jsonify({"challenge": challenge})

        if 'event' in data and data['event'].get('type') == 'reaction_added':
            logging.info("Событие reaction_added получено")
            event = data['event']
            reaction = event['reaction']  # Получаем реакцию
            user_id = event['user']  # ID пользователя, который поставил реакцию
            item = event['item']  # Данные о сообщении
            channel_id = item['channel']  # Канал, где было сообщение
            timestamp = item['ts']  # Время сообщения

            logging.info(f"Реакция: {reaction}, Пользователь: {user_id}, Канал: {channel_id}, Время: {timestamp}")

            response = slack_client.users_info(user=user_id)
            user_name = response['user']['real_name']
            logging.info(f"Имя пользователя: {user_name}")

            channel_info = slack_client.conversations_info(channel=channel_id)
            channel_name = channel_info['channel']['name']
            logging.info(f"Имя канала: {channel_name}")

            original_ts = data['event'].get('thread_ts', timestamp)


            if 'thread_ts' in event and event['thread_ts'] != event['item']['ts']:
                logging.info("Реакция добавлена в ответе на сообщение, пропускаем")
                return jsonify({"status": "ok"})

            replies = slack_client.conversations_replies(channel=channel_id, ts=original_ts)
            original_message_data = replies['messages'][0]
            original_message = original_message_data['text']
            original_user_id = original_message_data['user']
            original_user_info = slack_client.users_info(user=original_user_id)
            original_user_name = original_user_info['user']['real_name']

            logging.info(f"Оригинальное сообщение: {original_message}, Автор: {original_user_name}")

            if reaction == TRIGGER_EMOJI:
                if user_name.lower() in AUTHORIZED_USERS:
                    try:
                        # Получаем сообщение, на которое была добавлена реакция
                        original_message_data = slack_client.conversations_history(
                            channel=channel_id,
                            latest=timestamp,
                            limit=1,
                            inclusive=True
                        )['messages'][0]

                        response = slack_client.reactions_add(
                            channel=channel_id,
                            name="white_check_mark",
                            timestamp=original_ts
                        )

                        unix_time = float(timestamp)
                        date_normal = datetime.fromtimestamp(unix_time).strftime("%d.%m.%Y %H:%M")

                        logging.info(
                            f"Оригинальное сообщение: {original_message}\n"
                            f"Автор оригинального сообщения: {original_user_name}\n"
                            f"Кто решил: {user_name}\n"
                            f"Канал: {channel_name}\n"
                            f"Дата: {date_normal}\n"
                        )

                        insert_message(original_message, original_user_name, user_name, channel_name, date_normal)

                    except SlackApiError as e:
                        if e.response['error'] == 'already_reacted':
                            logging.info(f"Реакция уже добавлена к сообщению от {user_name}")
                        else:
                            logging.error(f"Ошибка: {e.response['error']}")
                else:
                    logging.info(f"Пользователь {user_name} не технический специалист")
        return jsonify({"status": "ok"})
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    create_table()
    logging.info("Таблица создана")
=======
        logging.info(f"Получены данные: {json.dumps(data, indent=2, ensure_ascii=False)}")

        if data.get("type") == "url_verification":
            return jsonify({"challenge": data["challenge"]})

        if 'event' not in data or data['event'].get('type') != 'reaction_added':
            return jsonify({"status": "ignored"})

        event = data['event']
        reaction = event.get('reaction')
        user_id = event.get('user')
        channel_id = event['item'].get('channel')
        message_ts = event['item'].get('ts')

        logging.info(f"Получена реакция '{reaction}' от пользователя {user_id} на сообщение {message_ts}")

        # Реакция должна быть именно та, что указана в TRIGGER_EMOJI
        if reaction != TRIGGER_EMOJI:
            logging.info(f"Реакция '{reaction}' не соответствует триггеру '{TRIGGER_EMOJI}', пропускаем")
            return jsonify({"status": "ok"})

        # Проверяем, что реакция на главное сообщение, а не в треде
        if 'thread_ts' in event and event['thread_ts'] != message_ts:
            logging.info(f"Реакция в треде — пропускаем (ts={message_ts})")
            return jsonify({"status": "ok"})

        # Получаем информацию о пользователе, который поставил реакцию
        user_info = slack_client.users_info(user=user_id)
        user_name = user_info['user']['real_name']

        if user_name.lower() not in AUTHORIZED_USERS:
            logging.info(f"Пользователь {user_name} не авторизован для отметок")
            return jsonify({"status": "ok"})

        # Получаем оригинальное сообщение
        history = slack_client.conversations_history(
            channel=channel_id,
            latest=message_ts,
            limit=1,
            inclusive=True
        )

        if not history['messages']:
            logging.warning(f"Не удалось получить сообщение {message_ts} из канала {channel_id}")
            return jsonify({"status": "ok"})

        original_message_data = history['messages'][0]
        original_message_text = original_message_data.get('text', '')
        original_user_id = original_message_data.get('user', '')

        # Получаем имя автора сообщения
        original_user_info = slack_client.users_info(user=original_user_id)
        original_user_name = original_user_info['user']['real_name']

        # Добавляем галочку, если её ещё нет
        try:
            slack_client.reactions_add(
                channel=channel_id,
                name="white_check_mark",
                timestamp=message_ts
            )
        except SlackApiError as e:
            if e.response['error'] == 'already_reacted':
                logging.info("Галочка уже стоит, пропускаем добавление")
            else:
                logging.error(f"Ошибка при добавлении реакции: {e.response['error']}")
                return jsonify({"status": "error"})

        # Получаем имя канала
        channel_name = get_channel_name(channel_id)

        # Форматируем дату
        unix_time = float(message_ts)
        date_normal = datetime.fromtimestamp(unix_time).strftime("%d.%m.%Y %H:%M")

        # Логируем и сохраняем в базу
        logging.info(
            f"Добавляем запись в БД: сообщение='{original_message_text}', "
            f"автор='{original_user_name}', решил='{user_name}', канал='{channel_name}', дата='{date_normal}'"
        )

        insert_message(original_message_text, original_user_name, user_name, channel_name, date_normal)

        return jsonify({"status": "ok"})

    except Exception as e:
        logging.exception("Ошибка обработки события Slack")
        return jsonify({"status": "error", "message": str(e)})


if __name__ == "__main__":
    create_table()
>>>>>>> d03ebd5 (Update all code)
    app.run(host="0.0.0.0", port=3001)