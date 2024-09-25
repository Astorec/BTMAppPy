import os.path
import json
import google.auth

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.cloud import secretmanager

from google_auth_oauthlib.flow import InstalledAppFlow

from google.oauth2 import service_account

class GAuth:
    def __init__(self, creds_file, scopes):
        self.creds_file = creds_file
        self.scopes = scopes
        self.credentials = None
        self.service = None
        self.load_creds()
        
    def load_creds(self):
        credentials_path =  "./src/credentials.json"
        try:
            self.creds = Credentials.from_authorized_user_file(credentials_path, self.scopes)
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())  
        except (FileNotFoundError, ValueError):
            print("Credentials file not found or invalid format - " + credentials_path)
            pass  # File not found or invalid format, proceed with new credentials

        client = secretmanager.SecretManagerServiceClient()
       
        name = f"projects/{os.getenv('BTM_CLIENT_SECRET')}/secrets/{os.getenv('BTM_SECRET_ID')}/versions/latest"
        result = client.access_secret_version(name=name)
        response = result.payload.data.decode('UTF-8')
        client_config = json.loads(response)    
        flow = InstalledAppFlow.from_client_config(client_config, self.scopes)
        self.creds = flow.run_local_server(port=0)

        with open(credentials_path, 'w+') as token:
            token.write(self.creds.to_json())

        self.service = build('sheets', 'v4', credentials=self.creds)

    def get_service(self):
        return self.service

