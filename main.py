import os
import time
from dotenv import load_dotenv

from auth import get_credentials
from post_to_telegram import send_to_telegram
from post_to_vk import post_vk
from google_api import (
    get_all_posts,
    get_posts_to_publish,
    get_txt_document_id,
    get_text_from_document,
    change_status_published_post,
    set_post_id
)

STATUSES = ["POSTED", "ERROR", "WAIT", "DELETED"]


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
            "ok": "TRUE" == post.get('OK')
            }
    return dct_posts


def planner_loop(creds, spreadsheet_id):
    # получаем таблицу
    all_posts = get_all_posts(creds, spreadsheet_id)
    # получаем посты на публикацию ("ERROR", "WAIT")
    posts = get_posts_to_publish(all_posts)
    # качаем контент(pic, text)
    dct_posts = load_content(posts, creds)
    print(dct_posts)
    for row_num, post_dct in dct_posts.items():
        post_id = None
        text = post_dct.get('text')
        img_url = post_dct.get('img_url')
        
        if post_dct.get('tg'):
            post_id = send_to_telegram(text, img_url)
            if post_id:
                set_post_id(
                    creds,
                    spreadsheet_id, 
                    post_id,
                    row_num,
                    'tg'
                )
                change_status_published_post(
                    creds,
                    spreadsheet_id,
                    'опубликовано',
                    row_num, 
                    'tg',
                )
            elif post_id is None:
                change_status_published_post(
                    creds,
                    spreadsheet_id,
                    'ошибка',
                    row_num,
                    'tg',
                )

        # if post_dct.get('vk'):
        #     post_id = post_vk(text, img_url)
        #     if post_id:
        #         set_post_id(
        #             creds,
        #             spreadsheet_id, 
        #             post_id,
        #             row_num,
        #             'vk'
        #         )
        #         change_status_published_post(
        #             creds,
        #             spreadsheet_id,
        #             'опубликовано',
        #             row_num, 
        #             'vk',
        #         )
        #     elif post_id is None:
        #         change_status_published_post(
        #             creds,
        #             spreadsheet_id,
        #             'ошибка',
        #             row_num,
        #             'vk',
        #         )
        # отдаём контент(пост) в соответствующий модуль
        # получаем статус успех/ошибка
        # 
        print(post_id)
        # меняем статус в таблице.

    # # Получение списка постов на удаление


def main():
    load_dotenv()
    timeout = int(os.getenv("TIMEOUT_CALL", 60 * 60))
    spreadsheet_id = os.getenv('SPREADSHEET_ID') 
    creds = get_credentials()

    while 1:
        planner_loop(creds, spreadsheet_id)
        time.sleep(timeout)


if __name__ == "__main__":
    main()