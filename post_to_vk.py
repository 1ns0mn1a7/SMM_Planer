import requests
import os

from dotenv import load_dotenv

# message = "Тест путь гиф"
# media_url = "src/picture.gif"
# "https://i.pinimg.com/736x/4d/10/d1/4d10d1797711846a6dfbc4d51d6b3bdb.jpg"
# "https://trikky.ru/wp-content/blogs.dir/1/files/2022/04/22/unnamed-file.gif"
# "src/picture.jpg"


def download_media(media_url):

    os.makedirs("src", exist_ok=True)

    resolution = os.path.splitext(media_url)[1]
    file_path = os.path.join("src", f"picture{resolution}")
    response = requests.get(media_url)
    response.raise_for_status()

    with open(file_path, "wb") as file:
        file.write(response.content)

    return file_path


def jpg_get_wall_upload_server(group_id, vk_api_key, media_url):

    url = "https://api.vk.com/method/photos.getWallUploadServer"
    payload = {
        "access_token": vk_api_key,
        "group_id": group_id,
        "v": 5.199
    }
    response = requests.get(url, params=payload)
    response.raise_for_status()
    upload_url = response.json()["response"]["upload_url"]

    response = requests.post(upload_url, files={'photo': open(media_url, 'rb')})

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


def gif_get_wall_upload_server(group_id, vk_api_key, media_url):

    url = "https://api.vk.com/method/docs.getWallUploadServer"
    payload = {
        "access_token": vk_api_key,
        "group_id": group_id,
        "v": 5.199
    }

    response = requests.get(url, params=payload)
    response.raise_for_status()

    upload_url = response.json()["response"]["upload_url"]

    response = requests.post(upload_url, files={'file': open(media_url, 'rb')})

    url = "https://api.vk.com/method/docs.save"
    payload = {
        "access_token": vk_api_key,
        'file': response.json()['file'],
        "v": 5.199

    }
    response = requests.get(url, params=payload)
    response.raise_for_status()

    gif_link = f"doc{response.json()["response"]["doc"]["owner_id"]}_{response.json()["response"]["doc"]["id"]}"
    
    return gif_link


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


def get_attachments_vk_link(group_id, vk_api_key, media_url):

    if os.path.isfile(media_url):

        if os.path.splitext(media_url)[1] == ".gif":
            attachments = gif_get_wall_upload_server(group_id, vk_api_key, media_url)

        if (
            os.path.splitext(media_url)[1] == ".jpg" 
            or os.path.splitext(media_url)[1] == ".png"
        ):
            attachments = jpg_get_wall_upload_server(group_id, vk_api_key, media_url)

    else:

        file_path = download_media(media_url)

        if os.path.splitext(media_url)[1] == ".gif":
            attachments = gif_get_wall_upload_server(group_id, vk_api_key, file_path)

        if os.path.splitext(media_url)[1] == ".jpg":
            attachments = jpg_get_wall_upload_server(group_id, vk_api_key, file_path)
  
    return attachments


def post_vk(message, media_url):

    # Возвращает номер созданного поста строкой

    load_dotenv()

    vk_api_key = os.getenv("VK_API_KEY")
    owner_id = os.getenv("VK_OWNER_ID")
    group_id = os.getenv("VK_GROUP_ID")

    attachments = get_attachments_vk_link(group_id, vk_api_key, media_url)

    payload_wall_post = {
        "owner_id": owner_id,
        "message": message, 
        "access_token": vk_api_key,
        "attachments": attachments,
        "v": 5.199
    }
    url = "https://api.vk.com/method/wall.post"    
    response = requests.get(url, params=payload_wall_post)
    response.raise_for_status()
    return response.json()["response"]["post_id"]
