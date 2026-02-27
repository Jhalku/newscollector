import logging
from datetime import datetime, timedelta
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from GoogleNews import GoogleNews
import local_report_helper

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

@app.route("/webhook", methods=['POST'])
def webhook():
    incoming_msg = request.values.get('Body', '').strip()
    sender = request.values.get('From', '')

    target_number = "whatsapp:+917011669724"
    
    logging.info(f"Received message: {incoming_msg} from {sender}")
    
    resp = MessagingResponse()

    if sender != target_number:
        logging.warning(f"Unauthorized access attempt from {sender}")
        return str(resp) # Return empty response for unauthorized numbers
        
    msg = resp.message()
    
    parts = incoming_msg.split(maxsplit=2)
    
    if len(parts) < 3 or parts[0].lower() != "search":
       msg.body("Usage: search <website> <keyword>\nExample: search site:ndtv.com election or search site:timesofindia.indiatimes.com modi")
       return str(resp)
        
    site = parts[1]
    keyword = parts[2]
    
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
            msg.body(f"Report generated successfully!\nSaved locally to: {doc_link}")
        else:
            msg.body("Found articles, but failed to generate the local report file. Please check server logs.")
    else:
        msg.body("No articles found in last 48 hours.")
        
    return str(resp)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
