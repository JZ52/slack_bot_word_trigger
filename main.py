import os
from dotenv import load_dotenv
import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode.builtin import SocketModeHandler
import json
from datetime import datetime

load_dotenv("key.env")

SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
BOT_USER_OAUTH_TOKEN = os.getenv("BOT_USER_OAUTH_TOKEN")

EMOJI = os.getenv("emoji")

logging.basicConfig(filename='slack_bot.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)



if not SLACK_APP_TOKEN or not BOT_USER_OAUTH_TOKEN:
    print(f"Not found key. Need check .env")
    exit(1)

app = App(token=BOT_USER_OAUTH_TOKEN)

try:
    with open("user.txt", "r", encoding="utf-8") as file:
        temp = file.read()
        admin_list = temp.lower()
except FileNotFoundError:
    print("List with admin not found!")


@app.event("reaction_added")
def handle_reaction_added(event, client, logger):
    #print("Data: ", json.dumps(event, indent=4, ensure_ascii=False))
    user_id = event.get("user")
    item = event.get("item")
    channel_id = item.get("channel")
    reaction = event.get("reaction")

    user_name = user_id
    channel_name = channel_id

    try:
        response_name = client.users_info(user=user_id)
        #print("Data:", json.dumps(response_name.data, indent=4, ensure_ascii=False))
        if response_name["ok"]:
            users = response_name["user"]["real_name"]
    except Exception as e:
        logger.error(f"Not found user name: {e}")

    try:
        response_channel = client.conversations_info(channel=channel_id)
        #print("Data:", json.dumps(response_channel.data, indent=4, ensure_ascii=False))
        if response_channel["ok"]:
            channel_names = response_channel["channel"]["name"]
    except Exception as e:
        logger.error(f"Not found user name: {e}")

    if reaction == EMOJI:
        if users.lower() in admin_list:
            message_ts = item.get("ts")
            history = client.conversations_history(
                channel=channel_id,
                latest=message_ts,
                inclusive=True,
                limit=1
            )
            if history["ok"] and len(history["messages"]) > 0:
                target_message = history["messages"][0]
                print(f"Message { target_message["text"] }")
                original_message = target_message["text"]
                ts_raw = target_message["ts"]
                date_ts = datetime.fromtimestamp(float(ts_raw))
                date_string = date_ts.strftime("%Y-%m-%d %H:%M:%S")
            else:
                thread_ts = target_message.get("thread_ts")
        else:
            print("User not admin")
    #else:




if __name__ == "__main__":
    print("Slack bot started")
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()