# Bilingual News Monitoring Automation

A Python-based automation system for searching multiple news websites in Hindi and English, extracting articles, removing duplicates, and exporting results to Google Docs.

## ✨ Features

✅ **Multi-Website Search** - Search across multiple news sources simultaneously  
✅ **Bilingual Support** - Support for both Hindi and English keywords and websites  
✅ **Smart Deduplication** - Remove duplicate articles by URL, title, and similarity  
✅ **Google Sheets Integration** - Manage keywords and websites from Google Sheets  
✅ **Google Docs Export** - Create formatted documents with clickable article links  
✅ **Web UI** - Simple, intuitive interface for manual execution  
✅ **Real-time Progress** - Monitor execution status and progress  
✅ **Robust Error Handling** - Automatic retries and graceful error recovery  

## 📁 Project Structure

```
newsautocollector/
├── app.py                          # Flask web application
├── quickstart.py                   # Quick setup script
├── credentials.json                # OAuth 2.0 credentials (create after setup)
├── token.pickle                    # Auth token (auto-created)
├── .env                            # Environment variables (create from .env.example)
├── .env.example                    # Environment template
├── requirements.txt                # Python dependencies
├── pyproject.toml                  # Project metadata
├── README.md                       # This file
├── SETUP_GUIDE.md                 # Detailed setup instructions
│
├── src/
│   ├── __init__.py
│   ├── main.py                     # Main orchestrator
│   ├── google_sheets_handler.py    # Google Sheets API
│   ├── google_docs_exporter.py     # Google Docs API
│   ├── news_scraper.py             # Web scraping
│   └── deduplicator.py             # Duplicate removal
│
├── templates/
│   └── index.html                  # Web UI
│
└── static/
    ├── style.css                   # Styling
    └── script.js                   # UI logic
```

## 🚀 Quick Start

### 1. Run Quick Setup

```bash
python quickstart.py
```

This will:
- Check Python version (3.9+)
- Install dependencies
- Create .env file
- Provide next steps

### 2. Setup Google API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable APIs: Google Sheets, Google Docs, Google Drive
4. Create OAuth 2.0 Desktop credentials
5. Download and save as `credentials.json` in project root

### 3. Configure Environment

Edit `.env` with your Google Sheets IDs:
```
KEYWORDS_SHEET_ID=1gLvmp0E9f9xEwF6YHgNM0eZJklN4XVB76pKUBqXIgr0
WEBSITES_SHEET_ID=1TCHI4zm7gyavORlgbH0j94cs55CCBwSVBjswtoi93nA
OUTPUT_FOLDER_ID=root
```

### 4. Start Web Application

```bash
python app.py
```

Open browser: http://localhost:5000

## 📋 Data Sources

### Keywords Google Sheet
- **URL**: https://docs.google.com/spreadsheets/d/1gLvmp0E9f9xEwF6YHgNM0eZJklN4XVB76pKUBqXIgr0
- **Format**: Column A (Keyword), Column B (Language: Hindi/English)
- **Example**: "election", "budget", "क्रिकेट"

### Websites Google Sheet
- **URL**: https://docs.google.com/spreadsheets/d/1TCHI4zm7gyavORlgbH0j94cs55CCBwSVBjswtoi93nA
- **Format**: Column A (Name), Column B (URL), Column C (Language: Hindi/English)
- **Example**: "BBC News", "https://www.bbc.com/news", "English"

## 💻 Usage

### Web Interface (Recommended)

1. Start the application: `python app.py`
2. Open http://localhost:5000
3. Click "Run Collection"
4. Monitor progress in real-time
5. Click document link in results

### Command Line

```bash
python -m src.main
```

## 🔧 Configuration

### Environment Variables

- `KEYWORDS_SHEET_ID` - Google Sheet ID for keywords
- `WEBSITES_SHEET_ID` - Google Sheet ID for websites
- `OUTPUT_FOLDER_ID` - Google Drive folder for output documents (default: "root")
- `FLASK_ENV` - Flask environment (default: "development")
- `FLASK_DEBUG` - Debug mode (default: "true")

## 📚 Detailed Setup

For comprehensive setup instructions, see [SETUP_GUIDE.md](SETUP_GUIDE.md)

## 🔄 Workflow

1. **Update Data Sources**
   - Add/remove keywords in Google Sheet
   - Add/remove websites in Google Sheet

2. **Run Collection**
   - Open web UI at http://localhost:5000
   - Click "Run Collection"
   - System searches all websites for keywords

3. **Processing Steps**
   - Fetches keywords from Google Sheet
   - Fetches websites from Google Sheet
   - Searches each website for keyword matches
   - Extracts article titles, URLs, summaries
   - Removes duplicate articles
   - Groups by language
   - Exports to Google Doc

