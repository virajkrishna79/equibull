# services/recommendation_email_service.py
import logging
from typing import List, Dict, Any
from datetime import datetime
from models import User
from app import db
from services.emailjs_service import EmailJSService
from services.recommendation_service import RecommendationService

logger = logging.getLogger(__name__)

class RecommendationEmailService:
    def __init__(self):
        self.email_service = EmailJSService()
        self.recommendation_service = RecommendationService()
    
    def send_top_stocks_to_users(self, top_n: int = 5) -> Dict[str, Any]:
        """
        Send top N stocks from screener to all active users using EmailJS
        Returns: {"success": bool, "sent_count": int, "total_users": int, "error": str}
        """
        try:
            # Get active users
            active_users = User.query.filter_by(is_active=True).all()
            if not active_users:
                logger.info("No active users found for email notifications")
                return {"success": True, "sent_count": 0, "total_users": 0, "error": None}
            
            # Get screener recommendations
            screener_results = self.recommendation_service.get_screener_recommendations()
            
            if not screener_results:
                logger.warning("No screener results found")
                return {"success": False, "sent_count": 0, "total_users": len(active_users), "error": "No screener results"}
            
            # Get top N stocks by confidence score
            top_stocks = sorted(
                screener_results, 
                key=lambda x: x.get('confidence_score', 0), 
                reverse=True
            )[:top_n]
            
            if not top_stocks:
                logger.warning("No top stocks found after sorting")
                return {"success": False, "sent_count": 0, "total_users": len(active_users), "error": "No top stocks"}
            
            # Send emails to all users using EmailJS
            success_count = 0
            for user in active_users:
                if self._send_top_stocks_email(user, top_stocks):
                    success_count += 1
                    # Update last email sent timestamp
                    user.last_email_sent = datetime.utcnow()
            
            # Commit all timestamp updates
            db.session.commit()
            
            logger.info(f"Successfully sent top {top_n} stocks to {success_count}/{len(active_users)} users using EmailJS")
            
            return {
                "success": True,
                "sent_count": success_count,
                "total_users": len(active_users),
                "top_stocks_count": len(top_stocks),
                "email_service_used": "emailjs",
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Error sending top stocks to users: {e}")
            db.session.rollback()
            return {"success": False, "sent_count": 0, "total_users": 0, "error": str(e)}
    
    def _send_top_stocks_email(self, user: User, top_stocks: List[Dict[str, Any]]) -> bool:
        """Send top stocks email to a specific user using EmailJS"""
        try:
            # Get user name safely
            user_name = getattr(user, 'name', None) or user.email.split('@')[0] or "Investor"
            
            # Prepare stock data for template - INDIVIDUAL STOCKS, NOT HTML
            stocks_data = []
            for i, stock in enumerate(top_stocks, 1):
                symbol = stock.get('symbol', 'N/A')
                recommendation = stock.get('recommendation', 'HOLD')
                confidence = stock.get('confidence_score', 0)
                current_price = stock.get('current_price', 0)
                reasoning = stock.get('reasoning', 'No reasoning provided')
                
                # Convert confidence to percentage
                confidence_percentage = confidence * 100 if confidence <= 1 else confidence
                
                # Get screener data
                screener_data = stock.get('screener_data', {})
                mcap = screener_data.get('MCap(Cr)', 'N/A')
                down_from_high = screener_data.get('%DownFromHigh', 'N/A')
                
                # Determine badge color
                badge_color = {
                    'BUY': '#28a745',
                    'SELL': '#dc3545', 
                    'HOLD': '#ffc107'
                }.get(recommendation, '#6c757d')
                
                stocks_data.append({
                    'symbol': symbol,
                    'recommendation': recommendation,
                    'confidence': f"{confidence_percentage:.1f}%",
                    'current_price': f"₹{current_price:,.2f}",
                    'mcap': f"₹{mcap} Cr",
                    'down_from_high': f"{down_from_high}%",
                    'reasoning': reasoning,
                    'badge_color': badge_color
                })
            
            # Template parameters - NO html_content, use stocks array
            template_params = {
                "user_name": user_name,
                "sent_date": datetime.now().strftime('%B %d, %Y'),
                "to_email": user.email,
                "stocks": stocks_data  # This is the key - individual stock data
            }
            
            return self.email_service.send_email(
                to_email=user.email,
                template_params=template_params
            )
            
        except Exception as e:
            logger.error(f"Failed to send top stocks email to {user.email} via EmailJS: {e}")
            return False

# Singleton instance for easy import
recommendation_email_service = RecommendationEmailService()
