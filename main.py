import os
from dotenv import load_dotenv
import slack_sdk

TRACKED_WORD = "Вопрос решён"

load_dotenv('key.env')

SLACK_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")

