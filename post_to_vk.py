import requests
import os

from dotenv import load_dotenv


def post_vk(message):
    load_dotenv()
    vk_api_key_group = os.getenv("VK_API_KEY")

    payload_wall_post = {
        "owner_id": -230220710,
        "message": message, 
        "access_token": vk_api_key_group,
        "v": 5.199
    }
    url = "https://api.vk.com/method/wall.post"    
    response = requests.get(url, params=payload_wall_post)
    response.raise_for_status()
    return response.json()["response"]["post_id"]


def delete_post_vk(post_id):

    # Для работы необходим токен пользователя

    load_dotenv()
    vk_api_key_user = os.getenv("Токен пользователя")

    payload = {
        "owner_id": -230220710,
        "post_id": post_id, 
        "access_token": vk_api_key_user,
        "v": 5.199
    }
    url = "https://api.vk.com/method/wall.delete"    
    response = requests.get(url, params=payload)
    response.raise_for_status()


def main():
    
    message = "Текст поста"
    post_vk(message)


if __name__ == '__main__':
    main()
