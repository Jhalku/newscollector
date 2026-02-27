"""
News Scraper - Search news websites for articles matching keywords
"""

import logging
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from urllib.parse import urljoin, quote
import time
import random

logger = logging.getLogger(__name__)


class NewsScraper:
    """Scrape news articles from websites"""
    
    def __init__(self, timeout=15, delay=1):
        self.timeout = timeout
        self.delay = delay  # Delay between requests in seconds
        self.headers = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        ]
        self.session = requests.Session()
    
    def _get_headers(self):
        """Get random user agent headers"""
        return {
            'User-Agent': random.choice(self.headers),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def search_articles(self, websites: List[Dict], keywords: List[Dict]) -> List[Dict]:
        """
        Search for articles across multiple websites matching keywords
        
        Returns:
            List of article dicts: {
                'title': str,
                'url': str,
                'summary': str,
                'language': str,
                'website': str,
                'keyword': str
            }
        """
        articles = []
        
        # Group keywords by language
        keywords_by_lang = self._group_by_language(keywords, key='language')
        
        # Search each website
        for website in websites:
            logger.info(f"Searching website: {website['name']} ({website['url']})")
            language = website['language']
            keywords_for_lang = keywords_by_lang.get(language, [])
            
            if not keywords_for_lang:
                logger.warning(f"No keywords found for language: {language}")
                continue
            
            for keyword_obj in keywords_for_lang:
                keyword = keyword_obj['keyword']
                try:
                    found_articles = self._search_website(
                        website['url'],
                        keyword,
                        language,
                        website['name']
                    )
                    articles.extend(found_articles)
                    time.sleep(self.delay + random.uniform(0, 1))  # Randomize delay
                except Exception as e:
                    logger.error(
                        f"Error searching {website['name']} for '{keyword}': {str(e)}"
                    )
                    continue
        
        logger.info(f"Total articles found: {len(articles)}")
        return articles
    
    def _search_website(self, url: str, keyword: str, language: str, 
                       website_name: str) -> List[Dict]:
        """
        Search a specific website for articles matching a keyword
        """
        try:
            # Construct search URL
            search_url = self._build_search_url(url, keyword)
            logger.debug(f"Searching URL: {search_url}")
            
            # Try to fetch with retries
            response = None
            for attempt in range(3):
                try:
                    response = self.session.get(
                        search_url, 
                        headers=self._get_headers(),
                        timeout=self.timeout,
                        allow_redirects=True
                    )
                    response.raise_for_status()
                    break
                except requests.exceptions.Timeout:
                    if attempt < 2:
                        logger.debug(f"Timeout, retrying... (attempt {attempt + 1})")
                        time.sleep(2)
                    else:
                        raise
                except requests.exceptions.ConnectionError:
                    if attempt < 2:
                        logger.debug(f"Connection error, retrying... (attempt {attempt + 1})")
                        time.sleep(2)
                    else:
                        raise
            
            if not response:
                logger.warning(f"No response from {website_name}")
                return []
            
            # Parse and extract articles
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = self._parse_articles(soup, url, language, website_name, keyword)
            
            logger.info(f"Found {len(articles)} articles from {website_name} for '{keyword}'")
            return articles
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {website_name}: {type(e).__name__}: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error parsing articles from {website_name}: {str(e)}", exc_info=False)
            return []
    
    def _build_search_url(self, base_url: str, keyword: str) -> str:
        """
        Build search URL for the website with proper encoding
        """
        base_url = base_url.rstrip('/')
        keyword_encoded = quote(keyword)
        
        # Detect domain and use appropriate search pattern
        domain_lower = base_url.lower()
        
        if 'google.com' in domain_lower or 'news.google' in domain_lower:
            return f"https://www.google.com/search?q={keyword_encoded}"
        elif 'bbc.com' in domain_lower:
            return f"{base_url}/search?q={keyword_encoded}"
        elif 'cnn.com' in domain_lower:
            return f"{base_url}/cnn/search?query={keyword_encoded}"
        elif 'reuters.com' in domain_lower:
            return f"{base_url}/search?query={keyword_encoded}"
        elif 'bbc.co.in' in domain_lower or 'bbc' in domain_lower:
            return f"{base_url}/search?q={keyword_encoded}"
        elif 'thehindu.com' in domain_lower or 'hindu' in domain_lower:
            return f"{base_url}/news/national?q={keyword_encoded}"
        elif 'indiatoday.in' in domain_lower or 'indiatoday' in domain_lower:
            return f"{base_url}/search?q={keyword_encoded}"
        elif 'deccan' in domain_lower or 'herald' in domain_lower:
            return f"{base_url}/search?q={keyword_encoded}"
        elif 'aaj-tak' in domain_lower or 'aajtaak' in domain_lower:
            return f"{base_url}/search?q={keyword_encoded}"
        else:
            # Default: try common search patterns
            return f"{base_url}/search?q={keyword_encoded}"
    
    def _parse_articles(self, soup: BeautifulSoup, base_url: str, language: str,
                       website_name: str, keyword: str) -> List[Dict]:
        """
        Parse HTML and extract article information using multiple selector strategies
        """
        articles = []
        
        # Common article selectors (in order of specificity)
        article_selectors = [
            'article',
            'div[role="article"]',
            'div.article-item',
            'div.news-item',
            'div.post',
            'div.story',
            'div.item',
            'a[data-trackable="link"]',  # BBC style
            'div.result',  # Google search
            'div.g',  # Google search
            'section.article',
            'div[class*="article"]',
            'div[class*="news"]',
            'li[data-article]',
        ]
        
        # Try each selector
        found_elements = set()
        for selector in article_selectors:
            try:
                article_elements = soup.select(selector)[:20]  # Limit to 20 per selector
                
                for element in article_elements:
                    elem_str = str(element)[:100]  # Avoid duplicates
                    if elem_str not in found_elements:
                        found_elements.add(elem_str)
                        try:
                            article = self._extract_article_data(
                                element, base_url, language, website_name, keyword
                            )
                            if article and article not in articles:  # Avoid duplicates
                                articles.append(article)
                        except Exception as e:
                            logger.debug(f"Error extracting article: {str(e)}")
                            continue
            except Exception as e:
                logger.debug(f"Error with selector '{selector}': {str(e)}")
                continue
        
        return articles[:30]  # Limit to 30 articles per search
    
    def _extract_article_data(self, element, base_url: str, language: str,
                            website_name: str, keyword: str) -> Optional[Dict]:
        """
        Extract title, URL, and summary from article element
        """
        try:
            # Try to find title
            title = None
            title_selectors = [
                'h1', 'h2', 'h3', 'h4',
                'a[aria-label]',  # BBC style
                'span[class*="headline"]',
                '.title', '.headline', '.heading',
                '[class*="title"]',
                '[class*="headline"]',
            ]
            
            for selector in title_selectors:
                title_elem = element.select_one(selector)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if title and len(title) > 10:  # Ensure reasonable length
                        break
            
            if not title or len(title) < 10:
                return None
            
            # Try to find URL
            url = None
            link_elem = element.find('a', href=True)
            if not link_elem:
                link_elem = element.select_one('a')
            
            if link_elem:
                url = link_elem.get('href')
                if url:
                    url = urljoin(base_url, url)
                    # Clean up URL
                    url = url.split('#')[0].split('?')[0] if url else None
            
            if not url:
                return None
            
            # Try to find summary
            summary = None
            summary_selectors = [
                '.summary', '.excerpt', '.description',
                '[class*="summary"]',
                '[class*="excerpt"]',
                '[class*="description"]',
                'p'
            ]
            
            for selector in summary_selectors:
                summary_elem = element.select_one(selector)
                if summary_elem:
                    summary = summary_elem.get_text(strip=True)
                    if summary:
                        summary = summary[:300]  # Limit to 300 chars
                        break
            
            return {
                'title': title.strip(),
                'url': url,
                'summary': summary.strip() if summary else '',
            }
        except Exception as e:
            logger.debug(f"Error extracting article data: {str(e)}")
            return None
    
    @staticmethod
    def _group_by_language(items: List[Dict], key: str = 'language') -> Dict[str, List]:
        """Group items by language"""
        grouped = {}
        for item in items:
            lang = item.get(key, 'Unknown')
            if lang not in grouped:
                grouped[lang] = []
            grouped[lang].append(item)
        return grouped
