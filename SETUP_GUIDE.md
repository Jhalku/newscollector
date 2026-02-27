# Setup Guide - Bilingual News Monitoring Automation

## Complete Setup Instructions

### Step 1: Clone/Setup the Project

```bash
cd newsautocollector
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Google Cloud Project Setup

#### 3.1 Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on "Select a project" → "New Project"
3. Enter project name: `News Auto Collector`
4. Click "Create"

#### 3.2 Enable Required APIs
1. In the Cloud Console, search for and enable:
   - **Google Sheets API**
   - **Google Docs API**
   - **Google Drive API**

#### 3.3 Create OAuth 2.0 Credentials
1. Go to **Credentials** in the left sidebar
2. Click **Create Credentials** → **OAuth 2.0 Client ID**
3. Choose application type: **Desktop application**
4. Click "Create"
5. Download the JSON file and rename it to `credentials.json`
6. Place `credentials.json` in the project root directory:
   ```
   newsautocollector/
   ├── credentials.json  ← Place here
   ├── app.py
   ├── src/
   └── ...
   ```

### Step 4: Setup Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and set your Google Sheets IDs:
   ```
   KEYWORDS_SHEET_ID=1gLvmp0E9f9xEwF6YHgNM0eZJklN4XVB76pKUBqXIgr0
   WEBSITES_SHEET_ID=1TCHI4zm7gyavORlgbH0j94cs55CCBwSVBjswtoi93nA
   OUTPUT_FOLDER_ID=root
   ```

### Step 5: Google Sheets Setup

#### 5.1 Keywords Sheet
URL: https://docs.google.com/spreadsheets/d/1gLvmp0E9f9xEwF6YHgNM0eZJklN4XVB76pKUBqXIgr0/edit?usp=sharing

**Format:**
- **Column A**: Keyword (e.g., "election", "budget", "cricket")
- **Column B**: Language (e.g., "English" or "Hindi")

Example:
```
Keyword          | Language
election         | English
चुनाव           | Hindi
budget           | English
बजट            | Hindi
cricket          | English
क्रिकेट         | Hindi
```

#### 5.2 Websites Sheet
URL: https://docs.google.com/spreadsheets/d/1TCHI4zm7gyavORlgbH0j94cs55CCBwSVBjswtoi93nA/edit?usp=sharing

**Format:**
- **Column A**: Website Name (e.g., "BBC News", "The Hindu")
- **Column B**: Website URL (e.g., "https://www.bbc.com/news")
- **Column C**: Language (e.g., "English" or "Hindi")

Example:
```
Website Name    | URL                              | Language
BBC News        | https://www.bbc.com/news        | English
CNN             | https://www.cnn.com             | English
The Hindu       | https://www.thehindu.com        | English
BBC Hindi       | https://www.bbc.com/hindi       | Hindi
Aaj Tak         | https://www.aajtaak.in          | Hindi
India Today     | https://www.indiatoday.in       | Hindi
```

### Step 6: Run the Application

#### Option A: Web UI (Recommended)

1. Start the Flask application:
   ```bash
   python app.py
   ```

2. Open your browser and go to:
   ```
   http://localhost:5000
   ```

3. Click "Run Collection" to start the process

4. Monitor progress in real-time:
   - Status updates
   - Progress bar
   - Completion status
   - Results with Google Docs link

#### Option B: Command Line

```bash
python -m src.main
```

### Step 7: First-Time Authentication

1. When you run the application for the first time, a browser window will open
2. Sign in with your Google account
3. Grant the necessary permissions:
   - ✓ See and download all your Google Drive files
   - ✓ Create, edit, and delete Google Docs
   - ✓ View and manage Google Sheets
4. The browser will show "The authentication flow has completed"
5. Close the browser window and return to the application

The authentication token will be saved as `token.pickle` for future use.

### Step 8: Generated Output

After successful execution:
- A new Google Document will be created automatically
- Document name format: `News Report - YYYY-MM-DD HH:MM:SS`
- Document location: Google Drive (root or specified folder)
- Document contents:
  - Report title and timestamp
  - Article count
  - Articles organized by language
  - Clickable links to original articles
  - Website sources and summaries
  - Automatic duplicate removal applied

## Usage Workflow

### For Daily Monitoring:

1. **Update Keywords** (if needed):
   - Edit the keywords Google Sheet
   - Add/remove search terms
   - Can mix English and Hindi keywords

2. **Update Websites** (if needed):
   - Edit the websites Google Sheet
   - Add/remove news sources
   - Ensure URLs are accessible

3. **Run Collection**:
   - Open http://localhost:5000
   - Click "Run Collection"
   - Wait for completion (typically 2-5 minutes)
   - Click the Google Docs link in results

4. **Review Results**:
   - Open the generated Google Doc
   - Browse articles by language
   - Click links to read full articles
   - Share or download as needed

## Troubleshooting

### Common Issues

**Issue**: "credentials.json not found"
- **Solution**: Download OAuth 2.0 credentials from Google Cloud Console and place in project root

**Issue**: "KEYWORDS_SHEET_ID must be set"
- **Solution**: Copy `.env.example` to `.env` and update with your sheet IDs

**Issue**: "The authentication flow has completed. You may close this window"
- **Solution**: Normal - just close the browser window and return to the application

**Issue**: "Request timeout" during search
- **Solution**: This is normal for some websites. The application will retry automatically.

**Issue**: No articles found
- **Possible causes**:
  - Keywords don't exist in website content
  - Website structure changed (HTML selectors need update)
  - Website blocking automated requests
- **Solution**: Try different keywords or websites

### Debugging

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check logs in console output for detailed information about each step.

## Project Structure

```
newsautocollector/
├── app.py                        # Flask web application
├── credentials.json              # OAuth 2.0 credentials (created after auth)
├── token.pickle                  # Auth token (created after first login)
├── .env                          # Environment variables
├── .env.example                  # Environment template
├── requirements.txt              # Python dependencies
├── pyproject.toml               # Project metadata
├── README.md                    # Project overview
├── SETUP_GUIDE.md              # This file
│
├── src/
│   ├── __init__.py
│   ├── main.py                 # Main orchestrator
│   ├── google_sheets_handler.py # Google Sheets API
│   ├── google_docs_exporter.py  # Google Docs API
│   ├── news_scraper.py         # Web scraping
│   └── deduplicator.py         # Duplicate removal
│
├── templates/
│   └── index.html              # Web UI
│
└── static/
    ├── style.css               # Styling
    └── script.js               # JavaScript logic
