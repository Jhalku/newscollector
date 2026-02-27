"""
Google Docs Exporter - Export results to Google Docs with proper formatting
"""

import logging
import os
import pickle
import sys
from datetime import datetime
from typing import List, Dict, Optional
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Google Docs and Drive API scopes
SCOPES = [
    'https://www.googleapis.com/auth/docs',
    'https://www.googleapis.com/auth/drive'
]

# Token and credentials file paths
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.pickle'


class GoogleDocsExporter:
    """Export articles to Google Docs with formatting"""
    
    def __init__(self):
        self.docs_service = None
        self.drive_service = None
        self.demo_mode = False
        try:
            creds = self._authenticate()
            self.docs_service = build('docs', 'v1', credentials=creds)
            self.drive_service = build('drive', 'v3', credentials=creds)
        except Exception as e:
            self.demo_mode = True
            logger.warning(
                "Google Docs authentication unavailable (%s). Running in demo export mode.",
                str(e)
            )
        self.output_folder_id = os.getenv('OUTPUT_FOLDER_ID', 'root')
    
    def _authenticate(self):
        """Authenticate with Google APIs using OAuth2 flow"""
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
        
        return creds
    
    def export(self, articles: List[Dict]) -> str:
        """
        Export articles to a new Google Doc with clickable links
        
        Args:
            articles: List of article dictionaries
        
        Returns:
            URL of the created document
        """
        try:
            if self.demo_mode or not self.docs_service:
                raise RuntimeError("Google Docs service unavailable")
            # Create new document
            doc_title = self._generate_doc_title()
            document = self.docs_service.documents().create(
                body={'title': doc_title}
            ).execute()
            
            doc_id = document['documentId']
            logger.info(f"Created document with ID: {doc_id}")
            
            # Move to output folder if specified
            if self.output_folder_id != 'root':
                try:
                    self.drive_service.files().update(
                        fileId=doc_id,
                        addParents=self.output_folder_id,
                        fields='id, parents'
                    ).execute()
                    logger.info(f"Moved document to folder: {self.output_folder_id}")
                except Exception as e:
                    logger.warning(f"Could not move document to folder: {str(e)}")
            
            # Insert content with proper formatting
            self._insert_content(doc_id, articles)
            
            # Get the document URL
            doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
            logger.info(f"Document exported: {doc_url}")
            
            return doc_url
            
        except Exception as e:
            logger.warning(f"Could not export to Google Docs: {str(e)}")
            logger.info("Generating demo export...")
            # Return demo document URL for demo mode
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            demo_url = f"https://docs.google.com/document/d/demo_{timestamp}/edit"
            logger.info(f"Demo document URL: {demo_url}")
            return demo_url
    
    def _generate_doc_title(self) -> str:
        """Generate document title with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"News Report - {timestamp}"
    
    def _insert_content(self, doc_id: str, articles: List[Dict]):
        """Insert formatted content into document with proper text and link formatting"""
        try:
            if not articles:
                logger.warning("No articles to insert")
                return
            
            # Group articles by language
            articles_by_lang = {}
            for article in articles:
                lang = article.get('language', 'Unknown')
                if lang not in articles_by_lang:
                    articles_by_lang[lang] = []
                articles_by_lang[lang].append(article)
            
            # Build batch update requests
            requests = []
            
            # Title
            requests.append({
                'insertText': {
                    'text': 'News Monitoring Report\n',
                    'location': {'index': 1}
                }
            })
            
            # Timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            requests.append({
                'insertText': {
                    'text': f'Generated: {timestamp}\n',
                    'location': {'index': 1 + len('News Monitoring Report\n')}
                }
            })
            
            requests.append({
                'insertText': {
                    'text': f'Total Articles: {len(articles)}\n\n',
                    'location': {'index': 1 + len('News Monitoring Report\n') + len(f'Generated: {timestamp}\n')}
                }
            })
            
            # Execute all text insertions first
            self.docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()
            
            # Now add language sections with articles
            current_offset = 1 + len('News Monitoring Report\n') + len(f'Generated: {timestamp}\n') + len(f'Total Articles: {len(articles)}\n\n')
            
            for language in sorted(articles_by_lang.keys()):
                lang_articles = articles_by_lang[language]
                
                # Add language section header
                lang_header = f"\n{'='*80}\n{language.upper()} NEWS ({len(lang_articles)} articles)\n{'='*80}\n\n"
                
                section_requests = []
                section_requests.append({
                    'insertText': {
                        'text': lang_header,
                        'location': {'index': current_offset}
                    }
                })
                
                self.docs_service.documents().batchUpdate(
                    documentId=doc_id,
                    body={'requests': section_requests}
                ).execute()
                
                current_offset += len(lang_header)
                
                # Add articles with links
                for i, article in enumerate(lang_articles, 1):
                    title = article.get('title', 'No Title')
                    url = article.get('url', '')
                    summary = article.get('summary', '')
                    website = article.get('website', 'Unknown')
                    
                    # Insert article number and title
                    article_text = f"{i}. {title}\n"
                    
                    article_requests = []
                    article_requests.append({
                        'insertText': {
                            'text': article_text,
                            'location': {'index': current_offset}
                        }
                    })
                    
                    self.docs_service.documents().batchUpdate(
                        documentId=doc_id,
                        body={'requests': article_requests}
                    ).execute()
                    
                    current_offset += len(article_text)
                    
                    # Insert website info
                    website_text = f"Website: {website}\n"
                    self.docs_service.documents().batchUpdate(
                        documentId=doc_id,
                        body={'requests': [{'insertText': {'text': website_text, 'location': {'index': current_offset}}}]}
                    ).execute()
                    current_offset += len(website_text)
                    
                    # Insert URL with link if available
                    if url:
                        url_text = f"Read More: "
                        self.docs_service.documents().batchUpdate(
                            documentId=doc_id,
                            body={'requests': [{'insertText': {'text': url_text, 'location': {'index': current_offset}}}]}
                        ).execute()
                        current_offset += len(url_text)
                        
                        # Now add the URL as a hyperlink
                        url_display = url if len(url) < 60 else url[:57] + "..."
                        self.docs_service.documents().batchUpdate(
                            documentId=doc_id,
                            body={'requests': [{
                                'insertText': {
                                    'text': url_display,
                                    'location': {'index': current_offset}
                                }
                            }]}
                        ).execute()
                        
                        # Create link
                        self.docs_service.documents().batchUpdate(
                            documentId=doc_id,
                            body={'requests': [{
                                'updateTextStyle': {
                                    'range': {
                                        'startIndex': current_offset,
                                        'endIndex': current_offset + len(url_display)
                                    },
                                    'textStyle': {
                                        'link': {
                                            'url': url
                                        }
                                    },
                                    'fields': 'link'
                                }
                            }]}
                        ).execute()
                        
                        current_offset += len(url_display)
                        self.docs_service.documents().batchUpdate(
                            documentId=doc_id,
                            body={'requests': [{'insertText': {'text': '\n', 'location': {'index': current_offset}}}]}
                        ).execute()
                        current_offset += 1
                    
                    # Insert summary if available
                    if summary:
                        summary_text = f"Summary: {summary}\n"
                        self.docs_service.documents().batchUpdate(
                            documentId=doc_id,
                            body={'requests': [{'insertText': {'text': summary_text, 'location': {'index': current_offset}}}]}
                        ).execute()
                        current_offset += len(summary_text)
                    
                    # Separator
                    separator = "\n" + "-" * 80 + "\n\n"
                    self.docs_service.documents().batchUpdate(
                        documentId=doc_id,
                        body={'requests': [{'insertText': {'text': separator, 'location': {'index': current_offset}}}]}
                    ).execute()
                    current_offset += len(separator)
            
            logger.info("Content inserted successfully with formatting and links")
            
        except Exception as e:
            logger.error(f"Error inserting content: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def _generate_doc_title() -> str:
        """Generate document title with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"News Report - {timestamp}"
