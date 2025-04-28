import os
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from urllib import parse

from googleapiclient.discovery import build

from post_text_validation import text_to_post_format


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


def change_status_published_post(creds, spreadsheet_id, status, row_number, platform): 
    dct = {
        'tg': 'K',
        'vk': 'L',
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


def clear_cell_deleted_post(creds, spreadsheet_id, row_number, platform):  
    dct = {
        'tg_post_id': 'N',
        'vk_post_id': 'O',
        'ok_post_id': 'P'
    }   
    service = build('sheets', 'v4', credentials=creds)
    body = {
        'values': [['']]
    }     
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, 
        range=f"Лист1!{dct.get(platform)}{row_number}", 
        valueInputOption='USER_ENTERED',
        body=body,
    ).execute()


def set_post_id(creds, spreadsheet_id, post_id, row_number, platform):
    dct = {
        'tg': 'N',
        'vk': 'O',
        'ok': 'P'
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


def get_posts_to_publish(all_posts):
    posts_to_publish = []
    for i, row in enumerate(all_posts, 1):
        if (
            row.get('Telegram') == 'TRUE' 
            or row.get('VK') == 'TRUE' 
            or row.get('ОК') == 'TRUE'
        ):
            pub_date = row.get("Дата")
            pub_time = row.get("Время")
            if not pub_date or not pub_time:
                continue
            publication_time = datetime.strptime(
                f'{pub_date} {pub_time}', '%d.%m.%y %H:%M'
            )
            if publication_time <= datetime.now():
                row['id'] = i
                posts_to_publish.append(row)
    return posts_to_publish


def update_status(creds, spreadsheet_id, all_posts):
    for i, row in enumerate(all_posts, 2):
        tg = row.get('Telegram') == 'TRUE'
        vk = row.get('VK') == 'TRUE'
        ok = row.get('ОК') == 'TRUE'
        if tg or vk or ok:
            pub_date = row.get("Дата")
            pub_time = row.get("Время")
            if not pub_date or not pub_time:
                continue
            publication_time = datetime.strptime(
                f'{pub_date} {pub_time}', '%d.%m.%y %H:%M'
            )
            if publication_time > datetime.now():
                if tg:
                    change_status_published_post(creds, spreadsheet_id, 'ожидание', i, 'tg')
                if vk:
                    change_status_published_post(creds, spreadsheet_id, 'ожидание', i, 'vk')
                if ok:
                    change_status_published_post(creds, spreadsheet_id, 'ожидание', i, 'ok')


def get_posts_to_delete(all_posts):
    posts_to_delete = []

    for i, row in enumerate(all_posts, 1):
        if row.get('Удалить') == 'FALSE':
            continue
        del_date = row.get("Удалить в")
        if not del_date:
            continue

        deletion_time = datetime.strptime(
            f'{row["Удалить в"]}', '%d.%m.%y %H:%M'
        )
    
        if deletion_time <= datetime.now():
            row['id'] = i
            posts_to_delete.append(row)
    return posts_to_delete


def unset_flag(creds, spreadsheet_id, row_number, platform):
    dct = {
        'vk': 'G',
        'tg': 'F',
        'ok': 'H',
        'delete': 'I'
    }
    service = build('sheets', 'v4', credentials=creds)
    body = {
        'values': [['FALSE']]
    }
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, 
        range=f"Лист1!{dct.get(platform)}{row_number}", 
        valueInputOption='USER_ENTERED',
        body=body,
    ).execute()


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
    text = text_to_post_format(text)
    return text


def get_txt_document_id(document_url):
    url_part = parse.urlparse(document_url)
    txt_file_id = url_part.path.split('/')[3]
    return txt_file_id


def get_image_document_id(document_url):
    parsed_url = urlparse(document_url)
    query_params = parse_qs(parsed_url.query)
    image_file_id = query_params.get("id", [None])[0]
    return image_file_id


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
