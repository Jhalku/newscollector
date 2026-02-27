"""
News Auto Collector - Main Application Entry Point
Bilingual News Monitoring Automation System
"""

import logging
from src.google_sheets_handler import GoogleSheetsHandler
from src.news_scraper import NewsScraper
from src.deduplicator import Deduplicator
from src.google_docs_exporter import GoogleDocsExporter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NewsAutoCollector:
    """Main orchestrator for the news collection workflow"""
    
    def __init__(self):
        self.sheets_handler = GoogleSheetsHandler()
        self.scraper = NewsScraper()
        self.deduplicator = Deduplicator()
        self.exporter = GoogleDocsExporter()
    
    def run(self):
        """Execute the complete news collection workflow"""
        try:
            logger.info("Starting News Auto Collector...")
            
            # Step 1: Fetch keywords from Google Sheets
            logger.info("Fetching keywords from Google Sheets...")
            keywords = self.sheets_handler.fetch_keywords()
            logger.info(f"Fetched {len(keywords)} keywords")
            
            # Step 2: Fetch websites from Google Sheets
            logger.info("Fetching websites from Google Sheets...")
            websites = self.sheets_handler.fetch_websites()
            logger.info(f"Fetched {len(websites)} websites")
            
            # Step 3: Search for articles
            logger.info("Starting article search across websites...")
            articles = self.scraper.search_articles(websites, keywords)
            logger.info(f"Found {len(articles)} articles before deduplication")
            
            # Step 4: Remove duplicates
            logger.info("Removing duplicate articles...")
            unique_articles = self.deduplicator.remove_duplicates(articles)
            logger.info(f"Found {len(unique_articles)} unique articles after deduplication")
            
            # Step 5: Export to Google Docs
            logger.info("Exporting results to Google Docs...")
            doc_url = self.exporter.export(unique_articles)
            logger.info(f"Successfully exported to Google Docs: {doc_url}")
            
            return doc_url
            
        except Exception as e:
            logger.error(f"Error during execution: {str(e)}", exc_info=True)
            raise


def main():
    """Main entry point"""
    collector = NewsAutoCollector()
    doc_url = collector.run()
    print(f"\n✓ Success! Document created at: {doc_url}")


if __name__ == "__main__":
    main()
