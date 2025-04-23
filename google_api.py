import os
from dotenv import load_dotenv

from googleapiclient.discovery import build

from auth import get_credentials
# from googleapiclient.errors import HttpError


load_dotenv()
creds = get_credentials()
spreadsheet_id = os.environ['SPREADSHEET_ID']


def get_all_posts(creds, spreadsheet_id):
    service = build('sheets', 'v4', credentials=creds)
    request = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, 
        range='A2:K3', 
        valueRenderOption='FORMATTED_VALUE',
    )
    all_posts = request.execute()['values']
    return all_posts


# print(get_all_posts(creds, spreadsheet_id))


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


# print(change_status_published_post(creds, spreadsheet_id, row_number=2))
