import sys
import io

# set stdout to utf-8 to avoid charmap errors
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from datetime import datetime, timedelta
from GoogleNews import GoogleNews

site = "site:ndtv.com"
keyword = "election"

end_date = datetime.now()
start_date = end_date - timedelta(hours=48)

print(f"Searching for {keyword} {site} from {start_date.strftime('%m/%d/%Y')} to {end_date.strftime('%m/%d/%Y')}")

gn = GoogleNews(start=start_date.strftime('%m/%d/%Y'), end=end_date.strftime('%m/%d/%Y'), lang='en')
gn.search(f"{keyword} {site}")

results = []
for page in range(1, 3):
    gn.getpage(page)
    results.extend(gn.result())

print(f"Total results: {len(results)}")
if results:
    print(f"Sample result: {results[0]}")

recent_articles = [r for r in results if 'pubDate' in r and keyword.lower() in (r.get('title', '').lower() + r.get('desc', '').lower())]
print(f"Filtered results: {len(recent_articles)}")

if recent_articles:
    latest = max(recent_articles, key=lambda x: str(x['pubDate'])) 
    print(f"Latest pubDate: {latest['pubDate']}")
