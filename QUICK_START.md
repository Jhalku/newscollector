# 🚀 Getting Started - 5 Minutes

## TL;DR - Quick Start

```bash
# Step 1: Setup
python quickstart.py

# Step 2: Get credentials from Google Cloud
# Download credentials.json and place in project root

# Step 3: Run
python app.py

# Step 4: Open browser
# Go to http://localhost:5000

# Step 5: Click "Run Collection" button
```

That's it! 🎉

---

## What You'll Need

1. **Google Account** (free)
2. **Python 3.9+** (check with `python --version`)
3. **5 minutes** of setup time

---

## Step-by-Step

### 1️⃣ Run Quick Setup (30 seconds)

```bash
cd newsautocollector
python quickstart.py
```

This will:
- Check Python version
- Install dependencies
- Create `.env` file

### 2️⃣ Get Google Credentials (2 minutes)

1. Go to: https://console.cloud.google.com/
2. Create new project (name it anything)
3. Enable these APIs:
   - Google Sheets API
   - Google Docs API
   - Google Drive API
4. Create OAuth 2.0 Desktop credentials
5. Download the JSON file
6. Rename to `credentials.json`
7. Copy to project root (same folder as `app.py`)

### 3️⃣ Start Application (1 minute)

```bash
python app.py
```

You'll see:
```
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

### 4️⃣ Open in Browser (30 seconds)

Open: http://localhost:5000

You should see a beautiful dashboard! 🎨

### 5️⃣ First Run

1. Click **"Run Collection"** button
2. Browser will open for Google login (first time only)
3. Grant permissions
4. Come back to app - it will start running
5. Watch the progress bar
6. Click the document link when done ✅

---

## Data Setup (Optional but Recommended)

### Keywords
Add search terms to: https://docs.google.com/spreadsheets/d/1gLvmp0E9f9xEwF6YHgNM0eZJklN4XVB76pKUBqXIgr0

Example:
```
election          | English
चुनाव            | Hindi
budget            | English
बजट              | Hindi
```

### Websites
Add news sources to: https://docs.google.com/spreadsheets/d/1TCHI4zm7gyavORlgbH0j94cs55CCBwSVBjswtoi93nA

Example:
```
BBC News        | https://www.bbc.com/news      | English
The Hindu       | https://www.thehindu.com      | English
Aaj Tak         | https://www.aajtaak.in        | Hindi
```

---

## What Happens When You Click "Run"

```
1. Reads keywords from Google Sheet
2. Reads websites from Google Sheet
3. Searches each website for keywords
4. Extracts article titles, URLs, summaries
5. Removes duplicate articles
6. Creates Google Doc
7. Adds formatted content with clickable links
8. Shows success with document link
```

**All this takes 2-5 minutes!** ⏱️

---

## Output

You get a Google Document with:
- 📰 Article titles
- 🔗 Clickable links
- 📝 Summaries
- 🌐 Source websites
- 🗣️ Organized by language
- ⏰ Generated timestamp

And no duplicates! ✨

---

## Troubleshooting

### "credentials.json not found"
→ Download from Google Cloud Console and place in project root

### "KEYWORDS_SHEET_ID must be set"
→ Edit `.env` and add your sheet IDs from the links above

### "No articles found"
→ Try different keywords or add more websites

### "Browser didn't open for login"
→ First time only - manually go to shown URL in console

### Still stuck?
→ See `SETUP_GUIDE.md` for detailed help

---

## That's All!

You now have a fully automated news monitoring system! 🎉

### What to do next:

1. **Use it daily**: Click "Run Collection" anytime
2. **Update keywords**: Edit Google Sheet to change search terms
3. **Add websites**: Add more news sources in Google Sheet
4. **Share results**: Document is shareable from Google Drive

---

## Tips

💡 **Tip 1**: Keep keywords specific (e.g., "election" not "e")  
💡 **Tip 2**: Use 3-5 keywords per language  
💡 **Tip 3**: Add 5-10 news websites  
💡 **Tip 4**: Run once a day for news monitoring  
💡 **Tip 5**: Export documents to share with team  

---

## Commands Reference

```bash
# Start the app
python app.py

# Run from command line (no UI)
python -m src.main

# Setup again
python quickstart.py

# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

---

## Questions?

- **Setup issues?** → See `SETUP_GUIDE.md`
- **Want details?** → See `BUILD_SUMMARY.md`
- **Deploy?** → See `DEPLOYMENT_CHECKLIST.md`
- **What was built?** → See `BUILD_REPORT.md`

---

**Enjoy your news monitoring system!** 📰✨

Made with ❤️ for automated bilingual news collection
