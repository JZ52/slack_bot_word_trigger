import os
import sqlite3
import psycopg2
from psycopg2 import OperationalError
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from slack_sdk.rtm import RTMClient
from slack_sdk.web import WebClient

app = Flask(__name__)
SQL_ADRES = os.getenv("SQL_ADRES")
SQL_USER = os.getenv("SQL_USER")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_PORT = os.getenv("SQL_PORT")


try:
    connection = psycopg2.connect(
        host = SQL_ADRES,
        user = SQL_USER,
        password = SQL_PASSWORD,
        database = SQL_DATABASE,
        port = SQL_PORT,
        client_encoding = 'UTF8'
    )

    cursor = connection.cursor()
    print("Успешное подключение к базе данных")
except OperationalError as e:
    print(f"Ошибка подключения: {e}")


@app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.json
    event = data.get("event", {})
    if data.get("type") == "url_verification":
        challenge = data.get("challenge")
        return jsonify({"challenge": challenge})

    # if event.get("type") == "message" and not event.get("bot_id") and event.get("channel_type") == "im":
    #     user = event.get("user")
    #     text = event.get("text")

        #cursor.execute("INSERT INTO message (user, message) VALUES (?, ?)", (user, text))
        #conn.commit()

        #return "Message received", 200

    return "OK", 200


if __name__ == "__main__":
    app.run(port=3001)

TRACKED_WORD = "Вопрос решён"

load_dotenv('key.env')

SLACK_TOKEN = os.getenv("BOT_USER_OAUTH_TOKEN")
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
rtm_client = RTMClient(token=SLACK_TOKEN)
slack_client = WebClient(token=SLACK_TOKEN)
