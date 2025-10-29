from app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    subscribed_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_email_sent = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'is_active': self.is_active,
            'subscribed_at': self.subscribed_at.isoformat() if self.subscribed_at else None,
            'last_email_sent': self.last_email_sent.isoformat() if self.last_email_sent else None
        }
