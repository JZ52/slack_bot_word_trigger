import os
import json
# import psycopg2
# from psycopg2 import OperationalError
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from slack_sdk.rtm import RTMClient
from slack_sdk.web import WebClient
from slack_sdk.errors import SlackApiError
from datetime import datetime

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
# SQL_ADRES = os.getenv("SQL_ADRES")
# SQL_USER = os.getenv("SQL_USER")
# SQL_PASSWORD = os.getenv("SQL_PASSWORD")
# SQL_DATABASE = os.getenv("SQL_DATABASE")
# SQL_PORT = os.getenv("SQL_PORT")

SLACK_TOKEN = os.getenv("BOT_USER_OAUTH_TOKEN")
rtm_client = RTMClient(token=SLACK_TOKEN)
slack_client = WebClient(token=SLACK_TOKEN)



# try:
#     connection = psycopg2.connect(
#         host = SQL_ADRES,
#         user = SQL_USER,
#         password =  SQL_PASSWORD,
#         database = SQL_DATABASE,
#         port = SQL_PORT,
#         client_encoding = 'UTF8'
#     )
#
#     cursor = connection.cursor()
#     print("Успешное подключение к базе данных")
# except OperationalError as e:
#     print(f"Ошибка подключения: {e}")


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

        if any(word in data['event']['text'] for word in TRIGGER_WORD):
            try:
                slack_client.reactions_add(channel = channel_id, timestamp = timestamp, name = "white_check_mark")
                response = slack_client.reactions_add(
                    channel= data['event']['channel'],
                    name = "white_check_mark",
                    timestamp = data['event']['ts']
                )

            except SlackApiError as e:
                if e.response['error'] == 'already_reacted':
                    print(f"Реакция добавлена к сообщению от { user_name }")
                    unix_time = float(timestamp)
                    date_normal = datetime.fromtimestamp(unix_time).strftime("%d-%m-%Y %H:%M:%S")
                    print(
                        f"{data['event']['text']}\n"
                        f"{user_id}\n"
                        f"{channel_id}\n"
                        f"{date_normal}\n"
                    )
                else:
                    print(f"Ошибка { e.response['error'] }")
        return jsonify({"status" : "ok"})

if __name__ == "__main__":
    app.run(port=3001)