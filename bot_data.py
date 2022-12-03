from __future__ import print_function
import pickle
import os
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import googleapiclient.http
from datetime import datetime
from pytz import timezone

# If modifying these scopes, delete the file token.pickle.
SHEET_SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive']

# The ID and range of a the spreadsheet.

FINANCE_SPREADSHEET_ID = os.getenv('FINANCE_SHEET')
CLAIMS_RANGE_NAME = 'Spending!A2:H2'

TIMESTAMP = str(datetime.now().astimezone(timezone('Asia/Singapore')))[:16]

def sheets_authenticator():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token2.pickle'):
        with open('token2.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SHEET_SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token2.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def drive_authenticator():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', DRIVE_SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds

def sheet_ul(claimsdata):
    print("running...")
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    
    service = build('sheets', 'v4', credentials=sheets_authenticator())

    sheet = service.spreadsheets()
    
    user = claimsdata['user'][0]
    
    claim_list = claimsdata['user']
    claim_list.pop(0)
    
    print("for the excel sheet", claim_list)

    for c in claim_list:
        c.append(user)
        x = c[3]
        c.pop(3)
        c.extend(['Not Uploaded','Not Done',x])
        c.insert(0,TIMESTAMP[5:10].replace('-','/'))

    print(claim_list)
    values = claim_list
    body = {
        'values': values
    }

    result = sheet.values().append(spreadsheetId=FINANCE_SPREADSHEET_ID,
                                range=CLAIMS_RANGE_NAME,
                                valueInputOption='USER_ENTERED',
                                body=body).execute()
    
    print(result)

def receipt_ul(folder_id):

    service = build('drive', 'v3', credentials=drive_authenticator())
    
    receipts_dir = os.listdir('receipts')
    receipt_pics = []
    
    for item in receipts_dir:
        receipt_pics.append(f'{item}')
        print(receipt_pics)

    for x in receipt_pics:
        if x != '.keep':
            file_metadata = {
            'name': x,
            'parents': [folder_id]
            }
            media = googleapiclient.http.MediaFileUpload(f'receipts/{x}',
                                    mimetype='image/jpeg')
            results = service.files().create(body=file_metadata,
                                                media_body=media,
                                                fields='id').execute()
        
    print('File ID: %s' % results.get('id'))

def receipt_del():
    receipts_dir = os.listdir('receipts')
    receipt_pics = []
    
    for item in receipts_dir:
        receipt_pics.append(f'{item}')
        print(receipt_pics)

    for y in receipt_pics:
        path = os.path.join('receipts',y)
        os.remove(path)

def claims_ul():
    service = build('drive', 'v3', credentials=drive_authenticator()) 
    months_list = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November','December']
    claims_month = f'{TIMESTAMP[5:7]}/{TIMESTAMP[:4]} {months_list[int(TIMESTAMP[5:7])-1]} BOT'
    claims_date = f'{TIMESTAMP[5:7]}/{TIMESTAMP[8:10]} BOT'
    claims_bot_folder = '1P-nxakvDSuYzmMC3agf_nuhpN913RuFD'
    month_folder_id = ''
    date_folder_id = ''

    folder_res = service.files().list(q = f"mimeType = 'application/vnd.google-apps.folder' and name = '{claims_month}' and trashed = false" ,spaces='drive', pageSize=10, fields="nextPageToken, files(id, name)").execute()
    date_res = service.files().list(q = f"mimeType = 'application/vnd.google-apps.folder' and name = '{claims_date}' and trashed = false" ,spaces='drive', pageSize=10, fields="nextPageToken, files(id, name)").execute()
    
    # check for folder & date existing
    
    print(folder_res.get('files', []))
    print(date_res.get('files', []))

    if len(folder_res.get('files', [])) >= 1 or len(date_res.get('files', [])) >= 1:
        for x in folder_res.get('files', []):
            month_folder_id = x.get('id')
            print(f"\n\nfolders exist, uploading file...\nmonth folder name/id: {x.get('name')}/{month_folder_id}")
        for y in date_res.get('files',[]):
            date_folder_id = y.get('id')
            print(f"\ndate folder name/id: {y.get('name')}/{date_folder_id}")

    if len(folder_res.get('files', [])) == 0: 
        # create folder by month if it doesnt exist
        print("folders dont exist, creating...")
        month_metadata = {
            'name': claims_month,
            'mimeType':'application/vnd.google-apps.folder',
            'parents' : [claims_bot_folder]
        }
        
        month_folder = service.files().create(body=month_metadata,fields='id').execute()
        month_folder_id = month_folder.get('id')
    
    if len(date_res.get('files', [])) == 0:
        # create folder by date if it doesnt exist
        print("folders dont exist, creating...")
        date_metadata = {
        'name': claims_date,
        'mimeType':'application/vnd.google-apps.folder',
        'parents': [month_folder_id]
        }

        date_folder = service.files().create(body=date_metadata,fields='id').execute()
        date_folder_id = date_folder.get('id')

    receipt_ul(date_folder_id)

