import os
import io
import requests
from dotenv import load_dotenv
from telegram import Bot, InputFile
from telegram.error import TelegramError
from requests.exceptions import RequestException
from url_get_file_extension import get_file_extension


def send_to_telegram(message_text: str, image_link: str = None) -> int | None:
    load_dotenv()
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    telegram_channel_id = os.getenv("TELEGRAM_CHANNEL_ID")
    telegram_bot = Bot(token=telegram_token)

    try:
        if image_link:
            request_headers = {"User-Agent": "Mozilla/5.0"}
            image_response = requests.get(image_link.strip(), headers=request_headers)
            image_response.raise_for_status()
            image_bytes = image_response.content

            extension = get_file_extension(image_link)

            if extension == ".gif":
                message = telegram_bot.send_animation(
                    chat_id=telegram_channel_id,
                    animation=InputFile(io.BytesIO(image_bytes), filename="animation.gif"),
                    caption=message_text,
                    parse_mode="HTML"
                )
            else:
                message = telegram_bot.send_photo(
                    chat_id=telegram_channel_id,
                    photo=InputFile(io.BytesIO(image_bytes), filename="image" + extension),
                    caption=message_text,
                    parse_mode="HTML"
                )
        else:
            message = telegram_bot.send_message(
                chat_id=telegram_channel_id,
                text=message_text,
                parse_mode="HTML"
            )

        return message.message_id

    except (TelegramError, RequestException):
        return None
