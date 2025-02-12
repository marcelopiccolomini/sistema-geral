from __future__ import print_function
from googleapiclient.discovery import build # type: ignore
from googleapiclient.errors import HttpError # type: ignore
from google.oauth2 import service_account # type: ignore

class Connect():

    def __init__(self) -> None:
        # If modifying these scopes, delete the file token.json.
        global SCOPES 
        global creds 
        creds = None
        

    def connect():
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        SERVICE_ACCOUNT_FILE = r"/root/sistema-geral/vizzela-server-3f9fe2c572e0.json"

    # Create credentials using the service account file
        creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        try:
            # Create drive API client
            service = build('sheets', 'v4', credentials=creds)         
        except HttpError as error:
            print(f"An error occurred: {error}")
            

        return service