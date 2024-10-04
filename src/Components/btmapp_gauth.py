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
        if os.path.exists("./src/token.json"):
            self.credentials = Credentials.from_authorized_user_file("./src/token.json", self.scopes)
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("./src/credentials.json", self.scopes)
                self.credentials = flow.run_local_server(port=0)
            with open("./src/token.json", 'w') as credentials_file:
                credentials_file.write(self.credentials.to_json())

        self.service = build('sheets', 'v4', credentials=self.credentials)

    def get_service(self):
        return self.service