4. **Review Results**
   - Document opens with clickable links
   - Articles organized by language
   - Website sources and summaries included
   - Ready to share or download

## ✅ Output Format

Generated Google Document includes:
- Report title and timestamp
- Total article count
- Articles grouped by language (English/Hindi)
- Clickable links to original articles
- Website sources
- Article summaries
- Professional formatting

## 📊 Status Tracking

Web UI provides real-time feedback:
- Current status (Idle, Initializing, Searching, etc.)
- Progress bar (0-100%)
- Detailed status message
- Results or error information
- Document link after completion

## 🐛 Troubleshooting

**Issue**: "credentials.json not found"
- **Solution**: Download OAuth 2.0 credentials from Google Cloud Console

**Issue**: "KEYWORDS_SHEET_ID must be set"
- **Solution**: Copy .env.example to .env and update with your sheet IDs

**Issue**: "No articles found"
- **Solution**: 
  - Try different keywords
  - Check that websites are accessible
  - Verify websites contain content matching keywords

**Issue**: Application timeout
- **Solution**: This is normal for some websites. App auto-retries with backoff.

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for more troubleshooting help.

## 🛠️ Development

### Install Dev Dependencies

```bash
pip install -r requirements.txt
pip install pytest pytest-cov black flake8 isort
```

### Run Tests

```bash
pytest
```

### Code Formatting

```bash
black src/ app.py
isort src/ app.py
```

## 📋 Requirements

- Python 3.9+
- Google Account
- Google Cloud Project
- Internet connection
- Modern web browser

## 📦 Dependencies

- `google-api-python-client` - Google APIs
- `google-auth-oauthlib` - OAuth 2.0 authentication
- `beautifulsoup4` - HTML parsing
- `requests` - HTTP requests
- `flask` - Web framework
- `python-dotenv` - Environment variables

## 📄 License

[Add your license here]

## 🤝 Contributing

Contributions welcome! Feel free to submit issues and pull requests.

## 📞 Support

For questions and support:
1. Check [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed instructions
2. Review application logs for error details
3. Check Google Cloud Console for API issues

---

**Built with ❤️ for bilingual news monitoring**


### Run via Terminal

```bash
python -m src.main
```

## Configuration Files

### `.env` Variables

- `KEYWORDS_SHEET_ID` - Google Sheets ID for keywords
- `WEBSITES_SHEET_ID` - Google Sheets ID for websites
- `OUTPUT_FOLDER_ID` - Google Drive folder to save documents (optional)

## How It Works

1. **Fetch Keywords** - Read from Google Sheets (Column A: Keyword, Column B: Language)
2. **Fetch Websites** - Read from Google Sheets (Column A: Name, Column B: URL, Column C: Language)
3. **Search Articles** - Loop through websites and keywords, scrape articles
4. **Extract Data** - Get title, URL, summary from each article
5. **Remove Duplicates**:
   - By URL (exact match)
   - By title (exact match)
   - By similarity (for cross-language matches)
6. **Export** - Create Google Doc with formatted results organized by language
7. **Timestamps** - Each document has timestamp for tracking

## Supported Languages

- 🇬🇧 English
- 🇮🇳 Hindi

## Dependencies

- `google-auth-oauthlib` - Google OAuth authentication
- `google-api-python-client` - Google API client
- `beautifulsoup4` - HTML parsing
- `requests` - HTTP requests
- `selenium` - Browser automation (optional, for JavaScript-heavy sites)
- `python-dotenv` - Environment variable management

## Troubleshooting

### API Authentication Issues

If you get authentication errors:
1. Delete `token.json` if it exists
2. Re-run the application
3. Authenticate with your Google account

### No Articles Found

1. Check your website URLs are correct
2. Verify keywords exist in Google Sheets
3. Check website structure (may need custom parsing)

### Google Sheets Errors

1. Share Google Sheets with your OAuth app email
2. Verify sheet IDs in `.env`
3. Check "Sheet1" exists in both spreadsheets

## Development

### Project Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Code Style

- Format: Black
- Linting: Flake8
- Line length: 88 characters

## Future Enhancements

- [ ] Add scheduled execution (APScheduler)
- [ ] Implement advanced web scraping (Selenium, Playwright)
- [ ] Add RSS feed support
- [ ] Create web UI for management
- [ ] Add email notifications
- [ ] Support more languages
- [ ] Export to Word, PDF formats
- [ ] Implement article summarization with AI
- [ ] Add filtering by date range
- [ ] Create analytics dashboard

## License

This project is provided as-is for news monitoring purposes.

## Support

For issues or questions, please check:
1. Project documentation
2. Google API documentation
3. BeautifulSoup documentation

---

**Last Updated:** January 2026
