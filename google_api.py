import os
from dotenv import load_dotenv
from datetime import datetime
# from urllib import parse
# from pprint import pprint

from googleapiclient.discovery import build

from auth import get_credentials
# from googleapiclient.errors import HttpError


load_dotenv()
creds = get_credentials()
spreadsheet_id = os.environ['SPREADSHEET_ID']


# Получение всех постов в формате list[dict], 
# явно указывается диапазон таблицы (range)

def get_all_posts(creds, spreadsheet_id):
    service = build('sheets', 'v4', credentials=creds)
    request = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, 
        range='A1:K4', 
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
# (нужно передать row_number (номер ряда для смены статуса))

def change_status_published_post(creds, spreadsheet_id, row_number):    
    service = build('sheets', 'v4', credentials=creds)
    body = {
        'values': [['опубликовано']]
    }     
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, 
        range=f"Лист1!K{row_number}", 
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

def get_posts_to_delete(all_posts):
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

def get_text_from_document(creds):
    document_id = '1C1dM1H8tzaaxS1a2iuo7Nsv-hzgJyO1gAxGTZYEP3_U'

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


# print(get_text_from_document(creds))


all_posts = get_all_posts(creds, spreadsheet_id)
posts_to_publish = get_posts_to_publish(all_posts)
