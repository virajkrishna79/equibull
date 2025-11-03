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
    
    def _send_top_stocks_email(self, user: User, top_stocks: List[Dict[str, Any]]) -> bool:
    """Send top stocks email to a specific user using EmailJS"""
    try:
        # Get user name safely
        user_name = getattr(user, 'name', None) or user.email.split('@')[0] or "Investor"
        
        # Prepare stock data for template
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
        
        template_params = {
            "user_name": user_name,
            "sent_date": datetime.now().strftime('%B %d, %Y'),
            "to_email": user.email,
            "stocks": stocks_data  # Pass individual stock data for loop
        }
        
        return self.email_service.send_email(
            to_email=user.email,
            template_params=template_params
        )
        
    except Exception as e:
        logger.error(f"Failed to send top stocks email to {user.email} via EmailJS: {e}")
        return False
    
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
