import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class BTMAppSheets:
    SCOPES = ["https://www.googleapis.com/auth/drive"]

    SHEET_ID = ""
    creds = None

    def __init__(self, sheet_id):

        # Set the sheet id which is located in the google sheet url
        self.SHEET_ID = sheet_id

        # Check to see if we already have a token.json file
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json') # Authorize the user
            
        # if there is no valid credentials, then get new credentials
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", self.SCOPES
                )
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(self.creds.to_json())

    def get_sheet_names(self):
        try:
            service = build("sheets", "v4", credentials=self.creds)
        
            sheet = service.spreadsheets()
            result = sheet.get(spreadsheetId=self.SHEET_ID).execute()
            sheets = result.get("sheets", [])
        
            sheet_names = []
            for sheet in sheets:
                sheet_names.append(sheet['properties']['title'])
            return sheet_names
        except HttpError as e:
            print(f"An error occurred: {e}") 

    def get_headers(self, sheetname):
        try:
            service = build("sheets", "v4", credentials=self.creds)
        
            sheet = service.spreadsheets()
            result = sheet.values().get(spreadsheetId=self.SHEET_ID, range="{}!A1:T".format(sheetname)).execute()
            values = result.get("values", [])

            if not values:
                print("No data found.")
                return
            else:
                return values[0]
        except HttpError as e:
            print(f"An error occurred: {e}")

    def get_sheet(self, sheetname):  
        try:
            service = build("sheets", "v4", credentials=self.creds)
        
            sheet = service.spreadsheets()
            result = sheet.values().get(spreadsheetId=self.SHEET_ID, range="{}!A1:T".format(sheetname)).execute()
            values = result.get("values", [])
            
        
            if not values:
                print("No data found.")
                return
            else:
                # expected header names
                expected_headers = ['Rank', 'Blader', 'Wins' 'Losses', 
                                    '1st', '2nd', '3rd', 'Points', 'Win%',
                                    'Rating', 'Region', 'Column 1', 'Column 2',
                                    'Column 3', 'Column 4', 'Column 5', 'Column 6',
                                    'Column 7', 'Column 8', 'Column 9']
                
                # get the header row
                header_row = None
                for row in values:
                    for row_value in row:
                        if row_value in expected_headers:
                            header_row = row
                            break
                if header_row is None:
                    raise ValueError("Expected headers not found in the sheet")
                # return list of values minus the header row

                return values
        except HttpError as e:
            print(f"An error occurred: {e}")
            
    def create_sheet(self, sheetname):
        try:
            service = build("sheets", "v4", credentials=self.creds)
            body = {
                "requests": [{
                    "addSheet": {
                        "properties": {
                            "title": sheetname
                        }
                    }
                }]
            }

            result = service.spreadsheets().batchUpdate(spreadsheetId=self.SHEET_ID, body=body).execute()
            
            
        
            # Update header row
            headers = ['Rank', 'Blader', 'Wins' 'Losses', 
                                    '1st', '2nd', '3rd', 'Points', 'Win%',
                                    'Rating', 'Region', 'Column 1', 'Column 2',
                                    'Column 3', 'Column 4', 'Column 5', 'Column 6',
                                    'Column 7', 'Column 8', 'Column 9']
            
            values = [headers]
            body = {
                "values": values
            }

            result = service.spreadsheets().values().update(spreadsheetId=self.SHEET_ID, range="{}!A1:T".format(sheetname), valueInputOption="RAW", body=body).execute()

        
        except HttpError as e:
            print(f"An error occurred: {e}")