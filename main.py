import os
import json
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from slack_sdk.rtm import RTMClient
from slack_sdk.web import WebClient
from slack_sdk.errors import SlackApiError
from datetime import datetime
from models import create_table, insert_message, load_users
import logging

load_dotenv('key.env')

TRIGGER_EMOJI = "slack"

app = Flask(__name__)

SLACK_TOKEN = os.getenv("BOT_USER_OAUTH_TOKEN")
rtm_client = RTMClient(token=SLACK_TOKEN)
slack_client = WebClient(token=SLACK_TOKEN)
USER_FILE = "user.txt"

AUTHORIZED_USERS = load_users(USER_FILE)

@app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.json
    if data.get("type") == "url_verification":
        challenge = data.get("challenge")
        return jsonify({"challenge": challenge})

    if 'event' in data and data['event'].get('type') == 'reaction_added':
        logging.info("Событие reaction_added получено")
        event = data['event']
        reaction = event['reaction']  # Получаем реакцию
        user_id = event['user']  # ID пользователя, который поставил реакцию
        item = event['item']  # Данные о сообщении
        channel_id = item['channel']  # Канал, где было сообщение
        timestamp = item['ts']  # Время сообщения



        response = slack_client.users_info(user=user_id)
        user_name = response['user']['real_name']

        channel_info = slack_client.conversations_info(channel=channel_id)
        channel_name = channel_info['channel']['name']

        original_ts = data['event'].get('thread_ts', timestamp)

        replies = slack_client.conversations_replies(channel=channel_id, ts=original_ts)
        original_message_data = replies['messages'][0]
        original_message = original_message_data['text']
        original_user_id = original_message_data['user']
        original_user_info = slack_client.users_info(user = original_user_id)
        original_user_name = original_user_info['user']['real_name']


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
                        channel = channel_id,
                        name = "white_check_mark",
                        timestamp = original_ts
                    )

                    unix_time = float(timestamp)
                    date_normal = datetime.fromtimestamp(unix_time).strftime("%d.%m.%Y %H:%M")

                    print(
                    f"Оригинальное сообщение: {original_message}\n"
                    f"Автор оригинального сообщения: {original_user_name}\n"
                    f"Кто решил: {user_name}\n"
                    f"Канал: {channel_name}\n"
                    f"Дата: {date_normal}\n"
                    )

                    insert_message(original_message, original_user_name, user_name, channel_name, date_normal)

                except SlackApiError as e:
                    if e.response['error'] == 'already_reacted':
                        print(f"Реакция добавлена к сообщению от { user_name }")
                    else:
                        print(f"Ошибка { e.response['error'] }")
            else:
                print(f"Пользователь { user_name }  не технический специалист")
    return jsonify({"status" : "ok"})

if __name__ == "__main__":
    create_table()
    app.run(host = "0.0.0.0", port=3001)