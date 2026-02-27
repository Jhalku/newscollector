# Deployment Checklist

## Pre-Launch Verification

### Core Files ✅
- [ ] `src/main.py` exists and is complete
- [ ] `src/google_sheets_handler.py` exists with OAuth2 auth
- [ ] `src/google_docs_exporter.py` exists with proper linking
- [ ] `src/news_scraper.py` exists with retry logic
- [ ] `src/deduplicator.py` exists with multi-strategy dedup
- [ ] `app.py` (Flask app) exists
- [ ] `quickstart.py` (setup script) exists

### Web UI ✅
- [ ] `templates/index.html` exists
- [ ] `static/style.css` exists
- [ ] `static/script.js` exists
- [ ] UI is responsive and works on mobile
- [ ] Progress bar updates correctly
- [ ] Status messages display properly

### Documentation ✅
- [ ] `README.md` is complete
- [ ] `SETUP_GUIDE.md` is comprehensive
- [ ] `BUILD_SUMMARY.md` documents what was built
- [ ] `.env.example` has correct variable names
- [ ] Code has proper comments

### Configuration ✅
- [ ] `requirements.txt` includes Flask
- [ ] `requirements.txt` includes all Google APIs
- [ ] `pyproject.toml` is complete
- [ ] `.env.example` is properly formatted

## Installation Verification

### Step 1: Environment Setup
```bash
# Run quick setup
python quickstart.py
```
Expected output:
- ✓ Python version check passes
- ✓ Dependencies install successfully
- ✓ .env file created from .env.example
- Instructions provided for next steps

### Step 2: Google API Setup
Verify:
- [ ] Google Cloud Console project created
- [ ] Google Sheets API enabled
- [ ] Google Docs API enabled
- [ ] Google Drive API enabled
- [ ] OAuth 2.0 Desktop credentials created
- [ ] `credentials.json` downloaded and placed in project root

### Step 3: Environment Configuration
```bash
# Copy template to actual .env
cp .env.example .env

# Edit .env with your sheet IDs
# KEYWORDS_SHEET_ID=1gLvmp0E9f9xEwF6YHgNM0eZJklN4XVB76pKUBqXIgr0
# WEBSITES_SHEET_ID=1TCHI4zm7gyavORlgbH0j94cs55CCBwSVBjswtoi93nA
```

### Step 4: First Run
```bash
python app.py
```
Expected:
- [ ] Flask server starts on port 5000
- [ ] No authentication errors
- [ ] Web UI accessible at http://localhost:5000
- [ ] Web UI loads and displays properly

### Step 5: First Execution
1. [ ] Open http://localhost:5000 in browser
2. [ ] Click "Run Collection"
3. [ ] Browser opens for Google authentication (first time only)
4. [ ] Status changes from "Idle" to "Running"
5. [ ] Progress bar updates
6. [ ] Status messages update
7. [ ] Execution completes with "Complete" status
8. [ ] Document URL appears in results
9. [ ] Can click document link to open in Google Docs

## Functionality Testing

### Data Source Testing
- [ ] Keywords sheet is readable
- [ ] Websites sheet is readable
- [ ] Data format is correct (columns A, B, etc.)
- [ ] Both English and Hindi keywords work
- [ ] Both English and Hindi websites work

### Search Testing
- [ ] Articles are found for keywords
- [ ] URLs are valid and clickable
- [ ] Summaries are extracted correctly
- [ ] Website names are captured
- [ ] Language tags are correct

### Deduplication Testing
- [ ] Duplicate URLs are removed
- [ ] Duplicate titles are removed
- [ ] Similar titles are detected
- [ ] No data loss during deduplication
- [ ] Language organization works

### Export Testing
- [ ] Google Doc is created successfully
- [ ] Document title includes timestamp
- [ ] Content is formatted properly
- [ ] Links are clickable and correct
- [ ] Language sections are organized
- [ ] Article count is accurate

### Error Handling
- [ ] Network timeouts are handled gracefully
- [ ] Invalid websites show appropriate errors
- [ ] Missing keywords sheet shows clear error
- [ ] Authentication failures are informative
- [ ] All errors are logged

## Performance Verification

- [ ] Small keyword set (3 keywords): 2-3 minutes
- [ ] Medium keyword set (5 keywords): 3-5 minutes
- [ ] Large keyword set (10+ keywords): 5-10 minutes
- [ ] Web UI responds during execution
- [ ] Progress bar updates smoothly
- [ ] No memory leaks during long execution

## Security Verification

- [ ] Credentials are not logged
- [ ] OAuth tokens are stored securely
- [ ] HTTPS is used (if deployed)
- [ ] No sensitive data in version control
- [ ] API keys are properly scoped
- [ ] User agents are rotated

## Browser Compatibility

- [ ] Chrome/Edge (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Mobile browsers (iOS Safari, Chrome Mobile)

## Deployment Readiness

### Code Quality
- [ ] No syntax errors
- [ ] No undefined variables
- [ ] Proper error handling throughout
- [ ] Consistent code style
- [ ] Comments where needed

### Documentation
- [ ] README is clear and helpful
- [ ] SETUP_GUIDE is comprehensive
- [ ] API endpoints documented
- [ ] Code comments are helpful
- [ ] Examples are provided

### Logging
- [ ] INFO level messages for major steps
- [ ] ERROR level for failures
- [ ] DEBUG level for details
- [ ] No sensitive data logged
- [ ] Timestamps included

## Launch Checklist

- [ ] All tests pass
- [ ] Documentation is complete
- [ ] Code review completed
- [ ] No known bugs
- [ ] Performance is acceptable
- [ ] Security is verified
- [ ] Backup plan exists
- [ ] Support docs available

## Post-Launch

- [ ] Monitor application logs
- [ ] Track any errors or issues
- [ ] Collect user feedback
- [ ] Plan improvements
- [ ] Schedule maintenance
- [ ] Update documentation
- [ ] Prepare for scaling

---

## Final Sign-Off

- [ ] Developer: _________________ Date: _______
- [ ] Reviewer: _________________ Date: _______

---

**Status**: Ready for deployment when all items are checked ✅
