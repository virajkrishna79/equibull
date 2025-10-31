import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
from typing import List, Dict, Any
from models import User, StockRecommendation
from app import db

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email_address = os.getenv('EMAIL_ADDRESS')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.from_name = os.getenv('FROM_NAME', 'Stock Recommendation System')
        
    def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Public wrapper for _send_email"""
        return self._send_email(to_email, subject, html_content)

    def send_confirmation_email(self, email: str) -> bool:
        try:
            if not self._check_email_config():
                logger.warning("Email configuration not set up")
                return False
            
            subject = "Welcome to Stock Recommendations!"
            html_content = self._get_confirmation_email_template(email)
            return self._send_email(email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Error sending confirmation email: {e}")
            return False
    
    def send_daily_recommendations(self) -> bool:
        try:
            if not self._check_email_config():
                logger.warning("Email configuration not set up")
                return False
            
            active_users = User.query.filter_by(is_active=True).all()
            if not active_users:
                logger.info("No active subscribers found")
                return True
            
            recommendations = StockRecommendation.query.order_by(
                StockRecommendation.created_at.desc()
            ).limit(10).all()
            
            if not recommendations:
                logger.info("No recommendations to send")
                return True
            
            success_count = 0
            for user in active_users:
                if self._send_recommendation_email(user.email, recommendations):
                    success_count += 1
                    user.last_email_sent = datetime.utcnow()
                    db.session.commit()
            
            logger.info(f"Sent daily recommendations to {success_count}/{len(active_users)} subscribers")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error sending daily recommendations: {e}")
            return False
    
    def send_recommendation_update(self, symbol: str, recommendation: Dict[str, Any]) -> bool:
        try:
            if not self._check_email_config():
                logger.warning("Email config missing")
                return False
            
            active_users = User.query.filter_by(is_active=True).all()
            if not active_users:
                return True
            
            subject = f"Stock Alert: {symbol} - {recommendation['recommendation']}"
            html_content = self._get_recommendation_email_template(symbol, [recommendation])
            
            success_count = 0
            for user in active_users:
                if self._send_email(user.email, subject, html_content):
                    success_count += 1
            
            logger.info(f"Sent alert to {success_count}/{len(active_users)}")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error sending update: {e}")
            return False
    
    def _send_recommendation_email(self, email: str, recommendations: List[StockRecommendation]) -> bool:
        try:
            subject = f"Daily Stock Recommendations - {datetime.now().strftime('%Y-%m-%d')}"
            html_content = self._get_recommendation_email_template("Daily Update", recommendations)
            return self._send_email(email, subject, html_content)
        except Exception as e:
            logger.error(f"Error sending recommendation email: {e}")
            return False
    
    def _send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.email_address}>"
            msg['To'] = to_email
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
                server.send_message(msg)
            
            logger.info(f"Email sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    def _check_email_config(self) -> bool:
        return all([
            self.email_address,
            self.email_password,
            self.smtp_server,
            self.smtp_port
        ])
    
    # Templates remain unchanged below
    # ...

    
    def _get_confirmation_email_template(self, email: str) -> str:
        """Generate confirmation email HTML template"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome to Stock Recommendations</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; padding: 12px 24px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Welcome to Stock Recommendations!</h1>
                    <p>Your daily dose of intelligent stock insights</p>
                </div>
                <div class="content">
                    <h2>Hello!</h2>
                    <p>Thank you for subscribing to our stock recommendation service. You're now part of a community that receives:</p>
                    <ul>
                        <li>📈 Daily stock recommendations based on our proprietary algorithm</li>
                        <li>📊 Technical analysis and market sentiment insights</li>
                        <li>🤖 Machine learning-powered price predictions</li>
                        <li>📰 Latest market news and analysis</li>
                    </ul>
                    <p>You'll receive your first recommendations tomorrow morning. Stay tuned!</p>
                    <a href="#" class="button">Visit Our Website</a>
                    <p><strong>Note:</strong> You can unsubscribe at any time by replying to this email with "UNSUBSCRIBE".</p>
                </div>
                <div class="footer">
                    <p>© 2024 Stock Recommendation System. All rights reserved.</p>
                    <p>This email was sent to {email}</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_recommendation_email_template(self, title: str, recommendations: List[StockRecommendation]) -> str:
        """Generate recommendation email HTML template"""
        recommendations_html = ""
        for rec in recommendations:
            rec_dict = rec.to_dict() if hasattr(rec, 'to_dict') else rec
            action_color = {
                'BUY': '#28a745',
                'SELL': '#dc3545',
                'HOLD': '#ffc107'
            }.get(rec_dict.get('recommendation', 'HOLD'), '#6c757d')
            
            recommendations_html += f"""
            <div style="border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin: 15px 0; background: white;">
                <h3 style="margin: 0 0 10px 0; color: {action_color};">
                    {rec_dict.get('symbol', 'N/A')} - {rec_dict.get('recommendation', 'HOLD')}
                </h3>
                <p><strong>Current Price:</strong> ₹{rec_dict.get('current_price', 'N/A'):,.2f}</p>
                <p><strong>Target Price:</strong> ₹{rec_dict.get('target_price', 'N/A'):,.2f}</p>
                <p><strong>Confidence:</strong> {rec_dict.get('confidence_score', 0)*100:.1f}%</p>
                <p><strong>Reasoning:</strong> {rec_dict.get('reasoning', 'N/A')}</p>
            </div>
            """
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Stock Recommendations - {title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
                .disclaimer {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Stock Recommendations</h1>
                    <p>{title} - {datetime.now().strftime('%B %d, %Y')}</p>
                </div>
                <div class="content">
                    <h2>Today's Top Recommendations</h2>
                    {recommendations_html}
                    
                    <div class="disclaimer">
                        <h4>⚠️ Important Disclaimer</h4>
                        <p>These recommendations are for informational purposes only and should not be considered as financial advice. Always do your own research and consult with a financial advisor before making investment decisions.</p>
                    </div>
                    
                    <p><strong>Happy Investing!</strong></p>
                </div>
                <div class="footer">
                    <p>© 2024 Stock Recommendation System. All rights reserved.</p>
                    <p>To unsubscribe, reply to this email with "UNSUBSCRIBE".</p>
                </div>
            </div>
        </body>
        </html>
        """

