import os
import io
import requests
import json
from dotenv import load_dotenv
from url_get_file_extension import get_file_extension
from generate_sig import generate_sig


def upload_photo(image_url: str, access_token: str, application_key: str, group_id: str):
    upload_params = {
        "method": "photosV2.getUploadUrl",
        "application_key": application_key,
        "access_token": access_token,
        "gid": group_id,
        "format": "json"
    }

    try:
        upload_url_response = requests.post(
            "https://api.ok.ru/fb.do",
            data=upload_params, timeout=10
        ).json()

        upload_url = upload_url_response.get("upload_url")
        if not upload_url:
            return None

        image_response = requests.get(image_url.strip(), timeout=10)
        image_response.raise_for_status()
        image_bytes = image_response.content

        extension = get_file_extension(image_url)
        filename = f"image{extension}"
        content_type = f"image/{extension.lstrip('.')}"
        files = {"photo": (filename, io.BytesIO(image_bytes), content_type)}

        upload_result = requests.post(upload_url, files=files, timeout=10).json()

        if upload_result.get("photos"):
            photo_info = list(upload_result["photos"].values())[0]
            return photo_info.get("token")

        return None
    except requests.RequestException:
        return None


def post_to_ok(message_text: str, image_url: str = None) -> str | None:
    load_dotenv()

    access_token = os.getenv("OK_ACCESS_TOKEN")
    application_key = os.getenv("OK_APP_KEY")
    session_secret_key = os.getenv("OK_SESSION_SECRET")
    group_id = os.getenv("OK_GROUP_ID")

    media = []

    if message_text:
        media.append({"type": "text", "text": message_text})

    if image_url:
        photo_token = upload_photo(image_url, access_token, application_key, group_id)
        if photo_token:
            media.append({"type": "photo", "list": [{"id": photo_token}]})

    if not media:
        return None

    attachment_json = json.dumps({"media": media}, ensure_ascii=True)

    request_params = {
        "application_key": application_key,
        "method": "mediatopic.post",
        "gid": group_id,
        "type": "GROUP_THEME",
        "access_token": access_token,
        "attachment": attachment_json,
        "format": "json"
    }

    request_params["sig"] = generate_sig(request_params, session_secret_key)

    try:
        response = requests.post(
            "https://api.ok.ru/fb.do",
            data=request_params,
            timeout=10
        )
    except requests.RequestException:
        return None

    try:
        result = response.json()
    except (ValueError, TypeError):
        result = response.text

    if isinstance(result, dict):
        if result.get("error_code") is None:
            return result.get("result")
        return None

    if isinstance(result, str) and result.isdigit():
        return result

    return None
