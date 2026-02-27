import os
import logging
from datetime import datetime

def generate_news_report(keyword, articles):
    """Creates a local text file and writes news articles into it."""
    try:
        filename = f"News_Report_{keyword.replace(' ', '_').replace(':', '')}.txt"
        filepath = os.path.join(os.getcwd(), filename)
        
        logging.info(f"Generating local report at: {filepath}")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"News Report for '{keyword}'\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for idx, article in enumerate(articles, 1):
                date_str = article.get('date', 'Unknown Date')
                f.write(f"{idx}. {article.get('title', 'Unknown Title')}\n")
                f.write(f"Date: {date_str}\n")
                f.write(f"Link: {article.get('link', 'No Link')}\n\n")
                
        return filepath

    except Exception as err:
        logging.error(f"An error occurred generating the local report: {err}")
        return None
