import os
from dotenv import load_dotenv
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from urllib import parse
# from pprint import pprint

from googleapiclient.discovery import build
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from auth import get_credentials


# Получение всех постов в формате list[dict], 
# явно указывается диапазон таблицы (range)

def get_all_posts(creds, spreadsheet_id):
    service = build('sheets', 'v4', credentials=creds)
    request = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, 
        range='A1:P', 
        valueRenderOption='FORMATTED_VALUE',
    )

    list_posts = request.execute()['values']

    keys = list_posts[0]
    all_posts = []
    for row in list_posts[1:]:
        row_dict = {}
        for key, value in zip(keys, row):
            row_dict[key] = value
        all_posts.append(row_dict)

    return all_posts


# Изменение статуса на 'опубликовано' 

def change_status_published_post(creds, spreadsheet_id, status, row_number, platform): 
    dct = {
        'vk': 'L',
        'tg': 'K',
        'ok': 'M'
    }  
    service = build('sheets', 'v4', credentials=creds)
    body = {
        'values': [[status]]
    }
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, 
        range=f"Лист1!{dct.get(platform)}{row_number}", 
        valueInputOption='USER_ENTERED',
        body=body,
    ).execute()


def set_post_id(creds, spreadsheet_id, post_id, row_number, platform):
    dct = {
        'vk': 'P',
        'tg': 'N',
        'ok': 'O'
    }
    service = build('sheets', 'v4', credentials=creds)
    body = {
        'values': [[post_id]]
    }
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, 
        range=f"Лист1!{dct.get(platform)}{row_number}", 
        valueInputOption='USER_ENTERED',
        body=body,
    ).execute()


# Получение списка постов на публикацию

def get_posts_to_publish(all_posts):
    posts_to_publish = []
    for i, row in enumerate(all_posts, 1):
        if row.get('Статус') == 'опубликовано' or row.get('Статус') == 'удалён':
            continue

        publication_time = datetime.strptime(
            f'{row["Дата"]} {row["Время"]}', '%d.%m.%y %H:%M'
        )
        if publication_time <= datetime.now():
            row['id'] = i
            posts_to_publish.append(row)
    return posts_to_publish


# Получение списка постов на удаление и смена статуса в google таблице

def get_posts_to_delete(all_posts, creds, spreadsheet_id, row_number):
    posts_to_delete = []

    for i, row in enumerate(all_posts, 1):
        if row.get('Статус') == 'опубликовано' and row.get('Удалить') == 'TRUE':
            deletion_time = datetime.strptime(
                f'{row["Удалить в"]}', '%d.%m.%y %H:%M'
            )
        
            if deletion_time <= datetime.now():
                row['id'] = i
                posts_to_delete.append(row)
                change_status_deleted_post(creds, spreadsheet_id, row_number=i+1)
    return posts_to_delete


def change_status_deleted_post(creds, spreadsheet_id, row_number):    
    service = build('sheets', 'v4', credentials=creds)
    body = {
        'values': [['удалён']]
    }     
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, 
        range=f"Лист1!K{row_number}", 
        valueInputOption='USER_ENTERED',
        body=body,
    ).execute()


# Получение текста из документа

def get_text_from_document(creds, document_id):
    service = build('docs', 'v1', credentials=creds)
    document = service.documents().get(
        documentId=document_id
    ).execute()

    text = ''
    elements = document.get('body').get('content')
    for element in elements:
        if 'paragraph' in element:
            paragraph_elements = element.get('paragraph').get('elements')
            for paragraph_element in paragraph_elements:
                text_run = paragraph_element.get('textRun')
                if text_run:
                    text += text_run.get('content')
    return text


# Получение id из ссылок

def get_txt_document_id(document_url):
    url_part = parse.urlparse(document_url)
    txt_file_id = url_part.path.split('/')[3]
    return txt_file_id


def get_image_document_id(document_url):
    parsed_url = urlparse(document_url)
    query_params = parse_qs(parsed_url.query)
    image_file_id = query_params.get("id", [None])[0]
    return image_file_id


# Скачивание текста и картинок

def get_file_title(file_id, drive):
    file = drive.CreateFile({'id': file_id})
    file.FetchMetadata(fields='title')
    file_title = file['title']
    return file_title
    

def download_image(file_id, file_title, drive, folder):
    filepath = os.path.join(folder, file_title)
    file = drive.CreateFile({'id': file_id})
    file.GetContentFile(filepath)
    return filepath


def download_txt(file_id, file_title, drive, folder):
    extension = '.txt'
    filename = file_title + extension
    filepath = os.path.join(folder, filename)
    file = drive.CreateFile({'id': file_id})
    file.GetContentFile(filepath, mimetype='text/plain')
    return filepath


def main():
    load_dotenv()

    spreadsheet_id = os.getenv('SPREADSHEET_ID')

    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)

    creds = get_credentials()

    folder = 'download'
    os.makedirs(folder, exist_ok=True)


if __name__ == '__main__':
    main()
