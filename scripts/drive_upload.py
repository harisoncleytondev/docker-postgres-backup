import os
from datetime import datetime
from dotenv import load_dotenv

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/drive']

def get_credentials():
    creds = None
    
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            client_config = {
                "installed": {
                    "client_id": os.getenv('GOOGLE_CLIENT_ID'),
                    "project_id": os.getenv('GOOGLE_PROJECT_ID'),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_secret": os.getenv('GOOGLE_CLIENT_SECRET'),
                    "redirect_uris": ["http://localhost"]
                }
            }
            
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(port=0)
            
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            
    return creds

def create_folder(service, folder_name, parent_folder_id=None):
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    
    if parent_folder_id:
        file_metadata['parents'] = [parent_folder_id]

    folder = service.files().create(
        body=file_metadata,
        fields='id'
    ).execute()
    
    return folder.get('id')

def upload(file_path):
    folder_id = os.getenv('GOOGLE_FOLDER_ID')

    now = datetime.now()
    print(f"[{now.strftime('%d/%m/%Y %H:%M:%S')}] Iniciando upload diário.")
    
    creds = get_credentials()
    service = build('drive', 'v3', credentials=creds)
    
    full_file_name = os.path.basename(file_path)
    base_file_name = os.path.splitext(full_file_name)[0]
    
    formatted_date = now.strftime('%d-%m-%Y')
    new_folder_name = f"backup-{base_file_name}-{formatted_date}"
    
    print(f"Criando pasta no Drive: '{new_folder_name}'...")
    
    new_folder_id = create_folder(service, new_folder_name, folder_id)
    
    file_metadata = {
        'name': full_file_name,
        'parents': [new_folder_id]
    }

    print(f"Fazendo upload do arquivo '{full_file_name}'...")

    media = MediaFileUpload(file_path, resumable=True)
    uploaded_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    print(f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] Upload concluído com sucesso! ID do arquivo: {uploaded_file.get('id')}")