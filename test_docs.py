import google_docs_helper
import logging

logging.basicConfig(level=logging.INFO)

print("Starting Google Docs test...")
try:
    articles = [
        {'title': 'Test Article 1', 'date': 'Yesterday', 'link': 'http://example.com/1'},
        {'title': 'Test Article 2', 'date': 'Today', 'link': 'http://example.com/2'}
    ]
    res = google_docs_helper.generate_news_report('Test Run', articles)
    print(f"Success! Link: {res}")
except Exception as e:
    print(f"Failed with exception: {e}")
