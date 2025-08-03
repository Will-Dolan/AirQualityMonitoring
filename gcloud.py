from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from secret import EMAIL_ADDR
from Email import Email
import os

def gcloud_init() -> (Email, any):
    # If modifying these scopes, delete the file token.json.
    os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
    SCOPES = ['openid', 'https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.compose']

    # obtain gcloud credentials
    creds = None
    
    # Load existing credentials from token.json
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # build gcloud service
    try:
        # create gmail api client
        service = build('gmail', 'v1', credentials=creds)
    except Exception as e:
        print(f'An error has occurred: {e}')

    # template for email
    email = Email(
        to_email=EMAIL_ADDR,
        from_email=EMAIL_ADDR,
        subject='Particulate Matter high'
    )
    
    return email, service