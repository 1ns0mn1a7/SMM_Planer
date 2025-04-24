import requests
import os

from dotenv import load_dotenv

# owner id (id группы) должен быть со знаком -
owner_id = -230220710 
# group id (id группы) 
group_id = 230220710
message = "Текст поста"
photo_url = "https://i1.sndcdn.com/avatars-000247982818-ak7ft3-t500x500.jpg"


def download_photo(photo_url):
    
    response = requests.get(photo_url)
    response.raise_for_status()

    with open("picture.jpg", "wb") as file:
        file.write(response.content)


def get_wall_upload_server(group_id, vk_api_key, photo_url):

    download_photo(photo_url)

    url = "https://api.vk.com/method/photos.getWallUploadServer"
    payload = {
        "access_token": vk_api_key,
        "group_id": group_id,
        "v": 5.199
    }
    response = requests.get(url, params=payload)
    response.raise_for_status()
    upload_url = response.json()["response"]["upload_url"]

    response = requests.post(upload_url, files={'photo': open('picture.jpg', 'rb')})

    url = "https://api.vk.com/method/photos.saveWallPhoto"
    payload = {
        "access_token": vk_api_key,
        "group_id": group_id,
        'photo': response.json()['photo'],
        'server': response.json()['server'],
        'hash': response.json()['hash'],
        "v": 5.199

    }
    response = requests.get(url, params=payload)
    response.raise_for_status()

    photo_link = f"photo{response.json()["response"][0]["owner_id"]}_{response.json()["response"][0]["id"]}"

    return photo_link

    
def post_vk(message, photo_url, owner_id, group_id, vk_api_key):

    # Возвращает номер созданного поста строкой

    payload_wall_post = {
        "owner_id": owner_id,
        "message": message, 
        "access_token": vk_api_key,
        "attachments": get_wall_upload_server(group_id, vk_api_key, photo_url),
        "v": 5.199
    }
    url = "https://api.vk.com/method/wall.post"    
    response = requests.get(url, params=payload_wall_post)
    response.raise_for_status()
    return response.json()["response"]["post_id"]


def delete_post_vk(post_id, owner_id, vk_api_key):

    # Возвращает 1 при удачном удалении поста строкой

    payload = {
        "owner_id": owner_id,
        "post_id": post_id, 
        "access_token": vk_api_key,
        "v": 5.199
    }
    url = "https://api.vk.com/method/wall.delete"    
    response = requests.get(url, params=payload)
    response.raise_for_status()
    print(response.json()["response"])


def main():

    load_dotenv()

    vk_api_key = os.getenv("VK_API_KEY")

    post_vk(message, photo_url, owner_id, group_id, vk_api_key)


if __name__ == '__main__':
    main()
