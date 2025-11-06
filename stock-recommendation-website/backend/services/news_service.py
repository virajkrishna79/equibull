import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os
from models import NewsArticle
from app import db
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class NewsService:
    def __init__(self):
        self.news_api_key = os.getenv('NEWS_API_KEY')
        self.news_base_url = 'https://newsapi.org/v2'
        self.fallback_news = self._get_fallback_news()

        # Indian financial news sources (whitelist approach)
        self.preferred_sources = [
            "thehindu.com", "economictimes.indiatimes.com", "business-standard.com",
            "moneycontrol.com", "livemint.com", "financialexpress.com",
            "bloombergquint.com", "reuters.com", "bloomberg.com",
            "ndtv.com", "zeebiz.com", "cnbctv18.com"
        ]

        # Block these website domains
        self.blocked_domains = [
            "twistedsifter.com", "autoexpress.co.uk", "oklahoman.com", "tvline.com",
            "variety.com", "allears.net", "pcgamer.com", "nintendolife.com",
            "indiewire.com", "commonsensewithmoney.com", "forbes.com",
            "redflagdeals.com", "bringatrailer.com", "irishtimes.com",
            "ozbargain.com.au", "wccftech.com", "globenewswire.com",
            "notebookcheck.net", "finance.yahoo.com", "comicbook.com",
            "biztoc.com", "cnet.com", "cbc.ca", "adexchanger.com",
            "wwd.com", "americanthinker.com", "mcnews.com.au",
            "cnblogs.com", "sammobile.com", "protothema.gr", "abc.net.au"
        ]
        
        # Block specific paths within allowed domains
        self.blocked_paths = [
            "/magazines/", "/entertainment/", "/lifestyle/", "/sports/", "/panache/"
        ]
        
    def _is_allowed_article(self, article: Dict[str, Any]) -> bool:
        """Return False if the article domain or path is blocked"""
        url = article.get("url", "")
        
        # Parse URL
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        path = parsed_url.path.lower()

        # Check blocked domains
        for blocked_domain in self.blocked_domains:
            if blocked_domain in domain:
                return False

        # Check blocked paths (even for allowed domains)
        for blocked_path in self.blocked_paths:
            if blocked_path in path:
                return False
                
        return True

    def _is_indian_financial_news(self, article: Dict[str, Any]) -> bool:
        """Check if article is Indian financial news"""
        title = article.get('title', '').lower()
        description = article.get('description', '').lower()
        content = article.get('content', '').lower()
        
        # Indian financial keywords
        indian_keywords = [
            'india', 'indian', 'bse', 'nse', 'sensex', 'nifty', 'rupee', 'rs.',
            'mumbai', 'delhi', 'bangalore', 'chennai', 'kolkata', 'hyderabad',
            'sebi', 'rbi', 'fmcg', 'psu', 'psb', 'indian economy', 'gst',
            'union budget', 'finance minister', 'mcap', 'market cap'
        ]
        
        # Financial keywords
        financial_keywords = [
            'stock', 'share', 'market', 'trading', 'investment', 'investing',
            'ipo', 'dividend', 'earnings', 'profit', 'revenue', 'quarterly',
            'financial', 'banking', 'insurance', 'mutual fund', 'portfolio'
        ]
        
        # Check if article contains Indian financial content
        text = f"{title} {description} {content}"
        
        indian_matches = sum(1 for keyword in indian_keywords if keyword in text)
        financial_matches = sum(1 for keyword in financial_keywords if keyword in text)
        
        return indian_matches >= 1 and financial_matches >= 2

    def get_latest_news(self, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            if self.news_api_key:
                # Try multiple approaches to get fresh news
                news_sources = [
                    self._fetch_recent_indian_financial_news,
                    self._fetch_top_headlines_india,
                    self._fetch_indian_financial_news
                ]
                
                for news_source in news_sources:
                    news = news_source(limit)
                    if news and len(news) > 0:
                        # Filter for very recent articles (last 6 hours)
                        recent_news = self._filter_recent_articles(news, hours=6)
                        if recent_news:
                            return recent_news
                
                # If no recent news found, return whatever we have
                for news_source in news_sources:
                    news = news_source(limit)
                    if news and len(news) > 0:
                        return news

            return []
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return []

    def _filter_recent_articles(self, articles: List[Dict[str, Any]], hours: int = 6) -> List[Dict[str, Any]]:
        """Filter articles published within the last specified hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_articles = []
        
        for article in articles:
            published_at = article.get('published_at')
            if not published_at:
                continue
                
            try:
                # Handle different datetime formats
                if isinstance(published_at, str):
                    if 'Z' in published_at:
                        article_dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                    else:
                        article_dt = datetime.fromisoformat(published_at)
                else:
                    article_dt = published_at
                    
                if article_dt >= cutoff_time:
                    recent_articles.append(article)
            except Exception as e:
                logger.warning(f"Error parsing date {published_at}: {e}")
                continue
                
        return recent_articles

    def _fetch_recent_indian_financial_news(self, limit: int) -> Optional[List[Dict[str, Any]]]:
        """Fetch very recent Indian financial news (last 24 hours)"""
        try:
            # Calculate date for last 24 hours
            from_date = (datetime.utcnow() - timedelta(hours=24)).strftime('%Y-%m-%d')
            
            query = "(India OR Indian OR BSE OR NSE OR Sensex OR Nifty OR rupee) AND (stock OR share OR market OR trading OR investment OR finance)"
            url = f"{self.news_base_url}/everything"
            
            params = {
                'q': query,
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': limit * 3,  # Fetch more to filter
                'from': from_date,
                'apiKey': self.news_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'articles' in data:
                articles = []
                for article in data['articles']:
                    # Skip blocked domains/paths
                    if not self._is_allowed_article(article):
                        continue
                    
                    # Filter for Indian financial news
                    if not self._is_indian_financial_news(article):
                        continue
                    
                    # Remove sentiment analysis since you don't want scores
                    
                    news_article = NewsArticle(
                        title=article['title'],
                        description=article.get('description', ''),
                        content=article.get('content', ''),
                        url=article.get('url', ''),
                        source=article.get('source', {}).get('name', ''),
                        published_at=datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00')),
                        sentiment_score=0.0,  # Default value
                        sentiment_label='neutral'  # Default value
                    )
                    
                    try:
                        db.session.add(news_article)
                        db.session.commit()
                    except Exception as e:
                        logger.warning(f"Failed to store news article: {e}")
                        db.session.rollback()
                    
                    articles.append({
                        'title': article['title'],
                        'description': article.get('description', ''),
                        'url': article.get('url', ''),
                        'source': article.get('source', {}).get('name', ''),
                        'published_at': article['publishedAt']
                        # Removed sentiment_score and sentiment_label
                    })
                    
                    if len(articles) >= limit:
                        break
                
                return articles
                
        except Exception as e:
            logger.warning(f"Recent Indian financial news API failed: {e}")
            
        return None

    def _fetch_indian_financial_news(self, limit: int) -> Optional[List[Dict[str, Any]]]:
        """Fetch specifically Indian financial news"""
        try:
            # Indian financial news query
            query = "(India OR Indian OR BSE OR NSE OR Sensex OR Nifty) AND (stock market OR finance OR economy OR investing OR banking)"
            url = f"{self.news_base_url}/everything"
            
            params = {
                'q': query,
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': limit * 2,  # Fetch more to filter
                'apiKey': self.news_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'articles' in data:
                articles = []
                for article in data['articles']:
                    # Skip blocked domains/paths
                    if not self._is_allowed_article(article):
                        continue
                    
                    # Filter for Indian financial news
                    if not self._is_indian_financial_news(article):
                        continue
                    
                    articles.append({
                        'title': article['title'],
                        'description': article.get('description', ''),
                        'url': article.get('url', ''),
                        'source': article.get('source', {}).get('name', ''),
                        'published_at': article['publishedAt']
                        # Removed sentiment_score and sentiment_label
                    })
                    
                    if len(articles) >= limit:
                        break
                
                return articles
                
        except Exception as e:
            logger.warning(f"Indian financial news API failed: {e}")
            
        return None

    def _fetch_top_headlines_india(self, limit: int) -> Optional[List[Dict[str, Any]]]:
        try:
            url = f"{self.news_base_url}/top-headlines"
            params = {
                'country': 'in',
                'category': 'business',
                'pageSize': limit,
                'apiKey': self.news_api_key
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if 'articles' in data:
                articles = []
                for article in data['articles'][:limit]:

                    # Skip blocked domains
                    if not self._is_allowed_article(article):
                        continue

                    try:
                        published = article.get('publishedAt')
                        published_dt = None
                        if published:
                            try:
                                published_dt = datetime.fromisoformat(published.replace('Z', '+00:00'))
                            except Exception:
                                published_dt = datetime.utcnow()
                        news_article = NewsArticle(
                            title=article['title'],
                            description=article.get('description', ''),
                            content=article.get('content', ''),
                            url=article.get('url', ''),
                            source=article.get('source', {}).get('name', ''),
                            published_at=published_dt,
                            sentiment_score=0.0,  # Default value
                            sentiment_label='neutral'  # Default value
                        )
                        db.session.add(news_article)
                        db.session.commit()
                    except Exception as e:
                        logger.warning(f"Failed to store top headline: {e}")
                        db.session.rollback()

                    articles.append({
                        'title': article['title'],
                        'description': article.get('description', ''),
                        'url': article.get('url', ''),
                        'source': article.get('source', {}).get('name', ''),
                        'published_at': article.get('publishedAt', datetime.now().isoformat())
                        # Removed sentiment_score and sentiment_label
                    })
                return articles
        except Exception as e:
            logger.warning(f"Top headlines (IN) failed: {e}")
        return None
    
    def _get_stored_news(self, limit: int) -> List[Dict[str, Any]]:
        try:
            # Only get very recent stored news (last 6 hours)
            cutoff_time = datetime.utcnow() - timedelta(hours=6)
            articles = NewsArticle.query.filter(
                NewsArticle.published_at >= cutoff_time
            ).order_by(NewsArticle.published_at.desc()).limit(limit).all()
            
            return [{
                'title': article.title,
                'description': article.description,
                'url': article.url,
                'source': article.source,
                'published_at': article.published_at.isoformat()
                # Removed sentiment fields
            } for article in articles]
        except Exception as e:
            logger.error(f"Error getting stored news: {e}")
            return self.fallback_news[:limit]
    
    def _get_fallback_news(self) -> List[Dict[str, Any]]:
        return [
            {
                'title': 'Stock Market Shows Resilience Amid Economic Challenges',
                'description': 'Major indices demonstrate strength despite ongoing economic uncertainties.',
                'url': '',
                'source': 'Market News',
                'published_at': datetime.now().isoformat()
                # Removed sentiment_score and sentiment_label
            },
            {
                'title': 'Tech Sector Leads Market Recovery',
                'description': 'Technology stocks continue to outperform as investors seek growth opportunities.',
                'url': '',
                'source': 'Financial Times',
                'published_at': datetime.now().isoformat()
                # Removed sentiment_score and sentiment_label
            },
            {
                'title': 'Federal Reserve Policy Impact on Markets',
                'description': 'Investors closely watch Fed decisions for market direction clues.',
                'url': '',
                'source': 'Reuters',
                'published_at': datetime.now().isoformat()
                # Removed sentiment_score and sentiment_label
            },
            {
                'title': 'Oil Prices Fluctuate on Supply Concerns',
                'description': 'Energy sector faces volatility amid changing supply dynamics.',
                'url': '',
                'source': 'Bloomberg',
                'published_at': datetime.now().isoformat()
                # Removed sentiment_score and sentiment_label
            },
            {
                'title': 'Earnings Season Brings Mixed Results',
                'description': 'Corporate earnings reports show varied performance across sectors.',
                'url': '',
                'source': 'CNBC',
                'published_at': datetime.now().isoformat()
                # Removed sentiment_score and sentiment_label
            }
        ]
    
    def get_news_for_symbol(self, symbol: str, limit: int = 5) -> List[Dict[str, Any]]:
        try:
            if self.news_api_key:
                try:
                    url = f"{self.news_base_url}/top-headlines"
                    params = {
                        'country': 'in',
                        'q': f'"{symbol}" OR "{self._get_company_name(symbol)}"',
                        'pageSize': limit,
                        'apiKey': self.news_api_key
                    }
                    response = requests.get(url, params=params, timeout=10)
                    response.raise_for_status()
                    data = response.json()
                    if 'articles' in data and data['articles']:
                        articles = []
                        for article in data['articles'][:limit]:

                            # Skip blocked domains
                            if not self._is_allowed_article(article):
                                continue

                            articles.append({
                                'title': article['title'],
                                'description': article.get('description', ''),
                                'url': article.get('url', ''),
                                'source': article.get('source', {}).get('name', ''),
                                'published_at': article.get('publishedAt', datetime.now().isoformat())
                                # Removed sentiment_score and sentiment_label
                            })
                        return articles
                except Exception:
                    pass

                query = f'("{symbol}" OR "{self._get_company_name(symbol)}") AND (India OR NSE OR BSE)'
                url = f"{self.news_base_url}/everything"
                params = {
                    'q': query,
                    'language': 'en',
                    'sortBy': 'publishedAt',
                    'pageSize': limit,
                    'apiKey': self.news_api_key
                }
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                if 'articles' in data:
                    articles = []
                    for article in data['articles'][:limit]:

                        # Skip blocked domains
                        if not self._is_allowed_article(article):
                            continue

                        articles.append({
                            'title': article['title'],
                            'description': article.get('description', ''),
                            'url': article.get('url', ''),
                            'source': article.get('source', {}).get('name', ''),
                            'published_at': article.get('publishedAt', datetime.now().isoformat())
                            # Removed sentiment_score and sentiment_label
                        })
                    return articles
            
            return self.get_latest_news(limit)
            
        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {e}")
            return self.get_latest_news(limit)
    
    def _get_company_name(self, symbol: str) -> str:
        company_names = {
            'AAPL': 'Apple Inc',
            'MSFT': 'Microsoft Corporation',
            'GOOGL': 'Alphabet Inc',
            'AMZN': 'Amazon.com Inc',
            'TSLA': 'Tesla Inc',
            'RELIANCE': 'Reliance Industries',
            'TCS': 'Tata Consultancy Services',
            'INFY': 'Infosys Limited',
            'HDFC': 'HDFC Bank Limited',
            'ICICIBANK': 'ICICI Bank Limited'
        }
        return company_names.get(symbol.upper(), symbol)
