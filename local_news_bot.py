import io
import sys
import logging
from datetime import datetime, timedelta
from GoogleNews import GoogleNews
import local_report_helper

# set stdout to utf-8 to avoid charmap errors with emojis
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

logging.basicConfig(level=logging.INFO)

def run_local_bot():
    print("=== Welcome to the Local News Collector Bot ===")
    print("Type a command like 'search site:ndtv.com election'.")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("News Bot > ").strip()
            if user_input.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
            
            if not user_input.lower().startswith("search "):
                print("Usage: search <website> <keyword>")
                print("Example: search site:ndtv.com election")
                continue

            parts = user_input.split(maxsplit=2)
            if len(parts) < 3:
                print("Usage: search <website> <keyword>")
                continue
                
            site = parts[1]
            keyword = parts[2]
            
            print(f"Searching for '{keyword}' on {site}...")
            
            # 48 hours ago
            end_date = datetime.now()
            start_date = end_date - timedelta(hours=48)
            
            gn = GoogleNews(start=start_date.strftime('%m/%d/%Y'), end=end_date.strftime('%m/%d/%Y'), lang='en')
            gn.search(f"{keyword} {site}")
            
            results = []
            for page in range(1, 3):  # Top 2 pages
                gn.getpage(page)
                results.extend(gn.result())
            
            recent_articles = [r for r in results if r.get('datetime') is not None and keyword.lower() in (r.get('title', '').lower() + r.get('desc', '').lower())]
            
            if recent_articles:
                doc_link = local_report_helper.generate_news_report(f"{keyword} {site}", recent_articles)
                if doc_link:
                    print(f"✅ Report generated successfully!")
                    print(f"📁 Saved locally to: {doc_link}\n")
                else:
                    print("❌ Found articles, but failed to generate the local report file. Please check server logs.\n")
            else:
                print("ℹ️ No articles found in last 48 hours.\n")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Run a single query from CLI args
        query = " ".join(sys.argv[1:])
        try:
            parts = query.split(maxsplit=2)
            if not query.lower().startswith("search ") or len(parts) < 3:
                print("Usage: python local_news_bot.py search <website> <keyword>")
            else:
                site = parts[1]
                keyword = parts[2]
                print(f"Searching for '{keyword}' on {site}...")
                
                end_date = datetime.now()
                start_date = end_date - timedelta(hours=48)
                
                gn = GoogleNews(start=start_date.strftime('%m/%d/%Y'), end=end_date.strftime('%m/%d/%Y'), lang='en')
                gn.search(f"{keyword} {site}")
                
                results = []
                for page in range(1, 3):
                    gn.getpage(page)
                    results.extend(gn.result())
                
                recent_articles = [r for r in results if r.get('datetime') is not None and keyword.lower() in (r.get('title', '').lower() + r.get('desc', '').lower())]
                
                if recent_articles:
                    doc_link = local_report_helper.generate_news_report(f"{keyword} {site}", recent_articles)
                    if doc_link:
                        print(f"✅ Report generated successfully!")
                        print(f"📁 Saved locally to: {doc_link}\n")
                    else:
                        print("❌ Found articles, but failed to generate the local report file.\n")
                else:
                    print("ℹ️ No articles found in last 48 hours.\n")
        except Exception as e:
            print(f"An error occurred: {e}")
    else:
        run_local_bot()
