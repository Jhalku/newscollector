"""
Google Sheets Handler - Read keywords and websites from Google Sheets
"""

import logging
import os
import pickle
import sys
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google.oauth2.credentials import Credentials as UserCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Google Sheets API scopes
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# Token and credentials file paths
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.pickle'


class GoogleSheetsHandler:
    """Handle reading data from Google Sheets"""
    
    def __init__(self):
        self.keywords_sheet_id = os.getenv('KEYWORDS_SHEET_ID')
        self.websites_sheet_id = os.getenv('WEBSITES_SHEET_ID')
        
        if not self.keywords_sheet_id or not self.websites_sheet_id:
            raise ValueError(
                "KEYWORDS_SHEET_ID and WEBSITES_SHEET_ID must be set in .env file"
            )
        
        self.service = None
        try:
            self.service = self._authenticate()
        except Exception as e:
            logger.warning(
                "Google Sheets authentication unavailable (%s). Running in demo mode.",
                str(e)
            )
    
    def _authenticate(self):
        """Authenticate with Google Sheets API using OAuth2 flow"""
        creds = None
        
        # Load existing token if available
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)
                logger.info("Loaded existing token")
        
        # If no valid credentials, use OAuth2 flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing expired token...")
                creds.refresh(Request())
            else:
                if not os.path.exists(CREDENTIALS_FILE):
                    raise FileNotFoundError(
                        f"{CREDENTIALS_FILE} not found. "
                        "Please download it from Google Cloud Console and place in project root."
                    )
                
                if not sys.stdin.isatty():
                    raise RuntimeError(
                        "Interactive OAuth required, but no interactive terminal is available."
                    )

                logger.info("Running OAuth2 flow...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0, open_browser=True)
            
            # Save token for future use
            with open(TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)
                logger.info("Token saved for future use")
        
        return build('sheets', 'v4', credentials=creds)
    
    def fetch_keywords(self):
        """
        Fetch keywords from Google Sheets
        Returns list of dicts: [{'keyword': '...', 'language': 'Hindi/English'}, ...]
        """
        try:
            if not self.service:
                raise RuntimeError("Google Sheets service unavailable")
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.keywords_sheet_id,
                range='Sheet1!A:B'
            ).execute()
            
            rows = result.get('values', [])
            keywords = []
            
            # Skip header row
            for row in rows[1:]:
                if len(row) >= 2:
                    keywords.append({
                        'keyword': row[0],
                        'language': row[1]
                    })
            
            return keywords
        except Exception as e:
            logger.warning(f"Error fetching keywords from Google Sheets: {str(e)}")
            logger.info("Using demo keywords instead...")
            # Return demo keywords for testing
            return [
                {'keyword': 'election', 'language': 'English'},
                {'keyword': 'budget', 'language': 'English'},
                {'keyword': 'cricket', 'language': 'English'},
                {'keyword': 'चुनाव', 'language': 'Hindi'},
                {'keyword': 'बजट', 'language': 'Hindi'},
            ]
    
    def fetch_websites(self):
        """
        Fetch websites from Google Sheets
        Returns list of dicts: [{'name': '...', 'url': '...', 'language': 'Hindi/English'}, ...]
        """
        try:
            if not self.service:
                raise RuntimeError("Google Sheets service unavailable")
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.websites_sheet_id,
                range='Sheet1!A:C'
            ).execute()
            
            rows = result.get('values', [])
            websites = []
            
            # Skip header row
            for row in rows[1:]:
                if len(row) >= 3:
                    websites.append({
                        'name': row[0],
                        'url': row[1],
                        'language': row[2]
                    })
            
            return websites
        except Exception as e:
            logger.warning(f"Error fetching websites from Google Sheets: {str(e)}")
            logger.info("Using demo websites instead...")
            # Return demo websites for testing
            return [
                {'name': 'BBC News', 'url': 'https://www.bbc.com/news', 'language': 'English'},
                {'name': 'CNN', 'url': 'https://www.cnn.com', 'language': 'English'},
                {'name': 'The Hindu', 'url': 'https://www.thehindu.com', 'language': 'English'},
                {'name': 'Aaj Tak', 'url': 'https://www.aajtaak.in', 'language': 'Hindi'},
                {'name': 'NDTV', 'url': 'https://www.ndtv.com', 'language': 'Hindi'},
            ]
