from app import db
from datetime import datetime

class StockRecommendation(db.Model):
    __tablename__ = 'stock_recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False)
    recommendation = db.Column(db.String(20), nullable=False)  # BUY, SELL, HOLD
    confidence_score = db.Column(db.Float, nullable=False)
    algorithm_recommendation = db.Column(db.String(20), nullable=False)
    sentiment_score = db.Column(db.Float, nullable=True)
    current_price = db.Column(db.Float, nullable=True)
    target_price = db.Column(db.Float, nullable=True)
    reasoning = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<StockRecommendation {self.symbol}: {self.recommendation}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'recommendation': self.recommendation,
            'confidence_score': self.confidence_score,
            'algorithm_recommendation': self.algorithm_recommendation,
            'sentiment_score': self.sentiment_score,
            'current_price': self.current_price,
            'target_price': self.target_price,
            'reasoning': self.reasoning,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
