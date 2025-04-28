import os
import time
from dotenv import load_dotenv

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from auth import get_credentials
from post_to_telegram import send_to_telegram
from post_to_vk import post_vk
from post_to_ok import post_to_ok
from delete_post_from_telegram import delete_post_from_telegram
from delete_post_from_ok import delete_post_from_ok
from post_to_vk import delete_post_vk
from google_api import (
    get_all_posts,
    get_posts_to_publish,
    get_txt_document_id,
    get_text_from_document,
    change_status_published_post,
    set_post_id,
    get_image_document_id,
    get_file_title,
    download_image,
    get_posts_to_delete,
    clear_cell_deleted_post,
    unset_flag,
    update_status
)


def load_content(posts, creds):
    dct_posts = {}
    for post in posts:
        document_url = post.get('Текст')
        img_url = post.get('Картинка')
        post_id = int(post.get('Пост')) + 1

        txt_document_id = get_txt_document_id(document_url)
        text = get_text_from_document(creds, txt_document_id)
        dct_posts[post_id] = {
            "text": text,
            "img_url": img_url,
            "tg": "TRUE" == post.get('Telegram'),
            "vk": "TRUE" == post.get('VK'),
            "ok": "TRUE" == post.get('ОК'),
            "detele": "TRUE" == post.get('Удалить'),
            "delete_at": post.get('Удалить в'),
            "tg_post_id": post.get('TG_POST_ID'),
            "vk_post_id": post.get('VK_POST_ID'),
            "ok_post_id": post.get('OK_POST_ID')
        }
    return dct_posts


def planner_loop(creds, spreadsheet_id, drive, folder='src'):
    all_posts = get_all_posts(creds, spreadsheet_id)
    posts = get_posts_to_publish(all_posts)
    dct_posts = load_content(posts, creds)
    for row_num, post_dct in dct_posts.items():
        post_id = None
        text = post_dct.get('text')
        img_url = post_dct.get('img_url')

        if post_dct.get('tg'):
            post_id = send_to_telegram(text, img_url)
            if post_id:
                set_post_id(creds, spreadsheet_id, post_id, row_num, 'tg')
                change_status_published_post(creds, spreadsheet_id, 'опубликовано', row_num, 'tg')
                unset_flag(creds, spreadsheet_id, row_num, 'tg')
            else:
                change_status_published_post(creds, spreadsheet_id, 'ошибка', row_num, 'tg')

        if post_dct.get('vk'):
            if img_url.startswith('https://drive.google.com'):
                os.makedirs(folder, exist_ok=True)
                image_document_id = get_image_document_id(img_url)
                image_title = get_file_title(image_document_id, drive)
                filepath = download_image(image_document_id, image_title, drive, folder)
                post_id = post_vk(text, filepath)
            else:
                post_id = post_vk(text, img_url)

            if post_id:
                set_post_id(creds, spreadsheet_id, post_id, row_num, 'vk')
                change_status_published_post(creds, spreadsheet_id, 'опубликовано', row_num, 'vk')
                unset_flag(creds, spreadsheet_id, row_num, 'vk')
            else:
                change_status_published_post(creds, spreadsheet_id, 'ошибка', row_num, 'vk')

        if post_dct.get('ok'):
            if img_url.startswith('https://drive.google.com'):
                os.makedirs(folder, exist_ok=True)
                image_document_id = get_image_document_id(img_url)
                image_title = get_file_title(image_document_id, drive)
                filepath = download_image(image_document_id, image_title, drive, folder)
                post_id = post_to_ok(text, filepath)
            else:
                post_id = post_to_ok(text, img_url)

            if post_id:
                set_post_id(creds, spreadsheet_id, post_id, row_num, 'ok')
                change_status_published_post(creds, spreadsheet_id, 'опубликовано', row_num, 'ok')
                unset_flag(creds, spreadsheet_id, row_num, 'ok')
            else:
                change_status_published_post(creds, spreadsheet_id, 'ошибка', row_num, 'ok')

    posts_to_delete = get_posts_to_delete(all_posts)
    dct_posts = load_content(posts_to_delete, creds)
    for post_id, value in dct_posts.items():

        if tg_post_id := value.get('tg_post_id'):
            deleted_tg = delete_post_from_telegram(tg_post_id)
            if deleted_tg:
                print('tg_del')
                change_status_published_post(creds, spreadsheet_id, 'удалён', post_id, 'tg')
                clear_cell_deleted_post(creds, spreadsheet_id, post_id, 'tg_post_id')
                unset_flag(creds, spreadsheet_id, post_id, 'delete')
        if vk_post_id := value.get('vk_post_id'):
            deleted_vk = delete_post_vk(vk_post_id)
            if deleted_vk:
                print('vk_del')
                change_status_published_post(creds, spreadsheet_id, 'удалён', post_id, 'vk')
                clear_cell_deleted_post(creds, spreadsheet_id, post_id, 'vk_post_id')
                unset_flag(creds, spreadsheet_id, post_id, 'delete')

        if ok_post_id := value.get('ok_post_id'):
            deleted_ok = delete_post_from_ok(ok_post_id)
            if deleted_ok:
                print('ok_del')
                change_status_published_post(creds, spreadsheet_id, 'удалён', post_id, 'ok')
                clear_cell_deleted_post(creds, spreadsheet_id, post_id, 'ok_post_id')
                unset_flag(creds, spreadsheet_id, post_id, 'delete')

    update_status(creds, spreadsheet_id, all_posts)


def main():
    load_dotenv()
    timeout = int(os.getenv("TIMEOUT_CALL", 60))
    spreadsheet_id = os.getenv('SPREADSHEET_ID') 
    creds = get_credentials()

    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)

    while 1:
        planner_loop(creds, spreadsheet_id, drive)
        time.sleep(timeout)


if __name__ == "__main__":
    main()
