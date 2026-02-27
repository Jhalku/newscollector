import os
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

report = """
🏗️ <b>News Autobot: System Design Explained (Simple Terms)</b>

Hey there! Here is how your News Tracker actually works behind the scenes:

<b>1. The Brain (.env file)</b> 🧠
This is where we store your secrets and preferences. It tells the bot:
• Keywords to look for (like "AI India")
• Where to look (like "bbc.com" or "ndtv.com")
• Who to send it to (Your Telegram ID)

<b>2. The Fetcher (news_tracker.py)</b> 🕵️
When you double-click `run_now.bat` (or at 9 AM daily), the Python script wakes up.
• It goes to <b>Google News RSS</b> (a special raw data feed meant for computers) and asks for articles from the last 2 days matching your keywords and sites.
• <i>Why RSS?</i> Because normal Google scraping blocks robots with "Too Many Requests" errors. RSS is safe!

<b>3. The Organizer (python-docx library)</b> 📋
Once it has all the links, it throws away duplicates. Then it uses a library called `docx` to create a beautiful <b>Microsoft Word Document</b> automatically, formatting titles in bold and pasting the links neatly.

<b>4. The Delivery Boy (Telegram API)</b> 🚀
Finally, the script connects to Telegram's servers using your Bot Token.
• First, it sends a quick text summary of the top 10 articles.
• Second, it securely uploads the Word document straight into this chat for you to download.

That's it! 4 simple parts working together to save you hours of searching. ⚙️
"""

url_msg = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
payload = {
    'chat_id': TELEGRAM_CHAT_ID,
    'text': report,
    'parse_mode': 'HTML',
    'disable_web_page_preview': True
}

try:
    print("Sending system design report to Telegram...")
    res = requests.post(url_msg, json=payload)
    if res.status_code == 200:
        print("Successfully sent report to Telegram!")
    else:
        print(f"Failed to send: {res.text}")
except Exception as e:
    print(f"Error: {e}")
