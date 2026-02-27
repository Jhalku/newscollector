"""
Deduplicator - Remove duplicate articles based on URL and title similarity
"""

import logging
from typing import List, Dict
from difflib import SequenceMatcher
import hashlib

logger = logging.getLogger(__name__)


class Deduplicator:
    """Remove duplicate articles using multiple strategies"""
    
    def __init__(self, title_similarity_threshold=0.85):
        self.title_similarity_threshold = title_similarity_threshold
    
    def remove_duplicates(self, articles: List[Dict]) -> List[Dict]:
        """
        Remove duplicate articles using multiple strategies:
        1. Exact URL match
        2. Title similarity (for cross-language duplicates)
        3. Exact title match
        """
        logger.info("Starting deduplication process...")
        
        # Step 1: Remove exact URL duplicates
        articles = self._remove_url_duplicates(articles)
        logger.info(f"After URL deduplication: {len(articles)} articles")
        
        # Step 2: Remove exact title duplicates
        articles = self._remove_title_duplicates(articles)
        logger.info(f"After title deduplication: {len(articles)} articles")
        
        # Step 3: Remove similar titles (cross-language duplicates)
        articles = self._remove_similar_titles(articles)
        logger.info(f"After similarity deduplication: {len(articles)} articles")
        
        return articles
    
    def _remove_url_duplicates(self, articles: List[Dict]) -> List[Dict]:
        """Remove articles with duplicate URLs"""
        seen_urls = set()
        unique_articles = []
        
        for article in articles:
            url = article.get('url', '').lower()
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_articles.append(article)
            elif not url:
                # Keep articles without URLs
                unique_articles.append(article)
        
        removed = len(articles) - len(unique_articles)
        if removed > 0:
            logger.debug(f"Removed {removed} articles with duplicate URLs")
        
        return unique_articles
    
    def _remove_title_duplicates(self, articles: List[Dict]) -> List[Dict]:
        """Remove articles with exact same title"""
        seen_titles = set()
        unique_articles = []
        
        for article in articles:
            title = article.get('title', '').lower().strip()
            title_hash = hashlib.md5(title.encode()).hexdigest()
            
            if title and title_hash not in seen_titles:
                seen_titles.add(title_hash)
                unique_articles.append(article)
            elif not title:
                # Keep articles without titles
                unique_articles.append(article)
        
        removed = len(articles) - len(unique_articles)
        if removed > 0:
            logger.debug(f"Removed {removed} articles with exact duplicate titles")
        
        return unique_articles
    
    def _remove_similar_titles(self, articles: List[Dict]) -> List[Dict]:
        """Remove articles with similar titles (potential cross-language duplicates)"""
        unique_articles = []
        processed_indices = set()
        
        for i, article in enumerate(articles):
            if i in processed_indices:
                continue
            
            unique_articles.append(article)
            current_title = article.get('title', '').lower().strip()
            
            # Check against remaining articles
            for j in range(i + 1, len(articles)):
                if j in processed_indices:
                    continue
                
                other_title = articles[j].get('title', '').lower().strip()
                
                # Calculate similarity
                similarity = self._calculate_similarity(current_title, other_title)
                
                if similarity >= self.title_similarity_threshold:
                    logger.debug(
                        f"Removing similar article: '{articles[j]['title'][:50]}' "
                        f"(similarity: {similarity:.2f})"
                    )
                    processed_indices.add(j)
        
        removed = len(articles) - len(unique_articles)
        if removed > 0:
            logger.debug(f"Removed {removed} articles with similar titles")
        
        return unique_articles
    
    @staticmethod
    def _calculate_similarity(str1: str, str2: str) -> float:
        """Calculate similarity between two strings (0.0 to 1.0)"""
        if not str1 or not str2:
            return 0.0
        
        matcher = SequenceMatcher(None, str1, str2)
        return matcher.ratio()
