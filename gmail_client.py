from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64
import email
import os.path
import pickle
import time
import json
from datetime import datetime

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_credentials():
    """Gets valid user credentials from storage or runs the OAuth2 flow."""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def get_message_body(message):
    """Extract plain text body from email message."""
    if 'parts' in message['payload']:
        for part in message['payload']['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data', '')
                if data:
                    return base64.urlsafe_b64decode(data).decode('utf-8')
    elif message['payload']['mimeType'] == 'text/plain':
        data = message['payload']['body'].get('data', '')
        if data:
            return base64.urlsafe_b64decode(data).decode('utf-8')
    return ''

def setup_watch(service):
    """Set up Gmail watch for new emails."""
    request = {
        'labelIds': ['INBOX'],
        'topicName': 'projects/your-project-id/topics/your-topic-name'
    }
    try:
        response = service.users().watch(userId='me', body=request).execute()
        print(f"Watch setup successful. History ID: {response['historyId']}")
        return response['historyId']
    except Exception as e:
        print(f"Error setting up watch: {e}")
        return None

def get_new_emails(service, history_id):
    """Get new emails since the last history ID."""
    try:
        history = service.users().history().list(
            userId='me',
            startHistoryId=history_id,
            historyTypes=['messageAdded']
        ).execute()
        
        if 'history' not in history:
            return []
        
        new_emails = []
        for history_item in history['history']:
            for message in history_item.get('messagesAdded', []):
                msg_id = message['message']['id']
                msg = service.users().messages().get(
                    userId='me',
                    id=msg_id,
                    format='full'
                ).execute()
                
                headers = msg['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                
                try:
                    date_obj = email.utils.parsedate_to_datetime(date)
                    formatted_date = date_obj.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    formatted_date = date
                
                body = get_message_body(msg)
                
                new_emails.append({
                    "Absender": sender,
                    "Betreff": subject,
                    "Datum": formatted_date,
                    "Nachrichtentext": body
                })
        
        return new_emails
    except Exception as e:
        print(f"Error getting new emails: {e}")
        return []

def watch_emails():
    """Main function to watch for new emails."""
    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)
    
    # Get initial history ID
    profile = service.users().getProfile(userId='me').execute()
    history_id = profile['historyId']
    
    print("Starting to watch for new emails...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            new_emails = get_new_emails(service, history_id)
            if new_emails:
                for email in new_emails:
                    print("\nNew email received:")
                    print(f"From: {email['Absender']}")
                    print(f"Subject: {email['Betreff']}")
                    print(f"Date: {email['Datum']}")
                    print(f"Body: {email['Nachrichtentext'][:200]}...")  # Print first 200 chars
                    print("-" * 50)
                
                # Update history ID
                history_id = service.users().getProfile(userId='me').execute()['historyId']
            
            time.sleep(10)  # Check every 10 seconds
            
    except KeyboardInterrupt:
        print("\nStopping email watch...")

if __name__ == '__main__':
    watch_emails() 