```

## Features

✅ **Multi-Website Search** - Search across multiple news sources
✅ **Bilingual Support** - English and Hindi keywords and sources  
✅ **Smart Deduplication** - Remove duplicates by URL, title, and similarity
✅ **Google Sheets Integration** - Easy keyword and website management
✅ **Google Docs Export** - Formatted documents with clickable links
✅ **Web UI** - Simple, intuitive interface for manual triggering
✅ **Real-time Progress** - Monitor execution in real-time
✅ **Error Handling** - Robust error recovery and logging

## API Endpoints (for advanced users)

### GET /api/status
Get current execution status
```json
{
  "running": false,
  "status": "idle",
  "progress": 0,
  "message": "Ready to start",
  "doc_url": null,
  "error": null
}
```

### POST /api/run
Start collection
```json
{"success": true, "message": "Execution started"}
```

### POST /api/reset
Reset execution status
```json
{"success": true, "message": "Status reset"}
```

## Performance Tips

1. **Optimal Keywords**: Use 3-5 relevant keywords per language
2. **Website Selection**: Use fast, reliable news sources
3. **Execution Time**: Typically 2-5 minutes depending on:
   - Number of websites
   - Number of keywords
   - Website response time
   - Network speed

4. **Rate Limiting**: Application respects server limits with:
   - Random delays between requests
   - User agent rotation
   - Automatic retry on timeout

## Support & Maintenance

- Check logs in application output for debugging
- Monitor Google Drive for generated documents
- Update keywords and websites in Google Sheets
- Keep Python packages updated: `pip install -r requirements.txt --upgrade`

---

**Happy News Monitoring!** 📰✨
