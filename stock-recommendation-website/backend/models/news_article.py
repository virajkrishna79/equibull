from app import db
from datetime import datetime

class NewsArticle(db.Model):
    __tablename__ = 'news_articles'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=True)
    url = db.Column(db.String(500), nullable=True)
    source = db.Column(db.String(100), nullable=True)
    published_at = db.Column(db.DateTime, nullable=True)
    sentiment_score = db.Column(db.Float, nullable=True)
    sentiment_label = db.Column(db.String(20), nullable=True)  # positive, negative, neutral
    relevance_score = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<NewsArticle {self.title[:50]}...>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'content': self.content,
            'url': self.url,
            'source': self.source,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'sentiment_score': self.sentiment_score,
            'sentiment_label': self.sentiment_label,
            'relevance_score': self.relevance_score,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
