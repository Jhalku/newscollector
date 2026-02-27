# Bilingual News Monitoring Automation - Copilot Instructions

## Project Overview

This is a Python project for automated bilingual (Hindi/English) news monitoring that:
- Searches multiple news websites for keywords
- Removes duplicate articles intelligently
- Exports results to Google Docs with proper formatting

## Key Technologies

- **Language**: Python 3.9+
- **APIs**: Google Sheets, Google Docs, Google Drive
- **Scraping**: BeautifulSoup, Requests, Selenium (optional)
- **Deduplication**: String similarity, URL hashing

## Important Files

- `src/main.py` - Application entry point and orchestrator
- `src/google_sheets_handler.py` - Fetch keywords and websites from Google Sheets
- `src/news_scraper.py` - Search websites and extract articles
- `src/deduplicator.py` - Remove duplicate articles
- `src/google_docs_exporter.py` - Export to Google Docs
- `requirements.txt` - Python dependencies
- `.env` - Configuration (create from .env.example)

## Setup Checklist

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Download credentials.json from Google Cloud Console
- [ ] Copy `.env.example` to `.env` and fill in values
- [ ] Verify Google Sheets are shared with OAuth app
- [ ] Run `python -m src.main` to start

## Running the Project

**Option 1: VS Code**
- Command Palette → "Tasks: Run Task" → "Run News Collector"

**Option 2: Terminal**
- `python -m src.main`

## Key Functions

### GoogleSheetsHandler
- `fetch_keywords()` - Returns list of {keyword, language}
- `fetch_websites()` - Returns list of {name, url, language}

### NewsScraper
- `search_articles(websites, keywords)` - Returns articles with {title, url, summary, language, website, keyword}

### Deduplicator
- `remove_duplicates(articles)` - Returns unique articles

### GoogleDocsExporter
- `export(articles)` - Creates Google Doc, returns doc URL

## Configuration

Create `.env` with:
```
KEYWORDS_SHEET_ID=<your_sheet_id>
WEBSITES_SHEET_ID=<your_sheet_id>
OUTPUT_FOLDER_ID=<optional_folder_id>
```

## Important Notes

- All Google API credentials are in `credentials.json` (not in git)
- Add `credentials.json` and `token.json` to `.gitignore`
- The project uses a 1-second delay between requests to be respectful to servers
- Deduplication threshold is set to 0.85 (85% similarity) for title matching
