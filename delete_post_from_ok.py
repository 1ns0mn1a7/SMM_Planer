import os
import requests
from dotenv import load_dotenv
from generate_sig import generate_sig


def delete_post_from_ok(post_id: str) -> bool:
    load_dotenv()

    access_token = os.getenv("OK_ACCESS_TOKEN")
    application_key = os.getenv("OK_APP_KEY")
    session_secret_key = os.getenv("OK_SESSION_SECRET")

    request_params = {
        "application_key": application_key,
        "method": "mediatopic.deleteTopic",
        "access_token": access_token,
        "format": "json",
        "topic_id": post_id
    }

    request_params["sig"] = generate_sig(request_params, session_secret_key)

    try:
        response = requests.post(
            "https://api.ok.ru/fb.do",
            data=request_params,
            timeout=10
        )
        result = response.json()

        return isinstance(result, dict) and result.get("success") is True

    except requests.RequestException:
        return False
