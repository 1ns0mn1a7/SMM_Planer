import os
from dotenv import load_dotenv
from telegram import Bot
from telegram.error import TelegramError


def delete_post_from_telegram(message_id: int) -> bool:
    load_dotenv()
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    telegram_channel_id = os.getenv("TELEGRAM_CHANNEL_ID")
    telegram_bot = Bot(token=telegram_token)

    try:
        telegram_bot.delete_message(
            chat_id=telegram_channel_id,
            message_id=message_id
        )
        return True

    except TelegramError:
        return False
