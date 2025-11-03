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
            subject = f"🚀 Top {len(top_stocks)} Stock Picks - {datetime.now().strftime('%Y-%m-%d')}"
            html_content = self._create_top_stocks_email_content(user, top_stocks)
            
            # Use EmailJS to send the email
            # Get user name safely - use email username as fallback
            user_name = getattr(user, 'name', None) or user.email.split('@')[0] or "Investor"
            
            template_params = {
                "user_name": user_name,
                "subject": subject,
                "html_content": html_content,
                "top_stocks_count": len(top_stocks),
                "sent_date": datetime.now().strftime('%B %d, %Y'),
                "to_email": user.email
            }
            
            return self.email_service.send_email(
                to_email=user.email,
                template_params=template_params
            )
            
        except Exception as e:
            logger.error(f"Failed to send top stocks email to {user.email} via EmailJS: {e}")
            return False
    
    def _create_top_stocks_email_content(self, user: User, top_stocks: List[Dict[str, Any]]) -> str:
        """Create HTML email content for top stocks"""
        # Get user name safely
        user_name = getattr(user, 'name', None) or user.email.split('@')[0] or "Investor"
        
        stocks_html = ""
        for i, stock in enumerate(top_stocks, 1):
            symbol = stock.get('symbol', 'N/A')
            recommendation = stock.get('recommendation', 'HOLD')
            confidence = stock.get('confidence_score', 0)
            current_price = stock.get('current_price', 0)
            reasoning = stock.get('reasoning', 'No reasoning provided')
            
            # Convert confidence to percentage if it's a decimal
            if confidence <= 1:  # If it's a decimal like 0.85
                confidence_percentage = confidence * 100
            else:  # If it's already a percentage like 85
                confidence_percentage = confidence
            
            # Get screener data if available
            screener_data = stock.get('screener_data', {})
            mcap = screener_data.get('MCap(Cr)', 'N/A')
            down_from_high = screener_data.get('%DownFromHigh', 'N/A')
            
            # Determine color based on recommendation
            action_color = {
                'BUY': '#28a745',
                'SELL': '#dc3545', 
                'HOLD': '#ffc107'
            }.get(recommendation, '#6c757d')
            
            stocks_html += f"""
            <div style="border: 1px solid #e0e0e0; border-radius: 10px; padding: 20px; margin: 15px 0; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <h3 style="margin: 0; color: #333;">#{i} {symbol}</h3>
                    <span style="background: {action_color}; color: white; padding: 5px 12px; border-radius: 20px; font-weight: bold;">
                        {recommendation}
                    </span>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;">
                    <div>
                        <strong>Current Price:</strong><br>
                        <span style="font-size: 18px; font-weight: bold; color: #2c3e50;">₹{current_price:,.2f}</span>
                    </div>
                    <div>
                        <strong>Confidence:</strong><br>
                        <span style="font-size: 16px; color: #27ae60;">{confidence_percentage:.1f}%</span>
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;">
                    <div>
                        <strong>Market Cap:</strong><br>
                        <span>₹{mcap} Cr</span>
                    </div>
                    <div>
                        <strong>From 52W High:</strong><br>
                        <span>{down_from_high}%</span>
                    </div>
                </div>
                
                <div style="background: #f8f9fa; padding: 12px; border-radius: 5px;">
                    <strong>Analysis:</strong><br>
                    <span style="color: #555;">{reasoning}</span>
                </div>
            </div>
            """
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Top Stock Picks</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
                .disclaimer {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .stats {{ background: white; padding: 15px; border-radius: 8px; margin: 20px 0; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0; font-size: 28px;">🎯 Top Stock Picks</h1>
                    <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">
                        Carefully selected based on our advanced screening algorithm
                    </p>
                    <p style="margin: 5px 0 0 0; font-size: 14px; opacity: 0.8;">
                        {datetime.now().strftime('%B %d, %Y')}
                    </p>
                </div>
                
                <div class="content">
                    <div class="stats">
                        <h3 style="margin: 0 0 10px 0; color: #2c3e50;">Hello {user_name}!</h3>
                        <p style="margin: 0; color: #666;">
                            Based on technical analysis, market cap screening, and momentum indicators
                        </p>
                    </div>
                    
                    {stocks_html}
                    
                    <div style="text-align: center; margin: 25px 0;">
                        <a href="#" style="background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                            View Detailed Analysis
                        </a>
                    </div>
                    
                    <div class="disclaimer">
                        <h4 style="margin: 0 0 10px 0; color: #856404;">⚠️ Investment Disclaimer</h4>
                        <p style="margin: 0; font-size: 13px;">
                            These recommendations are generated by our automated screening system and are for informational purposes only. 
                            They do not constitute financial advice. Please conduct your own research and consult with a qualified financial 
                            advisor before making any investment decisions. Past performance is not indicative of future results.
                        </p>
                    </div>
                </div>
                
                <div class="footer">
                    <p>© 2024 Stock Recommendation System. All rights reserved.</p>
                    <p>
                        <a href="#" style="color: #667eea; text-decoration: none;">Unsubscribe</a> | 
                        <a href="#" style="color: #667eea; text-decoration: none;">Privacy Policy</a> | 
                        <a href="#" style="color: #667eea; text-decoration: none;">Contact Us</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
