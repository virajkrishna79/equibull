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
            "bloombergquint.com", "reuters.com", "bloomberg.com", "ndtv.com",
            "zeebiz.com", "cnbctv18.com"
        ]

        # Block these website domains
        self.blocked_domains = [
            "twistedsifter.com", "autoexpress.co.uk", "oklahoman.com", "tvline.com",
            "variety.com", "allears.net", "pcgamer.com", "nintendolife.com",
            "indiewire.com", "commonsensewithmoney.com", "forbes.com",
            "redflagdeals.com", "bringatrailer.com", "irishtimes.com",
            "ozbargain.com.au", "wccftech.com", "globenewswire.com",
            "notebookcheck.net", "finance.yahoo.com", "comicbook.com", "biztoc.com",
            "cnet.com", "cbc.ca", "adexchanger.com", "wwd.com", "americanthinker.com",
            "mcnews.com.au", "cnblogs.com", "sammobile.com", "protothema.gr",
            "abc.net.au"
        ]

        # Block specific paths within allowed domains
        self.blocked_paths = [
            "/magazines/", "/entertainment/", "/lifestyle/", "/sports/", "/panache/"
        ]

    def _is_allowed_article(self, article: Dict[str, Any]) -> bool:
        """Return False if the article domain or path is blocked"""
        url = article.get("url", "")
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        path = parsed_url.path.lower()

        for blocked_domain in self.blocked_domains:
            if blocked_domain in domain:
                return False

        for blocked_path in self.blocked_paths:
            if blocked_path in path:
                return False

        return True

    def _is_indian_financial_news(self, article: Dict[str, Any]) -> bool:
        title = article.get('title', '').lower()
        description = article.get('description', '').lower()
        content = article.get('content', '').lower()

        indian_keywords = [
            'india', 'indian', 'bse', 'nse', 'sensex', 'nifty', 'rupee', 'rs.',
            'mumbai', 'delhi', 'bangalore', 'chennai', 'kolkata', 'hyderabad',
            'sebi', 'rbi', 'fmcg', 'psu', 'psb', 'indian economy', 'gst',
            'union budget', 'finance minister', 'mcap', 'market cap'
        ]

        financial_keywords = [
            'stock', 'share', 'market', 'trading', 'investment', 'investing', 'ipo',
            'dividend', 'earnings', 'profit', 'revenue', 'quarterly', 'financial',
            'banking', 'insurance', 'mutual fund', 'portfolio'
        ]

        text = f"{title} {description} {content}"
        indian_matches = sum(1 for keyword in indian_keywords if keyword in text)
        financial_matches = sum(1 for keyword in financial_keywords if keyword in text)

        return indian_matches >= 1 and financial_matches >= 2

    def get_latest_news(self, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            if self.news_api_key:
                news = self._fetch_top_headlines_india(limit)
                if news and len(news) > 0:
                    return news

                news = self._fetch_indian_financial_news(limit)
                if news and len(news) > 0:
                    return news

            return []
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return []

    def _fetch_indian_financial_news(self, limit: int) -> Optional[List[Dict[str, Any]]]:
        try:
            query = "(India OR Indian OR BSE OR NSE OR Sensex OR Nifty) AND (stock market OR finance OR economy OR investing OR banking)"
            url = f"{self.news_base_url}/everything"
            params = {
                'q': query,
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': limit * 2,
                'apiKey': self.news_api_key
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if 'articles' in data:
                articles = []
                for article in data['articles']:

                    if not self._is_allowed_article(article):
                        continue

                    if not self._is_indian_financial_news(article):
                        continue

                    sentiment_score, sentiment_label = self._analyze_sentiment(article['title'])

                    news_article = NewsArticle(
                        title=article['title'],
                        description=article.get('description', ''),
                        content=article.get('content', ''),
                        url=article.get('url', ''),
                        source=article.get('source', {}).get('name', ''),
                        published_at=datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00')),
                        sentiment_score=sentiment_score,
                        sentiment_label=sentiment_label
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
                        'sentiment_score': sentiment_score,
                        'sentiment_label': sentiment_label
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
                    if not self._is_allowed_article(article):
                        continue

                    sentiment_score, sentiment_label = self._analyze_sentiment(article['title'])

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
                            sentiment_score=sentiment_score,
                            sentiment_label=sentiment_label
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
                        'sentiment_score': sentiment_score,
                        'sentiment_label': sentiment_label
                    })

                return articles

        except Exception as e:
            logger.warning(f"Top headlines (IN) failed: {e}")

        return None

    def _analyze_sentiment(self, text: str) -> tuple:
        try:
            positive_keywords = [
                'surge', 'jump', 'rise', 'gain', 'profit', 'earnings', 'growth',
                'positive', 'bullish', 'rally', 'breakout', 'strong', 'up'
            ]

            negative_keywords = [
                'fall', 'drop', 'decline', 'loss', 'crash', 'bearish', 'weak',
                'negative', 'down', 'plunge', 'slump', 'concern', 'risk'
            ]

            text_lower = text.lower()
            positive_count = sum(1 for word in positive_keywords if word in text_lower)
            negative_count = sum(1 for word in negative_keywords if word in text_lower)

            if positive_count > negative_count:
                return 0.5, 'positive'
            elif negative_count > positive_count:
                return -0.5, 'negative'
            else:
                return 0.0, 'neutral'

        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return 0.0, 'neutral'

    def _get_stored_news(self, limit: int) -> List[Dict[str, Any]]:
        try:
            articles = NewsArticle.query.order_by(NewsArticle.published_at.desc()).limit(limit).all()
            stored = [article.to_dict() for article in articles]

            # strip published_at before returning
            for item in stored:
                item.pop("published_at", None)

            return stored

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
                'sentiment_score': 0.3,
                'sentiment_label': 'positive'
            },
            {
                'title': 'Tech Sector Leads Market Recovery',
                'description': 'Technology stocks continue to outperform as investors seek growth opportunities.',
                'url': '',
                'source': 'Financial Times',
                'sentiment_score': 0.5,
                'sentiment_label': 'positive'
            },
            {
                'title': 'Federal Reserve Policy Impact on Markets',
                'description': 'Investors closely watch Fed decisions for market direction clues.',
                'url': '',
                'source': 'Reuters',
                'sentiment_score': 0.0,
                'sentiment_label': 'neutral'
            },
            {
                'title': 'Oil Prices Fluctuate on Supply Concerns',
                'description': 'Energy sector faces volatility amid changing supply dynamics.',
                'url': '',
                'source': 'Bloomberg',
                'sentiment_score': -0.2,
                'sentiment_label': 'negative'
            },
            {
                'title': 'Earnings Season Brings Mixed Results',
                'description': 'Corporate earnings reports show varied performance across sectors.',
                'url': '',
                'source': 'CNBC',
                'sentiment_score': 0.1,
                'sentiment_label': 'neutral'
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
                            if not self._is_allowed_article(article):
                                continue

                            sentiment_score, sentiment_label = self._analyze_sentiment(article['title'])

                            articles.append({
                                'title': article['title'],
                                'description': article.get('description', ''),
                                'url': article.get('url', ''),
                                'source': article.get('source', {}).get('name', ''),
                                'sentiment_score': sentiment_score,
                                'sentiment_label': sentiment_label
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
                    if not self._is_allowed_article(article):
                        continue

                    sentiment_score, sentiment_label = self._analyze_sentiment(article['title'])

                    articles.append({
                        'title': article['title'],
                        'description': article.get('description', ''),
                        'url': article.get('url', ''),
                        'source': article.get('source', {}).get('name', ''),
                        'sentiment_score': sentiment_score,
                        'sentiment_label': sentiment_label
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
