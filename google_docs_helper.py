import os.path
import logging

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/documents", "https://www.googleapis.com/auth/drive"]

def get_credentials():
    """Gets valid user credentials from storage or initiates OAuth2 login."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists("credentials.json"):
                logging.error("Missing credentials.json file. Please download from Google Cloud Console.")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def generate_news_report(keyword, articles):
    """Appends news articles into the existing Google Doc."""
    creds = get_credentials()
    if not creds:
        return None

    try:
        # Build the Docs API service
        docs_service = build("docs", "v1", credentials=creds)
        document_id = "1VNYgXThasDttWyBs5CwiG-gt1rpVjjpJQJEGFZMfxao"
        logging.info(f"Appending to document with ID: {document_id}")

        # Format the articles into text
        requests = []
        text_content = f"News Report for '{keyword}'\n\n"
        
        for idx, article in enumerate(articles, 1):
            date_str = article.get('date', 'Unknown Date')
            text_content += f"{idx}. {article.get('title', 'Unknown Title')}\n"
            text_content += f"Date: {date_str}\n"
            text_content += f"Link: {article.get('link', 'No Link')}\n\n"
            
        # Insert text at the end of the document
        requests.append({
            "insertText": {
                "endOfSegmentLocation": {
                    "segmentId": ""
                },
                "text": text_content
            }
        })
        
        docs_service.documents().batchUpdate(
            documentId=document_id, body={"requests": requests}
        ).execute()
        
        # Return the viewable link
        return f"https://docs.google.com/document/d/{document_id}/edit"

    except HttpError as err:
        logging.error(f"An error occurred with Google Docs: {err}")
        return None
