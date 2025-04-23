import requests
import os

from dotenv import load_dotenv

load_dotenv()

vk_api_key = os.getenv("VK_API_KEY")


url_get_upload_server = "https://api.vk.com/method/photos.getUploadServer"

payload = {
    "album_id": 306982325,
    "group_id": 230220710 
}

response = requests.get(url_get_upload_server, params=payload)
response.raise_for_status()
print(response.json())


# payload_wall_post = {
#     "owner_id": -230220710,
#     "message": "Запись сообщества",
#     "attachments": "",  
#     "access_token": vk_api_key,
#     "v": 5.199
# }

# url = "https://api.vk.com/method/wall.post"

# response = requests.get(url, params=payload)
# response.raise_for_status()


def main():

    print(vk_api_key)


if __name__ == '__main__':
    main()
