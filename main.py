import os
import json
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from slack_sdk.rtm import RTMClient
from slack_sdk.web import WebClient
from slack_sdk.errors import SlackApiError
from datetime import datetime
from models import create_table, insert_message, load_users

load_dotenv('key.env')

TRIGGER_WORD = (
    "Вопрос решён",
    "Вопрос решен",
    "вопрос решён",
    "вопрос решен",
    "Вопрос решён!",
    "Вопрос решен!",
    "вопрос решён!",
    "вопрос решен!",
)

app = Flask(__name__)

SLACK_TOKEN = os.getenv("BOT_USER_OAUTH_TOKEN")
rtm_client = RTMClient(token=SLACK_TOKEN)
slack_client = WebClient(token=SLACK_TOKEN)
USER_FILE = "user.txt"

AUTHORIZED_USERS = load_users(USER_FILE)

@app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.json
    #print(data)
    if data.get("type") == "url_verification":
        challenge = data.get("challenge")
        return jsonify({"challenge": challenge})

    #print(json.dumps(data, indent=4, ensure_ascii=False))
    if 'event' in data and 'text' in data['event']:
        message_text = data['event']['text']
        user_id = data['event']['user']
        channel_id = data['event']['channel']
        timestamp = data['event']['ts']

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


        if any(word in message_text for word in TRIGGER_WORD):
                    print(AUTHORIZED_USERS)
                    if user_name.lower() in AUTHORIZED_USERS:
                        try:
                            response = slack_client.reactions_add(
                                channel= channel_id,
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
    app.run(port=3001)