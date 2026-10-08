# Gmail API Client

This Python module allows you to watch for new emails in your Gmail account in real-time using the Gmail API.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up OAuth2 credentials:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the Gmail API for your project
   - Create OAuth 2.0 credentials (Desktop application)
   - Download the credentials and save them as `credentials.json` in the same directory as this script

## Usage

The script will continuously monitor your Gmail inbox for new emails. When a new email arrives, it will display:
- Absender (From)
- Betreff (Subject)
- Datum (Date)
- Nachrichtentext (Message body)

To start watching for new emails:
```bash
python gmail_client.py
```

The script will:
1. Open a browser window asking you to authorize the application (first run only)
2. Save the authorization token in `token.pickle` for future use
3. Start monitoring your inbox for new emails
4. Display new emails as they arrive
5. Press Ctrl+C to stop the monitoring

## Notes

- The script uses the Gmail API's read-only scope
- The token is stored locally in `token.pickle`
- The script handles multipart emails and extracts plain text content
- Dates are formatted as 'YYYY-MM-DD HH:MM:SS'
- The script checks for new emails every 10 seconds
- Only emails in the INBOX are monitored 